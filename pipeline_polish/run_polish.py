"""Drive the paragraph polish across all seven books, in parallel.

    python -X utf8 pipeline_polish/run_polish.py --smoke        # 3 batches/book
    python -X utf8 pipeline_polish/run_polish.py --workers 150
    python -X utf8 pipeline_polish/run_polish.py --writeback

Cache: work_polish2/<book>/<chapter>/bNNN.json — a batch already on disk is
never re-requested, so the pass is fully resumable and re-runnable.
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


def run_book(book, workers, limit=0, verbose=True):
    units_fn, _ = books.BOOKS[book]
    units = units_fn()
    if limit:
        units = units[:limit]
    outdir = os.path.join(books.CACHE, book)
    tb = terms.termbase(book)
    t0 = time.time()
    st = engine.run(units, outdir, workers=workers, resume=True,
                    verbose=verbose, tb=tb or None)
    st["book"] = book
    st["units"] = len(units)
    st["terms"] = len(tb)
    st["secs"] = round(time.time() - t0, 1)
    print(f"[{book}] {st}", flush=True)
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", default="all")
    ap.add_argument("--workers", type=int, default=150)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--writeback", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    names = list(books.BOOKS) if a.books == "all" else a.books.split(",")
    if a.smoke:
        a.limit = 3

    if a.writeback:
        for b in names:
            rules = terms.all_rules(b)
            if rules:
                txts = books.book_texts(b)
                fixed, n = terms.apply_variants(txts, rules)
                print(f"[{b}] term rules: {len(rules)}, hits {n}", flush=True)
                books.put_book_texts(b, fixed)
            n = books.BOOKS[b][1]()
            print(f"[{b}] wrote back {n} files", flush=True)
        return

    t0 = time.time()
    # one shared pool: workers are spent on whichever book has batches ready
    results = []
    with ThreadPoolExecutor(max_workers=len(names)) as ex:
        futs = {ex.submit(run_book, b, a.workers, a.limit): b for b in names}
        for f in futs:
            results.append(f.result())
    dt = time.time() - t0
    ok = sum(r["ok"] for r in results)
    kept = sum(r["kept"] for r in results)
    fail = sum(r["fail"] for r in results)
    print(f"\nTOTAL {dt:.0f}s  ok={ok} kept={kept} fail={fail}", flush=True)
    json.dump(results, open(os.path.join(books.CACHE, "last_run.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
