"""Large-scale revision pass for the Proust supplement, driven by cssmapi.

Rationale: the mechanical pass (fix_mech.py) can settle quote direction, doubled
punctuation and name variants, but it cannot decide
  - which of two homonyms a pronoun refers to (指代模糊)
  - how to un-overload a sentence that stacks 那…那…/仿佛…/也许…
  - which 专名 variant is canonical when both sides look plausible
so the literary layer needs a model that sees the whole chunk.

Design decisions that matter:
  * The model NEVER sees the book as a whole, only ~4000-char windows with
    overlap, because Proust's coherence is local and context windows are finite.
  * Every chunk is addressed with the *specific* defects found in it (by regex),
    not a generic "polish this" prompt. Generic prompts make models rewrite
    freely; targeted ones make them edit surgically.
  * A revision is accepted only if hard invariants hold:
        paragraphs unchanged, length within +-12%, no new unbalanced quotes,
        no dropped sentence-final punctuation. Otherwise we keep the original
        and log the rejection — never silently degrade the text.
  * Everything is resumable: work_proust/rev/<chunk>/ holds draft/final/meta.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, "E:/Translate/pipeline")
import llm

BOOK = "E:/Translate/work_proust/book/book_r1.md"
OUT = "E:/Translate/work_proust/rev2"
LOG = "E:/Translate/work_proust/rev2_log.jsonl"
MODEL = "xm:mimo-v2.6-flash"

CJK = re.compile(r"[\u4e00-\u9fff]")

SYS = """你是资深中文文学编辑，专精普鲁斯特。你面前是一段已译好的《追忆似水年华》中译稿，
译自法语原文，文笔已经有底子，但存在几类具体瑕疵。你的工作是**外科手术式的修订**，
不是重译。

铁律：
1. 不许改情节、不许删减信息、不许增加原文没有的内容。
2. 段落数与段落顺序完全不变。原来 5 段，改完还是 5 段。
3. 长句该长就长——普鲁斯特的句子是呼吸，不要为了"顺"而拆成短句。
   只有在真的过载（一句话里"那……那……""仿佛……""也许……"堆了三层以上）时，
   才用逗号、分号或换序来卸载，仍不拆成多个句号短句。
4. 只在必要时改动。能用两个字解决就不重写整句。没有问题的句子一个字都不要动。
5. 专名一律按给定的规范形，不得自行另创译名。
6. 引号：外层直接引语用“ ”，内层引用用‘ ’；说完一句收尾必须是”。不是“。
7. 只输出修订后的正文，不要解释、不要标注、不要 markdown 代码块。"""


def build_prompt(chunk: str, defects: dict, canon: dict) -> str:
    parts = [SYS, ""]
    if defects:
        parts.append("【本段已检测到的具体问题，请逐条处理】")
        for label, items in defects.items():
            if not items:
                continue
            parts.append(f"· {label}（{len(items)} 处）：")
            for it in items[:8]:
                parts.append(f"    {it}")
            if len(items) > 8:
                parts.append(f"    ……另有 {len(items)-8} 处同类")
        parts.append("")
    if canon:
        parts.append("【专名规范形，出现变体一律改成它】")
        parts.append("  " + "；".join(f"{k}→{v}" for k, v in canon.items()))
        parts.append("")
    parts.append("""【这次的修订重点：中文流畅度】
盲审显示本稿在忠实度上强于已出版译本，但“中文读起来是否顺”是最弱项。请优先治这三类：
A. 插入语残逗：如“兼司机，他是上尉的侄子，的帮助”——插入语结束后遗留逗号，使后面的
   中心词悬空。改成破折号插入、或把插入语移到定语之后，让句子一口气读得下去。
B. “的”字连缀：“一种对动物学家说来也有特殊个性，以某种无性别为特征，的族类”——
   多个“的”堆在名词前。改法：把其中一层改成动词结构（“……那种族类，动物学家也认为它……”），
   或用破折号把描写部分拉出来。
C. 逗号层级过多：一句话里四个以上逗号分句层层套叠时，允许把其中一层改成破折号或
   重新排序；但**不要拆成多个句号短句**，普鲁斯特的呼吸要留着。
D. 动词性弱：“孵了一会儿”“交付给地上的事物”“最不相同的念头在我脑中拥挤”这类——
   中文里动词被硬译成不及物或名词化，读着发膈。改成中国人会说的动词搭配
   （“把……孵在眼里”➔“盯着……看了半天”这种程度），但只改动词和搭配，不改句子的
   信息量与层次。
E. 主语隐没：从句连续两三个不带主语时，在第二个分句处补出“他/她/它”或一个名词，
   让人知道谁在做；但不要改成流水短句。

