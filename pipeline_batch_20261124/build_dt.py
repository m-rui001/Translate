"""Build 《一个做梦人的故事集：邓萨尼短篇十六则》; no API calls, no paid services.

Source: Project Gutenberg #2148, *The Works of Edgar Allan Poe, Volume 2* (Raven Edition),
fetched from the GITenberg transcription because gutenberg.org was down for maintenance.
Third Poe collection from the same volume; translated here from the English, no Chinese
version consulted. Translated by parallel sub-agents against the shelf's conventions.

Run: python -X utf8 pipeline_batch_20261124/build_dt.py
"""
from pathlib import Path
import datetime
import hashlib
import html
import json
import re
import zipfile
from xml.etree import ElementTree as ET

stamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work_batch_20261124"
TITLE = "一个做梦人的故事集：邓萨尼短篇十六则"
OUT = ROOT / "out" / f"{TITLE}（坟头草译）.epub"
UID = "urn:translate:dunsany-dreamers-tales-20261124"

# (label, source, translation, year, exempt indexes)
# exempt = epigraphs (may carry latin), ＊ separators, and Berenice's title-turned-epigraph line.
TALES = [
    ("波尔塔尼斯，海洋的旁观者", "_poltarnees_paras.json", "dt_poltarnees_zh.json", "1910", ()),
    ("布拉格达罗斯", "_blagdaross_paras.json", "dt_blagdaross_zh.json", "1910", ()),
    ("安德斯普鲁兹的疯狂", "_andelsprutz_paras.json", "dt_andelsprutz_zh.json", "1910", ()),
    ("潮起潮落之处", "_tides_paras.json", "dt_tides_zh.json", "1910", ()),
    ("贝斯穆拉", "_bethmoora_paras.json", "dt_bethmoora_zh.json", "1910", ()),
    ("雅恩河上的闲日", "_yann_paras.json", "dt_yann_zh.json", "1910", ()),
    ("剑与偶像", "_sword_idol_paras.json", "dt_sword_idol_zh.json", "1910", ()),
    ("闲城", "_idle_city_paras.json", "dt_idle_city_zh.json", "1910", ()),
    ("食大麻者", "_hashish_paras.json", "dt_hashish_zh.json", "1910", ()),
    ("可怜的老比尔", "_poor_bill_paras.json", "dt_poor_bill_zh.json", "1910", ()),
    ("乞丐", "_beggars_paras.json", "dt_beggars_zh.json", "1910", (5,)),
    ("卡卡松", "_carcassonne_paras.json", "dt_carcassonne_zh.json", "1910", ()),
    ("在萨克卡拉特", "_zaccarath_paras.json", "dt_zaccarath_zh.json", "1910", ()),
    ("田野", "_field_paras.json", "dt_field_zh.json", "1910", ()),
    ("选举日", "_poll_paras.json", "dt_poll_zh.json", "1910", ()),
    ("不幸的身体", "_body_paras.json", "dt_body_zh.json", "1910", ()),
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
    entries = []
    total_han = 0
    total_words = 0
    stats = []

    for i, (label, src_file, zh_file, year, exempt) in enumerate(TALES, 1):
        zh = json.loads((WORK / zh_file).read_text(encoding="utf-8"))
        # every slice keeps its title line as item 0, except the epilogue (cleaned)
        raw = json.loads((WORK / src_file).read_text(encoding="utf-8"))
        en = raw[1:] if label != "尾声" else raw
        assert len(zh) == len(en) and all(zh) and all(en), (label, len(zh), len(en))
        checked = [p for j, p in enumerate(zh) if j not in exempt]
        assert not any(re.search(r"[A-Za-z]{2,}", p) for p in checked), label
        tail = ("。", "！", "”", "？", "：", "—", "…", "）", "」", "』", "］")
        assert all(p.rstrip("」』")[-1:] in tail for p in checked), label

        body = "<h1>" + label + "</h1>" + "".join(
            "<p>" + html.escape(p).replace("\n", "<br/>") + "</p>" for p in zh)
        files[f"OEBPS/c{i:03}.xhtml"] = xhtml(label, body)
        entries.append((f"c{i:03}.xhtml", label))

        han = len(re.findall(r"[\u4e00-\u9fff]", "".join(zh)))
        words = len(re.findall(r"\b[\w'-]+\b", " ".join(en)))
        total_han += han
        total_words += words
        stats.append({"title": label, "year": year, "paragraphs": len(zh),
                      "han": han, "source_words": words,
                      "source_sha256": hashlib.sha256("\n\n".join(en).encode()).hexdigest()})

    note = (
        "作者：邓萨尼勋爵（Lord Dunsany，1878—1957）。"
        "《一个做梦人的故事集》初版于一九一〇年，收短篇十六篇，多自幻境中得来。"
        "英文据 Project Gutenberg 第2148号《坡全集》第二卷（Raven Edition）转录本"
        "（gutenberg.org 当次维护，取自 GITenberg 镜像）。原作属公版文本；"
        "中文由本项目直接据英文翻译、逐段校订，段落与原文一一对应。"
        "这四篇皆有不止一种中文译介，本译文未据任何既有中译本转译。"
        "本库另收邓萨尼短篇三册：《无歌之国：邓萨尼短篇七则》《风与雾：邓萨尼短篇三则》"
        "《惊奇之书：邓萨尼短篇十五则》，四册并存。"
        "原文：https://www.gutenberg.org/ebooks/2148。"
    )
    files["OEBPS/copyright.xhtml"] = xhtml(
        "版本说明", "<h1>版本说明</h1><div class='cn'>" + note + "</div>")

    all_entries = [("copyright.xhtml", "版本说明")] + entries
    links = "".join(f"<li><a href='{n}'>{t}</a></li>" for n, t in all_entries)
    files["OEBPS/nav.xhtml"] = xhtml(
        "目录",
        "<nav xmlns:epub='http://www.idpf.org/2007/ops' epub:type='toc'><h1>目录</h1><ol>"
        + links + "</ol></nav>")
    points = "".join(
        f"<navPoint id='n{i}' playOrder='{i}'><navLabel><text>{t}</text></navLabel>"
        f"<content src='{n}'/></navPoint>" for i, (n, t) in enumerate(all_entries, 1))
    files["OEBPS/toc.ncx"] = (
        "<?xml version='1.0'?><ncx xmlns='http://www.daisy.org/z3986/2005/ncx/' version='2005-1'>"
        f"<head><meta name='dtb:uid' content='{UID}'/></head><docTitle><text>{TITLE}</text>"
        "</docTitle><navMap>" + points + "</navMap></ncx>")

    manifest = ("<item id='nav' href='nav.xhtml' media-type='application/xhtml+xml' properties='nav'/>"
                "<item id='ncx' href='toc.ncx' media-type='application/x-dtbncx+xml'/>")
    manifest += "".join(f"<item id='b{i}' href='{n}' media-type='application/xhtml+xml'/>"
                        for i, (n, _) in enumerate(all_entries))
    spine = "<itemref idref='nav'/>" + "".join(f"<itemref idref='b{i}'/>"
                                               for i in range(len(all_entries)))
    files["OEBPS/content.opf"] = (
        "<?xml version='1.0'?><package xmlns='http://www.idpf.org/2007/opf' version='3.0' "
        "unique-identifier='uid'><metadata xmlns:dc='http://purl.org/dc/elements/1.1/'>"
        f"<dc:identifier id='uid'>{UID}</dc:identifier><dc:title>{TITLE}</dc:title>"
        "<dc:creator>埃德加·爱伦·坡</dc:creator><dc:language>zh-CN</dc:language>"
        f"<meta property='dcterms:modified'>{stamp}</meta></metadata><manifest>{manifest}"
        f"</manifest><spine toc='ncx'>{spine}</spine></package>")
    files["META-INF/container.xml"] = (
        "<?xml version='1.0'?><container xmlns='urn:oasis:names:tc:opendocument:xmlns:container' "
        "version='1.0'><rootfiles><rootfile full-path='OEBPS/content.opf' "
        "media-type='application/oebps-package+xml'/></rootfiles></container>")

    for doc in files.values():
        ET.fromstring(doc)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        for n, t in files.items():
            z.writestr(n, t.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)

    (WORK / "stats_dt.json").write_text(
        json.dumps({"tales": stats, "han": total_han, "source_words": total_words,
                    "size": OUT.stat().st_size}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(f"{TITLE}  {len(TALES)} tales  {total_han:,} han  {total_words:,} src words  "
          f"{OUT.stat().st_size/1024:.0f} KB")
    for s in stats:
        print(f"   {s['title']}  {s['paragraphs']} paras  {s['han']:,} han  "
              f"{s['source_words']:,} words")


if __name__ == "__main__":
    main()