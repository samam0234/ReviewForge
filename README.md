# ReviewForge

리뷰 한 줄을 넣으면 **가짜일 확률**, **판정 확신도**, **판단 근거**를 바로 보여 주고, 로그인한 사용자의 분석은 MongoDB에 남겨 대시보드로 다시 봅니다. 리뷰 사진(JPEG/PNG/WEBP)을 함께 올리면 사진 점수가 최종 확률에 가산됩니다. 사진 원본은 저장하지 않습니다.

> AI-powered fake review detector. Next.js + Spring Boot + Flask (PyTorch, EfficientNet-B3, Gradio) + MongoDB.

판정은 시드 데이터로 학습한 MVP입니다. 판매 제재나 분쟁의 단독 근거로 쓰지 마세요. 학습 데이터와 한계는 [텍스트 베이스라인](./Docs/trainings/261101_baseline_model.md), [EfficientNet-B3](./Docs/trainings/261101_efficientnet_b3_image.md)에 있습니다.

## 요청이 지나가는 길

```
브라우저
  │  POST /api/analyze
  │  JSON {text}  또는  multipart text + image
  ▼
Next.js :3000          쿠키 rf_token → Bearer JWT
  │                    UI · 폼 · 대시보드 · Route Handler
  ▼
Spring Boot :8080      검증 · 인증 · Flask 호출 · 결과 저장
  │
  ├──▶ Flask :5000     텍스트 분류 + (선택) EfficientNet-B3
  │                      점수 계산은 ai-server/ml/scoring.py 한곳
  │
  └──▶ MongoDB         users, analyses (로그인 사용자만 저장)
```

Gradio(`:7860`)는 같은 추론기를 브라우저에서 바로 시험하는 별도 화면입니다. Spring Boot를 거치지 않으므로 기록에 남지 않습니다.

| 단계 | 하는 일 | 하지 않는 일 |
|------|---------|--------------|
| [frontend/](./frontend/README.md) | 화면, 쿠키 세션, 백엔드로 요청 전달 | 모델 추론, DB 접근 |
| [backend/](./backend/README.md) | 입력 검증, JWT, Flask 호출, 저장·통계 | 텍스트 전처리, 모델 로드 |
| [ai-server/](./ai-server/README.md) | 전처리, 추론, 점수, Gradio | 사용자 계정, 영속 저장 |
| [ai-server/ml/](./ai-server/ml/README.md) | 학습·추론·규칙·점수 식 | HTTP, DB |

계층을 넘는 로직을 넣지 않습니다. 점수 식은 [`Docs/guidance/scoring.md`](./Docs/guidance/scoring.md)와 `ai-server/ml/scoring.py`가 기준입니다.

## 화면에서 보는 것

| 주소 | 내용 |
|------|------|
| http://localhost:3000/ | 소개, 분석·대시보드·Gradio 링크 |
| `/analyze` | 리뷰 입력, 예시 문장, 선택 사진, 결과 카드(하이라이트) |
| `/login` | 회원가입·로그인. 성공하면 httpOnly 쿠키 `rf_token` |
| `/dashboard` | 로그인 필요. 최근 20건, 전체 기록의 가중 평균·라벨 분포 |
| http://localhost:7860 | Gradio. 텍스트와 사진을 모델에 직접 넣음 |

라벨은 최종 확률 `p` 기준입니다. `p < 0.4` Genuine, `0.4 ≤ p < 0.7` Suspicious, `p ≥ 0.7` Fake. 확신도는 "진짜다"가 아니라 **한쪽으로 얼마나 치우쳤는가**입니다. `p = 0.03`과 `p = 0.97`은 둘 다 확신도 97입니다.

사진은 의심을 올리기만 합니다. 사진이 평범해도 과장·홍보 문구로 올라간 텍스트 점수는 내려가지 않습니다. 이미지 체크포인트(`image_model.pt`)가 없으면 사진 점수는 EXIF·해상도·배경 규칙만 쓰고, 응답 `image.source`가 `rules`입니다.

## 저장소 지도

```
ReviewForge/
├── frontend/          Next.js 16  —  README.md
├── backend/           Spring Boot 4.1  —  README.md
├── ai-server/         Flask + Gradio  —  README.md
│   └── ml/            학습·추론·점수  —  README.md
├── Docs/              기획·아키텍처·가이드·기록  —  README.md
├── docker-compose.yml 로컬 MongoDB 7 (27017)
├── AGENTS.md          에이전트 공통 규칙 (SSOT)
└── ReviewForge_인수인계.md
```

