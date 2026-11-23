# -*- coding: utf-8 -*-
"""Build 《仙境囚徒》.

Source: PG #6021 via the GITenberg mirror
A-Prisoner-in-Fairyland-The-Book-That-Uncle-Paul-Wrote_6021 (1913), 140,644
words in thirty-four chapters. Chapter numerals and chapter titles were
stripped from the source before cutting, and the text was cut into sixteen
consecutive slices of about nine thousand words each for parallel sub-agents.
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
TITLE = "仙境囚徒"
AUTHOR = "阿尔杰农·布莱克伍德"
UID = "urn:translate:blackwood-prisoner-fairyland-20261124"

SLICES = [f"pf_{k}_zh.json" for k in "abcdefghijklmnop"]

# Paragraphs exempt from the Latin and closing-punctuation assertions. In every
# case the paragraph is either a verse epigraph carrying an attribution line
# (——作者〈篇名〉, no full stop) or a French/German phrase quoted as a word with
# a Chinese gloss beside it, which the library keeps in the original.
EXEMPT = {
    "pf_a_zh.json": (0,),
    "pf_b_zh.json": (20, 80),
    "pf_c_zh.json": (6, 42, 104),
    "pf_e_zh.json": (19, 63, 83),
    "pf_g_zh.json": (127, 131),
    "pf_h_zh.json": (20,),
    "pf_i_zh.json": (146,),
    "pf_j_zh.json": (11, 71, 99, 124),
    "pf_k_zh.json": (36, 85, 87, 88, 89, 141),
    "pf_l_zh.json": (46, 82, 108, 110, 111, 113, 114, 131, 144, 155, 165),
    "pf_n_zh.json": (82, 138),
    "pf_o_zh.json": (72, 73, 94, 104, 141, 164, 165),
    "pf_p_zh.json": (11, 13, 66, 78),
}


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
    for zh_file in SLICES:
        key = zh_file.split("_")[1]
        zh = json.loads((WORK / zh_file).read_text(encoding="utf-8"))
        src = json.loads((WORK / f"_pf_{key}_paras.json").read_text(encoding="utf-8"))
        assert len(zh) == len(src) and all(zh) and all(src), (zh_file, len(zh), len(src))
        ex = EXEMPT.get(zh_file, ())
        checked.extend(p for i, p in enumerate(zh) if i not in ex)
        zh_all.extend(zh)
        en_all.extend(src)

    assert not any(re.search(r"[A-Za-z]{2,}", p) for p in checked), "latin"
    tail = ("。", "！", "”", "？", "：", "—", "…", "）", "」", "』", "＊")
    assert all(p.rstrip("」』")[-1:] in tail for p in checked), "punct"

    body = "<h1>仙境囚徒</h1>" + "".join(
        "<p>" + html.escape(p).replace("\n", "<br/>") + "</p>" for p in zh_all)
    entries = [("title.xhtml", TITLE), ("copyright.xhtml", "版权信息"),
               ("nav.xhtml", "目录"), ("c001.xhtml", "仙境囚徒")]
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
            "<p>《仙境囚徒》初版于一九一三年，副题「保罗舅舅写的那本书」。"
            "中年实业家亨利·罗杰斯回到童年的村庄，被一群孩子和他们口中的"
            "「星窟」「星光快车」「乱缠」拉进了一场漫长的梦境。</p>"
            "<p>本库另收布莱克伍德九册，十册并存。</p>"),
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