"""LLM sample review of finished public-domain units.

Mechanical checks catch what a regex can see. This asks an independent model (cssmapi
deepseek, a different family from the writers) to read a stratified sample against the
source and report only defects it can point at: mistranslation, omission, unidiomatic
Chinese, name drift. Paragraph numbers are included so a verdict can be checked
against the actual line instead of taken on trust.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = "E:/Translate"
sys.path.insert(0, os.path.join(ROOT, "pipeline_whale"))
import llm

OUT = os.path.join(ROOT, "work_polish2", "reports")
PARA = re.compile(r"\n\s*\n")

SYS = (
    "你是资深文学编辑，中英法德文俱精，正在抽检一部文学译文。你会拿到原文和译文，"
    "逐段核对。只报告确凿的问题：①误译或漏译（意思错了、整句没译）；"
    "②中文不通或明显生硬；③人名地名等专名前后不一致；④残留外文或乱码。"
    "不要报告风格偏好、不要建议改写、不要夸奖。"
    "以下不算问题，禁止报告："
    "⟦i⟧、⟦/i⟧ 是有意的斜体排版标记，不是乱码；"
    "原文与译文的分段边界可能不同，段号对不上本身不是问题，只按译文自己的段号引用；"
    "原文中本来就有的外语词句（引语、标题、人名原文）被保留是译者的选择，不是残留；"
    "对“误译”的判断必须先通读整个窗口再下结论，拿不准的不报。"
    "每条问题必须给出段号（从1开始，按空行分段）、原文片段和问题说明。若没有问题，返回空数组。"
    "只输出 JSON：{\"issues\":[{\"para\":12,\"src\":\"...\",\"zh\":\"...\",\"why\":\"...\"}],"
    "\"verdict\":\"pass 或 needs_work\"}。"
)


def units(books=None, trees=("work_pub",)):
    out = []
    for tree in trees:
        for fp in sorted(glob.glob(os.path.join(ROOT, tree, "*", "out", "*", "c*",
                                                "final.txt"))):
            if os.path.getsize(fp) < 800:
                continue
            book = os.path.relpath(fp, os.path.join(ROOT, tree)).split(os.sep)[0]
            if books and book not in books:
                continue
            rel = os.path.relpath(fp, os.path.join(ROOT, tree, book, "out"))
            key = rel.replace(os.sep, "/")[:-len("/final.txt")]
            out.append((tree, book, key, fp))
    return out


def source_for(tree, book, key):
    cid, _, sub = key.rpartition("/")
    i = int(sub.lstrip("c"))
    try:
        spec = json.load(open(os.path.join(ROOT, tree, book, "chunks", cid + ".json"),
                              encoding="utf-8"))
        blocks = spec["chunks"][i]
    except Exception:                                          # noqa: BLE001
        return ""
    return "\n\n".join((b.get("text") or "").strip() for b in blocks if isinstance(b, dict))


def review(tree, book, key, fp, models):
    zh = open(fp, encoding="utf-8").read()
    src = source_for(tree, book, key)
    # The endpoint's fast zone measured 2026-10-30: ≤1000 chars in, 4-10 s back;
    # 2000 already sits on the 125 s edge; 3500+ mostly 524s. Window stays a *prefix*
    # so the paragraph numbers the model reports stay valid against the full text.
    user = (f"原文：\n<source>\n{src[:700]}\n</source>\n\n"
            f"译文：\n<translation>\n{zh[:1300]}\n</translation>\n\n"
            f"只输出一行紧凑 JSON，不要 markdown 代码块。issues 最多 3 条，"
            f"why 不超过 14 字，src/zh 只摘不超过 12 字的片段。")
    last = ""
    for _ in range(3):
        try:
            t, _used = llm.chat_pool([{"role": "system", "content": SYS},
                                      {"role": "user", "content": user}],
                                     models,
                                     max_tokens=700, temperature=0.2,
                                     tag=f"review:{book}/{key}", timeout=140,
                                     retries=2)
        except Exception as e:                                  # noqa: BLE001
            last = str(e)[:120]
            continue
        m = re.search(r"\{[\s\S]*\}", t)
        if not m:
            last = "no json"
            continue
        try:
            d = json.loads(m.group(0))
        except Exception:                                       # noqa: BLE001
            last = "bad json"
            continue
        d.update({"book": book, "unit": key})
        return d
    return {"book": book, "unit": key, "error": last}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.environ.get("REVIEW_POOL", ""),
                    help="comma-separated rotating pool; default = the cssm-free family pool")
    ap.add_argument("--per-book", type=int, default=1)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--books", default="")
    ap.add_argument("--trees", default="work_pub",
                    help="comma-separated work trees to sample (work_pub,work_gutenberg)")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    models = [m.strip() for m in a.model.split(",") if m.strip()] or [
        "csf:DeepSeek-V4.1-Flash", "csf:MiMo-V2.6-Flash",
        "csf:GLM-5.3-Flash", "csf:Qwen3.8-Flash-Next"]
    books = [b.strip() for b in a.books.split(",") if b.strip()] or None

    by_book: dict[str, list] = {}
    for tree, book, key, fp in units(books, tuple(
            t.strip() for t in a.trees.split(",") if t.strip())):
        by_book.setdefault(book, []).append((tree, key, fp))
    rnd = random.Random(a.seed)
    picks = []
    for book, items in sorted(by_book.items()):
        rnd.shuffle(items)
        for tree, key, fp in items[:a.per_book]:
            picks.append((tree, book, key, fp))

    if a.limit:
        rnd.shuffle(picks)
        picks = picks[:a.limit]
    print(f"reviewing {len(picks)} units over {len(by_book)} books with {','.join(models)}")
    os.makedirs(OUT, exist_ok=True)
    cache_dir = os.path.join(OUT, "review_cache")
    os.makedirs(cache_dir, exist_ok=True)

    def cache_path(book, key):
        return os.path.join(cache_dir, book + "__" + key.replace("/", "_") + ".json")

    # Resumable: the endpoint is unreliable, so a unit that already answered is never
    # re-asked. Coverage accumulates across waves instead of dying with one run.
    todo, out = [], []
    for t, b, k, f in picks:
        cp = cache_path(b, k)
        if os.path.exists(cp):
            try:
                out.append(json.load(open(cp, encoding="utf-8")))
                continue
            except Exception:                                  # noqa: BLE001
                pass
        todo.append((t, b, k, f, cp))
    print(f"cached={len(out)} todo={len(todo)}")
    with ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(review, t, b, k, f, models) for t, b, k, f, cp in todo]
        for n, f in enumerate(as_completed(futs), 1):
            r = f.result()
            out.append(r)
            # write through immediately -- a later crash must not lose finished units
            json.dump(r, open(cache_path(r["book"], r["unit"]), "w", encoding="utf-8"),
                      ensure_ascii=False)
            bad = len(r.get("issues") or [])
            print(f"  {n}/{len(todo)} {r['book']}/{r['unit']} "
                  f"{'ERR ' + r['error'] if r.get('error') else f'{bad} issues'}")
    path = os.path.join(OUT, "pub_sample_review.json")
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", path)


if __name__ == "__main__":
    main()
