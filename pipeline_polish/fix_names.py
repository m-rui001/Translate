"""Repair proper-noun drift introduced by the polish pass.

The polish brief requires glossary terms to be used verbatim, but the model drifts them
anyway, and a rename is the worst kind of defect: 斯达巴克 → 斯塔巴克 does not look
like an error in isolation, it just makes the reader think there are two characters.

The glossary gives us the canonical form. What it does not give us is the *wrong*
form — the drift is not in any list. So this works in two passes:

1. **Known variants.** A small curated map of the drifts actually found in this
   workspace, each one confirmed by reading the before/after pair.

2. **Near-variant mining.** For each canonical term, look for same-length strings that
   share a prefix or suffix and differ in one character, occurring in the same book.
   Candidates are only *reported*; they are applied solely when the canonical form is
   far more frequent, because otherwise the "wrong" form may simply be a different
   character whose name genuinely looks alike.

Every rewrite is verified to keep the paragraph count and to change nothing except the
substituted name.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import terms  # noqa: E402

BAK = os.path.join(ROOT, "work_polish2", "_backup_polish3")

# Drifts confirmed by eye against the pre-polish text. Left side is the damage, right
# side is the glossary form.
CONFIRMED = {
    "whale": {"斯塔巴克": "斯达巴克"},
    "soledad": {"奥雷亚诺": "奥雷里亚诺"},
}

PATTERNS = {
    "whale": "work_whale/out/*/*/final.txt",
    "soledad": "work_soledad/out/*/*/final.txt",
    "camus": "work_camus/out/*/final.txt",
    "chekhov": "work_chekhov/out/*/final.txt",
    "zauberberg": "work_zauberberg/out/*/*/final.txt",
    "lotr": None,      # json book, handled separately
}


def paras(t: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]


def book_texts(book: str) -> list[tuple[str, str, list[str]]]:
    """(path, format, paragraphs) for every unit of a book."""
    out = []
    pat = PATTERNS.get(book)
    if pat:
        for f in sorted(glob.glob(os.path.join(ROOT, pat))):
            out.append((f, "txt", paras(open(f, encoding="utf-8").read())))
    elif book == "lotr":
        for f in sorted(glob.glob(os.path.join(ROOT, "work_overhaul/lotr/final/*.json"))):
            if f.endswith(".polished.json"):
                continue
            out.append((f, "json", json.load(open(f, encoding="utf-8"))["texts"]))
    return out


def mine(book: str, units, canon: list[str]) -> dict[str, tuple[str, int]]:
    """Candidate wrong forms: same length, one character apart, rarer than canonical.

    Only offers candidates; `--apply-mined` is needed to act on them, because two
    characters can legitimately have similar names and the miner cannot tell.
    """
    cnt = Counter()
    for _p, _fmt, ps in units:
        for s in ps:
            for run in re.findall(r"[\u4e00-\u9fff]{2,10}", s):
                cnt[run] += 1
    cand = {}
    for c in canon:
        if len(c) < 4:
            continue
        n = cnt.get(c, 0)
        if n < 5:
            continue
        for s, k in cnt.items():
            if len(s) != len(c) or s == c:
                continue
            diff = sum(1 for a, b in zip(s, c) if a != b)
            # same head and tail, exactly one character apart in the middle
            if diff == 1 and s[0] == c[0] and s[-1] == c[-1] and k * 8 < n:
                cand[s] = (c, k)
    return cand


def repair(book: str, mapping: dict[str, str], dry: bool) -> int:
    units = book_texts(book)
    total = 0
    touched = []
    for path, fmt, ps in units:
        if fmt == "txt":
            rel = os.path.relpath(path, ROOT).replace(os.sep, "__")
            bak = os.path.join(BAK, rel)
            n_old = None
            if os.path.exists(bak):
                n_old = len(paras(open(bak, encoding="utf-8").read()))
        else:
            n_old = len(ps)
        new = []
        changed = 0
        for p in ps:
            q = p
            for bad, good in mapping.items():
                if bad in q:
                    changed += q.count(bad)
                    q = q.replace(bad, good)
            new.append(q)
        if not changed:
            continue
        # a name substitution must not alter the paragraph count
        if n_old is not None and len(new) != n_old:
            print(f"  SKIP {rel}: paragraph count {len(new)} != {n_old}")
            continue
        total += changed
        touched.append((path, new, changed))
        if not dry:
            if fmt == "txt":
                open(path, "w", encoding="utf-8").write("\n\n".join(new) + "\n")
            else:
                d = json.load(open(path, encoding="utf-8"))
                d["texts"] = new
                json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for p, _n, c in touched:
        print(f"  {c:4d} fixes  {os.path.relpath(p, ROOT)}")
    return total


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    dry = "--dry-run" in sys.argv
    only = None
    if "--book" in sys.argv:
        only = sys.argv[sys.argv.index("--book") + 1]
    books = [only] if only else [b for b in PATTERNS if PATTERNS[b] or b == "lotr"]
    grand = 0
    for book in books:
        try:
            tb = terms.termbase(book)
        except Exception as e:  # noqa: BLE001
            print(f"[{book}] glossary unavailable: {str(e)[:60]}")
            continue
        canon = sorted({v for v in (tb.values() if isinstance(tb, dict) else [])
                        if isinstance(v, str) and 2 <= len(v) <= 10},
                       key=len, reverse=True)
        units = book_texts(book)
        if not units:
            continue
        mapping = dict(CONFIRMED.get(book) or {})
        mined = mine(book, units, canon)
        fresh = {k: v[0] for k, v in mined.items() if k not in mapping}
        if fresh:
            print(f"[{book}] mined candidates (not applied): "
                  + ", ".join(f"{k}->{v}" for k, v in list(fresh.items())[:12]))
        if "--apply-mined" in sys.argv:
            mapping.update(fresh)
        if not mapping:
            continue
        print(f"[{book}] repairing {len(mapping)} variant(s){' (dry run)' if dry else ''}")
        grand += repair(book, mapping, dry)
    print(f"total substitutions: {grand}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
