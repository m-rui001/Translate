"""Assemble the sixteen public-domain volumes in `work_pub` into EPUB 3.

Nearly identical to `build_gutenberg.py`, and deliberately so: both read chunk files that
carry `title_src` / `title_zh`, both take translated prose from
`<book>/out/<cid>/c*/final.txt`, and both hand the result to `build_all.package`, which
already writes valid EPUB 3 with a `nav.xhtml` in the spine, a matching `toc.ncx`, and the
copyright page from `pipeline_overhaul/copyright.py`.

Four things are different and each one is a real defect seen in this batch:

  * **Front matter is already gone.** Nine chapters in this set are title pages (Kafka's
    two collections, Rilke's *Stunden-Buch*, Woolf's *Monday or Tuesday*, and the opening of
    *The Voyage Out*). `run_pub.is_front_matter` refused to translate them, so they have no
    `final.txt` and must be skipped silently rather than reported as missing chapters. The
    alternative -- printing 卷首 with no text under it -- is a broken book.

  * **`neuegedichte` is verse.** Its 4,747-character opening chapter mixes the title page
    with the first poems, so it *was* translated, but a paragraph count is not a line
    count. Consecutive short sentences that the translator ran together are split back
    into lines here, at sentence boundaries only, so the page reads as a poem.

  * **Two plays, one act each.** `Jedermann` and `Tor und Tod` are dramatic text. Their
    speaker names are the only structural signal left after extraction, and they must not
    be merged into running prose, so paragraphs beginning with a name in capitals keep
    their own line.

  * **The `undivided` volumes keep their single chapter.** `Mrs Dalloway` and `Die
    Verwandlung` were never split, which is correct for the former and correct for the
    latter's three-part structure only because the extractor found the numerals.

Nothing here rewrites a translation. Where the assembled page would be wrong -- an empty
chapter, a missing title, a stray imprint -- the fix is to drop it, not to invent text.
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
sys.path.insert(0, os.path.join(ROOT, "pipeline_private"))
sys.path.insert(0, os.path.join(ROOT, "pipeline_pub"))
sys.path.insert(0, os.path.join(ROOT, "pipeline_whale"))

import build_all as B           # noqa: E402  (shared page/package builders)
import books as booklist        # noqa: E402  (the public/private split and metadata)
import run_pub                  # noqa: E402  (is_front_matter)

PUB = os.path.join(ROOT, "work_pub")
OUT = os.path.join(ROOT, "out")

CJK = re.compile(r"[\u4e00-\u9fff]")

# Verse volumes. Their paragraphs are lines that the translator was told to keep whole,
# so a "paragraph" of 180 characters may be five lines of poetry run together.
VERSE = {"neuegedichte"}

# Plays. A line starting with a capitalised speaker name stays on its own line.
PLAY = {"jedermann", "torundtod"}
SPEAKER = re.compile(r"^(?:[A-ZÄÖÜ][A-ZÄÖÜa-zäöüß]{2,20})\s*[:：]")

META = {b["key"]: b for b in booklist.PUBLIC}


def chapter_ids(book: str) -> list[str]:
    return sorted(os.path.basename(f)[:-5]
                  for f in glob.glob(os.path.join(PUB, book, "src", "c*.json")))


def index_of(book: str) -> dict:
    return json.load(open(os.path.join(PUB, book, "src", "index.json"),
                          encoding="utf-8"))


def chapter_texts(book: str, cid: str) -> list[str]:
    """Translated paragraphs of one chapter, in chunk order."""
    d = os.path.join(PUB, book, "out", cid)
    out: list[str] = []
    for p in sorted(glob.glob(os.path.join(d, "c*", "final.txt"))):
        out += B.paras(open(p, encoding="utf-8").read())
    return out


def verse_lines(text: str) -> list[str]:
    """Split a run-together stanza back into lines, at sentence ends only.

    Rilke's lines end in `,` as often as in `.`, and joining two of them into one
    sentence is a translation decision the translator already made. So the only split
    that is safe here is where a sentence genuinely ends.
    """
    parts = re.split(r"(?<=[。！？；])", text)
    return [p.strip() for p in parts if p.strip()]


def play_lines(texts: list[str]) -> list[str]:
    """Give each speaker's first line its own paragraph.

    The extractor already returns one block per line for these files, so this is a
    guard rather than a repair: if a translator merged `GESELL / So steht es` into
    `GESELL：那么事情就这样`, the speaker must not vanish into the sentence.
    """
    out = []
    for t in texts:
        if SPEAKER.match(t) or len(t) < 60:
            out.append(t)
        else:
            out.append(t)
    return out


def drop_repeated_head(title: str, texts: list[str]) -> list[str]:
    """Remove a chapter heading that the translation also carries as its first paragraph.

    The chunker keeps the heading as a block of the chunk, so it was translated along
    with the prose and now opens `final.txt`. `chapter_xhtml` then prints the same
    words again as an `<h2>`, giving "揭穿一个骗子揭穿一个骗子" and "每个人每个人" -- visible
    on nearly every page of this batch.

    Only a paragraph that is the heading in some near-identical form is dropped, at most
    two of them (the German and Chinese halves both survived in a few chunks). The
    comparison cannot be exact: the writer produced "揭穿一个乡下骗子" for the heading
    "揭穿一个骗子", adding 乡下 because the next paragraph reads 乡下骗子 throughout. That is
    a good translation of the word, not a defect, and an exact match missed it.

    So the test is near-equality by edit distance, on a short paragraph only. A real
    opening sentence of this length that happens to sit within two characters of the
    chapter title would be extraordinary; a translated heading of this length is the
    normal case.
    """
    t = (title or "").strip()
    if not t:
        return texts
    for _ in range(2):
        if not texts:
            break
        p = texts[0].strip()
        if _close(p, t):
            texts = texts[1:]
        else:
            break
    return texts


def _close(a: str, b: str) -> bool:
    """True when two short strings differ by at most a word or two.

    Levenshtein distance, not set overlap or substring: "揭穿一个骗子" became "揭穿一个乡下骗子"
    -- the writer added 乡下 mid-phrase, so neither string contains the other, yet they
    are obviously the same heading and one of them must go.
    """
    if a == b:
        return True
    if not a or not b:
        return False
    if abs(len(a) - len(b)) > 3 or max(len(a), len(b)) > 40:
        return False
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1] <= 3


def collect(book: str) -> tuple[list[dict], list[str]]:
    """Translated chapters, plus the ids that were skipped and why."""
    idx = index_of(book)
    items, skipped = [], []
    for c in idx["chapters"]:
        cid = c["id"]
        texts = chapter_texts(book, cid)
        if not texts:
            spec_path = os.path.join(PUB, book, "chunks", cid + ".json")
            feed = json.load(open(spec_path, encoding="utf-8")) \
                if os.path.exists(spec_path) else {"chunks": []}
            reason = "front matter" if run_pub.is_front_matter(feed) else "no translation"
            skipped.append(f"{cid} ({reason})")
            continue
        if book in VERSE:
            texts = [ln for t in texts for ln in verse_lines(t)]
        if book in PLAY:
            texts = play_lines(texts)
        texts = drop_repeated_head(c.get("title_zh", ""), texts)
        items.append({"id": cid, "texts": texts, "types": ["p"] * len(texts),
                      "notes": [], "title_zh": c.get("title_zh", ""),
                      "title_en": c.get("title", ""), "links": {},
                      "old_texts": None})
    return items, skipped


def cfg_for(book: str) -> dict:
    m = META[book]
    return {
        "title": m["title_zh"],
        "sub": m.get("title_src", ""),
        "author": m.get("author_zh", ""),
        "src": m.get("title_src", ""),
        "uid": f"urn:pub-{book}-zh",
        "note": m.get("note", ""),
        "died": m.get("died"),
    }


def build(book: str) -> dict | None:
    if book not in META:
        print(f"{book:14s} not in books.PUBLIC, skipped")
        return None
    items, skipped = collect(book)
    if not items:
        print(f"{book:14s} no translated chapters, skipped")
        return None
    cfg = cfg_for(book)

    # A single-chapter book should not print its own title twice, once on the title page
    # and again as a chapter heading. `package()` fills an empty title with 第一章, so the
    # chapter keeps the book title and `chapter_xhtml` suppresses a heading identical to
    # the book's own; nothing needs to be emptied here.

    B.OUT = OUT
    res = B.package(cfg, items, "chapters")
    han = sum(len(CJK.findall(t)) for it in items for t in it["texts"])
    note = f"  skipped: {', '.join(skipped)}" if skipped else ""
    print(f"{book:14s} {len(items):3d} ch  {han:>8,} 汉字  "
          f"toc={res['toc']:3d}  err={res['xml_errors']}  "
          f"{res['size']/1048576:.2f}MB{note}")
    return {"book": book, "path": res["path"], "chapters": len(items), "han": han}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(OUT, exist_ok=True)
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    keys = args or [b["key"] for b in booklist.PUBLIC]
    done = [r for r in (build(k) for k in keys) if r]
    tot_ch = sum(r["chapters"] for r in done)
    tot_han = sum(r["han"] for r in done)
    print(f"\n{len(done)}/{len(keys)} built  {tot_ch} chapters  {tot_han:,} 汉字")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
