"""Normalise Chinese quote levels in the translation.

Dialogue at the outermost level must be “ ”; only a quotation inside a quotation
may use ‘ ’. The models sometimes hand back single quotes at the top level, which
reads wrong in print. This rewrites levels with a nesting stack and leaves the
wording untouched.
"""
from __future__ import annotations

import glob
import io
import os
import re
import sys

OUT = "E:/Translate/work/out"
OPEN_2, CLOSE_2 = "“", "”"   # “ ”
OPEN_1, CLOSE_1 = "‘", "’"   # ‘ ’


def normalise(text: str) -> str:
    """Level 0 speech -> “ ”, level 1+ quotation -> ‘ ’, whatever the model used."""
    out = []
    for ch in text:
        if ch == OPEN_2 or ch == OPEN_1:
            out.append(OPEN_2 if not stack_push(out) else OPEN_1)
        elif ch == CLOSE_2 or ch == CLOSE_1:
            out.append(closest_for(out))
        else:
            out.append(ch)
    return "".join(out)


def _depth(out: list[str]) -> int:
    """How many quote runs are still open, from the text emitted so far."""
    d = 0
    for c in out:
        if c in (OPEN_1, OPEN_2):
            d += 1
        elif c in (CLOSE_1, CLOSE_2):
            d = max(0, d - 1)
    return d


def stack_push(out: list[str]) -> bool:
    """True when this opener is at level >= 1 (needs a single quote)."""
    return _depth(out) > 0


def closest_for(out: list[str]) -> str:
    return CLOSE_1 if _depth(out) > 1 else CLOSE_2


def normalise_doc(text: str) -> str:
    """Apply per paragraph so a level leak cannot run across the whole chapter."""
    parts = re.split(r"(\n\s*\n)", text)
    return "".join(normalise(p) if i % 2 == 0 else p for i, p in enumerate(parts))


def count_levels(text: str) -> tuple[int, int]:
    return text.count(OPEN_1), text.count(OPEN_2)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    touched = 0
    for f in sorted(glob.glob(os.path.join(OUT, "*", "chapter.md"))):
        raw = io.open(f, encoding="utf-8").read()
        before = count_levels(raw)
        new = normalise_doc(raw)
        after = count_levels(new)
        if new != raw:
            io.open(f, "w", encoding="utf-8").write(new)
            touched += 1
            cid = os.path.basename(os.path.dirname(f))
            print(f"  {cid:12s} 单引号 {before[0]:4d}->{after[0]:4d}  双引号 {before[1]:4d}->{after[1]:4d}")
    print(f"normalised {touched} chapters")


if __name__ == "__main__":
    main()
