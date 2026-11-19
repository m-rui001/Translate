"""Assemble the 20 public-domain Gutenberg books into EPUB 3.

These books were translated chunk by chunk, then polished. Three things differ from
the older books in `build_all.py`:

  * the chapter list comes from `work_gutenberg/<book>/chunks/*.json`, which carries
    `title_src` / `title_zh`, and the translated prose lives in
    `work_gutenberg/<book>/out/<cid>/cNN/final.txt`;
  * there are no footnote sidecars and no JSON text arrays, so the assembled text is
    simply the polished paragraphs concatenated in chunk order;
  * some volumes lost their `*** START` marker, so the first chapter still opens with
    Gutenberg's own transcription notice. That has to be cut before the prose starts.

Two known defects get fixed here, at assembly time, rather than by rebuilding
thousands of translation units:

  * `⟦i⟧…⟦/i⟧` emphasis markers leak into the prose because chunk files were written
    before the assembler learned about emphasis. `para_html` converts them to `<em>`,
    exactly as it does for the older books;
  * a first chapter that is still Gutenberg front matter is skipped past by finding the
    first substantial prose paragraph, the same heuristic the chunker used.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "pipeline_gutenberg"))

import build_all as B           # noqa: E402  (shared page/package builders)
import books_meta               # noqa: E402
import titles_src               # noqa: E402

GUT = os.path.join(ROOT, "work_gutenberg")
OUT = os.path.join(ROOT, "out")

CJK = re.compile(r"[\u4e00-\u9fff]")

# Gutenberg's own front matter, in the languages this shelf uses. Matched only at the
# start of a chapter, and only to *drop* paragraphs, never to alter prose.
FRONT = re.compile(
    r"produced by|transcriber|project gutenberg|"
    r"this ebook is for the use of anyone anywhere|"
    r"erreurs? de transcription|transcription|"
    r"edizione elettronica|progetto manuzio|"
    r"este livro foi digitalizado|"
    r"título original|publicado originalmente|"
    r"^\s*[A-Z][A-Za-z ]{2,30}\s*:\s*$",
    re.I)

# The transcription notice as it actually reaches us, already translated. It is a short
# opening paragraph (or a bracketed block) naming the proofreading effort; matching those
# words is what `strip_front` needs, and it must never be widened into "skip to the first
# paragraph that looks like prose", which silently eats real chapters.
NOTICE = re.compile(
    r"produced by|project\s+gutenberg|gutenberg\.org|distributed\s+proof|pgdp\.net|"
    r"转录|校对|校读|分布式",
    re.I)


# A Project Gutenberg licence page that the extractor sliced as a chapter. These must
# not reach the table of contents: `effi` shipped one as "chapter 1", which pushed every
# real chapter one number higher, and `diana` shipped the writer's refusal to translate
# it. Both are identified by wording that cannot occur in a novel.
LICENCE_CH = re.compile(
    r"Release date:|Most recently updated|eBook #\d+|^\s*Credits:|Project Gutenberg",
    re.I | re.M)


def chapter_ids(book: str) -> list[str]:
    fs = sorted(glob.glob(os.path.join(GUT, book, "chunks", "*.json")))
    ids = [os.path.basename(f)[:-5] for f in fs]
    keep = []
    for cid in ids:
        f = os.path.join(GUT, book, "chunks", cid + ".json")
        try:
            raw = open(f, encoding="utf-8").read()
        except Exception:  # noqa: BLE001
            keep.append(cid)
            continue
        # only a chapter with no Chinese at all can be a licence page; a real chapter
        # that quotes a notice in an epigraph has prose in it and is kept
        if LICENCE_CH.search(raw) and not CJK.search(raw):
            print(f"  {book}/{cid}: licence page, dropped from the book")
            continue
        keep.append(cid)
    return keep


def chapter_meta(book: str, cid: str) -> dict:
    f = os.path.join(GUT, book, "chunks", cid + ".json")
    try:
        return json.load(open(f, encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def chapter_texts(book: str, cid: str) -> list[str]:
    """Translated paragraphs of one chapter, in chunk order."""
    d = os.path.join(GUT, book, "out", cid)
    out: list[str] = []
    for p in sorted(glob.glob(os.path.join(d, "c*", "final.txt"))):
        out += B.paras(open(p, encoding="utf-8").read())
    return out


def strip_front(texts: list[str]) -> list[str]:
    """Drop a left-over Gutenberg transcription notice from the top of a chapter.

    The licence stripper keys off `*** START OF ...`, which several of these volumes
    do not carry, so the notice is still the opening of the first chapter. Only the
    *notice itself* may go.

    This used to skip to the first paragraph that was long enough to be prose, on the
    theory that a notice always precedes it. Applied to every chapter it deleted real
    prose: any chapter whose opening short paragraphs did not add up to one paragraph
    of 500 chars / 200 hanzi lost everything before the first such block — a third of
    `maias`, a fifth of `regenta`, and 460k hanzi across the shelf. Matching the notice
    by its wording is narrower and does not depend on how a chapter happens to open.
    """
    out = list(texts)
    i = 0
    while i < len(out):
        t = out[i]
        if not NOTICE.search(t):
            break
        i += 1
        # a bracketed transcription note runs on for several paragraphs; take them
        # all, up to and including the one that closes the bracket
        if t.lstrip()[:1] in "［[" and "］" not in t and "]" not in t:
            while i < len(out) and "］" not in out[i - 1] and "]" not in out[i - 1]:
                i += 1
    return out[i:] if i else out


def collect(book: str) -> list[dict]:
    revision = B.collect_revision(book)
    if revision is not None:
        return revision

    items = []
    for cid in chapter_ids(book):
        texts = chapter_texts(book, cid)
        if not texts:
            continue
        texts = strip_front(texts)
        m = chapter_meta(book, cid)
        title = (m.get("title_zh") or "").strip()
        src = (m.get("title_src") or "").strip()
        items.append({"id": cid, "texts": texts, "types": ["p"] * len(texts),
                      "notes": [], "title_zh": title, "title_en": src,
                      "links": {}, "old_texts": None})
    return [it for it in items if it["texts"]]


def cfg_for(book: str) -> dict:
    m = books_meta.BOOKS[book]
    return {
        "title": m["title_zh"],
        "sub": m["title_src"],
        "author": m["author_zh"],
        "src": m["title_src"],
        "uid": f"urn:gutenberg-{book}-zh",
        "note": m.get("note", ""),
        "died": m.get("died"),
    }


def build(book: str) -> dict | None:
    items = collect(book)
    if not items:
        print(f"{book:14s} no translated chapters, skipped")
        return None
    cfg = cfg_for(book)
    # The source headings are in German, Spanish, Dutch, Danish and English, and many
    # are bare numerals ("-I-", "CHAPTER VII"). Both have to become readable Chinese,
    # so translate a named heading from a table and otherwise use the ordinal the
    # heading itself implies.
    for i, it in enumerate(items, 1):
        cur = (it["title_zh"] or "").strip()
        if cur and re.search(r"[一-鿿]", cur):
            continue
        it["title_zh"] = titles_src.title_for(it["title_en"] or cur, i)
    # package() writes the EPUB itself and honours build_all.OUT, so point that at
    # ./out before calling it; the shared builder hard-codes nothing else.
    B.OUT = OUT
    res = B.package(cfg, items, "chapters")
    han = sum(len(CJK.findall(t)) for it in items for t in it["texts"])
    print(f"{book:14s} {len(items):4d} chapters  {han:>9,} han  "
          f"toc={res['toc']:3d}  xml_err={res['xml_errors']}  "
          f"{res['size']/1048576:.2f}MB")
    return {"book": book, "path": res["path"], "chapters": len(items), "han": han}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(OUT, exist_ok=True)
    args = sys.argv[1:]
    books = [a for a in args if not a.startswith("-")] or list(books_meta.BOOKS)
    ok = 0
    for b in books:
        if b not in books_meta.BOOKS:
            print(f"unknown book: {b}")
            continue
        if build(b):
            ok += 1
    print(f"\n{ok}/{len(books)} built")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
