# Codex Agent 규칙 (ReviewForge)

> **단일 진실 공급원**: 루트 [`AGENTS.md`](../AGENTS.md) 및 [`ReviewForge_인수인계.md`](../ReviewForge_인수인계.md)를 반드시 따르세요.
> 이 파일은 Codex 전용 추가 지시만 담습니다. 공통 규칙은 여기에 복제하지 않습니다.

## Codex 전용 지침

- 작업 시작 전 `git branch --show-current` 로 `feature/*` 브랜치인지 확인하세요.
- 레이어별 디렉터리(`frontend/`, `backend/`, `ai-server/`) 경계를 넘는 수정은 커밋을 분리하세요.
- 커밋마다 `Docs/branchs/COMMIT_TEMPLATE.md` 기반 기록 파일을 함께 커밋하세요.
