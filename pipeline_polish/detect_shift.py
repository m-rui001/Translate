"""Detect paragraph displacement introduced by the polish pass.

A polish pass must leave paragraph *i* as paragraph *i*. The engine enforces the
count, which is not enough: a run of paragraphs can come back one slot out of step
and still have the right length. That is the worst possible failure — the text reads
fine, paragraph by paragraph, while the narrative has been silently scrambled.

The test is per paragraph: compare output paragraph *i* against every backup
paragraph, and flag it when

* its best match is some other index *j != i*,
* that match is very close (>= 0.82), and
* that match is **unique** — exactly one backup paragraph is that similar.

Uniqueness matters because these books repeat lines (chapter epigraphs, refrains,
"他什么也没说。"); without it, every repeated line looks like a shift.
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


def units():
    for pat in PATTERNS:
        for f in glob.glob(os.path.join(ROOT, pat)):
            yield f, "txt"
    for f in glob.glob(os.path.join(ROOT, "work_overhaul/lotr/final/*.json")):
        if not f.endswith(".polished.json"):
            yield f, "json"


def load(path: str, form: str) -> list[str] | None:
    if not os.path.exists(path):
        return None
    if form == "json":
        return [t for t in json.load(open(path, encoding="utf-8"))["texts"] if t.strip()]
    return paras(open(path, encoding="utf-8").read())


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    near = 0.82
    flagged = []
    checked = 0
    for f, form in units():
        rel = os.path.relpath(f, ROOT).replace(os.sep, "__")
        a = load(os.path.join(BAK, rel), form)
        b = load(f, form)
        if not a or not b or len(a) != len(b):
            continue
        for i, y in enumerate(b):
            checked += 1
            if a[i] == y:
                continue
            scores = [(difflib.SequenceMatcher(None, x, y).ratio(), j)
                      for j, x in enumerate(a)]
            top = max(scores)
            if top[1] == i:
                continue                                  # best match is its own slot
            close = [j for s, j in scores if s >= near]
            if len(close) == 1 and top[0] >= near:
                flagged.append({"file": os.path.relpath(f, ROOT), "para": i,
                                "moved_from": top[1], "ratio": round(top[0], 3)})
    print(f"paragraphs checked: {checked:,}")
    print(f"suspect displacements: {len(flagged)}")
    by = {}
    for it in flagged:
        by[it["file"]] = by.get(it["file"], 0) + 1
    for f, n in sorted(by.items(), key=lambda z: -z[1])[:25]:
        print(f"  {n:3d}  {f}")
    if flagged:
        p = os.path.join(ROOT, "work_polish2", "_shift_issues.json")
        json.dump(flagged, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
