"""Deterministic post-processing for the Chinese Moby-Dick manuscript.

Applied to every chunk. Removes the class of defects a model keeps reintroducing
(arabic numerals, half-width punctuation, doubled spaces, straight quotes,
markdown leakage) while preserving the ⟦i⟧…⟦/i⟧ emphasis markers and verse line
breaks.
"""
from __future__ import annotations

import re

CN_NUM = "零一二三四五六七八九"
UNITS = ["", "十", "百", "千"]
NL = chr(10)
SEP = re.compile(r"\n\s*\n")


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
    digits, zero = [], False
    s = str(n)
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
    def repl(m):
        raw = m.group(0).replace(",", "")
        if "." in raw:
            a, b = raw.split(".", 1)
            return num_to_cn(int(a)) + "点" + "".join(CN_NUM[int(d)] for d in b)
        n = int(raw)
        tail = text[m.end():m.end() + 2]
        if len(raw) == 4 and 1000 <= n <= 2100 and tail.startswith("年"):
            return "".join(CN_NUM[int(d)] for d in raw)
        return num_to_cn(n)

    return re.sub(r"(?<![A-Za-z0-9])(\d[\d,]*(?:\.\d+)?)(?![A-Za-z0-9])", repl, text)


def _drop_latin_glosses(text: str) -> str:
    """Remove parenthetical English glosses like （Gandalf） or (sic)."""
    def repl(m):
        inner = m.group(1)
        if re.fullmatch(r"[A-Za-z0-9 .,'\-–—!?;:&/]+", inner.strip()):
            return ""
        return m.group(0)
    return re.sub(r"[（(]([^（）()]{1,60})[）)]", repl, text)


def _punct(text: str) -> str:
    text = text.replace("?", "？").replace("!", "！")
    text = re.sub(r"(?<=[\u4e00-\u9fff”’]),(?=[\u4e00-\u9fff“‘])", "，", text)
    text = re.sub(r"(?<=[\u4e00-\u9fff”’]);", "；", text)
    text = re.sub(r"(?<=[\u4e00-\u9fff”’]):(?=[\u4e00-\u9fff“‘])", "：", text)
    text = re.sub(r"\.{3,}", "……", text)
    text = re.sub(r"…{1,}", "……", text)
    text = re.sub(r"……+", "……", text)
    text = re.sub(r"—{3,}", "——", text)
    text = re.sub(r"(?<!-)-{2,}(?!-)", "——", text)
    text = re.sub(r"[•]{2,}", "·", text)
    # editorial asterisks: a run of them marks an elision in the quoted source,
    # a lone one is a note call that this edition does not carry
    text = re.sub(r"(?:\*\s*){2,}", "……", text)
    text = text.replace("*", "")
    text = re.sub(r"\((?=[\u4e00-\u9fff])", "（", text)
    text = re.sub(r"(?<=[\u4e00-\u9fff])\)", "）", text)
    return text


def _straight(text: str) -> str:
    out = []
    open_double, open_single = True, True
    OPEN_CTX = "，。：；！？、—…“‘」』（【“ " + NL
    for i, ch in enumerate(text):
        if ch == '"':
            prev = text[i - 1] if i else ""
            if open_double and (i == 0 or prev in OPEN_CTX):
                out.append("“")
            else:
                out.append("”")
            open_double = not open_double
        elif ch == "'":
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


_ITAL = "⟦i⟧[^⟦]+⟦/i⟧"
ATTR_RE = re.compile(r"^(?:" + _ITAL + r"[。.．]?\s*)+$")
ATTR_LINE_RE = re.compile(r"^\s*(?:" + _ITAL + r"[。.．]?\s*)+$")
OPEN = "“"
CLOSE = "”"
S_OPEN = "‘"
S_CLOSE = "’"
ANY = OPEN + CLOSE + S_OPEN + S_CLOSE


def _bare(p: str) -> str:
    t = p.strip()
    t = re.sub("^[" + ANY + "]+", "", t)
    t = re.sub("[" + ANY + "]+$", "", t)
    return t


def is_attr_para(p: str) -> bool:
    """A paragraph that is nothing but an italic source attribution."""
    t = p.strip()
    if NL in t:
        return False
    return bool(ATTR_RE.match(t)) or bool(ATTR_RE.match(_bare(t)))


