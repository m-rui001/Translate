"""Fidelity check for the revision pass.

The reviser is told not to add or drop meaning, and it mostly obeys; but a
paragraph that reads better and says slightly less is exactly the failure mode
this project cannot afford. Every edited paragraph goes back to a different
model with the source beside it. Verdicts are per paragraph: ok / loss / add /
error, plus an optional corrected text.
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

MODEL = "xm:mimo-v2.6-flash"

SYS = """你是译文校对，只判断忠实，不判断文采。
给你原文、旧译、新译。逐条判断新译有没有：
- loss：丢掉原文的信息、意象、限定语；
- add：添加原文没有的信息；
- error：译错、指代错、逻辑关系错。
措辞更顺、句子更短，都不算问题。只有意义层面的偏差才算。
输出 JSON 数组，每项：
{"i": 段号, "verdict": "ok|loss|add|error", "why": "不超过20字", "fix": "仅当 verdict 不是 ok 时，给出改正后的整段译文"}
只输出 JSON。"""


def one(book: str, cid: str) -> str:
    rev_p = os.path.join(common.WORK, book, "rev", cid + ".json")
    out_p = os.path.join(common.WORK, book, "verify", cid + ".json")
    if os.path.exists(out_p) or not os.path.exists(rev_p):
        return f"skip {cid}"
    rev = common.load_json(rev_p)
    edits = rev.get("edits") or []
    if not edits:
        common.save_json(out_p, {"id": cid, "verdicts": []})
        return f"{cid}: no edits"
    ch = common.load_json(common.chapter_path(book, cid))
    if book == "whale":
        src = "\n".join(f"[{i}] {p['src']}" for i, p in enumerate(ch["paras"]))
    else:
        src = "\n\n".join(ch["src_paras"])
    body = []
    for e in edits:
        body.append(f"[{e['i']}]\n旧译：{e['old']}\n新译：{e['new']}")
    user = (f"原文：\n{src[:24000]}\n\n逐条核对：\n" + "\n\n".join(body))
    try:
        text, _ = llm.chat([{"role": "system", "content": SYS},
                            {"role": "user", "content": user}],
                           MODEL, max_tokens=6000, temperature=0.1,
                           tag=f"{book}:verify:{cid}", timeout=600)
        m = re.search(r"\[.*\]", text, re.S)
        verdicts = json.loads(m.group(0)) if m else []
    except Exception as e:  # noqa: BLE001
        return f"!! {cid} {str(e)[:100]}"
    clean = []
    for v in verdicts:
        if not isinstance(v, dict) or "i" not in v:
            continue
        clean.append({"i": int(v["i"]), "verdict": v.get("verdict", "ok"),
                      "why": (v.get("why") or "")[:40],
                      "fix": (v.get("fix") or "").strip()})
    common.save_json(out_p, {"id": cid, "verdicts": clean})
    bad = sum(1 for v in clean if v["verdict"] != "ok")
    return f"{cid}: {len(clean)} checked, {bad} flagged"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, choices=["whale", "soledad", "lotr"])
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(os.path.join(common.WORK, a.book, "verify"), exist_ok=True)
    cids = sorted(os.path.splitext(f)[0] for f in
                  os.listdir(os.path.join(common.WORK, a.book, "ch")))
    with ThreadPoolExecutor(a.workers) as ex:
        for f in as_completed([ex.submit(one, a.book, c) for c in cids]):
            print(f.result(), flush=True)


if __name__ == "__main__":
    main()
