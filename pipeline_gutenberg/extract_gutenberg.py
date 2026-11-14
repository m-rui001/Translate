"""Turn a Project Gutenberg plain-text file into the pipeline's block format.

Every earlier book in this workspace arrived as a PDF or an EPUB and needed a
bespoke extractor, because page ranges and calibre class names are specific to
one file. Gutenberg text is plain UTF-8 with a licence header and footer, so one
extractor covers every public-domain title: strip the boilerplate, split at the
chapter headings that `structure.py` located, fold hard-wrapped lines back into
paragraphs, and emit the same `{id, title, blocks}` JSON the chunker consumes.

Paragraph folding must not be naive. Gutenberg wraps at ~70 columns, so a
paragraph is a run of lines between blank lines. Two traps:

  * a hyphen at a line end is usually, but not always, a broken word. It is
    joined only when the next line continues in lower case, so "wohl-\ngebildet"
    becomes "wohlgebildet" while "Vor-\nund Nachteile" keeps its dash.
  * Gutenberg marks italics with underscores, which would otherwise print as
    literal `_word_` in Chinese. They become the pipeline's own `⟦i⟧…⟦/i⟧`
    markers, the same ones the EPUB extractor emits.

Usage:
    python pipeline_gutenberg/extract_gutenberg.py --book nachsommer
    python pipeline_gutenberg/extract_gutenberg.py --all
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import structure  # noqa: E402

WS = re.compile(r"[ \t\u00a0]+")
# a page number, a running head, or bracketed editorial junk
JUNK = re.compile(r"^\s*(?:\[?[Pp]age\s*\d+\]?|\[[^\]]{0,40}\]|\[Ilustración\]|"
                  r"\[Illustration\])\s*$")
# Some volumes carry the licence title as a *plain line* rather than inside the
# asterisked wrapper ("End of Project Gutenberg's X, by Y"). Splitting at the
# chapter level leaves such a line as the last paragraph of the last chapter,
# where it would be translated into Chinese as if it were the final sentence.
LICENCE_LINE = re.compile(
    r"^(?:End of (?:the )?Project Gutenberg.*|\*\*\* ?END OF.*|"
    r"Produced by .{0,80}|Updated editions will replace the previous one.*|"
    r"This eBook is for the use of anyone anywhere.*)$", re.I)
# Gutenberg italic marking, always a balanced pair inside one line
ITAL = re.compile(r"(?<!\w)_([^_\n]{1,200})_(?!\w)")


def mark_italics(s: str) -> str:
    """`_word_` -> `⟦i⟧word⟦/i⟧`, the pipeline's emphasis convention."""
    return ITAL.sub(lambda m: "⟦i⟧" + m.group(1) + "⟦/i⟧", s)


def clean_line(s: str) -> str:
    s = s.replace("\r", "").replace("\u00ad", "")
    s = WS.sub(" ", s)
    return s.strip()


def fold(lines: list[str]) -> str:
    """Join a hard-wrapped paragraph, undoing hyphenation only where it is real."""
    out = ""
    for i, l in enumerate(lines):
        if i == 0:
            out = l
            continue
        if out.endswith("-") and not out.endswith("--") and l[:1].islower():
            out = out[:-1] + l          # a word broken across the line break
        else:
            out = out + " " + l
    out = re.sub(r"\s+", " ", out).strip()
    return mark_italics(out)


def build_blocks(lines: list[str], starts: list[int]) -> list[tuple[str, list[dict]]]:
    """Split at `starts`, returning (chapter title, blocks) pairs."""
    chapters: list[tuple[str, list[dict]]] = []
    front = lines[:starts[0]] if starts else lines
    chapters.append(("", to_blocks(front, skip_head=False)))
    for j, at in enumerate(starts):
        end = starts[j + 1] if j + 1 < len(starts) else len(lines)
        body = lines[at:end]
        title = body[0].strip()
        chapters.append((title, to_blocks(body[1:], skip_head=True, title=title)))
    return chapters


def to_blocks(lines: list[str], skip_head: bool = False, title: str = "") -> list[dict]:
    blocks: list[dict] = []
    if title:
        blocks.append({"type": "head", "text": title})
    buf: list[str] = []

    def flush():
        nonlocal buf
        if buf:
            t = fold(buf)
            if t:
                blocks.append({"type": "p", "text": t})
            buf = []

    for raw in lines:
        line = clean_line(raw)
        if not line:
            flush()
            continue
        if JUNK.match(line) or LICENCE_LINE.match(line):
            continue
        buf.append(line)
    flush()
    return blocks


def run(book: str, min_paras: int = 3) -> dict:
    import books_meta
    meta = books_meta.BOOKS[book]
    src = os.path.join(ROOT, "work_gutenberg", "src", book + ".txt")
    out = os.path.join(ROOT, "work_gutenberg", book, "src")
    os.makedirs(out, exist_ok=True)

    raw = open(src, encoding="utf-8", errors="replace").read()
    lines = structure.strip_licence(raw).split("\n")
    kind, starts = structure.chapter_starts(lines)

    chapters = build_blocks(lines, starts)
    index, kept = [], 0
    for i, (title, blocks) in enumerate(chapters, 1):
        paras = [b for b in blocks if b["type"] == "p" and b["text"].strip()]
        if len(paras) < min_paras:
            continue          # title pages, contents lists, half-titles
        cid = f"c{i:03d}"
        kept += 1
        chars = sum(len(b["text"]) for b in blocks)
        json.dump({"id": cid, "title": title, "blocks": blocks},
                  open(os.path.join(out, cid + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        index.append({"id": cid, "title": title, "paras": len(paras), "chars": chars})

    json.dump({"book": book, "lang": meta["lang"], "structure": kind,
               "title_zh": meta["title_zh"], "chapters": index},
              open(os.path.join(out, "index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    total = sum(x["chars"] for x in index)
    return {"book": book, "kind": kind, "chapters": kept,
            "chars": total, "out": out}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    import books_meta
    books = list(books_meta.BOOKS) if a.all else [a.book]
    for b in books:
        r = run(b)
        print(f"{r['book']:16s} {r['kind']:10s} ch={r['chapters']:3d} "
              f"chars={r['chars']:8,}")


if __name__ == "__main__":
    main()
