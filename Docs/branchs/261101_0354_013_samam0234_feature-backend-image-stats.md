# 커밋 기록 013

## 기본 정보

| 항목 | 내용 |
|------|------|
| 일시 | 2026-11-01 03:54 |
| ID | 013 |
| 작성자 | samam0234 |
| 브랜치 | feature/backend-image-stats |
| 커밋 메시지 | `fix(backend): 이미지 multipart 중계 시 NoClassDefFoundError 수정` |

## 작업 내용

- E2E 에서 사진을 첨부한 분석 요청이 모두 500 으로 실패
  - 원인: `MultipartBodyBuilder` 는 WebClient 용 헬퍼라 `org.reactivestreams.Publisher` 가 필요하지만, 서블릿(webmvc) 클래스패스에는 없음 → `NoClassDefFoundError`
  - 단위 테스트는 `AiClient` 를 목으로 대체해 실제 직렬화 경로를 거치지 않아 놓침
- `LinkedMultiValueMap` + `HttpEntity`(Content-Disposition·Content-Type 지정) 로 교체 → `FormHttpMessageConverter` 가 직렬화
- `MockRestServiceServer` 로 실제 RestClient 직렬화를 거치는 테스트 추가 (text·image 파트, 파일명, Content-Type 확인)

## 변경 파일

| 구분 | 경로 | 설명 |
|------|------|------|
| 수정 | backend/src/main/java/com/reviewforge/service/AiClient.java | multipart 본문 구성 방식 교체 |
| 수정 | backend/src/test/java/com/reviewforge/service/AiClientTest.java | 직렬화 테스트 추가 |

## 검증

- `mvnw.cmd -B test` → 13 tests, 0 failures
- E2E 재확인 결과는 `Docs/vaildates/` 검증 문서에 기록

## 비고 / 다음 작업

- 이 내용은 `Docs/find_debug/261101_multipart_reactive_streams.md` 에도 정리
