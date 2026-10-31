# ReviewForge 기획서 v1.0

**AI 기반 가짜 리뷰 탐지 및 신뢰도 분석 플랫폼**

| 항목 | 내용 |
|------|------|
| 프로젝트명 | ReviewForge |
| 버전 | 1.0 |
| 작성일 | 2026-11-01 |
| 기술 스택 | Next.js + Spring Boot + Flask |
| 데이터베이스 | MongoDB Atlas |
| 유형 | 미니 프로젝트 (Vibe Coding 대상) |
| ML 핵심 | TensorFlow / PyTorch (NLP Classification) + Gradio MVP |

---

## 1. 프로젝트 개요

**ReviewForge**는 사용자가 상품/서비스 리뷰 텍스트를 입력하거나 업로드하면 AI가 해당 리뷰가 가짜(스팸, 조작, 과장)일 가능성을 분석하고, 신뢰도 점수와 주요 근거를 제공하는 플랫폼입니다.

핵심 가치는 **“리뷰 한 줄로 진짜인지 가짜인지 바로 판단하고 기록할 수 있는 경험”**입니다.

### 선정 배경
- 이전 미니 프로젝트들(스토리 생성, 일기 감정 분석, 문서 요약 Q&A, 식물 식별, 소셜 미디어 콘텐츠 생성, 음식 사진 칼로리 분석 등)과 중복되지 않는 주제
- 5개 AI/ML 주제 중 제비뽑기로 선정
- NLP 기반 텍스트 분류(가짜 리뷰 탐지) + 데이터 처리 패턴 학습에 적합
- TensorFlow 또는 PyTorch 실습 + Gradio를 통한 빠른 MVP 시각화에 적합
- Next.js(동적 기능 포함) + Spring Boot + Flask 3계층 아키텍처 연습에 적합
- MongoDB Atlas로 사용자 분석 기록 저장 실습

### 선정된 5개 후보 주제
1. AI 피부 트러블 및 피부 타입 분석기
2. AI 스마트 홈 에너지 이상 탐지 및 최적화
3. AI 코드 품질 분석 및 리팩토링 제안기
4. AI 얼굴 표정 기반 감정 인식 미러
5. **AI 가짜 리뷰 탐지 및 신뢰도 분석기** ✅

---

## 2. 목표 및 범위

### 목표
1. 리뷰 텍스트 입력 → 가짜 여부 분석 → 신뢰도 점수 및 근거 제공까지 End-to-End 흐름 구현
2. Next.js(UI + 간단한 서버 기능) / Spring Boot(Orchestrator) / Flask(AI/ML Server) 역할 분리 실습
3. Vibe Coding 방식으로 빠르게 동작하는 MVP 완성
4. Gradio를 활용한 ML 모델 결과 및 예시 화면 출력
5. 사용자별 분석 기록 저장 및 간단한 조회 기능 (MongoDB Atlas)

### 범위 (MVP)
- 리뷰 텍스트 입력 (단일 또는 다중 리뷰)
- AI 기반 가짜 리뷰 확률 분석 (신뢰도 점수 0~100)
- 주요 판단 근거 키워드/패턴 하이라이트 (선택)
- 사용자 분석 기록 저장 (날짜, 리뷰 내용, 점수, 결과)
- 간단한 로그인/회원가입 (Next.js 기반 동적 기능)
- Gradio 데모 페이지: 모델 직접 테스트 및 결과 시각화
- 기본 대시보드: 최근 분석 목록 및 평균 신뢰도 요약

### 제외 범위 (향후 확장)
- 이미지 포함 리뷰 분석 (사진 조작 탐지)
- 실시간 대량 리뷰 크롤링 및 배치 분석
- 다중 언어 지원 (한국어 외)
- 고급 소셜 로그인 / OAuth
- 리뷰 작성 추천 또는 자동 생성
- 판매자 대시보드 / 통계 리포트
- 모바일 앱

---

## 3. 기술 스택

