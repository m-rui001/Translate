"""Collect proper-noun variant candidates (no frequency-ratio gate) and snapshot
a context window for each spelling, so a reviewer can decide same/different.

The 8x ratio gate in names_scan.py hid real splits (夏尔吕 909 vs 夏吕斯 408).
Here every pair with >=4 occurrences on both sides and edit distance <=2 is kept;
precision is recovered downstream by LLM adjudication on context.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from names_scan import book_text, collect, lev, lcs


def pairs(cnt: Counter, min_n: int = 4) -> list[tuple]:
    buckets: dict[tuple[int, str], list[str]] = defaultdict(list)
    for w in cnt:
        if 3 <= len(w) <= 10:
            buckets[(len(w), w[0])].append(w)
    out, seen = [], set()
    for (L, first), words in buckets.items():
        for a in words:
            if cnt[a] < min_n:
                continue
            for L2 in (L - 1, L, L + 1):
                for b in buckets.get((L2, first), []):
                    if a == b or cnt[b] < min_n:
                        continue
                    k = tuple(sorted((a, b)))
                    if k in seen:
                        continue
                    if b.startswith(a) or a.startswith(b):
                        continue
                    if lev(a, b) > 2 or lcs(a, b) < max(len(a), len(b)) - 2:
                        continue
                    seen.add(k)
                    out.append((a, b))
    return out


def ctx(text: str, w: str, width: int = 26, k: int = 1) -> str:
    i = text.find(w)
    if i < 0:
        return ""
    return text[max(0, i - width):i + len(w) + width].replace("\n", " ")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:] or sorted(glob.glob("out/*.epub"))
    rows = []
    for p in args:
        t = book_text(p)
        cnt = collect(t)
        book = os.path.basename(p)[:-5]
        for a, b in pairs(cnt):
            major, minor = (a, b) if cnt[a] >= cnt[b] else (b, a)
            rows.append({"book": book, "major": major, "minor": minor,
                         "n_major": cnt[major], "n_minor": cnt[minor],
                         "ctx_major": ctx(t, major), "ctx_minor": ctx(t, minor)})
    rows.sort(key=lambda r: -(r["n_major"] + r["n_minor"]))
    json.dump(rows, open("scratch/name_cands.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("candidates", len(rows))
