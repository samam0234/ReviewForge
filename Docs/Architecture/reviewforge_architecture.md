# ReviewForge 시스템 아키텍처

**프로젝트**: ReviewForge  
**버전**: 1.2 (v1.1 리뷰 사진 분석·통계 집계 반영)  
**작성일**: 2026-11-01

## 계층 구조

1. **Presentation Layer**: Next.js 16 (App Router, Cache Components) — `frontend/`
   - UI, 폼(텍스트 + 선택 사진), 대시보드, 인증 UI
   - Route Handler(`app/api/*`)가 Spring Boot 로 중계 (JSON·multipart), JWT 는 httpOnly 쿠키 `rf_token`
2. **Orchestration Layer**: Spring Boot 4.1 (Java 21) — `backend/`
   - 입력 검증(텍스트·이미지 형식/크기), JWT 인증, Flask 호출(RestClient, 5초 타임아웃)
   - MongoDB 저장/조회, **통계 집계**(`$group`), 전역 예외 처리
3. **AI/ML Layer**: Flask + Gradio — `ai-server/`
   - `ml/predict.py`: 텍스트 하이브리드(fastText 방식 분류기 + 규칙)
   - `ml/image_predict.py`: **EfficientNet-B3** + 이미지 규칙 (체크포인트 없으면 규칙만)
   - `ml/scoring.py`: 하이브리드·융합·반올림·라벨 — 모든 점수의 단일 계산 지점
   - `app/`: `/analyze`, `/health`, `gradio_app.py`: 데모
4. **Data Layer**: MongoDB (로컬 docker / Atlas)
   - `users` (email unique), `analyses` (userId index) — 원본 이미지는 저장하지 않음

## 데이터 흐름 — 분석

```
브라우저
  │  POST /api/analyze  (JSON {text}  또는  multipart text + image)
  ▼
Next.js Route Handler ──Bearer JWT──▶ Spring Boot POST /api/analyze
                                        │ 텍스트 검증 (공백 금지, ≤5000자)
                                        │ 이미지 검증 (jpeg/png/webp, ≤5MB) — 위반 시 415/413
                                        ├──▶ Flask POST /analyze
                                        │      ├─ 텍스트: 모델 0.7 + 규칙 0.3            → t
                                        │      ├─ 이미지: EfficientNet-B3 0.7 + 규칙 0.3 → i  (모델 없으면 0.1 + 0.8·규칙)
                                        │      └─ 융합: p = max(t, (1−w)·t + w·i)
                                        │◀── fakeProbability(p), confidenceScore, label, keywords,
                                        │    highlights, textFakeProbability(t), image{…}
                                        ├──▶ MongoDB analyses 저장 (로그인 사용자만, 결과만)
  ◀──────────── AnalysisResponse (saved 여부 포함) ◀┘
```

## 데이터 흐름 — 대시보드

서버 컴포넌트가 쿠키를 읽어 두 API 를 병렬 호출한다 (`<Suspense>` 내부).

```
Next.js /dashboard ──┬─▶ GET /api/analyses?limit=20   → 최근 기록 표
                     └─▶ GET /api/analyses/stats       → MongoDB:
                            $match userId → $project hasImage → $group label (count, Σp, Σconf, Σimage)
                            → 백엔드에서 합산 · 가중 평균 · HALF_UP 반올림
```

계산 규칙 전체: [`Docs/guidance/scoring.md`](../guidance/scoring.md)

## 분석 기록 스키마 (`analyses`)

| 필드 | 타입 | 설명 |
|------|------|------|
| `userId` | string (index) | 소유자 |
| `reviewText` | string | 정리된(strip) 리뷰 |
| `fakeProbability` | double | 최종 점수 (사진이 있으면 융합) |
| `confidenceScore` | int | `max(p, 1−p)×100` 사사오입 |
| `label` | string | Genuine / Suspicious / Fake |
| `keywords`, `highlights` | array | 판단 근거 |
| `textFakeProbability` | double \| null | 텍스트 단독 점수 (v1.0 기록은 없음) |
| `image` | object \| null | `fakeProbability, confidenceScore, label, signals[], source, width, height` |
| `createdAt` | date | 생성 시각 |

## 업로드 제한 (계층별 동일)

| 계층 | 제한 | 초과 시 |
|------|------|---------|
| 브라우저 | 5MB, jpeg/png/webp | 전송 전 오류 표시 |
| Spring Boot | `max-file-size 5MB`, `max-request-size 6MB`, 타입 화이트리스트 | 413 / 415 |
| Flask | `MAX_CONTENT_LENGTH 6MB`, 5MB, 4천만 픽셀, 실제 포맷 확인 | 413 / 400 (메시지는 백엔드가 그대로 전달) |

## 포트 및 환경

| 서비스 | 포트 | 주요 환경 변수 |
|--------|------|----------------|
| Next.js | 3000 | `BACKEND_URL`, `NEXT_PUBLIC_GRADIO_URL` |
| Spring Boot | 8080 | `MONGODB_URI`, `AI_SERVER_URL`, `JWT_SECRET`, `CORS_ORIGINS` |
| Flask | 5000 | `FLASK_PORT`, `MODEL_PATH`, `IMAGE_MODEL_PATH` |
| Gradio | 7860 | `GRADIO_PORT` |
| MongoDB | 27017 (로컬) | - |

실행 방법은 [`Docs/guidance/run_local.md`](../guidance/run_local.md) 참고.
