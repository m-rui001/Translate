# -*- coding: utf-8 -*-
"""Build 《人类的和声》 and 《吉姆博：一个奇想》.

Sources, both via the GITenberg mirror:
  * The Human Chord, PG #11988 (1910) -- 59,165 words, cut into six slices.
  * Jimbo: A Fantasy, PG #30974 (1909) -- 49,177 words, cut into five slices.

Chapter headings and the standalone roman numerals were stripped from the
source slices before dispatch, so the paragraph counts match one to one.
"""
import html
import json
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "work_batch_20261124"
OUT = ROOT / "out"
AUTHOR = "阿尔杰农·布莱克伍德"

BOOKS = [
    {
        "title": "人类的和声", "short": "人类的和声",
        "uid": "urn:translate:blackwood-human-chord-20261124",
        "slices": [(k, f"hc_{k}_zh.json", f"_hc_{k}_paras.json") for k in "abcdef"],
        "exempt": {"hc_b_zh.json": (59,), "jb_a_zh.json": ()},
        "note": ("《人类的和声》初版于一九一〇年。青年斯宾罗宾应募到威尔士山中一位怪牧师的"
                 "宅邸任秘书，渐渐明白主人穷毕生之力在找“那声音”——事物的真名；念出它，"
                 "便能改造、乃至重组宇宙。"),
        "others": "本库另收布莱克伍德六册（约翰·塞伦斯、温迪戈、马人、不可思议的冒险、柳林），"
                  "七册并存。",
    },
    {
        "title": "吉姆博：一个奇想", "short": "吉姆博",
        "uid": "urn:translate:blackwood-jimbo-20261124",
        "slices": [(k, f"jb_{k}_zh.json", f"_jb_{k}_paras.json") for k in "abcde"],
        "exempt": {"jb_a_zh.json": (0, 94)},
        "note": ("《吉姆博：一个奇想》初版于一九〇九年。小男孩吉姆博在一次意外中跌进“空屋”"
                 "——介于生死之间的中间地带，那里的一切都由他自身的恐惧与想象塑成。"),
        "others": "本库另收布莱克伍德六册，七册并存。",
    },
]


def xhtml(title, body):
    return (
        "<?xml version='1.0' encoding='utf-8'?>"
        "<html xmlns='http://www.w3.org/1999/xhtml' lang='zh-CN'>"
        f"<head><title>{html.escape(title)}</title>"
        "<style>body{font-family:serif;line-height:1.85;margin:5%;}"
        "p{text-indent:2em;margin:0 0 .7em;}h1{text-align:center;font-size:1.5em;}"
        "p.ep{text-indent:0;font-size:.9em;color:#555;}</style></head><body>"
        + body + "</body></html>"
    )


