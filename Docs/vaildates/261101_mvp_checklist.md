# 261101 MVP 검증 체크리스트

## 자동 테스트

| 대상 | 명령 | 결과 |
|------|------|------|
| ai-server (ML 6 + API 4) | `python -m unittest discover -s tests -t .` | ✅ 10 tests OK |
| backend | `mvnw.cmd -B test` | ✅ BUILD SUCCESS |
| frontend | `npm run lint`, `npm run build` | ✅ 오류 없음 |

## E2E (로컬: docker mongo + Flask + Spring Boot + `next start`)

| 시나리오 | 기대 | 결과 |
|----------|------|------|
| `GET /api/health` | AI 서버 up | ✅ `{"aiServer":"up"}` |
| 비로그인 `GET /api/analyses` | 401 | ✅ |
| 빈 텍스트 분석 | 400 | ✅ |
| Next 회원가입 → 쿠키 발급 | 200 | ✅ |
| 과장 리뷰 분석 | Fake, 저장됨 | ✅ 0.91, `saved=true`, 57ms |
| 구체적 리뷰 분석 | Genuine, 저장됨 | ✅ 0.03, `saved=true`, 15ms |
| `/dashboard` | 본인 기록·이름 표시 | ✅ |
| 중복 가입 | 409 | ✅ |
| 잘못된 비밀번호 | 401 | ✅ |
| 브라우저 `/analyze` | 결과 카드·하이라이트 표시 | ✅ |

## 기획서 성공 기준

- [x] 리뷰 입력 시 5초 이내 분석 결과 반환 (로컬 100ms 미만)
- [x] Gradio 에서 모델 결과 시각화 가능 (`gradio_app.py`, 7860)
- [x] 로그인 후 개인 분석 기록 조회 가능
- [x] 전체 스택 (Next.js → Spring Boot → Flask → MongoDB) 동작 — 로컬 MongoDB 기준, Atlas 연결은 미확인
- [x] Vibe Coding 으로 빠르게 반복 가능한 구조

## 남은 과제

- MongoDB Atlas 실제 연결 확인
- 공개 가짜 리뷰 데이터셋으로 재학습, 사전학습 모델 비교
- 다중 리뷰 입력 UI (Flask 는 `texts` 배치 지원, 백엔드/프론트는 단건만)
