"""Flask AI 서버 진입점.  실행: ai-server 디렉터리에서 `python -m app.main`"""
import os

from dotenv import load_dotenv

from app import create_app

load_dotenv()
app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
