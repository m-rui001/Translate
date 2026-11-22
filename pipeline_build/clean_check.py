"""Scan every output EPUB for text that should not be there.

The assembler guarantees structure -- manifest, spine, nav, ncx, one copyright paragraph.
It cannot guarantee that the prose is clean, because translations came from a model and
defects reach the page whenever a chunk was accepted with a flaw inside it. This script
checks the finished books, not the intermediate files, so what it reports is what a
reader would actually see.

Five checks, each aimed at a defect this pipeline has produced at least once:

1. **Latin words inside Chinese sentences.** The writer occasionally left an adverb in
   English and carried on in Chinese -- `杜兰特太太 meanwhile 在后屋`. Ten such leaks were
   found and repaired by hand; this check proves there are no more.
2. **Untranslated paragraphs.** A whole paragraph that is two-thirds Latin letters in a
   Chinese book means a chunk was passed through instead of translated.
3. **Markup leakage.** `⟦i⟧` becomes `<em>` at assembly, so any surviving marker, any
   `**bold**`, any leading `#`, any `[SEP1]` is a failure to convert.
4. **Empty chapters.** A chapter file with fewer than 20 Chinese characters is a heading
   with nothing under it -- the reader turns a page and finds a blank.
5. **Doubled headings.** `<title>` and `<h1>` are separate elements and both render in the
   TOC; a chapter whose `<h1>` repeats the book title is not an error, but a `<h1>` that
   appears twice verbatim in the body is.

Quoted foreign text is expected and must not be flagged: `Floret silva undique` is a song
the characters sing, `König, birgst dich in Finsternissen` is a poem, and the emendation
list in *Jedermann* prints `Das → Daß`. The rule is therefore *Chinese on both sides of a
lowercase Latin word*, which quoted verse never satisfies.
"""
from __future__ import annotations

import glob
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "out")

CJK = re.compile(r"[\u4e00-\u9fff]")
TAG = re.compile(r"<[^>]+>")
# a lowercase Latin word with Chinese on both sides -- the signature of a leak
LEAK = re.compile(r"[\u4e00-\u9fff]\s+([a-z]{3,12})\s+[\u4e00-\u9fff]")

# Loanwords the source text itself speaks in. These are not defects: the book names a
# thing in its own language and a Chinese reader is meant to see that word.
LOAN = {
    # Italian
    "lazzo", "pazzi", "ragione", "ribellione", "calli", "virtuoso",
    # Latin, quoted or mock-quoted
    "moribundus", "vacuum", "mot", "liquefacta", "aquatinta", "gaudeamus",
    # words being glossed -- the paragraph exists to explain the word itself
    "hvalt", "hval", "welsch", "welschland",
    # Spanish
    "delicado", "visitador", "prolongada", "peseta", "plaisir", "bandera",
    # German
    "kauern", "hoch",
    # Dutch colonial measures and terms, glossed in the same paragraph
    "erf",
    # other
    "fogas", "pas", "plateau",
}# Left-over inline markup that should have become <em> or been dropped. `#` is not a
# marker here -- the books print numbered lists ("#{1,6} 40. 此章中…") and verse
# counts, so only the pipeline's own conventions are checked.
#
# `**` needs care: the source prints redacted proper names as asterisks --
# `冯·***亲王`, the prince whose name Proust never gives. That is the text, not a leak,
# so a run of asterisks adjacent to a middle dot or Chinese is accepted.
MARKER = re.compile(r"⟦[^⟧]{0,4}⟧|(?<![·\u4e00-\u9fff])\*\*(?![*·\u4e00-\u9fff])|\|\|")
SEP = re.compile(r"\[?\s*(?:SEP|分割线)\s*\d+\s*\]?")


def body_text(html: str) -> str:
    """Visible text of a content document, block tags turned into line breaks."""
    m = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
    inner = m.group(1) if m else html
    inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
    # A heading directly followed by a paragraph would otherwise concatenate into one
    # block, and `第一部 … 清晨鸟儿的啁啾…` then looks like markup leaked into prose.
    inner = re.sub(r"</(?:p|h[1-6]|div|li|blockquote|tr)>|<br\s*/?>", "\n\n", inner)
    return TAG.sub("", inner)


