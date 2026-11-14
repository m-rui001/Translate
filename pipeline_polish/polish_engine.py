"""Polish existing Chinese translation — do not retranslate.

This is the second-generation polish engine. `engine.py` drove the first overhaul
of the seven delivered books; it works, but it is line-numbered, anchored to the
dead API key, and knows nothing about source alignment. This one is written for the
current situation, where the workspace holds ~6 million characters of finished
Chinese across thirty-odd books and the job is to lift all of it one register.

Design
------
* **Paragraph-in, paragraph-out.** The unit of work is a run of paragraphs, sent as
  numbered blocks, returned as the same numbered blocks. Count and order are
  enforced mechanically; a failed unit falls back to the original text, so the pass
  can only improve the manuscript.
* **Source is optional, and its absence is fine.** When the French/German/... source
  aligns to the Chinese (same paragraph count), it is included so the polisher can
  also repair mistranslation. When it does not align — chapter-heading runs, merged
  dialogue — the unit is polished as pure Chinese, which is the safer operation.
* **The prompt prefix is byte-stable.** Instructions live in the system message and
  never vary, so prompt caching applies across every call in the run.

Usage is via `run_polish_all.py`; see there for the queue and resume behaviour.
"""
from __future__ import annotations

import difflib
import json
import os
import re
import threading

import sys
sys.path.insert(0, "E:/Translate/pipeline_whale")

import llm

CJK = re.compile(r"[\u4e00-\u9fff]")

# Canned refusals the upstream content filter can glue onto an otherwise good reply.
# Writing one into the manuscript silently destroys that paragraph.
REFUSAL = re.compile(
    r"Sorry,?\s*I\s*(?:can(?:'|’)t|cannot)\s*(?:respond|help|answer)"
    r"|I\s+apologi[sz]e,?\s*but"
    r"|我无法(?:回答|协助|帮助)|抱歉[，,]\s*我(?:无法|不能)",
    re.I)

MODEL = os.environ.get("POLISH_MODEL", "csf:MiMo-V2.6-Flash")
# A pool is worth it here: the polish calls are short, so several free ids answer in
# seconds and the rotating start spreads the load instead of hammering one account.
# 2026-10-30: every other station (8317 gateway, xiaomi, old cssmapi key, bailian,
# openox) is dead or 403s, so the pool is cssm-free's own families. chat_pool rotates
# the starting member per call, which is what actually exercises every id -- a fixed
# list would be a failover chain and the first model would do all the work. Flash-class
# only: reasoning models burn the token budget before the first sentence.
POOL = [m.strip() for m in os.environ.get("POLISH_POOL", "").split(",") if m.strip()] \
    or [MODEL, "csf:DeepSeek-V4.1-Flash", "csf:GLM-5.3-Flash",
        "csf:Qwen3.8-Flash-Next"]

# Canonical renderings of proper nouns, loaded once. Used to reject a reply that
# renamed a character: the glossary is the contract, and a drift here silently
# breaks both the reader's memory and the footnote anchors keyed on those names.
_TERMS: dict[str, list[str]] = {}


def _load_terms() -> dict[str, list[str]]:
    """Every book's glossary, keyed by book.

    The `reports/terms_*.json` files are advisory and mostly empty; the real
    glossaries are the ones the translators were driven from, so `terms.termbase`
    is the source of truth here.
    """
    if _TERMS:
        return _TERMS
    try:
        import terms as _terms
    except Exception:  # noqa: BLE001
        return _TERMS
    for book in ("whale", "soledad", "lotr", "zauberberg", "camus", "chekhov",
                 "proust"):
        try:
            tb = _terms.termbase(book)
        except Exception:  # noqa: BLE001
            continue
        vals = [v for v in (tb.values() if isinstance(tb, dict) else tb)
                if isinstance(v, str) and 2 <= len(v) <= 10]
        if vals:
            _TERMS[book] = vals
    return _TERMS


def _terms_in(text: str) -> list[str]:
    """Canonical proper nouns that occur in this text.

    Scans every book's termbase rather than guessing the book: a paragraph carries no
    book identity. A false positive is harmless, because the check only fires when a
    term that was present has vanished from the reply.
    """
    hits = []
    for vals in _load_terms().values():
        hits += [v for v in vals if v in text]
    return sorted(set(hits), key=len, reverse=True)[:16]


