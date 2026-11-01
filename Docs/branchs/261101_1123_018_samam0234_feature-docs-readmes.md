# 커밋 기록 018

## 기본 정보

| 항목 | 내용 |
|------|------|
| 일시 | 2026-11-01 11:23 |
| ID | 018 |
| 작성자 | samam0234 |
| 브랜치 | feature/docs-readmes |
| 커밋 메시지 | `docs(readme): 계층별 README 추가 및 루트 설명 보강` |

## 작업 내용

- 루트 README를 요청 경로, 계층 경계, 화면, 저장소 지도, 스택, 실행, API가 한 화면에서 이어지게 다시 작성
- `frontend/`, `backend/`, `ai-server/`, `ai-server/ml/` README를 각 폴더를 연 사람 기준으로 작성
- `Docs/README.md`에서 코드 README로 가는 링크 추가

## 변경 파일

| 구분 | 경로 | 설명 |
|------|------|------|
| 수정 | README.md | 루트 설명 보강 |
| 수정 | frontend/README.md | Next.js 화면·쿠키·폴더 |
| 추가 | backend/README.md | Spring Boot API·패키지·MongoDB |
| 추가 | ai-server/README.md | Flask·Gradio·환경 변수 |
| 추가 | ai-server/ml/README.md | 학습·추론·점수 합치는 순서 |
| 수정 | Docs/README.md | 코드 README 링크 |

## 검증

- 문서에 적은 경로·엔드포인트·환경 변수를 현재 코드(`ReviewForm`, 컨트롤러, `scoring.py`, `.env.example`)와 대조

## 비고 / 다음 작업

- 이 브랜치를 `develop`에 `--no-ff`로 병합. `main` 병합은 이번 지시 범위 밖
