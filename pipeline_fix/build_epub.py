
"""Assemble a Chinese EPUB 3 from already-translated chapter texts.

Written for the repair pass: the existing books are structurally wrong (chapter
numbers taken from file ids, no scene headings, verse collapsed into prose), and the
old builder's numbering rule cannot express what these books actually need. This one
takes an explicit list of items and writes exactly that structure.
"""
from __future__ import annotations

import html
import os
import re
import zipfile

CJK = re.compile(r"[\u4e00-\u9fff]")

STYLE = """body{line-height:1.85;font-family:serif;margin:0 5%}
h1{text-align:center;margin:2.4em 0 .3em;font-size:1.45em;letter-spacing:.06em;font-weight:normal}
h2{text-align:center;color:#666;font-weight:normal;font-style:italic;font-size:.92em;margin:0 0 2em;letter-spacing:.04em}
h3.book{text-align:center;margin:3em 0 1.6em;font-size:1.2em;letter-spacing:.2em;font-weight:normal;color:#444}
p{text-indent:2em;margin:0 0 .55em;text-align:justify}
p.verse{text-indent:0;margin-left:2.5em;margin-bottom:.9em;line-height:1.6;white-space:pre-line}
p.speaker{text-indent:0;margin-left:1.5em;text-indent:-1.5em}
p.center{text-indent:0;text-align:center;margin:1.6em 0}
div.titlepage{text-align:center;margin-top:22%}
div.titlepage .t{font-size:2.1em;letter-spacing:.3em;margin-bottom:1.4em}
div.titlepage .s{font-size:1.05em;color:#555;margin-bottom:.5em}
div.titlepage .a{font-size:1em;margin-top:3em;color:#444}
div.titlepage .n{font-size:.85em;color:#777;margin-top:4em;line-height:1.9}
div.part{text-align:center;margin-top:30%}
div.part .k{font-size:.95em;color:#777;letter-spacing:.3em;margin-bottom:1.2em}
div.part .t{font-size:1.9em;letter-spacing:.15em}
div.copyright{margin-top:14%;margin-bottom:10%}
div.copyright h1{font-size:1.3em;letter-spacing:.2em;margin:0 0 1.6em;text-align:center}
div.copyright p{text-indent:0;text-align:center;margin:0 0 .6em}
div.copyright p.src{font-size:.95em;color:#555}
div.copyright p.tr{font-size:1em;color:#333;margin-bottom:3em}
div.copyright div.cn{font-size:.82em;line-height:1.85;color:#555;text-align:left;
  border-top:1px solid #ddd;padding-top:1.2em;margin:0 1em}
"""

COPY = ("本译本由坟头草翻译，保留署名权；除此之外不主张任何权利，"
        "亦不作任何担保。")


def esc(s: str) -> str:
    return html.escape(s or "", quote=False)


def page(title: str, body: str, extra_head: str = "") -> str:
    return ("<?xml version='1.0' encoding='utf-8'?>\n<!DOCTYPE html>\n"
            "<html xmlns='http://www.w3.org/1999/xhtml' "
            "xmlns:epub='http://www.idpf.org/2007/ops' xml:lang='zh-CN'>"
            f"<head><meta charset='utf-8'/><title>{esc(title)}</title>"
            "<link rel='stylesheet' type='text/css' href='style.css'/>"
            f"{extra_head}</head><body>{body}</body></html>")


def para_html(text: str, kind: str) -> str:
    t = esc(text)
    if kind == "verse":
        # One <br/> per source line: the CSS pre-line alone is not honoured by every
        # reading system, and a poem printed as one run of prose is a defect.
        t = "<br/>".join(esc(line) for line in text.split("\n"))
        return f"<p class='verse'>{t}</p>"
    if kind == "center":
        return f"<p class='center'>{t}</p>"
    return f"<p>{t}</p>"


def title_page(cfg: dict) -> str:
    return page("书名页",
                "<div class='titlepage'>"
                f"<div class='t'>{esc(cfg['title'])}</div>"
                f"<div class='s'>{esc(cfg.get('sub', ''))}</div>"
                f"<div class='a'>{esc(cfg['author'])}　著</div>"
                "<div class='n'>坟头草　译</div>"
                f"<div class='n'>{esc(cfg.get('note', ''))}</div>"
                "</div>")


def copyright_page(cfg: dict) -> str:
    return page("版权",
                "<div class='copyright'>"
                f"<h1>{esc(cfg['title'])}</h1>"
                f"<p class='src'>{esc(cfg['src'])}　著</p>"
                "<p class='tr'>坟头草　译</p>"
                f"<div class='cn'>{COPY}</div>"
                "</div>")


def part_page(kicker: str, title: str) -> str:
    return page(title, "<div class='part'>"
                       f"<div class='k'>{esc(kicker)}</div>"
                       f"<div class='t'>{esc(title)}</div></div>")


