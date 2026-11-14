"""Gap-filling pass: translate whatever chunks the shards left unfinished.

The shards walk chapters in order, so a chunk that fails during a bad provider
window sits unfilled until the shard restarts. This loop picks those gaps one at
a time and keeps going until the book is complete.
"""
from __future__ import annotations

import glob
import json
import os
import time

import workflow as wf

OUT = "E:/Translate/work/out"
SRC = "E:/Translate/work/src"

# tc: is free and fast; its reasoning eats long outputs, so it is first in the
# chain but the openox models catch whatever it cannot finish.
MODELS = {
    "writer": ["tc:deepseek-v4.1-flash", "ox:gpt-6.1-sol", "ox:gemini-3.8-flash"],
    "critic": ["tc:deepseek-v4.1-flash", "ox:gpt-6.1-sol"],
    "reviewer": ["ox:gpt-6.1-sol", "tc:deepseek-v4.1-flash"],
    "polisher": ["ox:gpt-6.1-sol", "ox:gemini-3.8-flash", "tc:deepseek-v4.1-flash"],
    "proof": ["tc:deepseek-v4.1-flash", "ox:gpt-6.1-sol"],
}


def gaps():
    out = []
    for f in sorted(glob.glob(os.path.join(OUT, "*", "chunks.json"))):
        cid = os.path.basename(os.path.dirname(f))
        spec = json.load(open(f, encoding="utf-8"))
        analysis = ""
        ap = os.path.join(OUT, cid, "analysis.txt")
        if os.path.exists(ap):
            analysis = open(ap, encoding="utf-8").read()
        for k, blocks in sorted(spec.items(), key=lambda kv: int(kv[0])):
            d = os.path.join(OUT, cid, f"chunk{int(k):02d}")
            if not os.path.exists(os.path.join(d, "final.txt")):
                out.append((cid, int(k), blocks, analysis))
    return out


def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    round_no = 0
    while True:
        round_no += 1
        todo = gaps()
        if not todo:
            print("[fill] complete — no gaps left", flush=True)
            return
        print(f"[fill] round {round_no}: {len(todo)} chunks remaining", flush=True)
        for cid, k, blocks, analysis in todo:
            outdir = os.path.join(OUT, cid, f"chunk{k:02d}")
            try:
                r = wf.translate_chunk(blocks, analysis, outdir, MODELS,
                                       f"{cid}/c{k:02d}", resume=True)
                flag = "cached" if r.get("cached") else "done"
                print(f"[fill] {cid} chunk {k:02d} {flag} {len(r['translation'])} chars", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"[fill] {cid} chunk {k:02d} FAILED {str(e)[:80]}", flush=True)
            time.sleep(2)


if __name__ == "__main__":
    main()