def _is_attr_line(line: str) -> bool:
    return bool(ATTR_LINE_RE.match(line))


def _strip_boundary_marks(line: str) -> str:
    t = line.strip()
    t = re.sub("^[" + ANY + "]+", "", t)
    t = re.sub("[" + ANY + "]+$", "", t)
    return t


def _one_pair(lines: list[str], was_quoted: bool) -> list[str]:
    """Make a run of lines into a single quotation, if it was quoted at all."""
    out = [_strip_boundary_marks(l) for l in lines]
    if not was_quoted:
        return out
    for i, l in enumerate(out):
        if l:
            out[i] = OPEN + l
            break
    for i in range(len(out) - 1, -1, -1):
        if out[i]:
            out[i] = out[i] + CLOSE
            break
    return out


def _norm_block(body: str) -> str:
    """A multi-line block: either one stanzated poem or an anthology of citations."""
    lines = body.split(NL)
    groups, cur = [], []
    for l in lines:
        if _is_attr_line(l):
            groups.append(("attr", l.strip()))
        else:
            cur.append(l)
    # split the non-attribute runs on attribution lines
    blocks, buf = [], []
    for l in lines:
        if _is_attr_line(l):
            if buf:
                blocks.append(buf)
                buf = []
            blocks.append([l])
        else:
            buf.append(l)
    if buf:
        blocks.append(buf)

    if not any(_is_attr_line(l) for l in lines):
        # one poem: the whole block is a single quotation
        was = any(l.strip() and l.strip()[0] in ANY for l in lines) or \
              any(l.strip() and l.strip()[-1] in ANY for l in lines)
        return NL.join(_one_pair(lines, was))

    # an anthology: every citation keeps its own pair
    out = []
    for blk in blocks:
        if len(blk) == 1 and _is_attr_line(blk[0]):
            out.append(blk[0].strip())
            continue
        was = any(l.strip() and l.strip()[0] in ANY for l in blk) or \
              any(l.strip() and l.strip()[-1] in ANY for l in blk)
        out += _one_pair(blk, was)
    return NL.join(out)


def _remap_nesting(text: str) -> str:
    """Outermost “…”, anything inside it ‘…’. Lone ’ closes the outer level."""
    buf, depth = [], 0
    for ch in text:
        if ch == OPEN:
            buf.append(OPEN if depth == 0 else S_OPEN)
            depth += 1
        elif ch == CLOSE:
            depth = max(0, depth - 1)
            buf.append(CLOSE if depth == 0 else S_CLOSE)
        elif ch == S_OPEN:
            depth = max(depth, 1)
            buf.append(S_OPEN)
        elif ch == S_CLOSE:
            if depth > 0:
                depth -= 1
                buf.append(S_CLOSE)
            else:
                buf.append(CLOSE)
        else:
            buf.append(ch)
    return "".join(buf)


def _norm_prose(body: str) -> str:
    t = body.strip()
    if t.startswith(S_OPEN) and OPEN not in t:
        t = t.replace(S_OPEN, OPEN).replace(S_CLOSE, CLOSE)
    return _remap_nesting(t)


def fix_quotes(text: str) -> str:
    paras = SEP.split(text)
    out, depth = [], 0

    for i, para in enumerate(paras):
        body = para.strip()
        if not body:
            continue
        if is_attr_para(body):
            # the citation above owns the marks; an attribution owns none
            out.append(_bare(body))
            continue

        body = _norm_block(body) if NL in body else _norm_prose(body)

        if depth > 0 and body.startswith(OPEN):
            tail = body[1:]          # this OPEN only reopens the running quote
            body = OPEN + tail
        elif depth > 0:
            tail = body
            body = OPEN + body
        else:
            tail = body
        d = tail.count(OPEN) - tail.count(CLOSE)
        depth = max(0, depth + d)

        nxt = paras[i + 1] if i + 1 < len(paras) else ""
        if depth > 0 and is_attr_para(nxt):
            body = body + CLOSE * depth
            depth = 0
        out.append(body)

    if depth > 0 and out:
        out[-1] = out[-1] + CLOSE * depth
    return (NL + NL).join(out)


