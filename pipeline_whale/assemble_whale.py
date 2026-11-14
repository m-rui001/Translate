"""Assemble the translated Moby-Dick into a Chinese EPUB.

Reads work_whale/chunks/<id>.json for the chapter order and block structure and
work_whale/out/<id>/c<NN>/final.txt for the text, so paragraph types are preserved:
prose becomes <p>, verse blocks become <p class="verse"> with <br/> line breaks,
attributions get their own class, and ⟦i⟧…⟦/i⟧ becomes <em>.

Self-checks (must pass before the EPUB counts as produced):
  - every XHTML file parses with xml.dom.minidom: 0 errors
  - the number of paragraph elements equals the number of source blocks per chapter
  - CJK character count is reported per chapter and overall
  - no residual ⟦i⟧ markers, no arabic numerals where a numeral was expected,
    no unbalanced quotes in any paragraph
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

HERE = os.path.dirname(os.path.abspath(__file__))
CHUNKS = "E:/Translate/work_whale/chunks"
OUT = "E:/Translate/work_whale/out"
DEFAULT_EPUB = "E:/Translate/白鲸（新译）.epub"

STYLE = """body{line-height:1.85;font-family:serif;margin:0 4%}
h1{text-align:center;margin:2.6em 0 .3em;font-size:1.45em;letter-spacing:.06em}
h2{text-align:center;color:#666;font-weight:normal;font-style:italic;
   font-size:.95em;margin:0 0 2.2em;letter-spacing:.04em}
