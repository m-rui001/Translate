"""Moby-Dick translation workflow: draft -> audit -> repair -> polish.

Stages (each persisted under work_whale/out/<chapter>/c<NN>/):

  00_brief.txt       per-chapter analysis (tone, speakers, hard spots, terms)
  01_expression.txt  free exploration of the hardest sentences
  02_first.txt       first translation (xm:mimo-v2.6-flash by default)
  03_audit.txt       independent audit by another model family
  04_improved.txt    repair against the audit
  05_polish.txt      literary polish (gemini-3.8-flash)
  09_proof.txt       mechanical proofread (only if defects detected)
  final.txt          what actually gets used

Resumable: a chunk with final.txt is skipped. Every stage falls back to the best
draft available, so no chunk is ever left empty by a stage failure.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import llm
import postprocess
from glossary import relevant as rel_gl, render as render_gl
from style import STYLE, WEAKNESS_ALERT

CJK = re.compile(r"[\u4e00-\u9fff]")
PARA_SEP = re.compile(r"\n\s*\n")

# A dead upstream otherwise costs the full 600 s per attempt and the failover loop
# walks the whole pool, so one stalled model can idle a chunk for an hour. Free
# gateways answer in seconds or not at all, so batch runs set WF_TIMEOUT low.
CALL_TIMEOUT = float(os.environ.get("WF_TIMEOUT", "600"))
# chat_pool walks the whole writer pool after a failure, so retries multiply across
# every model: 4 retries over 8 models is 32 dead requests before a chunk gives up.
CALL_RETRIES = int(os.environ.get("WF_RETRIES", "4"))

SYS_WRITER = (
    "你是当代最优秀的中文文学译者之一，长期翻译十九世纪英美散文与诗歌，"
    "汉语文笔老到，也懂得克制。你正在与编辑合作，逐段打磨《白鲸》的新译本。\n\n"
    + STYLE + "\n\n" + WEAKNESS_ALERT
)

SYS_AUDITOR = (
    "你是资深文学编辑与翻译批评家，中英文俱精，读过《白鲸》原文多遍，"
    "也熟悉麦尔维尔的圣经文体与莎士比亚腔。"
    "你的职责是挑错：漏译、增译、误译、腔调不对、长句被拍平、翻译腔、"
    "专名不一致、术语漂移、诗行被并成散文。"
    "你只提具体问题，每条都要指出原文片段与译文片段，不做泛泛的赞美，不必重写全文。"
)

SYS_POLISHER = (
    "你是顶尖的文学译者，正在为《白鲸》做出版前的最后一轮精校。"
    "你的任务是让译文读起来像汉语文学作品，而不是像译文。\n\n"
    + STYLE
)

_TAG_FOR = {
    "first": "first_translation",
    "improved": "improved_translation",
    "polished": "polished",
    "proof": "proofread",
    "continued": "continued_translation",
}

_REASONING_PAT = re.compile(
    r"(?:^|\n)\s*(?:We need|We must|I need|Let's|Let me|Need translate|Need to|Need ensure"
    r"|首先|我们需要|我需要|需要译|需要确保|需要输出|要译|下面|首先我们"
    r"|### (?:Instruction|Response|Thinking)|<source>|<first_translation>|<system>"
    r"|译文如下|译成中文时|要逐段|必须逐段|glossary|术语表要求)", re.I)


def looks_like_reasoning(text: str) -> bool:
    if not text or len(text) < 20:
        return True
    if _REASONING_PAT.search(text[:600]):
        return True
    cjk = len(CJK.findall(text))
    return cjk < 0.25 * max(1, len(text))


def tag(text: str, name: str) -> str:
    m = re.search(rf"<\s*{name}\s*>(.*?)(?:<\s*/\s*{name}\s*>|$)", text, re.S)
    if not m:
        return ""
    body = re.sub(rf"<\s*/?\s*{name}\s*>", "", m.group(1))
    return body.strip()


def strip_fence(text: str) -> str:
    text = re.sub(r"^\s*```[a-zA-Z]*\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"\1", text)
    text = re.sub(r"(?m)^\s*#{1,6}\s*", "", text)
    return text.strip()


# ─────────────────────────────────────────────── source rendering

def render_source(blocks: list[dict]) -> str:
    out = []
    for b in blocks:
        if b["type"] == "verse":
            out.append("<verse>\n" + "\n".join(l.strip() for l in b["lines"]) + "\n</verse>")
        elif b["type"] == "attr":
            out.append("<attr>" + b["text"].strip() + "</attr>")
        else:
            out.append(b["text"].strip())
    return "\n\n".join(out)


def render_extra(blocks: list[dict]) -> str:
    """A precise, mechanical statement of the output shape required."""
    shape, vers, attrs = [], 0, 0
    for b in blocks:
        if b["type"] == "p":
            shape.append("段")
        elif b["type"] == "head":
            shape.append("题")
        elif b["type"] == "attr":
            attrs += 1
            shape.append("署")
        else:
            vers += 1
            shape.append(f"诗{b['lines'].__len__()}")
    n_p = shape.count("段")
    lines = [f"输出必须严格分成 {len(blocks)} 个块，块与块之间空一行，顺序与下面完全一致：",
             " ".join(shape)]
    lines.append(f"即：{n_p} 个散文段落" +
                 (f"、{vers} 个诗/分行块（行数依次为 " +
                  "、".join(str(len(b['lines'])) for b in blocks if b["type"] != "p"
                           and b["type"] not in ("head", "attr")) +
                  "，必须逐行分行，不许并成散文）" if vers else "") +
                 (f"、{attrs} 条引文出处（独立成行）" if attrs else "") + "。")
    lines.append("不要把两个块合成一段，也不要为节奏把一段拆成几段。")
    return "\n".join(lines)


# ─────────────────────────────────────────────── prompts

def p_analysis(title_en, title_zh, source):
    return f"""这是《白鲸》第「{title_zh}」（{title_en}）一章的一段原文。译文将由你与编辑逐步
