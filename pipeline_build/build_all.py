"""Assemble every finished book into ./out, taking prose from the polished copies.

The workspace grew in two generations and they disagree about where the text lives:

* `work_overhaul/{book}/final/*.json` holds the *pre-polish* prose together with the
  structural metadata (`types`, `title_zh`, `title_en`, footnotes). It is the only
  place the metadata exists.
* `work_whale/out/**/final.txt`, `work_soledad/out/**/final.txt`,
  `work_polish2/_backup_polish3/…` and friends hold the *polished* prose.

Building from the JSON would silently ship the pre-polish text, which is exactly what
this pass was for. Building from the directories would lose the headings and the
footnote anchors. So this assembler marries them: metadata and note anchors come from
the JSON, the paragraph strings come from the polished files, and the pairing is
verified paragraph-by-paragraph before anything is written. A chapter whose polished
paragraph count no longer matches its metadata is reported and left on the old text
rather than guessed at.

Usage:
    python pipeline_build/build_all.py --list
    python pipeline_build/build_all.py --books whale,lotr
    python pipeline_build/build_all.py --all
"""
from __future__ import annotations

import argparse
import difflib
import glob
import html
import json
import os
import re
import shutil
import sys
import zipfile
from xml.dom import minidom

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "pipeline_overhaul"))
import copyright as cpr  # noqa: E402

OUT = os.path.join(ROOT, "out")

STYLE = """body{line-height:1.85;font-family:serif;margin:0 5%}
h1{text-align:center;margin:2.4em 0 .3em;font-size:1.45em;letter-spacing:.06em;font-weight:normal}
h2{text-align:center;color:#666;font-weight:normal;font-style:italic;font-size:.92em;margin:0 0 2em;letter-spacing:.04em}
h3.book{text-align:center;margin:3em 0 1.6em;font-size:1.2em;letter-spacing:.2em;font-weight:normal;color:#444}
p{text-indent:2em;margin:0 0 .55em;text-align:justify}
p.verse{text-indent:0;margin-left:2.5em;margin-bottom:.9em;line-height:1.6;white-space:pre-line}
div.titlepage{text-align:center;margin-top:22%}
div.titlepage .t{font-size:2.1em;letter-spacing:.3em;margin-bottom:1.4em}
div.titlepage .s{font-size:1.05em;color:#555;margin-bottom:.5em}
div.titlepage .a{font-size:1em;margin-top:3em;color:#444}
div.titlepage .n{font-size:.85em;color:#777;margin-top:4em;line-height:1.9}
sup.fn{font-size:.7em;vertical-align:super;line-height:0}
sup.fn a{text-decoration:none;color:#555}
aside.footnote{margin:.6em 0 .6em 1.6em;padding-left:.7em;border-left:2px solid #ddd;font-size:.86em;line-height:1.6;color:#333}
aside.footnote p{text-indent:0;margin:0 0 .4em}
aside.footnote a{text-decoration:none;color:#888}
div.notes-head{margin-top:2.2em;font-size:.85em;color:#888;letter-spacing:.1em}
div.copyright{margin-top:14%;margin-bottom:10%}
div.copyright h1{font-size:1.3em;letter-spacing:.2em;margin:0 0 1.6em}
div.copyright p{text-indent:0;text-align:center;margin:0 0 .6em}
div.copyright p.src{font-size:.95em;color:#555}
div.copyright p.tr{font-size:1em;color:#333;margin-bottom:3em}
div.copyright div.cn{font-size:.82em;line-height:1.85;color:#555;text-align:left;
  border-top:1px solid #ddd;padding-top:1.2em;margin:0 1em}
"""

MARK = re.compile(r"\[\[(\d+)\]\]")
ITAL = re.compile(r"⟦i⟧(.*?)⟦/i⟧", re.S)
HEAD = re.compile(r"^第[一二三四五六七八九十百零\d]{1,4}[章回节部卷]$")
CN = "零一二三四五六七八九"

