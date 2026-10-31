"""EfficientNet-B3 + 이미지 규칙을 결합한 리뷰 이미지 추론기.

학습된 체크포인트가 없으면 규칙 기반만으로 동작한다 (분류 헤드가 학습되지 않은 모델은 쓰지 않는다).
"""
from __future__ import annotations

from pathlib import Path

import torch
from PIL import Image, ImageOps
from torch import nn

from ml.image_model import ARCH, IMAGE_SIZE, build_model, eval_transform
from ml.image_rules import image_signals
from ml.scoring import hybrid, summarize

DEFAULT_IMAGE_MODEL_PATH = Path(__file__).resolve().parent / "artifacts" / "image_model.pt"


class ImagePredictor:
    def __init__(self, model: nn.Module | None = None, image_size: int = IMAGE_SIZE) -> None:
        self.model = model
        self.transform = eval_transform(image_size)

    @property
    def model_loaded(self) -> bool:
        return self.model is not None

    @classmethod
    def load(cls, path: str | Path = DEFAULT_IMAGE_MODEL_PATH) -> "ImagePredictor":
        path = Path(path)
        if not path.exists():
            return cls()
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
        if checkpoint.get("arch") != ARCH:
            raise ValueError(f"지원하지 않는 이미지 모델입니다: {checkpoint.get('arch')}")
        model = build_model(pretrained=False)
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        return cls(model, checkpoint.get("image_size", IMAGE_SIZE))

    @torch.no_grad()
    def _model_predict(self, image: Image.Image) -> float:
        tensor = self.transform(ImageOps.exif_transpose(image).convert("RGB")).unsqueeze(0)
        return torch.sigmoid(self.model(tensor)).item()

    def analyze(self, image: Image.Image) -> dict:
        rules = image_signals(image)
        ml_prob = self._model_predict(image) if self.model_loaded else None
        return {
            **summarize(hybrid(ml_prob, rules["score"])),
            "signals": [h["reason"] for h in rules["hits"]],
            "source": "efficientnet_b3+rules" if self.model_loaded else "rules",
            "width": image.width,
            "height": image.height,
        }