打磨，先做一次整体分析。全部用中文回答，条目清楚，不要客套。

<source>
{source}
</source>

1. 场景：谁在场、在哪里、在做什么、这一段的语气（冷静叙述／狂怒／讥讽／庄重／戏谑／说教／工艺说明）。
2. 文体：这一段属于本书的哪一路（叙事、莎士比亚式独白、讲道、工艺手册、论辩、歌谣、戏剧对白、
   百科全书式分类）。若是讲道与经文，注明对应圣经篇目。
3. 难点：长句的骨架怎么搭、哪几处同位语堆叠、哪几个比喻是麦尔维尔的硬核比喻、哪几句必须
   保留拗口、哪一处有反讽。
4. 人物声音：文中说话的人各有什么用词与句长特征，一句话概括。
5. 术语与名物：捕鲸、航海、解剖、鲸类的专门说法，凡术语表可能没收的，列出英文与建议译法。
6. 译文要领：给这一段三五条具体建议（例如某处必须短句、某处该保留三段并列）。

把全部内容放在 <analysis> 与 </analysis> 之间。"""


def p_first(source, analysis, gl, extra):
    return f"""{gl}

{WEAKNESS_ALERT}

这是《白鲸》的一段原文，附上一份分析。请把它完整译成中文。

<analysis>
{analysis}
</analysis>

<source>
{source}
</source>

{extra}

- 若原文某段以破折号或转折词硬接下一段（麦尔维尔常这么干），译文也要硬接，不要加过渡句。
- 原文用 <verse> 包住的诗/分行块，译文保留分行，不要加 <verse> 之外的任何标记。
- 不写任何说明、不写标题、不加注释、不加序号。

把完整译文放在 <first_translation> 与 </first_translation> 之间。"""


def p_audit(source, draft, gl, extra):
    return f"""{gl}

下面是《白鲸》的英文原文和一份中文译稿。请只查下列高危问题，逐段核对，
不要重写全文，不要泛泛称赞。

<source>
{source}
</source>

<current_translation>
{draft}
</current_translation>

结构：{extra}

