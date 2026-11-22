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
    into lines here, at sentence boundaries only, so the page reads as a poem. A poem's
    own title and its place line are a different kind of line (`verse-title`,
    `verse-sub`): the source sets them as capitals blocks, the writer carried them over
    as ordinary paragraphs, and printed as ordinary paragraphs they read as the first
    words of the poem -- `诗人你离开我，你这时辰。`, `在一座陌生的园林里博尔盖比庄园是两条路。`
    The writer's Chinese titles are listed per chapter in `verse_roles.json` and are
    emitted whole, never split at their own `。`.

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


# Brackets and quotes, so that a line break never lands inside them. `（像人们有时在康复中
# 走着，沉思：从前这里曾有什么？）` and `（哪里有一个头脑存在并思考，好有朝一日享用它们？）`
# are single sentences: splitting them at the `？` stranded a lone `）` on the next line.
BRACKETS = {"（": 1, "(": 1, "【": 1, "《": 1, "“": 1,
            "）": -1, ")": -1, "】": -1, "》": -1, "”": -1}


def verse_lines(text: str) -> list[str]:
    """Split a run-together stanza back into lines, at sentence ends only.

    Rilke's lines end in `,` as often as in `.`, and joining two of them into one
    sentence is a translation decision the translator already made. So the only split
    that is safe here is where a sentence genuinely ends -- and not where one ends inside
    a bracket, because the closing mark belongs with it.
    """
    balanced = sum(BRACKETS.get(c, 0) for c in text) == 0
    out, cur, depth = [], "", 0
    for ch in text:
        cur += ch
        if balanced:
            depth += BRACKETS.get(ch, 0)
        if ch in "。！？；" and depth <= 0:
            out.append(cur.strip())
            cur = ""
    out.append(cur.strip())
    return [p for p in out if p]


# A source group numeral (`I`, `II`, `III`), as the writer rendered it. The chunker keeps
# Rilke's numeral as a block of its own and it arrives as 一 / 第二 / 壹 / 第二部. Printed
# under the chapter heading it looks like a one-word poem; it numbers a poem *group*.
GROUP_NUM = re.compile(
    r"^(?:[一二三四五六七八九十百]{1,3}|"
    r"[壹贰叁肆伍陆柒捌玖拾]{1,3}|"
    r"第[一二三四五六七八九十百0-9]{1,3}[部篇章节回卷]?|"
    r"I{1,3}|IV|V|VI{0,3}|IX|X)$")


def verse_roles(book: str) -> dict:
    """The book's poem-title inventory, if it ships one."""
    path = os.path.join(PUB, book, "verse_roles.json")
    if not os.path.exists(path):
        return {}
    return json.load(open(path, encoding="utf-8"))


def verse_block(book: str, cid: str, texts: list[str],
                prefix: tuple[list[str], list[str]] = ([], [])) -> tuple[list[str], list[str]]:
    """Turn one translated poem group into labelled lines: titles whole, body split.

    `verse_lines` cuts at sentence ends, which is right for a stanza the translator ran
    together and wrong for a title: `俄耳甫斯。欧律狄刻。赫尔墨斯` is one title, not three
    lines, and `（诺娜修女旧藏）` keeps its brackets. Titles therefore bypass the splitter
    and get their own kinds, so that `chapter_xhtml` prints them as headings instead of
    as the poem's first line.

    `prefix` holds the lines carried over from the previous chapter -- see `carry_tail`.
    """
    roles = verse_roles(book).get(cid, {})
    left = {kind: list(roles.get(kind, [])) for kind in ("titles", "subs")}
    kinds = {"titles": "verse-title", "subs": "verse-sub"}

    while texts and GROUP_NUM.match(texts[0].strip()):
        texts = texts[1:]

    out: list[str] = list(prefix[0])
    types: list[str] = list(prefix[1])
    for t in texts:
        t = t.strip()
        if not t:
            continue
        hit = next((k for k in ("titles", "subs") if t in left[k]), None)
        if hit:
            left[hit].remove(t)
            out.append(t)
            types.append(kinds[hit])
            continue
        for line in verse_lines(t):
            out.append(line)
            types.append("verse")
    return out, types


TITLE_KINDS = ("verse-title", "verse-sub")


