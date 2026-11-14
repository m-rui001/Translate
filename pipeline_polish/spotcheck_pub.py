"""Mechanical spot-check of the public-domain batch.

Checks that need no model: leftover foreign script, untranslated Latin runs, repeated
paragraphs, paragraph drift against the source blocks, and wrapper/markdown leaks.
Writes a JSON-lines report plus a human summary; the sampler picks its units from
the same enumeration so both stages agree on what a unit is.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

ROOT = "E:/Translate"
OUT = os.path.join(ROOT, "work_polish2", "reports")

SCRIPT = {
    "cyrillic": re.compile(r"[\u0400-\u04ff]"),
    "greek": re.compile(r"[\u0370-\u03ff]"),
    "hangul": re.compile(r"[\uac00-\ud7af]"),
    "kana": re.compile(r"[\u3040-\u30ff]"),
    "arabic": re.compile(r"[\u0600-\u06ff]"),
}
LATIN_RUN = re.compile(r"[A-Za-z][A-Za-z'\u2019-]*(?:[ ,.;:!?]+[A-Za-z][A-Za-z'\u2019-]*){3,}")
# `**` is bold markup, but `***` is the French convention for a masked name
# ("Mme de ***") and appears verbatim in the source.
LEAK = re.compile(r"<translation>|<source>|</?p>|^\s*#{1,6}\s|(?<!\*)\*\*(?!\*)")
PARA = re.compile(r"\n\s*\n")


def units(books=None):
    for fp in sorted(glob.glob(os.path.join(ROOT, "work_pub", "*", "out", "*", "c*", "final.txt"))):
        if os.path.getsize(fp) == 0:
            continue
        book = os.path.relpath(fp, os.path.join(ROOT, "work_pub")).split(os.sep)[0]
        if books and book not in books:
            continue
        rel = os.path.relpath(fp, os.path.join(ROOT, "work_pub", book, "out"))
        yield book, rel.replace(os.sep, "/")[:-len("/final.txt")], fp


def src_paras(book, cid, i):
    p = os.path.join(ROOT, "work_pub", book, "chunks", cid + ".json")
    if not os.path.exists(p):
        return None
    try:
        spec = json.load(open(p, encoding="utf-8"))
        blocks = spec.get("chunks") or []
        if i >= len(blocks):
            return None
        return sum(1 for b in blocks[i] if isinstance(b, dict) and b.get("type") == "p")
    except Exception:  # noqa: BLE001
        return None


def check(book, key, path):
    text = open(path, encoding="utf-8").read()
    ps = [p.strip() for p in PARA.split(text) if p.strip()]
    issues = []

    for name, rx in SCRIPT.items():
        hits = rx.findall(text)
        if hits:
            m = rx.search(text)
            ctx = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
            issues.append({"kind": "foreign_script", "script": name,
                           "n": len(hits), "ctx": ctx})

    latin = LATIN_RUN.findall(text)
    if latin:
        issues.append({"kind": "latin_run", "n": len(latin), "ctx": latin[0][:120]})

    seen = {}
    for i, p in enumerate(ps):
        if len(p) >= 30:
            seen.setdefault(p, []).append(i)
    dup = {p: v for p, v in seen.items() if len(v) > 1}
    if dup:
        issues.append({"kind": "duplicate_para", "n": len(dup),
                       "ctx": next(iter(dup))[:80]})

    if LEAK.search(text):
        issues.append({"kind": "markup_leak", "n": 1,
                       "ctx": LEAK.search(text).group(0)})

    cid, _, sub = key.rpartition("/")
    try:
        i = int(sub.lstrip("c"))
    except ValueError:
        i = 0
    want = src_paras(book, cid, i)
    if want:
        got = len(ps) - 1 if ps and len(ps[0]) <= 40 else len(ps)
        if abs(got - want) > max(1, round(want * 0.12)):
            issues.append({"kind": "para_drift", "src": want, "zh": got})

    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    if len(text) > 200 and cjk < 0.45 * len(text):
        issues.append({"kind": "low_cjk", "cjk": cjk, "chars": len(text)})

    return {"book": book, "unit": key, "chars": len(text), "paras": len(ps),
            "issues": issues}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", default="")
    ap.add_argument("--jsonl", default=os.path.join(OUT, "pub_spotcheck.jsonl"))
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    books = [b.strip() for b in a.books.split(",") if b.strip()] or None

    os.makedirs(OUT, exist_ok=True)
    n = bad = 0
    by_kind: dict[str, int] = {}
    by_book: dict[str, int] = {}
    rows = []
    for book, key, path in units(books):
        n += 1
        r = check(book, key, path)
        rows.append(r)
        if r["issues"]:
            bad += 1
            by_book[book] = by_book.get(book, 0) + 1
            for it in r["issues"]:
                by_kind[it["kind"]] = by_kind.get(it["kind"], 0) + 1
    with open(a.jsonl, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"units={n} with_issues={bad}")
    for k, v in sorted(by_kind.items(), key=lambda x: -x[1]):
        print(f"  {k:16s} {v}")
    for k, v in sorted(by_book.items(), key=lambda x: -x[1])[:15]:
        print(f"  {k:16s} {v}")
    print("report:", a.jsonl)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
