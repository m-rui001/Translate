
"""Post-repair verification: structure, names, register, integrity, size."""
from __future__ import annotations

import glob
import html
import os
import re
import sys
import zipfile
from collections import Counter

sys.path.insert(0, "pipeline_fix")
import names_scan as NS

CJK = re.compile(r"[\u4e00-\u9fff]")
MARK = ["甭管", "甭提", "甭", "咋", "啥", "这号", "那号", "得嘞", "这当儿",
        "那光景", "得了吧", "压根", "捅娄子", "瞎琢磨"]


def read(path):
    z = zipfile.ZipFile(path)
    text, xml_errors = "", 0
    for n in z.namelist():
        if not n.endswith(".xhtml"):
            continue
        s = z.read(n).decode("utf-8")
        if s.count("<p") != s.count("</p>"):
            xml_errors += 1
        if n.endswith("nav.xhtml"):
            continue
        text += html.unescape(re.sub(r"<[^>]+>", "", s))
    return text, xml_errors, z


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = []
    for p in sorted(glob.glob("out/*.epub")):
        t, err, z = read(p)
        nav = z.read("OEBPS/nav.xhtml").decode("utf-8")
        titles = [html.unescape(x) for x in re.findall(r"<a href='[^']+'>([^<]+)</a>", nav)][2:]
        dup = len(titles) - len(set(titles))
        marks = sum(t.count(w) for w in MARK)
        rows.append({"book": os.path.basename(p)[:-5], "hanzi": len(CJK.findall(t)),
                     "toc": len(titles), "dup": dup, "marks": marks,
                     "xml": err, "mb": os.path.getsize(p) / 1048576})
    print(f'{"book":28s}{"hanzi":>9s}{"toc":>5s}{"dup":>5s}{"mark":>6s}{"xml":>4s}{"MB":>7s}')
    for r in rows:
        print(f'{r["book"][:26]:28s}{r["hanzi"]:>9,}{r["toc"]:>5d}{r["dup"]:>5d}'
              f'{r["marks"]:>6d}{r["xml"]:>4d}{r["mb"]:>7.2f}')
    print("books", len(rows), "hanzi", sum(r["hanzi"] for r in rows),
          "xml_errors", sum(r["xml"] for r in rows),
          "dup_titles", sum(1 for r in rows if r["dup"]),
          "marks", sum(r["marks"] for r in rows))


if __name__ == "__main__":
    main()
