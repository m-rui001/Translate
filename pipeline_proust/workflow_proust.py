"""Proust translation workflow: draft, audit, repair — with Zhou Kexi's register."""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, "E:/Translate/pipeline")

import llm
import postprocess
from glossary_proust import relevant as rel_gl, render as render_gl
from style_proust import STYLE, WEAKNESS_ALERT

CJK = re.compile(r"[\u4e00-\u9fff]")

SYS_WRITER = (
    "你是顶尖的法译中文学译者，长期翻译普鲁斯特、纪德、波伏瓦，汉语文笔老到。"
    "你正在为《追忆似水年华》补译缺失卷册，译文将与周克希先生的既有译本并置出版，"
    "必须读起来像出自同一位译者之手。\n\n" + STYLE + "\n\n" + WEAKNESS_ALERT
)

SYS_REVIEWER = (
    "你是资深文学编辑，精通法语与中文，读过普鲁斯特全集多遍，也熟悉周克希先生的中译。"
    "你只挑具体的错：漏译、增译、误译、丢掉的从句层级、被拆散的长句、专名不一致。"
    "不写空泛的赞美，不重写全文。"
)

# reasoning leaks that models emit instead of a translation
_REASONING_PAT = re.compile(
    r"(?:^|\n)\s*(?:We need|We must|I need|Let's|Let me|Need to|Need ensure"
    r"|首先|我们需要|需要译|需要确保|需要输出|要译|下面|首先我们"
    r"|### (?:Instruction|Response|Thinking)|<source>|<first_translation>|<system>"
    r"|译文如下|要逐段|必须逐段|glossary|术语表要求)",
    re.I)


def looks_like_reasoning(text: str) -> bool:
    if not text:
        return True
    if _REASONING_PAT.search(text[:600]):
        return True
    cjk = len(CJK.findall(text))
    return cjk < 0.25 * max(1, len(text))


def render_source(units: list[str]) -> str:
    return "\n\n".join(u.strip() for u in units)


def p_first(source, gl):
    return f"""{gl}

{WEAKNESS_ALERT}

请把下面这段普鲁斯特的法语原文完整译成中文。逐段对应，一段不漏，一段不并。
务必保留原文的长句结构与从句层次，不要拆短句。

<source>
{source}
</source>

把完整译文放在 <first_translation> 与 </first_translation> 之间，不要写任何说明。"""


def p_audit(source, draft, gl):
    return f"""{gl}

下面是法语原文和一份中文译稿。请只查这五类高危问题，不要重写全文。

<source>
{source}
</source>

<current_translation>
{draft}
</current_translation>

逐段核对：
1. 丢从句：原文的 parce que / bien que / si / quoique 等嵌套关系，译文是否拍平成并列了？
2. 丢插入语：原文用逗号夹住的插入成分是否被整句跳过或浓缩？
3. 漏译：原文有而译文没有的句子、分句、形容词、动作次序。
4. 增译：译文有而原文没有的解释、评价。
5. 长句被拆：原文一个长句、译文变成几个短句的地方。
6. 专名：与术语表一致？头衔 de → 德· 是否保留？

只列问题，格式：
- 【类型】原文片段 → 译文片段 → 应改为

最后一行给出判断：可以定稿 / 需要返工。

把内容放在 <audit> 与 </audit> 之间。"""


def p_repair(source, draft, problem):
    return f"""{problem}

请修正后输出完整译稿，保留原段落结构。

<source>
{source}
</source>

<current_translation>
{draft}
</current_translation>

把修正后的完整译稿放在 <refined_final_translation> 与 </refined_final_translation> 之间。"""


SYS_POLISHER = (
    "你是顶尖的法译中文学译者，正在为《追忆似水年华》做出版前的最后一道精校。"
    "译文将与周克希先生的既有译本并置出版，必须读起来像出自同一位译者之手。\n\n"
    + STYLE + "\n\n" + WEAKNESS_ALERT
)


