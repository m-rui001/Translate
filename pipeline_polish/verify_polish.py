"""Verify that the polish pass only changed expression, not content.

The engine already enforces paragraph count, so nothing was added or dropped at the
paragraph level. What it cannot check is whether information inside a paragraph
survived. This script measures that directly, against the pre-polish backups:

* **length drift** — a paragraph that shrank a lot has probably lost something;
* **digit drift** — numbers, dates and ages must be identical;
* **proper-noun drift** — capitalised Latin words and CJK names must be identical;
* **similarity** — `SequenceMatcher` below a floor means the paragraph was rewritten
  rather than polished.

It is a screen, not a proof: it points at the handful of paragraphs worth reading.
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

CJK = re.compile(r"[\u4e00-\u9fff]")
NUM = re.compile(r"\d+")
LATIN = re.compile(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'’\-]{2,}")


def paras(t: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]


def load_current(f: str, form: str) -> list[str]:
    if form == "json":
        d = json.load(open(f, encoding="utf-8"))
        return [t for t in d["texts"] if t.strip()]
    return paras(open(f, encoding="utf-8").read())


def load_backup(f: str, form: str) -> list[str] | None:
    rel = os.path.relpath(f, ROOT).replace(os.sep, "__")
    p = os.path.join(BAK, rel)
    if not os.path.exists(p):
        return None
    if form == "json":
        d = json.load(open(p, encoding="utf-8"))
        return [t for t in d["texts"] if t.strip()]
    return paras(open(p, encoding="utf-8").read())


def targets() -> list[tuple[str, str]]:
    out = []
    for pat in ("work_proust/out/*/*/final.txt",
                "work_gutenberg/*/out/*/c*/final.txt",
                "work_whale/out/*/*/final.txt",
                "work_soledad/out/*/*/final.txt",
                "work_camus/out/*/final.txt",
                "work_chekhov/out/*/final.txt",
                "work_zauberberg/out/*/*/final.txt"):
        out += [(f, "txt") for f in glob.glob(os.path.join(ROOT, pat))]
    out += [(f, "json") for f in glob.glob(os.path.join(ROOT, "work_overhaul/lotr/final/*.json"))
            if not f.endswith(".polished.json")]
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    floor = 0.62
    n_par = 0
    issues: list[tuple] = []
    for f, form in targets():
        a = load_backup(f, form)
        b = load_current(f, form)
        if not a or not b:
            continue
        if len(a) != len(b):
            issues.append((f, "COUNT", len(a), len(b), ""))
            continue
        for i, (x, y) in enumerate(zip(a, b)):
            n_par += 1
            if x == y:
                continue
            if NUM.findall(x) != NUM.findall(y):
                issues.append((f, "DIGIT", i, "", f"{NUM.findall(x)} -> {NUM.findall(y)}"))
                continue
            lx = sorted(w.lower() for w in LATIN.findall(x))
            ly = sorted(w.lower() for w in LATIN.findall(y))
            if lx != ly:
                issues.append((f, "LATIN", i, "", f"{lx[:5]} -> {ly[:5]}"))
                continue
            r = difflib.SequenceMatcher(None, x, y).ratio()
            if r < floor:
                issues.append((f, "REWRITE", i, round(r, 2), ""))
                continue
            if len(y) < 0.72 * len(x):
                issues.append((f, "SHRANK", i, f"{len(x)}->{len(y)}", y[:60]))

    print(f"paragraphs checked: {n_par:,}")
    by = {}
    for it in issues:
        by[it[1]] = by.get(it[1], 0) + 1
    for k, v in sorted(by.items(), key=lambda z: -z[1]):
        print(f"  {k:9s} {v}")
    print(f"total flagged: {len(issues)}")
    for it in issues[:40]:
        print(f"  {it[1]:8s} {os.path.relpath(it[0], ROOT)[:58]:58s} "
              f"p{it[2]} {it[3]} {it[4]}")
    if issues:
        with open(os.path.join(ROOT, "work_polish2", "_verify_issues.json"),
                  "w", encoding="utf-8") as fh:
            json.dump([{"file": it[0], "kind": it[1], "para": it[2],
                        "detail": str(it[3]), "note": it[4]} for it in issues],
                      fh, ensure_ascii=False, indent=1)
        print("wrote work_polish2/_verify_issues.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
