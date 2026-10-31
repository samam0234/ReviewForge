"""규칙 기반 가짜 리뷰 신호. ML 모델과 섞어 쓰는 하이브리드의 규칙 부분."""
from __future__ import annotations

import re
from collections import Counter

from ml.preprocess import normalize, tokenize

HYPE_WORDS = [
    "최고", "인생템", "인생", "강추", "무조건", "대박", "완벽", "후회", "넘버원", "기적",
    "best", "amazing", "perfect", "must buy", "life changing",
]
PROMO_PATTERNS = [
    r"쿠폰", r"할인", r"코드", r"링크", r"카톡", r"문의", r"특가", r"사은품",
    r"https?://", r"www\.", r"\bcode\b", r"\d+\s*%\s*off",
]
_EXCLAIM_RE = re.compile(r"[!！]{2,}")


def rule_signals(text: str) -> dict:
    lowered = normalize(text)
    hits: list[dict] = []

    for match in _EXCLAIM_RE.finditer(text):
        hits.append({"text": match.group(), "reason": "과도한 느낌표", "weight": 0.25})
        break

    found = [w for w in HYPE_WORDS if w in lowered]
    hype = [w for w in found if not any(w != o and w in o for o in found)]
    for word in hype[:3]:
        hits.append({"text": word, "reason": "과장 표현", "weight": 0.12})

    for pattern in PROMO_PATTERNS:
        match = re.search(pattern, lowered)
        if match:
            hits.append({"text": match.group(), "reason": "홍보·유도 문구", "weight": 0.3})
            break

    words = [w for w in tokenize(text) if w[0] not in "!?"]
    repeated = [w for w, c in Counter(words).items() if c >= 3]
    if repeated:
        hits.append({"text": repeated[0], "reason": "같은 단어 반복", "weight": 0.25})

    if not re.search(r"\d", text) and len(lowered) < 25:
        hits.append({"text": "", "reason": "구체적 정보 부족 (짧고 수치 없음)", "weight": 0.1})

    return {"score": min(1.0, sum(h["weight"] for h in hits)), "hits": hits}