# The style contract is deliberately short and absolute: this pass may not change
# what the text says, only how it reads. Anything longer invites the model to
# rewrite, which is exactly the failure mode being guarded against.
SYS = """你是中文文学编辑，正在润色一部已译完的长篇译作。

你的职责是**动手改**，不是审读。拿到一段译稿，先在心里找出所有翻译腔和拗口的句子，
然后逐句改写，输出改写后的完整译文。只把原文原样抄回来的回答是不合格的。

必须改掉的：
- 介词框架堆叠："把 X 添进了 Y 之中" → "把 X 添进 Y"。
- "的"字连缀："这几天来一直盼着重温的那些形象" → "这几天一直盼着重温的形象"。
- 主语悬空："她身材高挑，金发轻盈，梳得高高的" → "她个子高挑，一头金发梳得很高"。
- 硬配的动词："仿佛许诺了温柔" → "仿佛应许了温柔"；"让记忆去适合它们" → "让记忆迁就它们"。
- 名词化动词："进行了…的处理" → 还原为动词。
- 滥用"被"、"它是…的"套壳、欧化语序。
- 比喻直译后主谓不成立：按中文重新组织，使类比能立住。
- 稀碎：一个完整的思绪被切成等长短句，读着像电报——用逗号、分号合回去。
- 指代不清、语气不匀、标点误用、一句里虚词扎堆（究竟/无论/又或者/诚然/然而/于是/遂/便 两次以上）。

长句的处理：普鲁斯特的长句要保住它的层次（让步、转念、补充、自我修正一个都不能少），
但**不照抄法语语序**。层次靠动词连缀、标点分层、语序归位来承载。
读不通就断开重排，能一口气读完就保留。句子可以断，层次不能平。

绝对禁止：
- 增删信息：不补背景、不解释文化词、不加译注、不写"原文为…"、不加括号注外文。
- 增删段落：输入几段，输出几段，顺序不变。
- 改动专名、数字、日期、称谓。
- 为了"更优美"换近义词、改写比喻、调整叙事层次。
- 输出 markdown、序号、任何说明文字。

只输出润色后的段落，用空行分隔，与输入的段落一一对应。不要编号，不要前言后语。"""


