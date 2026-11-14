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

# The whole name table, once. Used when `trim_glossary` is off.
GLOSSARY_ALL = names.render(dict(names.ALL))

# Behaviour switches, set per run so an A/B can be measured rather than argued about.
#
# trim_glossary: build the system message from the names this chunk actually contains
#   instead of all 174. The reasoning in the docstring above assumes a cached prefix
#   always wins, but measurement showed the prefix only caches within one chunk's own
#   three calls -- it is a different prefix for every chunk, because the dynamic part
#   sits inside a single user message. So the "never filter" rule was paying the full
#   2k-token table on every call for a cache hit that never arrived. Measured hit rate
#   was 16% on polish, not the ~100% the rule assumed.
#
# trim_source: drop the French source from the polish request. Polish already receives
#   the aligned draft, and the source is the largest repeated block in the whole
#   pipeline. The cost is that polish can no longer catch omitted clauses wholesale;
#   `max_correction` bounds how far it may rewrite without the source to check against.
# Behaviour switches, set per run so an A/B can be measured rather than argued about.
#
# Everything below is the outcome of measurement, not of intuition:
#
# trim_glossary: build the system message from the names this chunk actually contains
#   instead of all 174. The docstring above assumes a cached prefix always wins, but the
#   prefix only ever caches *within* one chunk's own calls -- it differs for every chunk,
#   because the dynamic part sits inside a single user message. So the "never filter"
#   rule paid ~2k tokens of name table on every call for a cache hit that never arrived;
#   measured polish hit rate was 16%, not the ~100% assumed. Trimming measured -29% prompt
#   on draft, -42% on polish, and won a blind pairwise judge 4:1.
#
# trim_source: drop the French from the polish request. Polish already holds an aligned
#   draft, and the source was the largest repeated block in the pipeline. The risk was
#   that polish would no longer catch omitted clauses, so `max_correction` bounds how far
#   it may move without the source to check against; the same judge preferred the trimmed
#   output 4:1, so the risk did not materialise at this budget.
#
# Wall time barely moved (-1%) despite the token cut. Latency is decode-bound, not
#   prefill-bound: a fixed input with 20 vs 240 output tokens differed by 861ms, i.e.
#   ~3.9ms per emitted token over a 256 tok/s pipe. The real cost per chunk was the
#   *number of stages that emit a full rewrite*, which is why audit is off by default --
#   see below.
OPTIONS = {"trim_glossary": True, "trim_source": True,
           "max_correction": 0.12}

SYS_WRITER_HEAD = (
    "你是一位当代中国最优秀之一的法译中文学译者，独立翻译过普鲁斯特。"
    "你在做一部全新的《追忆似水年华》全译本，这是你自己的译本，"
    "不与任何既有中译本衔接，也不模仿任何既有中译本的文风。\n\n"
    + STYLE + "\n\n" + WEAKNESS_ALERT + "\n\n"
)

SYS_POLISHER_HEAD = (
    "你是中文文学编辑，任务是改掉译稿里的翻译腔，让它读起来像中文作家写的句子。"
    "你改的是句子的走法，不是句子的意思：意思一个字都不能动，段落一行都不能增删。\n\n"
    + STYLE + "\n\n"
)

SYS_WRITER = SYS_WRITER_HEAD + GLOSSARY_ALL
SYS_POLISHER = SYS_POLISHER_HEAD + GLOSSARY_ALL


def _sys_writer(glossary: str) -> str:
    """System message for the draft call, optionally carrying a trimmed name table."""
    return SYS_WRITER_HEAD + (glossary if OPTIONS["trim_glossary"] else GLOSSARY_ALL)


def _sys_polisher(glossary: str) -> str:
    return SYS_POLISHER_HEAD + (glossary if OPTIONS["trim_glossary"] else GLOSSARY_ALL)

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


