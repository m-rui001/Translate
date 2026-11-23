# -*- coding: utf-8 -*-
"""Build 《温迪戈：布莱克伍德荒原异闻》.

Source: PG #10897 (Algernon Blackwood, The Wendigo, 1907) via the GITenberg
mirror The-Wendigo_10897. One novella in nine roman-numbered sections, cut
into two slices for two parallel sub-agents.
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
TITLE = "温迪戈：布莱克伍德荒原异闻"
AUTHOR = "阿尔杰农·布莱克伍德"
UID = "urn:translate:blackwood-wendigo-20261124"

# (slice source file, leading-line offset, zh file)
PARTS = [("_wendigo_a", 1, "wendigo_a_zh.json"),
         ("_wendigo_b", 5, "wendigo_b_zh.json")]
# slice-internal para indexes exempt from the punctuation/Latin assertions:
# a: 32/91/102 = roman section marks II/III/IV, 34 = "bonne chance" cited, 68 = ＊ row
# b: slice carried its own roman marks V-IX, dropped (5); 5/20/36/45/117 = ＊ rows
EXEMPT = {0: (32, 34, 68, 91, 102), 1: (5, 20, 36, 45, 117)}


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
    zh_all = []
    en_all = []
    for j, (src_name, skip, zh_file) in enumerate(PARTS):
        src = json.loads((WORK / f"{src_name}_paras.json").read_text(encoding="utf-8"))
        zh = json.loads((WORK / zh_file).read_text(encoding="utf-8"))
        # slice sources carry leading section-mark lines; the agents rendered
        # only slice A's leading 'I' as dropped -- the interior roman marks stay
        assert len(zh) == len(src) - skip, (src_name, len(zh), len(src) - skip)
        zh_all.extend(zh)
        en_all.extend(src[skip:])
    assert all(zh_all) and all(en_all) and len(zh_all) == len(en_all)

    checked = []
    base = 0
    for j, (_, _, zh_file) in enumerate(PARTS):
        zh = json.loads((WORK / zh_file).read_text(encoding="utf-8"))
        checked.extend(p for i, p in enumerate(zh) if i not in EXEMPT[j])
        base += len(zh)
    assert not any(re.search(r"[A-Za-z]{2,}", p) for p in checked), "latin leak"
    tail = ("。", "！", "”", "？", "：", "—", "…", "）", "」", "』", "］", "＊")
    assert all(p.rstrip("」』")[-1:] in tail for p in checked), "punctuation"

    body = "".join("<p>" + html.escape(p).replace("\n", "<br/>") + "</p>" for p in zh_all)
    entries = [("title.xhtml", TITLE), ("copyright.xhtml", "版权信息"),
               ("nav.xhtml", "目录"), ("c001.xhtml", "温迪戈")]
    links = "".join("<li><a href='" + f + "'>" + html.escape(t) + "</a></li>"
                    for f, t in entries)
    files = {
        "OEBPS/c001.xhtml": xhtml(TITLE, "<h1>温迪戈</h1>" + body),
        "OEBPS/title.xhtml": xhtml(TITLE,
            "<h1>" + html.escape(TITLE) + "</h1>"
            f"<p class='ep' style='text-align:center'>{html.escape(AUTHOR)}</p>"
            "<p class='ep' style='text-align:center'>坟头草译</p>"),
        "OEBPS/copyright.xhtml": xhtml("版权",
            "<h2>版权信息</h2>"
            f"<p>书名：{html.escape(TITLE)}</p>"
            f"<p>作者：{html.escape(AUTHOR)}（Algernon Blackwood，1869—1951）。</p>"
            "<p>译文：坟头草译。</p>"
            "<p>《温迪戈》初刊于一九〇七年，是布莱克伍德最负盛名的中篇："
            "大北方的风之灵把猎人的灵魂拖去环游世界，直到他\"看见了温迪戈\"。</p>"
            "<p>本库另收《约翰·塞伦斯医生奇案：布莱克伍德灵异五案》，两册并存。</p>"),
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
    (WORK / "stats_wendigo.json").write_text(json.dumps(
        {"title": TITLE, "paras": len(zh_all), "han": han, "words": words},
        ensure_ascii=False, indent=1), encoding="utf-8")


main()
