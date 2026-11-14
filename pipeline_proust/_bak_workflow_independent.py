"""Independent Proust translation workflow — all seven volumes.

Nothing here consults an existing Chinese translation. The writer gets the French
source, a self-authored name table (`names_proust.py`) and a style contract that
targets readable literary Chinese (`style_independent.py`).

Cost model
----------
The project now runs on per-token billing with prompt caching, which changes what
"efficient" means. Two rules follow:

1. **The prompt prefix must be byte-identical across calls.** The name table and
   the style contract therefore live in the *system* message, unpruned, even though
   a given chunk only needs a dozen of the 174 names. A cached prefix bills at a
   fraction of an uncached one; a prefix that changes per chunk never caches.
2. **Per-chunk task prompts stay small and stable in shape**, so the cached prefix
   extends as far into the request as possible.

Translation itself is two calls per chunk by default:

  1. draft   — translate the French, paragraph for paragraph
  2. polish  — fix translationese; also the natural place for a fidelity repair,
               because the polisher sees the source anyway

An optional audit stage (a third call that hunts mistranslation) is off by default.
It roughly doubles cost, and on this account both calls would hit the same model,
so it is one mind grading its own paper. Turn it on only when a chunk looks wrong.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, "E:/Translate/pipeline_whale")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import llm
import names_proust as names
from style_independent import STYLE, WEAKNESS_ALERT

CJK = re.compile(r"[\u4e00-\u9fff]")

# The whole name table, once. Never filtered per chunk — see "Cost model" above.
GLOSSARY_ALL = names.render(dict(names.ALL))

SYS_WRITER = (
    "你是一位当代中国最优秀之一的法译中文学译者，独立翻译过普鲁斯特。"
    "你在做一部全新的《追忆似水年华》全译本，这是你自己的译本，"
    "不与任何既有中译本衔接，也不模仿任何既有中译本的文风。\n\n"
    + STYLE + "\n\n" + WEAKNESS_ALERT + "\n\n" + GLOSSARY_ALL
)

SYS_POLISHER = (
    "你是中文文学编辑，任务是改掉译稿里的翻译腔，让它读起来像中文作家写的句子。"
    "你改的是句子的走法，不是句子的意思：意思一个字都不能动，段落一行都不能增删。\n\n"
    + STYLE + "\n\n" + GLOSSARY_ALL
)

SYS_REVIEWER = (
    "你是资深文学编辑兼法文校勘者。你只对照法语原文挑硬错：漏译、增译、误译、"
    "丢掉的从句、被压平的插入语、被篡改的动作次序、专名与术语表不符。"
    "不评论文风好坏，不写赞美，不重写全文。\n\n" + GLOSSARY_ALL
)

_REASONING = re.compile(
    r"(?:^|\n)\s*(?:We need|We must|I need|Let's|Let me|Need to|Need ensure"
    r"|首先|我们需要|需要译|需要确保|需要输出|要译|下面|首先我们"
    r"|### (?:Instruction|Response|Thinking)|<source>|<first_translation>"
    r"|<system>|译文如下|要逐段|必须逐段)", re.I)

_MARKDOWN = re.compile(r"(?m)^\s*(?:#{1,6}\s|[-*+]\s|\d+\.\s)|(\*\*|__|```)")


# ── guards ──────────────────────────────────────────────────────────────

def looks_like_reasoning(text: str) -> bool:
    if not text or not text.strip():
        return True
    if _REASONING.search(text[:600]):
        return True
    cjk = len(CJK.findall(text))
    return cjk < 0.25 * max(1, len(text))


def strip_fence(t: str) -> str:
    t = t.strip()
    t = re.sub(r"^```[\w-]*\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    for tag in ("first_translation", "refined_final_translation", "polished",
                "translation", "audit", "answer"):
        t = re.sub(rf"^\s*<{tag}>\s*", "", t)
        t = re.sub(rf"\s*</{tag}>\s*$", "", t)
    return t.strip()


def para_list(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def check(src_paras: int, text: str, gl_entries: dict[str, str] | None = None) -> list[str]:
    """Mechanical problems in a candidate translation. Empty list = pass."""
    bad = []
    if looks_like_reasoning(text):
        return ["looks like reasoning, not a translation"]
    ps = para_list(text)
    if src_paras and len(ps) != src_paras:
        bad.append(f"paragraph count {len(ps)} != source {src_paras}")
    if _MARKDOWN.search(text):
        bad.append("markdown leaked")
    cjk = len(CJK.findall(text))
    if cjk < 0.30 * max(1, len(text)):
        bad.append(f"too few CJK characters ({cjk}/{len(text)})")
    for fr in (gl_entries or {}):
        if len(fr) < 4 or "'" in fr:
            continue
        if re.search(r"(?<![A-Za-zÀ-ÿ])" + re.escape(fr) + r"(?![A-Za-zÀ-ÿ])", text):
            bad.append(f"untranslated name: {fr}")
            if len(bad) > 4:
                break
    return bad


# ── prompts ─────────────────────────────────────────────────────────────

def p_draft(source: str) -> str:
    return f"""请把下面这段法语原文完整译成中文。

