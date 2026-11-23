# -*- coding: utf-8 -*-
"""Build 《空屋及其他鬼故事：布莱克伍德短篇十则》.

Source: PG #14471 via the GITenberg mirror The-Empty-House-and-Other-Ghost-
Stories_14471 (1906). Ten stories, 67,257 words. The long ninth story (A
Private Secretary in New York) was cut into two slices; every slice was
stripped of standalone section numerals before dispatch.

The last story's slice carried the publisher's catalogue pages after the
printer's credit; those are not part of the story and were trimmed.
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
TITLE = "空屋及其他鬼故事：布莱克伍德短篇十则"
AUTHOR = "阿尔杰农·布莱克伍德"
UID = "urn:translate:blackwood-empty-house-20261124"

# (label, [(zh file, source slice)], exempt para indexes within the story)
TALES = [
    ("空屋", [("eh_empty_zh.json", "_eh_empty_paras.json")], ()),
    ("闹鬼的岛", [("eh_island_zh.json", "_eh_island_paras.json")], ()),
    ("窃听一例", [("eh_eaves_zh.json", "_eh_eaves_paras.json")], ()),
    ("守信", [("eh_promise_zh.json", "_eh_promise_paras.json")], ()),
    ("蓄意窃取", [("eh_steal_zh.json", "_eh_steal_paras.json")], ()),
    ("死者之林", [("eh_wood_zh.json", "_eh_wood_paras.json")], ()),
    ("史密斯：一间公寓里的插曲", [("eh_smith_zh.json", "_eh_smith_paras.json")], ()),
    ("一件可疑的礼物", [("eh_gift_zh.json", "_eh_gift_paras.json")], ()),
    ("一名私人秘书在纽约的奇遇",
     [("eh_secretary_a_zh.json", "_eh_secretarya_paras.json"),
      ("eh_secretary_b_zh.json", "_eh_secretaryb_paras.json")], (44,)),
    ("骷髅湖：营中插曲", [("eh_skeleton_zh.json", "_eh_skeleton_paras.json")], ()),
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
        f"<p>作者：{html.escape(AUTHOR)}（Algernon Blackwood，1869—1951）。</p>"
        "<p>译文：坟头草译。</p>"
        "<p>《空屋及其他鬼故事》初版于一九〇六年，是布莱克伍德的第一部短篇集，"
        "十篇都以“这地方有些不对头”起手。</p>"
        "<p>本库另收布莱克伍德七册（约翰·塞伦斯、温迪戈、马人、不可思议的冒险、柳林、"
        "人类的和声、吉姆博），八册并存。</p>")
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
    print(f"{TITLE}  {len(stats)} tales  {total_han:,} han  {total_words:,} src words  "
          f"{out.stat().st_size // 1024} KB")


main()