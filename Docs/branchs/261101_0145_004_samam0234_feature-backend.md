# 커밋 기록 004

## 기본 정보

| 항목 | 내용 |
|------|------|
| 일시 | 2026-11-01 01:45 |
| ID | 004 |
| 작성자 | samam0234 |
| 브랜치 | feature/backend |
| 커밋 메시지 | `feat(backend): Spring Boot 오케스트레이터 API·인증·MongoDB 연동 구현` |

## 작업 내용

- Spring Boot 4.1.2 / Java 21 타깃 Maven 프로젝트 (start.spring.io 생성, mvnw 포함)
- 인증: 회원가입·로그인(BCrypt), JWT(HS256, 24h) 발급, `AuthInterceptor`가 Bearer 토큰 → `userId` 요청 속성
- 분석: `POST /api/analyze` 검증 → Flask `/analyze` 호출(RestClient, 5초 타임아웃) → 로그인 시 MongoDB 저장
- 조회: `GET /api/analyses?limit=`, `GET /api/analyses/{id}` (본인 기록만)
- `GET /api/health` (AI 서버 상태 포함), 전역 예외 처리(`{"error": "..."}` 형식), CORS(3000)
- 설정 외부화: `application.yml` + 환경 변수(`MONGODB_URI`, `AI_SERVER_URL`, `JWT_SECRET`, `CORS_ORIGINS`)

## 변경 파일

| 구분 | 경로 | 설명 |
|------|------|------|
| 추가 | backend/pom.xml, mvnw, mvnw.cmd, .mvn/ | 빌드 설정 |
| 추가 | backend/src/main/java/com/reviewforge/{config,auth,controller,service,repository,domain,dto,exception} | 애플리케이션 코드 |
| 추가 | backend/src/main/resources/application.yml, backend/.env.example | 설정 |
| 추가 | backend/src/test/... | 컨텍스트·JWT·분석 서비스 테스트 |

## 검증

- `mvnw.cmd -B test` → BUILD SUCCESS (contextLoads, JwtServiceTest 3건, AnalysisServiceTest 2건)

## 비고 / 다음 작업

- 전체 흐름(E2E) 검증은 docker-compose 로 MongoDB 를 띄운 뒤 feature/infra-docs 에서 수행
