
"""Rename one chapter in a finished EPUB (nav, ncx and the chapter heading)."""
import re, sys, zipfile, os, html

path = "out/白鲸（坟头草译）.epub"
old, new = "甲板上·亚哈与木匠", "亚哈与木匠"
marker = "甲板——第一夜班"

z = zipfile.ZipFile(path)
items = [(i, z.read(i.filename)) for i in z.infolist()]
z.close()

# the chapter file that starts with the night-watch paragraph
target = None
for info, data in items:
    if info.filename.endswith(".xhtml"):
        s = data.decode("utf-8")
        if marker in s and f"<h1>{old}</h1>" in s:
            target = info.filename
            break
print("target", target)

out = []
done_nav = done_ncx = False
for info, data in items:
    if info.filename.endswith(".xhtml"):
        s = data.decode("utf-8")
        if info.filename.endswith("nav.xhtml") and not done_nav:
            s = s.replace(f">{old}</a>", f">{new}</a>", 1)
            done_nav = True
        elif info.filename == target:
            s = s.replace(f"<h1>{old}</h1>", f"<h1>{new}</h1>", 1)
            s = s.replace(f"<title>{old}</title>", f"<title>{new}</title>", 1)
        data = s.encode("utf-8")
    elif info.filename.endswith("toc.ncx") and not done_ncx:
        s = data.decode("utf-8")
        s = s.replace(f"<text>{old}</text>", f"<text>{new}</text>", 1)
        data = s.encode("utf-8")
        done_ncx = True
    out.append((info, data))

tmp = path + ".tmp"
with zipfile.ZipFile(tmp, "w") as z2:
    for info, data in out:
        z2.writestr(info, data)
os.replace(tmp, path)
print("done", done_nav, done_ncx)
