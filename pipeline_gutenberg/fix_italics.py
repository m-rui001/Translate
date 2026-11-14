"""Repair emphasis markers the polish pass mangled.

The translation used `⟦i⟧…⟦/i⟧` for italics. Polishing is told to keep those markers
verbatim, and mostly does, but in about a dozen paragraphs the closing marker came back
damaged — as `⟧`, as `/i⟧`, or as both together (`⟧/i⟧`) — and a few lost the opening
marker's tail instead. Left alone, the leftovers appear as literal `⟦i⟧` in the prose.

The repair is a small normaliser, not a pattern-guessing exercise:

  1. every intact `⟦i⟧…⟦/i⟧` pair is parked under a placeholder, so it cannot be
     touched again (an earlier version rewrote good pairs into `⟦/i⟧/i⟧` this way);
  2. inside what remains, an opening marker followed by any of `⟧`, `/i⟧`, `⟧/i⟧`
     is normalised to `⟦i⟧…⟦/i⟧`;
  3. a bare `⟦…⟧/i⟧` (opening marker lost its `i`) is likewise normalised.

Anything still unbalanced afterwards is reported and left alone, because guessing at
that point would corrupt real prose. The paragraph count is asserted unchanged.
"""
from __future__ import annotations

import glob
import os
import re
import sys

ROOT = "E:/Translate"

PAIR = re.compile(r"⟦i⟧[^⟦⟧]{0,300}?⟦/i⟧")
DAMAGED_CLOSE = re.compile(r"⟦i⟧([^⟦⟧]{1,120}?)(?:⟧/i⟧|/i⟧|⟧)")
DAMAGED_OPEN = re.compile(r"⟦([^⟦⟧/]{1,120}?)⟧/i⟧")
LEFTOVER = re.compile(r"⟦|⟧|/i⟧")


def fix_text(t: str) -> tuple[str, int]:
    """Normalise damaged markers. Idempotent: an already-clean text is returned as is."""
    parked: list[str] = []

    def park(m: re.Match) -> str:
        parked.append(m.group(0))
        return f"\x00{len(parked) - 1}\x00"

    t = PAIR.sub(park, t)
    n = 0

    def em(m: re.Match) -> str:
        nonlocal n
        n += 1
        return f"⟦i⟧{m.group(1)}⟦/i⟧"

    t = DAMAGED_OPEN.sub(em, t)
    t = DAMAGED_CLOSE.sub(em, t)
    t = re.sub(r"\x00(\d+)\x00", lambda m: parked[int(m.group(1))], t)
    return t, n


def leftovers(t: str) -> list[str]:
    """Brackets that are not part of a well-formed marker.

    Counting is done by removing the two marker tokens and looking at what is left.
    Matching whole pairs instead would report a legitimate italic run longer than the
    pattern's window as damage, which is how a false positive was introduced before.
    """
    stripped = t.replace("⟦i⟧", "").replace("⟦/i⟧", "")
    return [m.group(0) for m in LEFTOVER.finditer(stripped)]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    dry = "--dry-run" in sys.argv
    targets = [a for a in sys.argv[1:] if not a.startswith("-")] or ["*"]
    books = []
    for t in targets:
        books += sorted(glob.glob(os.path.join(ROOT, "work_gutenberg", t)))
    nfix = nfile = nbad = 0
    for b in books:
        for f in sorted(glob.glob(os.path.join(b, "out", "*", "c*", "final.txt"))):
            raw = open(f, encoding="utf-8").read()
            if not raw:
                continue
            new, k = fix_text(raw)
            left = leftovers(new)
            if new == raw and not left:
                continue
            if left:
                nbad += 1
                print(f"UNRESOLVED {os.path.relpath(f, ROOT)}  {left[:4]}")
            if new != raw:
                nfix += k
                nfile += 1
                print(f"{'DRY ' if dry else ''}{os.path.relpath(f, ROOT)}  damaged={k}")
                if not dry:
                    assert (len(new.split("\n\n")) == len(raw.split("\n\n"))), \
                        "paragraph count changed"
                    open(f, "w", encoding="utf-8").write(new)
    print(f"\n{nfile} file(s) changed, {nfix} marker(s) normalised, {nbad} unresolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
