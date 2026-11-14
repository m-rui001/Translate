"""Diagnose how a Gutenberg plain-text file marks its chapters.

Every one of these books was typeset in a different century and country, so there
is no single heading pattern. `Der Nachsommer` numbers its ten books with bare
roman numerals and no word at all; `Effi Briest` writes `Erstes Kapitel`;
`Os Maias` writes `CAPITULO I` in caps; `La Regenta` just writes `I`. Hard-coding
any one of those silently produces a one-chapter book.

This script prints the short standalone lines -- the candidates -- with their
line numbers, so the real structure of each file can be read off rather than
guessed. Run it per book when adding a title.

Usage:
    python pipeline_gutenberg/diagnose.py --book effi
"""
from __future__ import annotations

import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "work_gutenberg", "src")

START = re.compile(r"^\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*$", re.M)
END = re.compile(r"^\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG.*$", re.M)

# lines that are *only* a number, a roman numeral, or one of the heading words
NUMWORD = re.compile(r"^(?:[IVXLC]{1,7}|\d{1,3})\.?$")
WORDNUM = re.compile(
    r"^(?:Kapitel|KAPITEL|Chapter|CHAPTER|Capitulo|CAPITULO|Capítulo|CAPÍTULO|"
    r"Cap[ií]tulo|CAPITOLO|Capitolo|Hoofdstuk|HOOFDSTUK|Kapitlet|KAPITLET|"
    r"LIBRO|Libro|PARTE|Parte|Buch|BUCH|Book|BOOK)\b", re.I)
ORDINAL = re.compile(
    r"^(?:Erstes|Zweites|Drittes|Viertes|Fünftes|Sechstes|Siebentes|Achtes|"
    r"Neuntes|Zehntes|Elftes|Zwölftes|Thirteenth|First|Second|Third|Fourth|"
    r"Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Primera|Segunda|Tercera|Cuarta|"
    r"Quinta|Sexta|Séptima|Octava|Primeiro|Segundo|Terceiro|Quarto)\b", re.I)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True)
    ap.add_argument("--limit", type=int, default=40)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    raw = open(os.path.join(SRC, a.book + ".txt"), encoding="utf-8", errors="replace").read()
    m = START.search(raw)
    if m:
        raw = raw[m.end():]
    m = END.search(raw)
    if m:
        raw = raw[:m.start()]

    lines = raw.split("\n")
    classes: Counter = Counter()
    hits: list[tuple[int, str, str]] = []
    for i, l in enumerate(lines):
        s = l.strip()
        if not s or len(s) > 60:
            continue
        kind = ""
        if NUMWORD.match(s):
            kind = "num"
        elif WORDNUM.match(s):
            kind = "word"
        elif ORDINAL.match(s) and len(s) < 40:
            kind = "ordinal"
        if kind:
            classes[kind] += 1
            hits.append((i, kind, s))

    print(f"{a.book}: {len(lines)} lines, candidates {dict(classes)}")
    for i, kind, s in hits[:a.limit]:
        prev = lines[i - 1].strip()[:30] if i else ""
        nxt = lines[i + 1].strip()[:46] if i + 1 < len(lines) else ""
        print(f"  {i:6d} [{kind:7s}] {s[:44]:44s} | prev={prev!r} next={nxt!r}")
    if len(hits) > a.limit:
        print(f"  ... {len(hits) - a.limit} more")


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    main()
