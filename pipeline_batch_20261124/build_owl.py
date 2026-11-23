"""Build 《枭河桥事件》; no API calls, no paid services.

Source: Project Gutenberg #375 (Ambrose Bierce, *An Occurrence at Owl Creek Bridge*, 1890),
fetched from the GITenberg transcription because gutenberg.org was down for maintenance.
The translation is this project's own, paragraph for paragraph.

Run: python -X utf8 pipeline_batch_20261124/build_owl.py
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
TITLE = "枭河桥事件"
OUT = ROOT / "out" / f"{TITLE}（坟头草译）.epub"
UID = "urn:translate:owl-creek-20261124"

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
    zh = json.loads((WORK / "owl_zh.json").read_text(encoding="utf-8"))
    src = json.loads((WORK / "_owl_paras.json").read_text(encoding="utf-8"))[:-1]
    assert len(zh) == len(src), (len(zh), len(src))
    assert not any(re.search(r"[A-Za-z]{2,}", p) for p in zh)
    tail = ("。", "！", "”", "？", "：", "—", "…", "）")
    assert all(p.rstrip("」』")[-1:] in tail or p in ("二", "三") for p in zh)

    body = "<h1>" + TITLE + "</h1>" + "".join(
        "<p>" + html.escape(p).replace("\n", "<br/>") + "</p>" for p in zh)
    files = {"OEBPS/c001.xhtml": xhtml(TITLE, body)}
    entries = [("copyright.xhtml", "版本说明"), ("c001.xhtml", TITLE)]

    note = (
        "作者：安布罗斯·比尔斯（Ambrose Bierce，1842—1914？）。"
        "本篇一八九〇年七月发表于《旧金山考察家报》，后收入短篇集《军旅生涯之中》（一八九一年）。"
        "英文据 Project Gutenberg 第375号转录本（gutenberg.org 当次维护，取自 GITenberg 镜像）。"
        "原作属公版文本；中文由本项目直接据英文翻译、逐段校订，段落与原文一一对应。"
        "本篇另有一种以上中文译介，本译文未据任何既有中译本转译。"
        "原文：https://www.gutenberg.org/ebooks/375。"
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

    (WORK / "stats_owl.json").write_text(
        json.dumps({"tales": [{"title": TITLE, "year": "1890", "paragraphs": len(zh),
                               "han": len(re.findall(r"[\u4e00-\u9fff]", "".join(zh))),
                               "source_words": len(re.findall(r"\b[\w'-]+\b", " ".join(src)))}],
                    "han": len(re.findall(r"[\u4e00-\u9fff]", "".join(zh))),
                    "source_words": len(re.findall(r"\b[\w'-]+\b", " ".join(src))),
                    "size": OUT.stat().st_size}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(f"{TITLE}  {len(zh)} paras  {len(re.findall(r'[\u4e00-\u9fff]', ''.join(zh))):,} han  "
          f"{len(re.findall(r'\\b[\\w\'-]+\\b', ' '.join(src))):,} src words  "
          f"{OUT.stat().st_size/1024:.0f} KB")
    print(f"  -> {OUT.name}")


if __name__ == "__main__":
    main()