from flask import Flask
from flask_cors import CORS

from app.routes.analyze import bp as analyze_bp

MAX_CONTENT_LENGTH = 6 * 1024 * 1024  # 이미지 5MB + 텍스트·multipart 여유분


def create_app() -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    CORS(app)
    app.register_blueprint(analyze_bp)
    return app
