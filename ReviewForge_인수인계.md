# ReviewForge 에이전트 인수인계 및 규칙

**프로젝트명**: ReviewForge  
**버전**: 1.1 (리뷰 사진 분석 · 점수 계산 공통화 · 통계 집계)  
**작성일**: 2026-11-01  
**기술 스택**: Next.js (App Router) + Spring Boot + Flask + MongoDB Atlas  
**유형**: 미니 프로젝트 (Vibe Coding 대상)  
**ML 핵심**: PyTorch (NLP Classification) + **EfficientNet-B3** (리뷰 사진) + Gradio MVP  
**SSOT**: 루트 `AGENTS.md` (본 문서는 인수인계 및 규칙 원본, AGENTS.md는 이를 가리킴)

---

## 1. 프로젝트 개요

**ReviewForge**는 사용자가 상품/서비스 리뷰 텍스트를 입력하거나 업로드하면 AI가 해당 리뷰가 가짜(스팸, 조작, 과장)일 가능성을 분석하고, 신뢰도 점수와 주요 근거를 제공하는 플랫폼입니다.

**핵심 가치**: “리뷰 한 줄로 진짜인지 가짜인지 바로 판단하고 기록할 수 있는 경험”

### 선정 배경
- 이전 미니 프로젝트들(스토리 생성, 일기 감정 분석, 문서 요약 Q&A, 식물 식별 등)과 중복되지 않는 주제
- 5개 AI/ML 주제 중 제비뽑기로 선정
- NLP 기반 텍스트 분류(가짜 리뷰 탐지) + 데이터 처리 패턴 학습에 적합
- TensorFlow 또는 PyTorch 실습 + Gradio를 통한 빠른 MVP 시각화에 적합
- Next.js(동적 기능 포함) + Spring Boot + Flask 3계층 아키텍처 연습에 적합
- MongoDB Atlas로 사용자 분석 기록 저장 실습

### 목표
1. 리뷰 텍스트 입력 → 가짜 여부 분석 → 신뢰도 점수 및 근거 제공까지 End-to-End 흐름 구현
2. Next.js(UI + 간단한 서버 기능) / Spring Boot(Orchestrator) / Flask(AI/ML Server) 역할 분리 실습
3. Vibe Coding 방식으로 빠르게 동작하는 MVP 완성
4. Gradio를 활용한 ML 모델 결과 및 예시 화면 출력
5. 사용자별 분석 기록 저장 및 간단한 조회 기능 (MongoDB Atlas)

### MVP 범위
- 리뷰 텍스트 입력 (단일 또는 다중 리뷰)
- 리뷰 사진 첨부 (선택, v1.1) — EfficientNet-B3 + 메타데이터 규칙, 원본 미저장
- AI 기반 가짜 리뷰 확률 분석 (신뢰도 점수 0~100)
- 주요 판단 근거 키워드/패턴 하이라이트 (선택)
- 사용자 분석 기록 저장 (날짜, 리뷰 내용, 점수, 결과)
- 간단한 로그인/회원가입 (Next.js 기반 동적 기능)
- Gradio 데모 페이지: 모델 직접 테스트 및 결과 시각화
- 기본 대시보드: 최근 분석 목록 + 전체 기록 기준 통계 (MongoDB 집계, v1.1)

### 제외 범위 (향후 확장)
- 고급 이미지 위변조 포렌식 (픽셀 단위 합성 위치 탐지 등) — v1.1 은 사진 단위 분류만
- 실시간 대량 리뷰 크롤링 및 배치 분석
- 다중 언어 지원 (한국어 외)
- 고급 소셜 로그인 / OAuth
- 리뷰 작성 추천 또는 자동 생성
- 판매자 대시보드 / 통계 리포트
- 모바일 앱

---

## 2. 기술 스택 및 역할

| 레이어 | 기술 | 역할 | 기본 포트 |
|--------|------|------|-----------|
| Frontend | Next.js (App Router) | UI, 리뷰 입력 폼, 결과 표시, 로그인/회원가입, 분석 기록 대시보드, 동적 서버 컴포넌트 | 3000 |
| Backend (Orchestrator) | Spring Boot | 요청 검증, 사용자 인증 연동, 리뷰 데이터 전달, MongoDB 연동, Flask 프록시, 에러 핸들링 | 8080 |
| AI/ML Server | Flask | 텍스트 전처리, 가짜 리뷰 분류 모델 추론 (TensorFlow/PyTorch), 신뢰도 계산, Gradio 통합 | 5000 |
| Database | MongoDB Atlas | 사용자 정보, 분석 기록, 모델 결과 히스토리 저장 | - (클라우드) |
| ML / 데이터 | TensorFlow 또는 PyTorch, Pandas, Gradio | 가짜 리뷰 분류 모델, 데이터 전처리, MVP 결과 시각화 | - |
| 기타 | NextAuth 또는 JWT, RestTemplate / WebClient, Bean Validation | 인증, 서비스 간 통신, 입력 검증 | - |