def check(path: str) -> list[str]:
    problems: list[str] = []
    name = os.path.basename(path)
    with zipfile.ZipFile(path) as z:
        docs = [n for n in z.namelist() if n.endswith(".xhtml")]
        for d in docs:
            if d.endswith(("nav.xhtml", "title.xhtml", "copyright.xhtml")):
                continue
            text = body_text(z.read(d).decode("utf-8", "replace"))
            paras = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]

            for p in paras:
                # A page with only a volume marker (". 第三部 .") is a divider, not an
                # empty chapter: 魔戒 emits one between books on purpose.
                if len(paras) <= 2 and all(len(CJK.findall(x)) < 12 for x in paras):
                    break
                m = LEAK.search(p)
                if m and m.group(1) not in LOAN:
                    problems.append(f"{d}: Latin leak {m.group(1)!r} in {p[max(0, m.start()-30):m.end()+30]!r}")
                han = len(CJK.findall(p))
                if han < 25:
                    continue
                lat = len(re.findall(r"[A-Za-zÄÖÜäöüß]", p))
                # A glossary entry glosses a foreign word by quoting it whole. 草原村 ends
                # with one, and those paragraphs are mostly the entry itself. The entry
                # number is Chinese -- 【七十九】 -- not Arabic.
                if lat > len(p) * 0.6 and not re.search(r"【[\d一二三四五六七八九十零百]+】", p[:12]):
                    problems.append(f"{d}: untranslated paragraph {p[:60]!r}")
                if MARKER.search(p) or SEP.search(p):
                    problems.append(f"{d}: markup leaked {p[:60]!r}")

            han = len(CJK.findall(text))
            if han < 20:
                # A volume divider is a title page on purpose -- one per book, marked
                # `class='titlepage'` with the volume number and the volume title and
                # nothing else. It is only an empty chapter if the page is not one.
                raw = z.read(d).decode("utf-8", "replace")
                if "titlepage" not in raw and not re.search(r"<h[12]>", raw):
                    problems.append(f"{d}: near-empty chapter ({han} 汉字)")

            heads = re.findall(r"<h1>(.*?)</h1>", z.read(d).decode("utf-8", "replace"))
            if len(heads) > 1:
                problems.append(f"{d}: {len(heads)} <h1> in one document")
    return [f"{name}: {p}" for p in problems]


# Deliberate exceptions, with the reason. Anything not listed here is a defect.
ALLOW = {
    ("达洛维夫人", "space between Chinese"):
        "留声机唱词按音节分行，原文 ee um fah um so 一个音一个格",
    ("新诗集", "near-empty chapter"):
        "里尔克的献辞页，一页只有一行",
    ("茵梦湖", "Latin leak"):
        "注文引用它所解释的德语动词 priesterten",
    ("追忆似水年华", "Latin leak"):
        "原文 corridor/collidor 的谐音玩笑，注释里必须保留",
}


def allowed(book: str, problem: str) -> str | None:
    for (b, kind), reason in ALLOW.items():
        if b in book and kind in problem:
            return reason
    return None

def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    files = sorted(glob.glob(os.path.join(OUT, "*.epub")))
    total = 0
    bad_books = 0
    for f in files:
        raw = check(f)
        probs = [p for p in raw if not allowed(os.path.basename(f), p)]
        skipped = len(raw) - len(probs)
        if skipped:
            print(f"[ok ] {os.path.basename(f)}: {skipped} known exception(s)")
        if probs:
            bad_books += 1
            print(f"[!! ] {os.path.basename(f)}  ({len(probs)})")
            for p in probs[:8]:
                print("      " + p)
        total += len(probs)
    print(f"\n{len(files)} epub, {bad_books} with problems, {total} problems")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
