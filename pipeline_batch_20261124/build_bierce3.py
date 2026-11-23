"""Build 《窗户上的眼：比尔斯短篇五则》; no API calls, no paid services.

Source: Project Gutenberg #13334, *The Collected Works of Ambrose Bierce, Volume 2:
In the Midst of Life*, fetched from the GITenberg transcription. Third Bierce collection
from the same volume; translated by parallel sub-agents.

Run: python -X utf8 pipeline_batch_20261124/build_bierce3.py
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
TITLE = "窗户上的眼：比尔斯短篇五则"
OUT = ROOT / "out" / f"{TITLE}（坟头草译）.epub"
UID = "urn:translate:bierce-third-five-20261124"

# (label, source, translation, year, exempt indexes)
# exempt = roman-numeral section markers, the capitalized section headings the source
# prints as unpunctuated lines, and the initials signature 「J.R.C.」
TALES = [
    ("可怕的家伙", "_holyster_paras.json", "bierce_holyster_zh.json", "1889", (0, 1, 4, 8, 19, 31)),
    # para 1 cites the Spanish quien sabe as the nickname's origin -- a word as a word
    ("合宜的环境", "_suitable_paras.json", "bierce_suitable_zh.json", "1889", (7, 25, 29, 36, 38)),
    ("雷德霍斯的贵妇", "_redhorse_paras.json", "bierce_redhorse_zh.json", "1892", ()),
    ("窗户上的眼", "_panther_paras.json", "bierce_panther_zh.json", "1891",
     (0, 1, 17, 18, 33, 34, 49, 50)),
    ("钉死的窗户", "_boarded_paras.json", "bierce_boarded_zh.json", "1891", ()),
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
        en = json.loads((WORK / src_file).read_text(encoding="utf-8"))[1:]
        assert len(zh) == len(en) and all(zh), (label, len(zh), len(en))
        checked = [p for j, p in enumerate(zh) if j not in exempt]
        assert not any(re.search(r"[A-Za-z]{2,}", p) for p in checked), label
        tail = ("。", "！", "”", "？", "：", "—", "…", "）", "」", "』")
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
        "作者：安布罗斯·比尔斯（Ambrose Bierce，1842—1914？）。"
        "五篇出自短篇集《军旅生涯之中》（In the Midst of Life，1891）及其增订各版，"
        "原刊年份分别为：《可怕的家伙》一八八九年、《合宜的环境》一八八九年、"
        "《雷德霍斯的贵妇》一八九二年、《窗户上的眼》一八九一年、《钉死的窗户》一八九一年。"
        "英文据 Project Gutenberg 第13334号《比尔斯全集》第二卷转录本"
        "（gutenberg.org 当次维护，取自 GITenberg 镜像）。原作属公版文本；"
        "中文由本项目直接据英文翻译、逐段校订，段落与原文一一对应。"
        "这些篇目皆有不止一种中文译介，本译文未据任何既有中译本转译。"
        "本册与《枭河桥事件》《奇卡莫加》《死人监视者》同出一源，四册并存。"
        "原文：https://www.gutenberg.org/ebooks/13334。"
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
        "<dc:creator>安布罗斯·比尔斯</dc:creator><dc:language>zh-CN</dc:language>"
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

    (WORK / "stats_bierce3.json").write_text(
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