# 커밋 기록 006

## 기본 정보

| 항목 | 내용 |
|------|------|
| 일시 | 2026-11-01 02:10 |
| ID | 006 |
| 작성자 | samam0234 |
| 브랜치 | feature/infra-docs |
| 커밋 메시지 | `fix(frontend): HTTP 환경에서 세션 쿠키가 전송되지 않는 문제 수정` |

## 작업 내용

- E2E 검증 중 발견: production 빌드에서 세션 쿠키가 항상 `Secure` 로 설정되어 HTTP 에서 로그인 상태가 유지되지 않음
- 요청이 HTTPS(또는 `x-forwarded-proto: https`)일 때만 `secure` 적용
- 디버깅 기록 `Docs/find_debug/261101_secure_cookie_http.md`

## 변경 파일

| 구분 | 경로 | 설명 |
|------|------|------|
| 수정 | frontend/lib/session.ts | `startSession(request, auth)` 로 프로토콜 판단 |
| 수정 | frontend/app/api/auth/{login,register}/route.ts | request 전달 |
| 추가 | Docs/find_debug/261101_secure_cookie_http.md | 디버깅 기록 |

## 검증

- `npm run build` 성공
- E2E: 회원가입 → 분석 2건 `saved=true` → `/dashboard` 에 리뷰·이름 표시

## 비고 / 다음 작업

- 같은 브랜치에서 docker-compose 및 실행 가이드 문서 커밋
