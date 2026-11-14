"""Assemble translated chapters into deliverables: per-book Markdown + a full EPUB."""
from __future__ import annotations

import glob
import json
import os
import re
import sys
import zipfile

SRC = "E:/Translate/work/src"
OUT = "E:/Translate/work/out"
BOOKS = "E:/Translate/work/book"
EPUB = "E:/Translate/魔戒（坟头草译）.epub"

BOOK_ORDER = ["prologue", "book1", "book2", "book3", "book4", "book5", "book6"]
BOOK_TITLES = {
    "prologue": ("楔子", "Prologue"),
    "book1": ("第一部 魔戒同盟", "The Fellowship of the Ring"),
    "book2": ("第二部 双塔殊途", "The Two Towers"),
    "book3": ("第三部 王者归来", "The Return of the King"),
    "book4": ("卷四", "Book Four"),
    "book5": ("卷五", "Book Five"),
    "book6": ("卷六", "Book Six"),
}
PART_TITLES = {"book1": "第一部", "book2": "第二部", "book3": "第三部"}


def chapter_text(cid: str):
    """Return (title_zh, body_paragraphs) for one chapter, or None."""
    meta = json.load(open(os.path.join(SRC, cid + ".json"), encoding="utf-8"))
    p = os.path.join(OUT, cid, "chapter.md")
    if not os.path.exists(p):
        parts = []
        for f in sorted(glob.glob(os.path.join(OUT, cid, "chunk*", "final.txt"))):
            parts.append(open(f, encoding="utf-8").read())
        if not parts:
            return None
        body = "\n".join(parts)
    else:
        body = open(p, encoding="utf-8").read()
        body = re.sub(r"^#.*$", "", body, flags=re.M)
    body = body.replace("\r", "")
    body = re.sub(r"<\s*verse\s*>\s*", "\n<verse>\n", body)
    body = re.sub(r"\s*</verse\s*>", "\n</verse>\n", body)
    paras = []
    for line in body.split("\n"):
        t = line.strip()
        if not t:
            continue
        if t.startswith("<verse>") or t.endswith("</verse>"):
            paras.append({"type": "verse", "text": t})
        else:
            paras.append({"type": "p", "text": t.lstrip("#").strip()})
    return {"id": cid, "title": meta["title_zh"], "en": meta["title_en"],
            "book": meta["book"], "no": meta["no"], "paras": paras}


def _is_scene_break(text: str) -> bool:
    """Tolkien marks a change of scene with a row of asterisks."""
    t = text.strip()
    return bool(t) and all(ch in "* \t" for ch in t) and t.count("*") >= 1


def chapter_html(meta):
    out = [f"<h2>{meta['title']}</h2>"]
    for b in meta["paras"]:
        if b["type"] == "p":
            if _is_scene_break(b["text"]):
                out.append('<p class="break">&#8258;</p>')
            else:
                out.append(f"<p>{b['text']}</p>")
        else:
            inner = b["text"].strip()
            inner = re.sub(r"^<verse>\s*", "", inner)
            inner = re.sub(r"\s*</verse>$", "", inner)
            lines = [l.strip() for l in inner.split("\n") if l.strip()]
            body = "<br/>".join(lines)
            out.append(f'<p class="verse">{body}</p>')
    return "\n".join(out)


