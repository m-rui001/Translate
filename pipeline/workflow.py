"""Dadeumi-style iterative-refinement workflow, chunked for a full-length novel.

The stage sequence, XML-tag protocol and self-critique structure follow
hrishioa/dadeumi (MIT). Adapted for: chapter-level context injection, a mandated
glossary, Chinese literary register, and resumable chunk-level runs.
"""
from __future__ import annotations

import json
import os
import re

import llm
import postprocess
from style import WEAKNESS_ALERT
from glossary import G, relevant, render as render_glossary
from style import QA_CHECK, STYLE

# ─────────────────────────────────────────────────────────── chunking

def chunk_blocks(blocks: list[dict], target_words: int = 1500, max_words: int = 2100):
    """Split a chapter into chunks on paragraph/verse boundaries."""
    chunks, cur, nwords = [], [], 0

    def wc(b):
        if b["type"] == "p":
            return len(b["text"].split())
        return len(" ".join(b["lines"]).split())

    for b in blocks:
        w = wc(b)
        if cur and (nwords + w > max_words or (nwords >= target_words and w > 250)):
            chunks.append(cur)
            cur, nwords = [], 0
        cur.append(b)
        nwords += w
    if cur:
        chunks.append(cur)
    return chunks


def render_source(blocks: list[dict]) -> str:
    out = []
    for b in blocks:
        if b["type"] == "p":
            out.append(b["text"].strip())
        else:
            out.append("<verse>\n" + "\n".join(l.strip() for l in b["lines"]) + "\n</verse>")
    return "\n\n".join(out)


def counts(blocks: list[dict]) -> dict:
    return {
        "paras": sum(1 for b in blocks if b["type"] == "p"),
        "verses": [len(b["lines"]) for b in blocks if b["type"] == "verse"],
    }


# ─────────────────────────────────────────────────────────── tags

def tag(text: str, name: str) -> str:
    m = re.search(rf"<\s*{name}\s*>(.*?)(?:<\s*/\s*{name}\s*>|$)", text, re.S)
    if not m:
        return ""
    body = m.group(1)
    body = re.sub(rf"<\s*/?\s*{name}\s*>", "", body)
    return body.strip()


# Model reasoning that leaked into the content field instead of a real answer.
_REASONING_PAT = re.compile(
    r"(?:^|\n)\s*(?:We need|We must|I need|Let's|Let me|Need translate|Need to|Need ensure"
    r"|首先|我们需要|我需要|需要译|需要确保|需要输出|要译|下面|首先我们"
    r"|### (?:Instruction|Response|Thinking)|<source>|<first_translation>|<system>"
    r"|译文如下|译成中文时|要逐段|必须逐段|glossary|术语表要求)",
    re.I)


def looks_like_reasoning(text: str) -> bool:
    """True when a 'translation' is actually the model's scratchpad."""
    if not text:
        return True
    head = text[:600]
    if _REASONING_PAT.search(head):
        return True
    # a real Chinese translation is mostly CJK; reasoning leaks are mostly latin
    cjk = len(CJK.findall(text))
    return cjk < 0.25 * max(1, len(text))


