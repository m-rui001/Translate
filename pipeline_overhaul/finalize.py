"""Deterministic post-revision cleanup on the final text.

The revision model translates from the source and does not know the book's
chosen names, so it occasionally restores the minority form (白兰地鹿, 法拉米尔).
Those and the few remaining duplicate drafts are fixed here, with no model.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402
from names import MAPS  # noqa: E402

# lotr duplicate-draft second indices are obsolete: the paragraph list has been
# re-indexed since those drafts were dropped, so these indices now point at
# ordinary narrative paragraphs and deleting them would tear holes in chapters.
# Duplicate paragraphs are instead detected structurally -- see drop_dups.
DROP_LOTR: dict[str, list[int]] = {}


def fix_names(book: str) -> int:
    rules = sorted(MAPS[book], key=lambda r: -len(r[0]))
    d = os.path.join(common.WORK, book, "final")
    total = 0
    for fn in sorted(os.listdir(d)):
        p = os.path.join(d, fn)
        ch = common.load_json(p)
        hit = 0
        for i, t in enumerate(ch["texts"]):
            for a, b in rules:
                if a in t:
                    hit += t.count(a)
                    t = t.replace(a, b)
            ch["texts"][i] = t
        if hit:
            total += hit
            common.save_json(p, ch)
    print(f"{book}: {total} name fixes in final")
    return total


def drop_dups(book: str) -> int:
    """Collapse repeated non-text placeholders, e.g. two ``*`` scene breaks.

    Duplicated *prose* is deliberately not dropped here: a repeated narrative
    paragraph deserves a human look, and deleting it silently tears a hole in
    the chapter. Only markers carrying no text are collapsed.
    """
    d = os.path.join(common.WORK, book, "final")
    n = 0
    for fn in sorted(os.listdir(d)):
        p = os.path.join(d, fn)
        ch = common.load_json(p)
        texts, types = list(ch["texts"]), list(ch.get("types") or [])
        keep = [i for i in range(len(texts))
                if not (i and texts[i] == texts[i - 1]
                        and not common.CJK.search(texts[i]))]
        if len(keep) == len(texts):
            continue
        ch["texts"] = [texts[i] for i in keep]
        if types:
            ch["types"] = [types[i] for i in keep]
        common.save_json(p, ch)
        n += len(texts) - len(keep)
        print(f"  dropped {len(texts) - len(keep)} placeholder(s) in {fn[:-5]}")
    return n


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for b in sys.argv[1:] or ["whale", "soledad", "lotr"]:
        fix_names(b)
        if b == "lotr":
            drop_dups(b)
