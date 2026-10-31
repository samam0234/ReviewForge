# 병합 기록 015 (develop → main, v1.1)

## 기본 정보

| 항목 | 내용 |
|------|------|
| 일시 | 2026-11-01 04:28 |
| 작성자 | samam0234 |
| 병합 지시 | "develop -> main 병합 ㄱㄱ" (사용자 지시 원문) |

## 병합 순서

| 순서 | 소스 브랜치 | 대상 브랜치 | 내용 |
|------|-------------|-------------|------|
| 1 | feature/ai-image-efficientnet | develop | EfficientNet-B3 리뷰 사진 분석, 점수 계산 공통화 (PR #3, main 에 먼저 병합됨) |
| 2 | feature/backend-image-stats | develop | 사진 중계 API, 전체 기록 통계, multipart 오류 수정 (PR #1, develop 병합) |
| 3 | feature/frontend-image-stats | main | 사진 업로드 UI, 통계 대시보드 (PR #2, main 병합) |
| 4 | feature/docs-release | main | 공개용 문서, 점수 계산 명세 (PR #4, main 병합) |
| N | develop | main | **이 기록의 병합**: backend 변경을 main 에 반영 (`--no-ff`) |

## 병합 배경

- 1~4 는 PR 의 base 가 `develop` 이 아닌 `main` 으로 잡혀 `main` 에 먼저 들어갔다.
- 그 결과 `develop` 에는 backend 만, `main` 에는 frontend·ai-server·docs 만 있는 상태가 되었다.
- `main` 의 대시보드는 `GET /api/analyses/stats` 를 호출하지만 backend 가 없어 404 가 되므로, backend 를 `main` 에 반영한다.

## 충돌 / 해결

- 없음. `git merge-tree` 로 사전 확인했고, 실제 병합도 자동 병합으로 끝났다.

## 병합 후 검증

| 명령 | 결과 |
|------|------|
| `cd backend && mvnw.cmd -B test` | ✅ 13 tests, 0 failures |
| `cd ai-server && python -m unittest discover -s tests -t .` | ✅ 29 tests OK |

## 남은 작업

- `develop` 이 `main` 보다 뒤처져 있다 (ai-server·frontend·docs 없음). `main` → `develop` 동기화는 사용자 지시 후 진행한다.
- E2E 는 병합 전 작업 트리에서 이미 확인했다 ([v1.1 검증](../vaildates/261101_v1.1_checklist.md)).
