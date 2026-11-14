"""Extract the French source with real paragraph boundaries.

This PDF comes from a single-page HTML and carries no indentation, but paragraph
starts show up as a ~38pt vertical gap between lines. Without that, Proust's
enormous paragraphs cannot be preserved and chunks get cut mid-sentence.
"""
from __future__ import annotations

import json
import os
import re
import sys

import pymupdf

PDF = "E:/Translate/A la recherche du temps perdu.pdf"
OUT = "E:/Translate/work_proust/src"

# page ranges (1-based, inclusive)
VOL = {
    "v3": (532, 869, "Le Côté de Guermantes", "盖尔芒特家那边"),
    "v4": (870, 1148, "Sodome et Gomorrhe", "所多玛与蛾摩拉"),
    "v6": (1363, 1505, "Albertine disparue", "逃亡者"),
    "v7": (1506, 1692, "Le Temps retrouvé", "重现的时光"),
}

GAP_THRESHOLD = 8.0  # points; a normal line gap is ~0.5


def page_lines(page):
    lines = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            txt = "".join(s["text"] for s in l["spans"])
            if not txt.strip():
                continue
            if re.fullmatch(r"\s*\d+\s*", txt):  # folio
                continue
            lines.append((l["bbox"][1], l["bbox"][3], txt))
    lines.sort()
    return lines


def extract(doc, start, end):
    paras, cur, prev_y1 = [], [], None
    for pg in range(start - 1, end):
        for y0, y1, txt in page_lines(doc[pg]):
            txt = re.sub(r"[ \t]+", " ", txt).strip()
            if prev_y1 is not None and (y0 - prev_y1) > GAP_THRESHOLD:
                if cur:
                    paras.append(" ".join(cur))
                cur = []
            cur.append(txt)
            prev_y1 = y1
    if cur:
        paras.append(" ".join(cur))
    # a paragraph must survive a hyphenated line break correctly
    out = []
    for p in paras:
        p = re.sub(r"-\s+(?=[a-zà-ÿ])", "", p)   # fin de mot coupé
        p = p.replace("Ŕ", "«").replace("Ś", "»")  # guillemets mis-decoded
        p = re.sub(r"\s+", " ", p).strip()
        if len(p) > 60:
            out.append(p)
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(OUT, exist_ok=True)
    doc = pymupdf.open(PDF)
    total_p = 0
    for vol, (a, b, fr, zh) in VOL.items():
        paras = extract(doc, a, b)
        with open(os.path.join(OUT, vol + "_paras.json"), "w", encoding="utf-8") as f:
            json.dump(paras, f, ensure_ascii=False, indent=1)
        words = sum(len(re.findall(r"[A-Za-zÀ-ÿ'’-]+", p)) for p in paras)
        total_p += len(paras)
        print(f"{vol} {zh:12s} p{a}-{b}  paragraphs={len(paras):5d}  words={words:7d}")
    print("TOTAL paragraphs:", total_p)


if __name__ == "__main__":
    main()
