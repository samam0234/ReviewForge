"""fastText 방식의 최소 텍스트 분류기 (EmbeddingBag 평균 + 선형층).

logit = w · mean(E[f]) + b 이므로 피처별 기여도(w · E[f] / N)를 정확히 분해할 수 있어
근거 키워드 추출에 그대로 사용한다.
"""
from __future__ import annotations

import torch
from torch import nn


class FakeReviewClassifier(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 32) -> None:
        super().__init__()
        self.embedding = nn.EmbeddingBag(vocab_size, embed_dim, mode="mean")
        self.fc = nn.Linear(embed_dim, 1)

    def forward(self, ids: torch.Tensor, offsets: torch.Tensor) -> torch.Tensor:
        return self.fc(self.embedding(ids, offsets)).squeeze(-1)

    @torch.no_grad()
    def feature_scores(self, ids: list[int]) -> torch.Tensor:
        """각 피처가 '가짜' logit 에 더하는 값 (평균 전, 1/N 미적용)."""
        vectors = self.embedding.weight[torch.tensor(ids, dtype=torch.long)]
        return vectors @ self.fc.weight.squeeze(0)


def collate(batch: list[list[int]]) -> tuple[torch.Tensor, torch.Tensor]:
    offsets = torch.tensor([0] + [len(x) for x in batch[:-1]], dtype=torch.long).cumsum(0)
    ids = torch.tensor([i for x in batch for i in x], dtype=torch.long)
    return ids, offsets
