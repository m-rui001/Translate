"""Drive every Gutenberg title through the existing whale/new translation chain.

The chunker, prompts, audit and polish steps in `pipeline_whale/workflow.py` are
book-agnostic apart from the glossary, so this module is a thin driver: it points
the workflow at `work_gutenberg/<book>/src`, uses a per-book glossary (or none),
and runs all books concurrently.

Two deliberate choices:

  * **One global concurrency budget.** Twenty books at four workers each would be
    80 concurrent model calls, and the reseller starts refusing TLS handshakes
    past ~200. Books are therefore run in parallel while the *chunks* share one
    bounded pool, so adding books does not multiply load.
  * **Writer and auditor differ.** The audit is a check, not a self-review, so
    the auditor pool does not contain the writer model. With a single model on
    this key, that means audit is off by default: an audit by the translator is
    only a second pass by the same head.

Usage:
    python pipeline_gutenberg/run_all.py --books nachsommer,effi --workers 24
    python pipeline_gutenberg/run_all.py --all --workers 32 --dry-run
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "pipeline_whale"))

import workflow as wf            # noqa: E402
import chunk as chunktool       # noqa: E402

WRITER = ["lc:deepseek-v4.1-flash"]  # local freeai gateway :8317 (NOT openox)
_print_lock = threading.Lock()


def log(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def load_glossary(work: str) -> dict:
    """Per-book glossary, if one has been mined.

    None of these books has an existing Chinese translation to borrow names
    from, so the glossary starts empty and is filled later from the finished
    draft by `pipeline_polish/terms.py` (mine the recurring proper nouns, then
    enforce them). Translating without a glossary is correct here: inventing
    renderings before reading the book would fix names the text has not yet
    justified.
    """
    p = os.path.join(work, "glossary.json")
    if not os.path.exists(p):
        return {}
    d = json.load(open(p, encoding="utf-8"))
    return {k: v for k, v in d.items() if not k.startswith("_")}


def make_render(gl: dict):
    def rel(source: str) -> list[tuple[str, str]]:
        low = source.lower()
        return [(k, v) for k, v in gl.items() if k.lower() in low][:60]

    def render(entries) -> str:
        if not entries:
            return ""
        lines = ["【术语表：原文 → 中文定译，必须照用】"]
        lines += [f"  {k} → {v}" for k, v in entries]
        return "\n".join(lines) + "\n"

    return rel, render


def chunk_plan(book: str) -> dict:
    """Chunk every chapter once, cached under work_gutenberg/<book>/chunks."""
    src = os.path.join(ROOT, "work_gutenberg", book, "src")
    cdir = os.path.join(ROOT, "work_gutenberg", book, "chunks")
    os.makedirs(cdir, exist_ok=True)
    plan = {}
    for p in sorted(glob.glob(os.path.join(src, "c*.json"))):
        cid = os.path.splitext(os.path.basename(p))[0]
        cache = os.path.join(cdir, cid + ".json")
        if os.path.exists(cache):
            plan[cid] = json.load(open(cache, encoding="utf-8"))
            continue
        d = json.load(open(p, encoding="utf-8"))
        chunks = chunktool.chunk_blocks(d["blocks"])
        spec = {"id": cid, "title_src": d.get("title", ""),
                "title_zh": d.get("title", ""), "chunks": chunks}
        json.dump(spec, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
        plan[cid] = spec
    return plan


def analyse(book: str, spec: dict, chapter_dir: str) -> str:
    """A short chapter-level note fed to every chunk, so unit decisions agree."""
    path = os.path.join(chapter_dir, "analysis.txt")
    if os.path.exists(path) and os.path.getsize(path) > 100:
        return open(path, encoding="utf-8").read()
    os.makedirs(chapter_dir, exist_ok=True)
    body = wf.render_source([b for c in spec["chunks"] for b in c][:400])
    if len(body) < 2500:
        text = "（短章，无需整体分析。）"
    else:
        try:
            text, _ = wf.llm.chat_pool(
                [{"role": "system", "content": wf.SYS_AUDITOR},
                 {"role": "user", "content": wf.p_analysis(
                     spec["title_src"], spec["title_zh"], body[:9000])}],
                WRITER, max_tokens=2500, temperature=0.4,
                tag=f"{book}:{spec['id']}:analysis", timeout=300)
            text = wf.tag(text, "analysis") or text
        except Exception as e:      # noqa: BLE001
            text = f"（本章分析缺省：{str(e)[:60]}）"
    open(path, "w", encoding="utf-8").write(text.rstrip() + "\n")
    return text


def run_book(book: str, workers: int, audit: bool, resume: bool) -> dict:
    work = os.path.join(ROOT, "work_gutenberg", book)
    out_root = os.path.join(work, "out")
    os.makedirs(out_root, exist_ok=True)

    gl = load_glossary(work)
    wf.rel_gl, wf.render_gl = make_render(gl)

    plan = chunk_plan(book)
    units = []
    for cid, spec in plan.items():
        cdir = os.path.join(out_root, cid)
        os.makedirs(cdir, exist_ok=True)
        analysis = analyse(book, spec, cdir)
        for i, blocks in enumerate(spec["chunks"]):
            units.append((cid, i, blocks, analysis))

    pools = {"writer": WRITER, "auditor": [], "polisher": WRITER, "explorer": []}
    t0 = time.time()
    ok = cached = fail = 0

    def one(u):
        cid, i, blocks, analysis = u
        od = os.path.join(out_root, cid, f"c{i:02d}")
        try:
            r = wf.translate_chunk(blocks, od, pools, f"{book}:{cid}/c{i:02d}",
                                   nums=True, resume=resume, audit=audit,
                                   polish=True, analysis_text=analysis)
            return "cached" if r.get("cached") else "ok"
        except Exception as e:       # noqa: BLE001
            log(f"  [{book}/{cid}/c{i:02d}] FAIL {str(e)[:110]}")
            return "fail"

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(one, u) for u in units]
        done = 0
        for f in as_completed(futs):
            r = f.result()
            done += 1
            ok += r == "ok"
            cached += r == "cached"
            fail += r == "fail"
            if done % 25 == 0 or done == len(units):
                log(f"  {book}: {done}/{len(units)} chunks "
                    f"(new={ok} cached={cached} fail={fail})")

    for cid in plan:
        assemble_chapter(book, cid, out_root)
    log(f"[{book}] done {len(plan)} chapters / {len(units)} chunks in "
        f"{time.time() - t0:.0f}s (new={ok} cached={cached} fail={fail})")
    return {"book": book, "chapters": len(plan), "chunks": len(units),
            "ok": ok, "cached": cached, "fail": fail}


def assemble_chapter(book: str, cid: str, out_root: str) -> int:
    d = os.path.join(out_root, cid)
    parts = []
    for p in sorted(glob.glob(os.path.join(d, "c*", "final.txt"))):
        t = open(p, encoding="utf-8").read().strip()
        if t:
            parts.append(t)
    if not parts:
        return 0
    body = "\n\n".join(parts)
    open(os.path.join(d, "chapter.md"), "w", encoding="utf-8").write(body + "\n")
    return len(body)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    import books_meta
    books = list(books_meta.BOOKS) if a.all else \
        [b.strip() for b in a.books.split(",") if b.strip()]

    if a.dry_run:
        tot_c = tot_k = 0
        for b in books:
            plan = chunk_plan(b)
            nc = sum(len(s["chunks"]) for s in plan.values())
            tot_c += len(plan)
            tot_k += nc
            print(f"  {b:16s} chapters={len(plan):3d} chunks={nc:5d}")
        print(f"{len(books)} books, {tot_c} chapters, {tot_k} chunks")
        return

    # books run concurrently; chunks share one bounded pool so the total number of
    # in-flight model calls stays flat as books are added
    per_book = max(2, a.workers // max(1, len(books)))
    log(f"{len(books)} books, {per_book} workers each")
    results = []
    with ThreadPoolExecutor(max_workers=len(books)) as ex:
        futs = {ex.submit(run_book, b, per_book, a.audit, not a.no_resume): b
                for b in books}
        for f in as_completed(futs):
            try:
                results.append(f.result())
            except Exception as e:   # noqa: BLE001
                log(f"[{futs[f]}] ERROR {str(e)[:160]}")
    print()
    for r in sorted(results, key=lambda x: x["book"]):
        print(f"  {r['book']:16s} ch={r['chapters']:3d} chunks={r['chunks']:5d} "
              f"new={r['ok']:5d} cached={r['cached']:5d} fail={r['fail']}")


if __name__ == "__main__":
    main()