def restore_separators(text: str, slots: dict[int, str]) -> str:
    """Re-insert the ornamental paragraphs at their original positions.

    `slots` maps an insertion point to the ornament: key `n` means "before translated
    paragraph n". Nothing in the translated text refers to them, which is the point --
    the model is never asked to carry a placeholder it has no reason to keep.

    An insertion point past the end of the translated body is appended, so a trailing
    rule survives. The paragraph-count check runs on the prose alone, so a genuinely
    short draft still fails rather than being padded out to look correct.
    """
    if not slots:
        return text
    paras = para_list(text)
    out: list[str] = []
    for i in range(len(paras) + 1):
        if i in slots:
            out.append(slots[i])
        if i < len(paras):
            out.append(paras[i])
    for k in sorted(slots):
        if k > len(paras):
            out.append(slots[k])
    return "\n\n".join(out)


def para_list(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


# A paragraph that carries no prose: an ellipsis, a rule of asterisks, a dinkus. These
# come from the printed page and the chunker kept them because they are separated by
# blank lines like any other paragraph. Asking the model to translate them fails in one
# of two directions, and both were observed: it drops them (`paragraph count 1 != 2`)
# or it copies them through and trips the markdown guard (`* * * * *` reads as a list
# bullet). Neither is a translation problem, so neither should be solved by prompting.
_SEPARATOR = re.compile(
    r"^(?:[\s.·•*＊\-—–_~#/\\]+)$")


def is_separator(text: str) -> bool:
    """True for paragraphs that are punctuation or ornaments only."""
    s = text.strip()
    if not s or len(s) > 40:
        return False
    if CJK.search(s):            # a line with Chinese in it is text, whatever else it has
        return False
    if re.search(r"[A-Za-zÀ-ÿ0-9]", s):   # ditto for latin letters and digits
        return False
    return bool(_SEPARATOR.match(s))


def check(src_paras: int, text: str, gl_entries: dict[str, str] | None = None) -> list[str]:
    """Mechanical problems in a candidate translation. Empty list = pass."""
    bad = []
    if looks_like_reasoning(text):
        return ["looks like reasoning, not a translation"]
    ps = para_list(text)
    if src_paras and len(ps) != src_paras:
        bad.append(f"paragraph count {len(ps)} != source {src_paras}")
    # placeholder paragraphs are structural, not prose; they must not be judged as
    # markdown or as a failed translation
    prose = [p for p in ps
             if not re.fullmatch(r"\[?\s*(?:SEP|分割线)\s*\d+\s*\]?", p)]
    probe = "\n\n".join(prose) if prose else text
    if _MARKDOWN.search(probe):
        bad.append("markdown leaked")
    cjk = len(CJK.findall(probe))
    if cjk < 0.30 * max(1, len(probe)):
        bad.append(f"too few CJK characters ({cjk}/{len(probe)})")
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


def _similarity(a: str, b: str) -> float:
    """Share of characters kept, measured on the shorter string.

    Used only to bound how freely the polisher may rewrite when it cannot see the
    source. Character-level overlap is crude, but the question here is blunt: did this
    pass touch a fifth of the text, or a line? Any reasonable metric answers that.
    """
    if not a or not b:
        return 0.0
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()


def p_polish_short(current: str, src_paras: int, max_correction: float) -> str:
    """Polish without the French source.

    The source is dropped because it is the largest repeated block in the pipeline and
    polish already holds an aligned draft. What replaces it is a hard budget on how much
    text this pass may move: with the source present the polisher is allowed to rewrite
    freely while checking against it, but a rewrite of that size with nothing to check
    against is how translations drift. The budget keeps this pass to what it is good at
    -- sentence rhythm, connectives, word order -- and leaves fidelity to the draft.
    """
    return f"""下面是一份中文译稿，共 {src_paras} 段。请润色。

只改这些：拗口（主语悬空、"的"字堆叠、欧化语序、名词化的动词、滥用的"被"字）、
稀碎（一个完整的思绪被切成等长短句，读着像电报）、虚词、指代、标点、语气不匀。

严格禁止：增删信息、改变意思、合并或拆分段落、改动专名。
改动幅度必须小：整段只该动句子怎么走，不该动它说什么。

润色后仍必须是 {src_paras} 段。

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

    # Ornamental paragraphs (an ellipsis, a row of asterisks) are not prose and cannot be
    # translated. Two earlier attempts kept them in the prompt behind a placeholder --
    # first `[SEP1]`, then a Chinese label in corner brackets -- on the theory that the
    # model would carry the marker through. It never did: both forms were silently
    # deleted, and the paragraph-count guard then rejected every attempt at these two
    # chunks, which is exactly why they were the last two failures left in Proust.
    #
    # So the model never sees them. They are removed from the prompt, the prose is
    # translated and checked on its own, and the ornaments are re-inserted by position
    # afterwards. That also matches what they are: a rule between scenes is page
    # furniture, not a sentence, and there is nothing in it to translate.
    units_prose: list[str] = []
    slots: dict[int, str] = {}
    for u in units:
        s = u.strip()
        if is_separator(s):
            slots[len(units_prose)] = s
        else:
            units_prose.append(s)

    source = "\n\n".join(units_prose)
    src_paras = len(units_prose)
    gl_entries = names.relevant(source)
    glossary = names.render(gl_entries) if OPTIONS["trim_glossary"] else GLOSSARY_ALL
    meta: dict = {"models": [], "errors": [], "stages": {}, "cached_tok": 0,
                  "prompt_chars": {"system": len(glossary)},
                  "separators": {str(k): v for k, v in slots.items()}}
    writer = models["writer"][0]
    polisher = models["polisher"][0]

    # 1. draft
    draft = None
    last_bad = ""
    for attempt in range(max_attempts):
        try:
            t, m = _chat(_sys_writer(glossary), p_draft(source), writer,
                         f"{tag_}:draft")
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
                t, m = _chat(_sys_writer(glossary), p_repair(source, draft, problems),
                             writer, f"{tag_}:repair")
                meta["cached_tok"] += _cached_tokens(m)
                t = strip_fence(t)
                if not check(src_paras, t, gl_entries):
                    draft = t
                    meta["models"].append("repair")
        except Exception as e:                                    # noqa: BLE001
            meta["errors"].append(f"audit:{str(e)[:70]}")

    # 3. polish (fidelity repair folded in only when the source is present)
    best = draft
    trim = OPTIONS["trim_source"]
    # note: named `polish_prompt`, not `p_polish` -- that name is the function
    polish_prompt = (p_polish_short(draft, src_paras, OPTIONS["max_correction"])
                     if trim else p_polish(source, draft))
    for attempt in range(max_attempts):
        try:
            t, m = _chat(_sys_polisher(glossary), polish_prompt, polisher,
                         f"{tag_}:polish", temperature=0.35)
            meta["cached_tok"] += _cached_tokens(m)
            t = strip_fence(t)
            if check(src_paras, t, gl_entries):
                meta["errors"].append(f"polish#{attempt + 1} rejected")
                continue
            if trim:
                # With no source to check against, bound how much the pass may rewrite:
                # the draft is the reference for fidelity here, not the French. The
                # threshold is a safety net, and is logged whatever it decides, so the
                # real distribution accumulates and the number stops being a guess.
                sim = _similarity(draft, t)
                meta.setdefault("polish_sim", []).append(round(sim, 3))
                if sim < 1.0 - OPTIONS["max_correction"]:
                    meta["errors"].append(
                        f"polish#{attempt + 1} over-edited (sim={sim:.2f})")
                    continue
            best = t
            meta["models"].append(f"polish:{polisher}")
            break
        except Exception as e:                                    # noqa: BLE001
            meta["errors"].append(f"polish#{attempt + 1}: {str(e)[:70]}")

    with open(final_path, "w", encoding="utf-8") as f:
        f.write(restore_separators(best, slots).strip() + "\n")
    meta["paras"] = len(para_list(restore_separators(best, slots)))
    meta["cjk"] = len(CJK.findall(best))
    meta["src_paras"] = src_paras
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    return meta
