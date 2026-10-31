import io
import unittest

from PIL import Image

from app import create_app


def png_bytes(color="white", size=(300, 300)) -> io.BytesIO:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    buf.seek(0)
    return buf


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_health(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "ok")
        self.assertIn("imageModelLoaded", res.get_json())

    def test_analyze_single(self):
        res = self.client.post("/analyze", json={"text": "인생템!!! 무조건 사세요"})
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(0 <= body["fakeProbability"] <= 1)
        self.assertTrue(0 <= body["confidenceScore"] <= 100)
        self.assertIsNone(body["image"])
        self.assertEqual(body["textFakeProbability"], body["fakeProbability"])

    def test_analyze_batch(self):
        res = self.client.post("/analyze", json={"texts": ["좋아요", "배송 3일 걸렸어요"]})
        self.assertEqual(len(res.get_json()["results"]), 2)

    def test_empty_text_rejected(self):
        res = self.client.post("/analyze", json={"text": "   "})
        self.assertEqual(res.status_code, 400)

    def test_analyze_multipart_with_image(self):
        res = self.client.post(
            "/analyze",
            data={"text": "배송 3일 걸렸고 포장 꼼꼼해요", "image": (png_bytes(), "studio.png")},
            content_type="multipart/form-data",
        )
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertEqual(body["image"]["width"], 300)
        self.assertTrue(body["image"]["signals"])
        self.assertGreaterEqual(body["fakeProbability"], body["textFakeProbability"])

    def test_analyze_multipart_without_image(self):
        res = self.client.post("/analyze", data={"text": "좋아요"}, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(res.get_json()["image"])

    def test_invalid_image_rejected(self):
        res = self.client.post(
            "/analyze",
            data={"text": "좋아요", "image": (io.BytesIO(b"not an image"), "x.png")},
            content_type="multipart/form-data",
        )
        self.assertEqual(res.status_code, 400)

    def test_oversized_request_rejected(self):
        res = self.client.post(
            "/analyze",
            data={"text": "좋아요", "image": (io.BytesIO(b"0" * (7 * 1024 * 1024)), "big.png")},
            content_type="multipart/form-data",
        )
        self.assertEqual(res.status_code, 413)


if __name__ == "__main__":
    unittest.main()
