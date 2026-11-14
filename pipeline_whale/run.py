"""Run the Moby-Dick workflow over chapters, resumable and shardable.

    python run.py --chapters ch001-ch010 --workers 8
    python run.py --all --workers 8 --shard 1/3
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

import llm
import workflow as wf
from glossary import relevant as rel_gl, render as render_gl

CHUNKS = "E:/Translate/work_whale/chunks"
OUT = "E:/Translate/work_whale/out"

# openox.tech proxies sit behind Cloudflare's ~125 s edge timeout, so a 12k-char
# prompt with a long answer can die as 524. Fast models lead every pool; the slow,
# valuable ones (claude-opus-5) are kept as fallbacks and are only offered small jobs.
WRITER = ["xm:mimo-v2.6-flash", "ox:gemini-3.8-flash",
          "oxc:claude-opus-5", "xm:mimo-v2.6-flash"]
# deepseek last: same family as the writer, so it is a self-audit — but a
# self-audit that finds real errors beats no audit at all
AUDITOR = ["ox:gemini-3.8-flash", "oxg:gpt-6.1-sol", "oxc:claude-opus-5",
           "xm:mimo-v2.6-flash"]
ANALYST = ["ox:gemini-3.8-flash", "oxg:gpt-6.1-sol", "oxc:claude-opus-5"]
POLISHER = ["ox:gemini-3.8-flash", "oxg:gpt-6.1-sol", "oxc:claude-opus-5",
            "xm:mimo-v2.6-flash"]
EXPLORER = ["oxc:claude-opus-5", "ox:gemini-3.8-flash"]

_print_lock = threading.Lock()


def log(msg):
    with _print_lock:
        print(msg, flush=True)


def analyse(data, pools, chapter_dir):
    """One chapter-level analysis, cached."""
    path = os.path.join(chapter_dir, "analysis.txt")
    if os.path.exists(path) and os.path.getsize(path) > 100:
        return open(path, encoding="utf-8").read()
    os.makedirs(chapter_dir, exist_ok=True)
    body = wf.render_source([b for c in data["chunks"] for b in c][:400])
    if len(body) < 2500:      # a two-line chapter needs no scene analysis
        text = "（短章，无需整体分析。）"
        with open(path, "w", encoding="utf-8") as f:
            f.write(text + chr(10))
        return text
    gl = render_gl(rel_gl(body)[:40])
    prompt = wf.p_analysis(data["title_en"], data["title_zh"], body[:9000])
    try:
        text, used = llm.chat_pool(
            [{"role": "system", "content": wf.SYS_AUDITOR},
             {"role": "user", "content": gl + "\n\n" + prompt}],
            ANALYST, max_tokens=3500, temperature=0.4,
            tag=f"{data['id']}:analysis", timeout=300)
        text = wf.tag(text, "analysis") or text
    except Exception as e:  # noqa: BLE001
        text = f"（本章分析缺省：{str(e)[:60]}）"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")
    return text


def run_chapter(cid, data, pools, resume=True, audit=True, polish=True):
    chapter_dir = os.path.join(OUT, cid)
    os.makedirs(chapter_dir, exist_ok=True)
    analysis = analyse(data, pools, chapter_dir)
    t0 = time.time()
    n_ok = n_cached = n_fail = 0
    for i, blocks in enumerate(data["chunks"]):
        outdir = os.path.join(chapter_dir, f"c{i:02d}")
        try:
            r = wf.translate_chunk(blocks, outdir, pools, f"{cid}/c{i:02d}",
                                   nums=(data["num"] is None or True),
                                   resume=resume, audit=audit, polish=polish,
                                   analysis_text=analysis)
            if r.get("cached"):
                n_cached += 1
            else:
                n_ok += 1
        except Exception as e:  # noqa: BLE001
            n_fail += 1
            log(f"  [{cid}/c{i:02d}] FAILED: {str(e)[:140]}")
    log(f"[{cid}] chunks={len(data['chunks'])} new={n_ok} cached={n_cached} "
        f"fail={n_fail} {time.time() - t0:.0f}s  {data['title_zh']}")
    return n_ok, n_cached, n_fail


def assemble_chapter(cid, data):
    """Concatenate chunk finals into chapter.md, and record the block map so the
    evaluator can compare only prose against prose."""
    parts, types = [], []
    for i, blocks in enumerate(data["chunks"]):
        p = os.path.join(OUT, cid, f"c{i:02d}", "final.txt")
        if os.path.exists(p):
            parts.append(open(p, encoding="utf-8").read().strip())
            types.extend(b["type"] for b in blocks)
    if not parts:
        return 0
    body = "\n\n".join(parts)
    os.makedirs(os.path.join(OUT, cid), exist_ok=True)
    with open(os.path.join(OUT, cid, "chapter.md"), "w", encoding="utf-8") as f:
        f.write(body + "\n")
    with open(os.path.join(OUT, cid, "blocks.json"), "w", encoding="utf-8") as f:
        json.dump([{"type": t} for t in types], f, ensure_ascii=False)
    return len(body)


def select(ids, spec):
    if spec in (None, "", "all"):
        return ids
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            for cid in ids:
                num = cid_num(cid)
                if num is None:
                    continue
                if int(a.replace("ch", "")) <= num <= int(b.replace("ch", "")):
                    out.append(cid)
        elif part.startswith("front") or part.startswith("epi"):
            out += [c for c in ids if c.startswith(part[:5])]
        else:
            num = cid_num(part)
            out += [c for c in ids if cid_num(c) == num]
    seen, res = set(), []
    for c in out:
        if c not in seen:
            seen.add(c)
            res.append(c)
    return res


def cid_num(cid):
    if cid.startswith("ch") and cid[2:].isdigit():
        return int(cid[2:])
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", default="all")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--shard", default=None, help="i/n")
    ap.add_argument("--no-audit", action="store_true")
    ap.add_argument("--no-polish", action="store_true")
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--writer", default=",".join(WRITER))
    ap.add_argument("--auditor", default=",".join(AUDITOR))
    ap.add_argument("--polisher", default=",".join(POLISHER))
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    index = json.load(open(os.path.join(CHUNKS, "index.json"), encoding="utf-8"))
    ids = list(index.keys())
    ids = select(ids, a.chapters)
    if a.shard:
        i, n = a.shard.split("/")
        ids = [c for k, c in enumerate(ids) if k % int(n) == int(i)]

    pools = {"writer": a.writer.split(","), "auditor": a.auditor.split(","),
             "polisher": a.polisher.split(","), "explorer": EXPLORER}
    log(f"chapters: {len(ids)} workers={a.workers} "
        f"chunks={sum(len(index[c]) for c in ids)}")

    # load chapter specs lazily inside the pool, but keep chapter order sequential
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
        futs = {}
        for cid in ids:
            data = json.load(open(os.path.join(CHUNKS, cid + ".json"), encoding="utf-8"))
            futs[ex.submit(run_chapter, cid, data, pools, not a.no_resume,
                           not a.no_audit, not a.no_polish)] = cid
        for f in as_completed(futs):
            cid = futs[f]
            try:
                f.result()
                data = json.load(open(os.path.join(CHUNKS, cid + ".json"), encoding="utf-8"))
                assemble_chapter(cid, data)
                done = sum(1 for c in ids if os.path.exists(
                    os.path.join(OUT, c, "chapter.md")))
                log(f"  → {cid} assembled ({done}/{len(ids)})")
            except Exception as e:  # noqa: BLE001
                log(f"  → {cid} ERROR {str(e)[:140]}")
    log(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
