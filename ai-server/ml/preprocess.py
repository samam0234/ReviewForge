"""텍스트 정규화·토큰화·피처 사전.

한국어 형태소 분석기 없이도 동작하도록 단어 토큰 + 한글 음절 bigram 을 피처로 쓴다.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable

UNK = "<unk>"
_TOKEN_RE = re.compile(r"[가-힣]+|[a-z0-9]+|[!?]+")
_HANGUL_RE = re.compile(r"^[가-힣]+$")


def normalize(text: str) -> str:
    text = text.lower().strip()
    return re.sub(r"\s+", " ", text)


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(normalize(text))


def word_features(word: str) -> list[str]:
    if word[0] in "!?":
        return [f"p:{word[0]}" if len(word) == 1 else f"p:{word[0]}+"]
    feats = [f"w:{word}"]
    if _HANGUL_RE.match(word) and len(word) >= 2:
        feats.extend(f"c:{word[i:i + 2]}" for i in range(len(word) - 1))
    return feats


@dataclass
class Vocabulary:
    itos: list[str] = field(default_factory=lambda: [UNK])

    def __post_init__(self) -> None:
        self.stoi = {s: i for i, s in enumerate(self.itos)}

    def __len__(self) -> int:
        return len(self.itos)

    @classmethod
    def build(cls, texts: Iterable[str], min_freq: int = 1) -> "Vocabulary":
        counter: Counter[str] = Counter()
        for text in texts:
            for word in tokenize(text):
                counter.update(word_features(word))
        itos = [UNK] + sorted(f for f, c in counter.items() if c >= min_freq)
        return cls(itos)

    def encode_words(self, text: str) -> list[tuple[str, list[int]]]:
        """단어별 피처 id 목록. 사전에 없는 피처는 버린다."""
        result = []
        for word in tokenize(text):
            ids = [self.stoi[f] for f in word_features(word) if f in self.stoi]
            if ids:
                result.append((word, ids))
        return result

    def encode(self, text: str) -> list[int]:
        ids = [i for _, word_ids in self.encode_words(text) for i in word_ids]
        return ids or [0]