**ML 모델 규칙 (필수·예외 없음, 2026-11-01 사용자 지시)**:
- 새로 도입하는 머신러닝 모델은 **EfficientNet-B3** 를 사용한다 (torchvision `efficientnet_b3`, ImageNet 사전학습).
- 현재 적용: 리뷰 사진 분류 (`ai-server/ml/image_*.py`). 텍스트 분류기(v1.0 fastText 방식)는 기존 유지.
- 분류 헤드가 학습되지 않은 체크포인트는 서비스에 쓰지 않는다 (없으면 규칙 기반으로 동작).
- 점수 계산은 `ai-server/ml/scoring.py` 한곳에서만 한다. 규칙: [`Docs/guidance/scoring.md`](./Docs/guidance/scoring.md)

**AI/ML 옵션 (MVP 우선순위, v1.0 당시 검토)**:
1. 사전 학습된 BERT 계열 모델 파인튜닝 또는 Hugging Face 텍스트 분류 파이프라인 + 간단한 신뢰도 매핑
2. Amazon 또는 Yelp 가짜 리뷰 데이터셋 기반 Transfer Learning (BERT, DistilBERT 등) with TensorFlow/Keras 또는 PyTorch
3. 규칙 기반 + ML 하이브리드로 시작 (빠른 MVP)

환경 변수는 각 레이어 `.env` / `application.yml` / `.env.example`로 관리. API 키·DB 연결 문자열 절대 커밋 금지.

---

## 3. 시스템 아키텍처

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Next.js   │────▶│   Spring Boot    │────▶│     Flask       │
│  (Frontend) │◀────│  (Orchestrator)  │◀────│  (AI/ML Server) │
└─────────────┘     └──────────────────┘     └─────────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │ MongoDB Atlas│
                     └─────────────┘
