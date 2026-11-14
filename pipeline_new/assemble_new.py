"""Assemble translated chapters into one EPUB per book.

Deliberately simpler than the whale assembler: these two novels are plain prose
(no verse, no speaker labels, no front-matter extracts), so a chapter is just a
heading plus paragraphs.

    python pipeline_new/assemble_new.py --book soledad

Superseded for `soledad` by `pipeline_overhaul/assemble.py`: this script writes an
EPUB 2 with an NCX only and does not lift a chapter heading out of the body, so
running it after the overhaul assembler silently reverts both the table of
contents and the front matter. Kept for `zauberberg`, which the overhaul
assembler does not cover.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import zipfile
from xml.dom import minidom

sys.path.insert(0, 'E:/Translate/pipeline_overhaul')
import copyright as cpr  # noqa: E402

BOOKS = {
    "soledad": {
        "src": "E:/Translate/work_soledad/src",
        "out": "E:/Translate/work_soledad/out",
        "epub": "E:/Translate/百年孤独（坟头草译）.epub",
        "title": "百年孤独",
        "author": "加夫列尔·加西亚·马尔克斯",
        "lang_src": "Cien años de soledad",
    },
    "zauberberg": {
        "src": "E:/Translate/work_zauberberg/src",
        "out": "E:/Translate/work_zauberberg/out",
        "epub": "E:/Translate/魔山（坟头草译）.epub",
        "title": "魔山",
        "author": "托马斯·曼",
        "lang_src": "Der Zauberberg",
        # the EPUB splits chapters across files, so the seven chapters have to
        # be rebuilt from the source headings rather than trusted to the split
        "sections": [
            ("导言", ["index_split_001"]),
            ("前言", ["index_split_002"]),
            ("第一章", ["index_split_003"]),
            ("第二章", ["index_split_004"]),
            ("第三章", ["index_split_005"]),
            ("第四章", ["index_split_006", "index_split_007"]),
            ("第五章", ["index_split_008", "index_split_009",
                        "index_split_010", "index_split_011"]),
            ("第六章", ["index_split_012", "index_split_013",
                        "index_split_014", "index_split_015"]),
            ("第七章", ["index_split_016", "index_split_017", "index_split_018",
                        "index_split_019", "index_split_020", "index_split_021"]),
        ],
    },
}

STYLE = ("body{line-height:1.9;font-family:serif} "
         "h1{text-align:center;margin:3em 0 1em;font-size:1.4em} "
         "p{text-indent:2em;margin:0 0 .55em;text-align:justify}")


def split_paras(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


ITAL = re.compile(r"⟦i⟧(.*?)⟦/i⟧", re.S)
LATIN_RUN = re.compile(r"(?:[A-Za-zÀ-ÿ]{2,}[ ,.;:]+){5,}")
CJK_SPACE = re.compile(r"(?<=[\u4e00-\u9fff\u3001-\u303f\uff01-\uff65])[ \t]+"
                       r"(?=[\u4e00-\u9fff\u3001-\u303f\uff01-\uff65])")


def para_html(p: str) -> str:
    # the translator works in mainland punctuation: corner brackets that a
    # model occasionally emits are the same mark, just typed with a Japanese
    # keyboard
    p = p.replace("「", "“").replace("」", "”")
    p = CJK_SPACE.sub("", p)
    s = html.escape(p, quote=False)
    s = ITAL.sub(r"<em>\1</em>", s)
    return "<p>" + s.replace("⟦i⟧", "").replace("⟦/i⟧", "") + "</p>"


def chapter_xhtml(title: str, paras: list[str]) -> str:
    body = "".join(para_html(p) for p in paras)
    return ("<?xml version='1.0' encoding='utf-8'?>\n<!DOCTYPE html>\n"
            "<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='zh-CN'>"
            "<head><meta charset='utf-8'/><title>" + html.escape(title) + "</title>"
            "<style>" + STYLE + "</style></head><body>"
            f"<h1>{html.escape(title)}</h1>{body}</body></html>")


HEAD = re.compile(r"^第[一二三四五六七八九十百零\d]{1,4}[章回节]$")


def take_heading(paras: list[str]) -> str | None:
    """The pipeline renders the chapter heading as the first paragraph."""
    if not paras:
        return None
    if HEAD.match(paras[0]):
        return paras.pop(0)
    # a heading long enough to look like prose is sometimes echoed back
    # untranslated; the section already has a title, so the echo is just noise
    first = paras[0]
    if len(first) < 90 and sum(c.isascii() and c.isalpha() for c in first) > 0.6 * len(first):
        return paras.pop(0)
    return None


CN_DIGITS = "零一二三四五六七八九"


def cn_number(n: int) -> str:
    if n <= 10:
        return "十" if n == 10 else CN_DIGITS[n]
    if n < 20:
        return "十" + CN_DIGITS[n % 10]
    return CN_DIGITS[n // 10] + "十" + (CN_DIGITS[n % 10] if n % 10 else "")


def title_from_cid(cid: str) -> str | None:
    """`capitulo016` → 第十六章, for chapters whose heading the model dropped."""
    m = re.fullmatch(r"capitulo0*(\d+)", cid)
    return f"第{cn_number(int(m.group(1)))}章" if m else None


def load_chapter(cfg: dict, cid: str) -> list[str] | None:
    """Paragraphs of one source file, read from the chunk outputs.

    `chapter.md` is written once when a chapter finishes, but a chunk can be
    re-run afterwards, and the stale chapter file then disagrees with the text
    the pipeline actually produced. The chunk `final.txt` files are the source
    of truth, so they are read directly; `chapter.md` is only a fallback for
    chapters translated before chunking.
    """
    spec_p = os.path.join(os.path.dirname(cfg["out"]), "chunks", cid + ".json")
    if os.path.exists(spec_p):
        spec = json.load(open(spec_p, encoding="utf-8"))
        parts = []
        for k in range(len(spec["chunks"])):
            p = os.path.join(cfg["out"], cid, f"c{k:02d}", "final.txt")
            if not os.path.exists(p):
                return None
            parts.append(open(p, encoding="utf-8").read())
        return split_paras("\n\n".join(parts))
    p = os.path.join(cfg["out"], cid, "chapter.md")
    if os.path.exists(p):
        return split_paras(open(p, encoding="utf-8").read())
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, choices=sorted(BOOKS))
    ap.add_argument("--require-all", action="store_true",
                    help="fail instead of skipping chapters that are not translated yet")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    cfg = BOOKS[a.book]

    ids = sorted(os.path.splitext(f)[0] for f in os.listdir(cfg["src"])
                 if f.endswith(".json") and f != "index.json")
    sections = cfg.get("sections") or [(None, [cid]) for cid in ids]

    files, manifest, spine, nav = {}, [], [], []
    total_han = total_paras = missing = 0
    for i, (title, group) in enumerate(sections, 1):
        paras, head = [], None
        for cid in group:
            part = load_chapter(cfg, cid)
            if part is None:
                print(f"  MISSING {cid}")
                missing += 1
                continue
            h = take_heading(part)
            head = head or h
            paras += part
        if not paras:
            continue
        title = title or head or title_from_cid(group[0]) or (group[0] if group else f"第{i}章")
        fn = f"c{i:03d}.xhtml"
        files[fn] = chapter_xhtml(title, paras)
        manifest.append(f"<item id='c{i}' href='{fn}' media-type='application/xhtml+xml'/>")
        spine.append(f"<itemref idref='c{i}'/>")
        nav.append((title, fn))
        han = sum(1 for ch in "".join(paras) if "一" <= ch <= "鿿")
        total_han += han
        total_paras += len(paras)
        print(f"  {i:2d} {title:8s} paras={len(paras):4d} han={han:7,}  "
              f"{','.join(group)[:40]}")
        # quoted foreign phrases are deliberate — Mann and Márquez both quote in
        # Latin and French — so only a paragraph that is mostly foreign text,
        # outside the italic markers, counts as a missed translation
        for p in paras:
            m = LATIN_RUN.search(ITAL.sub("", p))
            if m and len(m.group(0)) > 0.4 * len(p):
                print(f"  !! untranslated in {title}: {p[:60]}")

    if missing and a.require_all:
        print(f"ABORT: {missing} source file(s) have no translation")
        return 2

    src_title = cfg.get("lang_src") or cfg["title"]
    files["copyright.xhtml"] = cpr.page(cfg["title"], src_title, cfg["author"], STYLE)
    manifest.insert(0, "<item id='cr' href='copyright.xhtml' "
                       "media-type='application/xhtml+xml'/>")
    spine.insert(0, "<itemref idref='cr'/>")
    nav.insert(0, ("版权", "copyright.xhtml"))

    toc = ["<?xml version='1.0' encoding='utf-8'?>",
           "<ncx xmlns='http://www.daisy.org/z3986/2005/ncx/' version='2005-1'>",
           f"<head><meta name='dtb:uid' content='urn:new-{a.book}'/></head>",
           f"<docTitle><text>{cfg['title']}</text></docTitle><navMap>"]
    for i, (t, fn) in enumerate(nav, 1):
        toc.append(f"<navPoint id='n{i}' playOrder='{i}'><navLabel><text>{html.escape(t)}"
                   f"</text></navLabel><content src='{fn}'/></navPoint>")
    toc.append("</navMap></ncx>")
    files["toc.ncx"] = "\n".join(toc)

    files["content.opf"] = f"""<?xml version='1.0' encoding='utf-8'?>
