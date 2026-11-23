# -*- coding: utf-8 -*-
"""Build 《马人：布莱克伍德长篇》.

Source: PG #9964 (Algernon Blackwood, The Centaur, 1911) via the GITenberg
mirror The-Centaur_9964. The novel runs in forty-six roman-numbered sections;
the source was cut into nine consecutive slices for nine parallel sub-agents,
then concatenated here. Section numerals were stripped from the slices before
dispatch, so the paragraph counts match one to one.
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
TITLE = "马人：布莱克伍德长篇"
AUTHOR = "阿尔杰农·布莱克伍德"
UID = "urn:translate:blackwood-centaur-20261124"

SLICES = [(k, f"cent_{k}_zh.json") for k in "abcdefghi"]
# slice-internal para indexes exempt from the punctuation / Latin assertions:
# star separators, poem lines whose stanza continues into the next paragraph,
# and foreign words quoted as words (unheimlich, Urwald/Urwelt, French patois,
# Vielen Dank).
EXEMPT = {
    "a": (), "b": (96, 102), "c": (),
    "d": (55, 124), "e": (66,), "f": (80, 83, 85), "g": (98,),
    "h": (), "i": (87,),
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
    zh_all, en_all = [], []
    for key, zh_file in SLICES:
        zh = json.loads((WORK / zh_file).read_text(encoding="utf-8"))
        src = json.loads((WORK / f"_centc_{key}_paras.json").read_text(encoding="utf-8"))
        assert len(zh) == len(src) and all(zh) and all(src), (key, len(zh), len(src))
        zh_all.extend(zh)
        en_all.extend(src)

    checked = []
    for key, zh_file in SLICES:
        zh = json.loads((WORK / zh_file).read_text(encoding="utf-8"))
        checked.extend(p for i, p in enumerate(zh) if i not in EXEMPT[key])
    assert not any(re.search(r"[A-Za-z]{2,}", p) for p in checked), "latin leak"
    tail = ("。", "！", "”", "？", "：", "—", "…", "）", "」", "』", "＊")
    assert all(p.rstrip("」』")[-1:] in tail for p in checked), "punctuation"

    body = "".join("<p>" + html.escape(p).replace("\n", "<br/>") + "</p>" for p in zh_all)
    entries = [("title.xhtml", TITLE), ("copyright.xhtml", "版权信息"),
               ("nav.xhtml", "目录"), ("c001.xhtml", "马人")]
    links = "".join("<li><a href='" + f + "'>" + html.escape(t) + "</a></li>"
                    for f, t in entries)
    files = {
        "OEBPS/c001.xhtml": xhtml(TITLE, "<h1>马人</h1>" + body),
        "OEBPS/title.xhtml": xhtml(TITLE,
            "<h1>" + html.escape(TITLE) + "</h1>"
            f"<p class='ep' style='text-align:center'>{html.escape(AUTHOR)}</p>"
            "<p class='ep' style='text-align:center'>坟头草译</p>"),
        "OEBPS/copyright.xhtml": xhtml("版权",
            "<h2>版权信息</h2>"
            f"<p>书名：{html.escape(TITLE)}</p>"
            f"<p>作者：{html.escape(AUTHOR)}（Algernon Blackwood，1869—1951）。</p>"
            "<p>译文：坟头草译。</p>"
            "<p>《马人》初版于一九一一年。爱尔兰人特伦斯·奥马利在开往高加索的轮船上"
            "结识一位俄国农夫和他的儿子，渐渐认出他们是一个远古诗中种族的最后幸存者。</p>"
            "<p>本库另收《约翰·塞伦斯医生奇案：布莱克伍德灵异五案》"
            "《温迪戈：布莱克伍德荒原异闻》，三册并存。</p>"),
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
    (WORK / "stats_centaur.json").write_text(json.dumps(
        {"title": TITLE, "paras": len(zh_all), "han": han, "words": words},
        ensure_ascii=False, indent=1), encoding="utf-8")


main()