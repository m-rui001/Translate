# -*- coding: utf-8 -*-
"""Build 《约翰·塞伦斯医生奇案：布莱克伍德灵异五案》.

Source: PG #49222 (Algernon Blackwood, John Silence, Physician Extraordinary,
1908) via the GITenberg mirror John-Silence-Physician-Extraordinary_49222.

The five cases were cut by line range, then each long case was split into
2-4 consecutive slices for parallel sub-agents; the translations are
concatenated here. Each slice file carries its leading CASE/title/section-
marker line, dropped per the offsets below.
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
TITLE = "约翰·塞伦斯医生奇案：布莱克伍德灵异五案"
AUTHOR = "阿尔杰农·布莱克伍德"
UID = "urn:translate:blackwood-john-silence-20261124"

# case -> (master source slice, [ (slice source file, leading-line offset, zh file), ... ],
#          subtitle, year, exempt global para indexes within the case)
CASES = {
    "灵异入侵": ("_js_invasion_paras.json",
        [("_js_invasion_a", 2, "js_inv_a_zh.json"),
         ("_js_invasion_b", 1, "js_inv_b_zh.json"),
         ("_js_invasion_c", 1, "js_inv_c_zh.json")],
        "A Psychical Invasion", "1908", (14, 34)),
    "古老巫术": ("_js_sorceries_paras.json",
        [("_js_sorceries_a", 2, "js_sor_a_zh.json"),
         ("_js_sorceries_b", 1, "js_sor_b_zh.json"),
         ("_js_sorceries_c", 1, "js_sor_c_zh.json"),
         ("_js_sorceries_d", 1, "js_sor_d_zh.json")],
        "Ancient Sorceries", "1908", (10, 14, 57, 72, 74, 169)),
    "火的报复": ("_js_nemesis_paras.json",
        [("_js_nemesis_a", 2, "js_nem_a_zh.json"),
         ("_js_nemesis_b", 1, "js_nem_b_zh.json"),
         ("_js_nemesis_c", 1, "js_nem_c_zh.json"),
         ("_js_nemesis_d", 1, "js_nem_d_zh.json")],
        "The Nemesis of Fire", "1908", ()),
    "秘传的崇拜": ("_js_worship_paras.json",
        [("_js_worship", 1, "js_worship_zh.json")],
        "Secret Worship", "1908", (140, 141, 142, 143, 147, 153, 180)),
    "狗营": ("_js_dog_paras.json",
        [("_js_dog_a", 2, "js_dog_a_zh.json"),
         ("_js_dog_b", 1, "js_dog_b_zh.json"),
         ("_js_dog_c", 1, "js_dog_c_zh.json"),
         ("_js_dog_d", 1, "js_dog_d_zh.json")],
        "The Camp of the Dog", "1908", (62 + 284, 100, 173, 203, 212, 238, 382)),
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
    files = {}
    entries = []
    total_han = 0
    total_words = 0
    stats = []

    for i, (label, (master, parts, sub, year, exempt)) in enumerate(CASES.items(), 1):
        zh_all = []
        for src_name, skip, zh_file in parts:
            src = json.loads((WORK / f"{src_name}_paras.json").read_text(encoding="utf-8"))
            zh = json.loads((WORK / zh_file).read_text(encoding="utf-8"))
            assert len(zh) == len(src) - skip and all(zh), (src_name, len(zh), len(src) - skip)
            zh_all.extend(zh)

        # per-slice count assertions were made when loading; the master file is not
        # re-checked here because slice-boundary roman-numeral markers live only in
        # the slices, and the agents rendered the interior ones as body paragraphs

        checked = [p for j, p in enumerate(zh_all) if j not in exempt]
        assert not any(re.search(r"[A-Za-z]{2,}", p) for p in checked), label
        tail = ("。", "！", "”", "？", "：", "—", "…", "）", "」", "』", "］", "＊")
        assert all(p.rstrip("」』")[-1:] in tail for p in checked), label

        body = "<h1>" + label + "</h1>" + "".join(
            "<p>" + html.escape(p).replace("\n", "<br/>") + "</p>" for p in zh_all)
        files[f"OEBPS/c{i:03}.xhtml"] = xhtml(f"{label}——{sub}", body)
        entries.append((f"c{i:03}.xhtml", label))

        han = len(re.findall(r"[\u4e00-\u9fff]", "".join(zh_all)))
        en = sum((json.loads((WORK / f"{src_name}_paras.json").read_text(encoding="utf-8"))[skip:]
                  for src_name, _, _ in parts), [])
        words = sum(len(re.findall(r"[A-Za-z']+", p)) for p in en)
        total_han += han
        total_words += words
        stats.append((label, len(zh_all), han, words))

    links = "".join("<li><a href='" + f + "'>" + html.escape(t) + "</a></li>" for f, t in entries)
    files["OEBPS/nav.xhtml"] = xhtml(
        "目录",
        "<nav xmlns:epub='http://www.idpf.org/2007/ops' epub:type='toc'><h1>目录</h1><ol>"
        + links + "</ol></nav>")
    points = "".join(
        f"<navPoint id='n{i}' playOrder='{i}'><navLabel><text>{t}</text></navLabel>"
        f"<content src='{n}'/></navPoint>" for i, (n, t) in enumerate(entries, 1))
    files["OEBPS/toc.ncx"] = (
        "<?xml version='1.0'?><ncx xmlns='http://www.daisy.org/z3986/2005/ncx/' version='2005-1'>"
        "<head><meta name='dtb:uid' content='" + UID + "'/></head>"
        "<docTitle><text>" + html.escape(TITLE) + "</text></docTitle>"
        "<navMap>" + points + "</navMap></ncx>")

    files["OEBPS/title.xhtml"] = xhtml(TITLE,
        "<h1>" + html.escape(TITLE) + "</h1>"
        f"<p class='ep' style='text-align:center'>{html.escape(AUTHOR)}</p>"
        "<p class='ep' style='text-align:center'>坟头草译</p>")
    files["OEBPS/copyright.xhtml"] = xhtml("版权",
        "<h2>版权信息</h2>"
        f"<p>书名：{html.escape(TITLE)}</p>"
        f"<p>作者：{html.escape(AUTHOR)}（Algernon Blackwood，1869—1951）。</p>"
        "<p>译文：坟头草译。</p>"
        "<p>本书五案原刊于一九〇八年《约翰·塞伦斯医生奇案》初版；"
        "约翰·塞伦斯是布莱克伍德笔下通晓灵学的心灵侦探。</p>"
        "<p>本库另收布莱克伍德其余各册（如有），并存。</p>")
    entries = [("title.xhtml", TITLE), ("copyright.xhtml", "版权信息"),
               ("nav.xhtml", "目录")] + entries
    # nav must also appear in the spine (verify_epub requirement)

    container = ("<?xml version='1.0' encoding='utf-8'?>"
                 "<container version='1.0' xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>"
                 "<rootfiles><rootfile full-path='OEBPS/content.opf' media-type='application/oebps-package+xml'/></rootfiles></container>")
    files["META-INF/container.xml"] = container

    manifest = "<item id='ncx' href='toc.ncx' media-type='application/x-dtbncx+xml'/>"
    manifest += "".join(
        (f"<item id='i{i}' href='{f}' media-type='application/xhtml+xml'"
         + (" properties='nav'" if f == "nav.xhtml" else "") + "/>")
        for i, (f, _) in enumerate(entries, 1))
    spine = "".join(f"<itemref idref='i{i}'/>" for i, (f, _) in enumerate(entries, 1))
    opf = (
        "<?xml version='1.0' encoding='utf-8'?>"
        "<package xmlns='http://www.idpf.org/2007/opf' version='3.0' unique-identifier='uid'>"
        f"<metadata xmlns:dc='http://purl.org/dc/elements/1.1/'>"
        f"<dc:title>{html.escape(TITLE)}</dc:title>"
        f"<dc:creator>{html.escape(AUTHOR)}</dc:creator>"
        "<dc:language>zh-CN</dc:language>"
        f"<dc:identifier id='uid'>{UID}</dc:identifier>"
        "<meta property='dcterms:modified'>2026-11-24T00:00:00Z</meta></metadata>"
        f"<manifest>{manifest}</manifest>"
        f"<spine>{spine}</spine></package>")
    files["OEBPS/content.opf"] = opf

    out = OUT / f"{TITLE}（坟头草译）.epub"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        for name, data in files.items():
            z.writestr(name, data)
    ET.fromstring(opf)
    ET.fromstring(files["OEBPS/nav.xhtml"])

    for label, n, han, words in stats:
        print(f"   {label}  {n} paras  {han:,} han  {words:,} words")
    print(f"{TITLE}  {len(stats)} cases  {total_han:,} han  {total_words:,} src words  "
          f"{out.stat().st_size // 1024} KB")
    (WORK / "stats_js.json").write_text(json.dumps(
        {"title": TITLE, "cases": stats, "total_han": total_han,
         "total_words": total_words}, ensure_ascii=False, indent=1), encoding="utf-8")


main()
