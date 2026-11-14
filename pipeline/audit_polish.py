"""Faithfulness audit of a polished chapter against the English source.

The polish pass is allowed to change wording, never content. Machine checks in
polish.py catch length/sentence/name drift, but they cannot see a *sense* error
("但它们在暮色中挺立" — the "but" survives, yet the clause lost its "they could
not be guessed" force). So this pass asks a model to compare source vs. polished
paragraph and flag only paragraphs with a real loss or addition, then we revert
exactly those paragraphs to the pre-polish draft.

Usage
    python pipeline/audit_polish.py --chapters book2c07 --model css:deepseek-flash --dry
    python pipeline/audit_polish.py --chapters book2c07 --apply
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import threading
import time

import providers

SRC = "E:/Translate/work/src"
OUT = "E:/Translate/work/out"
POL = "E:/Translate/work/polish"
BAK = "E:/Translate/work/prepolish"
AUD = "E:/Translate/work/audit"
LOG = "E:/Translate/work/audit_calls.jsonl"

MODEL = "css:deepseek-flash"
BATCH = 12

SYS = """你是《魔戒》中文译本的审校。你的职责只有一个：找出**意思走样**的地方。
你不评文笔，不评喜欢不喜欢，只判断译文有没有偏离英文原文的事实与语气。"""

PROMPT = """逐段比对《魔戒》英文原文与中文译文，找出**意思走样**的段落。

<english>
{en}
</english>

<chinese>
{zh}
</chinese>

判定标准：只算下面几类为问题——
1. 漏掉原文的实义成分（如"height could not be guessed"里的"无法估量"被删）。
2. 添加原文没有的内容（意象、解释、因果、情绪）。
3. 意思翻转或走样（否定变肯定、主次颠倒、逻辑连接词误用）。
4. 数量、颜色、方位、动作顺序错了。

**不算**问题的：语序调整、句式重写、同义词替换、为押韵而换字、口语化程度变化、
专名译法不同、标点差异。文笔好坏一律不评。

只列出有问题的段落。没有问题的段落不要提。严格按下面的格式，每行一段：

[段号] 问题类型 | 原文关键处 | 译文对应处 | 一句修改建议

若某段有多处问题，另起一行再写一遍段号。若所有段落都没问题，只输出一行：OK
不要写任何别的话。"""


def log(rec):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def split_paras(t):
    return [b.strip() for b in re.split(r"\n\s*\n", t) if b.strip()]


def render_src(b):
    if b["type"] == "p":
        return b["text"].strip()
    return "<verse>\n" + "\n".join(l.strip() for l in b["lines"]) + "\n</verse>"


def audit_chapter(cid: str, model: str, apply: bool, dry: bool) -> dict:
    src = json.load(open(os.path.join(SRC, cid + ".json"), encoding="utf-8"))["blocks"]
    ch = os.path.join(OUT, cid, "chapter.md")
    raw = open(ch, encoding="utf-8").read()
    title, body = raw.split("\n", 1)
    cur = split_paras(body)

    bak_p = os.path.join(BAK, cid + ".json")
    if not os.path.exists(bak_p):
        return {"cid": cid, "skip": "no pre-polish snapshot"}
    draft = json.load(open(bak_p, encoding="utf-8"))
    if len(draft) != len(cur) or len(cur) != len(src):
        return {"cid": cid, "skip": f"长度不符 {len(draft)}/{len(cur)}/{len(src)}"}

    os.makedirs(AUD, exist_ok=True)
    findings: list[tuple[int, str]] = []
    for start in range(0, len(cur), BATCH):
        stop = min(start + BATCH, len(cur))
        cp = os.path.join(AUD, f"{cid}.{start:03d}.txt")
        if os.path.exists(cp):
            txt = open(cp, encoding="utf-8").read()
        else:
            en = "\n\n".join(f"[{i - start + 1}] {render_src(src[i])}" for i in range(start, stop))
            zh = "\n\n".join(f"[{i - start + 1}] {cur[i]}" for i in range(start, stop))
            try:
                txt, used = providers.chat(
                    [{"role": "system", "content": SYS},
                     {"role": "user", "content": PROMPT.format(en=en, zh=zh)}],
                    model, temperature=0.1, max_tokens=3000,
                    tag=f"audit:{cid}:{start}", retries=3, timeout=420.0)
            except Exception as e:  # noqa: BLE001
                log({"ts": round(time.time(), 1), "cid": cid, "start": start,
                     "error": str(e)[:200]})
                return {"cid": cid, "skip": f"call failed {str(e)[:60]}"}
            open(cp, "w", encoding="utf-8").write(txt)
        if txt.strip().startswith("OK"):
            continue
        for m in re.finditer(r"^\s*\[(\d+)\]\s*(.+)$", txt, re.M):
            idx = start + int(m.group(1)) - 1
            if 0 <= idx < len(cur):
                findings.append((idx, m.group(2).strip()[:200]))
        log({"ts": round(time.time(), 1), "cid": cid, "start": start,
             "found": len(findings)})

    if dry:
        for i, why in findings:
            tag = "改动且被标" if cur[i] != draft[i] else "原稿旧疾"
            print(f"  [{i+1}] {tag} | {why}")
            print(f"     曲: {cur[i][:80]}")
            print(f"     原: {draft[i][:80]}")
    # Only paragraphs the polish pass actually touched can be a *regression*.
    # Flags on untouched paragraphs describe the shipped draft, not this pass.
    revert = sorted({i for i, _ in findings if cur[i] != draft[i]})
    if apply and revert:
        for i in revert:
            cur[i] = draft[i]
        open(ch, "w", encoding="utf-8").write(title + "\n\n" + "\n\n".join(cur) + "\n")
    return {"cid": cid, "flagged": len(findings), "regressions": len(revert)}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", required=True)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    cids = [c.strip() for c in a.chapters.split(",")]
    for cid in cids:
        r = audit_chapter(cid, a.model, a.apply, a.dry)
        print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    main()
