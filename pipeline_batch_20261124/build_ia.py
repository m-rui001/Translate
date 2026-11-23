# -*- coding: utf-8 -*-
"""Build 《不可思议的冒险：布莱克伍德中篇五则》 and 《柳林》.

Sources, both via the GITenberg mirror:
  * Incredible Adventures, PG #43816 -- five novellas, 103,000 words, cut into
    twelve consecutive slices for parallel sub-agents.
  * The Willows, PG #11438 -- one novella, 20,000 words, two slices.
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

BOOKS = [
    {
        "title": "不可思议的冒险：布莱克伍德中篇五则",
        "uid": "urn:translate:blackwood-incredible-20261124",
        "note": ("《不可思议的冒险》初版于一九一四年，收中篇五则：《厄尼勋爵的再生》写一个"
                 "没有欲望的少年在山村里被春之祭唤醒；《牺牲》写一场命中注定的登山献祭；"
                 "《诅咒者》写清教徒祖先的诅咒如何在萨塞克斯的宅子里显形；《下降埃及》写"
                 "一个人被古埃及的时间吞没；《行路人》写暮色中赶路的朝圣者。"),
        "others": "本库另收《约翰·塞伦斯医生奇案》五案、《温迪戈》、《马人》，四册并存。",
        "tales": [
            ("厄尼勋爵的再生", ["ia_ernie_a_zh.json", "ia_ernie_b_zh.json", "ia_ernie_c_zh.json"], ()),
            ("牺牲", ["ia_sacrifice_zh.json"], ()),
            ("诅咒者", ["ia_damned_a_zh.json", "ia_damned_b_zh.json",
                        "ia_damned_c_zh.json", "ia_damned_d_zh.json"], ()),
            ("下降埃及", ["ia_egypt_a_zh.json", "ia_egypt_b_zh.json", "ia_egypt_c_zh.json"], ()),
            ("行路人", ["ia_wayfarers_zh.json"], ()),
        ],
        "slices": {
            "ia_ernie_a_zh.json": "_ia_erniea_paras.json",
            "ia_ernie_b_zh.json": "_ia_ernieb_paras.json",
            "ia_ernie_c_zh.json": "_ia_erniec_paras.json",
            "ia_sacrifice_zh.json": "_ia_sacrificea_paras.json",
            "ia_damned_a_zh.json": "_ia_damneda_paras.json",
            "ia_damned_b_zh.json": "_ia_damnedb_paras.json",
            "ia_damned_c_zh.json": "_ia_damnedc_paras.json",
            "ia_damned_d_zh.json": "_ia_damnedd_paras.json",
            "ia_egypt_a_zh.json": "_ia_egypta_paras.json",
            "ia_egypt_b_zh.json": "_ia_egyptb_paras.json",
            "ia_egypt_c_zh.json": "_ia_egyptc_paras.json",
            "ia_wayfarers_zh.json": "_ia_wayfarersa_paras.json",
        },
    },
    {
        "title": "柳林：布莱克伍德河上异闻",
        "uid": "urn:translate:blackwood-willows-20261124",
        "note": ("《柳林》初刊于一九〇七年，是布莱克伍德影响最深远的中篇。两个人在多瑙河上游"
                 "的洪泛柳林间扎营，渐渐发觉林子里住着不属于人类的古老存在。洛夫克拉夫特"
                 "对它推崇备至。"),
        "others": "本库另收布莱克伍德四册：《约翰·塞伦斯医生奇案》《温迪戈》《马人》"
                  "《不可思议的冒险》，五册并存。",
        "tales": [("柳林", ["willows_a_zh.json", "willows_b_zh.json"], (0,))],
        "slices": {
            "willows_a_zh.json": "_willows_a_paras.json",
            "willows_b_zh.json": "_willows_b_paras.json",
        },
    },
]

AUTHOR = "阿尔杰农·布莱克伍德"


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
    entries = [("title.xhtml", title), ("copyright.xhtml", "版权信息"), ("nav.xhtml", "目录")]
    files = {}
    stats = []
    total_han = total_words = 0

    for i, (label, zh_files, exempt) in enumerate(book["tales"], 1):
        zh_all, en_all = [], []
        for zh_file in zh_files:
            zh = json.loads((WORK / zh_file).read_text(encoding="utf-8"))
            src = json.loads((WORK / book["slices"][zh_file]).read_text(encoding="utf-8"))
            assert len(zh) == len(src) and all(zh) and all(src), (zh_file, len(zh), len(src))
            zh_all.extend(zh)
            en_all.extend(src)
        checked = [p for j, p in enumerate(zh_all) if j not in exempt]
        assert not any(re.search(r"[A-Za-z]{2,}", p) for p in checked), (title, label, "latin")
        tail = ("。", "！", "”", "？", "：", "—", "…", "）", "」", "』", "＊")
        assert all(p.rstrip("」』")[-1:] in tail for p in checked), (title, label, "punct")

        body = "<h1>" + label + "</h1>" + "".join(
            "<p>" + html.escape(p).replace("\n", "<br/>") + "</p>" for p in zh_all)
        files[f"OEBPS/c{i:03}.xhtml"] = xhtml(label, body)
        entries.append((f"c{i:03}.xhtml", label))
        han = len(re.findall(r"[\u4e00-\u9fff]", "".join(zh_all)))
        words = sum(len(re.findall(r"[A-Za-z']+", p)) for p in en_all)
        total_han += han
        total_words += words
        stats.append((label, len(zh_all), han, words))

    files["OEBPS/title.xhtml"] = xhtml(title,
        "<h1>" + html.escape(title) + "</h1>"
        f"<p class='ep' style='text-align:center'>{html.escape(AUTHOR)}</p>"
        "<p class='ep' style='text-align:center'>坟头草译</p>")
    files["OEBPS/copyright.xhtml"] = xhtml("版权",
        "<h2>版权信息</h2>"
        f"<p>书名：{html.escape(title)}</p>"
        f"<p>作者：{html.escape(AUTHOR)}（Algernon Blackwood，1869—1951）。</p>"
        "<p>译文：坟头草译。</p>"
        f"<p>{html.escape(book['note'])}</p>"
        f"<p>{html.escape(book['others'])}</p>")
    links = "".join("<li><a href='" + f + "'>" + html.escape(t) + "</a></li>" for f, t in entries)
    files["OEBPS/nav.xhtml"] = xhtml("目录",
        "<nav xmlns:epub='http://www.idpf.org/2007/ops' epub:type='toc'>"
        "<h1>目录</h1><ol>" + links + "</ol></nav>")
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

    for label, n, han, words in stats:
        print(f"   {label}  {n} paras  {han:,} han  {words:,} words")
    print(f"{title}  {len(stats)} tales  {total_han:,} han  {total_words:,} src words  "
          f"{out.stat().st_size // 1024} KB")


for book in BOOKS:
    build(book)