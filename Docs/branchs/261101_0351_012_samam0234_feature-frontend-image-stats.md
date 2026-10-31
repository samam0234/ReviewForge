# 커밋 기록 012

## 기본 정보

| 항목 | 내용 |
|------|------|
| 일시 | 2026-11-01 03:51 |
| ID | 012 |
| 작성자 | samam0234 |
| 브랜치 | feature/frontend-image-stats |
| 커밋 메시지 | `feat(frontend): 리뷰 사진 업로드 및 전체 기록 통계 대시보드` |

## 작업 내용

- 분석 폼에 리뷰 사진(선택) 입력 추가: JPEG/PNG/WEBP, 5MB 이하를 브라우저에서 먼저 검사, "사진 빼기" 버튼
- 사진이 있으면 multipart 로 전송, Route Handler `/api/analyze` 가 multipart·JSON 모두 Spring Boot 로 중계
- `backendFetch` 가 `FormData` 본문을 받으면 Content-Type 을 지정하지 않고 그대로 전송 (boundary 자동)
- 결과 카드: 텍스트·사진 개별 가짜 확률, 사진 신호 목록, EfficientNet-B3 적용 여부 표시
- 대시보드: 통계를 `GET /api/analyses/stats`(전체 기록 집계)로 표시 — 기존에는 최근 20건만으로 평균 계산
  - 목록과 통계를 `Promise.all` 로 병렬 조회, 사진 포함 건수·표의 사진 점수 열 추가

## 변경 파일

| 구분 | 경로 | 설명 |
|------|------|------|
| 수정 | frontend/lib/types.ts | `ImageResult`, `AnalysisStats`, 응답 필드 확장 |
| 수정 | frontend/lib/backend.ts | FormData 본문 지원 |
| 수정 | frontend/app/api/analyze/route.ts | multipart 중계 |
| 수정 | frontend/components/ReviewForm.tsx | 사진 입력·검증 |
| 수정 | frontend/components/ResultCard.tsx | 사진 분석 결과 |
| 수정 | frontend/components/Dashboard.tsx, app/dashboard/page.tsx | 서버 통계 사용 |
| 수정 | frontend/app/globals.css | 파일 입력·사진 결과 스타일 |

## 검증

- `npm run lint` → 오류 없음
- `npm run build` → 성공 (/, /analyze, /dashboard, /login PPR, /api/* 동적)

## 비고 / 다음 작업

- 전체 스택 E2E 는 세 기능 브랜치를 합친 임시 작업 트리에서 확인 후 vaildates 문서에 기록
