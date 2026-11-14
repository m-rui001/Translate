"""Run the independent Proust translation over all seven volumes.

Kept separate from `run_proust.py` (which drove the Zhou-calibrated supplement and
reads `pipeline/llm.py`, a local-proxy module that no longer serves this machine).
This one uses `workflow_independent`, `pipeline_whale/llm.py`, and the self-authored
name table, and writes to `work_proust/out_ind` so the older translation in
`work_proust/out` stays intact for comparison.

Resumable at chunk granularity: a chunk is skipped if its `final.txt` exists.
Failures are collected and re-tried once at the end at lower concurrency, because
under high parallelism the failure mode is always transport-level.

Usage:
    python -X utf8 pipeline_proust/run_independent.py --volumes v1,v2
    python -X utf8 pipeline_proust/run_independent.py --all --workers 80
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import workflow_independent as W

CHUNKS = "E:/Translate/work_proust/chunks"
OUT = "E:/Translate/work_proust/out_ind"
VOLS = ("v1", "v2", "v3", "v4", "v5", "v6", "v7")

WRITER = ["xm:mimo-v2.6-flash"]
REVIEWER = ["xm:mimo-v2.6-flash"]
POLISHER = ["xm:mimo-v2.6-flash"]

_lock = threading.Lock()


def log(msg: str) -> None:
    with _lock:
        print(msg, flush=True)


def run_vol(vol: str, workers: int, audit: bool, resume: bool) -> dict:
    spec = json.load(open(os.path.join(CHUNKS, vol, "chunks.json"), encoding="utf-8"))
    # chunk keys are strings in the JSON object; coerce once so every f-string below
    # can format the index as an integer.
    keys = [int(k) for k in sorted(spec, key=int)]
    models = {"writer": WRITER, "reviewer": REVIEWER, "polisher": POLISHER}
    log(f"[{vol}] {len(keys)} chunks")
    t0 = time.time()
    ok = cached = fail = 0
    failed: list[str] = []

    def one(k: int) -> str:
        # chunk keys come out of the JSON spec as strings (they are object keys), so
        # the folder name is formatted from int(k) -- formatting a string with :03d
        # raises ValueError and kills the whole run.
        outdir = os.path.join(OUT, vol, f"chunk{int(k):03d}")
        try:
            r = W.translate_chunk(spec[str(k)], outdir, models, f"{vol}/c{int(k):03d}",
                                  resume=resume, audit=audit)
            return "cached" if r.get("cached") else "ok"
        except Exception as e:                                  # noqa: BLE001
            log(f"[{vol}] c{int(k):03d} FAIL {str(e)[:110]}")
            return "fail"

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, k): k for k in keys}
        done = 0
        for f in as_completed(futs):
            r = f.result()
            done += 1
            ok += r == "ok"
            cached += r == "cached"
            if r == "fail":
                fail += 1
                failed.append(f"c{futs[f]:03d}")
            if done % 10 == 0 or done == len(keys):
                el = time.time() - t0
                rate = done / el * 60 if el else 0
                log(f"[{vol}] {done}/{len(keys)} new={ok} cached={cached} "
                    f"fail={fail} {el:.0f}s ({rate:.0f}/min)")
    # one retry pass for transport failures, serially
    if failed:
        log(f"[{vol}] retrying {len(failed)} failed chunks serially")
        for name in failed:
            k = int(name[1:])
            outdir = os.path.join(OUT, vol, f"chunk{k:03d}")
            for attempt in range(2):
                try:
                    W.translate_chunk(spec[str(k)], outdir, models,
                                      f"{vol}/c{k:03d}", resume=False, audit=audit)
                    fail -= 1
                    log(f"[{vol}] {name} recovered on retry {attempt + 1}")
                    break
                except Exception as e:                            # noqa: BLE001
                    if attempt == 1:
                        log(f"[{vol}] {name} still failing: {str(e)[:90]}")
                    time.sleep(5)

    log(f"[{vol}] done {len(keys)} chunks in {time.time() - t0:.0f}s "
        f"(new={ok} cached={cached} fail={fail})")
    return {"vol": vol, "chunks": len(keys), "ok": ok,
            "cached": cached, "fail": fail}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--volumes", default="all")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--workers", type=int, default=64)
    # Audit is off by default because it was measured, not because it seemed expensive:
    # on five paired chunks a blind judge called it a tie (2:2) while it took 49.5s per
    # chunk against 19.8s without. Its repair pass also fired on 137 of 151 audits, which
    # is not diagnosis, it is a second rewrite. Keep it as an opt-in for chunks that look
    # wrong, not as a routine stage.
    ap.add_argument("--audit", action="store_true",
                    help="add the audit+repair stage (~2.5x wall time, judged no better)")
    ap.add_argument("--no-audit", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--no-resume", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(OUT, exist_ok=True)

    vols = VOLS if (a.all or a.volumes == "all") else a.volumes.split(",")
    t0 = time.time()
    results = []
    for vol in vols:
        results.append(run_vol(vol, a.workers, a.audit and not a.no_audit,
                               not a.no_resume))

    log("\n" + "=" * 56)
    tot = sum(r["chunks"] for r in results)
    ok = sum(r["ok"] for r in results)
    ca = sum(r["cached"] for r in results)
    fa = sum(r["fail"] for r in results)
    for r in results:
        log(f"  {r['vol']}  chunks={r['chunks']:4d} new={r['ok']:4d} "
            f"cached={r['cached']:4d} fail={r['fail']:3d}")
    log(f"TOTAL {tot} chunks  new={ok} cached={ca} fail={fa}  "
        f"{time.time() - t0:.0f}s")
    return 0 if fa == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
