"""Translation runner for the two new projects (Soledad, Zauberberg).

Reuses the whale workflow (chunk → draft → audit → repair → polish → clean) but
points it at a different source tree and a per-book glossary, because the whale
glossary is Moby-Dick's and would otherwise inject whaling vocabulary into
Macondo.

    python pipeline_new/run_new.py --book soledad --chapters capitulo001 --workers 1
    python pipeline_new/run_new.py --book zauberberg --all --workers 6

Model pools use the Alibaba Model Studio families (the resellers the older
pipelines depended on are out of quota). Writer and auditor are deliberately
different families so the audit is not a self-review.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pipeline_whale"))

import workflow as wf          # noqa: E402
import chunk as chunktool      # noqa: E402  (whale's chunker is generic)

BOOKS = {
    "soledad": {
        "src": "E:/Translate/work_soledad/src",
        "work": "E:/Translate/work_soledad",
        "title_zh": "百年孤独",
        "lang": "es",
    },
    "zauberberg": {
        "src": "E:/Translate/work_zauberberg/src",
        "work": "E:/Translate/work_zauberberg",
        "title_zh": "魔山",
        "lang": "de",
        # 000 is the title page, 022 the table of contents — neither is text
        "exclude": ["index_split_000", "index_split_022"],
    },
}

WRITER = ["xm:mimo-v2.6-flash", "ox:gemini-3.8-flash"]
AUDITOR = ["xm:mimo-v2.6-flash", "ox:gemini-3.8-flash"]
POLISHER = ["xm:mimo-v2.6-flash", "ox:gemini-3.8-flash"]
ANALYST = ["xm:mimo-v2.6-flash"]

_print_lock = threading.Lock()


def log(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


# ─────────────────────────────────────────────────────────────── glossary
def load_glossary(work: str) -> dict:
    p = os.path.join(work, "glossary.json")
    if not os.path.exists(p):
        return {}
    d = json.load(open(p, encoding="utf-8"))
    return {k: v for k, v in d.items() if not k.startswith("_")}


def make_render(gl: dict):
    """Same shape as pipeline_whale.glossary.render: name → target form."""

    def rel(source: str) -> list[tuple[str, str]]:
        low = source.lower()
        hits = [(k, v) for k, v in gl.items() if k.lower() in low]
        return hits[:60]

    def render(entries) -> str:
        if not entries:
            return ""
        lines = ["【术语表：原文 → 中文定译，必须照用】"]
        for k, v in entries:
            lines.append(f"  {k} → {v}")
        return "\n".join(lines) + "\n"

    return rel, render


# ─────────────────────────────────────────────────────────────── chunking
def chapter_chunks(cid: str, src_dir: str, out_dir: str) -> dict:
    """Chunk a chapter once and cache the spec next to the output tree."""
    cache_p = os.path.join(out_dir, cid + ".json")
    if os.path.exists(cache_p):
        return json.load(open(cache_p, encoding="utf-8"))
    d = json.load(open(os.path.join(src_dir, cid + ".json"), encoding="utf-8"))
    chunks = chunktool.chunk_blocks(d["blocks"])
    spec = {"id": cid, "num": None, "title_en": d.get("title", ""),
            "title_zh": d.get("title", "") or cid, "chunks": chunks}
    os.makedirs(out_dir, exist_ok=True)
    json.dump(spec, open(cache_p, "w", encoding="utf-8"), ensure_ascii=False)
    return spec


def analyse(data: dict, pools: dict, chapter_dir: str) -> str:
    path = os.path.join(chapter_dir, "analysis.txt")
    if os.path.exists(path) and os.path.getsize(path) > 100:
        return open(path, encoding="utf-8").read()
    os.makedirs(chapter_dir, exist_ok=True)
    body = wf.render_source([b for c in data["chunks"] for b in c][:400])
    if len(body) < 2500:
        text = "（短章，无需整体分析。）"
        open(path, "w", encoding="utf-8").write(text + "\n")
        return text
    prompt = wf.p_analysis(data["title_en"], data["title_zh"], body[:9000])
    try:
        text, _used = wf.llm.chat_pool(
            [{"role": "system", "content": wf.SYS_AUDITOR},
             {"role": "user", "content": prompt}],
            ANALYST, max_tokens=3500, temperature=0.4,
            tag=f"{data['id']}:analysis", timeout=300)
        text = wf.tag(text, "analysis") or text
    except Exception as e:  # noqa: BLE001
        text = f"（本章分析缺省：{str(e)[:60]}）"
    open(path, "w", encoding="utf-8").write(text.rstrip() + "\n")
    return text


def run_chapter(cid, data, pools, out_root, resume=True, audit=True, polish=True):
    chapter_dir = os.path.join(out_root, cid)
    os.makedirs(chapter_dir, exist_ok=True)
    analysis = analyse(data, pools, chapter_dir)
    t0 = time.time()
    n_ok = n_cached = n_fail = 0
    for i, blocks in enumerate(data["chunks"]):
        outdir = os.path.join(chapter_dir, f"c{i:02d}")
        try:
            r = wf.translate_chunk(blocks, outdir, pools, f"{cid}/c{i:02d}",
                                   nums=True, resume=resume, audit=audit,
                                   polish=polish, analysis_text=analysis)
            if r.get("cached"):
                n_cached += 1
            else:
                n_ok += 1
        except Exception as e:  # noqa: BLE001
            n_fail += 1
            log(f"  [{cid}/c{i:02d}] FAILED: {str(e)[:140]}")
    log(f"[{cid}] chunks={len(data['chunks'])} new={n_ok} cached={n_cached} "
        f"fail={n_fail} {time.time() - t0:.0f}s")
    return n_ok, n_cached, n_fail


def assemble_chapter(cid, data, out_root):
    parts = []
    for i, blocks in enumerate(data["chunks"]):
        p = os.path.join(out_root, cid, f"c{i:02d}", "final.txt")
        if os.path.exists(p):
            parts.append(open(p, encoding="utf-8").read().strip())
    if not parts:
        return 0
    body = "\n\n".join(parts)
    open(os.path.join(out_root, cid, "chapter.md"), "w", encoding="utf-8").write(body + "\n")
    return len(body)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, choices=sorted(BOOKS))
    ap.add_argument("--chapters", default="all")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--writer", default=",".join(WRITER))
    ap.add_argument("--auditor", default=",".join(AUDITOR))
    ap.add_argument("--polisher", default=",".join(POLISHER))
    ap.add_argument("--no-audit", action="store_true")
    ap.add_argument("--no-polish", action="store_true")
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="chunk + report only")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    cfg = BOOKS[a.book]
    src_dir = cfg["src"]
    out_root = os.path.join(cfg["work"], "out")
    chunks_dir = os.path.join(cfg["work"], "chunks")
    os.makedirs(out_root, exist_ok=True)

    gl = load_glossary(cfg["work"])
    wf.rel_gl, wf.render_gl = make_render(gl)

    ids = sorted(os.path.splitext(f)[0] for f in os.listdir(src_dir) if f.endswith(".json"))
    ids = [i for i in ids if i != "index" and i not in set(cfg.get("exclude", []))]
    if a.chapters != "all":
        want = {c.strip() for c in a.chapters.split(",") if c.strip()}
        ids = [i for i in ids if i in want]

    specs = {cid: chapter_chunks(cid, src_dir, chunks_dir) for cid in ids}
    total_chunks = sum(len(s["chunks"]) for s in specs.values())
    log(f"{cfg['title_zh']}: chapters={len(ids)} chunks={total_chunks} "
        f"workers={a.workers} glossary={len(gl)}")
    if a.dry_run:
        for cid, s in specs.items():
            print(f"  {cid:16s} chunks={len(s['chunks']):3d} "
                  f"paras={sum(1 for c in s['chunks'] for b in c if b['type']=='p')}")
        return

    pools = {"writer": a.writer.split(","), "auditor": a.auditor.split(","),
             "polisher": a.polisher.split(","), "explorer": []}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
        futs = {ex.submit(run_chapter, cid, specs[cid], pools, out_root,
                          not a.no_resume, not a.no_audit, not a.no_polish): cid
                for cid in ids}
        for f in as_completed(futs):
            cid = futs[f]
            try:
                f.result()
                n = assemble_chapter(cid, specs[cid], out_root)
                done = sum(1 for c in ids if os.path.exists(os.path.join(out_root, c, "chapter.md")))
                log(f"  → {cid} assembled {n} chars ({done}/{len(ids)})")
            except Exception as e:  # noqa: BLE001
                log(f"  → {cid} ERROR {str(e)[:140]}")
    log(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
