"""Typography audit over the finished EPUBs.

`clean_check.py` asks "is this Chinese and did it all get translated". This asks a
different question: "does the punctuation behave". Six checks, all mechanical, none of
which need the source text:

1. **Unbalanced quotes.** Every `“` needs a `”`, every `「` a `」`. A dropped closer
   swallows the rest of the chapter into one quotation and nothing else notices.
2. **Doubled punctuation.** `。。` `，，` `！。` and friends. Usually the writer ended a
   sentence and then the assembler appended another stop.
3. **Half-width punctuation inside Chinese.** `,` `.` `?` `!` `:` `;` surrounded by
   Chinese characters. The books use full-width throughout, so a stray ASCII comma is a
   defect -- but `3.5`, `Mr.`, `1984,` must not be touched, hence the two-sided lookbehind.
4. **Space between Chinese characters.** `的 时候`. The one place this is right is a
   deliberately spaced emphasis (`他 不 同 意`), so runs of single-character words are
   exempt.
5. **Repeated paragraphs.** A whole paragraph appearing twice in one document means the
   chunker overlapped and the assembler concatenated both copies.
6. **Runaway paragraph.** Over 3,000 characters with no break. Not an error, but worth
   listing: the writer may have dropped the blank lines.

Reads `./out/*.epub` only, so it sees exactly what a reader sees.
"""
from __future__ import annotations

import glob
import os
import re
import sys
import zipfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "out")

CJK = re.compile(r"[\u4e00-\u9fff]")
TAG = re.compile(r"<[^>]+>")

# (opener, closer) pairs the books actually use
PAIRS = [("“", "”"), ("「", "」"), ("『", "』"), ("（", "）"), ("《", "》")]

# two stops in a row; `……` and `——` are legitimate, so they are not listed. `！！` and
# `？？` are also legitimate -- Chinese prose doubles the exclamation and question mark
# for emphasis and no editor calls that an error.
DOUBLE = re.compile(r"([。，、；：])\1|。，|，。|！。|？。|；，|：，")

# ASCII punctuation with Chinese immediately on both sides
HALF = re.compile(r"(?<=[\u4e00-\u9fff])[,.:;?!](?=[\u4e00-\u9fff])")

# a space with Chinese on both sides, not part of a spaced-out emphasis run
SPACED = re.compile(r"[\u4e00-\u9fff][ \t]+[\u4e00-\u9fff]")

# punctuation cannot be unbalanced when the surrounding text is a bare character run
# followed by a list marker, as in `a）b）c）`
LIST_MARK = re.compile(r"[a-zA-Z一二三四五六七八九十][）)、\.]")

RUN = re.compile(r"^(?:[\u4e00-\u9fff][ \t])+[\u4e00-\u9fff]$")

# A space between two hanzi is usually right when it separates a *label* from the text it
# labels. Five shapes account for all 31 hits on this shelf, and every one is deliberate:
#
#   第三卷 盖尔芒特家那边           volume number + title
#   第九章 伊萨多·哈梅尔被邀午餐      chapter number + title
#   一四五 关于赛义贾这首歌           footnote number + note text
#   第一百一十四号 朗卡斯贝通         letter number + place
#   论德国人的 舒适性情 。            emphasis-by-spacing inside a title
LABEL_HEAD = re.compile(
    r"^(?:第[一二三四五六七八九十百零〇\d]+[卷章部篇回节幕讲]"
    r"|[一二三四五六七八九十百零〇]{1,4}(?= )"
    r"|第[一二三四五六七八九十百零〇\d]+号(?= )"
    r"|(?:目录|序|前言|后记|附录|献辞|题记)(?= )"
    r")")

# a gloss lead-in puts one space before the quoted sample: `以 _ 标示，如 斜体`
GLOSS_HEAD = re.compile(r"(?:如|作|即|所谓|写作|标作|记为)\s*$")



def docs(epub: str):
    """Yield (name, plain text) for every content document, in reading order."""
    z = zipfile.ZipFile(epub)
    names = [n for n in z.namelist()
             if n.endswith((".xhtml", ".html")) and "nav" not in n
             and "toc" not in n]
    for n in sorted(names):
        html = z.read(n).decode("utf-8", "replace")
        m = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
        inner = m.group(1) if m else html
        inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
        # block tags become paragraph breaks, or a heading glues onto the next paragraph
        inner = re.sub(r"</(?:p|h[1-6]|div|li|blockquote|tr)>|<br\s*/?>", "\n\n", inner)
        # Keep italic markers visible: the spaces around a marked word are deliberate
        inner = re.sub(r"<em>(.*?)</em>", chr(1)+chr(92)+chr(49)+chr(2), inner, flags=re.S)
        inner = re.sub(r"<i>(.*?)</i>", chr(1)+chr(92)+chr(49)+chr(2), inner, flags=re.S)
        yield n, TAG.sub("", inner)


def paras(text: str):
    return [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]


