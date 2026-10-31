# 커밋 기록 010

## 기본 정보

| 항목 | 내용 |
|------|------|
| 일시 | 2026-11-01 03:44 |
| ID | 010 |
| 작성자 | samam0234 |
| 브랜치 | feature/ai-image-efficientnet |
| 커밋 메시지 | `feat(ai-server): EfficientNet-B3 리뷰 이미지 분석 및 점수 계산 공통화` |

## 작업 내용

- **점수 계산 공통화** (`ml/scoring.py`): 라벨 임계값·하이브리드 가중치·확신도·융합을 한곳에서 계산
  - 확신도 반올림을 파이썬 `round`(은행가 반올림, 82.5 → 82)에서 사사오입(82.5 → 83)으로 정정
  - 확률을 소수 4자리로 반올림한 값에서 확신도·라벨을 같이 계산해 화면 수치가 서로 어긋나지 않게 함
- **평가 지표 확장** (`ml/metrics.py`): 혼동행렬, ROC-AUC(Mann-Whitney), 클래스 불균형용 `pos_weight`
- **EfficientNet-B3 이미지 분석**
  - `ml/image_model.py`: torchvision `efficientnet_b3` + 1-logit 헤드, 300px / bicubic 전처리
  - `ml/image_train.py`: ImageFolder(`genuine/`, `fake/`) 전이학습, 백본 고정 기본 · `--unfreeze` 미세조정
  - `ml/image_rules.py`: EXIF 편집 프로그램·촬영 기기 정보·저해상도·단색 배경 규칙
  - `ml/image_predict.py`: 체크포인트가 없으면 규칙만 사용 (미학습 헤드는 쓰지 않음)
- **텍스트 + 이미지 융합**: `max(t, (1-w)·t + w·i)` — 이미지는 의심을 올리기만 함, `w` = 0.3(모델) / 0.15(규칙만)
- Flask `/analyze` multipart(`text` + 선택 `image`) 지원, 업로드 6MB 제한(413), `/health` 에 `imageModelLoaded`
- `MODEL_PATH=` 처럼 빈 값이면 `Path("")` 가 현재 디렉터리로 해석되어 로드 실패하던 문제 수정 (`or` 기본값)
- Gradio 데모에 리뷰 사진 입력 추가

## 변경 파일

| 구분 | 경로 | 설명 |
|------|------|------|
| 추가 | ai-server/ml/scoring.py, metrics.py | 점수·지표 공통 모듈 |
| 추가 | ai-server/ml/image_model.py, image_rules.py, image_predict.py, image_train.py | EfficientNet-B3 이미지 분석 |
| 수정 | ai-server/ml/predict.py, train.py | 공통 모듈 사용, pos_weight·ROC-AUC |
| 수정 | ai-server/app/__init__.py, routes/analyze.py, services/model_service.py | multipart·이미지 검증·융합 |
| 수정 | ai-server/gradio_app.py | 이미지 입력 |
| 수정 | ai-server/requirements.txt, .env.example | torchvision, pillow, `IMAGE_MODEL_PATH` |
| 추가/수정 | ai-server/tests/test_scoring.py, test_image.py, test_api.py | 테스트 19건 추가 |

## 검증

- `python -m unittest discover -s tests -t .` → `Ran 29 tests ... OK`
- `python -m ml.train` → val accuracy 0.9091, f1 0.8889, ROC-AUC 0.9333 (이전과 동일 정확도, 지표만 추가)
- `build_model(pretrained=True)` → ImageNet 가중치 47.2MB 다운로드·로드 성공, 파라미터 10,697,769
- CPU 이미지 추론 평균 47ms (1200×900 입력, 5회 평균)

## 비고 / 다음 작업

- 실제 리뷰 사진 데이터셋이 없어 이미지 체크포인트는 아직 학습하지 않음 → 그동안 이미지 점수는 규칙 기반
- 백엔드·프론트엔드에서 이미지 업로드 중계 필요 (feature/backend-image-stats, feature/frontend-image-stats)
