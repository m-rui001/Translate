"""Deterministic mechanical cleanup for the Proust supplement.

Handles the six defect classes that need no literary judgement:
  1. quote direction: emphasis-quotes written ”…” instead of “...”
  2. missing opening quote at paragraph start (”foo” / ”foo)
  3. corner quotes 「」 -> “ ” (nesting-aware)
  4. doubled punctuation 。。 ，， ？。 etc.
  5. stray spaces / fullwidth-halfwidth punctuation drift
  6. name variants (delegated to NAMES table below)

Everything is idempotent and reports before/after counts so a human can audit.
Literary rewriting is NOT done here — that is the model pass.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys

# ---------------------------------------------------------------- name canon
# variant -> canonical. Longest keys must win, so we sort by length at apply time.
NAMES: dict[str, str] = {
    # 人物
    "夏吕斯": "夏尔吕",
    "夏吕斯先生": "德·夏尔吕先生",
    "拉斯佩利埃": "拉斯普利埃",
    "拉斯普里埃": "拉斯普利埃",
    "费泰尔纳": "费泰尔讷",
    "费代尔纳": "费泰尔讷",
    "费特尔纳": "费泰尔讷",
    "费泰纳": "费泰尔讷",
    "费代尔纳夫人": "费泰尔讷夫人",
    "费特尔纳夫人": "费泰尔讷夫人",
    "因卡维尔": "安卡维尔",
    "印卡维尔": "安卡维尔",
    "当西耶尔": "当西埃尔",
    "维尔帕里齐斯": "维尔帕里西斯",
    "圣皮埃尔代伊夫": "圣皮埃尔德伊夫",
    "马尔桑特": "马桑特",
    "玛桑特": "马桑特",
    "圣埃韦尔特": "圣厄韦尔特",
    "福瓦": "富瓦",
    "阿尔帕荣": "阿尔帕容",
    "阿尔帕戎": "阿尔帕容",
    "达尔帕容": "阿尔帕容",
    "埃波切维尔": "埃波什维尔",
    "阿让库尔": "阿尔让库尔",
    "阿尔让古尔": "阿尔让库尔",
    "博韦": "博韦",
    # 地名/宅邸
    "维尔邦": "维尔邦",
}

# names that must never be touched (they contain a variant as substring)
NAME_GUARD = ["维尔邦"]


# ------------------------------------------------------------ quote helpers
def fix_emphasis_quotes(text: str) -> tuple[str, int]:
    """Turn ”word” (both sides closing) into “word”.

    A closing quote used as an opening one is unambiguous only when the pair is
    balanced inside a short span and the left one sits in a position where a
    quote may open: after punctuation, whitespace, or line start.
    """
    # left ” is really an opener when a twin ” follows within a short span and
    # that span contains no “. Chinese has no bare ” usage, so this is safe.
    pat = re.compile(r'”([^“”\n]{1,40})”')
    n = 0

    def rep(m):
        nonlocal n
        n += 1
        return "“" + m.group(1) + "”"

    prev = None
    while prev != text:
        prev = text
        text = pat.sub(rep, text)
    return text, n


def fix_paragraph_open(text: str) -> tuple[str, int]:
    """A paragraph (or line) starting with ” almost always lost its opener."""
    n = 0
    lines = text.split("\n")
    out = []
    for ln in lines:
        s = ln.lstrip()
        if s.startswith("”"):
            # a line starting with a closing quote lost its opener
            idx = len(ln) - len(s)
            ln = ln[:idx] + "“" + s[1:]
            n += 1
        out.append(ln)
    return "\n".join(out), n


def demote_corner(text: str) -> tuple[str, int]:
    """「」 -> “ ” / ‘ ’ by curly-quote nesting depth."""
    out, depth, n = [], 0, 0
    for ch in text:
        if ch == "「":
            out.append("‘" if depth >= 1 else "“")
            depth += 1
            n += 1
        elif ch == "」":
            out.append("’" if depth > 1 else "”")
            depth = max(0, depth - 1)
            n += 1
        elif ch == "“":
            depth += 1
            out.append(ch)
        elif ch == "”":
            depth = max(0, depth - 1)
            out.append(ch)
        else:
            out.append(ch)
    return "".join(out), n


def fix_reversed_close(text: str) -> tuple[str, int]:
    """Left-quote used where a right-quote belongs: X“。 / X“、 / X“” etc."""
    n = 0
    # “ followed by terminal/clause punctuation always closes, never opens
    text, k = re.subn(r'“(?=[。，、；：！？])', "”", text)
    n += k
    # ““ at a juncture: the first one closed the previous speech
    text, k = re.subn(r'““', '”“', text)
    n += k
    # ””“ / “““ collapses first, then the two-char junctures
    text, k = re.subn(r'”{2,}“', '”“', text)
    n += k
    # ”” and “” are both artifacts of a speech juncture: close-then-open.
    # Chinese has no legitimate empty quote pair, so this is a safe rewrite.
    text, k = re.subn(r'””', '”“', text)
    n += k
    text, k = re.subn(r'“”', '”“', text)
    n += k
    return text, n


def fix_dangling_insert(text: str) -> tuple[str, int]:
    """A parenthetical that ends in a comma before its head noun.

    "……兼司机，他是上尉的侄子，的帮助……" — the second comma strands the
    head noun "帮助" with nothing to attach to. Dragging it into the
    parenthetical's tail is wrong too ("侄子的帮助" changes the sense); the only
    honest deterministic repair is to demote the parenthetical to dashes, which
    keeps word order and makes the head noun the clear continuation. Deeper
    reordering is a model job and is flagged by probe() as a priority defect.
    """
    pat = re.compile(r'，(?P<ins>[^，。；！？“”\n]{3,40})，的(?P<head>[\u4e00-\u9fff]{1,6})')
    n = 0

    def rep(m):
        nonlocal n
        n += 1
        s = text.rfind('。', 0, m.start())
        e = text.find('。', m.end())
        sent = text[s + 1:e + 1]
        if '——' in sent:
            # already inside a dash-nested clause: adding another pair would
            # nest dashes, so make the minimal cut instead
            return '，' + m.group('ins') + '的' + m.group('head')
        return "——" + m.group('ins') + "——的" + m.group('head')

    text = pat.sub(rep, text)
    return text, n


def fix_doubled_punct(text: str) -> tuple[str, int]:
    n = 0
    rules = [
        (r"。{2,}", "。"),
        (r"，{2,}", "，"),
        (r"、{2,}", "、"),
        (r"；{2,}", "；"),
        (r"：{2,}", "："),
        (r"！{3,}", "！"),
        (r"？{3,}", "？"),
        (r"。，", "。"),
        (r"，。", "。"),
        (r"？！{2,}", "？！"),
        (r"。”。", "。”"),
        (r"。。”", "。”"),
    ]
    for pat, rep in rules:
        text, k = re.subn(pat, rep, text)
        n += k
    # dashes: 3+ em dashes -> 2
    text, k = re.subn(r"—{3,}", "——", text)
    n += k
    return text, n


def fix_spaces(text: str) -> tuple[str, int]:
    n = 0
    text, k = re.subn(r"[ \t]+", " ", text)
    n += k
    text = re.sub(r" *\n *", "\n", text)
    # no space between CJK and CJK
    text, k = re.subn(r"(?<=[\u4e00-\u9fff]) (?=[\u4e00-\u9fff])", "", text)
    n += k
    # halfwidth punctuation next to CJK
    trans = str.maketrans({",": "，", ".": "。", ";": "；", ":": "：",
                           "?": "？", "!": "！"})
    lines = []
    for ln in text.split("\n"):
        if re.search(r"[\u4e00-\u9fff]", ln) and not re.search(r"[A-Za-z]{3,}", ln):
            k = sum(1 for c in ln if c in ",.;:?!")
            ln = ln.translate(trans)
            n += k
        lines.append(ln)
    return "\n".join(lines), n


def fix_names(text: str) -> tuple[str, int]:
    n = 0
    keys = sorted(NAMES, key=len, reverse=True)
    for k in keys:
        canon = NAMES[k]
        if k == canon:
            continue
        # guard: skip inside a longer protected name
        parts = text.split(k)
        if len(parts) == 1:
            continue
        rebuilt = []
        for i, p in enumerate(parts):
            rebuilt.append(p)
            if i < len(parts) - 1:
                rebuilt.append(canon)
                n += 1
        text = "".join(rebuilt)
    # 音译名被截断或串字（录入/OCR 残留）
    for bad, good in (
        ("在费泰尔讥称", "在费泰尔讷称为"),
        ("费泰尔内", "费泰尔讷"),
        ("来费泰尔拜访", "来费泰尔讷拜访"),
        ("玛尔桑特", "马桑特"),
    ):
        if bad in text:
            n += text.count(bad)
            text = text.replace(bad, good)
    # d'Argencourt：两种写法摇摆，统一为周克希译本的“达尔让库尔”
    # 只在前面没有“德”或“达”时改，避免改出“德·达尔让库尔”
    text, k = re.subn(r"(?<![德达])阿尔让库尔", "达尔让库尔", text)
    n += k
    # Racine 的 Phèdre 出现两种译名
    for bad in ("《淮德拉》", "《菲德尔》"):
        if bad in text:
            n += text.count(bad)
            text = text.replace(bad, "《费德尔》")
    # 无书名号的裸人物名也要统一（周围有“希波吕忒”等别的角色，不能泛改）
    for bad in ("淮德拉", "菲德尔"):
        if bad in text:
            n += text.count(bad)
            text = text.replace(bad, "费德尔")
    if "弗朗索瓦丝·勒尚皮" in text:
        n += text.count("弗朗索瓦丝·勒尚皮")
        text = text.replace("弗朗索瓦丝·勒尚皮", "弗朗索瓦丝·勒·尚皮")
    return text, n


# ------------------------------------------------------------------- driver
STEPS = [
    ("corner", demote_corner),
    ("revclose", fix_reversed_close),
    ("dangling", fix_dangling_insert),
    ("punct", fix_doubled_punct),
    ("emphq", fix_emphasis_quotes),
    ("paraopen", fix_paragraph_open),
    ("names", fix_names),
    ("spaces", fix_spaces),
]


def clean_text(text: str, verbose: bool = True) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    for name, fn in STEPS:
        text, n = fn(text)
        if verbose and n:
            print(f"    {name}: {n}")
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", default="E:/Translate/work_proust/book/追忆似水年华（补译卷）.md")
    ap.add_argument("--outp", default="E:/Translate/work_proust/book/clean_v1.md")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    t = io.open(a.inp, encoding="utf-8").read()
    print(f"in  {len(t)} chars")
    out = clean_text(t)
    io.open(a.outp, "w", encoding="utf-8").write(out)
    print(f"out {len(out)} chars -> {a.outp}")


if __name__ == "__main__":
    main()