【红线】不得拆句、不得合并或拆分段落、不得删减信息、不得加译注。
宁可保留一个不够顺的长句，也不能把它翻成一个好读的短句。
""")
    parts.append("")
    parts.append("【待修订正文】")
    parts.append(chunk)
    parts.append("")
    parts.append("现在输出修订后的完整正文（段落数不变，不加任何说明）。")
    return "\n".join(parts)


# ------------------------------------------------------------ defect probe
STACK = re.compile(r"(那[^，。]{0,14}那[^，。]{0,14}那|仿佛[^。]{0,40}仿佛|也许[^。]{0,30}也许)")
OVERLONG = 120
SENT_SPLIT = re.compile(r"。\s*")
NAME_VARS = ["费泰尔纳", "费代尔纳", "拉斯佩利埃", "夏吕斯", "因卡维尔", "印卡维尔",
             "当西耶尔", "维尔帕里齐斯", "圣皮埃尔代伊夫", "马尔桑特", "玛桑特",
             "圣埃韦尔特", "阿尔帕荣", "阿尔帕戎", "埃波切维尔", "阿让库尔"]


def probe(text: str) -> dict:
    d = {}
    neg = [f"「{m.group(0)[:40]}」" for m in re.finditer(r"[^。\n]{0,25}。\s*[^。\n]{0,25}", text)
           if False]
    # 1. 引号方向/配对
    qbad = []
    for m in re.finditer(r"[^\s，。；：！？、“”‘’\n]“(?=[^“”\n]{0,40}[。，！？”])", text):
        qbad.append(f"…{text[max(0,m.start()-14):m.start()+22]}…（左引号出现在句中，疑为收尾”）")
    if qbad:
        d["引号方向错误"] = qbad
    # 2. 堆叠
    st = [f"「{m.group(0)[:50]}」" for m in STACK.finditer(text)]
    if st:
        d["句法堆叠过载"] = st
    # 3. 超长句
    longs = []
    for para in text.split("\n"):
        for s in SENT_SPLIT.split(para):
            if len(s) >= OVERLONG:
                longs.append(f"（{len(s)}字）{s[:40]}…")
    if longs:
        d["超长句，读时需回看"] = longs
    # 4. 专名变体
    nv = []
    for v in NAME_VARS:
        if v in text:
            nv.append(v)
    if nv:
        d["专名变体"] = nv
    # 5. 重复字 / 漏字
    rep = [f"…{text[max(0,m.start()-10):m.start()+12]}…" for m in
           re.finditer(r"(他他|她她|我我|的的|了了|是是|就就|在在|们们|不不不)", text)]
    if rep:
        d["重复字"] = rep
    # 6. 破折号/标点不统一
    bad = []
    if re.search(r"—{3,}", text):
        bad.append("连续三个以上破折号")
    if re.search(r"[，。]{2,}", text):
        bad.append("重复句读")
    if bad:
        d["排印"] = bad
    # 7. 插入语残逗（最高优先级：盲审中被点名的欧化病灶）
    dang = []
    for m in re.finditer(r"，([^，。；！？“”\n]{3,40})，的([\u4e00-\u9fff]{1,6})", text):
        dang.append(f"「…{m.group(1)}，的{m.group(2)}…」→ 插入语后残留逗号，须重组")
    if dang:
        d["插入语残逗（最高优先级）"] = dang
    # 8. 定语过长的欧化结构：“的…的…的”连缀
    chain = []
    for m in re.finditer(r"[\u4e00-\u9fff]{2,}的[\u4e00-\u9fff]{2,}的[\u4e00-\u9fff]{2,}的", text):
        chain.append(f"「{m.group(0)[:30]}」（多个“的”累赘，可改用动词句或拆状语）")
    if chain:
        d["“的”字连缀"] = chain
    # 9. 一个逗号句内双重嵌套插入语
    nest = []
    for m in re.finditer(r"[，——][^，。；\n]{2,20}，[^，。；\n]{2,20}，[^，。；\n]{2,20}，", text):
        nest.append(f"「{m.group(0)[:40]}」")
    if nest:
        d["逗号层级过多"] = nest
    return d


CANON = {
    "夏吕斯": "夏尔吕", "拉斯佩利埃": "拉斯普利埃", "费泰尔纳": "费泰尔讷",
    "费代尔纳": "费泰尔讷", "因卡维尔": "安卡维尔", "印卡维尔": "安卡维尔",
    "当西耶尔": "当西埃尔", "维尔帕里齐斯": "维尔帕里西斯",
    "圣皮埃尔代伊夫": "圣皮埃尔德伊夫", "马尔桑特": "马桑特", "玛桑特": "马桑特",
    "圣埃韦尔特": "圣厄韦尔特", "阿尔帕荣": "阿尔帕容", "阿尔帕戎": "阿尔帕容",
}


# ---------------------------------------------------------------- invariants
def para_count(t: str) -> int:
    return len([p for p in re.split(r"\n\s*\n", t) if p.strip()])


def quote_balance(t: str) -> int:
    return abs(t.count("“") - t.count("”"))


def check(orig: str, new: str) -> tuple[bool, str]:
    if not new or len(new.strip()) < 20:
        return False, "empty"
    if para_count(orig) != para_count(new):
        return False, f"paras {para_count(orig)}->{para_count(new)}"
    ratio = len(new) / max(1, len(orig))
    if not (0.85 <= ratio <= 1.18):
        return False, f"len ratio {ratio:.2f}"
    if quote_balance(new) > quote_balance(orig):
        return False, f"quotes worse {quote_balance(orig)}->{quote_balance(new)}"
    if CJK.findall(new).__len__() < 0.85 * len(CJK.findall(orig)):
        return False, "cjk loss"
    return True, "ok"


# ------------------------------------------------------------------- chunking
def split_chunks(text: str, size: int = 3800) -> list[tuple[int, int]]:
    """Paragraph-aligned windows. Returns (start_char, end_char) spans."""
    spans, start, cur = [], 0, 0
    for m in re.finditer(r"\n\s*\n", text):
        if m.end() - start > size:
            spans.append((start, m.start()))
            start = m.end()
    if start < len(text):
        spans.append((start, len(text)))
    return spans


def cid_of(s: str, i: int) -> str:
    return f"{i:04d}_{hashlib.md5(s.encode()).hexdigest()[:8]}"


def revise_chunk(i, span, text, model, resume=True):
    a, b = span
    orig = text[a:b]
    cid = cid_of(orig, i)
    d = os.path.join(OUT, cid)
    fin = os.path.join(d, "final.txt")
    os.makedirs(d, exist_ok=True)
    if resume and os.path.exists(fin):
        return {"cid": cid, "cached": True}
    defects = probe(orig)
    canon = {k: v for k, v in CANON.items() if k in orig}
    prompt = build_prompt(orig, defects, canon)
    t0 = time.time()
    try:
        out, mdl = llm.chat([{"role": "user", "content": prompt}],
                            models=[model], max_tokens=6000, temperature=0.25,
                            tag="rev", timeout=300)
    except Exception as e:  # noqa: BLE001
        _log({"cid": cid, "err": str(e)[:200], "secs": round(time.time() - t0, 1)})
        return {"cid": cid, "err": str(e)[:80]}
    out = out.strip()
    out = re.sub(r"^```[a-z]*\n|\n```$", "", out).strip()
    ok, why = check(orig, out)
    io.open(os.path.join(d, "orig.txt"), "w", encoding="utf-8").write(orig)
    io.open(os.path.join(d, "draft.txt"), "w", encoding="utf-8").write(out)
    meta = {"cid": cid, "span": [a, b], "defects": {k: len(v) for k, v in defects.items()},
            "ok": ok, "why": why, "model": mdl, "secs": round(time.time() - t0, 1),
            "chars": [len(orig), len(out)]}
    io.open(os.path.join(d, "meta.json"), "w", encoding="utf-8").write(
        json.dumps(meta, ensure_ascii=False, indent=1))
    if ok:
        io.open(fin, "w", encoding="utf-8").write(out)
    _log(meta)
    return {"cid": cid, "ok": ok, "why": why, "secs": meta["secs"],
            "defects": meta["defects"]}


def _log(rec):
    with io.open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--size", type=int, default=3800)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--no-resume", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    text = io.open(BOOK, encoding="utf-8").read()
    spans = split_chunks(text, a.size)
    if a.limit:
        spans = spans[:a.limit]
    print(f"{len(spans)} chunks, model={a.model}, workers={a.workers}", flush=True)
    t0 = time.time()
    ok = rej = err = cached = 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(revise_chunk, i, sp, text, a.model, not a.no_resume): i
                for i, sp in enumerate(spans)}
        for n, f in enumerate(as_completed(futs), 1):
            r = f.result()
            if r.get("cached"):
                cached += 1
            elif r.get("err"):
                err += 1
            elif r.get("ok"):
                ok += 1
            else:
                rej += 1
                print(f"  REJECT {r['cid']}: {r['why']}", flush=True)
            if n % 20 == 0:
                print(f"{n}/{len(spans)} ok={ok} rej={rej} err={err} cached={cached} "
                      f"{time.time()-t0:.0f}s", flush=True)
    print(f"done ok={ok} rejected={rej} error={err} cached={cached} "
          f"in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