硬性要求：
- 逐段对应：原文几段，译文几段，顺序不变，不合并、不拆分、不增删。
- 句子怎么断由中文决定：能一口气读完就保留长句，读不通就断开重排。
  断的是句子，不是层次——原文的让步、转念、补充、自我修正都得在。
- 语气跟着这一段的内容走：段在讲什么，就用什么调子。
- 专名一律照系统消息里的对照表，不译成法语原文，不加括号注原文。
- 不写任何说明、译注、括号解释；不加 markdown 标记。

<source>
{source}
</source>

把完整译文放在 <first_translation> 与 </first_translation> 之间。"""


def p_polish(source: str, current: str) -> str:
    return f"""下面是一份中文译稿。请做**润色与校订**：先核准原意，再改掉翻译腔。

两部分都要做：
1. 对原意：漏译的分句、被压平的从句层级、被跳过的插入语、译错的词，补正回来。
2. 改文风，这稿可能有两种毛病，哪边都改：
   - 拗口：主语悬空、"的"字堆叠、欧化语序、名词化的动词、滥用的"被"字。
     这种句子该缩短、该重排、该把名词还原成动作。
   - 稀碎：原文一个完整的思绪被切成了一串等长短句，读着像电报。
     这种该合回去，用逗号和分号扛起来。

允许改：语序、断句、虚词、指代、被动句、标点、必要的词义订正。
**禁止改**：信息量、细节、段落数、段落顺序、专名。

改完必须与原文逐段对得上：原文一段，译文一段。

<source>
{source}
</source>

<current_translation>
{current}
</current_translation>

把润色后的完整译文放在 <polished> 与 </polished> 之间。只输出译文，不写说明。"""


def p_audit(source: str, draft: str) -> str:
    return f"""对照法语原文，核查下面这份中文译稿。只挑硬错：

1. 漏译：原文有的句子、分句、形容词、动作次序，译文没有。
2. 增译：译文有而原文没有的信息、解释、评价。
3. 误译：意思错了。
4. 丢从句层级：parce que / bien que / si / quoique / dont 等关系被拍平成并列句。
5. 丢插入语：原文用逗号或破折号夹住的插入成分被跳过或压缩。
6. 专名：与对照表不符。

只列问题，每条写成：
- 【类型】原文片段 → 译文片段 → 应改为

没有问题的项不要写。最后一行写"可以定稿"或"需要返工"。
放在 <audit> 与 </audit> 之间。

<source>
{source}
</source>

<translation>
{draft}
</translation>"""


def p_repair(source: str, draft: str, problems: str) -> str:
    return f"""下面是法语原文、一份中文译稿，以及编辑提出的问题。请逐条修正后输出完整译稿。

要求：段落数与原文严格一致；未被指出问题的地方不要动；不写说明。

<source>
{source}
</source>

<current_translation>
{draft}
</current_translation>

<problems>
{problems}
</problems>

