"""Map the French part/chapter markers onto the Chinese paragraphs.

The French markers are not preserved as separate blocks in the chunked source —
`Première partie` is glued to the front of the paragraph that follows it — so they
can only be located by character offset in `src/<vol>.txt`. That offset is then
mapped onto the Chinese paragraph list by *proportion of length*, which is sound
because the translation is paragraph-for-paragraph with a similar total length.

Two bugs in the first attempt are fixed here:

  * consecutive markers (part immediately followed by a chapter, which happens four
    times) were collapsed, because the fold step let the second marker overwrite
    the first instead of combining them;
  * the opening section could receive a chapter label belonging to a marker that
    sits *after* it, mislabelling Proust's dedication pages as a chapter.

The mapping is also sanity-checked: a section whose paragraph count is 0 is merged
forward, and a marker is dropped if two markers map to the same paragraph index
(that means the French text is denser than the mapping resolution there).
"""
from __future__ import annotations

import io
import os
import re

SRC = os.environ.get("PROUST_SRC", "E:/Translate/work_proust/src")

CN_NUM = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七",
          8: "八", 9: "九", 10: "十"}
ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5}
FRENCH = {"premier": 1, "première": 1, "premiere": 1,
          "deuxième": 2, "deuxieme": 2, "second": 2, "seconde": 2,
          "troisième": 3, "troisieme": 3, "quatrième": 4, "quatrieme": 4,
          "cinquième": 5, "cinquieme": 5}
MARK = re.compile(r"(?m)^\s*(?:(?P<part>[A-Za-zÀ-ÿ]+)\s+(?i:partie)|Chapitre\s+(?P<ch>\w+))\s*$")


def cn_ordinal(word: str) -> str:
    w = (word or "").strip().lower()
    n = ROMAN.get(w) or FRENCH.get(w) or 0
    return CN_NUM.get(n, "")


def markers(vol: str) -> list[dict]:
    p = os.path.join(SRC, vol + ".txt")
    if not os.path.exists(p):
        return []
    raw = io.open(p, encoding="utf-8").read()
    out = []
    for m in MARK.finditer(raw):
        nxt = raw[m.end():m.end() + 500].lstrip("\n")
        first = nxt.split("\n", 1)[0].strip()
        summary = (first if first and not MARK.match(first) and 10 < len(first) < 300
                   else "")
        out.append({"pos": m.start(), "part": m.group("part"),
                    "ch": m.group("ch"), "summary": summary})
    return out


def segments(vol: str, paras: list[str]) -> list[dict]:
    """Split `paras` at the source markers; each result carries its own labels."""
    marks = markers(vol)
    p = os.path.join(SRC, vol + ".txt")
    if not marks or not os.path.exists(p):
        return [{"part": "", "ch": "", "summary": "", "paras": paras}]

    n_src = len(io.open(p, encoding="utf-8").read())
    total = sum(len(x) for x in paras)

    # cumulative Chinese char offset at each paragraph start
    starts, acc = [], 0
    for x in paras:
        starts.append(acc)
        acc += len(x) + 2

    cuts: list[int] = []
    for m in marks:
        target = (m["pos"] / n_src) * total
        idx = min(range(len(starts)), key=lambda i: abs(starts[i] - target))
        cuts.append(idx)

    # keep only strictly increasing cut points; a marker that maps onto a boundary
    # already used is combined into the following one
    merged: list[tuple[int, dict]] = []
    for idx, m in zip(cuts, marks):
        if merged and idx <= merged[-1][0]:
            prev_idx, prev = merged[-1]
            prev = dict(prev)
            prev["part"] = prev["part"] or m["part"]
            prev["ch"] = prev["ch"] or m["ch"]
            prev["summary"] = prev["summary"] or m["summary"]
            merged[-1] = (prev_idx, prev)
        else:
            merged.append((idx, dict(m)))

    segs: list[dict] = []
    start = 0
    for idx, m in merged:
        if idx > start:
            segs.append({"part": "", "ch": "", "summary": "",
                         "paras": paras[start:idx]})
            start = idx
        segs.append({"part": m["part"] or "", "ch": m["ch"] or "",
                     "summary": m["summary"] or "", "paras": []})
    if start < len(paras):
        segs.append({"part": "", "ch": "", "summary": "", "paras": paras[start:]})

    # attach each label block to the paragraphs that follow it; empty one goes to
    # the next non-empty segment
    out: list[dict] = []
    carry = {"part": "", "ch": "", "summary": ""}
    for s in segs:
        if not s["paras"]:
            carry["part"] = carry["part"] or s["part"]
            carry["ch"] = carry["ch"] or s["ch"]
            carry["summary"] = carry["summary"] or s["summary"]
            continue
        out.append({"part": carry["part"] or s["part"],
                    "ch": carry["ch"] or s["ch"],
                    "summary": carry["summary"] or s["summary"],
                    "paras": s["paras"]})
        carry = {"part": "", "ch": "", "summary": ""}
    return out or [{"part": "", "ch": "", "summary": "", "paras": paras}]
