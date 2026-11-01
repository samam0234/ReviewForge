# 커밋 기록 020

## 기본 정보

| 항목 | 내용 |
|------|------|
| 일시 | 2026-11-01 12:47 |
| ID | 020 |
| 작성자 | samam0234 |
| 브랜치 | feature/docs-ko-policy |
| 커밋 메시지 | `docs(policy): SECURITY와 LICENSE를 한국어로 작성` |

## 작업 내용

- `SECURITY.md`의 지원 버전, 제보 방법, 개발 수칙, 업로드 사진 정책을 한국어로 옮김
- `LICENSE`의 MIT 허가·조건·보증 부인을 한국어로 옮김. 저작권 표시 `Copyright (c) 2026 WHILE496 / ReviewForge`는 유지

## 변경 파일

| 구분 | 경로 | 설명 |
|------|------|------|
| 수정 | SECURITY.md | 보안 정책 한국어 |
| 수정 | LICENSE | MIT 라이선스 한국어 |

## 검증

- 영어 원문의 항목(제보 48시간, JWT_SECRET, 내부망 포트, 사진 한도, 무보증)이 한국어 본문에 남았는지 대조

## 비고 / 다음 작업

- `develop`에 `--no-ff` 병합 후 `origin/develop` 푸시. `main`은 이번 지시 범위 밖