```

### 역할 분담 (필수·예외 없음)
| 컴포넌트 | 책임 |
|----------|------|
| **Next.js** | 사용자 인터페이스, 폼 처리, 인증 UI, 대시보드 렌더링. UI/상태 관리 및 간단한 서버 컴포넌트만. |
| **Spring Boot** | API 게이트웨이 역할, 비즈니스 로직, DB 연동, Flask 호출 오케스트레이션, 유효성 검사, 에러 핸들링. 오케스트레이션만. |
| **Flask** | ML 추론 전용, Gradio 인터페이스 제공, 모델 로딩 및 예측, 텍스트 전처리. AI 관련 작업만. |
| **MongoDB Atlas** | User, Analysis 컬렉션. |

### 오케스트레이션 흐름
1. 사용자가 Next.js에서 리뷰 텍스트 입력
2. Next.js → Spring Boot로 전송
3. Spring Boot가 유효성 검사 후 Flask AI 서버 호출
4. Flask에서 모델 추론 → 가짜 확률, 신뢰도 점수, 주요 토큰 반환
5. Spring Boot가 결과를 MongoDB에 저장
6. Next.js에 결과 반환 및 시각화

---

## 4. 폴더 구조 (권장)

```
reviewforge/
├── frontend/                     # Next.js (App Router)
│   ├── app/
│   │   ├── page.tsx
│   │   ├── analyze/
│   │   ├── dashboard/
│   │   └── api/
│   ├── components/
│   │   ├── ReviewForm.tsx
│   │   ├── ResultCard.tsx
│   │   └── Dashboard.tsx
│   ├── package.json
│   └── .env.example
│
├── backend/                      # Spring Boot
│   ├── src/main/java/com/reviewforge/
│   │   ├── controller/
│   │   ├── service/
│   │   ├── repository/
│   │   └── config/
│   ├── src/main/resources/
│   │   └── application.yml
│   ├── pom.xml 또는 build.gradle
│   └── .env.example
│
├── ai-server/                    # Flask + Gradio
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   └── analyze.py
│   │   ├── services/
│   │   │   └── model_service.py
│   │   └── models/
│   ├── requirements.txt
│   ├── gradio_app.py
│   └── .env.example
│
├── Docs/                         # 문서 저장 폴더 (아래 구조 필수)
│   ├── plan/
│   ├── Architecture/
│   ├── branchs/
│   ├── find_debug/
│   ├── guidance/
│   ├── trainings/
│   ├── repeater/
│   ├── vaildates/
│   └── web_management/
│
├── docker-compose.yml            # (선택) 전체 오케스트레이션
├── .env.example
├── AGENTS.md                     # SSOT (본 문서 규칙 요약 + 가리킴)
├── .gitattributes
├── LICENSE
├── SECURITY.md
└── README.md
```

### Docs 폴더 용도 (필수·예외 없음)
| 폴더 | 용도 |
|------|------|
| [plan/](./Docs/plan/) | 초기 기획·로직·DB·배포 계획 |
| [Architecture/](./Docs/Architecture/) | 시스템·계층·데이터 흐름 아키텍처 |
| [branchs/](./Docs/branchs/) | 브랜치·커밋 기록 (**템플릿 필수**) |
| [find_debug/](./Docs/find_debug/) | 작업/실행 디버깅 일일 기록 |
| [guidance/](./Docs/guidance/) | 기능·실행 가이드 |
| [trainings/](./Docs/trainings/) | 학습·연구 정리 |
| [repeater/](./Docs/repeater/) | 서버 연결·인프라 장애와 해결 |
| [vaildates/](./Docs/vaildates/) | 검증·체크리스트 |
| [web_management/](./Docs/web_management/) | 배포 전/배포 시 웹 관리 기록 |

- `Docs/branchs/_template.md` 또는 `COMMIT_TEMPLATE.md`는 절대 삭제하지 않는다.
- 새 문서는 반드시 위 폴더 중 적절한 곳에 배치한다.

---

## 5. API 설계 요약

### Spring Boot API
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/analyze` | 리뷰 텍스트 분석 요청 (JSON) / 텍스트 + 사진 (multipart, v1.1) |
| GET | `/api/analyses` | 사용자 분석 기록 목록 조회 |
| GET | `/api/analyses/stats` | 사용자 전체 기록 통계 (v1.1) |
| GET | `/api/analyses/:id` | 특정 분석 상세 조회 |
| POST | `/api/auth/login` | 로그인 (또는 NextAuth 연동) |
| POST | `/api/auth/register` | 회원가입 |

