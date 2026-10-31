# 커밋 기록 011

## 기본 정보

| 항목 | 내용 |
|------|------|
| 일시 | 2026-11-01 03:48 |
| ID | 011 |
| 작성자 | samam0234 |
| 브랜치 | feature/backend-image-stats |
| 커밋 메시지 | `feat(backend): 리뷰 이미지 중계 및 전체 기록 통계 집계 API 추가` |

## 작업 내용

- `POST /api/analyze` 를 `consumes` 로 분리: JSON(기존) + multipart(`text` + 선택 `image`)
  - 이미지 검증: 5MB 이하, `image/jpeg`·`image/png`·`image/webp` 만 허용 (415 / 413)
  - multipart 텍스트도 JSON 경로와 같은 규칙(공백 금지, 5000자)으로 검증
  - 원본 이미지는 Flask 로 넘기기만 하고 저장하지 않음, 결과(`image`)와 텍스트 단독 점수(`textFakeProbability`)만 저장
- Flask 400·413 오류 메시지를 사용자에게 그대로 전달 (기존: 모두 502 "AI 서버 오류")
- `GET /api/analyses/stats` 추가: MongoDB `$group` 으로 라벨별 건수·합계를 한 번에 집계
  - 평균은 라벨별 합계를 더한 뒤 전체 건수로 나눈 **가중 평균** (라벨별 평균의 평균이 아님)
  - 기존 대시보드는 최근 20건만으로 평균을 냈음 → 전체 기록 기준으로 정정
  - 반올림: 가짜 확률 소수 4자리, 확신도 소수 1자리 (HALF_UP)
- `spring.servlet.multipart` 제한 5MB / 6MB, 초과 시 413

## 변경 파일

| 구분 | 경로 | 설명 |
|------|------|------|
| 수정 | backend/.../domain/Analysis.java | `textFakeProbability`, `ImageResult image` |
| 수정 | backend/.../dto/AnalysisDtos.java | AI 응답·응답 DTO 확장, `LabelBucket`, `AnalysisStats` |
| 추가 | backend/.../repository/AnalysisStatsRepository(Impl).java | 집계 커스텀 조각 |
| 수정 | backend/.../controller/AnalysisController.java | multipart 분석, `/analyses/stats` |
| 수정 | backend/.../service/AiClient.java, AnalysisService.java | multipart 중계, 검증, 오류 변환 |
| 수정 | backend/.../exception/GlobalExceptionHandler.java | 업로드 초과 413 |
| 수정 | backend/src/main/resources/application.yml | multipart 제한 |
| 추가/수정 | backend/src/test/.../AiClientTest.java, AnalysisServiceTest.java | 테스트 6건 추가 |

## 검증

- `mvnw.cmd -B test` → 12 tests, 0 failures (BackendApplicationTests 1, JwtServiceTest 3, AiClientTest 2, AnalysisServiceTest 6)

## 비고 / 다음 작업

- 프론트엔드에서 이미지 업로드·통계 API 사용 (feature/frontend-image-stats)
- 실제 MongoDB 집계 동작은 E2E 에서 확인
