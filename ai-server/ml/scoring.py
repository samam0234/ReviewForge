"""판정 점수 계산 공통 규칙. 텍스트·이미지·융합 결과가 모두 같은 기준을 쓴다.

- hybrid: 모델 확률과 규칙 점수를 섞는다. 모델이 없으면 규칙만으로 0.1~0.9 범위에 매핑한다.
- fuse: 텍스트 + 이미지 융합. 이미지는 의심을 '올리기만' 한다
  (사진이 멀쩡해도 텍스트의 조작 신호가 사라지지 않기 때문).
- summarize: 확률을 소수 4자리로 반올림한 뒤 같은 값에서 확신도·라벨을 계산해 수치가 서로 어긋나지 않게 한다.
"""
from __future__ import annotations

import math

FAKE_THRESHOLD = 0.7
SUSPICIOUS_THRESHOLD = 0.4
ML_WEIGHT = 0.7
RULES_ONLY_BASE = 0.1
RULES_ONLY_SCALE = 0.8
IMAGE_WEIGHT = 0.3            # 이미지 모델이 학습된 경우
IMAGE_WEIGHT_RULES_ONLY = 0.15  # 이미지 모델 없이 메타데이터 규칙만 있는 경우


def clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def to_label(fake_probability: float) -> str:
    if fake_probability >= FAKE_THRESHOLD:
        return "Fake"
    if fake_probability >= SUSPICIOUS_THRESHOLD:
        return "Suspicious"
    return "Genuine"


def confidence_score(fake_probability: float) -> int:
    """판정 확신도 0~100 = max(p, 1-p) × 100, 사사오입 (파이썬 round 의 은행가 반올림을 쓰지 않는다)."""
    certainty = max(fake_probability, 1 - fake_probability) * 100
    return math.floor(round(certainty, 6) + 0.5)


def hybrid(ml_probability: float | None, rule_score: float) -> float:
    if ml_probability is None:
        return RULES_ONLY_BASE + RULES_ONLY_SCALE * clamp01(rule_score)
    return ML_WEIGHT * ml_probability + (1 - ML_WEIGHT) * clamp01(rule_score)


def fuse(text_probability: float, image_probability: float, image_model_loaded: bool) -> float:
    weight = IMAGE_WEIGHT if image_model_loaded else IMAGE_WEIGHT_RULES_ONLY
    return max(text_probability, (1 - weight) * text_probability + weight * image_probability)


def summarize(fake_probability: float) -> dict:
    p = round(clamp01(fake_probability), 4)
    return {"fakeProbability": p, "confidenceScore": confidence_score(p), "label": to_label(p)}
