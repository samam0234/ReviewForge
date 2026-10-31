"""EfficientNet-B3 기반 리뷰 이미지 분류기 (torchvision 전이학습).

ImageNet 사전학습 백본에 분류 헤드를 1개 logit(가짜 확률)으로 교체한다.
입력 해상도는 B3 기본값 300×300, 전처리는 torchvision 공식 가중치와 같게 맞춘다 (resize 320 → crop 300, bicubic).
"""
from __future__ import annotations

from torch import nn
from torchvision import transforms
from torchvision.models import EfficientNet_B3_Weights, efficientnet_b3

ARCH = "efficientnet_b3"
IMAGE_SIZE = 300
RESIZE_RATIO = 320 / 300
MEAN = (0.485, 0.456, 0.406)
STD = (0.229, 0.224, 0.225)


def build_model(pretrained: bool = False, dropout: float = 0.3) -> nn.Module:
    model = efficientnet_b3(weights=EfficientNet_B3_Weights.IMAGENET1K_V1 if pretrained else None)
    in_features = model.classifier[1].in_features  # 1536
    model.classifier = nn.Sequential(nn.Dropout(dropout, inplace=True), nn.Linear(in_features, 1))
    return model


def freeze_backbone(model: nn.Module) -> None:
    """소량 데이터용: 백본은 고정하고 분류 헤드만 학습한다."""
    for param in model.features.parameters():
        param.requires_grad = False


def eval_transform(size: int = IMAGE_SIZE) -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize(round(size * RESIZE_RATIO), interpolation=transforms.InterpolationMode.BICUBIC),
        transforms.CenterCrop(size),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])


def train_transform(size: int = IMAGE_SIZE) -> transforms.Compose:
    # 색감·압축 흔적이 판단 근거가 될 수 있어 색상 변형은 넣지 않는다.
    return transforms.Compose([
        transforms.RandomResizedCrop(size, scale=(0.7, 1.0), interpolation=transforms.InterpolationMode.BICUBIC),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])
