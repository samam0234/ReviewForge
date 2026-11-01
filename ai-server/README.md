# ai-server — Flask + Gradio

리뷰가 가짜일 확률을 계산하는 프로세스입니다. HTTP로 텍스트(와 선택 사진)를 받아 `ml` 패키지 결과를 JSON으로 돌려주고, Gradio는 같은 추론기를 데모 화면으로 엽니다. 계정, JWT, MongoDB는 없습니다.

| 항목 | 값 |
|------|-----|
| 스택 | Flask 3, flask-cors, PyTorch, torchvision, Pillow, Gradio |
| API | http://localhost:5000 |
| 데모 | http://localhost:7860 |
| 점수 코드 | [ml/README.md](./ml/README.md), [점수 명세](../Docs/guidance/scoring.md) |

## 실행

```bash
python -m venv .venv
.venv\Scripts\activate              # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m ml.train                  # ml/artifacts/model.pt. 생략 가능
python -m app.main                  # Flask
python gradio_app.py                # 선택. 별도 프로세스
python -m unittest discover -s tests -t .
```

가상환경은 `.venv`이고 git에 넣지 않습니다. Windows에서 이 저장소는 `.venv`를 만들어 두었습니다.

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `FLASK_HOST` / `FLASK_PORT` | `0.0.0.0` / `5000` | |
| `FLASK_DEBUG` | `false` | |
| `GRADIO_PORT` | `7860` | 이미 떠 있으면 두 번째 실행은 포트 오류로 끝남 |
| `MODEL_PATH` | 비움 → `ml/artifacts/model.pt` | 텍스트 분류기 |
| `IMAGE_MODEL_PATH` | 비움 → `ml/artifacts/image_model.pt` | EfficientNet-B3 |

`GET /health` 예:

```json
{"status":"ok","modelLoaded":true,"imageModelLoaded":false}
```

`imageModelLoaded: false`는 장애가 아닙니다. 체크포인트가 없으면 사진 분석은 메타데이터 규칙만 탑니다.

## API

| Method | Endpoint | 본문 | 응답 |
|--------|----------|------|------|
| GET | `/health` | - | 위 JSON |
| POST | `/analyze` | JSON `{"text"}` | 판정 객체 하나 |
| POST | `/analyze` | JSON `{"texts":[...]}` | `{"results":[...]}`. 1~20개. 사진은 없음 |
| POST | `/analyze` | multipart `text`, 선택 `image` | 판정 객체. 사진이 있으면 `image` 필드 |

텍스트는 공백만이면 400, 5000자를 넘으면 400입니다. 이미지는 JPEG/PNG/WEBP, 5MB, 4천만 픽셀 이하. 그 밖은 400, 요청 전체가 6MB를 넘으면 413.

응답 필드는 `fakeProbability`, `confidenceScore`, `label`, `keywords`, `highlights`, `source`(`hybrid` 또는 `rules`)입니다. 사진이 있으면 `textFakeProbability`와 `image`가 추가됩니다. `source`가 `rules`이면 해당 모델 파일이 없던 상태입니다.

호출자는 Spring Boot `AiClient`입니다. 브라우저가 이 포트로 직접 분석 요청을 보내면 CORS는 열려 있지만, 저장·인증은 되지 않습니다. 제품 경로는 Next.js → Spring Boot → Flask 입니다.

## 폴더

```
ai-server/
├── app/
│   ├── main.py                 python -m app.main
│   ├── routes/analyze.py       /health, /analyze
│   └── services/model_service.py   추론기 1개씩, 입력 검증
├── ml/                         학습·추론·점수. README 별도
├── gradio_app.py               텍스트 + 사진 데모, 예시 리뷰
├── tests/                      test_ml, test_image, test_scoring, test_api
├── requirements.txt
└── .env.example
```

`model_service`는 프로세스가 처음 분석할 때 체크포인트를 읽고, 그 다음부터 같은 `Predictor`를 재사용합니다. 학습으로 `model.pt`를 갈아끼운 뒤에는 Flask를 다시 띄워야 반영됩니다.

Gradio는 로그인 없이 같은 `analyze()`를 부릅니다. 결과를 MongoDB에 넣지 않습니다.

## 테스트

`python -m unittest discover -s tests -t .` 를 `ai-server`에서 실행합니다. 학습 테스트는 임시 디렉터리에 짧은 epoch만 돌리므로 저장소의 `artifacts/`를 덮어쓰지 않습니다.