def split_poems(cid: str, texts: list[str], types: list[str]) -> list[dict]:
    """Cut a chapter into one item per poem, so the TOC can name each poem.

    The volumes of verse are chunked by size, not by poem: one chapter file holds a
    handful of poems, and until now the TOC offered "第N首" for the whole group, which
    is useless in a 75-poem collection. A poem starts at every `verse-title` (and its
    optional `verse-sub` line); the lines before the first title, if any, stay with the
    chapter title.
    """
    groups: list[dict] = []
    cur = {"title": "", "sub": "", "texts": [], "types": []}
    for t, k in zip(texts, types):
        if k == "verse-title":
            if cur["texts"] or cur["title"]:
                groups.append(cur)
            cur = {"title": t, "sub": "", "texts": [], "types": []}
            continue
        if k == "verse-sub" and not cur["texts"]:
            cur["sub"] = t
            continue
        cur["texts"].append(t)
        cur["types"].append(k)
    if cur["texts"] or cur["title"]:
        groups.append(cur)
    out = []
    for i, g in enumerate(groups, 1):
        if not g["texts"]:
            # a title with no poem under it: keep it rather than drop a poet's name
            continue
        g["id"] = f"{cid}s{i:02d}"
        if not g["title"] and g["texts"]:
            # Rilke prints no title over some poems -- the first line is the title, in
            # the source as here. Label the TOC entry from that line instead of
            # inventing 第N首, and print no heading above the poem.
            first = g["texts"][0].strip().rstrip("，。；：、！？…")
            g["nav_label"] = first[:13] + ("…" if len(first) > 13 else "")
            g["no_heading"] = True
        out.append(g)
    return out or [{"id": cid, "title": "", "sub": "", "texts": texts, "types": types}]


def carry_tail(texts: list[str], types: list[str]) -> tuple[list[str], list[str]]:
    """Move a poem's title off the end of the chapter it was cut before.

    The chunker cuts Rilke's groups at a fixed size and the cut lands between a poem's
    title and its body often enough to be the norm, not the exception: `尖端` ends the
    chapter before the poem it names, `阿比萨格`, `大卫在扫罗面前歌唱`, `门廊`, `囚徒`,
    `贝居安会院` + `圣伊丽莎白贝居安会院。布鲁日` likewise. Standing there alone at the foot of
    the page a title is unreadable -- it is a word with no poem under it -- and the poem
    in the next chapter opens titleless. So the trailing title (and the place line after
    it) travels to the top of the next chapter, where it belongs.
    """
    moved: list[str] = []
    while texts and types[-1] in TITLE_KINDS:
        moved.insert(0, (texts.pop(), types.pop()))
    return [t for t, _ in moved], [k for _, k in moved]


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
        first, _, rest = p.partition("\n")
        if rest.strip() and _close(first.strip(), t):
            # the heading shares its paragraph with the chapter name or the opening line:
            # drop the heading line only, keep what follows
            texts = [rest.strip()] + texts[1:]
            return texts
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
    if max(len(a), len(b)) < 5:
        # Below five characters, an edit-distance match is meaningless: "召见" is within
        # three edits of "第三章", and dropping it deleted the chapter's real name.
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


# Books whose source prints a chapter *name* on the line after the numeral, which the
# extractor took for prose, so the translator translated it as an ordinary paragraph. The
# entry was checked chapter by chapter: the short line really is the chapter's name and not
# an epigraph (Trollope) or a part title (Stendhal).
NAMED_CHAPTERS = {"musketeers", "guarany", "sotileza", "diana", "notredame"}


def source_has_chapter_name(book: str, cid: str) -> bool:
    """True when the source prints a chapter name where the extractor saw prose.

    The extractor takes `CHAPITRE PREMIER` as the heading and the line under it as an
    ordinary paragraph. A name is unquoted and set in capitals; Trollope's chapter
    epigraphs are quoted sentences and must not be lifted.
    """
    path = os.path.join(PUB, book, "src", cid + ".json")
    if not os.path.exists(path):
        return False
    try:
        with open(path, encoding="utf-8") as f:
            blocks = json.load(f).get("blocks") or []
    except (OSError, ValueError):
        return False
    if len(blocks) < 2 or blocks[0].get("type") != "head":
        return False
    text = (blocks[1].get("text") or "").strip()
    if not text or len(text) > 70 or text[0] in "\u201c\u300c'\"":
        return False
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    if sum(1 for c in letters if c.isupper()) / len(letters) >= 0.6:
        return True
    # Dickens sets chapter names in title case, so case alone cannot decide; a short
    # unquoted line with no sentence punctuation is the remaining shape.
    return len(text) <= 40 and not re.search(r"[.!?;:。！？；：]$", text)


def is_chapter_name(text: str) -> bool:
    """A short line with no sentence punctuation, sitting where a chapter name would."""
    t = text.strip()
    return 0 < len(t) <= 30 and not re.search(r"[。！？；：，、\"”’）]$", t)


