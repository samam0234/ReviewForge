# backend — Spring Boot

오케스트레이터입니다. 요청을 검증하고, JWT로 사용자를 확인하고, Flask에 분석을 맡긴 뒤, 로그인한 사용자의 결과만 MongoDB에 저장합니다. 텍스트 전처리와 모델 가중치는 여기 없습니다.

| 항목 | 값 |
|------|-----|
| 스택 | Spring Boot 4.1.2, Java 21, Spring Data MongoDB, jjwt 0.13, BCrypt |
| 패키지 | `com.reviewforge` |
| 포트 | 8080 |
| 상위 설명 | [루트 README](../README.md) |
| 스키마·흐름 | [아키텍처](../Docs/Architecture/reviewforge_architecture.md) |

## 실행

```bash
# Windows
mvnw.cmd spring-boot:run
mvnw.cmd -B test

# macOS / Linux
./mvnw spring-boot:run
./mvnw test
```

Maven이 없으면 `mvnw`가 받아 옵니다. MongoDB(`docker compose up -d`)와 Flask(`http://localhost:5000`)가 떠 있어야 분석이 성공합니다. 컨텍스트 테스트는 MongoDB 없이도 통과합니다.

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `SERVER_PORT` | `8080` | |
| `MONGODB_URI` | `mongodb://localhost:27017/reviewforge` | Atlas면 이 값만 교체. 커밋 금지 |
| `AI_SERVER_URL` | `http://localhost:5000` | Flask. 연결 실패·타임아웃은 503 |
| `JWT_SECRET` | 개발용 문자열 | 운영은 32바이트 이상 무작위. HS256 |
| `CORS_ORIGINS` | `http://localhost:3000` | `/api/**` |

예시는 `.env.example`. 앱은 환경 변수를 직접 읽습니다 (`application.yml`).

## API

| Method | Endpoint | 인증 | 동작 |
|--------|----------|------|------|
| POST | `/api/auth/register` | - | 이메일 소문자, 이름, 비밀번호 8~64자. 201 + JWT |
| POST | `/api/auth/login` | - | 실패 시 401, 본문은 이메일/비밀번호를 구분하지 않음 |
| GET | `/api/auth/me` | Bearer | 토큰의 사용자 |
| POST | `/api/analyze` | 선택 | JSON `{text}` 또는 multipart `text` + `image` |
| GET | `/api/analyses?limit=20` | Bearer | 최신순, limit는 1~100으로 자름 |
| GET | `/api/analyses/stats` | Bearer | 내 전체 기록 가중 평균 |
| GET | `/api/analyses/{id}` | Bearer | `id`와 `userId`가 둘 다 맞을 때만 |
| GET | `/api/health` | - | `{status, aiServer: up\|down}` |

오류 본문은 항상 `{"error": "..."}` 입니다.

| 상태 | 언제 |
|------|------|
| 400 | 빈 리뷰, 5000자 초과, JSON 파손, Bean Validation |
| 401 | 기록 조회에 토큰이 없거나 만료·위조 |
| 409 | 이미 있는 이메일 |
| 413 / 415 | 이미지 5MB 초과 / jpeg·png·webp가 아님 |
| 502 | Flask가 4xx·5xx를 돌려줌 |
| 503 | Flask에 연결 불가 또는 5초 안에 응답 없음 |

익명 `POST /api/analyze`는 Flask까지 가고 `saved: false`로 반환합니다. `userId`가 있을 때만 `analyses`에 insert 합니다.

## 패키지

```
src/main/java/com/reviewforge/
├── BackendApplication.java
├── config/          AppProperties, WebConfig (CORS, RestClient 타임아웃, BCrypt)
├── auth/            JwtService (24h), AuthInterceptor → request attribute userId
├── controller/      Auth, Analysis, Health
├── service/         AuthService, AnalysisService, AiClient
├── repository/      User, Analysis, AnalysisStats (Mongo $group)
├── domain/          User, Analysis
├── dto/             요청·응답 레코드, AnalysisStats 평균 계산
└── exception/       ApiException, GlobalExceptionHandler
```

`AuthInterceptor`는 토큰이 유효하면 `userId`만 채웁니다. 거절은 컨트롤러가 합니다. 그래서 분석은 익명으로 열리고 기록 조회는 닫힙니다.

`AiClient`는 Flask `POST /analyze`만 부릅니다. 이미지 바이트는 multipart로 넘기고, 점수 식을 다시 계산하지 않습니다. 통계의 나눗셈·반올림만 `AnalysisDtos.AnalysisStats`에 있고, 식은 [점수 명세](../Docs/guidance/scoring.md) 5절과 같습니다.

## MongoDB

| 컬렉션 | 내용 |
|--------|------|
| `users` | `email`(unique), `name`, `passwordHash`, `createdAt` |
| `analyses` | `userId`(index), 리뷰 텍스트, 확률, 라벨, 키워드, 하이라이트, 선택적 `image` 요약, `createdAt` |

`image` 필드에는 확률·라벨·신호·가로·세로만 있습니다. 픽셀은 저장하지 않습니다.

## 테스트

| 클래스 | 확인하는 것 |
|--------|-------------|
| `BackendApplicationTests` | 컨텍스트 기동 |
| `JwtServiceTest` | 발급·위조·만료 |
| `AnalysisServiceTest` | 익명은 저장 안 함, 로그인 사용자는 저장 |
| `AiClientTest` | Flask 프록시 |

업로드 한도와 예외 매핑의 배경은 `Docs/find_debug/`의 multipart 기록을 보면 됩니다.