| 레이어 | 기술 | 역할 |
|--------|------|------|
| Frontend | Next.js (App Router) | UI, 리뷰 입력 폼, 결과 표시, 로그인/회원가입, 분석 기록 대시보드, 동적 서버 컴포넌트 |
| Backend (Orchestrator) | Spring Boot | 요청 검증, 사용자 인증 연동, 리뷰 데이터 전달, MongoDB 연동, Flask 프록시, 에러 핸들링 |
| AI/ML Server | Flask | 텍스트 전처리, 가짜 리뷰 분류 모델 추론 (TensorFlow/PyTorch), 신뢰도 계산, Gradio 통합 |
| Database | MongoDB Atlas | 사용자 정보, 분석 기록, 모델 결과 히스토리 저장 |
| ML / 데이터 | TensorFlow 또는 PyTorch, Pandas, Gradio | 가짜 리뷰 분류 모델, 데이터 전처리, MVP 결과 시각화 |
| 기타 | NextAuth 또는 JWT, RestTemplate / WebClient, Bean Validation | 인증, 서비스 간 통신, 입력 검증 |

### AI/ML 관련 기술 옵션
- **가짜 리뷰 탐지**: Amazon 또는 Yelp 가짜 리뷰 데이터셋 기반 Transfer Learning (BERT, DistilBERT 등) with TensorFlow/Keras 또는 PyTorch + Hugging Face
- **전처리**: Pandas로 데이터 정제, 토큰화, 레이블 처리
- **MVP 추천**: 사전 학습된 BERT 계열 모델 파인튜닝 또는 Hugging Face 텍스트 분류 파이프라인 + 간단한 신뢰도 매핑
- **Gradio**: 모델 추론 결과, 신뢰도 점수, 예시 리뷰 및 하이라이트 출력 화면

---

## 4. 시스템 아키텍처 및 오케스트레이션

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

### 역할 분담
- **Next.js**: 사용자 인터페이스, 폼 처리, 인증 UI, 대시보드 렌더링
- **Spring Boot**: API 게이트웨이 역할, 비즈니스 로직, DB 연동, Flask 호출 오케스트레이션
- **Flask**: ML 추론 전용, Gradio 인터페이스 제공, 모델 로딩 및 예측

---

## 5. 주요 기능 상세

### 5.1 리뷰 분석 플로우
1. 사용자가 리뷰 텍스트 입력
2. Next.js → Spring Boot로 전송
3. Spring Boot가 유효성 검사 후 Flask AI 서버 호출
4. Flask에서 모델 추론 → 가짜 확률, 신뢰도 점수, 주요 토큰 반환
5. Spring Boot가 결과를 MongoDB에 저장
6. Next.js에 결과 반환 및 시각화

### 5.2 Gradio MVP 화면
- 텍스트 입력 박스
- 분석 버튼
- 결과: 가짜 확률 (%), 신뢰도 레이블 (Genuine / Suspicious / Fake), 주요 키워드 하이라이트
- 예시 리뷰 버튼 (진짜/가짜 샘플)

### 5.3 데이터 모델 (MongoDB)
- User: { id, email, name, createdAt }
- Analysis: { id, userId, reviewText, fakeProbability, confidenceScore, label, keywords, createdAt }

---

## 6. 개발 로드맵 (Vibe Coding)

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

## 7. 성공 기준

- [ ] 리뷰 입력 시 5초 이내 분석 결과 반환
- [ ] Gradio에서 모델 결과 시각화 가능
- [ ] 로그인 후 개인 분석 기록 조회 가능
- [ ] 전체 스택 (Next.js → Spring Boot → Flask → MongoDB) 동작
- [ ] Vibe Coding으로 빠르게 반복 가능한 구조

---

## 8. 다음 단계

1. Flask Gradio 프로토타입 먼저 만들기
2. 간단한 가짜 리뷰 데이터셋으로 모델 테스트
3. Spring Boot 기본 프로젝트 생성
4. Next.js 프론트 스켈레톤 구성

**ReviewForge**로 머신러닝 기반 미니 프로젝트를 빠르게 시작해 보세요!
