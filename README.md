# ReviewForge

**AI 기반 가짜 리뷰 탐지 및 신뢰도 분석 플랫폼**

## 빠른 시작

1. 본 프로젝트의 인수인계 및 규칙을 먼저 확인하세요: [`ReviewForge_인수인계.md`](./ReviewForge_인수인계.md)
2. 단일 진실 공급원(SSOT): [`AGENTS.md`](./AGENTS.md)
3. 기획서: [`Docs/plan/ReviewForge_기획서_v1.0.md`](./Docs/plan/ReviewForge_기획서_v1.0.md)

## 기술 스택

- Frontend: Next.js (App Router)
- Orchestrator: Spring Boot
- AI/ML Server: Flask + Gradio
- Database: MongoDB Atlas

## 필수 규칙 요약

- 작업은 `feature/*` 브랜치에서만
- 커밋 메시지: `type(scope): 한국어 요약`
- 모든 커밋 시 `Docs/branchs/`에 기록 파일 생성
- 병합 / push 는 사용자 명시적 지시 후에만

자세한 내용은 인수인계 문서를 참조하세요.
