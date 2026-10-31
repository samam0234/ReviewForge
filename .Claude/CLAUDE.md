# Claude Agent 규칙 (ReviewForge)

> **단일 진실 공급원**: 루트 [`AGENTS.md`](../AGENTS.md) 및 [`ReviewForge_인수인계.md`](../ReviewForge_인수인계.md)를 반드시 따르세요.  
> 이 파일은 Claude 전용 추가 지시만 담습니다. 공통 규칙이 변경되면 AGENTS.md를 수정하세요.

## Claude 전용 지침

- 코드 생성 시 Next.js / Spring Boot / Flask 역할을 명확히 분리하세요.
- ML 추론 및 Gradio 관련 로직은 `ai-server/`에만 작성하세요.
- 커밋 메시지와 브랜치 규칙은 AGENTS.md를 100% 준수하세요.
- 사용자 명시적 지시 없이 push / merge 하지 마세요.
- MongoDB 연결 정보는 절대 하드코딩하지 마세요.

---

참고: 이 파일은 `.Claude/` 폴더 또는 `CLAUDE.md`로 사용합니다.