核对项：
1. 漏译：原文有而译文没有的句子、分句、形容词、同位语、举例。麦尔维尔的并列常常很长。
2. 增译：译文有而原文没有的解释、评语、因果、过渡、补充说明。
3. 误译：词义、句法归属、指代关系（他的、它的、他们指谁）、航海与捕鲸操作的具体动作。
4. 拍平长句：原文一个长句被切成几个等长短句，气势丢失的地方。
5. 腔调：亚哈的狂怒、斯塔布的油滑、斯达巴克的克制、梅普尔的经文腔有没有被统一成一种中性白话。
6. 术语：与术语表不一致的专名；同一样东西前后换了说法。
7. 诗行：分行是否被并成散文，行数是否与原诗相同。
8. 数字与年代：是否误用了阿拉伯数字，尺寸单位是否译错。

只列问题，格式：
- 【类型】原文片段 → 译文片段 → 应改为

每条一行，最多二十五条，只挑最要紧的；同一类型的问题合并成一条，不要逐段罗列同类。

最后一行写：可以定稿 / 需要返工。
把内容放在 <audit> 与 </audit> 之间。"""


def p_repair(source, draft, audit, gl, extra):
    return f"""{gl}

编辑对这份译稿提出了下面的问题。请据此修正，输出完整译稿（不是片段）。

<audit>
{audit}
</audit>

<source>
{source}
</source>

<current_translation>
{draft}
</current_translation>

修正要求：
- 只改确有问题的地方；编辑没提且原文对得上的地方，尽量保留现有措辞。
- 结构不变：{extra}
- 不许为了修一处而重写整段，也不许把编辑没提到的内容删掉。
- 不写说明。

把修正后的完整译稿放在 <improved_translation> 与 </improved_translation> 之间。"""


def p_polish(source, current, gl, extra):
    return f"""{gl}

下面是《白鲸》的英文原文和一份已成稿的中文译文。请做**大改精校**：不是小修小补，
而是以文学译者的身份把整段重新锤炼一遍，同时严格保住已有的正确内容。

<source>
{source}
</source>

<current_translation>
{current}
</current_translation>

精校目标（按优先级）：
1. 消灭翻译腔。“进行……的处理”“对于……而言”“使……得以”“作为一个……”这类句型一律改掉；
   “的”字连缀要拆；“被”字句尽量还原为主动；“一个”“一种”这类垫字删掉。
2. 长句绝不拆短：原文一个长句，中文仍是一个长句，逗号与破折号连着走。
   若现有译文已经把长句拆碎，请合回去。
3. 复现麦尔维尔的呼吸：短句要硬，长句要滚，破折号要留住。声调要有起伏，不能平铺。
4. 分腔：亚哈的独白要有莎士比亚式的呼语与顿挫；斯塔布要油滑些；斯达巴克要朴素些；
   讲道要有圣经腔；工艺段落要冷、要准。现有译文若把所有人说成一个人，请分开。
5. 逐段对应：段落数量与顺序不得改变，不漏译不增译。结构：{extra}
6. 术语严格照术语表，全书一致。诗行保持分行与行数。
7. 只改必要处：内容与原文一致的地方尽量保留现有措辞，不追求炫技式重写。

把精校后的完整译文放在 <polished> 与 </polished> 之间，不要写任何说明。"""


def p_expression(source, gl, extra):
    return f"""{gl}

这是《白鲸》里最难的一段。先不要翻译全文，只做**表达探索**：挑出其中最难处理的
五到十处（滚动的长句、堆叠的同位语、圣经引文、奇崛的比喻、方言与水手黑话、
需要保留拗口的句子），每一处给出两到三种不同的中文处理方案，并说明各自的得失。
判断的标准是：哪一种更能在汉语里立得住，又不失麦尔维尔的分量。

<source>
{source}
</source>

把内容放在 <expression> 与 </expression> 之间。"""


def p_proof(text, gl):
    return f"""{gl}

下面是《白鲸》一章中文译稿的一段。请只做机械校对，不做文学改写。

<current_translation>
{text}
</current_translation>

只查这些：错别字、标点误用（中文标点是否齐全、引号是否配对、破折号是否为“——”）、
阿拉伯数字是否残留（应改中文数字）、词语重复、漏字。不改句子风格，不改内容。

