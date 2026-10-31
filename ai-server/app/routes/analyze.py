from flask import Blueprint, jsonify, request

from app.services import model_service

bp = Blueprint("analyze", __name__)
MAX_BATCH = 20


@bp.get("/health")
def health():
    return jsonify(
        status="ok",
        modelLoaded=model_service.get_predictor().model_loaded,
        imageModelLoaded=model_service.get_image_predictor().model_loaded,
    )


@bp.post("/analyze")
def analyze():
    """JSON `{text}` / `{texts: []}` 또는 multipart `text` + 선택 `image` 파일."""
    try:
        if request.mimetype == "multipart/form-data":
            file = request.files.get("image")
            image_bytes = file.read() if file and file.filename else None
            return jsonify(model_service.analyze(request.form.get("text"), image_bytes))

        body = request.get_json(silent=True) or {}
        if "texts" in body:
            texts = body["texts"]
            if not isinstance(texts, list) or not 1 <= len(texts) <= MAX_BATCH:
                raise ValueError(f"texts 는 1~{MAX_BATCH}개의 문자열 배열이어야 합니다.")
            return jsonify(results=[model_service.analyze(t) for t in texts])
        return jsonify(model_service.analyze(body.get("text")))
    except ValueError as exc:
        return jsonify(error=str(exc)), 400


@bp.errorhandler(413)
def too_large(_):
    return jsonify(error="요청 크기가 너무 큽니다. 이미지는 5MB 이하로 올려 주세요."), 413