def paras(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def _looks_bad(t: str, src_paras: int, orig_text: str = "",
               keep_terms: list[str] | None = None) -> str | None:
    """Return a reason string when the reply is unusable, else None."""
    if not t or not t.strip():
        return "empty"
    ps = paras(t)
    if src_paras and len(ps) != src_paras:
        return f"paragraph count {len(ps)} != {src_paras}"
    cjk = len(CJK.findall(t))
    orig_cjk = len(CJK.findall(orig_text)) if orig_text else len(t)
    # Some chapters are glossaries or dialect lists: the Chinese is a minority of
    # the characters by design. Judge the reply against the input's own CJK ratio
    # rather than against an absolute threshold.
    # A long paragraph that comes back much shorter has been summarised, not polished.
    # Interior monologue and set-piece description are exactly where this happens:
    # the model decides the passage is repetitive and trims it.
    if len(orig_text) >= 120 and len(t) < 0.80 * len(orig_text):
        return f"shrunk ({len(t)} vs {len(orig_text)})"
    if orig_cjk and cjk < 0.45 * orig_cjk:
        return f"CJK dropped ({cjk} vs {orig_cjk})"
    if not orig_cjk and cjk < 0.30 * max(1, len(t)):
        return f"too few CJK ({cjk}/{len(t)})"
    # Markdown leak check. The old version matched any line starting with a dash,
    # which flagged ordinary Chinese dialogue dashes (——) and the ⟦i⟧ italic
    # markers the assembler uses. Only real Markdown syntax counts.
    if re.search(r"(?m)^\s*(?:#{1,6}\s|```|\*\*|_(?:[^_]{3,})_\s*$)", t):
        return "markdown leaked"
    if re.search(r"(?m)^\s*\d+[.、)]\s+\S", t):
        return "numbering leaked"
    if re.search(r"<first_translation>|<polished>", t):
        return "wrapper leaked"
    # The upstream content filter occasionally appends a canned English apology to an
    # otherwise usable reply. Writing that into the manuscript corrupts it.
    if REFUSAL.search(t):
        return "refusal leaked"
    # Proper nouns must survive verbatim. The polish brief says so, but the model does
    # drift them (斯达巴克 -> 斯塔巴克, 奥雷里亚诺 -> 奥雷亚诺), and a renamed character
    # is a far worse defect than an awkward sentence.
    if keep_terms:
        lost = [k for k in keep_terms if k in orig_text and k not in t]
        if lost:
            return "term dropped: " + "/".join(lost[:3])
    return None


def polish_unit(zh: str, src: str = "", tag: str = "",
                temperature: float = 0.35, max_tokens: int = 32000,
                attempts: int = 3) -> tuple[str, dict]:
    """Polish one run of paragraphs. Returns (text, meta).

    `src` is included only when it is known to align paragraph-for-paragraph.
    """
    n = len(paras(zh))
    if n == 0:
        return zh, {"skip": "empty"}
    user = ""
    if src:
        user += ("下面是原文与对应译稿。原文用于核对，译稿是你要润色的对象。\n\n"
                 f"<source>\n{src.strip()}\n</source>\n\n")
    user += f"<translation>\n{zh.strip()}\n</translation>"

    meta = {"tries": 0, "cached": 0}
    last = ""
    for i in range(attempts):
        meta["tries"] = i + 1
        try:
            keep = _terms_in(zh)
            msgs = [{"role": "system", "content": SYS},
                    {"role": "user", "content": user}]
            if len(POOL) > 1:
                t, _used = llm.chat_pool(msgs, POOL, temperature=temperature,
                                         max_tokens=max_tokens, tag=tag,
                                         timeout=1800.0)
                m = None
            else:
                t, _used, m = llm.chat(msgs, POOL[0], temperature=temperature,
                                       max_tokens=max_tokens,
                                       tag=tag, timeout=1800.0, with_meta=True)
            meta["cached"] = (((m or {}).get("usage") or {})
                              .get("prompt_tokens_details", {}) or {}).get("cached_tokens") or 0
            t = t.strip()
            t = re.sub(r"^```[\w-]*\s*", "", t)
            t = re.sub(r"\s*```$", "", t)
            why = _looks_bad(t, n, zh, keep)
            if why:
                last = why
                continue
            return t.strip(), meta
        except Exception as e:                                    # noqa: BLE001
            last = str(e)[:110]
    meta["failed"] = last
    return zh, meta


def write_unit(path: str, text: str, backup_dir: str | None = None) -> None:
    """Atomically replace a unit's text, keeping one backup copy."""
    if backup_dir:
        os.makedirs(backup_dir, exist_ok=True)
        rel = os.path.relpath(path, "E:/Translate").replace(os.sep, "__")
        bak = os.path.join(backup_dir, rel)
        if not os.path.exists(bak):
            with open(bak, "w", encoding="utf-8") as f:
                f.write(open(path, encoding="utf-8").read())
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")
    os.replace(tmp, path)


def write_json_unit(path: str, new_texts: list[str], idx: list[int],
                    backup_dir: str | None = None) -> None:
    """Replace only the prose paragraphs of a chapter JSON, leaving headings,
    verse and front matter untouched."""
    if backup_dir:
        os.makedirs(backup_dir, exist_ok=True)
        rel = os.path.relpath(path, "E:/Translate").replace(os.sep, "__")
        bak = os.path.join(backup_dir, rel)
        if not os.path.exists(bak):
            with open(bak, "w", encoding="utf-8") as f:
                f.write(open(path, encoding="utf-8").read())
    doc = json.load(open(path, encoding="utf-8"))
    texts = doc.get("texts") or []
    if len(new_texts) != len(idx):
        raise RuntimeError(f"json unit: {len(new_texts)} texts vs {len(idx)} slots")
    for i, t in zip(idx, new_texts):
        texts[i] = t
    doc["texts"] = texts
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def no_displacement(before: list[str], after: list[str],
                    near: float = 0.82) -> bool:
    """True when no paragraph was silently moved to a different slot.

    Paragraph count is checked separately; this catches the subtler failure where a
    run of paragraphs comes back one slot out of step and the count still matches.
    A paragraph passes if its closest match in `before` is its own slot, or if the
    match is not unique (these books repeat lines, so duplicates are normal).
    """
    if len(before) != len(after):
        return False
    for i, y in enumerate(after):
        if before[i] == y:
            continue
        scores = [(difflib.SequenceMatcher(None, x, y).ratio(), j)
                  for j, x in enumerate(before)]
        top_s, top_j = max(scores)
        if top_j == i or top_s < near:
            continue
        if sum(1 for s, _ in scores if s >= near) == 1:
            return False
    return True
