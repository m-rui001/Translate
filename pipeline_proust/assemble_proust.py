"""Assemble the Proust supplementary volumes into a standalone EPUB with a real TOC.

Earlier this file emitted one XHTML per volume, so the navigation held five
entries (版权 + four volumes) and a reader could not jump to anything inside a
1.1 million-character book. The source text does carry structure, though:

    Deuxième partie
    Chapitre premier
    Maladie de ma grand'mère. Maladie de Bergotte. ...

i.e. a part marker, a chapter marker, and a one-line summary of what the chapter
covers. Those are authentic division points in the French edition, so the build now
splits on them and emits

    卷 (h1)  ->  部 (h2)  ->  章 (h3)

with the French summary kept as the chapter's subtitle, and a matching nested
nav/ncx.

Two details matter for correctness:

  * the summary line must be *consumed* as a subtitle rather than left in the
    body, or every chapter opens with a stray contents-list fragment;
  * the text before the first chapter marker (Proust's dedication pages, and in
    v3 a long passage that precedes "Deuxième partie") is its own front section,
    not dropped.

Volumes whose text has fewer markers than expected still get a usable TOC: the
front section is titled from the volume name.
"""
from __future__ import annotations

import html
import io
import json
import os
import re
import sys
import zipfile
from xml.dom import minidom

sys.path.insert(0, 'E:/Translate/pipeline_overhaul')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import copyright as cpr  # noqa: E402
import outline  # noqa: E402
import chapter_titles  # noqa: E402

CHUNKS = os.environ.get("PROUST_CHUNKS", "E:/Translate/work_proust/chunks")
OUT = os.environ.get("PROUST_OUT", "E:/Translate/work_proust/out")
BOOKS = os.environ.get("PROUST_BOOK", "E:/Translate/work_proust/book")
SRC = os.environ.get("PROUST_SRC", "E:/Translate/work_proust/src")
EPUB = os.environ.get("PROUST_EPUB",
                      "E:/Translate/out/追忆似水年华（坟头草译）.epub")
TITLE_ZH = "追忆似水年华"
TITLE_FR = "À la recherche du temps perdu"
AUTHOR = "马塞尔·普鲁斯特"

VOL = [
    ("v1", "第一卷", "在斯万家那边", "Du côté de chez Swann",
     os.environ.get("PROUST_OUT_IND", "E:/Translate/work_proust/out_ind")),
    ("v2", "第二卷", "在少女们身旁", "À l'ombre des jeunes filles en fleurs",
     os.environ.get("PROUST_OUT_IND", "E:/Translate/work_proust/out_ind")),
    ("v3", "第三卷", "盖尔芒特家那边", "Le Côté de Guermantes", OUT),
    ("v4", "第四卷", "索多姆和戈摩尔", "Sodome et Gomorrhe", OUT),
    ("v5", "第五卷", "女囚", "La Prisonnière",
     os.environ.get("PROUST_OUT_IND", "E:/Translate/work_proust/out_ind")),
    ("v6", "第六卷", "女逃亡者", "Albertine disparue", OUT),
    ("v7", "第七卷", "重现的时光", "Le Temps retrouvé", OUT),
]

CN_NUM = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七",
          8: "八", 9: "九", 10: "十", 11: "十一", 12: "十二"}

STYLE = ("body{line-height:1.9;font-family:serif} "
         "h1{text-align:center;margin:3em 0 1em;font-size:1.5em} "
         "h2{text-align:center;margin:2.4em 0 .8em;font-size:1.25em} "
         "h3{text-align:center;margin:2em 0 .4em;font-size:1.1em} "
         "h4{text-align:center;color:#555;font-weight:normal;font-style:italic;"
         "margin:0 0 1.6em;font-size:.95em} "
         "p{text-indent:2em;margin:0 0 .6em} "
         "div.titlepage{text-align:center;margin-top:30%}")


def vol_body(vol: str, base: str = OUT) -> list[str]:
    spec = json.load(io.open(os.path.join(CHUNKS, vol, "chunks.json"),
                             encoding="utf-8"))
    out, missing = [], []
    for k in sorted(spec, key=int):
        p = os.path.join(base, vol, f"chunk{int(k):03d}", "final.txt")
        if os.path.exists(p):
            out.append(io.open(p, encoding="utf-8").read().strip())
        else:
            missing.append(k)
    if missing:
        print(f"WARNING [{vol}]: {len(missing)} chunks missing final.txt: "
              f"{missing[:10]}{'...' if len(missing) > 10 else ''}")
    return out


