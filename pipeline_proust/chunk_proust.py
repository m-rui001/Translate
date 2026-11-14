"""Chunk the extracted French paragraphs into translation units.

Proust's paragraphs can run to 30k characters, so very long ones are split at a
sentence boundary; short ones are grouped. Paragraph boundaries are never lost.
"""
from __future__ import annotations

import json
import os
import re
import sys

SRC = "E:/Translate/work_proust/src"
OUT = "E:/Translate/work_proust/chunks"

TARGET = 850     # words per chunk
HARD_MAX = 1250


def words(t: str) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÿ'’-]+", t))


def split_long(p: str, cap: int = 2500) -> list[str]:
    """Split an oversized paragraph on sentence boundaries."""
    if words(p) <= cap:
        return [p]
    sents = re.split(r"(?<=[.!?…»])\s+", p)
    out, cur, n = [], [], 0
    for s in sents:
        w = words(s)
        if cur and n + w > cap:
            out.append(" ".join(cur))
            cur, n = [], 0
        cur.append(s)
        n += w
    if cur:
        out.append(" ".join(cur))
    return out


def make_units(paras: list[str]) -> list[str]:
    units = []
    for p in paras:
        units.extend(split_long(p))
    return units


def chunk_units(units: list[str]) -> list[list[str]]:
    chunks, cur, n = [], [], 0
    for u in units:
        w = words(u)
        if cur and n + w > HARD_MAX:
            chunks.append(cur)
            cur, n = [], 0
        cur.append(u)
        n += w
        if n >= TARGET and w < 200:
            chunks.append(cur)
            cur, n = [], 0
    if cur:
        chunks.append(cur)
    return chunks


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    total = 0
    for vol in ("v3", "v4", "v6", "v7"):
        f = os.path.join(SRC, vol + "_paras.json")
        if not os.path.exists(f):
            print("missing", f)
            continue
        paras = json.load(open(f, encoding="utf-8"))
        units = make_units(paras)
        chunks = chunk_units(units)
        d = os.path.join(OUT, vol)
        os.makedirs(d, exist_ok=True)
        spec = {str(i): c for i, c in enumerate(chunks)}
        with open(os.path.join(d, "chunks.json"), "w", encoding="utf-8") as fh:
            json.dump(spec, fh, ensure_ascii=False)
        for i, c in enumerate(chunks):
            with open(os.path.join(d, f"chunk{i:03d}.json"), "w", encoding="utf-8") as fh:
                json.dump(c, fh, ensure_ascii=False)
        w = sum(words(u) for u in units)
        total += len(chunks)
        print(f"{vol}: paragraphs={len(paras):5d} units={len(units):5d} chunks={len(chunks):4d} words={w}")
    print("TOTAL chunks:", total)


if __name__ == "__main__":
    main()
