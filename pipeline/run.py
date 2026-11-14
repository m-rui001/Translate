"""Driver: translate chapters of the extracted source with the workflow."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import workflow as wf

SRC = "E:/Translate/work/src"
OUT = "E:/Translate/work/out"


def load_chapter(cid: str) -> dict:
    return json.load(open(os.path.join(SRC, cid + ".json"), encoding="utf-8"))


def split_models(s: str):
    return [m.strip() for m in s.split(",") if m.strip()]


def ensure_analysis(ch: dict, models) -> str:
    """Chapter-level analysis; degrades to a stub if every model is unavailable."""
    d = os.path.join(OUT, ch["id"])
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "analysis.txt")
    if os.path.exists(p) and os.path.getsize(p) > 200:
        return open(p, encoding="utf-8").read()
    source = wf.render_source(ch["blocks"])
    # keep analysis input within a sane size; long chapters get the whole text anyway
    print(f"[{ch['id']}] analysing {len(source.split())} words ...", flush=True)
    t0 = time.time()
    try:
        a = wf.run_analysis(ch["title_en"], source, models, tag_=ch["id"])
    except Exception as e:  # noqa: BLE001
        print(f"[{ch['id']}] analysis failed ({str(e)[:60]}); continuing without it", flush=True)
        a = "（本次未能生成章节分析，译者请自行把握本章语气与人物腔调。）"
    open(p, "w", encoding="utf-8").write(a)
    print(f"[{ch['id']}] analysis done in {time.time()-t0:.0f}s, {len(a)} chars", flush=True)
    return a


def plan_chunks(ch: dict, target: int):
    d = os.path.join(OUT, ch["id"])
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "chunks.json")
    if os.path.exists(p):
        spec = json.load(open(p, encoding="utf-8"))
        return [spec[str(i)] for i in range(len(spec))]
    chunks = wf.chunk_blocks(ch["blocks"], target_words=target, max_words=int(target * 1.35))
    spec = {str(i): c for i, c in enumerate(chunks)}
    json.dump(spec, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    return chunks


def run_chapter(cid, models, workers, target, resume=True):
    ch = load_chapter(cid)
    analysis = ensure_analysis(ch, models["writer"])
    chunks = plan_chunks(ch, target)
    print(f"[{cid}] {len(chunks)} chunks", flush=True)

    results = [None] * len(chunks)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {}
        for i, blocks in enumerate(chunks):
            outdir = os.path.join(OUT, cid, f"chunk{i:02d}")
            futs[ex.submit(wf.translate_chunk, blocks, analysis, outdir, models,
                           f"{cid}/c{i:02d}", resume)] = i
        for f in as_completed(futs):
            i = futs[f]
            try:
                r = results[i] = f.result()
                flag = "cached" if r.get("cached") else "done"
                print(f"[{cid}] chunk {i+1}/{len(chunks)} {flag} "
                      f"{len(r['translation'])} chars", flush=True)
            except Exception as e:  # noqa: BLE001
                results[i] = {"translation": "", "error": str(e)}
                print(f"[{cid}] chunk {i+1} FAILED: {e}", flush=True)
                traceback.print_exc()

    ok = [r for r in results if r and r.get("translation")]
    body = "\n\n".join(r["translation"].strip() for r in ok)
    os.makedirs(os.path.join(OUT, cid), exist_ok=True)
    with open(os.path.join(OUT, cid, "chapter.md"), "w", encoding="utf-8") as f:
        f.write(f"# {ch['title_zh']}\n\n{body}\n")
    print(f"[{cid}] assembled {len(ok)}/{len(chunks)} chunks, {len(body)} chars, "
          f"{time.time()-t0:.0f}s", flush=True)
    return len(ok), len(chunks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", required=True, help="comma separated ids, or 'all'")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--target", type=int, default=1500, help="words per chunk")
    ap.add_argument("--writer", default="ox:gpt-6.1-sol,ox:gemini-3.8-flash,or-nemotron-3-ultra")
    ap.add_argument("--critic", default="ms-deepseek-v4.1-flash,ms-qwen3.5-27b")
    ap.add_argument("--reviewer", default="or-nemotron-3-ultra,ox:gpt-6.1-sol")
    ap.add_argument("--polisher", default="ox:gpt-6.1-sol,ox:gemini-3.8-flash,or-nemotron-3-ultra")
    ap.add_argument("--proof", default="or-nemotron-3-ultra,ox:gpt-6.1-sol")
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--shard", default="0/1", help="i/n: split the chapter list across processes")
    a = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    if a.chapters == "all":
        ids = sorted(f[:-5] for f in os.listdir(SRC) if f.endswith(".json"))
    else:
        ids = split_models(a.chapters)
    try:
        si, sn = (int(x) for x in a.shard.split("/"))
        if sn > 1:
            ids = [c for i, c in enumerate(ids) if i % sn == si]
            print(f"[shard {si}/{sn}] {len(ids)} chapters", flush=True)
    except Exception:
        pass
    models = {
        "writer": split_models(a.writer),
        "critic": split_models(a.critic),
        "reviewer": split_models(a.reviewer),
        "polisher": split_models(a.polisher),
        "proof": split_models(a.proof),
    }
    # rotate each pool per shard so parallel runners spread load across providers
    try:
        si, sn = (int(x) for x in a.shard.split("/"))
    except Exception:
        si = 0
    if si:
        for k in list(models):
            models[k] = models[k][si % len(models[k]):] + models[k][:si % len(models[k])]
    for cid in ids:
        run_chapter(cid, models, a.workers, a.target, resume=not a.no_resume)


if __name__ == "__main__":
    main()
