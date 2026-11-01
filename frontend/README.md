# frontend — Next.js

브라우저가 보는 ReviewForge입니다. 리뷰 입력, 결과 카드, 로그인, 대시보드를 그리고, `/api/*` Route Handler가 Spring Boot로 요청을 넘깁니다. 모델 호출과 MongoDB 접근은 이 폴더에 없습니다.

| 항목 | 값 |
|------|-----|
| 스택 | Next.js 16.4.3, React 19.3, TypeScript, App Router |
| 포트 | 3000 |
| 상위 설명 | [루트 README](../README.md) |
| 실행 전체 | [Docs/guidance/run_local.md](../Docs/guidance/run_local.md) |

## 실행

```bash
cp .env.example .env.local
npm install
npm run dev          # http://localhost:3000
npm run lint
npm run build && npm run start
```

| 변수 | 기본값 | 노출 |
|------|--------|------|
| `BACKEND_URL` | `http://localhost:8080` | 서버 전용. 브라우저 번들에 넣지 않음 |
| `NEXT_PUBLIC_GRADIO_URL` | `http://localhost:7860` | 홈의 Gradio 링크. 클라이언트에 노출됨 |

Spring Boot와 Flask가 먼저 떠 있어야 분석·대시보드가 동작합니다.

## 화면

| 경로 | 파일 | 설명 |
|------|------|------|
| `/` | `app/page.tsx` | 소개와 이동 링크 |
| `/analyze` | `app/analyze/page.tsx` | `ReviewForm`. 텍스트(최대 5000자), 예시 2개, 선택 사진 |
| `/login` | `app/login/page.tsx` | `AuthForm`. 로그인·회원가입 탭 |
| `/dashboard` | `app/dashboard/page.tsx` | 세션이 없으면 `/login`으로 보냄 |

레이아웃(`app/layout.tsx`)의 헤더는 항상 있고, 오른쪽 사용자 메뉴만 쿠키를 읽습니다. Cache Components가 켜져 있어서 쿠키를 읽는 컴포넌트(`UserMenu`, 대시보드 본문)는 `<Suspense>` 안에 있습니다.

## 세션

JWT는 브라우저 JavaScript가 읽지 못합니다.

1. `POST /api/auth/login` 또는 `/register`가 Spring Boot에 인증을 맡깁니다.
2. 응답의 `token`을 httpOnly 쿠키 `rf_token`으로 저장합니다 (`lib/session.ts`). 수명 24시간, `SameSite=Lax`.
3. `secure`는 요청이 HTTPS이거나 `x-forwarded-proto: https`일 때만 켭니다. HTTP 로컬에서 항상 Secure로 두면 쿠키가 다시 안 갑니다.
4. 이후 `/api/analyze`와 대시보드의 서버 호출이 `Authorization: Bearer`로 붙입니다.
5. `POST /api/auth/logout`이 쿠키를 지웁니다.

익명 분석은 가능합니다. 그때 결과의 `saved`는 `false`이고 대시보드에는 안 쌓입니다.

## 폴더

```
frontend/
├── app/
│   ├── page.tsx, analyze/, login/, dashboard/
│   ├── api/analyze/route.ts          JSON·multipart를 백엔드로 전달
│   └── api/auth/{login,register,logout}/
├── components/
│   ├── ReviewForm.tsx                클라이언트. 제출·로딩·오류
│   ├── ResultCard.tsx                서버 컴포넌트. 확률 바, 근거 하이라이트
│   ├── Dashboard.tsx                 최근 목록과 통계 요약
│   ├── AuthForm.tsx, LogoutButton.tsx, UserMenu.tsx
├── lib/
│   ├── backend.ts                    BACKEND_URL fetch, 오류를 {error}로 맞춤
│   ├── session.ts                    쿠키 읽기·쓰기
│   └── types.ts                      Analysis, User, Label
├── .env.example
└── next.config.ts                    cacheComponents, partialPrefetching
```

`ResultCard`는 응답의 `highlights[].text`를 원문에서 찾아 `<mark>`로 칠합니다. 이유 문구는 `title` 툴팁입니다.

## 이 폴더에서 지키는 것

- Flask URL을 프론트에 하드코딩하지 않습니다. AI 주소는 Spring Boot의 `AI_SERVER_URL`입니다.
- 비밀번호, JWT, MongoDB URI를 클라이언트 상태로 두지 않습니다.
- 새 페이지에서 `cookies()`를 쓰면 `<Suspense>` 경계 안으로 넣습니다. 레이아웃 최상위에서 await 하면 화면 전체가 요청을 기다립니다.
