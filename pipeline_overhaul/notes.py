"""Footnotes: the four kinds the reader asked for (person, place, allusion,
term). Sparse by design — a note on every name would be a glossary, not an
edition. The model is told to skip anything the context already explains.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "pipeline_whale"))

import common  # noqa: E402
import llm  # noqa: E402

# bailian (qw/km/ds) returned "Access to model denied" mid-run; fall back to
# the channels that are still live. chat_pool tries them in order.
MODEL_POOL = os.environ.get(
    "NOTES_MODELS",
    "xm:mimo-v2.6-flash,oxd:deepseek-v4.1-flash,xm:mimo-v2.6-flash,mm:MiniMax-M3.1-Flash",
).split(",")

SYS = """你是这部译本的注释者。为本章挑出普通中文读者确实需要解释的条目。
四类：人名、地名、典故、术语。
只注真正构成阅读障碍的：
- 圣经、神话、历史、文学典故，以及书中不加说明就无从理解的专名；
- 捕鲸/航海/地方性行业术语；
- 作者虚构或借用的异域名物。
不注：读者从上下文能懂的；纯地理方位；小说人物（正文自会交代）。
每条注文 40—90 字，只给必要背景，不作评价，不剧透后文。
输出 JSON 数组，每项：
{"anchor":"译文里逐字出现的片段（8—20字，足以定位）","term":"条目名","kind":"人名|地名|典故|术语","text":"注文"}
每章最多 8 条。宁可少，不可滥。只输出 JSON。"""


def chapter_text(book: str, ch: dict) -> tuple[str, str]:
    if book == "whale":
        src = "\n".join(p["src"] for p in ch["paras"])
    else:
        src = "\n\n".join(ch["src_paras"])
    # notes must anchor to the text that will actually be published
    fin = common.load_json(os.path.join(common.WORK, book, "final", ch["id"] + ".json"))
    zh = "\n".join(fin["texts"]) if fin else (
        "\n".join(p["zh"] for p in ch["paras"]) if "paras" in ch else "\n".join(ch["zh"]))
    return src, zh


def one(book: str, cid: str) -> str:
    out = os.path.join(common.WORK, book, "notes", cid + ".json")
    if os.path.exists(out):
        return f"skip {cid}"
    ch = common.load_json(common.chapter_path(book, cid))
    src, zh = chapter_text(book, ch)
    user = (f"原文：\n{src[:14000]}\n\n译文：\n{zh[:14000]}\n\n"
            "请给出本章注释条目。")
    try:
        text, used = llm.chat_pool([{"role": "system", "content": SYS},
                            {"role": "user", "content": user}],
                           MODEL_POOL, max_tokens=3000, temperature=0.3,
                           tag=f"{book}:notes:{cid}", timeout=600)
        m = re.search(r"\[.*\]", text, re.S)
        items = json.loads(m.group(0)) if m else []
    except Exception as e:  # noqa: BLE001
        return f"!! {cid} {str(e)[:100]}"
    keep = []
    for it in items:
        a = (it.get("anchor") or "").strip()
        t = (it.get("text") or "").strip()
        if not a or not t or a not in zh:
            continue
        keep.append({"anchor": a, "term": it.get("term", ""),
                     "kind": it.get("kind", ""), "text": t})
    keep = keep[:8]
    common.save_json(out, keep)
    return f"{cid}: {len(keep)} notes"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, choices=["whale", "soledad", "lotr"])
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(os.path.join(common.WORK, a.book, "notes"), exist_ok=True)
    cids = sorted(os.path.splitext(f)[0] for f in
                  os.listdir(os.path.join(common.WORK, a.book, "ch")))
    with ThreadPoolExecutor(a.workers) as ex:
        for f in as_completed([ex.submit(one, a.book, c) for c in cids]):
            print(f.result(), flush=True)


if __name__ == "__main__":
    main()
