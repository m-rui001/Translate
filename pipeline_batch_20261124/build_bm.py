# -*- coding: utf-8 -*-
"""Build 《光明的使者》.

Source: PG #43594 via the GITenberg mirror The-Bright-Messenger_43594 (1921),
120,719 words in twenty-seven chapters, cut into fourteen consecutive slices of
about 8,800 words each; chapter numerals and titles stripped before cutting.
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
TITLE = "光明的使者"
AUTHOR = "阿尔杰农·布莱克伍德"
UID = "urn:translate:blackwood-bright-messenger-20261124"

SLICES = [f"bm_{k}_zh.json" for k in "abcdefghijklmn"]

# exempt: epigraph attributions, and French phrases kept in the original with a
# Chinese gloss beside them (rosa mystica, fille de joie, moulin a vent); j[162]
# ends on a signed note whose signature line carries no full stop.
EXEMPT = {
    "bm_e_zh.json": (145,),
    "bm_f_zh.json": (19,),
    "bm_h_zh.json": (173,),
    "bm_j_zh.json": (162,),
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
        src = json.loads((WORK / f"_bm_{key}_paras.json").read_text(encoding="utf-8"))
        assert len(zh) == len(src) and all(zh) and all(src), (zh_file, len(zh), len(src))
        ex = EXEMPT.get(zh_file, ())
        checked.extend(p for i, p in enumerate(zh) if i not in ex)
        zh_all.extend(zh)
        en_all.extend(src)

    assert not any(re.search(r"[A-Za-z]{2,}", p) for p in checked), "latin"
    tail = ("。", "！", "”", "？", "：", "—", "…", "）", "」", "』", "＊")
    assert all(p.rstrip("」』")[-1:] in tail for p in checked), "punct"

    body = "<h1>光明的使者</h1>" + "".join(
        "<p>" + html.escape(p).replace("\n", "<br/>") + "</p>" for p in zh_all)
    entries = [("title.xhtml", TITLE), ("copyright.xhtml", "版权信息"),
               ("nav.xhtml", "目录"), ("c001.xhtml", "光明的使者")]
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
            "<p>《光明的使者》初版于一九二一年，是《仙境囚徒》的姊妹篇。"
            "心理学家爱德华·菲利里收治一个双重人格的青年，"
            "他的第二人格自称「N. H.」（非人），来自一个比我们更古的世界。</p>"
            "<p>本库另收布莱克伍德十册，十一册并存。</p>"),
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