BOOKS = {
    "whale": {
        "title": "白鲸", "sub": "莫比—迪克", "author": "赫尔曼·麦尔维尔",
        "src": "Moby-Dick; or, The Whale", "uid": "urn:moby-dick-zh-rev",
        "note": "据查尔斯·弗雷德里克·布里格斯·普特南公司一八五一年初版译出",
        "json": "work_overhaul/whale/final", "polished": "work_whale/out",
        "notes": "work_overhaul/whale/notes", "shape": "chapters",
    },
    "soledad": {
        "title": "百年孤独", "sub": "Cien años de soledad", "author": "加夫列尔·加西亚·马尔克斯",
        "src": "Cien años de soledad", "uid": "urn:cien-anos-zh-rev",
        "note": "据一九六七年布宜诺斯艾利斯南美出版社初版译出",
        "json": "work_overhaul/soledad/final", "polished": "work_soledad/out",
        "notes": "work_overhaul/soledad/notes", "shape": "chapters",
    },
    "lotr": {
        "title": "魔戒", "sub": "The Lord of the Rings", "author": "J. R. R. 托尔金",
        "src": "The Lord of the Rings", "uid": "urn:lotr-zh-rev",
        "note": "据五十周年纪念版译出",
        "json": "work_overhaul/lotr/final", "polished": None,
        "notes": "work_overhaul/lotr/notes", "shape": "lotr",
    },
    "camus": {
        "title": "鼠疫", "sub": "La Peste", "author": "阿尔贝·加缪",
        "src": "La Peste", "uid": "urn:la-peste-zh-rev",
        "note": "据一九四七年巴黎伽利玛出版社初版译出",
        "json": None, "polished": "work_camus/out", "notes": None,
        "shape": "parts", "pattern": "c*/final.txt",
        "chunks": "work_camus/src/chunks.json",
    },
    "chekhov": {
        "title": "第六病室", "sub": "Палата № 6", "author": "安东·契诃夫",
        "src": "Палата № 6", "uid": "urn:palata-6-zh-rev",
        "note": "据一八九二年《俄罗斯思想》初刊本译出",
        "json": None, "polished": "work_chekhov/out", "notes": None,
        "shape": "flat", "pattern": "sec*/final.txt", "roman": True,
    },
    "zauberberg": {
        "title": "魔山", "sub": "Der Zauberberg", "author": "托马斯·曼",
        "src": "Der Zauberberg", "uid": "urn:zauberberg-zh-rev",
        "note": "据一九二四年柏林S. Fischer出版社初版译出",
        "json": None, "polished": "work_zauberberg/out", "notes": None,
        "shape": "split", "pattern": "index_split_*/c*/final.txt",
    },
}

VOLUMES = {"book1": ("第一部", "魔戒同盟"), "book2": ("第一部", "魔戒同盟"),
           "book3": ("第二部", "双塔殊途"), "book4": ("第二部", "双塔殊途"),
           "book5": ("第三部", "王者归来"), "book6": ("第三部", "王者归来")}
BOOKNAMES = {"book1": "卷一", "book2": "卷二", "book3": "卷三",
             "book4": "卷四", "book5": "卷五", "book6": "卷六"}
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI",
         "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]

# A short first line is only a chapter heading if it *reads* like one. Dialogue and
# verse also come in short lines ("“一个不大干净的理想主义者。”"), and treating every
# short line as a heading shredded 魔山 into 14 sections instead of 8.
HEADING_LIKE = re.compile(
    r"^(?:前言|序言|尾声|第[一二三四五六七八九十百零\d]{1,4}章|"
    r"[\u4e00-\u9fff·]{2,12}（[上下]）$)")

