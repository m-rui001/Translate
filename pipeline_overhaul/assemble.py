"""Build the three EPUBs (EPUB 3, with real footnotes).

Footnotes are <aside epub:type="footnote"> at the end of each chapter, linked
from a superscript in the text. That is the form readers expect: tap the mark,
read the note, tap back.
"""
from __future__ import annotations

import argparse
import html
import os
import re
import sys
import zipfile
from xml.dom import minidom

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402
import copyright as cpr  # noqa: E402

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

BOOKS = {
    "whale": {"title": "白鲸", "sub": "莫比—迪克", "author": "赫尔曼·麦尔维尔",
              "src": "Moby-Dick; or, The Whale", "uid": "urn:moby-dick-zh-rev",
              "epub": "E:/Translate/白鲸（坟头草译）.epub",
              "note": "据查尔斯·弗雷德里克·布里格斯·普特南公司一八五一年初版译出"},
    "soledad": {"title": "百年孤独", "sub": "Cien años de soledad", "author": "加夫列尔·加西亚·马尔克斯",
                "src": "Cien años de soledad", "uid": "urn:cien-anos-zh-rev",
                "epub": "E:/Translate/百年孤独（坟头草译）.epub",
                "note": "据一九六七年布宜诺斯艾利斯南美出版社初版译出"},
    "lotr": {"title": "魔戒", "sub": "The Lord of the Rings", "author": "J. R. R. 托尔金",
             "src": "The Lord of the Rings", "uid": "urn:lotr-zh-rev",
             "epub": "E:/Translate/魔戒（坟头草译）.epub",
             "note": "据五十周年纪念版译出"},
}

VOLUMES = {"book1": ("第一部", "魔戒同盟"), "book2": ("第一部", "魔戒同盟"),
           "book3": ("第二部", "双塔殊途"), "book4": ("第二部", "双塔殊途"),
           "book5": ("第三部", "王者归来"), "book6": ("第三部", "王者归来")}
BOOKNAMES = {"book1": "卷一", "book2": "卷二", "book3": "卷三",
             "book4": "卷四", "book5": "卷五", "book6": "卷六"}

MARK = re.compile(r"\[\[(\d+)\]\]")
ITAL = re.compile(r"⟦i⟧(.*?)⟦/i⟧", re.S)
HEAD = re.compile(r"^第[一二三四五六七八九十百零\d]{1,4}[章回节部卷]$")


def is_heading(s: str) -> bool:
    """A chapter heading that ended up in the body instead of title_zh.

    Deliberately narrow: a bare 第N章 / 第N回 line and nothing else. Anything
    longer is prose and must stay where it is.
    """
    s = s.strip()
    return bool(HEAD.match(s)) and len(s) <= 12


CN_DIGITS = "零一二三四五六七八九"


