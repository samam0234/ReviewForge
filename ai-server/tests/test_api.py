import unittest

from app import create_app


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_health(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "ok")

    def test_analyze_single(self):
        res = self.client.post("/analyze", json={"text": "인생템!!! 무조건 사세요"})
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(0 <= body["fakeProbability"] <= 1)
        self.assertTrue(0 <= body["confidenceScore"] <= 100)

    def test_analyze_batch(self):
        res = self.client.post("/analyze", json={"texts": ["좋아요", "배송 3일 걸렸어요"]})
        self.assertEqual(len(res.get_json()["results"]), 2)

    def test_empty_text_rejected(self):
        res = self.client.post("/analyze", json={"text": "   "})
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()
