# 로컬 실행 가이드

## 사전 준비

| 도구 | 확인한 버전 | 비고 |
|------|-------------|------|
| Python | 3.10 | torch, flask, pandas, gradio |
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

Atlas 를 쓰면 이 단계를 건너뛰고 `MONGODB_URI` 에 Atlas 연결 문자열을 넣는다.

### 2. AI 서버 (Flask + 모델)

```bash
cd ai-server
python -m venv .venv
.venv\Scripts\activate           # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m ml.train               # ml/artifacts/model.pt 생성 (생략 시 규칙 기반으로만 동작)
python -m app.main               # http://localhost:5000
python gradio_app.py             # (선택) http://localhost:7860
```

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

## 테스트

```bash
cd ai-server && python -m unittest discover -s tests -t .   # ML + API
cd backend && ./mvnw test                                    # Spring Boot
cd frontend && npm run lint && npm run build                 # Next.js
```

## API 요약

| 계층 | Method | Endpoint | 인증 | 설명 |
|------|--------|----------|------|------|
| Next.js | POST | `/api/analyze` | 쿠키(선택) | Spring Boot 로 중계 |
| Next.js | POST | `/api/auth/login`, `/register`, `/logout` | - | 쿠키 `rf_token` 설정/삭제 |
| Spring Boot | POST | `/api/analyze` | Bearer(선택) | 로그인 시 MongoDB 저장 |
| Spring Boot | GET | `/api/analyses?limit=20` | Bearer 필수 | 본인 기록 목록 |
| Spring Boot | GET | `/api/analyses/{id}` | Bearer 필수 | 본인 기록 상세 |
| Spring Boot | POST | `/api/auth/register`, `/login` | - | JWT 발급 |
| Spring Boot | GET | `/api/auth/me`, `/api/health` | Bearer / - | 내 정보, 상태 |
| Flask | POST | `/analyze` | - | `{text}` 또는 `{texts: []}` (최대 20) |
| Flask | GET | `/health` | - | `modelLoaded` 포함 |

### 분석 응답 필드

| 필드 | 의미 |
|------|------|
| `fakeProbability` | 가짜일 확률 0~1 |
| `confidenceScore` | 판정 확신도 0~100 = `max(p, 1-p) × 100` |
| `label` | `Genuine`(< 0.4) / `Suspicious`(< 0.7) / `Fake` |
| `keywords`, `highlights` | 판단 근거 문구와 이유 |
