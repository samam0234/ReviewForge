# 커밋 기록 002

## 기본 정보

| 항목 | 내용 |
|------|------|
| 일시 | 2026-11-01 01:28 |
| ID | 002 |
| 작성자 | samam0234 |
| 브랜치 | feature/ml-training |
| 커밋 메시지 | `feat(ml): PyTorch 가짜 리뷰 분류 모델 학습·추론 코드 추가` |

## 작업 내용

- 시드 데이터셋(55건) 작성
- 전처리(단어 + 한글 bigram), fastText 방식 분류기, 학습 스크립트, 규칙 신호, 하이브리드 추론기 구현
- unittest 6건 추가
- 실험 기록 `Docs/trainings/261101_baseline_model.md`

## 변경 파일

| 구분 | 경로 | 설명 |
|------|------|------|
| 추가 | ai-server/ml/*.py | 전처리·모델·학습·추론·규칙 |
| 추가 | ai-server/ml/data/reviews_seed.csv | 시드 데이터 |
| 추가 | ai-server/ml/artifacts/.gitkeep | 산출물 폴더 (내용은 git 제외) |
| 추가 | ai-server/tests/test_ml.py | 단위 테스트 |
| 추가 | Docs/trainings/261101_baseline_model.md | 학습 기록 |

## 검증

- `python -m ml.train` → val accuracy 0.91, f1 0.89
- `python -m unittest discover -s tests -t .` → 6 tests OK

## 비고 / 다음 작업

- feature/ai-server 에서 Flask API·Gradio 데모가 이 추론기를 사용
