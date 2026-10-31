"""추론기 단일 인스턴스 관리. 라우트와 Gradio 가 같은 추론기를 공유한다."""
from __future__ import annotations

import os
import threading

from ml.predict import DEFAULT_MODEL_PATH, Predictor

MAX_TEXT_LENGTH = 5000

_lock = threading.Lock()
_predictor: Predictor | None = None


def get_predictor() -> Predictor:
    global _predictor
    if _predictor is None:
        with _lock:
            if _predictor is None:
                _predictor = Predictor.load(os.getenv("MODEL_PATH", str(DEFAULT_MODEL_PATH)))
    return _predictor


def reload_predictor() -> Predictor:
    global _predictor
    with _lock:
        _predictor = None
    return get_predictor()


def validate_text(text: object) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("리뷰 텍스트가 비어 있습니다.")
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(f"리뷰는 {MAX_TEXT_LENGTH}자 이하로 입력해 주세요.")
    return text.strip()


def analyze(text: str) -> dict:
    return get_predictor().analyze(validate_text(text))