def p_polish(source, current, gl):
    return f"""{gl}

下面是法语原文和一份已成稿的中文译文。请做**大改精校**：不是小修小补，
而是以文学译者的身份把整段重新锤炼一遍，同时严格保住已有的正确内容。

<source>
{source}
</source>

<current_translation>
{current}
</current_translation>

精校目标（按优先级）：
1. 消灭翻译腔："被""进行""对于""使得""作为一个……""这是……的"式句型，
   "总是接受自己被人偏爱胜过他的对手"这类欧化搭配，改成周克希式的自然书面语。
2. 长句绝不拆短：原文一个长句，中文仍是一个长句，逗号连着逗号。
   若现有译文已经把长句拆碎，请合回去。
3. 语气贴近普鲁斯特：自省、温和、带一点耽溺；讽刺要留住锋芒。
4. 逐段对应：段落数量与顺序不得改变，不漏译不增译。
5. 专名严格照术语表；头衔 de → 德· 不得丢失。
6. 只改必要处：内容与原文一致的地方尽量保留现有措辞，不追求炫技式重写。

把精校后的完整译文放在 <polished> 与 </polished> 之间，不要写任何说明。"""


def polish_chunk(units, outdir, pools, tag_, resume=True):
    """Second-pass 大改精校 over an existing final.txt. Returns status string."""
    final_path = os.path.join(outdir, "final.txt")
    pol_path = os.path.join(outdir, "polish.txt")
    done_path = os.path.join(outdir, "polish_done.json")
    if resume and os.path.exists(done_path) and os.path.exists(pol_path):
        return "cached"
    if not os.path.exists(final_path) or os.path.getsize(final_path) == 0:
        return "missing"

    source = render_source(units)
    current = open(final_path, encoding="utf-8").read().strip()
    gl = render_gl(rel_gl(source))
    src_paras = len([p for p in source.split("\n\n") if p.strip()])
    cur_paras = len([p for p in current.split("\n\n") if p.strip()])
    meta = {"models": [], "errors": []}

    pool = list(pools["polisher"])
    best = None
    for _ in range(3):
        if not pool:
            break
        try:
            t, used, _ = llm.chat(
                [{"role": "system", "content": SYS_POLISHER},
                 {"role": "user", "content": p_polish(source, current, gl)}],
                models=pool, max_tokens=12000, temperature=0.35,
                tag=f"{tag_}:polish", with_meta=True, timeout=360)
        except Exception as e:  # noqa: BLE001
            meta["errors"].append(str(e)[:80])
            pool = pool[1:]
            continue
        meta["models"].append(used)
        m = re.search(r"<\s*polished\s*>(.*?)(?:<\s*/\s*polished\s*>|$)", t, re.S)
        got = (m.group(1) if m else t).strip()
        if looks_like_reasoning(got) or not CJK.search(got):
            meta["errors"].append("reasoning leak")
            pool = pool[1:]
            continue
        n_paras = len([p for p in got.split("\n\n") if p.strip()])
        ratio = len(got) / max(1, len(current))
        if n_paras < src_paras * 0.85 or n_paras > cur_paras * 1.3:
            meta["errors"].append(f"paras {n_paras} vs {cur_paras}")
            pool = pool[1:]
            continue
        if not (0.72 <= ratio <= 1.32):
            meta["errors"].append(f"ratio {ratio:.2f}")
            pool = pool[1:]
            continue
        best = got
        break

    if best:
        best = postprocess.clean(best)
        if not os.path.exists(os.path.join(outdir, "final_pre_polish.txt")):
            import shutil
            shutil.copyfile(final_path, os.path.join(outdir, "final_pre_polish.txt"))
        open(pol_path, "w", encoding="utf-8").write(best + "\n")
        open(final_path, "w", encoding="utf-8").write(best + "\n")
        json.dump(meta, open(done_path, "w", encoding="utf-8"), ensure_ascii=False)
        return "polished"
    json.dump(meta, open(done_path, "w", encoding="utf-8"), ensure_ascii=False)
    return "kept"


