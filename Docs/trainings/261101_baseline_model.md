# 261101 베이스라인 가짜 리뷰 분류기

## 구성

| 항목 | 내용 |
|------|------|
| 코드 | `ai-server/ml/` (preprocess, model, train, predict, rules) |
| 데이터 | `ai-server/ml/data/reviews_seed.csv` — 직접 작성한 시드 55건 (진짜 28 / 가짜 27) |
| 피처 | 단어 토큰 + 한글 음절 bigram + 느낌표/물음표 묶음 |
| 모델 | PyTorch `EmbeddingBag(mean)` → `Linear` (fastText 방식) |
| 학습 | Adam lr=0.01, weight_decay=1e-3, 60 epoch, batch 8, 층화 80/20 분할 |
| 산출물 | `ai-server/ml/artifacts/model.pt`, `metrics.json` (git 제외) |

## 추론 (하이브리드)

- 모델 있음: `fakeProbability = 0.7 × 모델 확률 + 0.3 × 규칙 점수`
- 모델 없음: `fakeProbability = 0.1 + 0.8 × 규칙 점수` (학습 전에도 서버 동작)
- `label`: `< 0.4` Genuine, `< 0.7` Suspicious, 그 이상 Fake
- `confidenceScore`: 판정 확신도 `max(p, 1 − p) × 100`
- 근거 키워드: 선형 구조라 피처별 기여도 `w · E[f] / N` 를 정확히 분해 → 단어별 합산 상위 5개 + 규칙 적중 문구

## 첫 결과 (seed=42)

| 세트 | accuracy | precision | recall | f1 |
|------|----------|-----------|--------|----|
| train (44) | 1.00 | 1.00 | 1.00 | 1.00 |
| val (11) | 0.91 | 1.00 | 0.80 | 0.89 |

시드 데이터가 매우 작아 수치는 동작 확인용일 뿐이다.

## 다음 실험

1. Amazon / Yelp 가짜 리뷰 공개 데이터셋 또는 한국어 리뷰 크롤링 데이터로 교체 (`--data` 옵션)
2. DistilBERT / KoELECTRA 등 사전학습 모델 파인튜닝과 비교
3. 규칙 가중치(`ML_WEIGHT`)를 검증 세트로 튜닝