def split_paras(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


FRENCH_ORD = {"premier": 1, "premiere": 1, "première": 1, "deuxième": 2,
              "deuxieme": 2, "second": 2, "seconde": 2, "troisième": 3,
              "troisieme": 3, "quatrième": 4, "quatrieme": 4, "cinquième": 5,
              "cinquieme": 5, "sixième": 6, "sixieme": 6, "septième": 7,
              "septieme": 7, "huitième": 8, "huitieme": 8, "neuvième": 9,
              "neuvieme": 9, "dixième": 10, "dixieme": 10}


def cn_ordinal(word: str) -> str:
    w = (word or "").strip().lower()
    n = FRENCH_ORD.get(w) or 0
    return CN_NUM.get(n, "")


def han_count(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def build_units(vol: str, title_zh: str, fr: str, base: str = OUT) -> list[dict]:
    """Return [{part, ch, label, paras}] for one volume, split at real chapters."""
    paras = split_paras("\n\n".join(vol_body(vol, base)))
    segs = outline.segments(vol, paras)
    for s in segs:
        s["label"] = chapter_titles.title_for(vol, s["part"], s["ch"])
    return segs


# ─────────────────────────────────────────── rendering

def esc(s: str) -> str:
    return html.escape(s, quote=False)


def section_xhtml(vol_title: str, fr: str, unit: dict, is_first: bool) -> str:
    body = "".join(f"<p>{esc(p)}</p>" for p in unit["paras"])
    head = [f"<h1>{esc(vol_title)}</h1>"] if is_first else []
    if unit.get("label"):
        head.append(f"<h2>{esc(unit['label'])}</h2>")
    elif unit["part"] or unit["ch"]:
        bits = ""
        if unit["part"]:
            bits += f"第{cn_ordinal(unit['part'])}部"
        if unit["ch"]:
            bits += (" " if bits else "") + f"第{cn_ordinal(unit['ch'])}章"
        head.append(f"<h2>{esc(bits)}</h2>")
    if is_first:
        head.append(f"<p style='text-align:center;font-style:italic;color:#666'>"
                    f"{esc(fr)}</p>")
    return ("<?xml version='1.0' encoding='utf-8'?>\n<!DOCTYPE html>\n"
            "<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='zh-CN'>"
            f"<head><meta charset='utf-8'/><title>{esc(vol_title)}</title>"
            f"<style>{STYLE}</style></head><body>"
            + "".join(head) + body + "</body></html>")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(BOOKS, exist_ok=True)

    files: dict[str, str] = {}
    manifest: list[str] = []
    spine: list[str] = []
    nav_tree: list[dict] = []          # {title, href, children:[...]}
    vol_stats = []
    total_han = total_paras = 0
    seq = 0

    for vol, vol_no, vol_name, fr, base in VOL:
        vol_title = f"{vol_no} {vol_name}"
        units = build_units(vol, vol_title, fr, base)
        vol_node = {"title": vol_title, "href": "", "children": []}
        vh = 0
        for j, u in enumerate(units):
            seq += 1
            fn = f"{vol}_{j + 1:02d}.xhtml"
            files[fn] = section_xhtml(vol_title, fr, u, j == 0)
            manifest.append(f"<item id='s{seq}' href='{fn}' "
                            "media-type='application/xhtml+xml'/>")
            spine.append(f"<itemref idref='s{seq}'/>")
            label = u.get("label") or ""
            if not label:
                bits = ""
                if u["part"]:
                    bits += f"第{cn_ordinal(u['part'])}部"
                if u["ch"]:
                    bits += (" " if bits else "") + f"第{cn_ordinal(u['ch'])}章"
                label = bits or (vol_name if j == 0 else f"续{j}")
            href = f"{fn}"
            if not vol_node["href"]:
                vol_node["href"] = href
            if label != vol_name:
                vol_node["children"].append({"title": label, "href": href,
                                             "children": []})
            vh += han_count("\n".join(u["paras"]))
            total_paras += len(u["paras"])
        total_han += vh
        nav_tree.append(vol_node)
        vol_stats.append((vol, vol_title, len(units), vh))
        print(f"{vol} {vol_title}: sections={len(units)} han={vh:,}")

    files["copyright.xhtml"] = cpr.page(TITLE_ZH, TITLE_FR, AUTHOR,
                                        STYLE.replace("%%", "%"))
    manifest.insert(0, "<item id='cr' href='copyright.xhtml' "
                       "media-type='application/xhtml+xml'/>")
    spine.insert(0, "<itemref idref='cr'/>")
    nav_tree.insert(0, {"title": "版权", "href": "copyright.xhtml", "children": []})

    # flat playOrder counter, nested structure
    counter = [0]

    def emit_ncx(nodes: list[dict], indent: int = 0) -> list[str]:
        lines = []
        pad = "  " * indent
        for nd in nodes:
            counter[0] += 1
            pid = f"n{counter[0]}"
            lines.append(f"{pad}<navPoint id='{pid}' playOrder='{counter[0]}'>"
                         f"<navLabel><text>{esc(nd['title'])}</text></navLabel>"
                         f"<content src='{nd['href']}'/>")
            if nd["children"]:
                lines.extend(emit_ncx(nd["children"], indent + 1))
            lines.append(f"{pad}</navPoint>")
        return lines

    toc = ["<?xml version='1.0' encoding='utf-8'?>",
           "<ncx xmlns='http://www.daisy.org/z3986/2005/ncx/' version='2005-1'>",
           "<head><meta name='dtb:uid' content='urn:proust-works-v3467'/></head>",
           f"<docTitle><text>{esc(TITLE_ZH)}</text></docTitle><navMap>"]
    toc.extend(emit_ncx(nav_tree))
    toc.append("</navMap></ncx>")
    files["toc.ncx"] = "\n".join(toc)

    # EPUB 3 navigation document. The NCX above stays for older readers, but several
    # current reading systems ignore an NCX-only book, which is why this title used to
    # open with no table of contents at all.
    def emit_nav(nodes: list[dict], depth: int = 1) -> list[str]:
        pad = "  " * depth
        out = [pad + "<ol>"]
        for nd in nodes:
            out.append(f"{pad}  <li><a href='{nd['href']}'>{esc(nd['title'])}</a>")
            if nd["children"]:
                out.extend(emit_nav(nd["children"], depth + 2))
                out.append(f"{pad}  </li>")
            else:
                out[-1] += "</li>"
        out.append(pad + "</ol>")
        return out

    nav = ["<?xml version='1.0' encoding='utf-8'?>",
           "<!DOCTYPE html>",
           "<html xmlns='http://www.w3.org/1999/xhtml' "
           "xmlns:epub='http://www.idpf.org/2007/ops' xml:lang='zh-CN'>",
           "<head><meta charset='utf-8'/><title>目录</title></head><body>",
           "<nav epub:type='toc' id='toc'><h1>目录</h1>"]
    nav.extend(emit_nav(nav_tree))
    nav.append("</nav></body></html>")
    files["nav.xhtml"] = chr(10).join(nav)

    opf = f"""<?xml version='1.0' encoding='utf-8'?>
<package xmlns='http://www.idpf.org/2007/opf' version='3.0' unique-identifier='uid'>
<metadata xmlns:dc='http://purl.org/dc/elements/1.1/'>
<dc:title>{esc(TITLE_ZH)}</dc:title>
<dc:creator>{esc(AUTHOR)}</dc:creator>
<dc:contributor>坟头草 译</dc:contributor>
<dc:language>zh-CN</dc:language>
<dc:identifier id='uid'>urn:proust-works-v3467</dc:identifier>
<meta property='dcterms:modified'>2026-10-25T12:00:00Z</meta>
</metadata>
<manifest>
<item id='ncx' href='toc.ncx' media-type='application/x-dtbncx+xml'/>
<item id='nav' href='nav.xhtml' media-type='application/xhtml+xml' properties='nav'/>
{''.join(manifest)}
</manifest>
<spine toc='ncx'>
<itemref idref='nav'/>
{''.join(spine)}
</spine>
</package>"""
    files["content.opf"] = opf

    files["container.xml"] = ("<?xml version='1.0'?><container version='1.0' "
                              "xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>"
                              "<rootfiles><rootfile full-path='OEBPS/content.opf' "
                              "media-type='application/oebps-package+xml'/></rootfiles></container>")

    n_err = 0
    for fn, content in files.items():
        try:
            minidom.parseString(content.encode("utf-8"))
        except Exception as e:  # noqa: BLE001
            n_err += 1
            print(f"XML ERROR in {fn}: {str(e)[:200]}")

    with zipfile.ZipFile(EPUB, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip",
                   zipfile.ZIP_STORED)
        for fn, content in files.items():
            if fn == "container.xml":
                z.writestr("META-INF/container.xml", content)
            else:
                z.writestr("OEBPS/" + fn, content)

    print("-" * 60)
    for vol, t, nsec, hc in vol_stats:
        print(f"{vol} {t}: {nsec} sections, han {hc:,}")
    print(f"TOTAL: han={total_han:,} paras={total_paras:,} files={len(files)}")
    print(f"XML validation: {n_err} errors")
    print("toc: volumes=%d entries=%d" % (len(nav_tree), counter[0]))
    print("epub:", EPUB)
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
