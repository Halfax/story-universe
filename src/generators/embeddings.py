"""Simple, dependency-free embedding placeholder.

This provides a tiny deterministic embedding based on token hashing
and term frequencies so the code can compute similarity without
pulling in heavy ML libraries. Replace with a real model later.
"""
from typing import List, Sequence
import math


def _tokenize(text: str) -> List[str]:
    if not text:
        return []
    # simple tokenization: lower, split on non-alpha
    import re
    return [t for t in re.findall(r"[a-zA-Z]+", text.lower()) if t]


def embed(text: str) -> List[float]:
    tokens = _tokenize(text)
    if not tokens:
        return []
    freqs = {}
    for t in tokens:
        freqs[t] = freqs.get(t, 0) + 1

    # deterministic hashing into a small vector (size 64)
    dim = 64
    vec = [0.0] * dim
    for tok, count in freqs.items():
        h = abs(hash(tok))
        idx = h % dim
        vec[idx] += count

    # normalize
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b:
        return 0.0
    # dot product (vectors may be different lengths)
    n = min(len(a), len(b))
    dot = sum(a[i] * b[i] for i in range(n))
    return float(dot)
