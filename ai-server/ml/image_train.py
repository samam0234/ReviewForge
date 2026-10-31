"""EfficientNet-B3 리뷰 이미지 분류기 학습 스크립트 (전이학습).

사용법 (ai-server 디렉터리에서):
    python -m ml.image_train --data ml/data/images
    python -m ml.image_train --data ml/data/images --unfreeze --epochs 15 --lr 3e-4

데이터 형식 (torchvision ImageFolder):
    ml/data/images/genuine/*.jpg   실제 구매자가 찍은 사진
    ml/data/images/fake/*.jpg      판매자 제공·도용·합성·과도 편집 사진

기본값은 ImageNet 사전학습 가중치를 내려받고(최초 1회, 약 47MB) 백본을 고정한 채 헤드만 학습한다.
"""
from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision.datasets import ImageFolder

from ml.image_model import ARCH, IMAGE_SIZE, build_model, eval_transform, freeze_backbone, train_transform
from ml.metrics import evaluate, pos_weight

ML_DIR = Path(__file__).resolve().parent
DEFAULT_DATA = ML_DIR / "data" / "images"
DEFAULT_OUT = ML_DIR / "artifacts"
FAKE_CLASS = "fake"


class FakeTarget:
    """ImageFolder 클래스 인덱스(알파벳순) → 가짜=1.0 / 진짜=0.0. Windows 멀티프로세스 로더를 위해 모듈 수준 클래스로 둔다."""

    def __init__(self, classes: list[str]) -> None:
        self.fake_index = classes.index(FAKE_CLASS)

    def __call__(self, index: int) -> float:
        return float(index == self.fake_index)


def stratified_indices(labels: list[int], val_ratio: float, seed: int) -> tuple[list[int], list[int]]:
    rng = random.Random(seed)
    train_idx, val_idx = [], []
    for cls in sorted(set(labels)):
        idx = [i for i, y in enumerate(labels) if y == cls]
        rng.shuffle(idx)
        n_val = max(1, round(len(idx) * val_ratio)) if len(idx) > 1 else 0
        val_idx += idx[:n_val]
        train_idx += idx[n_val:]
    return train_idx, val_idx


@torch.no_grad()
def predict_probabilities(model: nn.Module, loader: DataLoader) -> tuple[list[int], list[float]]:
    model.eval()
    y_true, probs = [], []
    for images, targets in loader:
        probs += torch.sigmoid(model(images).squeeze(-1)).tolist()
        y_true += [int(t) for t in targets.tolist()]
    return y_true, probs


def train(args: argparse.Namespace) -> dict:
    random.seed(args.seed)
    torch.manual_seed(args.seed)

    probe = ImageFolder(args.data)
    if FAKE_CLASS not in probe.classes or len(probe.classes) != 2:
        raise SystemExit(f"{args.data} 아래에 genuine/ 과 {FAKE_CLASS}/ 두 폴더가 필요합니다. (현재: {probe.classes})")
    target = FakeTarget(probe.classes)
    labels = [int(target(y)) for _, y in probe.samples]
    train_idx, val_idx = stratified_indices(labels, args.val_ratio, args.seed)

    train_set = Subset(ImageFolder(args.data, train_transform(args.image_size), target), train_idx)
    val_set = Subset(ImageFolder(args.data, eval_transform(args.image_size), target), val_idx)
    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True, num_workers=args.workers)
    val_loader = DataLoader(val_set, batch_size=args.batch_size, num_workers=args.workers)

    model = build_model(pretrained=args.pretrained)
    if not args.unfreeze:
        freeze_backbone(model)
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(params, lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(pos_weight([labels[i] for i in train_idx])))

    for epoch in range(1, args.epochs + 1):
        model.train()
        if not args.unfreeze:
            model.features.eval()  # 고정한 백본의 BatchNorm 통계가 바뀌지 않게 한다
        total, seen = 0.0, 0
        for images, targets in train_loader:
            loss = loss_fn(model(images).squeeze(-1), targets.float())
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total += loss.item() * len(targets)
            seen += len(targets)
        scheduler.step()
        print(f"epoch {epoch:3d}  loss {total / max(seen, 1):.4f}")

    metrics = {
        "arch": ARCH,
        "train": evaluate(*predict_probabilities(model, DataLoader(Subset(val_set.dataset, train_idx), batch_size=args.batch_size))),
        "val": evaluate(*predict_probabilities(model, val_loader)) if val_idx else None,
        "samples": {"train": len(train_idx), "val": len(val_idx)},
        "image_size": args.image_size,
        "pretrained": args.pretrained,
        "frozen_backbone": not args.unfreeze,
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    torch.save(
        {"state_dict": model.state_dict(), "arch": ARCH, "image_size": args.image_size, "classes": probe.classes},
        out / "image_model.pt",
    )
    (out / "image_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"saved -> {out / 'image_model.pt'}")
    return metrics


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ReviewForge 리뷰 이미지 분류기 학습 (EfficientNet-B3)")
    parser.add_argument("--data", default=str(DEFAULT_DATA))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--image-size", type=int, default=IMAGE_SIZE)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--unfreeze", action="store_true", help="백본까지 미세조정 (데이터가 충분할 때)")
    parser.add_argument("--no-pretrained", dest="pretrained", action="store_false",
                        help="ImageNet 가중치 없이 무작위 초기화 (오프라인 테스트용)")
    return parser.parse_args(argv)


if __name__ == "__main__":
    train(parse_args())
