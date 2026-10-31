# ReviewForge

**AI 기반 가짜 리뷰 탐지 및 신뢰도 분석 플랫폼** — 리뷰 텍스트(와 선택적으로 리뷰 사진)를 넣으면 가짜일 확률, 판정 확신도, 판단 근거를 보여 주고 기록합니다.

> AI-powered fake review detector. Next.js + Spring Boot + Flask (PyTorch, EfficientNet-B3, Gradio) + MongoDB.

| 텍스트 분석 | 사진 분석 | 기록·통계 |
|-------------|-----------|-----------|
| 과장 표현·홍보 문구·반복 패턴 + PyTorch 분류기, 근거 문구 하이라이트 | EfficientNet-B3 전이학습 + EXIF·해상도·배경 규칙 | 로그인 사용자별 기록, 전체 기록 기준 통계 |

## 주요 기능

- **가짜 확률 · 판정 확신도 · 라벨** (`Genuine` / `Suspicious` / `Fake`) — 계산 규칙은 [점수 계산 명세](./Docs/guidance/scoring.md)
- **판단 근거** — 규칙 적중 문구와 모델 기여도가 큰 단어를 하이라이트
- **리뷰 사진 분석 (선택)** — EfficientNet-B3 + 메타데이터 규칙. 사진은 의심을 올리기만 하고, 원본은 저장하지 않음
- **분석 기록 대시보드** — MongoDB 집계로 전체 기록의 가중 평균·라벨 분포
- **Gradio 데모** — 모델을 바로 시험하는 MVP 화면

## 아키텍처

```
브라우저 ─▶ Next.js (3000) ─▶ Spring Boot (8080) ─▶ Flask AI (5000)
            UI · 쿠키 세션       검증 · JWT · 저장       텍스트 + EfficientNet-B3
                                     │
                                     ▼
                              MongoDB (Atlas / 로컬)
```

| 디렉터리 | 역할 | 포트 |
|----------|------|------|
| [`frontend/`](./frontend/) | Next.js 16 (App Router) — UI, 로그인, 사진 업로드, 대시보드 | 3000 |
| [`backend/`](./backend/) | Spring Boot 4.1 (Java 21) — 오케스트레이터, JWT, MongoDB 집계 | 8080 |
| [`ai-server/`](./ai-server/) | Flask + PyTorch + torchvision + Gradio — 추론 전용 | 5000 / 7860 |
| `docker-compose.yml` | 로컬 MongoDB (운영은 MongoDB Atlas) | 27017 |

역할 분리는 엄격합니다: ML 로직은 `ai-server/` 에만, 백엔드는 오케스트레이션만, 프론트는 UI 만. 자세한 구조는 [아키텍처 문서](./Docs/Architecture/reviewforge_architecture.md).

## 빠른 시작

```bash
docker compose up -d --wait                      # 1. MongoDB

cd ai-server                                     # 2. AI 서버
python -m venv .venv && .venv\Scripts\activate   #    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m ml.train                               #    텍스트 모델 (생략 시 규칙 기반)
python -m app.main                               #    http://localhost:5000

cd backend && mvnw.cmd spring-boot:run           # 3. 백엔드 (macOS/Linux: ./mvnw)

cd frontend && cp .env.example .env.local        # 4. 프론트엔드
npm install && npm run dev                       #    http://localhost:3000
```

전체 절차·환경 변수·EfficientNet-B3 학습은 [로컬 실행 가이드](./Docs/guidance/run_local.md).

## API 요약

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/analyze` | JSON `{text}` 또는 multipart `text` + 선택 `image` (JPEG/PNG/WEBP, 5MB) |
| GET | `/api/analyses?limit=20` | 내 최근 기록 (Bearer) |
| GET | `/api/analyses/stats` | 내 전체 기록 통계 (Bearer) |
| GET | `/api/analyses/{id}` | 기록 상세 (Bearer) |
| POST | `/api/auth/register`, `/api/auth/login` | JWT 발급 |
| GET | `/api/auth/me`, `/api/health` | 내 정보, 상태 |

응답 예 (리뷰 `인생템!!! 무조건 사세요 강추` + 흰 배경 사진, 실제 E2E 결과 · `keywords`·`highlights` 생략):

```json
{
  "fakeProbability": 0.912, "confidenceScore": 91, "label": "Fake",
  "textFakeProbability": 0.912,
  "image": { "fakeProbability": 0.42, "label": "Suspicious", "source": "rules",
             "signals": ["단색 배경 — 판매자 제공 연출 사진 가능성"] },
  "saved": true
}
```

## 모델

| 대상 | 모델 | 학습 |
|------|------|------|
| 텍스트 | PyTorch `EmbeddingBag` + `Linear` (단어 + 한글 음절 bigram) | `python -m ml.train` — 시드 55건, val acc 0.91 / ROC-AUC 0.93 |
| 사진 | **EfficientNet-B3** (torchvision, ImageNet 사전학습, 300px) | `python -m ml.image_train --data ml/data/images` — 데이터는 직접 준비 |

사진 모델 체크포인트가 없으면 사진 점수는 메타데이터 규칙만으로 계산하고, 응답의 `image.source` 가 `rules` 로 표시됩니다.
실험 기록: [텍스트 베이스라인](./Docs/trainings/261101_baseline_model.md), [EfficientNet-B3](./Docs/trainings/261101_efficientnet_b3_image.md).

> ⚠️ 시드 데이터가 매우 작아 판정은 **참고용**입니다. 실제 판매·제재 판단에 단독으로 쓰지 마세요.

## 테스트

```bash
cd ai-server && python -m unittest discover -s tests -t .   # 29 tests
cd backend && mvnw.cmd -B test                               # 13 tests
cd frontend && npm run lint && npm run build
```

검증 결과: [v1.1 검증 체크리스트](./Docs/vaildates/261101_v1.1_checklist.md).

## 문서

| 문서 | 내용 |
|------|------|
| [`AGENTS.md`](./AGENTS.md), [`ReviewForge_인수인계.md`](./ReviewForge_인수인계.md) | 에이전트·기여 규칙 (SSOT) |
| [`Docs/`](./Docs/README.md) | 기획, 아키텍처, 가이드, 학습, 검증, 디버깅, 배포 기록 |
| [`SECURITY.md`](./SECURITY.md) | 보안 정책·취약점 제보 |

## 기여 규칙 요약

- 작업은 `feature/*` 브랜치에서만, `develop`/`main` 은 `--no-ff` 병합 전용
- 커밋 메시지: `type(scope): 한국어 요약` (예: `feat(ai-server): 이미지 규칙 추가`)
- 커밋마다 `Docs/branchs/YYMMDD_HHMM_[id]_[이름]_[브랜치].md` 기록 ([템플릿](./Docs/branchs/COMMIT_TEMPLATE.md))

## 라이선스

[MIT](./LICENSE)
