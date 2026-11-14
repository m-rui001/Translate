"""Repair paragraphs whose dialogue quotes never close.

The drafting models occasionally used a single outer quote and lost the closing
mark, or split one source paragraph into two. A naive depth counter cannot tell
these apart from a legitimate continuation ("段一说完，段二接着引"), so each
candidate is resolved against the English source:

  * if the source paragraph is one quotation that runs past this paragraph's
    end, the paragraph is a continuation → keep it open only when the next
    paragraph is dialogue, else close it;
  * if the source paragraph *ends* where this one ends, the quote must close
    here → append ”;
  * if the source paragraph is plain narration but ours opens a quote that
    never closes, the opening “ is spurious → drop it.

Every fix is reported; nothing is guessed silently.

    python pipeline/fix_quotes.py --dry
    python pipeline/fix_quotes.py --apply
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re

OUT = "E:/Translate/work/out"
SRC = "E:/Translate/work/src"

OD, CD = "“", "”"


def paras_of(path: str) -> tuple[str, list[str]]:
    raw = open(path, encoding="utf-8").read()
    if path.endswith("chapter.md"):
        title, body = raw.split("\n", 1)
        return title + "\n\n", [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    return "", [p.strip() for p in re.split(r"\n\s*\n", raw) if p.strip()]


def source_blocks(cid: str) -> list[dict]:
    return json.load(open(os.path.join(SRC, cid + ".json"), encoding="utf-8"))["blocks"]


def src_quote_state(b: dict) -> tuple[bool, bool, int]:
    """(opens, closes, net) quote depth at the end of a source block."""
    if b["type"] != "p":
        return False, False, 0
    t = b["text"]
    opens, closes = t.count("‘"), t.count("’")
    return opens > 0, closes > 0, opens - closes


def fix_file(path: str, blocks: list[dict] | None, apply: bool) -> list[str]:
    head, ps = paras_of(path)
    notes = []
    i = 0
    while i < len(ps):
        p = ps[i]
        if p.startswith("<verse>") or p.count(OD) - p.count(CD) <= 0:
            i += 1
            continue
        nxt = ps[i + 1].lstrip() if i + 1 < len(ps) else ""
        if nxt.startswith(OD) or nxt.startswith("<verse>"):
            i += 1
            continue          # legitimate continuation
        # unclosed and nothing follows that re-opens: decide from the source
        src = blocks[i] if blocks and i < len(blocks) else None
        if src and src["type"] == "p":
            opens, closes, net = src_quote_state(src)
            if net > 0:
                # source speech runs on; close it here, the next para is narration
                ps[i] = p.rstrip() + CD
                notes.append(f"[{i}] 源段续引已断，补 ”")
            elif opens and closes:
                ps[i] = p.rstrip() + CD
                notes.append(f"[{i}] 源段引号已收，补 ”")
            else:
                # narration in the source: the opening quote is spurious
                ps[i] = p.replace(OD, "", 1)
                notes.append(f"[{i}] 源段为叙述，删去孤立 “")
        else:
            ps[i] = p.rstrip() + CD
            notes.append(f"[{i}] 无源段可比，补 ”")
        i += 1
    if apply and notes:
        open(path, "w", encoding="utf-8").write(head + "\n\n".join(ps) + "\n")
    return notes


def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(OUT, "*", "chapter.md")))
    if a.only:
        files = [f for f in files if a.only in f]
    total = 0
    for f in files:
        cid = os.path.basename(os.path.dirname(f))
        notes = fix_file(f, source_blocks(cid), a.apply)
        if notes:
            total += len(notes)
            print(f"## {cid}")
            for n in notes:
                print("   ", n)
    print(f"{'fixed' if a.apply else 'would fix'} {total} paragraphs")


if __name__ == "__main__":
    main()
