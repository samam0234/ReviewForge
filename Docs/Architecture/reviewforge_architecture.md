# ReviewForge 시스템 아키텍처

**프로젝트**: ReviewForge  
**버전**: 1.1 (MVP 구현 반영)  
**작성일**: 2026-11-01

## 계층 구조

1. **Presentation Layer**: Next.js 16 (App Router, Cache Components) — `frontend/`
   - UI, 폼, 대시보드, 인증 UI
   - Route Handler(`app/api/*`)가 Spring Boot 로 중계하고 JWT 를 httpOnly 쿠키 `rf_token` 으로 보관
2. **Orchestration Layer**: Spring Boot 4.1 (Java 21) — `backend/`
   - 입력 검증, JWT 인증, Flask 호출(RestClient, 5초 타임아웃), MongoDB 저장/조회, 전역 예외 처리
3. **AI/ML Layer**: Flask + Gradio — `ai-server/`
   - `ml/`: 전처리·PyTorch 분류기·학습·하이브리드 추론(모델 70% + 규칙 30%)
   - `app/`: `/analyze`, `/health` API, `gradio_app.py`: 데모
4. **Data Layer**: MongoDB (로컬 docker / Atlas)
   - `users` (email unique), `analyses` (userId index)

## 데이터 흐름

```
브라우저
  │  fetch /api/analyze (쿠키 rf_token)
  ▼
Next.js Route Handler ──Bearer JWT──▶ Spring Boot /api/analyze
                                        │ @Valid 검증
                                        ├──▶ Flask /analyze ──▶ Predictor(모델 + 규칙)
                                        │◀── fakeProbability, confidenceScore, label, keywords, highlights
                                        ├──▶ MongoDB analyses 저장 (로그인 사용자만)
  ◀──────────── AnalysisResponse (saved 여부 포함) ◀┘
```

대시보드는 서버 컴포넌트가 쿠키를 읽어 `GET /api/analyses` 를 직접 호출한다 (`<Suspense>` 내부).

## 포트 및 환경

| 서비스 | 포트 | 주요 환경 변수 |
|--------|------|----------------|
| Next.js | 3000 | `BACKEND_URL`, `NEXT_PUBLIC_GRADIO_URL` |
| Spring Boot | 8080 | `MONGODB_URI`, `AI_SERVER_URL`, `JWT_SECRET`, `CORS_ORIGINS` |
| Flask | 5000 | `FLASK_PORT`, `MODEL_PATH` |
| Gradio | 7860 | `GRADIO_PORT` |
| MongoDB | 27017 (로컬) | - |

실행 방법은 [`Docs/guidance/run_local.md`](../guidance/run_local.md) 참고.
