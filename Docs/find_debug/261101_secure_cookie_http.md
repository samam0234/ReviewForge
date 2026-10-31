# 261101 로그인 후 분석 기록이 저장되지 않음

## 증상

- `next start`(production) 로 실행 후 회원가입 → 분석 요청 시 응답의 `saved` 가 `false`
- 대시보드 접근 시 로그인 페이지로 이동

## 재현

1. `npm run build && npm run start`
2. HTTP(`http://localhost:3000`) 에서 회원가입 후 `/api/analyze` 호출

## 원인

- `startSession` 이 `secure: process.env.NODE_ENV === "production"` 으로 쿠키를 설정
- production 빌드에서는 항상 `Secure` 쿠키가 되어, HTTP 요청에는 쿠키가 다시 전송되지 않음
  (일부 브라우저는 localhost 를 예외로 허용하지만, 일반 HTTP 호스트와 스크립트 클라이언트에서는 실패)

## 해결

- 요청 프로토콜이 HTTPS 이거나 `x-forwarded-proto: https` 일 때만 `secure` 플래그를 붙이도록 변경 (`frontend/lib/session.ts`)

## 재발 방지

- 운영 배포는 HTTPS 리버스 프록시 뒤에 두고 `x-forwarded-proto` 를 전달한다.
- E2E 확인 시 production 빌드(`next start`)로도 로그인 → 분석 저장 → 대시보드 흐름을 확인한다.
