import tempfile
import unittest
from pathlib import Path

from ml.predict import Predictor, to_label
from ml.preprocess import Vocabulary, tokenize
from ml.rules import rule_signals
from ml.train import parse_args, train


class PreprocessTest(unittest.TestCase):
    def test_tokenize_keeps_hangul_latin_and_exclaim(self):
        self.assertEqual(tokenize("최고 Best!!!"), ["최고", "best", "!!!"])

    def test_unknown_text_encodes_to_unk(self):
        vocab = Vocabulary.build(["배송 빨라요"])
        self.assertEqual(vocab.encode("zzz"), [0])


class RulesTest(unittest.TestCase):
    def test_hype_review_scores_higher_than_detailed_review(self):
        hype = rule_signals("인생템!!! 무조건 사세요 최고최고")["score"]
        detail = rule_signals("배송은 3일 걸렸고 사이즈는 한 치수 크게 추천합니다.")["score"]
        self.assertGreater(hype, detail)


class PredictorTest(unittest.TestCase):
    def test_label_thresholds(self):
        self.assertEqual(to_label(0.1), "Genuine")
        self.assertEqual(to_label(0.5), "Suspicious")
        self.assertEqual(to_label(0.9), "Fake")

    def test_rules_only_when_model_missing(self):
        result = Predictor.load("does-not-exist.pt").analyze("강추 강추 강추!!!")
        self.assertEqual(result["source"], "rules")
        self.assertIn(result["label"], {"Suspicious", "Fake"})

    def test_train_then_predict_hybrid(self):
        with tempfile.TemporaryDirectory() as tmp:
            train(parse_args(["--out", tmp, "--epochs", "30"]))
            predictor = Predictor.load(Path(tmp) / "model.pt")
            fake = predictor.analyze("최고 최고 무조건 사세요!!! 인생템 강추!!!")
            real = predictor.analyze("배송은 4일 걸렸고 색상은 사진보다 조금 어두워요.")
        self.assertEqual(fake["source"], "hybrid")
        self.assertGreater(fake["fakeProbability"], real["fakeProbability"])
        for key in ("fakeProbability", "confidenceScore", "label", "keywords", "highlights"):
            self.assertIn(key, fake)


if __name__ == "__main__":
    unittest.main()
