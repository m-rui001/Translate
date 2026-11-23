# -*- coding: utf-8 -*-
"""Build 《日与夜的故事：布莱克伍德短篇十五则》.

Source: PG #45964 via the GITenberg mirror Day-and-Night-Stories_45964 (1917).
Fifteen stories, 73,678 words, cut into eight consecutive slices of about ten
thousand words each. Chapter numerals and chapter titles were stripped from the
source slices before dispatch, so they read as one continuous text.
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
TITLE = "日与夜的故事：布莱克伍德短篇十五则"
AUTHOR = "阿尔杰农·布莱克伍德"
UID = "urn:translate:blackwood-day-night-20261124"

SLICES = [(k, f"dn_{k}_zh.json", f"_dn_{k}_paras.json") for k in "abcdefgh"]

# slice-internal para indexes exempt from the assertions:
# a[0] is the French epigraph of the opening story ("Je suis la premiere au
# rendez-vous..."), left in French on purpose; g[19] quotes a German newspaper
# headline (Ungluecksfall) as a word; b[80] ends on a footnote numeral and b[81] is that
# footnote itself, bracketed with ［…］ in the library convention.
EXEMPT = {"dn_a_zh.json": (0,), "dn_b_zh.json": (80, 81), "dn_g_zh.json": (19,)}


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


def main():
    zh_all, en_all, checked = [], [], []
    for key, zh_file, src_file in SLICES:
        zh = json.loads((WORK / zh_file).read_text(encoding="utf-8"))
        src = json.loads((WORK / src_file).read_text(encoding="utf-8"))
        assert len(zh) == len(src) and all(zh) and all(src), (zh_file, len(zh), len(src))
        ex = EXEMPT.get(zh_file, ())
        checked.extend(p for i, p in enumerate(zh) if i not in ex)
        zh_all.extend(zh)
        en_all.extend(src)
    assert not any(re.search(r"[A-Za-z]{2,}", p) for p in checked), "latin"
    tail = ("。", "！", "”", "？", "：", "—", "…", "）", "」", "』", "＊")
    assert all(p.rstrip("」』")[-1:] in tail for p in checked), "punct"

    body = "<h1>日与夜的故事</h1>" + "".join(
        "<p>" + html.escape(p).replace("\n", "<br/>") + "</p>" for p in zh_all)
    entries = [("title.xhtml", TITLE), ("copyright.xhtml", "版权信息"),
               ("nav.xhtml", "目录"), ("c001.xhtml", "日与夜的故事")]
    links = "".join("<li><a href='" + f + "'>" + html.escape(t) + "</a></li>" for f, t in entries)
    files = {
        "OEBPS/c001.xhtml": xhtml(TITLE, body),
        "OEBPS/title.xhtml": xhtml(TITLE,
            "<h1>" + html.escape(TITLE) + "</h1>"
            f"<p class='ep' style='text-align:center'>{html.escape(AUTHOR)}</p>"
            "<p class='ep' style='text-align:center'>坟头草译</p>"),
        "OEBPS/copyright.xhtml": xhtml("版权",
            "<h2>版权信息</h2>"
            f"<p>书名：{html.escape(TITLE)}</p>"
            f"<p>作者：{html.escape(AUTHOR)}（Algernon Blackwood，1869—1951）。</p>"
            "<p>译文：坟头草译。</p>"
            "<p>《日与夜的故事》初版于一九一七年，收短篇十五篇，从《幽会》《潘的一触》"
            "《荷鲁斯之翼》一路到《传统》，是布莱克伍德中后期短篇的代表选本。</p>"
            "<p>本库另收布莱克伍德八册，九册并存。</p>"),
        "OEBPS/nav.xhtml": xhtml("目录",
            "<nav xmlns:epub='http://www.idpf.org/2007/ops' epub:type='toc'>"
            "<h1>目录</h1><ol>" + links + "</ol></nav>"),
    }
    points = "".join(
        f"<navPoint id='n{i}' playOrder='{i}'><navLabel><text>{html.escape(t)}</text></navLabel>"
        f"<content src='{n}'/></navPoint>" for i, (n, t) in enumerate(entries, 1))
    files["OEBPS/toc.ncx"] = (
        "<?xml version='1.0'?><ncx xmlns='http://www.daisy.org/z3986/2005/ncx/' version='2005-1'>"
        "<head><meta name='dtb:uid' content='" + UID + "'/></head>"
        "<docTitle><text>" + html.escape(TITLE) + "</text></docTitle>"
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
        f"<dc:title>{html.escape(TITLE)}</dc:title>"
        f"<dc:creator>{html.escape(AUTHOR)}</dc:creator>"
        "<dc:language>zh-CN</dc:language>"
        f"<dc:identifier id='uid'>{UID}</dc:identifier>"
        "<meta property='dcterms:modified'>2026-11-24T00:00:00Z</meta></metadata>"
        f"<manifest>{manifest}</manifest>"
        f"<spine>{spine}</spine></package>")

    out = OUT / f"{TITLE}（坟头草译）.epub"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        for name, data in files.items():
            z.writestr(name, data)
    ET.fromstring(files["OEBPS/content.opf"])
    ET.fromstring(files["OEBPS/nav.xhtml"])

    han = len(re.findall(r"[\u4e00-\u9fff]", "".join(zh_all)))
    words = sum(len(re.findall(r"[A-Za-z']+", p)) for p in en_all)
    print(f"{TITLE}  {len(zh_all)} paras  {han:,} han  {words:,} src words  "
          f"{out.stat().st_size // 1024} KB")


main()