def main():
    os.makedirs(BOOKS, exist_ok=True)
    ids = sorted(f[:-5] for f in os.listdir(SRC) if f.endswith(".json"))
    chapters = [chapter_text(c) for c in ids]
    chapters = [c for c in chapters if c]
    print(f"assembling {len(chapters)} chapters")

    by_book = {}
    for c in chapters:
        by_book.setdefault(c["book"], []).append(c)

    # markdown
    full = ["# 魔戒（坟头草译）", ""]
    for bk in BOOK_ORDER:
        if bk not in by_book:
            continue
        title, en = BOOK_TITLES.get(bk, (bk, ""))
        full.append(f"\n## {title}\n\n*{en}*\n")
        for c in sorted(by_book[bk], key=lambda x: x["no"]):
            full.append(f"\n### {c['title']}\n")
            for b in c["paras"]:
                if b["type"] == "p":
                    full.append("\n" + b["text"])
                else:
                    inner = re.sub(r"</?verse>", "", b["text"])
                    full.append("\n> " + "\n> ".join(l.strip() for l in inner.split("\n") if l.strip()))
    open(os.path.join(BOOKS, "魔戒（坟头草译）.md"), "w", encoding="utf-8").write("\n".join(full))

    # epub
    spine, manifest, nav = [], [], []
    files = {}
    n = 0
    for bk in BOOK_ORDER:
        if bk not in by_book:
            continue
        title, en = BOOK_TITLES.get(bk, (bk, ""))
        n += 1
        nav.append({"id": f"b{n}", "title": title, "html": f"b{n:02d}.xhtml", "children": []})
        for c in sorted(by_book[bk], key=lambda x: x["no"]):
            n += 1
            fn = f"b{n:02d}.xhtml"
            html = ("<?xml version='1.0' encoding='utf-8'?>\n"
                    "<!DOCTYPE html><html xmlns='http://www.w3.org/1999/xhtml'>"
                    "<head><meta charset='utf-8'/><title>" + c["title"] + "</title>"
                    "<style>body{line-height:1.9;font-family:serif} "
                    "p.verse{margin-left:2em;line-height:1.6} "
                    "h2{margin-top:2em;text-align:center} "
                    "p.break{text-align:center;color:#999;letter-spacing:.5em;margin:1.4em 0}</style></head><body>"
                    + chapter_html(c) + "</body></html>")
            files[fn] = html
            manifest.append(f"<item id='c{n}' href='{fn}' media-type='application/xhtml+xml'/>")
            spine.append(f"<itemref idref='c{n}'/>")
            nav[-1]["children"].append({"title": c["title"], "html": fn})

    toc_ncx = ["<?xml version='1.0' encoding='utf-8'?>",
               "<ncx xmlns='http://www.daisy.org/z3986/2005/ncx/' version='2005-1'>",
               "<head><meta name='dtb:uid' content='urn:lotr-fentoucao'/></head>",
               "<docTitle><text>魔戒（坟头草译）</text></docTitle><navMap>"]
    for i, bk in enumerate([b for b in BOOK_ORDER if b in by_book], start=1):
        play = (i - 1) * 100 + 1
        toc_ncx.append(f"<navPoint id='n{i}' playOrder='{play}'><navLabel><text>{BOOK_TITLES[bk][0]}"
                       f"</text></navLabel><content src='{nav[i-1]['html']}'/></navPoint>")
        for j, kid in enumerate(nav[i - 1]["children"], start=1):
            toc_ncx.append(f"<navPoint id='n{i}_{j}' playOrder='{play + j}'>"
                           f"<navLabel><text>{kid['title']}</text></navLabel>"
                           f"<content src='{kid['html']}'/></navPoint>")
    toc_ncx.append("</navMap></ncx>")

    opf = f"""<?xml version='1.0' encoding='utf-8'?>
<package xmlns='http://www.idpf.org/2007/opf' version='2.0' unique-identifier='uid'>
<metadata xmlns:dc='http://purl.org/dc/elements/1.1/'>
<dc:title>魔戒（坟头草译）</dc:title>
<dc:creator>J.R.R. 托尔金</dc:creator>
<dc:language>zh-CN</dc:language>
<dc:identifier id='uid'>urn:lotr-fentoucao</dc:identifier>
<dc:publisher>坟头草 译</dc:publisher>
</metadata>
<manifest>
<item id='ncx' href='toc.ncx' media-type='application/x-dtbncx+xml'/>
{''.join(manifest)}
</manifest>
<spine toc='ncx'>
{''.join(spine)}
</spine>
</package>"""

    container = ("<?xml version='1.0'?><container version='1.0' "
                 "xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>"
                 "<rootfiles><rootfile full-path='OEBPS/content.opf' "
                 "media-type='application/oebps-package+xml'/></rootfiles></container>")

    with zipfile.ZipFile(EPUB, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container)
        z.writestr("OEBPS/content.opf", opf)
        z.writestr("OEBPS/toc.ncx", "\n".join(toc_ncx))
        for fn, html in files.items():
            z.writestr("OEBPS/" + fn, html)

    total = sum(len(b["text"]) for c in chapters for b in c["paras"])
    print(f"markdown: {os.path.join(BOOKS, '魔戒（坟头草译）.md')}  chapters={len(chapters)} chars={total}")
    print("epub:", EPUB)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
