"""Extract the newly fetched public-domain sources into per-chapter block JSON.

`pipeline_gutenberg/extract_gutenberg.py` already does this job well, but it reads
from `work_gutenberg/src` and consults `books_meta.BOOKS` for each title's language
and Chinese name. Those sixteen books are a different corpus with its own metadata
(`pipeline_private/books.py`), and their sources live in `work_pub/src`, so the
extractor is reused as a library rather than copied: `build_blocks` and
`structure.chapter_starts` are the parts that encode all the hard-won knowledge
about how five different publishers mark chapters, and there is no reason to
reimplement that.

Output layout matches `work_gutenberg/<book>/src/cNNN.json` exactly, so the chunker
and the translation workflow can be pointed at the new tree unchanged.
"""
from __future__ import annotations

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "pipeline_gutenberg"))
sys.path.insert(0, os.path.join(ROOT, "pipeline_private"))

import structure                      # noqa: E402
from extract_gutenberg import build_blocks   # noqa: E402
import books as booklist              # noqa: E402

SRC = os.path.join(ROOT, "work_pub", "src")
OUT = os.path.join(ROOT, "work_pub")


def _all_in_front_or_back(lines: list[str], starts: list[int],
                          edge_frac: float = 0.04) -> bool:
    """True when every detected heading sits in the front or back matter.

    `Mrs Dalloway` from Gutenberg has no chapter divisions at all -- the novel runs as one
    continuous text broken only by `* * * * *` scene rules. But `allcaps_titles` still
    found five candidates, and all five were page furniture: the author line, the title,
    the author again, the printer, and "THE END". Splitting there produced three
    "chapters": a 625-character imprint, the entire novel under the heading "PRINTED IN
    THE UNITED STATES OF AMERICA", and a 380-character ending.

    A real chapter heading falls somewhere in the body. If no candidate does, the book is
    undivided and should be treated as one chapter rather than mangled into front matter.
    """
    if not starts:
        return False
    edge = max(20, int(len(lines) * edge_frac))
    return all(i < edge or i > len(lines) - edge for i in starts)


def _drop_tiny_title_dupes(chapters, kind: str = "word",
                           max_chars: int = 2000, front_frac: float = 0.10):
    """Remove early chapters whose title reappears later and whose text is trivial.

    Four conditions, and each one is load-bearing.

    *The headings are words, not numbers.* This is the condition added last, and it is
    the one that finally separates the two cases cleanly. A contents entry is a phrase --
    "Book the First--Recalled to Life" -- while Rilke's headings in *Neue Gedichte* are
    `I`, `II`, `III`: stanza numbers that recur naturally all through a poetry collection.
    Requiring `word` leaves numeric structures alone entirely.

    *It sits in the front matter.* Added after the first version deleted nine chapters
    from *Neue Gedichte*; a contents list is by definition printed at the front.

    *The title repeats later.* The contents copy and the body copy share a string.

    *The text is small.* `Immensee` heads two real chapters "DER ALTE", both over 2,000
    characters, and none of the other three conditions would ever touch them.
    """
    if not chapters or kind != "word":
        return chapters
    limit = max(2, int(len(chapters) * front_frac))
    titles = [next((b["text"].strip() for b in blocks
                    if b["type"] == "head" and b["text"].strip()), "")
              for _title, blocks in chapters]
    last = {}
    for i, t in enumerate(titles):
        if t:
            last[t] = i
    keep = []
    for i, (title, blocks) in enumerate(chapters):
        chars = sum(len(b.get("text", "")) for b in blocks)
        if (i < limit and title and last.get(title, -1) > i
                and chars <= max_chars):
            continue
        keep.append((title, blocks))
    return keep


