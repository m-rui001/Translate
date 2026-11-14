
"""Check a proposed name variant against the source text.

The model is good at reading Chinese but it cannot know that Hirst and Hewet are two
different people in The Voyage Out, and it said they were one. The source can tell:
a real variant occurs in chunks whose source names are the same; a false one occurs
next to a different source name. So every pair the model accepted is checked here,
and only pairs whose source evidence agrees are applied.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, "pipeline_fix")
import names_align as NA

NAME = NA.NAME


def book_roots() -> dict[str, str]:
    """Chinese title -> work directory, from the two catalogues."""
    sys.path.insert(0, "pipeline_private")
    sys.path.insert(0, "pipeline_gutenberg")
    import books as pub
    roots = {}
    for m in pub.PUBLIC:
        for base in ("work_pub", "work_gutenberg"):
            d = os.path.join(base, m["key"])
            if os.path.isdir(os.path.join(d, "chunks")):
                roots[m["title_zh"]] = d
                break
    try:
        import books_meta as gm
        for m in getattr(gm, "BOOKS", []):
            d = os.path.join("work_gutenberg", m["key"])
            if os.path.isdir(os.path.join(d, "chunks")):
                roots.setdefault(m["title_zh"], d)
    except Exception:                                            # noqa: BLE001
        pass
    return roots


def source_names(src: str) -> Counter:
    c = Counter()
    for m in NAME.finditer(src):
        w = m.group(0)
        if w not in NA.STOP:
            c[w] += 1
    return c


def evidence(pairs: list[tuple[str, str]], root: str) -> dict:
    units = NA.units(root)
    src_counts = [source_names(src) for src, _z in units]
    out = {}
    for major, minor in pairs:
        um = [i for i, (_s, z) in enumerate(units) if major in z]
        un = [i for i, (_s, z) in enumerate(units) if minor in z]

        def assoc(ids):
            """P(source name | this Chinese spelling), not raw frequency.

            Raw counts in the surrounding chunks are dominated by whoever the book is
            about: every chunk of The Three Musketeers mentions d'Artagnan, so he wins
            for any spelling. The conditional makes the question the right one -- when
            this spelling is on the page, which name is on the page with it?
            """
            c = Counter()
            for i in ids:
                for name in src_counts[i]:
                    c[name] += 1
            if not ids:
                return []
            return [(n, round(k / len(ids), 2)) for n, k in c.most_common(4)]

        am, an = assoc(um), assoc(un)
        ok = False
        if am and an and an[0][1] >= 0.5:
            target = an[0][0]
            # The name that characterises the rare spelling must also be common
            # around the frequent spelling. This rejects Hirst/Hewet (each spelling
            # sits with its own person) and accepts Athos/Ados (both sit with Athos).
            share = dict(am).get(target, 0.0)
            ok = share >= 0.5 * an[0][1]
        out[(major, minor)] = {"src_major": am, "src_minor": an, "agree": ok,
                               "units_major": len(um), "units_minor": len(un)}
    return out


def main():
    roots = book_roots()
    data = json.load(open("scratch/audit/name_verdicts.json", encoding="utf-8"))
    report = {}
    for book, rows in data.items():
        same = [(r["major"], r["minor"]) for r in rows if r["verdict"] == "same"]
        if not same:
            continue
        root = roots.get(book.replace("（坟头草译）", ""))
        if not root:
            report[book] = {"skip": "no source",
                            "pairs": [{"major": a, "minor": b} for a, b in same]}
            continue
        ev = evidence(same, root)
        report[book] = {"root": root,
                        "pairs": [{"major": a, "minor": b, **ev[(a, b)]}
                                  for a, b in same]}
    json.dump(report, open("scratch/audit/name_verified.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    ok = sum(1 for b in report.values() for p in b.get("pairs", []) if p.get("agree"))
    bad = sum(1 for b in report.values() for p in b.get("pairs", []) if not p.get("agree"))
    print("agree", ok, "reject", bad, "books without source",
          sum(1 for b in report.values() if b.get("skip")))


if __name__ == "__main__":
    main()
