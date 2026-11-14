"""Check whether the polish pass renamed proper nouns.

The polish brief says a term that appears in the glossary must be used verbatim. If
polishing replaced 利维坦 with 巨兽, the book's terminology has drifted — and the
footnote anchors that point at those terms stop resolving, which is how this was
noticed in the first place.

This compares every (old, new) paragraph pair and reports proper nouns present in the
old text but absent from the new one. It is a report, not a fix: the correct remedy is
to restore the term in the paragraph, and that decision needs to be per-term, since
some replacements are legitimate.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import Counter

ROOT = "E:/Translate"
BAK = os.path.join(ROOT, "work_polish2", "_backup_polish3")

# Terms worth protecting: multi-character names that are not ordinary vocabulary.
TERMS = {
    "whale": ["利维坦", "莫比—迪克", "裴廓德", "亚哈", "以实玛利", "魁魁格", "斯塔布",
              "弗拉斯克", "斯达巴克", "以利亚", "加百列"],
    "soledad": ["马孔多", "奥雷里亚诺", "布恩迪亚", "梅尔基亚德斯", "乌尔苏拉",
                "何塞·阿尔卡蒂奥", "阿玛兰妲", "蕾梅黛丝", "庇拉尔·特尔内拉"],
    "lotr": ["佛罗多", "山姆", "甘道夫", "阿拉贡", "波罗莫", "咕鲁", "索伦", "夏尔",
             "魔戒", "中土", "洛汗", "刚铎", "精灵", "哈比人"],
}


def paras(t: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]


def units():
    for pat in ("work_whale/out/*/*/final.txt", "work_soledad/out/*/*/final.txt"):
        for f in glob.glob(os.path.join(ROOT, pat)):
            yield "whale" if "work_whale" in f else "soledad", f


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    lost = Counter()
    examples = {}
    checked = 0
    for book, f in units():
        rel = os.path.relpath(f, ROOT).replace(os.sep, "__")
        bak = os.path.join(BAK, rel)
        if not os.path.exists(bak):
            continue
        a, b = paras(open(bak, encoding="utf-8").read()), paras(open(f, encoding="utf-8").read())
        if len(a) != len(b):
            continue
        for x, y in zip(a, b):
            checked += 1
            for term in TERMS.get(book, []):
                if term in x and term not in y:
                    lost[term] += 1
                    examples.setdefault(term, (f, x[:120], y[:120]))
    print(f"paragraphs checked: {checked:,}")
    for term, n in lost.most_common():
        print(f"  {term:12s} {n:5d} lost")
        f, x, y = examples[term]
        print(f"      {os.path.basename(f)}")
        print(f"      OLD: {x}")
        print(f"      NEW: {y}")
    if not lost:
        print("  no protected term was dropped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