把校对后的完整文本放在 <proofread> 与 </proofread> 之间。"""


# ─────────────────────────────────────────────── structure checks

def n_paras(text: str) -> int:
    return len([p for p in re.split(PARA_SEP, text) if p.strip()])


def structure_problem(blocks, translation: str) -> str:
    """Verify the block count of the translation against the source blocks."""
    if not CJK.search(translation):
        return "译文里没有中文。"
    want = len(blocks)
    got = n_paras(translation)
    src_v = [len(b["lines"]) for b in blocks if b["type"] == "verse"]
    msgs = []
    if abs(got - want) > max(1, round(want * 0.12)):
        if got < want:
            msgs.append(f"原文分成 {want} 块，译文只有 {got} 块，有并段或漏段。")
        else:
            msgs.append(f"原文分成 {want} 块，译文有 {got} 块，段落被切得太碎。")
    if src_v:
        need = sum(src_v) - len(src_v) * 0.3
        lines = [l for l in translation.split("\n") if l.strip()]
        if len(lines) < need:
            msgs.append(f"原文有 {sum(src_v)} 行诗/舞台提示，译文仅 {len(lines)} 行，诗行被并成了散文。")
    return " ".join(msgs)


def _looks_truncated(body: str, source: str) -> bool:
    if not body:
        return True
    ratio = len(body) / max(1, len(source))
    if ratio < 0.18:          # Chinese is much shorter than English, but not that short
        return True
    tail = body.rstrip()[-1:]
    return tail not in "。！？…”’）】」』—…、；："


# ─────────────────────────────────────────────── the chunk runner

def translate_chunk(blocks, outdir, pools, tag_, nums=True, resume=True,
                    audit=True, polish=True, analysis_text=""):
    os.makedirs(outdir, exist_ok=True)
    final_path = os.path.join(outdir, "final.txt")
    meta_path = os.path.join(outdir, "meta.json")
    if resume and os.path.exists(final_path) and os.path.getsize(final_path) > 0:
        meta = json.load(open(meta_path, encoding="utf-8")) if os.path.exists(meta_path) else {}
        return {"cached": True, **meta}

    source = render_source(blocks)
    gl = render_gl(rel_gl(source))
    extra = render_extra(blocks)
    # a two-line chapter legitimately produces a very short translation, so every
    # length threshold below is scaled to the source instead of being absolute
    min_ok = max(60, int(len(source) * 0.18))
    meta = {"models": {}, "skipped": [], "notes": []}

    def save(name, text):
        with open(os.path.join(outdir, name + ".txt"), "w", encoding="utf-8") as f:
            f.write(text.rstrip() + "\n")

    def call(prompt, system, pool, max_tokens, temp, name):
        text, used = llm.chat_pool(
            [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            pool, max_tokens=max_tokens, temperature=temp, tag=f"{tag_}:{name}",
            timeout=CALL_TIMEOUT, retries=CALL_RETRIES)
        meta["models"][name] = used
        return text

    # ── 02 first draft, with structural verification and model fallback
    draft, draft_model = "", None
    pool = list(pools["writer"])
    for attempt in range(len(pool) + 1):
        if not pool:
            break
        try:
            t1 = call(p_first(source, analysis_text, gl, extra), SYS_WRITER,
                      pool, 16000, 0.72, "first")
        except Exception as e:  # noqa: BLE001
            meta["skipped"].append(f"first:{str(e)[:100]}")
            pool = pool[1:]
            continue
        got = tag(t1, "first_translation") or strip_fence(t1)
        if looks_like_reasoning(got) and len(got) < min_ok:
            meta["notes"].append("first: reasoning leak")
            pool = pool[1:]
            continue
        prob = structure_problem(blocks, got)
        if len(got) >= min_ok and not prob:
            draft = got
            draft_model = meta["models"].get("first")
            break
        # one structural retry on the same model, then drop it
        try:
            t1 = call(p_first(source, analysis_text, gl, extra) +
                      f"\n\n上一次的输出有这些问题：{prob or '不完整'}。请严格逐段对应重译。",
                      SYS_WRITER, [pool[0]], 16000, 0.6, "first_retry")
            got2 = tag(t1, "first_translation") or strip_fence(t1)
            if len(got2) >= min_ok and (not structure_problem(blocks, got2)
                                        or len(got2) > len(got)):
                draft, draft_model = got2, meta["models"].get("first_retry")
                break
        except Exception as e:  # noqa: BLE001
            meta["skipped"].append(f"first_retry:{str(e)[:80]}")
        if len(got) >= min_ok:
            draft, draft_model = got, meta["models"].get("first")
            meta["notes"].append(f"first kept despite: {prob}")
            break
        pool = pool[1:]

    if not draft:
        raise llm.LLMError(f"{tag_}: no usable first translation")
    save("02_first", draft)

    # ── 01 free exploration (written after the draft so it can be skipped cheaply)
    if os.environ.get("WHALE_EXPR", "0") == "1" and pools.get("explorer"):
        try:
            t0 = call(p_expression(source, gl, extra), SYS_WRITER, pools["explorer"],
                      3000, 0.85, "expression")
            save("01_expression", tag(t0, "expression") or t0)
        except Exception as e:  # noqa: BLE001
            meta["skipped"].append(f"expression:{str(e)[:80]}")

    current = draft

    # ── 03 audit by a different model family
    if audit and pools.get("auditor"):
        try:
            ta = call(p_audit(source, current, gl, extra), SYS_AUDITOR,
                      pools["auditor"], 3000, 0.35, "audit")
            aud = tag(ta, "audit") or ta
            save("03_audit", aud)
            n_bullets = len(re.findall(r"(?m)^\s*[-•*]\s*【", aud))
            meta["audit_bullets"] = n_bullets
            if n_bullets >= 1 and "可以定稿" not in aud.splitlines()[-1]:
                tr = call(p_repair(source, current, aud, gl, extra), SYS_WRITER,
                          pools["polisher"], 16000, 0.5, "repair")
                fixed = tag(tr, "improved_translation") or strip_fence(tr)
                if len(fixed) >= len(current) * 0.7 and not looks_like_reasoning(fixed):
                    current = fixed
                    save("04_improved", current)
                else:
                    meta["notes"].append("repair rejected (length/structure)")
        except Exception as e:  # noqa: BLE001
            meta["skipped"].append(f"audit:{str(e)[:100]}")

    # ── 05 literary polish
    if polish and pools.get("polisher"):
        best = None
        pool = list(pools["polisher"])
        for _ in range(len(pool) + 1):
            if not pool:
                break
            try:
                tp = call(p_polish(source, current, gl, extra), SYS_POLISHER,
                          pool, 16000, 0.42, "polish")
            except Exception as e:  # noqa: BLE001
                meta["skipped"].append(f"polish:{str(e)[:100]}")
                pool = pool[1:]
                continue
            got = tag(tp, "polished") or strip_fence(tp)
            if looks_like_reasoning(got):
                meta["notes"].append("polish: reasoning leak")
                pool = pool[1:]
                continue
            ratio = len(got) / max(1, len(current))
            prob = structure_problem(blocks, got)
            if prob:
                meta["notes"].append(f"polish rejected: {prob}")
                pool = pool[1:]
                continue
            if not (0.75 <= ratio <= 1.35):
                meta["notes"].append(f"polish rejected: ratio {ratio:.2f}")
                pool = pool[1:]
                continue
            best = got
            break
        if best:
            current = best
            save("05_polish", current)

    # ── 09 proofread, only when the text actually looks dirty
    if os.environ.get("WHALE_PROOF", "0") == "1" and pools.get("polisher"):
        if re.search(r"\d|[A-Za-z]{3,}", current):
            try:
                tq = call(p_proof(current, gl), SYS_WRITER, pools["polisher"],
                          16000, 0.2, "proof")
                pf = tag(tq, "proofread") or ""
                if pf and abs(len(pf) - len(current)) / max(1, len(current)) < 0.1:
                    current = pf
                    save("09_proof", current)
            except Exception as e:  # noqa: BLE001
                meta["skipped"].append(f"proof:{str(e)[:80]}")

    final = postprocess.clean(current, numerals=nums)
    save("final", final)
    meta["chars"] = len(final)
    meta["draft_model"] = draft_model
    json.dump(meta, open(meta_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return {"cached": False, **meta}
