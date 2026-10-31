# 261101 공개 저장소 전환 · 배포 전 체크리스트

## 저장소 공개 전 (2026-11-01 점검)

| 항목 | 방법 | 결과 |
|------|------|------|
| 전체 이력에 비밀값 없음 | `git log --all -p` 에서 Atlas 연결 문자열(`mongodb+srv://user:pass@`), AWS/GitHub/OpenAI 키, 개인 키, 하드코딩 비밀번호 패턴 검색 | ✅ 발견 없음 |
| `.env` 미추적 | `git ls-files` | ✅ `.env.example` 4개만 추적 |
| 모델·데이터 산출물 미추적 | `.gitignore` 의 `ai-server/ml/artifacts/*` | ✅ `.gitkeep` 만 추적 |
| 큰 파일 없음 | 추적 파일 크기 상위 | ✅ 최대 `package-lock.json` 216KB |
| LICENSE · SECURITY · README | 루트 | ✅ MIT, 제보 절차, 공개용 README |

## 배포 시 필수 설정

| 항목 | 이유 |
|------|------|
| `JWT_SECRET` 을 32바이트 이상 무작위 값으로 설정 | `application.yml` 의 기본값은 **공개 저장소에 노출된 개발용 값**이다. 그대로 두면 누구나 토큰을 위조할 수 있다 |
| `MONGODB_URI` 를 Atlas 연결 문자열로 (환경 변수만) | 코드·설정 파일에 하드코딩 금지 |
| Atlas Network Access 를 서버 IP 로 제한 | `0.0.0.0/0` 금지 |
| `CORS_ORIGINS` 를 실제 프론트 도메인으로 | |
| HTTPS 리버스 프록시 + `x-forwarded-proto` 전달 | 세션 쿠키 `Secure` 플래그 ([find_debug](../find_debug/261101_secure_cookie_http.md)) |
| Flask(5000)·Gradio(7860) 는 내부망만 | AI 서버는 인증이 없다. Spring Boot 만 외부에 연다 |
| 프록시 업로드 한도 6MB 이상 | 앱 제한(5MB 파일 / 6MB 요청)보다 프록시가 작으면 413 메시지가 바뀐다 |

## 기록

| 일시 | 내용 |
|------|------|
| 2026-11-01 | v1.1 기능 브랜치·문서 브랜치 원격 push. `develop`/`main` 병합은 사용자 지시 대기 |