### Flask AI Server API
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/analyze` | 리뷰 텍스트(+ 선택 사진) → 가짜 확률, 확신도, 키워드, 사진 결과 반환 |
| GET | `/health` | 헬스 체크 (`modelLoaded`, `imageModelLoaded`) |
| Gradio | `/gradio` 또는 별도 포트 | MVP 데모 인터페이스 |

**응답 예시** (JSON):
```json
{
  "fakeProbability": 0.78,
  "confidenceScore": 82,
  "label": "Suspicious",
  "keywords": ["amazing", "best ever", "must buy"],
  "highlights": [...]
}
```

### 데이터 모델 (MongoDB)
- **User**: `{ id, email, name, createdAt }`
- **Analysis**: `{ id, userId, reviewText, fakeProbability, confidenceScore, label, keywords, highlights, textFakeProbability, image, createdAt }` (`image` 는 결과만, 원본 사진 없음)

---

## 6. 공통 규칙 (필수·예외 없음)

### 6.1 커밋 메시지 형식
- **형식**: `type(scope): 한국어 요약`
- type/scope는 **영어**, 제목 요약과 본문은 **한국어**
- 예시:
  - ✅ `feat(frontend): 리뷰 분석 폼 컴포넌트 추가`
  - ✅ `fix(ai-server): 신뢰도 점수 계산 오류 수정`
  - ✅ `docs(rules): 커밋 기록 템플릿 업데이트`
  - ✅ `chore(backend): Spring Boot 의존성 정리`
- ❌ 금지 예시:
  - `added review form`
  - `feat: 리뷰 분석 추가` (scope 누락)
  - `fix(backend): fixed the bug` (영어 본문)

### 6.2 커밋 기록 문서화 (필수)
모든 커밋 시 아래 규칙으로 기록 파일을 생성·커밋한다.
- **경로**: `Docs/branchs/YYMMDD_HHMM_[id]_[이름]_[브랜치].md`
- **예시**: `Docs/branchs/261101_1430_001_WHILE496_feature-analyze.md`
- 템플릿: `Docs/branchs/COMMIT_TEMPLATE.md` 또는 `_template.md`
- 기록 파일도 같은 브랜치에 반드시 커밋한다.

### 6.3 브랜치 전략
- 작업은 **`feature/*`** 에서만 한다.
- `develop` / `main` 은 병합 전용.
- 병합은 `--no-ff` 로 이력을 보존한다.
- **병합 시점**: 브랜치 하나가 끝날 때마다 병합하지 않는다. 요청받은 작업을 전부 커밋한 뒤 한 번에 총 병합하고, **사용자 명시적 지시 없이는 병합하지 않는다**.
- 병합 기록 문서도 총 병합 때 한 번에 작성한다.

### 6.4 되돌리기 어려운 작업 (사전 확인 필수)
- push, 병합, 삭제, 덮어쓰기는 **명시적 지시가 있을 때만** 한다.
- 한 번 승인한 것을 다른 상황에 확장 적용하지 않는다.

### 6.5 SSOT 구조
- 루트 `AGENTS.md`에 공유 규칙을 두고, `.Claude/CLAUDE.md`, `.Grok/GROK.md` 등 에이전트별 파일은 **이를 가리키기만** 한다.
- 규칙을 여러 곳에 중복 작성하지 않는다.

### 6.6 에이전트 인수인계 대상 (필수)
아래 폴더/파일을 프로젝트 루트에 준비한다.
- `.Agents/` (공통)
- `.Claude/CLAUDE.md`
- `.Codex/`
- `.Grok/GROK.md`
- `.Gemini/`
- `.Antigravity/`
- `.Cursor/`
- `.Manus/`

모든 에이전트는 작업 시작 전 `AGENTS.md`를 확인한다.

### 6.7 ML 모델 (필수·예외 없음)
- 머신러닝 모델을 새로 쓸 때는 **EfficientNet-B3** 를 사용한다. (2장 "ML 모델 규칙" 참고)
- ML 추론·학습 코드는 `ai-server/` 에만 둔다. 백엔드·프론트에는 점수 계산을 다시 구현하지 않는다 (통계 집계 제외).

### 6.8 기타 필수 파일
- `.gitattributes`
- `LICENSE`
- `SECURITY.md`
- `README.md`

---

## 7. 개발 로드맵 (Vibe Coding)

### Phase 1: ML MVP (1~2일)
- Flask + Gradio로 가짜 리뷰 분류 데모 구현
- 간단한 사전학습 모델 또는 규칙 기반 + ML 하이브리드로 시작
- 예시 결과 화면 완성

### Phase 2: 백엔드 연동 (1~2일)
- Spring Boot API 구성
- Flask 프록시 및 MongoDB Atlas 연동
- 기본 CRUD

### Phase 3: 프론트엔드 (1~2일)
- Next.js UI + 로그인
- 분석 폼 및 대시보드
- 전체 End-to-End 테스트

### Phase 4: 폴리싱
- 에러 처리, UI 개선, Gradio 임베드 또는 별도 링크

---

## 8. 성공 기준

- [ ] 리뷰 입력 시 5초 이내 분석 결과 반환
- [ ] Gradio에서 모델 결과 시각화 가능
- [ ] 로그인 후 개인 분석 기록 조회 가능
- [ ] 전체 스택 (Next.js → Spring Boot → Flask → MongoDB) 동작
- [ ] Vibe Coding으로 빠르게 반복 가능한 구조

---

## 9. 다음 단계

1. Flask Gradio 프로토타입 먼저 만들기
2. 간단한 가짜 리뷰 데이터셋으로 모델 테스트
3. Spring Boot 기본 프로젝트 생성
4. Next.js 프론트 스켈레톤 구성
5. Docs 구조 및 에이전트 파일 생성
6. `.gitattributes`, `LICENSE`, `SECURITY.md` 작성

**ReviewForge**로 머신러닝 기반 미니 프로젝트를 빠르게 시작해 보세요!

---

## 참고
- 원본 기획서: `Docs/plan/ReviewForge_기획서_v1.0.md`
- 코딩 수칙 및 에이전트 인수인계 필수 가이드: `코딩수칙_및_에이전트인수인계_필수가이드.md`
- SSOT: 루트 `AGENTS.md`
