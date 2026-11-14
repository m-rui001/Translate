"""Structural repair before any rewriting.

Three faults, all of them evidence that drafts were concatenated without a
read-through:

1. literal <verse>…</verse> tags left in the prose (150 of them in LOTR);
2. the same source paragraph translated twice, both drafts kept (six places);
3. source blocks split mid-sentence, so the Chinese stops at "她，她".

Only (1) and (2) are repaired mechanically. (3) is recorded and handed to the
revision pass, which sees the whole source span and rewrites the unit.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

# chapter -> indices of the later duplicate draft, hand-checked against the source
DROP = {
    "book2c06": [142],
    "book3c02": [15, 33, 227],
    "book3c03": [40],
    "book6c02": [118],
}

TERM = "。！？…”』）】!?\"'"


def strip_verse(t: str) -> tuple[str, bool]:
    if "<verse>" not in t and "</verse>" not in t:
        return t, False
    t = t.replace("<verse>", "").replace("</verse>", "")
    lines = [x.strip() for x in t.split("\n") if x.strip()]
    return "\n".join(lines), True


def fragments(src: list[str]) -> list[tuple[int, int]]:
    """Source blocks that break mid-sentence and continue in the next block."""
    out = []
    for i, s in enumerate(src[:-1]):
        s = s.strip()
        if not s or len(s) < 40:
            continue
        if s[-1] in TERM:
            continue
        nxt = src[i + 1].lstrip()
        if nxt[:1].islower():
            out.append((i, i + 1))
    return out


def run(book: str) -> None:
    d = os.path.join(common.WORK, book, "ch")
    stats = {"verse": 0, "dropped": 0, "frag": 0}
    for fn in sorted(os.listdir(d)):
        p = os.path.join(d, fn)
        ch = common.load_json(p)
        changed = False

        if book == "lotr":
            drop = set(DROP.get(ch["id"], []))
            zh, types = [], []
            for i, t in enumerate(ch["zh"]):
                if i in drop:
                    stats["dropped"] += 1
                    changed = True
                    continue
                t2, is_verse = strip_verse(t)
                if is_verse:
                    stats["verse"] += 1
                    changed = True
                zh.append(t2)
                types.append("verse" if is_verse else "p")
            ch["zh"] = zh
            ch["zh_types"] = types

        src = ch.get("src_paras") or [p["src"] for p in ch.get("paras", [])]
        fr = fragments(src)
        if fr:
            ch["src_fragments"] = fr
            stats["frag"] += len(fr)
            changed = True

        if changed:
            common.save_json(p, ch)
    print(book, stats)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for b in sys.argv[1:] or ["whale", "soledad", "lotr"]:
        run(b)