def cn_number(n: int) -> str:
    if n <= 10:
        return "十" if n == 10 else CN_DIGITS[n]
    if n < 20:
        return "十" + CN_DIGITS[n % 10]
    return CN_DIGITS[n // 10] + "十" + (CN_DIGITS[n % 10] if n % 10 else "")


def cn_chapter(cid: str) -> str | None:
    """`capitulo016` → 第十六章, for a chapter whose heading never made it in.

    Only a fallback for a heading the source simply does not have. Nothing is
    invented beyond the ordinal the filename already carries.
    """
    m = re.fullmatch(r"capitulo0*(\d+)", cid)
    return f"第{cn_number(int(m.group(1)))}章" if m else None


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def para_html(text: str, kind: str = "p") -> str:
    # emphasis first, then escape each piece, so the <em> tags survive escaping
    parts = []
    pos = 0
    for m in ITAL.finditer(text):
        parts.append(esc(text[pos:m.start()]))
        parts.append("<em>" + esc(m.group(1)) + "</em>")
        pos = m.end()
    parts.append(esc(text[pos:]))
    s = "".join(parts)
    s = MARK.sub(lambda m: f'<sup class="fn"><a id="r{m.group(1)}" href="#n{m.group(1)}" '
                           f'epub:type="noteref">[{m.group(1)}]</a></sup>', s)
    cls = ' class="verse"' if kind == "verse" else ""
    return f"<p{cls}>{s}</p>"


def insert_notes(texts: list[str], notes: list[dict]) -> list[dict]:
    """Attach [[k]] right after each anchor's first occurrence.

    Several notes may legitimately sit in the same paragraph, so the dedupe is
    per (paragraph, anchor) rather than per paragraph -- otherwise every second
    note in a paragraph was silently dropped.
    """
    used, kept = set(), []
    for note in notes:
        a = note["anchor"]
        for i, t in enumerate(texts):
            if a in t and (i, a) not in used:
                k = len(kept) + 1
                texts[i] = t.replace(a, a + f"[[{k}]]", 1)
                kept.append(note)
                used.add((i, a))
                break
    return kept


def chapter_xhtml(title: str, subtitle: str, paras: list[str], types: list[str],
                  notes: list[dict], book_head: str = "") -> str:
    body = []
    if book_head:
        body.append(f"<h3 class='book'>{esc(book_head)}</h3>")
    body.append(f"<h1>{esc(title)}</h1>")
    if subtitle:
        body.append(f"<h2>{esc(subtitle)}</h2>")
    body += [para_html(t, ty) for t, ty in zip(paras, types)]
    if notes:
        body.append("<div class='notes-head'>注</div>")
        for k, n in enumerate(notes, 1):
            body.append(f"<aside class='footnote' id='n{k}' epub:type='footnote'>"
                        f"<p>[{k}] {esc(n['text'])} <a href='#r{k}'>↩</a></p></aside>")
    return ("<?xml version='1.0' encoding='utf-8'?>\n<!DOCTYPE html>\n"
            "<html xmlns='http://www.w3.org/1999/xhtml' "
            "xmlns:epub='http://www.idpf.org/2007/ops' xml:lang='zh-CN'>"
            f"<head><meta charset='utf-8'/><title>{esc(title)}</title>"
            "<link rel='stylesheet' type='text/css' href='style.css'/></head><body>"
            + "".join(body) + "</body></html>")


def title_page(cfg: dict) -> str:
    return ("<?xml version='1.0' encoding='utf-8'?>\n<!DOCTYPE html>\n"
            "<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='zh-CN'>"
            f"<head><meta charset='utf-8'/><title>{esc(cfg['title'])}</title>"
            "<link rel='stylesheet' type='text/css' href='style.css'/></head><body>"
            "<div class='titlepage'>"
            f"<div class='t'>{esc(cfg['title'])}</div>"
            f"<div class='s'>{esc(cfg['sub'])}</div>"
            f"<div class='a'>{esc(cfg['author'])}　著</div>"
            "<div class='n'>坟头草　译<br/>" + esc(cfg["note"]) + "</div>"
            "</div></body></html>")


# the copyright notice lives in pipeline_overhaul/copyright.py so that all seven
# assemblers print the same words; keeping a copy here let them drift apart
COPYRIGHT = cpr.TEXT


def copyright_page(cfg: dict) -> str:
    return ("<?xml version='1.0' encoding='utf-8'?>\n<!DOCTYPE html>\n"
            "<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='zh-CN'>"
            "<head><meta charset='utf-8'/><title>版权</title>"
            "<link rel='stylesheet' type='text/css' href='style.css'/></head><body>"
            "<div class='copyright'>"
            f"<h1>{esc(cfg['title'])}</h1>"
            f"<p class='src'>{esc(cfg['src'])}　著</p>"
            "<p class='tr'>坟头草　译</p>"
            f"<div class='cn'>{COPYRIGHT}</div>"
            "</div></body></html>")


def volume_page(vno: str, vtitle: str) -> str:
    return ("<?xml version='1.0' encoding='utf-8'?>\n<!DOCTYPE html>\n"
            "<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='zh-CN'>"
            f"<head><meta charset='utf-8'/><title>{esc(vtitle)}</title>"
            "<link rel='stylesheet' type='text/css' href='style.css'/></head><body>"
            f"<div class='titlepage'><div class='s'>{esc(vno)}</div>"
            f"<div class='t' style='font-size:1.7em'>{esc(vtitle)}</div></div>"
            "</body></html>")


def order_for(book: str) -> list[str]:
    d = os.path.join(common.WORK, book, "final")
    ids = sorted(os.path.splitext(f)[0] for f in os.listdir(d))
    if book == "whale":
        front = [c for c in ("front_ety", "front_ext") if c in ids]
        rest = sorted([c for c in ids if c.startswith("ch")], key=lambda x: int(x[2:]))
        epi = [c for c in ids if c.startswith("epi")]
        return front + rest + epi
    return ids


def build(book: str) -> None:
    cfg = BOOKS[book]
    ids = order_for(book)
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
    total_han = total_paras = total_notes = 0
    for n, cid in enumerate(ids, 1):
        fin = common.load_json(os.path.join(common.WORK, book, "final", cid + ".json"))
        texts = list(fin["texts"])
        types = list(fin.get("types") or ["p"] * len(texts))
        notes = common.load_json(
            os.path.join(common.WORK, book, "notes", cid + ".json"),
            fin.get("notes") or [])
        notes = insert_notes(texts, notes)
        title = (fin.get("title_zh") or "").strip()
        # some books never recorded a title_zh, and the chapter heading is sitting
        # in the body as the first paragraph. Pulling it up keeps the table of
        # contents readable and stops the heading being printed twice.
        if not title and texts and is_heading(texts[0]):
            title = texts.pop(0)
            types = types[1:]
        if not title:
            title = cn_chapter(cid) or cid
        sub = fin.get("title_en", "") if book == "whale" else ""
        if cid == "front_ety":
            title, sub = "词源", "Etymology"
        elif cid == "front_ext":
            title, sub = "摘录", "Extracts"
        elif cid.startswith("epi"):
            title, sub = "尾声", "Epilogue"

        book_head = ""
        if book == "lotr" and cid.startswith("book"):
            bk = cid[:5]
            vol = VOLUMES[bk]
            if vol != cur_vol:
                cur_vol = vol
                vn = f"v{len(nav)}"
                fn = f"v{len(nav)}.xhtml"
                files[fn] = volume_page(vol[0], vol[1])
                manifest.append(f"<item id='{vn}' href='{fn}' media-type='application/xhtml+xml'/>")
                spine.append(f"<itemref idref='{vn}'/>")
                nav.append((f"{vol[0]} {vol[1]}", fn))
            book_head = BOOKNAMES[bk]

        fn = f"c{n:03d}.xhtml"
        files[fn] = chapter_xhtml(title, sub, texts, types, notes, book_head)
        manifest.append(f"<item id='c{n}' href='{fn}' media-type='application/xhtml+xml'/>")
        spine.append(f"<itemref idref='c{n}'/>")
        nav.append(((book_head + "　" if book_head else "") + title, fn))
        total_han += common.han("".join(texts))
        total_paras += len(texts)
        total_notes += len(notes)

    navx = ["<?xml version='1.0' encoding='utf-8'?>",
            "<html xmlns='http://www.w3.org/1999/xhtml' xmlns:epub='http://www.idpf.org/2007/ops' xml:lang='zh-CN'>",
            "<head><meta charset='utf-8'/><title>目录</title></head><body>",
            "<nav epub:type='toc' id='toc'><h1>目录</h1><ol>"]
    for t, fn in nav:
        navx.append(f"<li><a href='{fn}'>{esc(t)}</a></li>")
    navx.append("</ol></nav></body></html>")
    files["nav.xhtml"] = "\n".join(navx)

    files["content.opf"] = f"""<?xml version='1.0' encoding='utf-8'?>
<package xmlns='http://www.idpf.org/2007/opf' version='3.0' unique-identifier='uid'>
<metadata xmlns:dc='http://purl.org/dc/elements/1.1/'>
<dc:title>{esc(cfg['title'])}</dc:title>
<dc:creator>{esc(cfg['author'])}</dc:creator>
<dc:contributor>坟头草 译</dc:contributor>
<dc:language>zh-CN</dc:language>
<dc:identifier id='uid'>{cfg['uid']}</dc:identifier>
<meta property='dcterms:modified'>2026-10-25T12:00:00Z</meta>
</metadata>
<manifest>
<item id='nav' href='nav.xhtml' media-type='application/xhtml+xml' properties='nav'/>
{chr(10).join(manifest)}
</manifest>
<spine>
{chr(10).join(spine)}
</spine>
</package>"""

    files["container.xml"] = ("<?xml version='1.0'?><container version='1.0' "
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
            print("XML ERROR", fn, str(e)[:120])

    with zipfile.ZipFile(cfg["epub"], "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", zipfile.ZIP_STORED)
        for fn, content in files.items():
            path = "META-INF/container.xml" if fn == "container.xml" else "OEBPS/" + fn
            z.writestr(path, content)

    print(f"{book}: {len(ids)} chapters, {total_paras} paragraphs, "
          f"{total_han:,} han, {total_notes} notes, {errs} xml errors -> {cfg['epub']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, choices=list(BOOKS))
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    build(a.book)
