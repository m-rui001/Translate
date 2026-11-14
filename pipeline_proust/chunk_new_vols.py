"""Chunk the newly fetched Gutenberg volumes (v1, v2, v5) into translation units.

The volumes already in the project (v3, v4, v6, v7) were extracted from a PDF and
their line wraps were repaired by `extract_proust.py`. The three volumes fetched
from Gutenberg (`fetch_missing.py`) are hard-wrapped at a fixed column, so they
need two things the old path does not do:

1. **unwrap** — rejoin lines that are not real paragraph breaks. Gutenberg wraps
   mid-sentence and mid-word (``gué- / rir``), so a line is joined unless it ends
   with sentence punctuation *and* the next line looks like a fresh paragraph
   (capital after a wide gap, or a blank line).
2. **chunk by paragraph budget**, never splitting a paragraph. Proust's
   paragraphs run to several pages, so a single oversized paragraph becomes its
   own chunk rather than being cut.

Output matches what the rest of the pipeline expects:
    work_proust/chunks/<vol>/chunks.json   {"0": [para, ...], ...}
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

SRC = "E:/Translate/work_proust/src"
OUT = "E:/Translate/work_proust/chunks"

VOLS = ("v1", "v2", "v5")

# ~1100 French words per chunk; Proust is dense, so this lands near 7k characters
TARGET_WORDS = 1100
HARD_MAX_WORDS = 2200


def unwrap(raw: str) -> str:
    """Rejoin hard-wrapped lines into real paragraphs."""
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = raw.split("\n")
    paras, buf = [], []
    for i, line in enumerate(lines):
        s = line.rstrip()
        if not s.strip():
            if buf:
                paras.append(" ".join(buf))
                buf = []
            continue
        # a wrapped word: previous line ends with a hyphen and no space
        if buf and buf[-1].endswith("-") and len(buf[-1]) > 1 \
                and not buf[-1].endswith("--"):
            buf[-1] = buf[-1][:-1] + s.lstrip()
        else:
            buf.append(s.strip())
    if buf:
        paras.append(" ".join(buf))
    # repair the remaining mid-sentence breaks: Gutenberg wraps at ~72 cols, so a
    # paragraph that starts lowercase is a continuation of the one before it
    merged = []
    for p in paras:
        p = re.sub(r"\s{2,}", " ", p).strip()
        if not p:
            continue
        if merged and (p[0].islower() or p[0] in ",;:)»”’"):
            merged[-1] = merged[-1] + " " + p
        else:
            merged.append(p)
    return "\n\n".join(merged)


def strip_noise(text: str) -> str:
    """Drop title pages, chapter headings, numerals and transcriber's asides.

    Gutenberg volumes open with a title page (author, series, volume number,
    dedication, publisher, city) before the novel proper begins. Rather than
    enumerate every possible line, the body is located as the first block long
    enough to be prose — a title page never contains a 500-character paragraph.
    """
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    start = 0
    for i, b in enumerate(blocks):
        if len(b) > 500 and b[0].isupper():
            start = i
            break
    blocks = blocks[start:]

    out = []
    for s in blocks:
        if re.fullmatch(r"(?:CHAPITRE|Chapitre)?\s*[IVXLC]+\.?", s):
            continue
        if re.fullmatch(r"(?:CHAPITRE|Chapitre)\s+\w+", s):
            continue
        if s.startswith(("Produced by", "Transcriber", "[Illustration")):
            continue
        if len(s) < 3:
            continue
        out.append(s)
    return "\n\n".join(out)


def words(s: str) -> int:
    return len(re.findall(r"[\wÀ-ÿ'’-]+", s))


def chunk(paras: list[str]) -> list[list[str]]:
    chunks, cur, n = [], [], 0
    for p in paras:
        w = words(p)
        if cur and (n + w > TARGET_WORDS or n > HARD_MAX_WORDS):
            chunks.append(cur)
            cur, n = [], 0
        cur.append(p)
        n += w
        if w > HARD_MAX_WORDS:
            chunks.append(cur)
            cur, n = [], 0
    if cur:
        chunks.append(cur)
    return chunks


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    total = 0
    for vol in VOLS:
        path = os.path.join(SRC, vol + ".txt")
        if not os.path.exists(path):
            print(f"{vol}: missing source, run fetch_missing.py first")
            continue
        raw = io.open(path, encoding="utf-8").read()
        text = strip_noise(unwrap(raw))
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = chunk(paras)
        d = os.path.join(OUT, vol)
        os.makedirs(d, exist_ok=True)
        spec = {str(i): c for i, c in enumerate(chunks)}
        with open(os.path.join(d, "chunks.json"), "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=1)
        wc = sum(words(p) for p in paras)
        print(f"{vol}: {len(paras)} paras -> {len(chunks)} chunks, "
              f"{wc:,} words, {sum(len(p) for p in paras):,} chars")
        total += len(chunks)
    print(f"TOTAL chunks: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
