# 커밋 기록 005

## 기본 정보

| 항목 | 내용 |
|------|------|
| 일시 | 2026-11-01 01:34 |
| ID | 005 |
| 작성자 | samam0234 |
| 브랜치 | feature/frontend |
| 커밋 메시지 | `feat(frontend): Next.js 분석 폼·결과 카드·로그인·대시보드 구현` |

## 작업 내용

- `create-next-app` (Next.js 16.4, App Router, TypeScript, Cache Components) 기반 스켈레톤
- Route Handler(`/api/analyze`, `/api/auth/{login,register,logout}`)가 Spring Boot 로 중계, JWT 는 httpOnly 쿠키 `rf_token`
- 페이지: 홈, `/analyze`(ReviewForm + ResultCard 하이라이트), `/login`(AuthForm), `/dashboard`(서버 컴포넌트, 최근 20건·평균 요약)
- 세션을 읽는 `UserMenu`, `DashboardContent` 는 `<Suspense>` 안에 배치 (Cache Components 규칙)
- 스캐폴드 기본 이미지/CSS 모듈 제거, 한국어 UI 스타일

## 변경 파일

| 구분 | 경로 | 설명 |
|------|------|------|
| 추가 | frontend/app/** | 페이지·레이아웃·Route Handler |
| 추가 | frontend/components/*.tsx | ReviewForm, ResultCard, Dashboard, AuthForm, UserMenu, LogoutButton |
| 추가 | frontend/lib/*.ts | 백엔드 호출, 세션, 타입 |
| 추가 | frontend/package.json 등 설정 파일, .env.example | 빌드·환경 설정 |

## 검증

- `npm run lint` → 오류 없음
- `npm run build` → 성공 (/, /analyze, /login, /dashboard 부분 사전 렌더링, /api/* 동적)

## 비고 / 다음 작업

- feature/infra-docs 에서 docker-compose(MongoDB) 와 실행 가이드 작성, 전체 E2E 확인