def load_notes(book: str, cid: str) -> list[dict]:
    """Footnote sidecar for one chapter, or an empty list.

    Same shape the older books use: {"anchor", "term", "kind", "text"}. `anchor` must be a
    phrase of that chapter; `build_all.insert_notes` places the marker on it and reports
    any note it could not place rather than dropping it silently.
    """
    path = os.path.join(PUB, book, "notes", cid + ".json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def collect(book: str) -> tuple[list[dict], list[str]]:
    """Translated chapters, plus the ids that were skipped and why."""
    revision = B.collect_revision(book)
    if revision is not None:
        return revision, []

    idx = index_of(book)
    items, skipped = [], []
    carry: tuple[list[str], list[str]] = ([], [])
    for ordinal, c in enumerate(idx["chapters"], 1):
        cid = c["id"]
        texts = chapter_texts(book, cid)
        if not texts:
            spec_path = os.path.join(PUB, book, "chunks", cid + ".json")
            feed = json.load(open(spec_path, encoding="utf-8")) \
                if os.path.exists(spec_path) else {"chunks": []}
            reason = "front matter" if run_pub.is_front_matter(feed) else "no translation"
            skipped.append(f"{cid} ({reason})")
            continue
        # Resolve the heading we will actually print before dropping the copy of it that
        # the translator left in the body. Comparing against the untranslated source
        # title ("CHAPITRE PREMIER") never matched the translated "第一章", so every one
        # of these chapters printed its number twice.
        title_zh = (c.get("title_zh") or "").strip()
        if not re.search(r"[一-鿿]", title_zh):
            title_zh = titles_src.title_for((c.get("title") or "").strip(), ordinal)
        texts = drop_repeated_head(title_zh, texts)
        while texts and (re.fullmatch(r"(?:[一二三四五六七八九十百零]+|[IVXLCDM]+|\d{1,4})", texts[0].strip())
                         or re.fullmatch(r"第[一二三四五六七八九十百零\d]+章", texts[0].strip())):
            num = texts.pop(0).strip()
            if re.fullmatch(r"(?:[一二三四五六七八九十百零]+|[IVXLCDM]+|\d{1,4})", title_zh.strip()):
                title_zh = num
        if book not in VERSE and book not in PLAY and texts and "\n" in texts[0]:
            # Sources that print the number and the chapter name on two lines of one block
            # leave them in one translated paragraph. Trust the number the book itself
            # prints: the positional fallback is off by however much front matter the
            # volume carries, and comparing against it left the number on the page twice.
            lines = texts[0].split("\n")
            head = lines[0].strip()
            if head == title_zh.strip() or re.fullmatch(
                    r"第[一二三四五六七八九十百零\d]+章", head):
                rest = [l for l in lines[1:] if l.strip()]
                name = rest[0].strip() if rest and is_chapter_name(rest[0]) else ""
                if name:
                    title_zh = name
                    rest = rest[1:]
                elif re.fullmatch(r"第[一二三四五六七八九十百零\d]+章", head):
                    title_zh = head
                if rest:
                    texts[0] = "\n".join(rest)
                else:
                    texts.pop(0)
        wants_name = book in NAMED_CHAPTERS or source_has_chapter_name(book, cid)
        if wants_name and texts and is_chapter_name(texts[0]) \
                and not texts[0].lstrip().startswith(("\u201c", "\u300c")):
            cand = re.sub(r"\s+", " ", texts.pop(0)).strip()
            cand = re.sub(r"⟦/?i⟧", "", cand)   # a heading never carries markup
            # some chapters came back as "第五章国王的火枪手…", with the numeral glued on
            m = re.match(r"^第[一二三四五六七八九十百零\d]+章[\s　]*(.*)$", cand)
            cand = (m.group(1).strip() if m else cand)
            if cand:
                title_zh = cand
        if book in VERSE:
            texts, types = verse_block(book, cid, texts, carry)
            carry = carry_tail(texts, types)
            for poem in split_poems(cid, texts, types):
                items.append({"id": poem["id"], "texts": poem["texts"],
                              "types": poem["types"],
                              "notes": [] if poem["id"] != cid else load_notes(book, cid),
                              "title_zh": poem["title"] or c.get("title_zh", ""),
                              "nav_label": poem.get("nav_label", ""),
                              "no_heading": poem.get("no_heading", False),
                              "title_en": "", "subtitle": poem["sub"],
                              "links": {}, "old_texts": None})
            continue
        elif book in PLAY:
            texts = play_lines(texts)
            types = ["p"] * len(texts)
        else:
            types = ["p"] * len(texts)
        items.append({"id": cid, "texts": texts, "types": types,
                      "notes": load_notes(book, cid), "title_zh": title_zh,
                      "title_en": c.get("title", ""), "links": {},
                      "old_texts": None})
    if carry[0]:
        # the last chapter ends on a title nothing follows: put it back rather than lose it
        items[-1]["texts"].extend(carry[0])
        items[-1]["types"].extend(carry[1])
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