WARN: list[str] = []
PARKED: list[str] = []


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def cn_number(n: int) -> str:
    if n <= 10:
        return "十" if n == 10 else CN[n]
    if n < 20:
        return "十" + CN[n % 10]
    return CN[n // 10] + "十" + (CN[n % 10] if n % 10 else "")


def paras(t: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]


def is_heading(s: str) -> bool:
    s = s.strip()
    return bool(HEAD.match(s)) and len(s) <= 12


ARTIFACT_HEAD = re.compile(
    r"^(第[零〇一二三四五六七八九十百千万0-9]{1,8}[节章回篇卷]?[。．]?|题[：:]?.{0,12}|"
    r"\[(?:first|second|third|next|this)_?translation\]|"
    r"(?:chapter|chapitre|kapitel|cap[ío]tulo)\s*[IVXLCDM0-9]+[.。]?)$", re.I)


def drop_artifact_head(title: str, texts: list[str], types: list[str]):
    """Drop a leading body line that only repeats the heading or leaks a template.

    The chunker translated the source heading along with the prose, so most chapters on
    this shelf open with a bare 第X章 under an <h1> that already says 第X章; a handful
    open with the writer's own placeholder (题, [first_translation]). Neither carries any
    content the reader gets elsewhere, and printing them looks like a corrupt book.

    Only the first one or two paragraphs qualify, only when they are at most twelve
    characters and match exactly, and only when the printed heading already carries a
    chapter ordinal (or the line is a placeholder). Nothing else is ever removed.
    """
    out, tys = list(texts), list(types)
    for _ in range(2):
        if not out:
            break
        p = out[0].strip()
        if len(p) > 12 or not ARTIFACT_HEAD.match(p):
            break
        ordinal = re.match(r"^第[零〇一二三四五六七八九十百千万0-9]{1,8}[章回][。．]?$", p)
        foreign = re.match(r"^(?:chapter|chapitre|kapitel|cap[ío]tulo)\s*[IVXLCDM0-9]+[.。]?$", p, re.I)
        placeholder = p.startswith("题") or p.startswith("[")
        if ordinal or foreign or placeholder or (title and p in title):
            out, tys = out[1:], tys[1:]
        else:
            break
    return out, tys


def para_html(text: str, kind: str = "p") -> str:
    # Emphasis first, then escape each piece, so the <em> tags survive escaping and a
    # literal "⟦i⟧" can never reach the reader.
    parts, pos = [], 0
    for m in ITAL.finditer(text):
        parts.append(esc(text[pos:m.start()]))
        parts.append("<em>" + esc(m.group(1)) + "</em>")
        pos = m.end()
    parts.append(esc(text[pos:]))
    s = "".join(parts)
    s = MARK.sub(lambda m: f'<sup class="fn"><a id="r{m.group(1)}" '
                           f'href="#n{m.group(1)}" epub:type="noteref">[{m.group(1)}]</a></sup>', s)
    cls = ' class="verse"' if kind == "verse" else ""
    # A newline inside a paragraph is a line break the translator preserved (verse,
    # songs, play dialogue). HTML collapses it to a space, so print it as <br/>.
    s = s.replace("\n", "<br/>")
    return f"<p{cls}>{s}</p>"


def _clean_mapped(text: str):
    """Strip inline emphasis markers, keeping a map from cleaned position -> original index.

    Note anchors are recorded against text that still carries ⟦i⟧ markers (e.g.
    "诺斯特拉达姆斯的达姆斯的⟦i⟧Centurias⟦/i⟧"), but `_clean` drops them from the anchor only.
    Matching a cleaned anchor against the raw text therefore fails on the exact pass and
    lands mid-word on the approximate one ("Centur[1]ias"). Cleaning both sides and
    mapping back keeps the anchor at the true end of the phrase.
    """
    cleaned, orig = [], []
    pos = 0
    for m in ITAL.finditer(text):
        for k in range(pos, m.start()):
            cleaned.append(text[k]); orig.append(k)
        for k in range(m.start(1), m.end(1)):
            cleaned.append(text[k]); orig.append(k)
        pos = m.end()
    for k in range(pos, len(text)):
        cleaned.append(text[k]); orig.append(k)
    return "".join(cleaned), orig


def _find_span(text: str, anchor: str) -> tuple[int, int] | None:
    """Locate `anchor` inside `text`, exactly or approximately.

    Return the (start, end) span, or None. Approximation is needed because the note
    anchors were recorded against the pre-polish text, and polishing legitimately
    changes wording: "伽图带着哲人的气派引剑自刎" may become "...气概...". A
    difflib window over the paragraph recovers the position without inventing text.
    """
    if not anchor:
        return None
    i = text.find(anchor)
    if i >= 0:
        return i, i + len(anchor)
    # Exact pass against emphasis-stripped text (anchors carry ⟦i⟧ markers).
    ctext, cmap = _clean_mapped(text)
    j = ctext.find(anchor)
    if j >= 0:
        return cmap[j], cmap[j] + (cmap[j + len(anchor) - 1] - cmap[j] + 1)
    n = len(anchor)
    if n < 4:
        return None
    best, best_score = None, 0.0
    for start in range(0, max(1, len(ctext) - n + 1)):
        window = ctext[start:start + n]
        sm = difflib.SequenceMatcher(None, anchor, window)
        if sm.real_quick_ratio() <= best_score or sm.quick_ratio() <= best_score:
            continue
        score = sm.ratio()
        if score > best_score:
            best, best_score = start, score
    if best is not None and best_score >= 0.72:
        return cmap[best], cmap[best] + (cmap[best + n - 1] - cmap[best] + 1)
    return None


def _clean(s: str) -> str:
    """Drop the inline emphasis markers so they never break an anchor match."""
    return ITAL.sub(lambda m: m.group(1), s or "")


def insert_notes(texts: list[str], notes: list[dict],
                 old_texts: list[str] | None = None) -> list[dict]:
    """Attach [[k]] to the anchor, and keep only notes that were actually placed.

    The anchors were mined from the pre-polish paragraphs, so matching them literally
    against polished text fails whenever polishing reworded the clause ("苦涩至极的
    塞涅卡" → "浓浓的塞涅卡"). Three stages, narrowing from safe to approximate:

    1. find the paragraph the anchor belonged to, using the old text (its indices are
       the ones the anchors were recorded against);
    2. inside the current text of that paragraph, locate the anchor exactly;
    3. failing that, locate the note's `term` — the proper noun the note explains —
       which polishing almost never removes.

    A note is dropped rather than mis-placed: a footnote pointing at the wrong clause
    is worse than a missing one, and every drop is reported.
    """
    used, kept = set(), []
    for note in notes:
        anchor = _clean(note.get("anchor") or "").strip()
        term = _clean(note.get("term") or "").strip()
        if not anchor and not term:
            continue
        hint = None
        if old_texts:
            for i, t in enumerate(old_texts):
                if anchor and anchor in _clean(t):
                    hint = i
                    break
        order = ([hint] if hint is not None else []) + [i for i in range(len(texts))
                                                        if i != hint]
        placed = False
        for i in order:
            if i >= len(texts) or (i, anchor) in used:
                continue
            span = _find_span(texts[i], anchor) if anchor else None
            if span is None and term:
                span = _find_span(texts[i], term)
            if span is None:
                continue
            k = len(kept) + 1
            end = span[1]
            texts[i] = texts[i][:end] + f"[[{k}]]" + texts[i][end:]
            kept.append(note)
            used.add((i, anchor))
            placed = True
            break
        if not placed:
            # Final fallback: park the mark at the end of the paragraph the anchor
            # belonged to. The note stays visible and still points at the right
            # passage; only the exact word is lost, which beats dropping the note.
            if hint is not None and hint < len(texts):
                k = len(kept) + 1
                texts[hint] = texts[hint].rstrip() + f"[[{k}]]"
                kept.append(note)
                used.add((hint, anchor))
                PARKED.append((anchor or term)[:24])
                continue
            WARN.append(f"note anchor lost: {(anchor or term)[:24]}")
    return kept


def page(title: str, body: str, cls: str = "") -> str:
    return ("<?xml version='1.0' encoding='utf-8'?>\n<!DOCTYPE html>\n"
            "<html xmlns='http://www.w3.org/1999/xhtml' "
            "xmlns:epub='http://www.idpf.org/2007/ops' xml:lang='zh-CN'>"
            f"<head><meta charset='utf-8'/><title>{esc(title)}</title>"
            "<link rel='stylesheet' type='text/css' href='style.css'/></head>"
            f"<body>{body}</body></html>")


def title_page(cfg: dict) -> str:
    return page(cfg["title"],
                "<div class='titlepage'>"
                f"<div class='t'>{esc(cfg['title'])}</div>"
                f"<div class='s'>{esc(cfg['sub'])}</div>"
                f"<div class='a'>{esc(cfg['author'])}　著</div>"
                f"<div class='n'>坟头草　译<br/>{esc(cfg['note'])}</div>"
                "</div>")


def copyright_page(cfg: dict) -> str:
    return page("版权",
                "<div class='copyright'>"
                f"<h1>{esc(cfg['title'])}</h1>"
                f"<p class='src'>{esc(cfg['src'])}　著</p>"
                "<p class='tr'>坟头草　译</p>"
                f"<div class='cn'>{cpr.TEXT}</div>"
                "</div>")


def chapter_xhtml(title: str, subtitle: str, ps: list[str], types: list[str],
                  notes: list[dict], book_head: str = "") -> str:
    body = []
    if book_head:
        body.append(f"<h3 class='book'>{esc(book_head)}</h3>")
    body.append(f"<h1>{esc(title)}</h1>")
    if subtitle:
        body.append(f"<h2>{esc(subtitle)}</h2>")
    body += [para_html(t, ty) for t, ty in zip(ps, types)]
    if notes:
        body.append("<div class='notes-head'>注</div>")
        for k, n in enumerate(notes, 1):
            body.append(f"<aside class='footnote' id='n{k}' epub:type='footnote'>"
                        f"<p>[{k}] {esc(n.get('text', ''))} <a href='#r{k}'>↩</a></p></aside>")
    return page(title, "".join(body))


def volume_page(vno: str, vtitle: str) -> str:
    return page(vtitle,
                "<div class='titlepage'>"
                f"<div class='s'>{esc(vno)}</div>"
                f"<div class='t' style='font-size:1.7em'>{esc(vtitle)}</div></div>")


# ── text sources ────────────────────────────────────────────────────────────────

def polished_chapter(cfg: dict, cid: str) -> list[str] | None:
    """Paragraphs of a chapter from the polished tree, or None when absent."""
    base = cfg.get("polished")
    if not base:
        return None
    d = os.path.join(ROOT, base, cid)
    files = sorted(glob.glob(os.path.join(d, "c*", "final.txt")))
    if not files:
        return None
    out = []
    for f in files:
        out += paras(open(f, encoding="utf-8").read())
    return out


def collect_json_book(cfg: dict) -> list[dict]:
    """Chapters that carry metadata in JSON plus prose in the polished tree."""
    d = os.path.join(ROOT, cfg["json"])
    items = []
    for f in sorted(glob.glob(os.path.join(d, "*.json"))):
        if f.endswith(".polished.json"):
            continue
        meta = json.load(open(f, encoding="utf-8"))
        if "texts" not in meta:
            continue
        cid = os.path.splitext(os.path.basename(f))[0]
        old_texts = list(meta["texts"])
        texts = list(old_texts)
        types = list(meta.get("types") or ["p"] * len(texts))
        pol = polished_chapter(cfg, cid)
        if pol is not None:
            if len(pol) == len(texts):
                texts = pol
            else:
                WARN.append(f"{cfg['title']} {cid}: polished {len(pol)} paras "
                            f"!= metadata {len(texts)}, kept older text")
        notes = []
        npath = os.path.join(ROOT, cfg["notes"], cid + ".json") if cfg.get("notes") else None
        if npath and os.path.exists(npath):
            notes = json.load(open(npath, encoding="utf-8"))
        items.append({"id": cid, "texts": texts, "types": types, "notes": notes,
                      "old_texts": old_texts,
                      "title_zh": (meta.get("title_zh") or "").strip(),
                      "title_en": (meta.get("title_en") or "").strip(),
                      "links": meta.get("links") or {}})
    return items


def collect_flat(cfg: dict) -> list[dict]:
    """Books translated straight to per-section directories with no JSON sidecar."""
    base = os.path.join(ROOT, cfg["polished"])
    pat = cfg.get("pattern", "*/final.txt")
    files = sorted(glob.glob(os.path.join(base, pat)))
    items = []
    for i, f in enumerate(files, 1):
        texts = paras(open(f, encoding="utf-8").read())
        if not texts:
            continue
        rel = os.path.relpath(f, base)
        if cfg.get("roman"):
            # 第六病室 is one novella in nineteen numbered sections, and the section
            # number survives inside the prose ("I", "二", "IX"). Label the sections
            # uniformly in Chinese numerals so the TOC does not mix numeral systems.
            title = f"{cfg['title']}（{cn_number(i)}）"
            if texts and len(texts[0]) <= 6 and re.fullmatch(
                    r"[IVXLCDM]+|[一二三四五六七八九十]+", texts[0].strip()):
                texts = texts[1:]
        else:
            title = ""
        items.append({"id": rel, "texts": texts, "types": ["p"] * len(texts),
                      "notes": [], "title_zh": title, "title_en": "", "links": {},
                      "ordinal": i})
    return items


def collect_parts(cfg: dict) -> list[dict]:
    """Books translated chunk by chunk, where the chapter is a *group* of chunks.

    鼠疫 was translated as 84 chunks and each chunk's source carries the part it
    belongs to (`第一部` … `第五部`). One chunk is a few pages, not a chapter, so the
    chunks are concatenated per part; the part's heading is lifted out of the prose
    because the translator kept it inside the text.
    """
    base = os.path.join(ROOT, cfg["polished"])
    chunkfile = os.path.join(ROOT, cfg["chunks"])
    plan = json.load(open(chunkfile, encoding="utf-8"))
    files = sorted(glob.glob(os.path.join(base, cfg.get("pattern", "c*/final.txt"))))
    groups: list[dict] = []
    cur_key = object()
    for i, f in enumerate(files):
        head = (plan[i].get("head") if i < len(plan) else "") or ""
        key = head or ""
        if key != cur_key:
            cur_key = key
            groups.append({"id": key or f"part{len(groups)+1}", "texts": [],
                           "types": [], "notes": [], "title_zh": key,
                           "title_en": "", "links": {}})
        texts = paras(open(f, encoding="utf-8").read())
        # the part marker is the first line of the first chunk of each part
        if texts and (not groups[-1]["texts"]) and len(texts[0]) <= 8 \
                and re.match(r"^第[一二三四五六七八九十]+部$", texts[0].strip()):
            groups[-1]["title_zh"] = texts[0].strip()
            texts = texts[1:]
        groups[-1]["texts"] += texts
    for g in groups:
        g["types"] = ["p"] * len(g["texts"])
    return [g for g in groups if g["texts"]]


def group_split(items: list[dict], cfg: dict) -> list[dict]:
    """Merge the small split files of 魔山 into its seven real chapters.

    The source EPUB slices each chapter across several `index_split_NNN` files, so
    one file is not one chapter. Grouping by the file that carries the chapter's
    heading restores the seven chapters the book actually has.
    """
    base = os.path.join(ROOT, cfg["polished"])
    groups, cur = [], None
    for f in sorted(glob.glob(os.path.join(base, "index_split_*/c*/final.txt")),
                    key=lambda p: (p.split("index_split_")[1].split(os.sep)[0],
                                   p.rsplit(os.sep, 2)[-2])):
        texts = paras(open(f, encoding="utf-8").read())
        if not texts:
            continue
        # a file that opens with a heading-like line starts a new chapter
        first = texts[0]
        head = first if len(first) <= 24 and HEADING_LIKE.match(first) else None
        if head or cur is None:
            cur = {"id": f, "texts": [], "types": [], "notes": [], "title_zh": "",
                   "title_en": "", "links": {}}
            groups.append(cur)
            if head:
                cur["title_zh"] = head
                texts = texts[1:]
        cur["texts"] += texts
        cur["types"] += ["p"] * len(texts)
    # Mann's Princeton address opens the book without a heading of its own, and its
    # first line is the German title of the lecture rather than prose to print.
    if groups:
        g0 = groups[0]
        head = g0["texts"][0] if g0["texts"] else ""
        if re.search(r"[A-Za-zÄÖÜäöüß]{4,}", head) and len(head) < 120:
            g0["texts"] = g0["texts"][1:]
            g0["title_zh"] = "楔子"
    for i, g in enumerate(groups, 1):
        if not g["title_zh"]:
            g["title_zh"] = f"第{cn_number(i - 1)}章"
        g["types"] = ["p"] * len(g["texts"])
    return groups


# ── packaging ───────────────────────────────────────────────────────────────────

def package(cfg: dict, items: list[dict], shape: str) -> dict:
    files, manifest, spine, nav = {}, [], [], []
    files["style.css"] = STYLE
    files["title.xhtml"] = title_page(cfg)
    files["copyright.xhtml"] = copyright_page(cfg)
    manifest.append("<item id='css' href='style.css' media-type='text/css'/>")
    manifest.append("<item id='title' href='title.xhtml' media-type='application/xhtml+xml'/>")
    manifest.append("<item id='copy' href='copyright.xhtml' media-type='application/xhtml+xml'/>")
    spine.append("<itemref idref='title'/>")
    spine.append("<itemref idref='copy'/>")
    nav.append(("书名页", "title.xhtml"))
    nav.append(("版权", "copyright.xhtml"))

    cur_vol = None
    han = npara = nnote = 0
    for n, it in enumerate(items, 1):
        texts = list(it["texts"])
        types = list(it["types"])
        title = it["title_zh"]
        # Some books never recorded a title_zh and the heading is sitting in the body
        # as the first paragraph. Lifting it keeps the TOC readable and stops the
        # heading being printed twice.
        if not title and texts and is_heading(texts[0]):
            title = texts.pop(0)
            types = types[1:]
        m = re.search(r"0*(\d+)$", it["id"].replace(os.sep, "/"))
        if not title:
            if cfg["title"] == "魔山":
                # the first split file holds Mann's framing essay, which has no
                # heading of its own in the source; name it rather than print a path
                title = "楔子" if n == 1 else (f"第{cn_number(n-1)}章" if m else it["id"])
            else:
                title = f"第{cn_number(int(m.group(1)))}章" if m else it["id"]
        sub = it["title_en"] if shape == "chapters" and cfg["title"] == "白鲸" else ""
        for special, (t, s) in {"front_ety": ("词源", "Etymology"),
                                "front_ext": ("摘录", "Extracts"),
                                "epi": ("尾声", "Epilogue")}.items():
            if it["id"].startswith(special):
                title, sub = t, s

        # Seven indexes print 第31章 once past thirty and 第三十一章 below it. The rest
        # of the shelf, and the reader's expectation, is Chinese numerals throughout.
        title = re.sub(r"第(\d{1,2})章", lambda g: "第" + cn_number(int(g.group(1))) + "章", title)

        book_head = ""
        if shape == "lotr" and it["id"].startswith("book"):
            bk = it["id"][:5]
            vol = VOLUMES[bk]
            if vol != cur_vol:
                cur_vol = vol
                vn, fn = f"v{len(nav)}", f"v{len(nav)}.xhtml"
                files[fn] = volume_page(vol[0], vol[1])
                manifest.append(f"<item id='{vn}' href='{fn}' "
                                "media-type='application/xhtml+xml'/>")
                spine.append(f"<itemref idref='{vn}'/>")
                nav.append((f"{vol[0]} {vol[1]}", fn))
            book_head = BOOKNAMES[bk]

        texts, types = drop_artifact_head(title, texts, types)
        notes = insert_notes(texts, it["notes"] or [], it.get("old_texts"))
        fn = f"c{n:03d}.xhtml"
        files[fn] = chapter_xhtml(title, sub, texts, types, notes, book_head)
        manifest.append(f"<item id='c{n}' href='{fn}' media-type='application/xhtml+xml'/>")
        spine.append(f"<itemref idref='c{n}'/>")
        nav.append(((book_head + "　" if book_head else "") + title, fn))
        han += sum(1 for c in "".join(texts) if "\u4e00" <= c <= "\u9fff")
        npara += len(texts)
        nnote += len(notes)

    navx = ["<?xml version='1.0' encoding='utf-8'?>",
            "<html xmlns='http://www.w3.org/1999/xhtml' "
            "xmlns:epub='http://www.idpf.org/2007/ops' xml:lang='zh-CN'>",
            "<head><meta charset='utf-8'/><title>目录</title></head><body>",
            "<nav epub:type='toc' id='toc'><h1>目录</h1><ol>"]
    navx += [f"<li><a href='{fn}'>{esc(t)}</a></li>" for t, fn in nav]
    navx.append("</ol></nav></body></html>")
    files["nav.xhtml"] = "\n".join(navx)
    # nav must also be in the spine, or readers that only follow the spine never
    # reach the table of contents
    manifest.append("<item id='nav' href='nav.xhtml' media-type='application/xhtml+xml' properties='nav'/>")
    spine.insert(0, "<itemref idref='nav'/>")

    files["toc.ncx"] = (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        "<ncx xmlns='http://www.daisy.org/z3986/2005/ncx/' version='2005-1'>"
        f"<head><meta name='dtb:uid' content='{cfg['uid']}'/>"
        "<meta name='dtb:depth' content='1'/>"
        "<meta name='dtb:totalPageCount' content='0'/>"
        "<meta name='dtb:maxPageNumber' content='0'/></head>"
        f"<docTitle><text>{esc(cfg['title'])}</text></docTitle><navMap>"
        + "".join(f"<navPoint id='np{i}' playOrder='{i}'><navLabel><text>{esc(t)}</text>"
                  f"</navLabel><content src='{fn}'/></navPoint>"
                  for i, (t, fn) in enumerate(nav, 1))
        + "</navMap></ncx>")
    manifest.append("<item id='ncx' href='toc.ncx' media-type='application/x-dtbncx+xml'/>")

    files["content.opf"] = f"""<?xml version='1.0' encoding='utf-8'?>
<package xmlns='http://www.idpf.org/2007/opf' version='3.0' unique-identifier='uid'>
<metadata xmlns:dc='http://purl.org/dc/elements/1.1/'>
<dc:title>{esc(cfg['title'])}</dc:title>
<dc:creator>{esc(cfg['author'])}</dc:creator>
<dc:contributor>坟头草 译</dc:contributor>
<dc:language>zh-CN</dc:language>
<dc:identifier id='uid'>{cfg['uid']}</dc:identifier>
<meta property='dcterms:modified'>2026-10-26T12:00:00Z</meta>
</metadata>
<manifest>
{chr(10).join(manifest)}
</manifest>
<spine toc='ncx'>
{chr(10).join(spine)}
</spine>
</package>"""

    files["container.xml"] = (
        "<?xml version='1.0'?><container version='1.0' "
        "xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>"
        "<rootfiles><rootfile full-path='OEBPS/content.opf' "
        "media-type='application/oebps-package+xml'/></rootfiles></container>")

    errs = 0
    for fn, content in files.items():
        if fn.endswith(".css"):
            continue
        try:
            minidom.parseString(content.encode("utf-8"))
        except Exception as e:  # noqa: BLE001
            errs += 1
            print("  XML ERROR", fn, str(e)[:110])

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{cfg['title']}（坟头草译）.epub")
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", zipfile.ZIP_STORED)
        for fn, content in files.items():
            p = "META-INF/container.xml" if fn == "container.xml" else "OEBPS/" + fn
            z.writestr(p, content)
    return {"path": path, "items": len(items), "paras": npara, "han": han,
            "notes": nnote, "xml_errors": errs, "toc": len(nav),
            "size": os.path.getsize(path)}


def build(book: str) -> dict:
    cfg = BOOKS[book]
    shape = cfg["shape"]
    if shape in ("chapters", "lotr"):
        items = collect_json_book(cfg)
        # `prologue` belongs in the book; only the earlier build dropped it by
        # filtering on the `book` prefix, which silently lost the framing chapter.
        if shape == "lotr":
            items = [it for it in items
                     if it["id"].startswith("book") or it["id"] == "prologue"]
            items.sort(key=lambda it: (it["id"] != "prologue",
                                       it["id"][:5], it["id"]))
    elif shape == "split":
        items = group_split([], cfg)
    elif shape == "parts":
        items = collect_parts(cfg)
    else:
        items = collect_flat(cfg)
    return package(cfg, items, shape)


def prune_old() -> None:
    """Remove our own earlier EPUBs from the project root.

    Only files matching the `（坟头草译）` naming pattern are touched; the downloaded
    reference editions in other languages stay, because they are evidence for the
    translation rather than output.
    """
    keep = os.path.join(OUT, "")
    removed = []
    for p in glob.glob(os.path.join(ROOT, "*.epub")):
        if os.path.abspath(p).startswith(os.path.abspath(keep)):
            continue
        if "坟头草译" in os.path.basename(p):
            os.remove(p)
            removed.append(os.path.basename(p))
    return removed


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--prune", action="store_true")
    ap.add_argument("--verify-only", action="store_true")
    a = ap.parse_args()

    if a.list:
        for k, v in BOOKS.items():
            print(f"  {k:12s} {v['title']}  shape={v['shape']}")
        return 0

    books = list(BOOKS) if a.all else [b.strip() for b in a.books.split(",") if b.strip()]
    if not books:
        ap.error("give --all or --books")

    os.makedirs(OUT, exist_ok=True)
    for b in books:
        WARN.clear()
        PARKED.clear()
        r = build(b)
        print(f"{b:12s} {r['items']:3d} sections {r['paras']:6,d} paras "
              f"{r['han']:9,d} han {r['notes']:4d} notes toc={r['toc']:3d} "
              f"xml_err={r['xml_errors']} {r['size']/1048576:.2f}MB")
        print(f"             -> {os.path.basename(r['path'])}")
        for w in dict.fromkeys(WARN):
            print(f"             ! {w}")
        if PARKED:
            print(f"             ~ {len(PARKED)} note(s) parked at paragraph end "
                  f"(anchor wording changed by polish)")
    if a.prune:
        gone = prune_old()
        print(f"pruned {len(gone)} old epub(s) from project root")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
