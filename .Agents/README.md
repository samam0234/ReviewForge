# Agents 공통 규칙 (ReviewForge)

모든 에이전트는 아래를 준수합니다.

- SSOT: 루트 `AGENTS.md`
- 상세 인수인계: `ReviewForge_인수인계.md`
- 작업 브랜치: `feature/*` 만
- 커밋 형식: `type(scope): 한국어 요약`
- 커밋 기록: `Docs/branchs/YYMMDD_HHMM_*.md` 필수
- push / merge / 삭제 / 덮어쓰기: 사용자 명시적 지시 후에만
- 역할 분리: Next.js (UI) / Spring Boot (Orchestrator) / Flask (AI/ML) 엄격히 유지
- ML 모델: 새로 도입할 때는 EfficientNet-B3 (상세: `ReviewForge_인수인계.md` 6.7)
