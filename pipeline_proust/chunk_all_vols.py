"""Rebuild translation chunks for all seven volumes at a size that suits the new
billing model.

Why this replaces the old chunker
---------------------------------
The seven source files are in two different shapes:

* ``v1``, ``v2``, ``v5`` came from Gutenberg — hard-wrapped at ~72 columns, so a
  paragraph spans many lines and must be unwrapped before it means anything.
* ``v3``, ``v4``, ``v6``, ``v7`` came from a PDF and were extracted with their line
  breaks intact. The old chunker cut these by *line count*, which is why every
  "paragraph" in those volumes is ~4,500 characters long: it is a page, not a
  paragraph. Feeding a page-shaped blob to the model destroys the paragraph
  correspondence the whole workflow depends on.

So both families now go through the same path: unwrap → drop front matter →
split on real paragraph breaks → pack into chunks.

Why the chunks got much bigger
------------------------------
Billing moved from per-call to per-token with prompt caching. Under per-token
billing the win comes from (a) a byte-stable prompt prefix that caches, and (b) not
paying for a fresh full system prompt on every tiny chunk. A chunk of ~2,600 French
words is ~11k tokens of source, which keeps the per-call prompt overhead small while
staying far inside the 1M-token window and leaving ample room for the reply. The
absolute ceiling is enforced by ``HARD_MAX_WORDS``; a single paragraph longer than
that becomes its own chunk rather than being cut, because cutting a paragraph
breaks the one-paragraph-in-one-paragraph-out contract.

Output: ``work_proust/chunks/<vol>/chunks.json`` = {"0": [para, ...], ...}
"""
from __future__ import annotations

import io
import json
import os
import re
import statistics
import sys

SRC = "E:/Translate/work_proust/src"
OUT = "E:/Translate/work_proust/chunks"
VOLS = ("v1", "v2", "v3", "v4", "v5", "v6", "v7")

# ~2,600 French words ≈ 11k tokens of source. See module docstring.
TARGET_WORDS = 2600
HARD_MAX_WORDS = 4500


def unwrap(raw: str) -> str:
    """Rejoin hard-wrapped lines into real paragraphs."""
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    paras, buf = [], []
    for line in raw.split("\n"):
        s = line.rstrip()
        if not s.strip():
            if buf:
                paras.append(" ".join(buf))
                buf = []
            continue
        if buf and buf[-1].endswith("-") and len(buf[-1]) > 1 \
                and not buf[-1].endswith("--"):
            buf[-1] = buf[-1][:-1] + s.lstrip()
        else:
            buf.append(s.strip())
    if buf:
        paras.append(" ".join(buf))

    # A line that starts lowercase (or with a closing mark) is a continuation of
    # the previous paragraph, not a new one — Gutenberg wraps mid-sentence.
    merged: list[str] = []
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
    """Drop title pages, chapter headings and transcriber's asides."""
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    start = 0
    for i, b in enumerate(blocks):
        if len(b) > 500 and b[0].isupper():
            start = i
            break
    out = []
    for s in blocks[start:]:
        if re.fullmatch(r"(?:CHAPITRE|Chapitre)?\s*[IVXLC]+\.?", s):
            continue
        if re.fullmatch(r"(?:CHAPITRE|Chapitre)\s+\w+", s):
            continue
        if s.startswith(("Produced by", "Transcriber", "[Illustration",
                         "The Project Gutenberg", "Online Distributed")):
            continue
        if len(s) < 3:
            continue
        out.append(s)
    return "\n\n".join(out)


def words(s: str) -> int:
    return len(re.findall(r"[\wÀ-ÿ'’-]+", s))


def chunk(paras: list[str]) -> list[list[str]]:
    chunks: list[list[str]] = []
    cur: list[str] = []
    n = 0
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
    total_chunks = 0
    for vol in VOLS:
        path = os.path.join(SRC, vol + ".txt")
        if not os.path.exists(path):
            print(f"{vol}: missing source")
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
        L = [len(p) for p in paras]
        cw = [sum(words(p) for p in c) for c in chunks]
        print(f"{vol}: {len(paras):>4} paras (med {int(statistics.median(L)):>4} ch) "
              f"-> {len(chunks):>4} chunks "
              f"(med {int(statistics.median(cw)):>5} words, max {max(cw):>5}), "
              f"{sum(L):>9,} chars")
        total_chunks += len(chunks)
    print(f"TOTAL chunks: {total_chunks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
