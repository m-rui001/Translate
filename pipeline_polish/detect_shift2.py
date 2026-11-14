"""Detect paragraph displacement, second attempt.

The first version compared every output paragraph against every backup paragraph and
flagged it when the best match was another slot *and* that match was unique. That
missed the most common case: a chapter where the model returns the right paragraphs
in the wrong order around a short heading, e.g. `["六", <prose>, ...]` coming back as
`[<prose>, ...]` with the heading dropped to the end. Every prose paragraph then has a
near-identical twin elsewhere, so the "unique" test never fires.

This version compares the two sequences position by position using a cheap but
decisive signal: does paragraph *i* resemble paragraph *i* far more than it resembles
its neighbours? A displacement shows up as a strong diagonal offset.
"""
from __future__ import annotations

import difflib
import glob
import json
import os
import re
import sys

ROOT = "E:/Translate"
BAK = os.path.join(ROOT, "work_polish2", "_backup_polish3")
PATTERNS = (
    "work_proust/out/*/*/final.txt",
    "work_gutenberg/*/out/*/c*/final.txt",
    "work_whale/out/*/*/final.txt",
    "work_soledad/out/*/*/final.txt",
    "work_camus/out/*/final.txt",
    "work_chekhov/out/*/final.txt",
    "work_zauberberg/out/*/*/final.txt",
)


def paras(t: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]


def ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def units():
    for pat in PATTERNS:
        for f in glob.glob(os.path.join(ROOT, pat)):
            yield f
    for f in glob.glob(os.path.join(ROOT, "work_overhaul/lotr/final/*.json")):
        if not f.endswith(".polished.json"):
            yield f


def load(path: str) -> list[str] | None:
    if not os.path.exists(path):
        return None
    if path.endswith(".json"):
        d = json.load(open(path, encoding="utf-8"))
        return [t for t in d.get("texts", []) if t.strip()]
    return paras(open(path, encoding="utf-8").read())


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    flagged = []
    checked = 0
    for f in units():
        rel = os.path.relpath(f, ROOT).replace(os.sep, "__")
        a = load(os.path.join(BAK, rel))
        b = load(f)
        if not a or not b or len(a) != len(b):
            continue
        n = len(a)
        bad_at = []
        for i in range(n):
            checked += 1
            same = ratio(a[i], b[i])
            if same >= 0.75:
                continue
            # how much better does this paragraph fit some other slot?
            best_j, best_r = i, same
            for j in range(max(0, i - 3), min(n, i + 4)):
                if j == i:
                    continue
                r = ratio(a[j], b[i])
                if r > best_r:
                    best_j, best_r = j, r
            if best_r >= 0.85 and best_r - same >= 0.30:
                bad_at.append((i, best_j, round(same, 2), round(best_r, 2)))
        if bad_at:
            flagged.append({"file": os.path.relpath(f, ROOT), "n": n,
                            "hits": bad_at[:12], "count": len(bad_at)})
    print(f"paragraphs checked: {checked:,}")
    print(f"units with displacement: {len(flagged)}")
    for it in sorted(flagged, key=lambda z: -z["count"])[:25]:
        print(f"  {it['count']:3d} hits  {it['file']}  e.g. {it['hits'][:3]}")
    if flagged:
        p = os.path.join(ROOT, "work_polish2", "_shift_issues.json")
        json.dump(flagged, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
