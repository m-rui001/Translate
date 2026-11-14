"""Second-generation proper-noun variant scan.

The first pass required the major spelling to be 8x more frequent than the minor one.
That hid the worst cases: 追忆 had 夏尔吕 909 vs 夏吕斯 408 — a real split that never
reached the reviewer.

Two changes:
1. A candidate must not contain any of the book's 120 most frequent characters.
   Real names are built from rare characters; 我不知 / 说到底 are not names.
2. Pairs are kept when the two spellings behave like the same person — they appear in
   the same paragraphs next to the same third parties (signature Jaccard). That also
   keeps 伊欧墨 / 伊欧玟 apart, because Éomer and Éowyn never share a scene the way
   two spellings of one man do.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
import zipfile
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from names_scan import book_text, collect, lev, lcs

STOP_TOP = 120


def top_chars(text: str, n: int = STOP_TOP) -> set[str]:
    c = Counter(ch for ch in text if "\u4e00" <= ch <= "\u9fff")
    return {ch for ch, _ in c.most_common(n)}


def clean(cnt: Counter, stop: set[str]) -> Counter:
    return Counter({w: n for w, n in cnt.items() if not (set(w) & stop)})


def paragraphs(text: str) -> list[str]:
    return [p for p in text.split("\n") if len(p) > 20]


def signatures(text: str, vocab: set[str], top: int = 25) -> dict[str, Counter]:
    sig: dict[str, Counter] = defaultdict(Counter)
    for p in paragraphs(text):
        here = [w for w in vocab if w in p]
        if len(here) > 12:
            here = sorted(here, key=lambda w: p.count(w), reverse=True)[:12]
        for w in here:
            for o in here:
                if o != w:
                    sig[w][o] += 1
    return {w: Counter(dict(c.most_common(top))) for w, c in sig.items()}


def jac(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    return len(sa & sb) / len(sa | sb)


def pairs(cnt: Counter, min_n: int = 4) -> list[dict]:
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
                    major, minor = (a, b) if cnt[a] >= cnt[b] else (b, a)
                    out.append({"major": major, "minor": minor,
                                "n_major": cnt[major], "n_minor": cnt[minor]})
    out.sort(key=lambda r: -r["n_major"])
    return out


def scan(path: str, min_jac: float = 0.30) -> list[dict]:
    t = book_text(path)
    cnt = clean(collect(t), top_chars(t))
    cands = pairs(cnt)
    if not cands:
        return []
    vocab = {r["major"] for r in cands} | {r["minor"] for r in cands}
    sig = signatures(t, vocab)
    keep = []
    for r in cands:
        j = jac(sig.get(r["major"], Counter()), sig.get(r["minor"], Counter()))
        if j < min_jac:
            continue
        r["jac"] = round(j, 2)
        r["book"] = os.path.basename(path)[:-5]
        keep.append(r)
    keep.sort(key=lambda r: -(r["n_major"] + r["n_minor"]))
    return keep


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:] or sorted(glob.glob("out/*.epub"))
    rows = []
    for p in args:
        rows += scan(p)
    rows.sort(key=lambda r: -(r["n_major"] + r["n_minor"]))
    print(f"{'book':26} {'major':8} {'n':>5} {'minor':8} {'n':>5} {'jac':>4}")
    for r in rows:
        print(f"{r['book'][:26]:26} {r['major']:8} {r['n_major']:5} {r['minor']:8} {r['n_minor']:5} {r['jac']:4}")
    json.dump(rows, open("scratch/name_pairs2.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("total", len(rows))