def strip_fence(text: str) -> str:
    text = re.sub(r"^\s*```[a-zA-Z]*\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    text = re.sub(r"\*\*([^*\n]+)\*\*", _debold, text)
    text = re.sub(r"(?m)^\s*#{1,6}\s*", "", text)
    return text.strip()


def _debold(m):
    return m.group(1)

# ─────────────────────────────────────────────────────────── prompts

SYS_WRITER = (
    "你是当代最优秀的中文文学译者之一，长期翻译托尔金、勒古恩一系的作品，"
    "汉语文笔老到，也懂得克制。你正在与编辑合作，逐段打磨《魔戒》的新译本。\n\n" + STYLE
)

SYS_REVIEWER = (
    "你是资深文学编辑与翻译批评家，同时精通英文与中文，读过《魔戒》原文多遍。"
    "你的职责是挑错：漏译、增译、误译、腔调不对、翻译腔、诗歌失韵、专名不一致。"
    "你只提具体问题，不做泛泛的赞美，也不必重写全文。"
)


def p_analysis(chapter_title, source):
    return f"""这是《魔戒》中「{chapter_title}」一章的英文原文。译文将由你与编辑逐步打磨，先做一次整体分析。

<source>
{source}
</source>

请输出以下内容（全部用中文，条目清晰，不要客套）：

1. 场景切分：按原文顺序列出各场景，标明地点、在场人物、发生了什么、语气（如紧张、舒缓、幽默、哀伤）。
2. 叙述语气与语域：叙述者的腔调在本章有何变化？哪些段落是古体、史诗体、口语体、仪式语言？
3. 人物说话特征：本章说话的人物各自的用词习惯、句长、语气，用两三句概括。
4. 译文用语基调：给译者三五条针对本章的具体建议（比如某段该用短句、某个词该反复出现以形成母题）。
5. 术语与名物：本章出现的专名、名物、称号、度量单位，凡术语表可能没收的，列出英文与建议中文译法。
6. 难处理之处：双关、古语、诗歌韵律、黍稷草木的专名、托尔金自造词，逐条给出处理方案。

请把全部内容放在 <analysis> 与 </analysis> 之间。"""


def p_expression(source, analysis):
    return f"""下面是本章的分析结论，供你参考：

<analysis>
{analysis}
</analysis>

现在请就下面这段原文做表达探索：找出 5 到 10 个最难译的地方（成语、双关、古语、自造词、诗歌句、动作描写），
对每一处给出两三种中文译法，并说明取舍理由。这一段还不必整体翻译。

<source>
{source}
</source>

请把内容放在 <expression_exploration> 与 </expression_exploration> 之间。"""


def p_first(source, analysis, glossary):
    return f"""{glossary}

<analysis>
{analysis}
</analysis>

{WEAKNESS_ALERT}

请把下面这段原文完整译成中文。要求：逐段对应，一段不漏，一段不并；<verse> 标记的诗行要保留分行与行数。

<source>
{source}
</source>

把完整译文放在 <first_translation> 与 </first_translation> 之间，不要写任何说明。"""


def p_critique(source, draft, glossary):
    return f"""{glossary}

下面是英文原文与目前的初稿译文。请以挑剔的编辑眼光批评它。

<source>
{source}
</source>

<draft>
{draft}
</draft>

请逐条指出问题，务必具体到句子：
- 漏译或并段：原文的哪句、哪段没有对应译文。
- 增译：译文里有而原文没有的意思、解释、情绪渲染。
- 误译：人物、方位、数量、因果、指代弄错的地方。
- 翻译腔：读起来不像中文的句子，指出应如何改写。
- 腔调：人物说话是否可分辨，叙述腔调是否合适。
- 诗歌：分行、行数、韵律、气势是否保住。
- 专名：与术语表不符的，逐一列出并改正。
- 标点与格式：引号、省略号、破折号、括号。

然后给出一版完整的改进译文。

把批评放在 <critique> 与 </critique> 之间，完整的改进译文放在 <improved_translation> 与 </improved_translation> 之间。"""


def p_second(source, draft, glossary):
    return f"""{glossary}

换一双新眼睛，再看一遍这份译文。

<source>
{source}
</source>

<draft>
{draft}
</draft>

这一次请特别看四件事：
1. 汉语的文学质地：有没有真正的中文节奏与意象，还是仅仅“意思对了”？哪些句子可以更好？
2. 忠实：细看原文的修饰语、次序、暗示，译文有没有偷工减料。
3. 一致性：同一专名、同一称谓、同一语气词，前后是否统一。
4. 朗读感：句子念出来是否别扭，有没有同音近音的误会。

批评完，请给出完整的再度改进译文。

把批评放在 <second_critique> 与 </second_critique> 之间，译文放在 <further_improved_translation> 与 </further_improved_translation> 之间。"""


def p_external(source, draft, glossary):
    return f"""{glossary}

请审读下面这份中译稿，对照英文原文挑错。

<source>
{source}
</source>

<translation>
{draft}
</translation>

只列问题，不重写全文。按重要性排序，每条格式为：

- 【类型】原文片段 → 译文片段 → 问题与改法（一句话）

类型限用：漏译／增译／误译／腔调／翻译腔／诗歌／专名／标点／其他。
最后用一两句话给出总体判断：这份译文是否达到出版水准。

把内容放在 <external_review> 与 </external_review> 之间。"""


def p_final(source, draft, review, glossary):
    return f"""{glossary}

<source>
{source}
</source>

<current_translation>
{draft}
</current_translation>

<external_review>
{review}
</external_review>

请吸收审读意见，逐条处理，给出定稿。你自己判断：意见合理的照改，不合理的可以不从，但要保证结果更好。
定稿必须完整，逐段对应原文，<verse> 诗行保留分行。

把定稿放在 <refined_final_translation> 与 </refined_final_translation> 之间。"""


def p_continue(source, partial):
    return f"""你正在翻译下面这段原文，上一段输出被截断了。请从截断处之后接着往下译，不要重复已经译过的内容，
也不要加任何说明，直接输出剩余的译文。

<source>
{source}
</source>

已经译出的部分（结尾处被截断）：
<partial>
{partial[-1200:]}
</partial>

请接着译完剩余部分，放在 <continued_translation> 与 </continued_translation> 之间。"""


def p_audit(source, draft, glossary):
    """Weakness-targeted review: only hunts the error classes this model family makes."""
    return f"""{glossary}

下面是英文原文和一份中文译稿。请**只查下面五类高危问题**，不要重写全文，不要管风格好坏。

<source>
{source}
</source>

<current_translation>
{draft}
</current_translation>

逐段核对：
1. 专名错位：原文出现的每个地名、人名、山川、族群，译文是否译对了**同一个对象**？
   特别小心"看起来眼熟就写成熟悉地名"的错误（例：Mindolluin 是明多立安山，不是米那斯提力斯）。
   把每个错的都列出来：原文 → 译文错写成 → 应改为术语表译法。
2. 诗性复合词：earth-thunder、sky-fields、death-odour、grey-cloak 这类，是否被拆开意译成了普通词？
   列出被"磨平"的地方。
3. 漏译：原文有而译文没有的句子、分句、数量、方位、颜色、气味。
4. 增译：译文有而原文没有的解释、评价、情绪渲染。
5. 数字与单位：阿拉伯数字、度量单位是否处理正确。

只列问题，格式：
- 【类型】原文片段 → 译文片段 → 应改为

最后一行给出总体判断：这段译文可以定稿 / 需要返工。

把内容放在 <audit> 与 </audit> 之间。"""


def p_proofread(draft, glossary):
    return f"""{glossary}

下面是一份已经译好的中文稿。请做最后一遍文字校对，只改错误，不改内容。

<draft>
{draft}
</draft>

逐项检查并修正：
1. 字数与段落：不得删减句子，不得合并段落，不得增加原文没有的内容。
2. 数字：阿拉伯数字一律改成中文读法。
3. 括号：一律化掉，改成短句、逗号或破折号。
4. 标点：中文全角标点；引号成对；不用分号；省略号用……；破折号用——。
5. 英文残留：不得出现拉丁字母。
6. 翻译腔与生硬句：改顺，但不许改意思、不许加解释。
7. 同音歧义、指代不清、说话人不明：修正。
8. 专名：与术语表一致。
9. 诗歌：保持分行，不得并入散文。

把校对后的完整中文稿放在 <proofread> 与 </proofread> 之间，不要写任何说明。"""


def p_review_apply(source, draft, glossary):
    return f"""{glossary}

<source>
{source}
</source>

<current_translation>
{draft}
</current_translation>

请做一次完整的编辑修订：
1. 先对照英文原文逐段挑错：漏译、误译、增译、误用的腔调、生硬的中文、专名不一致、诗歌失韵。
2. 然后给出修订后的完整中文稿，保留原段落结构，<verse> 诗行保留分行。

把挑错结论放在 <review> 与 </review> 之间，把修订后的完整中文稿放在 <refined_final_translation> 与 </refined_final_translation> 之间。"""


def p_repair(source, draft, problem):
    return f"""{problem}

请修正并重新给出完整译文。

<source>
{source}
</source>

<current_translation>
{draft}
</current_translation>

把修正后的完整译文放在 <refined_final_translation> 与 </refined_final_translation> 之间。"""


TAG_FOR = {
    "expression": "expression_exploration",
    "first": "first_translation",
    "critique": "improved_translation",
    "second": "further_improved_translation",
    "review": "external_review",
    "final": "refined_final_translation",
}


def lean_refine(source, draft, gl, pools, tag_, meta, call, call_story, save):
    """Lean mode: a weakness-targeted audit + one repair pass."""
    text = call(p_audit(source, draft, gl), SYS_REVIEWER, pools["polisher"],
                4000, 0.2, "audit")
    audit = tag(text, "audit") or text
    save("07_audit", audit)
    # only spend the repair call if the auditor actually found something
    verdict = "需要返工" in audit or "【" in audit
    if not verdict:
        meta["audit_clean"] = True
        return draft
    fixed = call(p_repair(source, draft, "审读发现以下问题，请逐条改正后输出完整译稿：" + audit[:2500]),
                 SYS_WRITER, pools["polisher"], 9000, 0.4, "audit_fix")
    refined = tag(fixed, "refined_final_translation") or strip_fence(fixed)
    if looks_like_reasoning(refined):
        return draft
    floor = max(20, int(len(draft) * 0.5))
    if not refined or len(refined) < floor:
        return draft
    save("08_fixed", refined)
    return refined


def _looks_truncated(body: str) -> bool:
    body = body.rstrip()
    if not body:
        return False
    return body[-1] not in "。！？…”’」』）)】》"


# ─────────────────────────────────────────────────────────── steps

def run_analysis(chapter_title: str, source: str, models, tag_: str) -> str:
    text, used = llm.chat(
        [{"role": "system", "content": SYS_WRITER},
         {"role": "user", "content": p_analysis(chapter_title, source)}],
        models=models, max_tokens=6000, temperature=0.6, tag=f"{tag_}:analysis",
    )
    out = tag(text, "analysis") or text
    return out


def translate_chunk(blocks, analysis, outdir, models, tag_, resume=True) -> dict:
    """Run the dadeumi stage sequence on one chunk.

    models: {"writer": [...], "critic": [...], "reviewer": [...], "polisher": [...]}
    Different families write and critique, so the review is genuinely independent.
    """
    os.makedirs(outdir, exist_ok=True)
    final_path = os.path.join(outdir, "final.txt")
    if resume and os.path.exists(final_path) and os.path.getsize(final_path) > 0:
        meta_p = os.path.join(outdir, "meta.json")
        meta = json.load(open(meta_p, encoding="utf-8")) if os.path.exists(meta_p) else {}
        return {"translation": open(final_path, encoding="utf-8").read().rstrip(),
                "cached": True, **meta}

    if isinstance(models, dict) and "writer" in models and isinstance(models["writer"], list):
        pools = {
            "writer": models["writer"],
            "critic": models.get("critic") or models["writer"],
            "reviewer": models.get("reviewer") or models["writer"],
            "polisher": models.get("polisher") or models["writer"],
            "proof": models.get("proof") or models.get("polisher") or models["writer"],
        }
    else:  # legacy flat pools
        pools = {k: models for k in ("writer", "critic", "reviewer", "polisher")}

    source = render_source(blocks)
    gl = render_glossary(relevant(source))
    meta = {"models": [], "stages": {}}

    def save(name, text):
        with open(os.path.join(outdir, name + ".txt"), "w", encoding="utf-8") as f:
            f.write(text)

    def call(prompt, system, pool, max_tokens, temp, name):
        text, used, info = llm.chat(
            [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            models=pool, max_tokens=max_tokens, temperature=temp, tag=f"{tag_}:{name}",
            with_meta=True,
        )
        meta["models"].append(used)
        meta["stages"][name] = used
        return text

    def call_story(prompt, system, pool, max_tokens, temp, name, source):
        """A call whose output must be a complete translation; continues if truncated."""
        text = call(prompt, system, pool, max_tokens, temp, name)
        for k in range(2):
            body = tag(text, TAG_FOR[name]) or (tag(text, "first_translation")
                                                or tag(text, "improved_translation")
                                                or tag(text, "further_improved_translation")
                                                or tag(text, "refined_final_translation"))
            if not body:
                break
            if not _looks_truncated(body):
                break
            more = call(p_continue(source, body), system, pool, max_tokens, temp,
                        f"{name}_cont{k}")
            add = tag(more, "continued_translation") or strip_fence(more)
            if not add or len(add) < 20:
                break
            text = text + chr(10) + f"<{TAG_FOR[name]}>" + body + add + f"</{TAG_FOR[name]}>"
            meta["continued"] = meta.get("continued", 0) + 1
        return text

    try:
        if os.environ.get("DADEUMI_EXPR", "1") == "1":
            try:
                ex = call(p_expression(source, analysis), SYS_WRITER, pools["critic"], 3000, 0.8,
                          "expression")
                save("01_expression", tag(ex, "expression_exploration") or ex)
            except Exception as e:  # noqa: BLE001
                meta.setdefault("skipped", []).append(f"expression:{str(e)[:60]}")

        # Draft with retries: drop whichever model produced an unusable result
        # (reasoning models sometimes burn their whole output budget thinking).
        floor = max(20, int(len(source) * 0.3))
        pool = list(pools["writer"])
        draft = ""
        for attempt in range(4):
            if not pool:
                break
            try:
                t1 = call(p_first(source, analysis, gl), SYS_WRITER, pool, 8000, 0.7, "first")
            except Exception as e:  # noqa: BLE001
                meta.setdefault("first_errors", []).append(str(e)[:80])
                pool = pool[1:]
                continue
            got = tag(t1, "first_translation") or strip_fence(t1)
            if looks_like_reasoning(got):
                meta.setdefault("first_errors", []).append("reasoning leak")
                pool = pool[1:]
                continue
            if len(got) >= floor:
                draft = got
                break
            meta.setdefault("first_errors", []).append(f"too short {len(got)}<{floor}")
            pool = pool[1:]
        if not draft:
            raise llm.LLMError(f"first translation unusable (floor={floor})")
        save("02_first", draft)

        lean = os.environ.get("DADEUMI_LEAN", "0") == "1"
        if lean:
            if os.environ.get("DADEUMI_POLISH", "1") == "1":
                draft = lean_refine(source, draft, gl, pools, tag_, meta, call, call_story, save)
            final = draft

        if not lean:
            try:
                t2 = call_story(p_critique(source, draft, gl), SYS_WRITER, pools["critic"], 9000, 0.65, "critique", source)
                save("03_critique", tag(t2, "critique") or "")
                draft = tag(t2, "improved_translation") or draft
                save("04_improved", draft)
            except Exception as e:  # noqa: BLE001
                meta.setdefault("skipped", []).append(f"critique:{str(e)[:80]}")

        try:
            if lean or os.environ.get("DADEUMI_SECOND", "1") != "1":
                raise RuntimeError("skipped")
            t3 = call_story(p_second(source, draft, gl), SYS_WRITER, pools["polisher"], 9000, 0.6, "second", source)
            save("05_second_critique", tag(t3, "second_critique") or "")
            draft = tag(t3, "further_improved_translation") or draft
            save("06_further", draft)
        except Exception as e:  # noqa: BLE001
            meta.setdefault("skipped", []).append(f"second:{str(e)[:80]}")

        review = ""
        try:
            if lean:
                raise RuntimeError("skipped")
            t4 = call(p_external(source, draft, gl), SYS_REVIEWER, pools["reviewer"], 4000, 0.5, "review")
            review = tag(t4, "external_review") or t4
            save("07_review", review)
        except Exception as e:  # noqa: BLE001
            meta.setdefault("skipped", []).append(f"review:{str(e)[:80]}")

        final = ""
        try:
            if lean:
                raise RuntimeError("skipped")
            t5 = call_story(p_final(source, draft, review, gl), SYS_WRITER, pools["polisher"], 9000, 0.5, "final", source)
            final = tag(t5, "refined_final_translation") or strip_fence(t5)
            if len(final) < 80:
                final = ""
            else:
                save("08_final", final)
        except Exception as e:  # noqa: BLE001
            meta.setdefault("skipped", []).append(f"final:{str(e)[:80]}")
        if not final:  # degrade gracefully to the best draft we have
            final = draft

        # proofread pass: only pay for it when the draft actually has surface defects
        needs_proof = (os.environ.get("DADEUMI_PROOF", "0") == "1") and bool(
            re.search(r"[0-9(（;]|[A-Za-z]{4,}|\*\*", final))
        try:
            if not needs_proof:
                raise RuntimeError("clean")
            tp = call(p_proofread(final, gl), SYS_WRITER, pools.get("proof") or pools["polisher"],
                      9000, 0.25, "proofread")
            pf = tag(tp, "proofread") or ""
            if len(pf) > 80 and len(pf) > 0.7 * len(final):
                final = pf
                save("10_proofread", final)
        except Exception as e:  # noqa: BLE001
            meta.setdefault("skipped", []).append(f"proofread:{str(e)[:80]}")

        final = postprocess.clean(final)
        save("11_clean", final)

        for attempt in range(2):
            problem = structure_problem(blocks, final)
            if not problem:
                break
            tr = call(p_repair(source, final, problem), SYS_WRITER, pools["polisher"], 9000, 0.4,
                      f"repair{attempt}")
            fixed = tag(tr, "refined_final_translation") or strip_fence(tr)
            if len(fixed) > 80:
                final = fixed
                save(f"09_repair{attempt}", final)
        meta["structure_ok"] = not structure_problem(blocks, final)
    except Exception as e:  # noqa: BLE001
        meta["error"] = str(e)[:300]
        json.dump(meta, open(os.path.join(outdir, "meta.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        raise

    with open(final_path, "w", encoding="utf-8") as f:
        f.write(final + chr(10))
    json.dump(meta, open(os.path.join(outdir, "meta.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"translation": final, "cached": False, **meta}


# ─────────────────────────────────────────────────────────── validation

CJK = re.compile(r"[\u4e00-\u9fff]")


def parse_paragraphs(text: str):
    """Return (paras, verse_line_counts) from a translated chunk."""
    text = re.sub(r"<\s*/?\s*verse\s*>", "\x00", text)
    parts = [p.strip() for p in text.split("\x00")]
    paras, verse_counts = [], []
    for i, p in enumerate(parts):
        if i % 2 == 0:
            paras.extend([q.strip() for q in p.split("\n\n") if q.strip()])
        else:
            verse_counts.append(len([l for l in p.split("\n") if l.strip()]))
    return paras, verse_counts


def name_problems(blocks, translation: str) -> list[str]:
    """Deterministic glossary conformance check."""
    src = render_source(blocks)
    gl = relevant(src, limit=200)
    missing = [f"{k}→{v}" for k, v in gl.items()
               if len(v) >= 2 and v not in translation and re.search(r"" + re.escape(k) + r"", src)]
    if not missing:
        return []
    return ["专名未照术语表：" + "、".join(missing[:8]) + "。请改用术语表译法。"]


def structure_problem(blocks, translation: str) -> str:
    src = counts(blocks)
    tr = translation
    if not CJK.search(tr):
        return "译文里没有中文。"
    src_paras = src["paras"]
    paras, verses = parse_paragraphs(tr)
    msgs = []
    # paragraph body lines include verse blocks separately; compare loosely
    if src_paras and len(paras) < src_paras * 0.9:
        msgs.append(f"原文有 {src_paras} 个散文段落，译文只有 {len(paras)} 段，明显有并段或漏段。")
    if src_paras and len(paras) > src_paras * 1.25:
        msgs.append(f"原文有 {src_paras} 个散文段落，译文有 {len(paras)} 段，段落被拆得过碎或多出段落。")
    if len(verses) < len(src["verses"]):
        msgs.append(
            f"原文有 {len(src['verses'])} 处诗行（行数分别为 {src['verses']}），"
            f"译文只保留了 {len(verses)} 处（行数 {verses}）。诗行必须用 <verse> 包裹并保留分行。"
        )
    msgs.extend(name_problems(blocks, tr))
    if re.search(r"[A-Za-z]{4,}", re.sub(r"<[^>]+>", "", tr)) and not re.search(
            r"(Mr\.|Mrs\.|Gandalf|Frodo)", tr):
        eng = re.findall(r"[A-Za-z]{4,}", re.sub(r"<[^>]+>", "", tr))[:8]
        msgs.append(f"译文里残留英文：{', '.join(eng)}。请全部译成中文。")
    return " ".join(msgs)
