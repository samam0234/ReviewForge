"""학습된 모델 + 규칙을 결합한 추론기.

모델 파일이 없으면 규칙 기반만으로 동작하므로 학습 전에도 서버를 띄울 수 있다.
"""
from __future__ import annotations

from pathlib import Path

import torch

from ml.model import FakeReviewClassifier, collate
from ml.preprocess import Vocabulary
from ml.rules import rule_signals

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "artifacts" / "model.pt"
ML_WEIGHT = 0.7
MAX_KEYWORDS = 5


def to_label(fake_probability: float) -> str:
    if fake_probability >= 0.7:
        return "Fake"
    if fake_probability >= 0.4:
        return "Suspicious"
    return "Genuine"


class Predictor:
    def __init__(self, model: FakeReviewClassifier | None = None, vocab: Vocabulary | None = None) -> None:
        self.model = model
        self.vocab = vocab

    @property
    def model_loaded(self) -> bool:
        return self.model is not None

    @classmethod
    def load(cls, path: str | Path = DEFAULT_MODEL_PATH) -> "Predictor":
        path = Path(path)
        if not path.exists():
            return cls()
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
        vocab = Vocabulary(checkpoint["itos"])
        model = FakeReviewClassifier(len(vocab), checkpoint["embed_dim"])
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        return cls(model, vocab)

    @torch.no_grad()
    def _model_predict(self, text: str) -> tuple[float, list[tuple[str, float]]]:
        word_ids = self.vocab.encode_words(text)
        ids = [i for _, w in word_ids for i in w] or [0]
        prob = torch.sigmoid(self.model(*collate([ids]))).item()
        scores = self.model.feature_scores(ids).tolist()
        contributions, cursor = [], 0
        for word, w_ids in word_ids:
            contributions.append((word, sum(scores[cursor:cursor + len(w_ids)]) / len(ids)))
            cursor += len(w_ids)
        return prob, contributions

    def analyze(self, text: str) -> dict:
        rules = rule_signals(text)
        highlights = [{"text": h["text"], "reason": h["reason"]} for h in rules["hits"]]
        keywords = [h["text"] for h in rules["hits"] if h["text"]]

        if self.model_loaded:
            ml_prob, contributions = self._model_predict(text)
            fake_probability = ML_WEIGHT * ml_prob + (1 - ML_WEIGHT) * rules["score"]
            suspicious_words = sorted((c for c in contributions if c[1] > 0), key=lambda c: -c[1])
            for word, _ in suspicious_words[:MAX_KEYWORDS]:
                if word not in keywords and word[0] not in "!?":
                    keywords.append(word)
                    highlights.append({"text": word, "reason": "모델 기여도 높음"})
            source = "hybrid"
        else:
            fake_probability = 0.1 + 0.8 * rules["score"]
            source = "rules"

        fake_probability = round(fake_probability, 4)
        return {
            "fakeProbability": fake_probability,
            "confidenceScore": round(max(fake_probability, 1 - fake_probability) * 100),
            "label": to_label(fake_probability),
            "keywords": keywords[:MAX_KEYWORDS],
            "highlights": highlights,
            "source": source,
        }
