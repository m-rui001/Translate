"""Rebuild every chapter.md from its chunk final.txt files.

chapter.md is written by the shard runner and can go stale when a corrupted chunk
is re-translated later; this makes the chunk finals the single source of truth.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

OUT = "E:/Translate/work/out"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rebuilt = 0
    for cj in sorted(glob.glob(os.path.join(OUT, "*", "chunks.json"))):
        cid = os.path.basename(os.path.dirname(cj))
        spec = json.load(open(cj, encoding="utf-8"))
        parts = []
        for k in sorted(spec, key=lambda x: int(x)):
            p = os.path.join(OUT, cid, f"chunk{int(k):02d}", "final.txt")
            if os.path.exists(p):
                parts.append(open(p, encoding="utf-8").read().strip())
        if not parts:
            continue
        src = json.load(open(os.path.join("E:/Translate/work/src", cid + ".json"),
                             encoding="utf-8"))
        md = os.path.join(OUT, cid, "chapter.md")
        body = "\n\n".join(parts)
        with open(md, "w", encoding="utf-8") as f:
            f.write(f"# {src['title_zh']}\n\n{body}\n")
        rebuilt += 1
    print(f"rebuilt {rebuilt} chapter.md from chunk finals")


if __name__ == "__main__":
    main()
