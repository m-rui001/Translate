"""Deterministic post-processing for Chinese manuscript hygiene.

Applied to every chunk before it is saved. Cheap, predictable, and it removes
the class of defects a model keeps reintroducing (Arabic numerals, parentheses,
half-width punctuation, stray Latin characters, doubled spaces).
"""
from __future__ import annotations

import re

CN_NUM = "零一二三四五六七八九"
UNITS = ["", "十", "百", "千"]


def num_to_cn(n: int) -> str:
    if n == 0:
        return "零"
    if n < 0:
        return "负" + num_to_cn(-n)
    if n >= 10000:
        high, low = divmod(n, 10000)
        out = num_to_cn(high) + "万"
        if low:
            out += (num_to_cn(low) if low >= 1000 else "零" + num_to_cn(low))
        return out
    digits = []
    s = str(n)
    zero = False
    for i, ch in enumerate(s):
        d = int(ch)
        pos = len(s) - i - 1
        if d == 0:
            zero = True
        else:
            if zero and digits:
                digits.append("零")
            zero = False
            digits.append(CN_NUM[d] + UNITS[pos])
    out = "".join(digits)
    if out.startswith("一十"):
        out = out[1:]
    return out


def _replace_numbers(text: str) -> str:
    # years read digit by digit in Chinese: 1418 -> 一四一八 (kept as 一千四百一十八 is wrong)
    def repl(m):
        raw = m.group(0)
        if "." in raw:  # decimal
            a, b = raw.split(".")
            return num_to_cn(int(a)) + "点" + "".join(CN_NUM[int(d)] for d in b)
        n = int(raw)
        if 1000 <= n <= 2100 and len(raw) == 4 and re.search(
                r"(年|纪元|第三纪|第二纪|第一纪|第四纪)", text[max(0, m.start() - 6):m.end() + 2]):
            return "".join(CN_NUM[int(d)] for d in raw)
        return num_to_cn(n)

    return re.sub(r"(?<![A-Za-z0-9])(\d+\.\d+|\d+)(?![A-Za-z0-9])", repl, text)


def _drop_latin_glosses(text: str) -> str:
    """Remove parenthetical English glosses like （Gandalf）or (sic)."""
    def repl(m):
        inner = m.group(1)
        return "" if re.fullmatch(r"[A-Za-z0-9 .,'\-–—!?;:&/]+", inner.strip()) else m.group(0)
    return re.sub(r"[（(]([^（）()]{1,60})[）)]", repl, text)


def _drop_parentheses(text: str) -> str:
    # full-width and half-width: turn "（……）" into a comma aside or drop it
    def repl(m):
        inner = m.group(1).strip()
        if not inner:
            return ""
        if len(inner) <= 12 and not re.search(r"[。！？；]", inner):
            return "，" + inner + "，"
        return "，" + inner + "。"

    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"[（(]([^（）()]{1,80})[）)]", repl, text)
    text = text.replace("（", "").replace("）", "").replace("(", "").replace(")", "")
    text = re.sub(r"，{2,}", "，", text)
    text = re.sub(r"，。", "。", text)
    text = re.sub(r"。，", "。", text)
    return text


def _punct(text: str) -> str:
    text = text.replace(";", "；").replace("；", "，")  # no semicolons in this register
    text = text.replace(",", "，") if re.search(r"[\u4e00-\u9fff],", text) else text
    text = text.replace("?", "？").replace("!", "！").replace(":", "：")
    text = re.sub(r'(?<=[\u4e00-\u9fff"])\s*"\s*(?=[\u4e00-\u9fff])', '”', text)
    text = text.replace("...", "……").replace("…", "……").replace("…………", "……")
    text = re.sub(r"—{3,}", "——", text)
    text = re.sub(r"-{2,}", "——", text)
    text = re.sub(r"[•·]{2,}", "·", text)
    return text


def _straight(text: str) -> str:
    """Convert paired straight quotes to Chinese curly quotes."""
    out = []
    open_double = True
    open_single = True
    OPEN_CTX = "，。：；！？、—…“‘」』（【“" + chr(10) + chr(9) + " "
    for i, ch in enumerate(text):
        if ch == chr(34):
            prev = text[i - 1] if i else ""
            if open_double and (i == 0 or prev in OPEN_CTX):
                out.append("“")
            else:
                out.append("”")
            open_double = not open_double
        elif ch == chr(39):
            prev = text[i - 1] if i else ""
            if prev.isalnum():
                out.append("’")
            elif open_single:
                out.append("‘")
                open_single = False
            else:
                out.append("’")
                open_single = True
        else:
            out.append(ch)
    return "".join(out)

def _quotes(text: str) -> str:
    # balance curly quotes: whatever opens must close
    out = []
    depth = 0
    for ch in text:
        if ch == "“":
            out.append("“" if depth == 0 else "‘")
            depth += 1
        elif ch == "”":
            depth = max(0, depth - 1)
            out.append("”" if depth == 0 else "’")
        else:
            out.append(ch)
    return "".join(out)


def _latin(text: str) -> str:
    text = re.sub(r"\*\*|__|`|#", "", text)
    # stray single latin letters left by the model (S rune etc. is spelled out)
    text = re.sub(r"(?<=[\u4e00-\u9fff])\s+([A-Za-z]{1,3})\s+(?=[\u4e00-\u9fff])", "", text)
    return text


def _space(text: str) -> str:
    text = text.replace(chr(12288), " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"， +", "，", text)
    text = re.sub(r"(?<=[\u4e00-\u9fff]) +(?=[\u4e00-\u9fff])", "", text)
    text = re.sub(r"(?<=[\u4e00-\u9fff]) +(?=[，。、；：！？”’）】])", "", text)
    text = re.sub(r"(?<=[（【“‘]) +", "", text)
    return text

def clean(text: str, numerals: bool = True) -> str:
    t = text
    t = _latin(t)
    t = _drop_latin_glosses(t)
    if numerals:
        t = _replace_numbers(t)
    t = _drop_parentheses(t)
    t = _punct(t)
    t = _straight(t)
    t = _quotes(t)
    t = _space(t)
    return t.strip()


if __name__ == "__main__":
    sample = "他在袋底洞住了（大概）六十年；111 岁，33 岁。1418 年的事。甘道夫（Gandalf）来了..."
    print(clean(sample))
