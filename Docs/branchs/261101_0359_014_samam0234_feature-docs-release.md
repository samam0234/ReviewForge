# 커밋 기록 014

## 기본 정보

| 항목 | 내용 |
|------|------|
| 일시 | 2026-11-01 03:59 |
| ID | 014 |
| 작성자 | samam0234 |
| 브랜치 | feature/docs-release |
| 커밋 메시지 | `docs(release): v1.1 공개용 문서 고도화 및 점수 계산 명세 추가` |

## 작업 내용

- **README** 를 공개 저장소용으로 재작성: 기능, 아키텍처, 빠른 시작, API·응답 예(실제 E2E 값), 모델, 테스트, 문서 색인
- **점수 계산 명세** 신설 (`Docs/guidance/scoring.md`): 하이브리드, 텍스트+사진 융합, 사사오입·라벨 경계, 가중 평균 통계, 학습 지표, 검증 예시
- **아키텍처 v1.2**: 사진 분석 흐름, 대시보드 집계 흐름, `analyses` 스키마, 계층별 업로드 제한
- **로컬 실행 가이드**: EfficientNet-B3 학습 절차·옵션, 환경 변수 표, 통계 API, 오류 코드
- **trainings**: EfficientNet-B3 기록 신설 (체크포인트 미학습 상태를 명시), 베이스라인에 ROC-AUC·혼동행렬 추가
- **vaildates**: v1.1 자동 테스트·E2E 결과와 발견 결함
- **find_debug**: multipart `NoClassDefFoundError` 원인·해결·재발 방지
- **web_management**: 공개 전 비밀값 점검 결과, 배포 필수 설정 (특히 `JWT_SECRET`)
- **SECURITY.md**: 운영 `JWT_SECRET`, 내부망 전용 서비스, 업로드 이미지 처리 정책
- **인수인계 · AGENTS.md · .Agents**: "ML 모델은 EfficientNet-B3" 규칙(6.7) 추가, v1.1 범위·API·데이터 모델 반영, AGENTS.md 의 Docs 링크 경로 정정 (`./plan/` → `./Docs/plan/`)

## 변경 파일

| 구분 | 경로 | 설명 |
|------|------|------|
| 수정 | README.md, SECURITY.md, AGENTS.md, ReviewForge_인수인계.md, .Agents/README.md | 공개용·규칙 반영 |
| 수정 | Docs/README.md, Architecture/reviewforge_architecture.md, guidance/run_local.md, trainings/261101_baseline_model.md | 갱신 |
| 추가 | Docs/guidance/scoring.md | 점수 계산 명세 |
| 추가 | Docs/trainings/261101_efficientnet_b3_image.md | 사진 모델 |
| 추가 | Docs/vaildates/261101_v1.1_checklist.md | 검증 |
| 추가 | Docs/find_debug/261101_multipart_reactive_streams.md | 디버깅 |
| 추가 | Docs/web_management/261101_public_release_checklist.md | 공개·배포 점검 |

## 검증

- 변경한 문서의 상대 링크를 기능 브랜치 파일 목록과 대조 → 깨진 링크 0 (AGENTS.md 기존 9건 정정 후)
- 문서의 수치는 테스트·E2E 실제 출력에서 옮김 (29 / 13 tests, 0.912 · 0.1038 · 0.3304 · 87.5, 47ms)

## 비고 / 다음 작업

- 문서가 참조하는 `ai-server/ml/scoring.py` 등은 기능 브랜치에 있으므로, 총 병합 후 링크가 모두 유효해진다
- 총 병합(`feature/*` → develop → main)은 사용자 지시 후 진행
