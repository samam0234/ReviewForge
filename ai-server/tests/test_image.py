import io
import tempfile
import unittest
from pathlib import Path

import torch
from PIL import Image

from ml.image_model import build_model
from ml.image_predict import ImagePredictor
from ml.image_rules import border_uniform_ratio, image_signals
from ml.image_train import parse_args, stratified_indices, train


def noise_image(size: int = 480, seed: int = 0) -> Image.Image:
    """실사 장면처럼 넓은 영역 단위로 색이 바뀌는 블록 노이즈 (픽셀 노이즈는 축소하면 단색 회색이 된다)."""
    g = torch.Generator().manual_seed(seed)
    blocks = torch.randint(0, 256, (12, 12, 3), dtype=torch.uint8, generator=g)
    return Image.fromarray(blocks.numpy()).resize((size, size), Image.NEAREST)


def to_bytes(image: Image.Image, fmt: str = "PNG", exif: Image.Exif | None = None) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format=fmt, **({"exif": exif} if exif is not None else {}))
    return buf.getvalue()


class ImageModelTest(unittest.TestCase):
    def test_efficientnet_b3_head_outputs_single_logit(self):
        model = build_model(pretrained=False).eval()
        self.assertEqual(model.classifier[1].in_features, 1536)
        with torch.no_grad():
            self.assertEqual(model(torch.zeros(2, 3, 64, 64)).shape, (2, 1))


class ImageRulesTest(unittest.TestCase):
    def test_uniform_background_detected(self):
        self.assertEqual(border_uniform_ratio(Image.new("RGB", (500, 500), "white")), 1.0)
        self.assertLess(border_uniform_ratio(noise_image()), 0.5)

    def test_editor_software_and_low_resolution(self):
        exif = Image.Exif()
        exif[0x0131] = "Adobe Photoshop 25.0"
        image = Image.open(io.BytesIO(to_bytes(noise_image(200), "JPEG", exif)))
        reasons = " ".join(h["reason"] for h in image_signals(image)["hits"])
        self.assertIn("편집 프로그램", reasons)
        self.assertIn("저해상도", reasons)

    def test_camera_photo_scores_lower_than_studio_shot(self):
        exif = Image.Exif()
        exif[0x010F], exif[0x0110] = "Samsung", "SM-S928N"
        camera = Image.open(io.BytesIO(to_bytes(noise_image(), "JPEG", exif)))
        studio = Image.new("RGB", (300, 300), "white")
        self.assertEqual(image_signals(camera)["score"], 0.0)
        self.assertGreater(image_signals(studio)["score"], 0.5)


class ImagePredictorTest(unittest.TestCase):
    def test_rules_only_when_checkpoint_missing(self):
        result = ImagePredictor.load("does-not-exist.pt").analyze(Image.new("RGB", (300, 300), "white"))
        self.assertEqual(result["source"], "rules")
        self.assertIn(result["label"], {"Suspicious", "Fake"})

    def test_stratified_split_keeps_both_classes_in_val(self):
        train_idx, val_idx = stratified_indices([0] * 5 + [1] * 5, 0.2, seed=1)
        self.assertEqual(sorted(train_idx + val_idx), list(range(10)))
        self.assertEqual({0, 1}, {0 if i < 5 else 1 for i in val_idx})

    def test_train_then_predict_with_efficientnet_b3(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "images"
            for cls in ("genuine", "fake"):
                (data / cls).mkdir(parents=True)
            for i in range(4):
                noise_image(96, seed=i).save(data / "genuine" / f"{i}.png")
                Image.new("RGB", (96, 96), (255, 255 - i, 255)).save(data / "fake" / f"{i}.png")
            metrics = train(parse_args([
                "--data", str(data), "--out", tmp, "--epochs", "1", "--batch-size", "4",
                "--image-size", "64", "--no-pretrained",
            ]))
            predictor = ImagePredictor.load(Path(tmp) / "image_model.pt")
            result = predictor.analyze(noise_image(96))
        self.assertEqual(metrics["arch"], "efficientnet_b3")
        self.assertTrue(predictor.model_loaded)
        self.assertEqual(result["source"], "efficientnet_b3+rules")
        self.assertTrue(0 <= result["fakeProbability"] <= 1)


if __name__ == "__main__":
    unittest.main()
