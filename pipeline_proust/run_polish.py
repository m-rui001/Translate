"""大改精校 pass over completed Proust volumes. Resumable per-chunk."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, "E:/Translate/pipeline")

import workflow_proust as wp

CHUNKS = "E:/Translate/work_proust/chunks"
OUT = "E:/Translate/work_proust/out"
VOLS = ("v3", "v4", "v6", "v7")


def run_vol(vol, pools, workers):
    spec = json.load(open(os.path.join(CHUNKS, vol, "chunks.json"), encoding="utf-8"))
    keys = sorted(spec, key=int)
    print(f"[{vol}] polishing {len(keys)} chunks", flush=True)
    ok = kept = cached = fail = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {}
        for k in keys:
            outdir = os.path.join(OUT, vol, f"chunk{int(k):03d}")
            futs[ex.submit(wp.polish_chunk, spec[k], outdir, pools,
                           f"{vol}/c{k}")] = k
        for i, f in enumerate(as_completed(futs), 1):
            k = futs[f]
            try:
                st = f.result()
                cached += st == "cached"
                ok += st == "polished"
                kept += st == "kept"
                fail += st == "missing"
            except Exception as e:  # noqa: BLE001
                fail += 1
                print(f"[{vol}] chunk {k} ERROR: {str(e)[:90]}", flush=True)
            if i % 10 == 0:
                print(f"[{vol}] {i}/{len(keys)} polished={ok} kept={kept} "
                      f"cached={cached} fail={fail} {time.time()-t0:.0f}s", flush=True)
    body = []
    for k in keys:
        p = os.path.join(OUT, vol, f"chunk{int(k):03d}", "final.txt")
        if os.path.exists(p):
            body.append(open(p, encoding="utf-8").read().strip())
    with open(os.path.join(OUT, vol, "volume.md"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(body) + "\n")
    print(f"[{vol}] DONE polished={ok} kept={kept} cached={cached} fail={fail} "
          f"chars={sum(len(b) for b in body)} {time.time()-t0:.0f}s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--volumes", default="all")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--polisher",
                    default="ox:claude-opus-5,ox:gpt-6.1-sol,ox:gemini-3.8-flash")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    pools = {"polisher": a.polisher.split(",")}
    vols = VOLS if a.volumes == "all" else a.volumes.split(",")
    for vol in vols:
        run_vol(vol, pools, a.workers)


if __name__ == "__main__":
    main()