def build(cfg: dict, items: list[dict], out_path: str) -> dict:
    """items: {title, texts, types, part} where part is an optional group key.

    Order matters; a part page is emitted the first time its key appears.
    """
    files = {"style.css": STYLE,
             "title.xhtml": title_page(cfg),
             "copyright.xhtml": copyright_page(cfg)}
    manifest = ["<item id='css' href='style.css' media-type='text/css'/>",
                "<item id='title' href='title.xhtml' media-type='application/xhtml+xml'/>",
                "<item id='copy' href='copyright.xhtml' media-type='application/xhtml+xml'/>"]
    spine = ["<itemref idref='title'/>", "<itemref idref='copy'/>"]

    # groups: [(part_title or None, part_href or None, [(title, href), ...])]
    groups: list[dict] = [{"part": None, "href": None, "items": [
        ("书名页", "title.xhtml"), ("版权", "copyright.xhtml")]}]
    seen_parts: dict[str, str] = {}
    n = 0
    for it in items:
        part = it.get("part")
        if part and part not in seen_parts:
            n += 1
            fn = f"p{n:03d}.xhtml"
            files[fn] = part_page(it.get("part_kicker", ""), part)
            manifest.append(f"<item id='p{n}' href='{fn}' "
                            "media-type='application/xhtml+xml'/>")
            spine.append(f"<itemref idref='p{n}'/>")
            seen_parts[part] = fn
            groups.append({"part": part, "href": fn, "items": []})
        n += 1
        fn = f"c{n:03d}.xhtml"
        body = [f"<h1>{esc(it['title'])}</h1>"]
        if it.get("sub"):
            body.append(f"<h2>{esc(it['sub'])}</h2>")
        body += [para_html(t, ty) for t, ty in zip(it["texts"], it["types"])]
        files[fn] = page(it["title"], "".join(body))
        manifest.append(f"<item id='c{n}' href='{fn}' media-type='application/xhtml+xml'/>")
        spine.append(f"<itemref idref='c{n}'/>")
        groups[-1]["items"].append((it["title"], fn))

    def nav_tree() -> str:
        out = []
        for g in groups:
            if not g["items"]:
                continue
            if g["part"] is None:
                out += [f"<li><a href='{h}'>{esc(t)}</a></li>" for t, h in g["items"]]
            else:
                inner = "".join(f"<li><a href='{h}'>{esc(t)}</a></li>"
                                for t, h in g["items"])
                out.append(f"<li><a href='{g['href']}'>{esc(g['part'])}</a>"
                           f"<ol>{inner}</ol></li>")
        return "".join(out)

    files["nav.xhtml"] = page(
        "目录", "<nav epub:type='toc' id='toc'><h1>目录</h1><ol>" + nav_tree()
                + "</ol></nav>")
    manifest.append("<item id='nav' href='nav.xhtml' media-type='application/xhtml+xml' "
                    "properties='nav'/>")
    spine.insert(0, "<itemref idref='nav'/>")

    def ncx_tree() -> str:
        out, order = [], [0]

        def point(label: str, href: str, kids: list[str] | None = None) -> str:
            order[0] += 1
            k = order[0]
            inner = "".join(kids or [])
            return (f"<navPoint id='np{k}' playOrder='{k}'>"
                    f"<navLabel><text>{esc(label)}</text></navLabel>"
                    f"<content src='{href}'/>{inner}</navPoint>")

        for g in groups:
            if not g["items"]:
                continue
            if g["part"] is None:
                out += [point(t, h) for t, h in g["items"]]
            else:
                kids = [point(t, h) for t, h in g["items"]]
                out.append(point(g["part"], g["href"], kids))
        return "".join(out)

    files["toc.ncx"] = ("<?xml version='1.0' encoding='utf-8'?>\n"
                        "<ncx xmlns='http://www.daisy.org/z3986/2005/ncx/' version='2005-1'>"
                        f"<head><meta name='dtb:uid' content='{cfg['uid']}'/></head>"
                        f"<docTitle><text>{esc(cfg['title'])}</text></docTitle>"
                        f"<navMap>{ncx_tree()}</navMap></ncx>")
    manifest.append("<item id='ncx' href='toc.ncx' media-type='application/x-dtbncx+xml'/>")

    opf = ("<?xml version='1.0' encoding='utf-8'?>\n"
           "<package xmlns='http://www.idpf.org/2007/opf' version='3.0' "
           f"unique-identifier='uid'>\n<metadata xmlns:dc='http://purl.org/dc/elements/1.1/'>"
           f"<dc:title>{esc(cfg['title'])}</dc:title>"
           f"<dc:creator>{esc(cfg['author'])}</dc:creator>"
           "<dc:contributor>坟头草 译</dc:contributor>"
           "<dc:language>zh-CN</dc:language>"
           f"<dc:identifier id='uid'>{cfg['uid']}</dc:identifier>"
           f"<meta property='dcterms:modified'>{cfg.get('modified', '2026-10-28T12:00:00Z')}</meta>"
           "</metadata><manifest>" + "".join(manifest) +
           "</manifest><spine toc='ncx'>" + "".join(spine) + "</spine></package>")
    files["content.opf"] = opf
    files["META-INF/container.xml"] = (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        "<container version='1.0' xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>"
        "<rootfiles><rootfile full-path='OEBPS/content.opf' "
        "media-type='application/oebps-package+xml'/></rootfiles></container>")

    tmp = out_path + ".tmp"
    with zipfile.ZipFile(tmp, "w") as z:
        z.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
        for name, content in files.items():
            z.writestr("OEBPS/" + name if not name.startswith("META-INF") else name,
                       content, zipfile.ZIP_DEFLATED)
    os.replace(tmp, out_path)
    return {"files": len(files), "chapters": len(items),
            "hanzi": sum(len(CJK.findall(t)) for it in items for t in it["texts"])}