<package xmlns='http://www.idpf.org/2007/opf' version='2.0' unique-identifier='uid'>
<metadata xmlns:dc='http://purl.org/dc/elements/1.1/'>
<dc:title>{cfg['title']}</dc:title>
<dc:creator>{cfg['author']}</dc:creator>
<dc:contributor>坟头草 译</dc:contributor>
<dc:language>zh-CN</dc:language>
<dc:identifier id='uid'>urn:new-{a.book}</dc:identifier>
</metadata>
<manifest>
<item id='ncx' href='toc.ncx' media-type='application/x-dtbncx+xml'/>
{''.join(manifest)}
</manifest>
<spine toc='ncx'>
{''.join(spine)}
</spine>
</package>"""

    files["container.xml"] = ("<?xml version='1.0'?><container version='1.0' "
                              "xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>"
                              "<rootfiles><rootfile full-path='OEBPS/content.opf' "
                              "media-type='application/oebps-package+xml'/></rootfiles></container>")
    errors = 0
    for fn, content in sorted(files.items()):
        try:
            minidom.parseString(content.encode("utf-8"))
        except Exception as e:  # noqa: BLE001
            errors += 1
            print(f"XML ERROR {fn}: {str(e)[:160]}")

    with zipfile.ZipFile(cfg["epub"], "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", zipfile.ZIP_STORED)
        for fn, content in files.items():
            z.writestr("META-INF/container.xml" if fn == "container.xml" else "OEBPS/" + fn,
                       content)
    print("-" * 60)
    print(f"TOTAL han={total_han:,} paras={total_paras:,} xml_errors={errors}")
    print("epub:", cfg["epub"])
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