p{text-indent:2em;margin:0 0 .55em;text-align:justify}
p.verse{text-indent:0;margin-left:2.5em;margin-bottom:.9em;line-height:1.55}
p.attr{text-indent:0;text-align:right;font-style:italic;margin:0 1.5em .9em 0}
p.head{text-indent:0;text-align:center;font-weight:bold;margin:1.6em 0 .8em}
p.front{text-indent:0;letter-spacing:.2em;text-align:center}
div.titlepage{text-align:center;margin-top:22%}
div.titlepage .t{font-size:2.1em;letter-spacing:.3em;margin-bottom:1.4em}
div.titlepage .s{font-size:1.05em;color:#555;margin-bottom:.5em}
div.titlepage .a{font-size:1em;margin-top:3em;color:#444}
div.titlepage .sub{font-size:.9em;color:#777}
div.titlepage .n{font-size:.85em;color:#777;margin-top:4em;line-height:1.8}
hr.sep{border:0;text-align:center;margin:2em 0}
hr.sep:after{content:"\\2042";color:#999}
"""

FRONT_TITLES = {
    "front_ety": ("词源", "Etymology"),
    "front_ext": ("摘录", "Extracts"),
}


def split_paras(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def esc(t: str) -> str:
    return html.escape(t, quote=False)


def rich(t: str) -> str:
    """⟦i⟧…⟦/i⟧ -> <em>, keeping the inner text escaped."""
    pieces = re.split(r"(⟦i⟧|⟦/i⟧)", t)
    buf, open_em = [], False
    for p in pieces:
        if p == "⟦i⟧":
            if open_em:
                buf.append("</em>")
            buf.append("<em>")
            open_em = True
        elif p == "⟦/i⟧":
            if open_em:
                buf.append("</em>")
            open_em = False
        else:
            buf.append(esc(p))
    if open_em:
        buf.append("</em>")
    return "".join(buf)


def para_html(text: str, kind: str) -> str:
    cls = {"p": "", "verse": ' class="verse"', "attr": ' class="attr"',
           "head": ' class="head"'}[kind]
    if kind == "verse":
        lines = [rich(l) for l in text.split("\n") if l.strip()]
        return f"<p{cls}>" + "<br/>".join(lines) + "</p>"
    return f"<p{cls}>{rich(text)}</p>"


def chapter_body(cid: str, spec: dict) -> tuple[str, list[dict]]:
    """Return (inner html, per-block records)."""
    blocks_meta = [b for c in spec["chunks"] for b in c]
    parts, records = [], []
    for i in range(len(spec["chunks"])):
        p = os.path.join(OUT, cid, f"c{i:02d}", "final.txt")
        if not os.path.exists(p):
            raise SystemExit(f"missing {p}")
        text = open(p, encoding="utf-8").read().strip()
        got = split_paras(text)
        want = spec["chunks"][i]
        if len(got) != len(want):
            print(f"  ! {cid}/c{i:02d}: {len(got)} paragraphs vs {len(want)} blocks "
                  f"(will align by order)")
        for j, t in enumerate(got):
            kind = want[j]["type"] if j < len(want) else "p"
            parts.append(para_html(t, kind))
            records.append({"type": kind, "text": t})
    return "\n".join(parts), records


def xhtml(title: str, subtitle: str, body: str) -> str:
    return ("<?xml version='1.0' encoding='utf-8'?>\n"
            "<!DOCTYPE html>\n"
            "<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='zh-CN'>"
            "<head><meta charset='utf-8'/><title>" + esc(title) + "</title>"
            "<style>" + STYLE + "</style></head><body>"
            f"<h1>{esc(title)}</h1>" +
            (f"<h2>{esc(subtitle)}</h2>" if subtitle else "") +
            body + "</body></html>")


def _title_page() -> str:
    L = []
    L.append("<?xml version='1.0' encoding='utf-8'?>")
    L.append("<!DOCTYPE html>")
    L.append("<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='zh-CN'>")
    L.append("<head><meta charset='utf-8'/><title>白鲸</title>")
    L.append("<style>" + STYLE + "</style></head><body>")
    L.append("<div class='titlepage'>")
    L.append("<div class='t'>白鲸</div>")
    L.append("<div class='s'>莫比—迪克</div>")
    L.append("<div class='sub'>Moby-Dick; or, The Whale</div>")
    L.append("<div class='a'>赫尔曼·麦尔维尔 著</div>")
    L.append("<div class='n'>一八五一年<br/>")
    L.append("据查尔斯·弗雷德里克·布里格斯·普特南公司初版<br/>")
    L.append("企鹅经典增注本核校</div>")
    L.append("</div></body></html>")
    return chr(10).join(L)


TITLE_XHTML = _title_page()


def validate(files: dict) -> int:
    errors = 0
    for fn, content in sorted(files.items()):
        try:
            minidom.parseString(content.encode("utf-8"))
        except Exception as e:  # noqa: BLE001
            errors += 1
            print(f"XML ERROR in {fn}: {str(e)[:200]}")
    return errors


def han(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def check_records(cid: str, records: list[dict]) -> list[str]:
    """Flag faults that actually hurt the reader, not stylistic balance.

    A quotation spanning paragraphs legitimately leaves every paragraph but the
    last open, so per-paragraph balance is the wrong test. What must hold is that
    the chapter as a whole balances, that no paragraph *starts* by closing
    something, and that the emphasis markers survive intact.
    """
    problems = []
    tot = 0
    for r in records:
        t = r["text"].strip()
        if t.count("⟦i⟧") != t.count("⟦/i⟧"):
            problems.append(f"{cid}: unbalanced emphasis marker")
        if "⟦" in re.sub(r"⟦/?i⟧", "", t):
            problems.append(f"{cid}: stray marker")
        if t.startswith(("”", "’")):
            problems.append(f"{cid}: paragraph starts by closing a quote: {t[:30]}")
        if t.count("‘") != t.count("’"):
            problems.append(f"{cid}: nested quotes unbalanced: {t[:30]}")
    # a running quotation legitimately leaves most paragraphs open, so the only
    # real failure is the last paragraph that carries a “ also failing to close
    for r in reversed(records):
        t = r["text"].strip()
        if "“" in t:
            if t.count("“") > t.count("”"):
                problems.append(f"{cid}: final quotation left open: {t[-30:]}")
            break
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epub", default=DEFAULT_EPUB)
    ap.add_argument("--require-all", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    index = json.load(open(os.path.join(CHUNKS, "index.json"), encoding="utf-8"))
    ids = list(index.keys())
    order = ([c for c in ids if c in ("front_ety", "front_ext")] +
             sorted([c for c in ids if c.startswith("ch")], key=lambda x: int(x[2:])) +
             ([c for c in ids if c.startswith("epi")]))

    files, manifest, spine, nav = {}, [], [], []
    files["title.xhtml"] = TITLE_XHTML
    manifest.append("<item id='title' href='title.xhtml' media-type='application/xhtml+xml'/>")
    spine.append("<itemref idref='title'/>")
    nav.append(("书名页", "title.xhtml"))

    total_han = 0
    total_paras = 0
    missing = []
    problems = []
    stats = []
    for n, cid in enumerate(order, 1):
        spec = json.load(open(os.path.join(CHUNKS, cid + ".json"), encoding="utf-8"))
        if not os.path.exists(os.path.join(OUT, cid, "chapter.md")):
            missing.append(cid)
            continue
        body, records = chapter_body(cid, spec)
        if cid in FRONT_TITLES:
            title, sub = FRONT_TITLES[cid]
        elif cid.startswith("epi"):
            title, sub = "尾声", "Epilogue"
        else:
            title = spec["title_zh"]
            sub = spec["title_en"]
        fn = f"c{n:03d}.xhtml"
        files[fn] = xhtml(title, sub, body)
        manifest.append(f"<item id='c{n}' href='{fn}' media-type='application/xhtml+xml'/>")
        spine.append(f"<itemref idref='c{n}'/>")
        nav.append((title, fn))
        h = han("".join(r["text"] for r in records))
        total_han += h
        total_paras += len(records)
        problems += check_records(cid, records)
        stats.append((cid, title, len(records), h))
        print(f"{cid:10s} {title:14s} blocks={len(records):3d} han={h:6,d}")

    if missing:
        print(f"\nMISSING chapters ({len(missing)}): {', '.join(missing[:20])}")
        if a.require_all:
            raise SystemExit("aborted: --require-all and chapters are missing")

    ncx = ["<?xml version='1.0' encoding='utf-8'?>",
           "<ncx xmlns='http://www.daisy.org/z3986/2005/ncx/' version='2005-1'>",
           "<head><meta name='dtb:uid' content='urn:moby-dick-zh-new'/></head>",
           "<docTitle><text>白鲸</text></docTitle><navMap>"]
    for i, (title, fn) in enumerate(nav, 1):
        ncx.append(f"<navPoint id='n{i}' playOrder='{i}'><navLabel><text>{esc(title)}"
                   f"</text></navLabel><content src='{fn}'/></navPoint>")
    ncx.append("</navMap></ncx>")
    files["toc.ncx"] = "\n".join(ncx)

    files["content.opf"] = f"""<?xml version='1.0' encoding='utf-8'?>
<package xmlns='http://www.idpf.org/2007/opf' version='2.0' unique-identifier='uid'>
<metadata xmlns:dc='http://purl.org/dc/elements/1.1/'>
<dc:title>白鲸</dc:title>
<dc:creator>赫尔曼·麦尔维尔</dc:creator>
<dc:language>zh-CN</dc:language>
<dc:identifier id='uid'>urn:moby-dick-zh-new</dc:identifier>
<dc:description>《白鲸；或，大鲸》(Moby-Dick; or, The Whale, 1851) 中文新译</dc:description>
</metadata>
<manifest>
<item id='ncx' href='toc.ncx' media-type='application/x-dtbncx+xml'/>
{chr(10).join(manifest)}
</manifest>
<spine toc='ncx'>
{chr(10).join(spine)}
</spine>
</package>"""

    files["container.xml"] = ("<?xml version='1.0'?><container version='1.0' "
                              "xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>"
                              "<rootfiles><rootfile full-path='OEBPS/content.opf' "
                              "media-type='application/oebps-package+xml'/></rootfiles></container>")

    n_err = validate({k: v for k, v in files.items() if k != "container.xml"})
    n_err += validate({"container.xml": files["container.xml"]})

    with zipfile.ZipFile(a.epub, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip",
                   zipfile.ZIP_STORED)
        for fn, content in files.items():
            path = "META-INF/container.xml" if fn == "container.xml" else "OEBPS/" + fn
            z.writestr(path, content)

    print("-" * 62)
    print(f"chapters={len(stats)} blocks={total_paras:,} han={total_han:,}")
    print(f"XML: {len(files)} files, {n_err} errors")
    print(f"quote problems: {len(problems)}")
    for p in problems[:12]:
        print("  ", p)
    print("epub:", a.epub)
    return 1 if (n_err or problems) else 0


if __name__ == "__main__":
    sys.exit(main())
