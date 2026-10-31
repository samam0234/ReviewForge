from flask import Blueprint, jsonify, request

from app.services import model_service

bp = Blueprint("analyze", __name__)
MAX_BATCH = 20


@bp.get("/health")
def health():
    return jsonify(status="ok", modelLoaded=model_service.get_predictor().model_loaded)


@bp.post("/analyze")
def analyze():
    body = request.get_json(silent=True) or {}
    try:
        if "texts" in body:
            texts = body["texts"]
            if not isinstance(texts, list) or not 1 <= len(texts) <= MAX_BATCH:
                raise ValueError(f"texts 는 1~{MAX_BATCH}개의 문자열 배열이어야 합니다.")
            return jsonify(results=[model_service.analyze(t) for t in texts])
        return jsonify(model_service.analyze(body.get("text")))
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