把修正后的完整译稿放在 <refined_final_translation> 与 </refined_final_translation> 之间。"""


# ── transport ───────────────────────────────────────────────────────────

def _chat(system: str, user: str, model: str, tag: str,
          max_tokens: int = 32000, temperature: float = 0.4,
          timeout: float = 1800.0):
    """One model, one call. Returns (text, meta)."""
    msgs = [{"role": "system", "content": system},
            {"role": "user", "content": user}]
    t, _used, meta = llm.chat(msgs, model, max_tokens=max_tokens,
                              temperature=temperature, tag=tag,
                              timeout=timeout, with_meta=True)
    return t, meta


def _cached_tokens(meta: dict) -> int:
    u = (meta or {}).get("usage") or {}
    return ((u.get("prompt_tokens_details") or {}).get("cached_tokens")) or 0


# ── main entry ──────────────────────────────────────────────────────────

def translate_chunk(units: list[str], outdir: str, models: dict, tag_: str,
                    resume: bool = True, audit: bool = False,
                    max_attempts: int = 3) -> dict:
    """Draft → polish [+ optional audit/repair] for one chunk. Writes final.txt."""
    os.makedirs(outdir, exist_ok=True)
    final_path = os.path.join(outdir, "final.txt")
    meta_path = os.path.join(outdir, "meta.json")
    if resume and os.path.exists(final_path) and os.path.getsize(final_path) > 0:
        return {"cached": True}

    source = "\n\n".join(u.strip() for u in units)
    src_paras = len(para_list(source))
    gl_entries = names.relevant(source)
    meta: dict = {"models": [], "errors": [], "stages": {}, "cached_tok": 0}

    writer = models["writer"][0]
    polisher = models["polisher"][0]

    # 1. draft
    draft = None
    last_bad = ""
    for attempt in range(max_attempts):
        try:
            t, m = _chat(SYS_WRITER, p_draft(source), writer, f"{tag_}:draft")
            meta["cached_tok"] += _cached_tokens(m)
            t = strip_fence(t)
            bad = check(src_paras, t, gl_entries)
            if not bad:
                draft = t
                meta["models"].append(f"draft:{writer}")
                break
            last_bad = "; ".join(bad[:3])
            meta["errors"].append(f"draft#{attempt + 1} rejected: {last_bad}")
        except Exception as e:                                    # noqa: BLE001
            last_bad = str(e)[:100]
            meta["errors"].append(f"draft#{attempt + 1}: {last_bad}")
    if draft is None:
        raise RuntimeError(f"draft failed for {tag_}: {last_bad}")

    # 2. optional audit + repair
    if audit:
        try:
            t, m = _chat(SYS_REVIEWER, p_audit(source, draft), writer,
                         f"{tag_}:audit", max_tokens=8000, temperature=0.2)
            meta["cached_tok"] += _cached_tokens(m)
            problems = strip_fence(t)
            meta["stages"]["audit"] = problems[:800]
            if "需要返工" in problems:
                t, m = _chat(SYS_WRITER, p_repair(source, draft, problems), writer,
                             f"{tag_}:repair")
                meta["cached_tok"] += _cached_tokens(m)
                t = strip_fence(t)
                if not check(src_paras, t, gl_entries):
                    draft = t
                    meta["models"].append("repair")
        except Exception as e:                                    # noqa: BLE001
            meta["errors"].append(f"audit:{str(e)[:70]}")

    # 3. polish (with fidelity repair folded in)
    best = draft
    for attempt in range(max_attempts):
        try:
            t, m = _chat(SYS_POLISHER, p_polish(source, draft), polisher,
                         f"{tag_}:polish", temperature=0.35)
            meta["cached_tok"] += _cached_tokens(m)
            t = strip_fence(t)
            if check(src_paras, t, gl_entries):
                meta["errors"].append(f"polish#{attempt + 1} rejected")
                continue
            best = t
            meta["models"].append(f"polish:{polisher}")
            break
        except Exception as e:                                    # noqa: BLE001
            meta["errors"].append(f"polish#{attempt + 1}: {str(e)[:70]}")

    with open(final_path, "w", encoding="utf-8") as f:
        f.write(best.strip() + "\n")
    meta["paras"] = len(para_list(best))
    meta["cjk"] = len(CJK.findall(best))
    meta["src_paras"] = src_paras
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    return meta
