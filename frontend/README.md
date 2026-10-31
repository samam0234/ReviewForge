# ReviewForge Frontend (Next.js)

```bash
cp .env.example .env.local   # BACKEND_URL 등 설정
npm install
npm run dev                  # http://localhost:3000
```

| 경로 | 설명 |
|------|------|
| `/` | 소개 |
| `/analyze` | 리뷰 분석 폼 + 결과 카드 |
| `/login` | 로그인 / 회원가입 |
| `/dashboard` | 내 분석 기록 (로그인 필요) |
| `/api/*` | Spring Boot 로 중계하는 Route Handler (JWT 는 httpOnly 쿠키 `rf_token`) |

전체 실행 방법은 루트 `Docs/guidance/` 를 참고하세요.
