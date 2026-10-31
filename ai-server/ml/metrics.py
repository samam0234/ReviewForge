"""이진 분류 평가 지표 (텍스트·이미지 학습 공용, 외부 라이브러리 없이 계산)."""
from __future__ import annotations


def binary_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == p == 0)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "accuracy": round((tp + tn) / len(y_true), 4) if y_true else 0.0,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
    }


def roc_auc(y_true: list[int], scores: list[float]) -> float | None:
    """Mann-Whitney U 방식. 동점은 0.5 로 센다. 한쪽 클래스만 있으면 정의되지 않으므로 None."""
    pos = [s for t, s in zip(y_true, scores) if t == 1]
    neg = [s for t, s in zip(y_true, scores) if t == 0]
    if not pos or not neg:
        return None
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return round(wins / (len(pos) * len(neg)), 4)


def evaluate(y_true: list[int], probabilities: list[float], threshold: float = 0.5) -> dict:
    metrics = binary_metrics(y_true, [int(p >= threshold) for p in probabilities])
    metrics["roc_auc"] = roc_auc(y_true, probabilities)
    return metrics


def pos_weight(labels: list[int]) -> float:
    """BCEWithLogitsLoss 의 pos_weight = 음성 수 / 양성 수 (클래스 불균형 보정)."""
    positives = sum(labels)
    negatives = len(labels) - positives
    return negatives / positives if positives and negatives else 1.0