def _fix_markers(text: str) -> str:
    """Repair the emphasis markers a model mangles.

    Observed faults: a closer that lost its slash, <i>…</i>, [[i]]…[[/i]], stray
    spacing inside the brackets. The marker carries meaning — it is how this
    edition shows a foreign phrase quoted inside Chinese prose — so it has to
    reach the EPUB stage intact and balanced.
    """
    # a closer whose left half was mangled: ⟦i⟧X⟧/i⟧ means ⟦i⟧X⟦/i⟧
    text = re.sub(r"⟧\s*/i\s*⟧", "⟦/i⟧", text)
    text = re.sub(r"[\[【]\s*(/?)i\s*[\]】]", lambda m: "⟦" + m.group(1) + "i⟧", text)
    text = re.sub(r"<\s*(/?)i\s*>", lambda m: "⟦" + m.group(1) + "i⟧", text, flags=re.I)
    text = re.sub(r"⟦\s*(/?)i\s*⟧", lambda m: "⟦" + m.group(1) + "i⟧", text)
    # an opener whose closer lost its slash: ⟦i⟧…⟧  ->  ⟦i⟧…⟦/i⟧
    text = re.sub(r"⟦i⟧([^⟦⟧]*)⟧", lambda m: "⟦i⟧" + m.group(1) + "⟦/i⟧", text)
    out, stack = [], []
    for piece in re.split(r"(⟦i⟧|⟦/i⟧)", text):
        if piece == "⟦i⟧":
            stack.append(len(out))
            out.append(piece)
        elif piece == "⟦/i⟧":
            if not stack:
                continue
            stack.pop()
            out.append(piece)
        else:
            out.append(piece)
    while stack:
        del out[stack.pop()]
    return "".join(out)


def _latin(text: str) -> str:
    # the prompt uses <verse>/<attr>/<head> wrappers for the source; models echo them
    text = re.sub(r"<\s*/?\s*(?:verse|attr|head|source|analysis|first_translation"
                  r"|improved_translation|polished|proofread|audit|expression)\s*>",
                  "", text, flags=re.I)
    text = re.sub(r"\*\*|__|`|~~", "", text)
    text = re.sub(r"(?m)^\s*#{1,6}\s*", "", text)
    return text


# One unit system for the whole book. style.py names only a few of these, and the
# writer promptly drifted into 英尺/英寸/英里 in a dozen places; a book that mixes
# two spellings of the same unit reads like two translators. Normalise here so the
# rule survives every rebuild instead of living as hand edits to final.txt.
UNIT_MAP = (
    ("平方英尺", "平方呎"), ("平方英寸", "平方吋"),
    ("立方英尺", "立方呎"), ("立方英寸", "立方吋"),
    ("英尺", "呎"), ("英寸", "吋"), ("英里", "哩"),
    ("海浬", "浬"), ("英寻", "浔"), ("英两", "盎司"),
)


def _units(text: str) -> str:
    for a, b in UNIT_MAP:
        text = text.replace(a, b)
    return text


def _space(text: str) -> str:
    text = text.replace("\u3000", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *" + NL + r" *", NL, text)
    text = re.sub(r"， +", "，", text)
    text = re.sub(r"(?<=[\u4e00-\u9fff]) +(?=[\u4e00-\u9fff])", "", text)
    text = re.sub(r"(?<=[\u4e00-\u9fff]) +(?=[，。、；：！？”’）】])", "", text)
    text = re.sub(r"(?<=[（【“‘]) +", "", text)
    return text


def clean(text: str, numerals: bool = True) -> str:
    t = text.replace("\r\n", NL).replace("\r", NL)
    t = _latin(t)
    t = _fix_markers(t)
    t = _drop_latin_glosses(t)
    if numerals:
        t = _replace_numbers(t)
    t = _punct(t)
    t = _straight(t)
    t = fix_quotes(t)
    t = _space(t)
    t = re.sub(r"⟦i⟧\s*⟦/i⟧", "", t)
    t = t.replace("⟦/i⟧⟦i⟧", "")
    t = _units(t)
    return t.strip()


if __name__ == "__main__":
    print(clean("他生于1819年，重约1,200磅；12.5浔深，他说\"好\"..."))
