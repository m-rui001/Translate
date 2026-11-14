"""Extract and chunk the French source for the volumes Zhou Kexi did not finish.

Paragraph-oriented, because Proust's paragraphs are enormous and must never be
split mid-sentence by the chunker.
"""
from __future__ import annotations

import json
import os
import re
import sys

SRC = "E:/Translate/work_proust/src"
OUT = "E:/Translate/work_proust/chunks"

VOL = {
    "v3": ("盖尔芒特家那边", "Le Côté de Guermantes"),
    "v4": ("所多玛与蛾摩拉", "Sodome et Gomorrhe"),
    "v6": ("逃亡者", "Albertine disparue"),
    "v7": ("重现的时光", "Le Temps retrouvé"),
}


def read_paras(path: str) -> list[str]:
    raw = open(path, encoding="utf-8").read()
    raw = raw.replace("\r", "")
    # PDF line wraps: join, then split on real paragraph breaks
    raw = re.sub(r"\n\s*\n", "\x00", raw)
    raw = re.sub(r"(?<![.!?:»”’])\n(?=\S)", " ", raw)
    paras = [re.sub(r"[ \t]+", " ", p).strip() for p in raw.split("\x00")]
    return [p for p in paras if len(p) > 40]


def chunk(paras: list[str], target: int = 900, hard_max: int = 1200):
    """Group whole paragraphs; never cut a paragraph in half."""
    chunks, cur, n = [], [], 0
    for p in paras:
        w = len(re.findall(r"[A-Za-zÀ-ÿ'’-]+", p))
        if cur and n + w > hard_max and n >= target * 0.6:
            chunks.append(cur)
            cur, n = [], 0
        cur.append(p)
        n += w
        if n >= target and w < 120:
            chunks.append(cur)
            cur, n = [], 0
    if cur:
        chunks.append(cur)
    return chunks


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(OUT, exist_ok=True)
    total = 0
    for vol, (zh, fr) in VOL.items():
        src = os.path.join(SRC, vol + ".txt")
        if not os.path.exists(src):
            print("missing", src)
            continue
        paras = read_paras(src)
        chunks = chunk(paras)
        os.makedirs(os.path.join(OUT, vol), exist_ok=True)
        spec = {}
        for i, ch in enumerate(chunks):
            spec[str(i)] = ch
            with open(os.path.join(OUT, vol, f"chunk{i:03d}.json"), "w", encoding="utf-8") as f:
                json.dump(ch, f, ensure_ascii=False)
        with open(os.path.join(OUT, vol, "chunks.json"), "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False)
        words = sum(len(re.findall(r"[A-Za-zÀ-ÿ'’-]+", p)) for p in paras)
        total += len(chunks)
        print(f"{vol} {zh:12s} paragraphs={len(paras):5d} chunks={len(chunks):4d} words={words}")
    print("TOTAL chunks:", total)


if __name__ == "__main__":
    main()