def build(book):
    title = book["title"]
    zh_all, en_all, checked = [], [], []
    for key, zh_file, src_file in book["slices"]:
        zh = json.loads((WORK / zh_file).read_text(encoding="utf-8"))
        src = json.loads((WORK / src_file).read_text(encoding="utf-8"))
        assert len(zh) == len(src) and all(zh) and all(src), (zh_file, len(zh), len(src))
        ex = book["exempt"].get(zh_file, ())
        checked.extend(p for i, p in enumerate(zh) if i not in ex)
        zh_all.extend(zh)
        en_all.extend(src)
    assert not any(re.search(r"[A-Za-z]{2,}", p) for p in checked), (title, "latin")
    tail = ("。", "！", "”", "？", "：", "—", "…", "）", "」", "』", "＊")
    assert all(p.rstrip("」』")[-1:] in tail for p in checked), (title, "punct")

    body = "<h1>" + book["short"] + "</h1>" + "".join(
        "<p>" + html.escape(p).replace("\n", "<br/>") + "</p>" for p in zh_all)
    entries = [("title.xhtml", title), ("copyright.xhtml", "版权信息"),
               ("nav.xhtml", "目录"), ("c001.xhtml", book["short"])]
    links = "".join("<li><a href='" + f + "'>" + html.escape(t) + "</a></li>" for f, t in entries)
    files = {
        "OEBPS/c001.xhtml": xhtml(title, body),
        "OEBPS/title.xhtml": xhtml(title,
            "<h1>" + html.escape(title) + "</h1>"
            f"<p class='ep' style='text-align:center'>{html.escape(AUTHOR)}</p>"
            "<p class='ep' style='text-align:center'>坟头草译</p>"),
        "OEBPS/copyright.xhtml": xhtml("版权",
            "<h2>版权信息</h2>"
            f"<p>书名：{html.escape(title)}</p>"
            f"<p>作者：{html.escape(AUTHOR)}（Algernon Blackwood，1869—1951）。</p>"
            "<p>译文：坟头草译。</p>"
            f"<p>{html.escape(book['note'])}</p>"
            f"<p>{html.escape(book['others'])}</p>"),
        "OEBPS/nav.xhtml": xhtml("目录",
            "<nav xmlns:epub='http://www.idpf.org/2007/ops' epub:type='toc'>"
            "<h1>目录</h1><ol>" + links + "</ol></nav>"),
    }
    points = "".join(
        f"<navPoint id='n{i}' playOrder='{i}'><navLabel><text>{html.escape(t)}</text></navLabel>"
        f"<content src='{n}'/></navPoint>" for i, (n, t) in enumerate(entries, 1))
    files["OEBPS/toc.ncx"] = (
        "<?xml version='1.0'?><ncx xmlns='http://www.daisy.org/z3986/2005/ncx/' version='2005-1'>"
        "<head><meta name='dtb:uid' content='" + book["uid"] + "'/></head>"
        "<docTitle><text>" + html.escape(title) + "</text></docTitle>"
        "<navMap>" + points + "</navMap></ncx>")
    files["META-INF/container.xml"] = (
        "<?xml version='1.0' encoding='utf-8'?>"
        "<container version='1.0' xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>"
        "<rootfiles><rootfile full-path='OEBPS/content.opf' media-type='application/oebps-package+xml'/></rootfiles></container>")
    manifest = "<item id='ncx' href='toc.ncx' media-type='application/x-dtbncx+xml'/>"
    manifest += "".join(
        (f"<item id='i{i}' href='{f}' media-type='application/xhtml+xml'"
         + (" properties='nav'" if f == "nav.xhtml" else "") + "/>")
        for i, (f, _) in enumerate(entries, 1))
    spine = "".join(f"<itemref idref='i{i}'/>" for i, (f, _) in enumerate(entries, 1))
    files["OEBPS/content.opf"] = (
        "<?xml version='1.0' encoding='utf-8'?>"
        "<package xmlns='http://www.idpf.org/2007/opf' version='3.0' unique-identifier='uid'>"
        "<metadata xmlns:dc='http://purl.org/dc/elements/1.1/'>"
        f"<dc:title>{html.escape(title)}</dc:title>"
        f"<dc:creator>{html.escape(AUTHOR)}</dc:creator>"
        "<dc:language>zh-CN</dc:language>"
        f"<dc:identifier id='uid'>{book['uid']}</dc:identifier>"
        "<meta property='dcterms:modified'>2026-11-24T00:00:00Z</meta></metadata>"
        f"<manifest>{manifest}</manifest>"
        f"<spine>{spine}</spine></package>")

    out = OUT / f"{title}（坟头草译）.epub"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        for name, data in files.items():
            z.writestr(name, data)
    ET.fromstring(files["OEBPS/content.opf"])
    ET.fromstring(files["OEBPS/nav.xhtml"])

    han = len(re.findall(r"[\u4e00-\u9fff]", "".join(zh_all)))
    words = sum(len(re.findall(r"[A-Za-z']+", p)) for p in en_all)
    print(f"{title}  {len(zh_all)} paras  {han:,} han  {words:,} src words  "
          f"{out.stat().st_size // 1024} KB")


for book in BOOKS:
    build(book)