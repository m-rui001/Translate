"""Split 追忆似水年华 volume 5 (女囚) into its three chapters and unify two names.

The source has three chapters (CHAPITRE PREMIER/DEUXIÈME/TROISIÈME) but the EPUB
carried the whole volume as one file, so the TOC had an empty node. The chapter
boundaries are recoverable because the translation kept the chapter subtitles as
stand-alone paragraphs: 「韦尔迪兰夫妇与德·夏吕斯先生闹翻了。」 and 「阿尔贝蒂娜的失踪」.
"""
import html, os, re, shutil, zipfile
from xml.etree import ElementTree as ET

SRC = "out/追忆似水年华（坟头草译）.epub"
NAMES = [("夏吕斯", "夏尔吕"), ("维尔帕里齐", "维尔帕里西")]

with zipfile.ZipFile(SRC) as z:
    v5 = z.read("OEBPS/v5_01.xhtml").decode("utf-8")
    nav = z.read("OEBPS/nav.xhtml").decode("utf-8")
    ncx = z.read("OEBPS/toc.ncx").decode("utf-8")
    opf = z.read("OEBPS/content.opf").decode("utf-8")
    others = {i.filename: z.read(i.filename) for i in z.infolist()}

head, body = v5.split("<body>", 1)
body_inner, tail = body.rsplit("</body>", 1)
h1 = re.findall(r"<h1>.*?</h1>", body_inner, re.S)
ps = re.findall(r"<p[^>]*>.*?</p>", re.sub(r"<h1>.*?</h1>", "", body_inner, count=1), re.S)
assert len(ps) == 368, len(ps)
txt = lambda p: re.sub(r"<[^>]+>", "", html.unescape(p))
assert txt(ps[255]).startswith("韦尔迪兰夫妇与德·夏吕斯先生闹翻了")
assert txt(ps[320]).startswith("阿尔贝蒂娜的失踪")


def page(title, paras, keep_h1):
    return head + "<body>" + (h1[0] if keep_h1 else title) + "".join(paras) + "</body>" + tail


p1 = page("", ps[:255], True)
p2 = page("<h2>第二章韦尔迪兰夫妇与夏尔吕先生反目</h2>", ps[256:320], False)
p3 = page("<h2>第三章阿尔贝蒂娜的失踪</h2>", ps[321:], False)

old = "<li><a href='v5_01.xhtml'>第五卷 女囚</a></li>"
assert old in nav
nav = nav.replace(old, "<li><a href='v5_01.xhtml'>第五卷 女囚</a>\n      <ol>\n"
                       "        <li><a href='v5_02.xhtml'>第二章 韦尔迪兰夫妇与夏尔吕先生反目</a></li>\n"
                       "        <li><a href='v5_03.xhtml'>第三章 阿尔贝蒂娜的失踪</a></li>\n"
                       "      </ol>\n    </li>")

oldn = ("<navPoint id='n22' playOrder='22'><navLabel><text>第五卷 女囚</text></navLabel>"
        "<content src='v5_01.xhtml'/>\n</navPoint>")
assert oldn in ncx
ncx = ncx.replace(oldn,
    "<navPoint id='n22' playOrder='22'><navLabel><text>第五卷 女囚</text></navLabel><content src='v5_01.xhtml'/>\n"
    "  <navPoint id='n22a' playOrder='23'><navLabel><text>第二章 韦尔迪兰夫妇与夏尔吕先生反目</text></navLabel><content src='v5_02.xhtml'/></navPoint>\n"
    "  <navPoint id='n22b' playOrder='24'><navLabel><text>第三章 阿尔贝蒂娜的失踪</text></navLabel><content src='v5_03.xhtml'/></navPoint>\n"
    "</navPoint>")
c = [0]
ncx = re.sub(r"playOrder='\d+'", lambda m: "playOrder='%d'" % (c.__setitem__(0, c[0] + 1) or c[0]), ncx)

oldi = "<item id='s17' href='v5_01.xhtml' media-type='application/xhtml+xml'/>"
opf = opf.replace(oldi, oldi + "<item id='s17b' href='v5_02.xhtml' media-type='application/xhtml+xml'/>"
                              "<item id='s17c' href='v5_03.xhtml' media-type='application/xhtml+xml'/>")
opf = opf.replace("<itemref idref='s17'/>",
                  "<itemref idref='s17'/><itemref idref='s17b'/><itemref idref='s17c'/>")

files = {"OEBPS/v5_01.xhtml": p1, "OEBPS/v5_02.xhtml": p2, "OEBPS/v5_03.xhtml": p3,
         "OEBPS/nav.xhtml": nav, "OEBPS/toc.ncx": ncx, "OEBPS/content.opf": opf}

n = 0
tmp = SRC + ".tmp"
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as o:
    for name, data in others.items():
        if name in files:
            continue
        if name.endswith((".xhtml", ".ncx", ".opf")):
            s = data.decode("utf-8")
            for a, b in NAMES:
                n += s.count(a)
                s = s.replace(a, b)
            data = s.encode("utf-8")
        o.writestr(name, data)
    for name, s in files.items():
        for a, b in NAMES:
            n += s.count(a)
            s = s.replace(a, b)
        ET.fromstring(s)
        o.writestr(name, s.encode("utf-8"))
shutil.move(tmp, SRC)
print("name replacements", n)