| 문서 | 언제 여나 |
|------|-----------|
| [로컬 실행](./Docs/guidance/run_local.md) | 포트, 환경 변수, 학습 명령, API 표 |
| [아키텍처](./Docs/Architecture/reviewforge_architecture.md) | 데이터 흐름, `analyses` 스키마, 업로드 제한 |
| [점수 명세](./Docs/guidance/scoring.md) | 하이브리드·융합·반올림·대시보드 평균 |
| [Docs/](./Docs/README.md) | 기획, 학습 기록, 검증, 디버깅, 배포 점검 |
| [SECURITY.md](./SECURITY.md) | 비밀 값 금지, 취약점 제보 |

## 기술 스택

| 계층 | 버전·라이브러리 | 포트 |
|------|-----------------|------|
| Frontend | Next.js 16.4, React 19, TypeScript, App Router | 3000 |
| Backend | Spring Boot 4.1.2, Java 21, Spring Data MongoDB, jjwt 0.13 | 8080 |
| AI | Flask 3, PyTorch, torchvision EfficientNet-B3, Gradio | 5000 / 7860 |
| DB | MongoDB 7 (Compose) 또는 Atlas | 27017 |

확인된 로컬 도구: Python 3.10, JDK 21+, Node.js 24, Docker 28. Maven은 `backend/mvnw`가 받습니다.

## 빠른 시작

네 프로세스를 각각 띄웁니다. 자세한 옵션은 [실행 가이드](./Docs/guidance/run_local.md).

```bash
docker compose up -d --wait                      # 1. MongoDB

cd ai-server                                     # 2. AI 서버
python -m venv .venv && .venv\Scripts\activate   #    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m ml.train                               #    텍스트 모델. 생략하면 규칙만
python -m app.main                               #    http://localhost:5000

cd backend && mvnw.cmd spring-boot:run           # 3. 백엔드 (macOS/Linux: ./mvnw)

cd frontend && cp .env.example .env.local        # 4. 프론트
npm install && npm run dev                       #    http://localhost:3000
```

사진 모델은 데이터가 있을 때만 `python -m ml.image_train --data ml/data/images` 입니다. 폴더 이름은 `genuine`, `fake`.

동작 확인:

```bash
curl http://localhost:8080/api/health
# {"status":"ok","aiServer":"up"}
```

`aiServer`가 `down`이면 Flask가 꺼져 있거나 `AI_SERVER_URL`이 다릅니다. 분석 API는 그때 503을 돌려줍니다.

## API 한눈에

브라우저가 치는 주소는 Next.js(`/api/*`)이고, 같은 경로를 Spring Boot가 받습니다. Flask는 `/analyze`, `/health`만 노출합니다.

| Method | Endpoint | 인증 | 설명 |
|--------|----------|------|------|
| POST | `/api/analyze` | 선택 | 로그인 시에만 저장. 익명은 결과만 반환 |
| GET | `/api/analyses?limit=20` | Bearer | 내 최근 기록 (최대 100) |
| GET | `/api/analyses/stats` | Bearer | 내 전체 기록의 가중 평균·라벨 건수 |
| GET | `/api/analyses/{id}` | Bearer | 본인 기록만 |
| POST | `/api/auth/register`, `/login` | - | JWT 발급 (24시간) |
| GET | `/api/auth/me` | Bearer | 내 정보 |
| GET | `/api/health` | - | 백엔드와 Flask 생존 |

응답 예 (과장 리뷰 + 흰 배경 사진, E2E에서 나온 값. `keywords`·`highlights` 생략):

```json
{
  "fakeProbability": 0.912,
  "confidenceScore": 91,
  "label": "Fake",
  "textFakeProbability": 0.912,
  "image": {
    "fakeProbability": 0.42,
    "label": "Suspicious",
    "source": "rules",
    "signals": ["단색 배경 — 판매자 제공 연출 사진 가능성"]
  },
  "saved": true
}
```

## 이 MVP에 없는 것

크롤링·배치 분석, 한국어 외 언어, OAuth, 리뷰 자동 작성, 판매자 통계, 모바일 앱. 기획서의 제외 범위와 같습니다.

## 기여

- 작업 브랜치는 `feature/*`. `develop`와 `main`은 `--no-ff` 병합만.
- 커밋: `type(scope): 한국어 요약`. 예) `docs(readme): 계층별 README 추가`
- 커밋마다 `Docs/branchs/` 기록. 템플릿은 [`COMMIT_TEMPLATE.md`](./Docs/branchs/COMMIT_TEMPLATE.md).
- 규칙 원문: [`AGENTS.md`](./AGENTS.md), [`ReviewForge_인수인계.md`](./ReviewForge_인수인계.md).
- `.env`, Atlas 연결 문자열, `JWT_SECRET` 실값은 커밋하지 않습니다.

## 라이선스

[MIT](./LICENSE)
