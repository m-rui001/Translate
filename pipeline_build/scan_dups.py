"""Fuzzy duplicate detector.

An exact-match scan found two repeated paragraphs in 魔戒 book1c03 and stopped there.
Looking at the actual text showed at least four: the overlapping chunk windows were
translated *twice, independently*, so the copies differ by a word or two and exact
comparison never sees them.

    山姆怎么也**无法**用言语描摹…   /   山姆怎么也**没法**用言语描摹…
    佛罗多坐在一旁…**但他**大部分心思…   /   佛罗多坐在一旁…**但**大部分心思…

So the test has to be similarity, not equality. Two paragraphs in one document with
`difflib.SequenceMatcher.ratio() >= 0.80` and at least 60 characters are the same
paragraph translated twice -- natural prose does not repeat itself that closely.

Length-bucketed so this stays linear-ish: a pair is only compared when the lengths are
within 25% of each other, which is what the ratio bound already implies.
"""
from __future__ import annotations

import difflib
import glob
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CJK = re.compile(r"[\u4e00-\u9fff]")
TAG = re.compile(r"<[^>]+>")

MIN_CHARS = 60
MIN_RATIO = 0.80


def near_dups(paras: list[str]) -> list[tuple[int, int, float, str]]:
    """Index pairs of paragraphs that are the same text with small edits."""
    idx = [(i, p) for i, p in enumerate(paras) if len(CJK.findall(p)) >= MIN_CHARS]
    out = []
    for a in range(len(idx)):
        ia, pa = idx[a]
        for b in range(a + 1, len(idx)):
            ib, pb = idx[b]
            # cheap length gate first: ratio <= 2*min/(min+max), so a wide gap cannot pass
            lo, hi = sorted((len(pa), len(pb)))
            if lo / hi < 2 * MIN_RATIO / (1 + MIN_RATIO):
                continue
            r = difflib.SequenceMatcher(None, pa, pb, autojunk=False).ratio()
            if r >= MIN_RATIO:
                out.append((ia, ib, r, pa))
    return out


def texts_final(path: str) -> list[str]:
    t = open(path, encoding="utf-8", errors="replace").read()
    return [p.strip() for p in re.split(r"\n{2,}", t) if p.strip()]


def texts_json(path: str) -> list[str]:
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return []
    if isinstance(d, dict) and isinstance(d.get("texts"), list):
        return [x for x in d["texts"] if isinstance(x, str)]
    return []


def docs_epub(path: str):
    z = zipfile.ZipFile(path)
    for n in sorted(z.namelist()):
        if not n.endswith((".xhtml", ".html")) or "nav" in n or "toc" in n:
            continue
        html = z.read(n).decode("utf-8", "replace")
        m = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
        inner = m.group(1) if m else html
        inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
        inner = re.sub(r"</(?:p|h[1-6]|div|li|blockquote|tr)>|<br\s*/?>", "\n\n", inner)
        yield n, [p.strip() for p in re.split(r"\n{2,}", TAG.sub("", inner)) if p.strip()]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    # source of truth first: the JSON the assembler reads, then the finished books
    targets: list[tuple[str, list[str]]] = []
    for f in sorted(glob.glob(os.path.join(ROOT, "work_*", "**", "*.json"), recursive=True)):
        if f.endswith(".polished.json") or "_backup" in f or "_pre_writeback" in f:
            continue
        t = texts_json(f)
        if t:
            targets.append((os.path.relpath(f, ROOT), t))
    for f in sorted(glob.glob(os.path.join(ROOT, "work_*", "**", "final.txt"), recursive=True)):
        if "_backup" in f:
            continue
        targets.append((os.path.relpath(f, ROOT), texts_final(f)))

    total = 0
    seen_src: set[tuple[str, str]] = set()
    for label, paras in targets:
        for ia, ib, r, pa in near_dups(paras):
            key = (label, pa[:40])
            if key in seen_src:
                continue
            seen_src.add(key)
            total += 1
            print(f"{label}  [{ia}]~[{ib}]  ratio={r:.2f}")
            print(f"    A {paras[ia][:78]!r}")
            print(f"    B {paras[ib][:78]!r}")

    print(f"\n{total} near-duplicate pairs in sources")

    # and the books the reader actually gets
    ep = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "out", "*.epub"))):
        base = os.path.basename(f)
        for doc, paras in docs_epub(f):
            for ia, ib, r, pa in near_dups(paras):
                ep += 1
                print(f"{base}:{doc} [{ia}]~[{ib}] ratio={r:.2f}  {pa[:60]!r}")
    print(f"\n{ep} near-duplicate pairs in ./out")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
