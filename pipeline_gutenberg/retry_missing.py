"""Re-run only the chunks that failed during the full Gutenberg pass.

`run_all.py --all` finished 2113 of 2121 chunks; eight were lost to API errors
(timeouts / 502s under 150-way concurrency). Re-running the whole book would
retranslate 2,113 good chunks, so this reads the same chunk manifests, finds the
missing `final.txt` files, and retries just those — at lower concurrency and with
a longer timeout, since the failures were all transport-level.

The retry has to go through `run_book`'s own helpers (`load_glossary`,
`make_render`, `analyse`) because `translate_chunk` reads the glossary and the
chapter analysis from module-level state; calling it bare would translate with an
empty name table.

Usage:
    python -X utf8 pipeline_gutenberg/retry_missing.py            # dry run
    python -X utf8 pipeline_gutenberg/retry_missing.py --apply
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, "E:/Translate/pipeline_gutenberg")

import run_all as RA
import importlib

wf = importlib.import_module("pipeline_whale.workflow") if False else RA.wf

WORK = "E:/Translate/work_gutenberg"


def chunk_count(spec) -> int:
    return len(spec) if isinstance(spec, list) else len(spec.get("chunks", spec))


def find_missing() -> list[tuple[str, str, int]]:
    out = []
    for book in sorted(os.listdir(WORK)):
        cdir = os.path.join(WORK, book, "chunks")
        if not os.path.isdir(cdir):
            continue
        for fn in sorted(os.listdir(cdir)):
            if not fn.endswith(".json"):
                continue
            cid = fn[:-5]
            spec = json.load(open(os.path.join(cdir, fn), encoding="utf-8"))
            for i in range(chunk_count(spec)):
                fp = os.path.join(WORK, book, "out", cid, f"c{i:02d}", "final.txt")
                if not os.path.exists(fp) or os.path.getsize(fp) == 0:
                    out.append((book, cid, i))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    missing = find_missing()
    print(f"missing chunks: {len(missing)}")
    for m in missing:
        print("  ", m)
    if not a.apply or not missing:
        return 0

    by_book: dict[str, list] = {}
    for book, cid, i in missing:
        by_book.setdefault(book, []).append((cid, i))

    ok = fail = 0
    for book, items in by_book.items():
        work = os.path.join(WORK, book)
        print(f"\n=== {book}: {len(items)} chunks ===")
        gl = RA.load_glossary(work)
        wf.rel_gl, wf.render_gl = RA.make_render(gl)
        plan = RA.chunk_plan(book)
        pools = {"writer": RA.WRITER, "auditor": [], "polisher": RA.WRITER,
                 "explorer": []}

        tasks = []
        for cid, i in items:
            spec = plan.get(cid)
            if spec is None:
                print(f"  {cid}/{i}: chapter not in plan, skipped")
                continue
            cdir = os.path.join(work, "out", cid)
            os.makedirs(cdir, exist_ok=True)
            analysis = RA.analyse(book, spec, cdir)
            tasks.append((cid, i, spec["chunks"][i], analysis))

        def one(t):
            cid, i, blocks, analysis = t
            od = os.path.join(work, "out", cid, f"c{i:02d}")
            wf.translate_chunk(blocks, od, pools, f"{book}:{cid}/c{i:02d}",
                               nums=True, resume=False, audit=False,
                               polish=True, analysis_text=analysis)
            return cid, i

        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            futs = {ex.submit(one, t): t for t in tasks}
            for f in as_completed(futs):
                t = futs[f]
                try:
                    f.result()
                    ok += 1
                    print(f"  ok   {t[0]}/c{t[1]:02d}")
                except Exception as e:                            # noqa: BLE001
                    fail += 1
                    print(f"  FAIL {t[0]}/c{t[1]:02d}: {str(e)[:120]}")

        # re-assemble only the affected chapters
        for cid in sorted({c for c, _ in items}):
            try:
                RA.assemble_chapter(book, cid, os.path.join(work, "out"))
                print(f"  assembled {cid}")
            except Exception as e:                                # noqa: BLE001
                print(f"  assemble {cid} failed: {str(e)[:100]}")

    print(f"\nretry done: ok={ok} fail={fail}")
    left = find_missing()
    print(f"still missing: {len(left)}")
    for m in left:
        print("  ", m)
    return 0 if not left else 1


if __name__ == "__main__":
    raise SystemExit(main())