def structure_problem(units, translation: str) -> str:
    src_paras = len(units)
    paras = [p.strip() for p in translation.split("\n\n") if p.strip()]
    if not CJK.search(translation):
        return "译文里没有中文。"
    msgs = []
    if len(paras) < src_paras * 0.85:
        msgs.append(f"原文 {src_paras} 段，译文只有 {len(paras)} 段，有并段或漏段。")
    if len(paras) > src_paras * 1.3:
        msgs.append(f"原文 {src_paras} 段，译文有 {len(paras)} 段，段落被拆得过碎。")
    return " ".join(msgs)


def translate_chunk(units, outdir, pools, tag_, resume=True, audit=True):
    os.makedirs(outdir, exist_ok=True)
    final_path = os.path.join(outdir, "final.txt")
    if resume and os.path.exists(final_path) and os.path.getsize(final_path) > 0:
        return {"translation": open(final_path, encoding="utf-8").read().rstrip("\n"),
                "cached": True}

    source = render_source(units)
    gl = render_gl(rel_gl(source))
    floor = max(30, int(len(source) * 0.22))
    meta = {"models": []}

    def call(prompt, system, pool, max_tokens, temp, name):
        text, used, _ = llm.chat(
            [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            models=pool, max_tokens=max_tokens, temperature=temp,
            tag=f"{tag_}:{name}", with_meta=True, timeout=300)
        meta["models"].append(used)
        return text

    def tag_extract(t, name):
        m = re.search(rf"<\s*{name}\s*>(.*?)(?:<\s*/\s*{name}\s*>|$)", t, re.S)
        return (m.group(1) if m else t).strip()

    draft = ""
    pool = list(pools["writer"])
    for _ in range(4):
        if not pool:
            break
        try:
            t = call(p_first(source, gl), SYS_WRITER, pool, 12000, 0.75, "first")
        except Exception as e:  # noqa: BLE001
            meta.setdefault("first_errors", []).append(str(e)[:80])
            pool = pool[1:]
            continue
        got = tag_extract(t, "first_translation")
        if looks_like_reasoning(got):
            meta.setdefault("first_errors", []).append("reasoning leak")
            pool = pool[1:]
            continue
        if len(got) >= floor:
            draft = got
            break
        meta.setdefault("first_errors", []).append(f"short {len(got)}<{floor}")
        pool = pool[1:]
    if not draft:
        raise RuntimeError(f"draft unusable (floor={floor})")

    with open(os.path.join(outdir, "draft.txt"), "w", encoding="utf-8") as f:
        f.write(draft)

    final = draft
    if audit:
        try:
            t = call(p_audit(source, draft, gl), SYS_REVIEWER, pools["reviewer"],
                     4000, 0.25, "audit")
            audit_txt = tag_extract(t, "audit")
            with open(os.path.join(outdir, "audit.txt"), "w", encoding="utf-8") as f:
                f.write(audit_txt)
            if "需要返工" in audit_txt or "【" in audit_txt:
                t2 = call(p_repair(source, draft, "审读发现以下问题，请逐条改正：" + audit_txt[:2500]),
                          SYS_WRITER, pools["polisher"], 12000, 0.4, "repair")
                fixed = tag_extract(t2, "refined_final_translation")
                if (fixed and not looks_like_reasoning(fixed)
                        and len(fixed) >= floor * 0.6):
                    final = fixed
        except Exception as e:  # noqa: BLE001
            meta.setdefault("skipped", []).append(f"audit:{str(e)[:80]}")

    final = postprocess.clean(final)
    for _ in range(2):
        prob = structure_problem(units, final)
        if not prob:
            break
        try:
            t3 = call(p_repair(source, final, prob), SYS_WRITER, pools["polisher"],
                      12000, 0.3, "struct")
            fixed = tag_extract(t3, "refined_final_translation")
            if fixed and not looks_like_reasoning(fixed) and len(fixed) >= floor * 0.6:
                final = postprocess.clean(fixed)
        except Exception:
            break

    with open(final_path, "w", encoding="utf-8") as f:
        f.write(final + "\n")
    json.dump(meta, open(os.path.join(outdir, "meta.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    return {"translation": final, "cached": False, **meta}
