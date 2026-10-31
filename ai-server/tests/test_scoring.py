import unittest

from ml.metrics import binary_metrics, evaluate, pos_weight, roc_auc
from ml.scoring import confidence_score, fuse, hybrid, summarize, to_label


class ScoringTest(unittest.TestCase):
    def test_confidence_rounds_half_up(self):
        # round() 은 82.5 → 82 (은행가 반올림). 사사오입으로 83 이어야 한다.
        self.assertEqual(confidence_score(0.825), 83)
        self.assertEqual(confidence_score(0.175), 83)
        self.assertEqual(confidence_score(0.5), 50)
        self.assertEqual(confidence_score(0.0), 100)

    def test_label_boundaries_are_inclusive(self):
        self.assertEqual(to_label(0.3999), "Genuine")
        self.assertEqual(to_label(0.4), "Suspicious")
        self.assertEqual(to_label(0.6999), "Suspicious")
        self.assertEqual(to_label(0.7), "Fake")

    def test_summary_fields_agree_after_rounding(self):
        # 0.69996 은 반올림하면 0.7 → 라벨도 반올림된 값 기준으로 Fake 여야 화면 수치와 어긋나지 않는다.
        self.assertEqual(summarize(0.69996), {"fakeProbability": 0.7, "confidenceScore": 70, "label": "Fake"})
        self.assertEqual(summarize(1.3)["fakeProbability"], 1.0)

    def test_hybrid_weights(self):
        self.assertAlmostEqual(hybrid(1.0, 0.0), 0.7)
        self.assertAlmostEqual(hybrid(0.0, 1.0), 0.3)
        self.assertAlmostEqual(hybrid(None, 0.0), 0.1)
        self.assertAlmostEqual(hybrid(None, 2.0), 0.9)

    def test_image_only_raises_suspicion(self):
        self.assertEqual(fuse(0.9, 0.1, image_model_loaded=True), 0.9)
        self.assertAlmostEqual(fuse(0.2, 0.9, image_model_loaded=True), 0.41)
        self.assertAlmostEqual(fuse(0.2, 0.9, image_model_loaded=False), 0.305)


class MetricsTest(unittest.TestCase):
    def test_confusion_and_f1(self):
        m = binary_metrics([1, 1, 0, 0], [1, 0, 1, 0])
        self.assertEqual(m["confusion"], {"tp": 1, "fp": 1, "fn": 1, "tn": 1})
        self.assertEqual((m["accuracy"], m["precision"], m["recall"], m["f1"]), (0.5, 0.5, 0.5, 0.5))

    def test_roc_auc(self):
        self.assertEqual(roc_auc([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8]), 0.75)
        self.assertEqual(roc_auc([0, 1], [0.5, 0.5]), 0.5)
        self.assertIsNone(roc_auc([1, 1], [0.2, 0.9]))
        self.assertEqual(evaluate([0, 1], [0.2, 0.9])["roc_auc"], 1.0)

    def test_pos_weight(self):
        self.assertEqual(pos_weight([1, 0, 0, 0]), 3.0)
        self.assertEqual(pos_weight([1, 1]), 1.0)


if __name__ == "__main__":
    unittest.main()
