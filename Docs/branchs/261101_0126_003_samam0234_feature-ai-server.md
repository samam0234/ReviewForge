# 커밋 기록 003

## 기본 정보

| 항목 | 내용 |
|------|------|
| 일시 | 2026-11-01 01:26 |
| ID | 003 |
| 작성자 | samam0234 |
| 브랜치 | feature/ai-server |
| 커밋 메시지 | `feat(ai-server): Flask 분석 API 및 Gradio 데모 구현` |

## 작업 내용

- Flask 앱 팩토리, `GET /health`, `POST /analyze` (단일 `text` / 다중 `texts` 최대 20건)
- `model_service`: 추론기 단일 인스턴스 관리, 입력 검증(빈 값, 5000자 제한)
- `gradio_app.py`: 7860 포트 데모 (판정 확률, 근거 하이라이트, 예시 리뷰)
- `requirements.txt`, `.env.example`, API 테스트 4건

## 변경 파일

| 구분 | 경로 | 설명 |
|------|------|------|
| 추가 | ai-server/app/ | Flask 앱·라우트·서비스 |
| 추가 | ai-server/gradio_app.py | Gradio MVP |
| 추가 | ai-server/requirements.txt, .env.example | 의존성·환경 변수 |
| 추가 | ai-server/tests/test_api.py | API 테스트 |

## 검증

- `python -m unittest discover -s tests -t .` → 10 tests OK
- `python -m app.main` 후 `/health` → `{"modelLoaded":true,"status":"ok"}`
- `/analyze` 과장 리뷰 → `Fake`, fakeProbability 0.91
- `python gradio_app.py` → http://localhost:7860 200 응답

## 비고 / 다음 작업

- feature/backend 에서 Spring Boot 가 `/analyze` 를 호출
