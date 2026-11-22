"""Build 《枭河桥事件》; no API calls, no paid services.

Source: Project Gutenberg #375 (Ambrose Bierce, *An Occurrence at Owl Creek Bridge*, 1890),
fetched from the GITenberg transcription because gutenberg.org was down for maintenance.
The translation is this project's own; no existing Chinese version was consulted.

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

stamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
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
        ".cn{font-size:.9em;}</style></head><body>" + body + "</body></html>"
    )


def main():
    zh = json.loads((WORK / "owl_zh.json").read_text(encoding="utf-8"))
    en = json.loads((WORK / "_owl_paras.json").read_text(encoding="utf-8"))[:-1]  # drop the end-of-ebook line
    assert len(zh) == len(en) and all(zh) and all(en)

    # the shelf's invariants: nothing left in English, every paragraph closed
    assert not any(re.search(r"[A-Za-z]{2,}", p) for p in zh)
    tail = ("。", "！", "”", "？", "：", "—", "…", "）")
    # sections II and III print as bare numerals, exactly like the source
    assert all(p.rstrip("」』")[-1:] in tail or p in ("二", "三") for p in zh)

    files = {}
    body = "<h1>" + TITLE + "</h1>" + "".join(
        "<p>" + html.escape(p) + "</p>" for p in zh)
    files["OEBPS/c001.xhtml"] = xhtml(TITLE, body)

    note = (
        "作者：安布罗斯·比尔斯（Ambrose Bierce，1842—1914？）。"
        "本篇一八九〇年七月发表于《旧金山考察家报》，后收入短篇集《军旅生涯之中》（一八九一年）。"
        "英文据 Project Gutenberg 第375号转录本（gutenberg.org 当次维护，取自 GITenberg 镜像）。"
        "原作属公版文本；中文由本项目直接据英文翻译、逐段校订，段落与原文一一对应。"
        "本篇另有一种以上中文译介，本译文未据任何既有中译本转译。"
        "原文：https://www.gutenberg.org/ebooks/375。"
    )
    files["OEBPS/copyright.xhtml"] = xhtml("版本说明",
                                           "<h1>版本说明</h1><div class='cn'>" + note + "</div>")

    entries = [("copyright.xhtml", "版本说明"), ("c001.xhtml", TITLE)]
    links = "".join(f"<li><a href='{n}'>{t}</a></li>" for n, t in entries)
    files["OEBPS/nav.xhtml"] = xhtml(
        "目录",
        "<nav xmlns:epub='http://www.idpf.org/2007/ops' epub:type='toc'><h1>目录</h1><ol>"
        + links + "</ol></nav>")
    points = "".join(
        f"<navPoint id='n{i}' playOrder='{i}'><navLabel><text>{t}</text></navLabel>"
        f"<content src='{n}'/></navPoint>" for i, (n, t) in enumerate(entries, 1))
    files["OEBPS/toc.ncx"] = (
        "<?xml version='1.0'?><ncx xmlns='http://www.daisy.org/z3986/2005/ncx/' version='2005-1'>"
        f"<head><meta name='dtb:uid' content='{UID}'/></head><docTitle><text>{TITLE}</text>"
        "</docTitle><navMap>" + points + "</navMap></ncx>")

    manifest = ("<item id='nav' href='nav.xhtml' media-type='application/xhtml+xml' properties='nav'/>"
                "<item id='ncx' href='toc.ncx' media-type='application/x-dtbncx+xml'/>")
    manifest += "".join(f"<item id='b{i}' href='{n}' media-type='application/xhtml+xml'/>"
                        for i, (n, _) in enumerate(entries))
    spine = "<itemref idref='nav'/>" + "".join(f"<itemref idref='b{i}'/>"
                                               for i in range(len(entries)))
    files["OEBPS/content.opf"] = (
        "<?xml version='1.0'?><package xmlns='http://www.idpf.org/2007/opf' version='3.0' "
        f"unique-identifier='uid'><metadata xmlns:dc='http://purl.org/dc/elements/1.1/'>"
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

    stats = {
        "paragraphs": len(zh),
        "source_words": len(re.findall(r"\b[\w'-]+\b", " ".join(en))),
        "han": len(re.findall(r"[\u4e00-\u9fff]", "".join(zh))),
        "source_sha256": hashlib.sha256("\n\n".join(en).encode()).hexdigest(),
        "size": OUT.stat().st_size,
    }
    (WORK / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n",
                                     encoding="utf-8")
    print(f"{TITLE}  {stats['paragraphs']} paras  {stats['han']:,} han  "
          f"{stats['source_words']:,} src words  {stats['size']/1024:.0f} KB")
    print(f"  -> {OUT.name}")


if __name__ == "__main__":
    main()