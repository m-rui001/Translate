"""Run the Proust pipeline over volumes v3/v4/v6/v7, resumable and shardable."""
from __future__ import annotations

import argparse
import glob
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


def run_vol(vol, models, workers, resume=True, audit=True):
    d = os.path.join(CHUNKS, vol)
    spec = json.load(open(os.path.join(d, "chunks.json"), encoding="utf-8"))
    keys = sorted(spec, key=int)
    print(f"[{vol}] {len(keys)} chunks", flush=True)
    ok = fail = cached = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {}
        for k in keys:
            outdir = os.path.join(OUT, vol, f"chunk{int(k):03d}")
            futs[ex.submit(wp.translate_chunk, spec[k], outdir, models,
                           f"{vol}/c{k}", resume, audit)] = k
        for i, f in enumerate(as_completed(futs), 1):
            k = futs[f]
            try:
                r = f.result()
                cached += 1 if r.get("cached") else 0
                ok += 0 if r.get("cached") else 1
                if i % 10 == 0:
                    print(f"[{vol}] {i}/{len(keys)} ok={ok} cached={cached} "
                          f"fail={fail} {time.time()-t0:.0f}s", flush=True)
            except Exception as e:  # noqa: BLE001
                fail += 1
                print(f"[{vol}] chunk {k} FAILED: {str(e)[:90]}", flush=True)
    body = []
    for k in keys:
        p = os.path.join(OUT, vol, f"chunk{int(k):03d}", "final.txt")
        if os.path.exists(p):
            body.append(open(p, encoding="utf-8").read().strip())
    os.makedirs(os.path.join(OUT, vol), exist_ok=True)
    with open(os.path.join(OUT, vol, "volume.md"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(body) + "\n")
    chars = sum(len(b) for b in body)
    print(f"[{vol}] assembled {len(body)}/{len(keys)} chunks, {chars} chars, "
          f"{time.time()-t0:.0f}s", flush=True)
    return len(body), len(keys)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--volumes", default="all")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--writer", default="tc:deepseek-v4.1-flash,ox:claude-opus-5,ox:gpt-6.1-sol,ox:gemini-3.8-flash")
    ap.add_argument("--reviewer", default="ox:claude-opus-5,ox:gpt-6.1-sol,tc:deepseek-v4.1-flash")
    ap.add_argument("--polisher", default="tc:deepseek-v4.1-flash,ox:claude-opus-5,ox:gpt-6.1-sol,ox:gemini-3.8-flash")
    ap.add_argument("--no-audit", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    models = {"writer": a.writer.split(","), "reviewer": a.reviewer.split(","),
              "polisher": a.polisher.split(",")}
    vols = VOLS if a.volumes == "all" else a.volumes.split(",")
    for vol in vols:
        run_vol(vol, models, a.workers, audit=not a.no_audit)


if __name__ == "__main__":
    main()
