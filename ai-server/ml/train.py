"""가짜 리뷰 분류기 학습 스크립트.

사용법 (ai-server 디렉터리에서):
    python -m ml.train
    python -m ml.train --data ml/data/my_reviews.csv --epochs 80

CSV 형식: text,label  (label: 1=가짜, 0=진짜)
"""
from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import torch
from torch import nn

from ml.model import FakeReviewClassifier, collate
from ml.preprocess import Vocabulary

ML_DIR = Path(__file__).resolve().parent
DEFAULT_DATA = ML_DIR / "data" / "reviews_seed.csv"
DEFAULT_OUT = ML_DIR / "artifacts"


def set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)


def stratified_split(df: pd.DataFrame, val_ratio: float, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    val = df.groupby("label", group_keys=False).sample(frac=val_ratio, random_state=seed)
    return df.drop(val.index), val


def binary_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "accuracy": round(correct / len(y_true), 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


@torch.no_grad()
def predict_labels(model: FakeReviewClassifier, encoded: list[list[int]]) -> list[int]:
    model.eval()
    ids, offsets = collate(encoded)
    return (torch.sigmoid(model(ids, offsets)) >= 0.5).long().tolist()


def train(args: argparse.Namespace) -> dict:
    set_seed(args.seed)
    df = pd.read_csv(args.data).dropna(subset=["text", "label"])
    df["label"] = df["label"].astype(int)
    train_df, val_df = stratified_split(df, args.val_ratio, args.seed)

    vocab = Vocabulary.build(train_df["text"])
    x_train = [vocab.encode(t) for t in train_df["text"]]
    y_train = torch.tensor(train_df["label"].tolist(), dtype=torch.float32)
    x_val = [vocab.encode(t) for t in val_df["text"]]

    model = FakeReviewClassifier(len(vocab), args.embed_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    loss_fn = nn.BCEWithLogitsLoss()

    order = list(range(len(x_train)))
    for epoch in range(1, args.epochs + 1):
        model.train()
        random.shuffle(order)
        total = 0.0
        for start in range(0, len(order), args.batch_size):
            idx = order[start:start + args.batch_size]
            ids, offsets = collate([x_train[i] for i in idx])
            loss = loss_fn(model(ids, offsets), y_train[idx])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total += loss.item() * len(idx)
        if epoch == 1 or epoch % 10 == 0 or epoch == args.epochs:
            print(f"epoch {epoch:3d}  loss {total / len(order):.4f}")

    metrics = {
        "train": binary_metrics(train_df["label"].tolist(), predict_labels(model, x_train)),
        "val": binary_metrics(val_df["label"].tolist(), predict_labels(model, x_val)),
        "samples": {"train": len(train_df), "val": len(val_df)},
        "vocab_size": len(vocab),
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    torch.save(
        {"state_dict": model.state_dict(), "itos": vocab.itos, "embed_dim": args.embed_dim},
        out / "model.pt",
    )
    (out / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"saved -> {out / 'model.pt'}")
    return metrics


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ReviewForge 가짜 리뷰 분류기 학습")
    parser.add_argument("--data", default=str(DEFAULT_DATA))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--embed-dim", type=int, default=32)
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--weight-decay", type=float, default=1e-3)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args(argv)


if __name__ == "__main__":
    train(parse_args())
