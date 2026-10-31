"""추론기 단일 인스턴스 관리. 라우트와 Gradio 가 같은 추론기를 공유한다."""
from __future__ import annotations

import io
import os
import threading

from PIL import Image, UnidentifiedImageError

from ml.image_predict import DEFAULT_IMAGE_MODEL_PATH, ImagePredictor
from ml.predict import DEFAULT_MODEL_PATH, Predictor
from ml.scoring import fuse, summarize

MAX_TEXT_LENGTH = 5000
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}

_lock = threading.Lock()
_predictor: Predictor | None = None
_image_predictor: ImagePredictor | None = None


def get_predictor() -> Predictor:
    global _predictor
    if _predictor is None:
        with _lock:
            if _predictor is None:
                _predictor = Predictor.load(os.getenv("MODEL_PATH") or str(DEFAULT_MODEL_PATH))
    return _predictor


def get_image_predictor() -> ImagePredictor:
    global _image_predictor
    if _image_predictor is None:
        with _lock:
            if _image_predictor is None:
                _image_predictor = ImagePredictor.load(os.getenv("IMAGE_MODEL_PATH") or str(DEFAULT_IMAGE_MODEL_PATH))
    return _image_predictor


def reload_predictor() -> Predictor:
    global _predictor, _image_predictor
    with _lock:
        _predictor = None
        _image_predictor = None
    return get_predictor()


def validate_text(text: object) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("리뷰 텍스트가 비어 있습니다.")
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(f"리뷰는 {MAX_TEXT_LENGTH}자 이하로 입력해 주세요.")
    return text.strip()


def load_image(data: bytes) -> Image.Image:
    if not data:
        raise ValueError("이미지 파일이 비어 있습니다.")
    if len(data) > MAX_IMAGE_BYTES:
        raise ValueError(f"이미지는 {MAX_IMAGE_BYTES // (1024 * 1024)}MB 이하로 올려 주세요.")
    try:
        image = Image.open(io.BytesIO(data))
        if image.format not in ALLOWED_IMAGE_FORMATS:
            raise ValueError("JPEG, PNG, WEBP 이미지만 지원합니다.")
        if image.width * image.height > MAX_IMAGE_PIXELS:
            raise ValueError("이미지 해상도가 너무 큽니다.")
        image.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("이미지 파일을 읽을 수 없습니다.") from exc
    return image


def analyze(text: object, image_bytes: bytes | None = None) -> dict:
    """텍스트 분석 + (선택) 이미지 분석. 이미지가 있으면 최상위 점수는 융합 점수다."""
    result = get_predictor().analyze(validate_text(text))
    result["textFakeProbability"] = result["fakeProbability"]
    result["image"] = None
    if image_bytes is None:
        return result

    image_predictor = get_image_predictor()
    image_result = image_predictor.analyze(load_image(image_bytes))
    fused = fuse(result["fakeProbability"], image_result["fakeProbability"], image_predictor.model_loaded)
    return {**result, **summarize(fused), "image": image_result}
