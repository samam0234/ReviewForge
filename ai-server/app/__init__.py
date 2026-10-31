from flask import Flask
from flask_cors import CORS

from app.routes.analyze import bp as analyze_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False
    CORS(app)
    app.register_blueprint(analyze_bp)
    return app
