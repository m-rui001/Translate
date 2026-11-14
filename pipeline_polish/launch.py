"""Run the full polish across all seven books, in parallel, resumably.

    python -X utf8 pipeline_polish/launch.py --workers 150

Each book has its own thread pool (so one slow book cannot starve the others)
and they all share engine's global in-flight gate, which caps total concurrent
requests at POLISH_GLOBAL_CONCURRENCY (default 150 — past ~200 cssmapi starts
refusing TLS handshakes).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import books   # noqa: E402
import engine  # noqa: E402
import terms   # noqa: E402


def run_book(book, per_book_workers, limit=0):
    units_fn, _ = books.BOOKS[book]
    units = units_fn()
    if limit:
        units = units[:limit]
    tb = terms.termbase(book)
    st = engine.run(units, os.path.join(books.CACHE, book),
                    workers=per_book_workers, resume=True,
                    verbose=False, tb=tb or None)
    st["book"] = book
    st["units"] = len(units)
    st["terms"] = len(tb)
    print(f"[{book}] ok={st['ok']} kept={st['kept']} cached={st['cached']} "
          f"fail={st['fail']} {st['secs']}s", flush=True)
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", default="all")
    ap.add_argument("--per-book", type=int, default=24,
                    help="worker threads per book (global cap still applies)")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    names = list(books.BOOKS) if a.books == "all" else a.books.split(",")
    os.makedirs(books.CACHE, exist_ok=True)
    t0 = time.time()
    out = []

    # One python thread per book, each driving its own engine pool. The engine
    # gate is what actually throttles the API, so this is safe.
    with ThreadPoolExecutor(max_workers=len(names)) as ex:
        futs = [ex.submit(run_book, b, a.per_book, a.limit) for b in names]
        for f in futs:
            out.append(f.result())

    tot = {k: sum(r.get(k, 0) for r in out)
           for k in ("ok", "kept", "fail", "cached", "units")}
    print(f"\nTOTAL {time.time()-t0:.0f}s  " +
          "  ".join(f"{k}={v}" for k, v in tot.items()), flush=True)
    json.dump({"books": out, "total": tot},
              open(os.path.join(books.CACHE, "last_run.json"), "w",
                   encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
