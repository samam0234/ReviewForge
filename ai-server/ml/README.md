# ml — 학습과 추론

가짜 리뷰 점수가 계산되는 곳입니다. Flask와 Gradio는 이 패키지를 import 할 뿐, 식을 따로 갖지 않습니다. 명령은 `ai-server` 디렉터리에서 `python -m ml....` 로 실행합니다.

점수 식의 설명과 예시는 [Docs/guidance/scoring.md](../../Docs/guidance/scoring.md)가 원본이고, 구현은 `scoring.py` 한 파일입니다.

## 파일

| 파일 | 역할 |
|------|------|
| `scoring.py` | `hybrid`, `fuse`, `summarize`, 라벨, 확신도. 텍스트·사진이 여기를 거침 |
| `preprocess.py` | 소문자·공백 정리, 단어 토큰, 한글 음절 bigram, 어휘 사전 |
| `model.py` | `EmbeddingBag(mean)` + `Linear`. 피처별 기여도를 분해할 수 있는 구조 |
| `rules.py` | 텍스트 규칙. 느낌표, 과장어, 홍보 문구, 단어 반복, 짧은 무정보 리뷰 |
| `train.py` | 텍스트 학습. CSV `text,label` (1 가짜, 0 진짜) |
| `predict.py` | 텍스트 모델 + 규칙. 체크포인트가 없으면 규칙만 |
| `image_model.py` | torchvision EfficientNet-B3, 입력 300px, ImageNet 사전학습 |
| `image_rules.py` | EXIF, 해상도, 단색·흰 배경 등 메타데이터 규칙 |
| `image_train.py` | `genuine/`, `fake/` ImageFolder 학습 |
| `image_predict.py` | 사진 확률. `image_model.pt`가 없으면 규칙만 (`source: rules`) |
| `metrics.py` | accuracy, precision, recall, f1, ROC-AUC |
| `data/reviews_seed.csv` | 시드 55건. 동작 확인용이며 성능 수치가 일반화 성능을 뜻하지 않음 |

## 학습

```bash
cd ai-server
python -m ml.train
python -m ml.train --data ml/data/my_reviews.csv --epochs 80

python -m ml.image_train --data ml/data/images
python -m ml.image_train --data ml/data/images --unfreeze --lr 3e-4
```

산출물은 `ml/artifacts/` 입니다.

| 파일 | 내용 |
|------|------|
| `model.pt` | 텍스트 가중치 + 어휘 |
| `metrics.json` | 텍스트 학습 지표 |
| `image_model.pt` | EfficientNet-B3 헤드(와 선택적 백본) |
| `image_metrics.json` | 사진 학습 지표 |

이 네 파일은 `.gitignore`에 있습니다. 클론한 뒤 `python -m ml.train`을 한 번 돌려야 텍스트 `source`가 `hybrid`가 됩니다. 사진 체크포인트는 데이터를 모은 뒤에만 생깁니다. ImageNet 가중치(약 47MB)는 처음 학습 때 `~/.cache/torch/hub/checkpoints/`로 받습니다.

기본 텍스트 학습은 Adam `lr=0.01`, `weight_decay=1e-3`, 60 epoch, batch 8, 층화 80/20, seed 42, 손실은 클래스 비율을 반영한 `BCEWithLogitsLoss(pos_weight)`입니다. 시드 검증(11건)은 accuracy 0.91, f1 0.89, ROC-AUC 0.93입니다. 데이터 55건이라 참고 수치입니다.

## 추론이 합쳐지는 순서

1. 텍스트: 모델 확률 `m`과 규칙 점수 `r` → `hybrid` → `t`
2. 사진이 있으면 같은 `hybrid`로 `i`. 학습된 체크포인트가 없으면 `m` 없이 규칙만
3. `fuse`: `p = max(t, (1-w)·t + w·i)`. 학습된 사진 모델이면 `w=0.30`, 규칙만이면 `w=0.15`
4. `summarize`: `p`를 소수 4자리로 맞춘 뒤 그 값으로 확신도와 라벨을 같이 냄

키워드는 규칙에 걸린 문구와, 선형층 기여도가 큰 단어 상위 5개입니다.

## 테스트

`ai-server`에서 `python -m unittest discover -s tests -t .`. `test_scoring.py`가 경계값(`0.69996` → Fake)과 융합이 텍스트 점수를 내리지 않는지를 고정합니다.
