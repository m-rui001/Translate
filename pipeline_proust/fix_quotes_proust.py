"""Model-assisted quote repair for the Proust supplement.

Deterministic rules cannot tell a dropped opening quote from legitimate
cross-paragraph speech, so the model looks at the chunk in context and fixes
punctuation only. The result is accepted only if it strictly improves balance.
"""
from __future__ import annotations

import glob
import io
import os
import re
import sys

sys.path.insert(0, "E:/Translate/pipeline")

import llm

OUT = "E:/Translate/work_proust/out"


def errors(text: str) -> int:
    text = re.sub(r"\n\s*\n+", "\n", text)
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    pending = 0
    errs = 0
    for p in paras:
        net = p.count("“") - p.count("”")
        sng = p.count("‘") - p.count("’")
        if pending > 0:
            if p.startswith("“"):
                net -= 1
            else:
                errs += 1
            pending = 0
        if net > 0:
            pending = net
        elif net < 0:
            errs += abs(net)
        errs += abs(sng) if sng < 0 else 0
    return errs


PROMPT = """下面是一段中文译稿，中文引号有问题：有的句子该用开引号“却写成了”（方向反了），
有的开引号没有闭合，有的闭合引号没有开引号。

<text>
{text}
</text>

请**只修引号**：
1. 直接引语的外层用“ ”，被引语里再引用的用‘ ’。
2. 每个“都必须配对一个”。句末句读（。？！）在闭合引号里面。
3. 一段话若在对话中间换段，前段末尾可留开引号，但下段必须以同样的开引号起头。
4. 单引号‘ ’不得用作最外层直接引语。

**绝对不要改动任何一个汉字、词序、段落划分，不要增删内容。**只动引号及其紧邻的句读。

把修好的完整文本放在 <fixed> 与 </fixed> 之间，不要写任何说明。"""


def fix_chunk(path: str, models) -> bool:
    body = io.open(path, encoding="utf-8").read().replace("\r\n", "\n")
    before = errors(body)
    if before == 0:
        return False
    try:
        out, _ = llm.chat([{"role": "user", "content": PROMPT.format(text=body[:8000])}],
                          models=models, max_tokens=10000, temperature=0.1,
                          tag="pquotefix", timeout=280)
    except Exception as e:  # noqa: BLE001
        print(f"    call failed: {str(e)[:60]}")
        return False
    m = re.search(r"<fixed>(.*?)</fixed>", out, re.S)
    fixed = (m.group(1) if m else out).strip()
    if not fixed or len(fixed) < len(body) * 0.7:
        return False
    if "“" not in fixed:
        return False
    after = errors(fixed)
    if after >= before:
        return False
    io.open(path, "w", encoding="utf-8").write(fixed + "\n")
    print(f"    {before} -> {after}")
    return True


def demote_corner(text: str) -> str:
    """「」 -> “ ” / ‘ ’ by curly-quote nesting depth. Deterministic."""
    out, depth = [], 0
    for ch in text:
        if ch == "「":
            out.append("‘" if depth >= 1 else "“")
            depth += 1
        elif ch == "」":
            out.append("’" if depth > 1 else "”")
            depth = max(0, depth - 1)
        elif ch == "“":
            depth += 1
            out.append(ch)
        elif ch == "”":
            depth = max(0, depth - 1)
            out.append(ch)
        else:
            out.append(ch)
    return "".join(out)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    for f in glob.glob(os.path.join(OUT, "*", "chunk*", "final.txt")):
        t = io.open(f, encoding="utf-8").read()
        if "「" in t:
            io.open(f, "w", encoding="utf-8").write(demote_corner(t))
            print(f"corner quotes demoted: {f}")
    targets = []
    for f in sorted(glob.glob(os.path.join(OUT, "*", "chunk*", "final.txt"))):
        if errors(io.open(f, encoding="utf-8").read()) > 0:
            targets.append(f)
    print(f"{len(targets)} chunks with quote problems")
    models = ["ox:claude-opus-5", "ox:gpt-6.1-sol", "ox:gemini-3.8-flash"]
    fixed = 0
    for i, f in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {f[len(OUT) + 1:]}")
        if fix_chunk(f, models):
            fixed += 1
    print(f"fixed {fixed}/{len(targets)}")


if __name__ == "__main__":
    main()
