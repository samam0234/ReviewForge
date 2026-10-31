# 261101 EfficientNet-B3 리뷰 사진 분류기

## 모델 선택

프로젝트 규칙: **ML 모델을 쓸 때는 EfficientNet-B3 를 사용한다.** 리뷰 사진(판매자 연출 사진·도용·합성·과도 편집 vs 실제 구매자 사진) 분류에 적용했다.

| 항목 | 내용 |
|------|------|
| 백본 | torchvision `efficientnet_b3`, `EfficientNet_B3_Weights.IMAGENET1K_V1` |
| 파라미터 | 10,697,769 (헤드 교체 후) |
| 헤드 | `Dropout(0.3)` → `Linear(1536, 1)` — 가짜 확률 1-logit |
| 입력 | 300×300, resize 320 → center crop 300, bicubic, ImageNet mean/std (공식 가중치 전처리와 동일) |
| 학습 증강 | `RandomResizedCrop(300, scale 0.7~1.0)`, 좌우 반전 — 색감·압축 흔적이 근거일 수 있어 색상 변형은 넣지 않음 |
| 손실 | `BCEWithLogitsLoss(pos_weight = 음성/양성)` |
| 최적화 | AdamW lr 1e-3, weight_decay 1e-4, CosineAnnealing |
| 기본 전략 | 백본 고정 + 헤드만 학습 (소량 데이터), 고정한 백본의 BatchNorm 은 eval 모드 유지 |
| 확장 | `--unfreeze` 로 전체 미세조정 (권장 lr 3e-4) |
| 코드 | `ai-server/ml/image_model.py`, `image_train.py`, `image_predict.py` |

## 규칙 신호 (모델과 하이브리드)

| 신호 | 가중치 | 근거 |
|------|--------|------|
| EXIF `Software` 에 편집 프로그램 (Photoshop, Lightroom, Snapseed, Meitu, Canva …) | 0.35 | 보정·합성 흔적 |
| 단색 배경 (가장자리 픽셀 90% 이상이 중앙값 색과 ±16 이내) | 0.30 | 스튜디오 연출 = 판매자 제공 사진 가능성 |
| 저해상도 (짧은 변 400px 미만) | 0.15 | 재가공·캡처 |
| 촬영 기기 정보(EXIF Make/Model) 없음 | 0.10 | 캡처·다운로드 가능성 — 많은 플랫폼이 EXIF 를 지우므로 낮게 둠 |

모델 있음: `0.7 · 모델 + 0.3 · 규칙`, 없음: `0.1 + 0.8 · 규칙`. 텍스트와의 융합은 [점수 계산 명세](../guidance/scoring.md) 3절.

## 현재 상태 (정직한 기록)

- **실제 리뷰 사진 데이터셋이 아직 없어 체크포인트를 학습하지 않았다.** 그동안 서비스의 사진 점수는 규칙만으로 계산되고 응답에 `image.source = "rules"` 로 표시된다.
- 분류 헤드가 학습되지 않은 B3 를 서비스에 쓰지 않는 이유: ImageNet 백본만으로는 "가짜 리뷰 사진" 의미가 없고, 무작위 헤드 출력은 근거 없는 숫자다.

## 확인한 것

| 항목 | 결과 |
|------|------|
| ImageNet 가중치 다운로드·로드 | ✅ 47.2MB, 파라미터 10,697,769 |
| 학습 파이프라인 (합성 이미지 8장, 64px, 1 epoch, `--no-pretrained`) | ✅ 체크포인트 저장 → 로드 → `source = efficientnet_b3+rules` (`tests/test_image.py`) |
| CPU 추론 시간 | 평균 47ms / 장 (1200×900 입력, 5회) — 성공 기준 5초 이내 충족 |

## 다음 실험

1. 데이터 수집: 쇼핑몰 공식 상품 이미지(fake 측 근사) vs 실구매 후기 사진 — 저작권·개인정보 확인 필수
2. 백본 고정(헤드만) → `--unfreeze` 미세조정 순서로 비교, ROC-AUC 와 혼동행렬 기록
3. 사진 비중 `IMAGE_WEIGHT`(0.3) 를 검증 세트로 튜닝
4. 이미지 중복 탐지(perceptual hash)로 도용 사진 신호 추가 검토
