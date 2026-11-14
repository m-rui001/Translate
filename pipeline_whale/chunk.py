"""Chunking: turn a chapter's blocks into translation units.

Moby-Dick's blocks are heterogeneous (prose paragraphs, verse blocks with line
breaks, speaker labels, quotation attributions). A chunk is a list of blocks; a
block is never split across chunks unless it is enormous, in which case it is cut
on sentence boundaries and the pieces stay in order.
"""
from __future__ import annotations

import json
import os
import re
import sys

SRC = "E:/Translate/work_whale/src"
OUT = "E:/Translate/work_whale/chunks"

TARGET = 1100          # words per chunk
HARD_MAX = 1600
BIG_BLOCK = 2200       # a single paragraph larger than this gets split


def words(t: str) -> int:
    return len(re.findall(r"[A-Za-z0-9’'-]+", re.sub(r"⟦/?i⟧", "", t)))


def block_words(b: dict) -> int:
    if b["type"] == "verse":
        return words(" ".join(b["lines"]))
    return words(b.get("text", ""))


def split_block(b: dict, cap: int = 1200) -> list[dict]:
    """Split an oversized prose block on sentence boundaries."""
    if b["type"] != "p" or block_words(b) <= BIG_BLOCK:
        return [b]
    sents = re.split(r"(?<=[.!?;:—])\s+", b["text"])
    out, cur, n = [], [], 0
    for s in sents:
        w = words(s)
        if cur and n + w > cap:
            out.append({"type": "p", "text": " ".join(cur), "cont": True})
            cur, n = [], 0
        cur.append(s)
        n += w
    if cur:
        out.append({"type": "p", "text": " ".join(cur), "cont": True})
    # the first piece keeps the original opening, the rest are marked continuations
    if len(out) > 1:
        out[0] = dict(out[0])
        out[0].pop("cont", None)
    return out


def chunk_blocks(blocks: list[dict]) -> list[list[dict]]:
    units: list[dict] = []
    for b in blocks:
        units.extend(split_block(b))
    chunks, cur, n = [], [], 0
    for u in units:
        w = block_words(u)
        if cur and (n + w > HARD_MAX or (n >= TARGET and w > 250)):
            chunks.append(cur)
            cur, n = [], 0
        cur.append(u)
        n += w
    if cur:
        chunks.append(cur)
    return chunks


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(OUT, exist_ok=True)
    index = {}
    total = 0
    for f in sorted(os.listdir(SRC)):
        if not f.endswith(".json"):
            continue
        d = json.load(open(os.path.join(SRC, f), encoding="utf-8"))
        cid = d["id"]
        chunks = chunk_blocks(d["blocks"])
        spec = []
        for i, c in enumerate(chunks):
            spec.append({
                "n": i,
                "types": [b["type"] for b in c],
                "paras": sum(1 for b in c if b["type"] == "p"),
                "verse_lines": [len(b["lines"]) for b in c if b["type"] == "verse"],
                "words": sum(block_words(b) for b in c),
            })
        with open(os.path.join(OUT, cid + ".json"), "w", encoding="utf-8") as fh:
            json.dump({"id": cid, "num": d["num"], "title_en": d["title_en"],
                       "title_zh": d["title_zh"], "chunks": chunks}, fh,
                      ensure_ascii=False)
        index[cid] = spec
        total += len(chunks)
        print(f"{cid:10s} chunks={len(chunks):3d} words={sum(s['words'] for s in spec):6d} "
              f"{d['title_zh']}")
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print("TOTAL chunks:", total)


if __name__ == "__main__":
    main()
