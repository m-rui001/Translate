# -*- coding: utf-8 -*-
"""Build 《时间与诸神》.

Source: PG #8183 via the GITenberg mirror Time-and-the-Gods_8183 (1906).
Twenty-one sections -- a preface, nineteen tales in Part I, and the long
Journey of the King in Part II -- 40,649 words. The last tale was cut into two
slices; every other section is one slice.
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
TITLE = "时间与诸神"
AUTHOR = "邓萨尼勋爵"
UID = "urn:translate:dunsany-time-and-gods-20261124"

# (label, [(zh file, source slice)], exempt para indexes)
TALES = [
    ("序", [("tg_preface_zh.json", "_tg_preface_paras.json")], ()),
    ("时间与诸神", [("tg_time_zh.json", "_tg_time_paras.json")], (4,)),
    ("海之来", [("tg_sea_zh.json", "_tg_sea_paras.json")], ()),
    ("黎明的传说", [("tg_dawn_zh.json", "_tg_dawn_paras.json")], ()),
    ("人之复仇", [("tg_vengeance_zh.json", "_tg_vengeance_paras.json")], ()),
    ("诸神沉睡时", [("tg_slept_zh.json", "_tg_slept_paras.json")], ()),
    ("非王之王", [("tg_king_zh.json", "_tg_king_paras.json")], ()),
    ("凯之洞穴", [("tg_kai_zh.json", "_tg_kai_paras.json")], ()),
    ("寻访之悲", [("tg_sorrow_zh.json", "_tg_sorrow_paras.json")], ()),
    ("雅尼斯人", [("tg_yarnith_zh.json", "_tg_yarnith_paras.json")], ()),
    ("为了诸神的荣耀", [("tg_honour_zh.json", "_tg_honour_paras.json")], ()),
    ("夜与晨", [("tg_night_zh.json", "_tg_night_paras.json")], ()),
    ("高利贷", [("tg_usury_zh.json", "_tg_usury_paras.json")], ()),
    ("姆利丁", [("tg_mlideen_zh.json", "_tg_mlideen_paras.json")], ()),
    ("诸神的秘密", [("tg_secret_zh.json", "_tg_secret_paras.json")], ()),
    ("南风", [("tg_southwind_zh.json", "_tg_southwind_paras.json")], ()),
    ("时间之地", [("tg_landtime_zh.json", "_tg_landtime_paras.json")], ()),
    ("萨尼达克的回心", [("tg_sarnidac_zh.json", "_tg_sarnidac_paras.json")], ()),
    ("诸神的玩笑", [("tg_jest_zh.json", "_tg_jest_paras.json")], ()),
    ("先知之梦", [("tg_dreams_zh.json", "_tg_dreams_paras.json")], (0, 18)),
    # exempt: the nine section numerals 一..九 of the journey (and 十, 十一 in
    # the second slice) stand as their own paragraphs
    ("国王之旅", [("tg_journey_a_zh.json", "_tg_journeya_paras.json"),
                  ("tg_journey_b_zh.json", "_tg_journeyb_paras.json")],
     (0, 15, 20, 49, 74, 83, 95, 104, 112, 138 + 10, 138 + 17)),
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


def main():
    files = {}
    entries = [("title.xhtml", TITLE), ("copyright.xhtml", "版权信息"), ("nav.xhtml", "目录")]
    stats = []
    total_han = total_words = 0
    for i, (label, parts, exempt) in enumerate(TALES, 1):
        zh_all, en_all = [], []
        for zh_file, src_file in parts:
            zh = json.loads((WORK / zh_file).read_text(encoding="utf-8"))
            src = json.loads((WORK / src_file).read_text(encoding="utf-8"))
            assert len(zh) == len(src) and all(zh) and all(src), (zh_file, len(zh), len(src))
            zh_all.extend(zh)
            en_all.extend(src)
        checked = [p for j, p in enumerate(zh_all) if j not in exempt]
        assert not any(re.search(r"[A-Za-z]{2,}", p) for p in checked), (label, "latin")
        tail = ("。", "！", "”", "？", "：", "—", "…", "）", "」", "』", "＊")
        assert all(p.rstrip("」』")[-1:] in tail for p in checked), (label, "punct")
        body = "<h1>" + label + "</h1>" + "".join(
            "<p>" + html.escape(p).replace("\n", "<br/>") + "</p>" for p in zh_all)
        files[f"OEBPS/c{i:03}.xhtml"] = xhtml(label, body)
        entries.append((f"c{i:03}.xhtml", label))
        han = len(re.findall(r"[\u4e00-\u9fff]", "".join(zh_all)))
        words = sum(len(re.findall(r"[A-Za-z']+", p)) for p in en_all)
        total_han += han
        total_words += words
        stats.append((label, len(zh_all), han, words))

    files["OEBPS/title.xhtml"] = xhtml(TITLE,
        "<h1>" + html.escape(TITLE) + "</h1>"
        f"<p class='ep' style='text-align:center'>{html.escape(AUTHOR)}</p>"
        "<p class='ep' style='text-align:center'>坟头草译</p>")
    files["OEBPS/copyright.xhtml"] = xhtml("版权",
        "<h2>版权信息</h2>"
        f"<p>书名：{html.escape(TITLE)}</p>"
        f"<p>作者：{html.escape(AUTHOR)}（Lord Dunsany，1878—1957）。</p>"
        "<p>译文：坟头草译。</p>"
        "<p>《时间与诸神》初版于一九〇六年，是《佩加纳的诸神》的续集："
        "写诸神、时间与人的种种寓言，末篇《国王之旅》是一篇长梦。</p>"
        "<p>本库另收邓萨尼七册（佩加纳诸神与短篇六册），八册并存。</p>")
    links = "".join("<li><a href='" + f + "'>" + html.escape(t) + "</a></li>" for f, t in entries)
    files["OEBPS/nav.xhtml"] = xhtml("目录",
        "<nav xmlns:epub='http://www.idpf.org/2007/ops' epub:type='toc'>"
        "<h1>目录</h1><ol>" + links + "</ol></nav>")
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
    for label, n, han, words in stats:
        print(f"   {label}  {n} paras  {han:,} han  {words:,} words")
    print(f"{TITLE}  {len(stats)} sections  {total_han:,} han  {total_words:,} src words  "
          f"{out.stat().st_size // 1024} KB")


main()