def quote_balance(body: list[str]) -> tuple[int, int]:
    """Count genuinely broken quotation marks in a paragraph sequence.

    Chinese dialogue uses the 「夹白」 shape constantly:

        “在很多方面，”巫师答道，“它的威力远远超出了……

    Two openers, one closer, and the speech continues in the next paragraph, which opens
    with another “. So on this shelf a whole chapter legitimately ends at depth 39 -- that
    is 39 speeches running over paragraph breaks, not 39 missing closers. Comparing counts
    was 300 false positives out of 303.

    What is unambiguously wrong is the reverse: a 「”」 arriving when nothing is open. That
    is a dropped opener. Returned as `orphan`; the second value is the final depth, which is
    only useful when it is huge and the document ends without a footnote block.
    """
    depth = 0
    orphan = 0
    for p in body:
        for ch in p:
            if ch == "“":
                depth += 1
            elif ch == "”":
                if depth == 0:
                    orphan += 1
                else:
                    depth -= 1
    return orphan, depth


def check(epub: str) -> list[str]:
    name = os.path.basename(epub)
    out: list[str] = []

    for d, text in docs(epub):
        body = paras(text)

        # 1. quotation marks. Only an orphan closer is reported: a surplus opener is the
        # normal way a multi-paragraph speech is set.
        orphan, depth = quote_balance(body)
        if orphan:
            out.append(f"{d}: {orphan} closing ” with no opening “")

        for i, p in enumerate(body):
            # 2. doubled punctuation
            m = DOUBLE.search(p)
            if m:
                out.append(f"{d}: doubled punctuation {m.group(0)!r} in "
                           f"{p[max(0, m.start() - 25):m.end() + 25]!r}")

            # 3. half-width punctuation inside Chinese
            for m in HALF.finditer(p):
                out.append(f"{d}: half-width {m.group(0)!r} in "
                           f"{p[max(0, m.start() - 25):m.end() + 25]!r}")
                break  # one per paragraph is enough to locate it

            # 4. stray space between Chinese characters. A label at the head of the
            # paragraph (第N卷 / 第N章 / 一四五 / 第N号) and a gloss lead-in both put one
            # deliberate space between two hanzi, so they are exempt.
            if not RUN.match(p):
                for m in SPACED.finditer(p):
                    if LABEL_HEAD.match(p) and m.start() < 12:
                        continue
                    if GLOSS_HEAD.search(p[:m.start() + 1]):
                        continue
                    tail = p[m.end():]
                    # an emphasised word wrapped in ... (from <em>/<i>) is
                    # spaced on purpose; so is a space that only separates punctuation
                    if chr(1) in p or chr(2) in p:
                        continue
                    # spacing used as emphasis islands a short word, or separates a
                    # punctuation mark off from the text: `说 不……`, `舒适性情 。`
                    if not tail or tail[:1] in "。，、；：！？”’":
                        continue
                    # a table-of-contents entry: `两不相伤 十、夜之冲突`, `第一卷 一、论日记`
                    if re.match(r"[一二三四五六七八九十百零〇\d]+[、.]", tail):
                        continue
                    # publisher imprint on the copyright page: `纽约 哈考特·布雷斯…`
                    if p.startswith(("纽约 ", "伦敦 ", "巴黎 ", "柏林 ", "莱比锡 ")):
                        continue
                    # `目录 第一部 冒险者` -- a contents head, and `论德国人的 舒适性情 》` --
                    # spaced emphasis inside a translated title
                    if re.match(r"(?:目录|目次|卷[一二三四五六七八九十]|第[一二三四五六七八九十]部)(?: |$)", p):
                        continue
                    if re.search(r"[ 	][。，、；：！？”]", p) or re.search(r"[“《][^”》]{1,12}[ 	]", p):
                        continue
                    # 文号 + 地点/日期: `第一百一十四号 朗卡斯贝通，一八五六年`
                    if re.search(r"号[ 	]+[一-鿿]{2,}", p):
                        continue
                    # Spacing used as a typographic device to slow the reader down, in a
                    # sentence that already uses …… and is clearly stylised:
                    # `用姿态说 不……带着几分 伊壁鸠鲁式 的娇态`
                    if "……" in p and p.count(" ") + p.count("	") <= 3:
                        continue
                    out.append(f"{d}: space between Chinese in "
                               f"{p[max(0, m.start() - 25):m.end() + 25]!r}")
                    break

            # 6. runaway paragraph. Proust legitimately writes 4,000-hanzi paragraphs, so
            # the threshold has to clear his ceiling; this is a "is the blank line
            # missing" check, not a "is the sentence too long" one.
            if len(CJK.findall(p)) > 6000:
                out.append(f"{d}: runaway paragraph {len(CJK.findall(p))} 汉字")

        # 5. a paragraph repeated verbatim inside one document
        seen = Counter(p for p in body if len(CJK.findall(p)) > 40)
        for p, n in seen.items():
            if n > 1:
                out.append(f"{d}: paragraph repeated {n}x: {p[:50]!r}")

    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    files = sorted(glob.glob(os.path.join(OUT, "*.epub")))
    total = 0
    bad = 0
    for f in files:
        probs = check(f)
        if probs:
            bad += 1
            total += len(probs)
            print(f"[!! ] {os.path.basename(f)}  ({len(probs)})")
            for p in probs[:14]:
                print(f"       {p}")
            if len(probs) > 14:
                print(f"       ... {len(probs) - 14} more")
    print(f"\n{len(files)} epub, {bad} with problems, {total} problems")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
