# 로컬 실행 가이드

## 사전 준비

| 도구 | 확인한 버전 | 비고 |
|------|-------------|------|
| Python | 3.10 | torch 2.12, torchvision 0.27, flask, pandas, pillow, gradio |
| JDK | 21 이상 (26 에서 확인) | Maven 은 `mvnw` 가 자동 설치 |
| Node.js | 24 | npm 11 |
| Docker | 28 | 로컬 MongoDB 용 (Atlas 사용 시 불필요) |

## 포트

| 서비스 | 포트 |
|--------|------|
| Next.js | 3000 |
| Spring Boot | 8080 |
| Flask API | 5000 |
| Gradio 데모 | 7860 |
| MongoDB (로컬) | 27017 |

## 실행 순서

### 1. MongoDB

```bash
docker compose up -d --wait      # 로컬 mongo:7
```

Atlas 를 쓰면 이 단계를 건너뛰고 `MONGODB_URI` 에 Atlas 연결 문자열을 넣는다. (연결 문자열은 절대 커밋하지 않는다)

### 2. AI 서버 (Flask + 모델)

```bash
cd ai-server
python -m venv .venv
.venv\Scripts\activate           # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m ml.train               # ml/artifacts/model.pt 생성 (생략 시 텍스트도 규칙 기반)
python -m app.main               # http://localhost:5000
python gradio_app.py             # (선택) http://localhost:7860 — 텍스트 + 사진 데모
```

### 2-1. (선택) EfficientNet-B3 리뷰 사진 모델 학습

데이터를 ImageFolder 형식으로 둔다. 폴더 이름은 정확히 `genuine`, `fake` 여야 한다.

```
ai-server/ml/data/images/
├── genuine/   실제 구매자가 찍은 사진
└── fake/      판매자 제공·도용·합성·과도 편집 사진
```

```bash
python -m ml.image_train --data ml/data/images                       # 백본 고정, 헤드만 (기본)
python -m ml.image_train --data ml/data/images --unfreeze --lr 3e-4  # 데이터가 충분하면 전체 미세조정
```

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--epochs` | 10 | 코사인 학습률 스케줄 |
| `--batch-size` | 16 | |
| `--image-size` | 300 | B3 기본 해상도 |
| `--lr` | 1e-3 | AdamW |
| `--unfreeze` | 꺼짐 | 백본까지 학습 |
| `--no-pretrained` | 꺼짐 | ImageNet 가중치 없이 (오프라인 테스트용) |

- 최초 실행 시 ImageNet 가중치(약 47MB)를 `~/.cache/torch/hub/checkpoints/` 에 내려받는다.
- 산출물: `ml/artifacts/image_model.pt`, `image_metrics.json` (git 제외). 서버를 다시 띄우면 자동 적용되고 `/health` 의 `imageModelLoaded` 가 `true` 가 된다.
- 체크포인트가 없어도 사진 분석은 동작한다 (메타데이터 규칙만, `image.source = "rules"`).

### 3. 백엔드 (Spring Boot)

```bash
cd backend
# 필요 시 환경 변수: MONGODB_URI, AI_SERVER_URL, JWT_SECRET, CORS_ORIGINS (.env.example 참고)
./mvnw spring-boot:run           # Windows: mvnw.cmd spring-boot:run
```

### 4. 프론트엔드 (Next.js)

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev                      # http://localhost:3000
```

## 환경 변수

| 계층 | 변수 | 기본값 | 설명 |
|------|------|--------|------|
| ai-server | `FLASK_PORT` | 5000 | |
| ai-server | `MODEL_PATH` | (빈 값) → `ml/artifacts/model.pt` | 텍스트 모델 |
| ai-server | `IMAGE_MODEL_PATH` | (빈 값) → `ml/artifacts/image_model.pt` | EfficientNet-B3 체크포인트 |
| ai-server | `GRADIO_PORT` | 7860 | |
| backend | `MONGODB_URI` | `mongodb://localhost:27017/reviewforge` | Atlas 사용 시 교체 |
| backend | `AI_SERVER_URL` | `http://localhost:5000` | |
| backend | `JWT_SECRET` | 개발용 값 | **운영에서는 반드시 32바이트 이상 무작위 값** |
| backend | `CORS_ORIGINS` | `http://localhost:3000` | |
| frontend | `BACKEND_URL` | `http://localhost:8080` | 서버 전용 |
| frontend | `NEXT_PUBLIC_GRADIO_URL` | `http://localhost:7860` | 브라우저 노출 |

## 테스트

```bash
cd ai-server && python -m unittest discover -s tests -t .   # ML·이미지·점수·API 29건
cd backend && ./mvnw test                                    # Spring Boot 13건
cd frontend && npm run lint && npm run build                 # Next.js
```

## API 요약

| 계층 | Method | Endpoint | 인증 | 설명 |
|------|--------|----------|------|------|
| Next.js | POST | `/api/analyze` | 쿠키(선택) | JSON·multipart 를 Spring Boot 로 중계 |
| Next.js | POST | `/api/auth/login`, `/register`, `/logout` | - | 쿠키 `rf_token` 설정/삭제 |
| Spring Boot | POST | `/api/analyze` | Bearer(선택) | JSON `{text}` 또는 multipart `text` + `image`, 로그인 시 저장 |
| Spring Boot | GET | `/api/analyses?limit=20` | Bearer 필수 | 본인 최근 기록 (최대 100) |
| Spring Boot | GET | `/api/analyses/stats` | Bearer 필수 | 본인 전체 기록 통계 |
| Spring Boot | GET | `/api/analyses/{id}` | Bearer 필수 | 본인 기록 상세 |
| Spring Boot | POST | `/api/auth/register`, `/login` | - | JWT 발급 |
| Spring Boot | GET | `/api/auth/me`, `/api/health` | Bearer / - | 내 정보, 상태 |
| Flask | POST | `/analyze` | - | JSON `{text}` / `{texts: []}`(최대 20) 또는 multipart `text` + `image` |
| Flask | GET | `/health` | - | `modelLoaded`, `imageModelLoaded` |

### 분석 응답 필드

| 필드 | 의미 |
|------|------|
| `fakeProbability` | 가짜일 확률 0~1 (사진이 있으면 텍스트·사진 융합) |
| `confidenceScore` | 판정 확신도 0~100 = `max(p, 1-p) × 100` 사사오입 |
| `label` | `Genuine`(< 0.4) / `Suspicious`(< 0.7) / `Fake` |
| `keywords`, `highlights` | 판단 근거 문구와 이유 |
| `textFakeProbability` | 텍스트 단독 점수 |
| `image` | 사진 결과 또는 `null` — `fakeProbability`, `confidenceScore`, `label`, `signals`, `source`, `width`, `height` |

### 통계 응답 (`/api/analyses/stats`)

```json
{ "total": 4, "avgFakeProbability": 0.3304, "avgConfidenceScore": 87.5,
  "labelCounts": { "Genuine": 3, "Suspicious": 0, "Fake": 1 }, "withImage": 2 }
```

계산식은 [점수 계산 명세](./scoring.md).

## 오류 코드

| 상황 | 상태 |
|------|------|
| 빈 텍스트·5000자 초과·읽을 수 없는 이미지 | 400 |
| 로그인 필요 | 401 |
| 이메일 중복 | 409 |
| 이미지 5MB 초과 | 413 |
| jpeg/png/webp 이외 | 415 |
| AI 서버 오류 / 연결 불가 | 502 / 503 |