def run(meta: dict, min_paras: int = 1) -> dict:
    key = meta["key"]
    src = os.path.join(SRC, key + ".txt")
    out = os.path.join(OUT, key, "src")
    os.makedirs(out, exist_ok=True)

    # Remove chapters from any earlier extraction. This directory is written to, never
    # cleared, so re-extracting a book with fewer chapters left the surplus behind:
    # `goriot` was re-run as one chapter and kept nine files, and `faust` was re-run as
    # one and kept a hundred and forty-six. Stale chapters still got chunked, translated
    # and bound into the EPUB, which is how a volume that should be a single section
    # arrived at 1,308,639 characters across nine "chapters".
    for old in glob.glob(os.path.join(out, "c*.json")):
        os.remove(old)

    raw = open(src, encoding="utf-8", errors="replace").read()
    lines = structure.strip_licence(raw).split("\n")
    if meta.get("one_act"):
        # A one-act play has no chapter structure to find. Every detector still fires --
        # speaker labels repeat, stage directions are set off by blank lines -- and
        # `repeat` split Jedermann into 33 "chapters" whose titles were the cast names
        # (JEDERMANN, DER EINE GAST, ...). Splitting a play at its speeches destroys it;
        # the chunker can carry a long single chapter perfectly well.
        kind, starts = "one_act", []
    else:
        kind, starts = structure.chapter_starts(lines)
        if _all_in_front_or_back(lines, starts):
            kind, starts = "undivided", []
    chapters = build_blocks(lines, starts)

    # A contents list that carries no page numbers defeats `contents_anchored`, whose two
    # entry patterns both end in a page number. *A Tale of Two Cities* has exactly that
    # shape -- "     CHAPTER I      The Period" with no numeral -- so the contents entries
    # survive as candidates and three of them (`Book the First--Recalled to Life` and its
    # two siblings) also appear as real body headings, yielding three 178/711/430-character
    # chapters ahead of the real ones.
    #
    # Widening the heading detectors to catch this was tried and reverted: accepting a
    # two-line heading made `find_headings` return nothing for *Le Père Goriot*, which fell
    # through to `allcaps_titles`, which matched the dedication and signature lines -- eight
    # false headings and 726,910 characters (57% of the book) silently dropped. *Faust* went
    # from 146 sections to 1. The shared detectors stay as they were.
    #
    # This is the narrow fix instead: drop a chapter only when its title repeats in a later
    # chapter AND it is too small to be prose. A genuine repeated title is never this short --
    # *Immensee* heads two real chapters "DER ALTE", both over 2,000 characters.
    chapters = _drop_tiny_title_dupes(chapters, kind)

    index, kept = [], 0
    for i, (title, blocks) in enumerate(chapters, 1):
        paras = [b for b in blocks if b["type"] == "p" and b["text"].strip()]
        if len(paras) < min_paras:
            continue
        cid = f"c{i:03d}"
        kept += 1
        chars = sum(len(b["text"]) for b in blocks)
        json.dump({"id": cid, "title": title, "blocks": blocks},
                  open(os.path.join(out, cid + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        index.append({"id": cid, "title": title, "paras": len(paras), "chars": chars})

    json.dump({"book": key, "lang": meta["lang"], "structure": kind,
               "title_zh": meta["title_zh"], "title_src": meta["title_src"],
               "author_zh": meta["author_zh"], "author_src": meta["author_src"],
               "died": meta["died"], "chapters": index},
              open(os.path.join(out, "index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    return {"book": key, "kind": kind, "chapters": kept,
            "chars": sum(x["chars"] for x in index)}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    todo = sys.argv[1:]
    metas = [m for m in booklist.PUBLIC if not todo or m["key"] in todo]
    bad = []
    for m in metas:
        try:
            r = run(m)
        except Exception as e:                     # noqa: BLE001
            print(f"{m['key']:16s} ERROR {str(e)[:90]}")
            bad.append(m["key"])
            continue
        flag = "" if r["chapters"] >= 2 else "  <- single chapter, check"
        print(f"{r['book']:16s} {r['kind']:12s} ch={r['chapters']:3d} "
              f"chars={r['chars']:8,}{flag}")
    if bad:
        print(f"\nFAILED: {bad}")
        sys.exit(1)


if __name__ == "__main__":
    main()
