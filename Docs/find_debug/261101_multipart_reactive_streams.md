# 261101 사진 첨부 분석이 500 으로 실패 (NoClassDefFoundError)

## 증상

- 텍스트만 보낸 분석은 정상, 사진을 첨부한 multipart 요청만 모두 `500 서버 오류가 발생했습니다.`
- 백엔드 단위 테스트 12건은 모두 통과한 상태였음

## 재현

1. Flask + Spring Boot + Next.js 실행
2. `curl -F 'text=...' -F 'image=@a.png;type=image/png' localhost:3000/api/analyze`

## 원인

```
jakarta.servlet.ServletException: Handler dispatch failed:
java.lang.NoClassDefFoundError: org/reactivestreams/Publisher
```

- `AiClient` 가 Flask 로 보낼 본문을 `org.springframework.http.client.MultipartBodyBuilder` 로 만들었음
- `MultipartBodyBuilder` 는 WebClient(리액티브)용 헬퍼라 Reactive Streams 의 `Publisher` 를 참조하지만,
  이 프로젝트는 `spring-boot-starter-webmvc` 만 써서 클래스패스에 없음
- 단위 테스트는 `AiClient` 를 Mockito 목으로 대체해 실제 직렬화 코드를 한 번도 실행하지 않았음

## 해결

- `LinkedMultiValueMap<String, Object>` 에 `text` 문자열과 `HttpEntity<ByteArrayResource>`(Content-Disposition 파일명 + Content-Type)를 넣어 `FormHttpMessageConverter` 가 직렬화하게 변경
- `MockRestServiceServer` 로 **실제 RestClient 직렬화 경로**를 거치는 테스트 추가 (`AiClientTest.multipartRequestIsSerializedWithTextAndImageParts`)

## 재발 방지

- 외부 호출 클라이언트는 목 대신 `MockRestServiceServer` 로 요청 본문까지 검증한다
- 서블릿 스택에서는 `org.springframework.http.client.reactive`·`MultipartBodyBuilder` 등 WebFlux 계열 API 를 쓰지 않는다
- 기능 브랜치 완료 전 전체 스택 E2E 를 한 번 돌린다 ([v1.1 검증](../vaildates/261101_v1.1_checklist.md))
