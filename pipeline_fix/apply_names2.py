"""Apply the stable name-variant merges to the EPUBs (and to the work_* segments,
so a later rebuild does not undo them)."""
import json, os, re, shutil, sys, zipfile
from collections import Counter

BOOK2EPUB = {}
for f in os.listdir("out"):
    if f.endswith(".epub"):
        BOOK2EPUB[f[:-5].replace("（坟头草译）", "")] = os.path.join("out", f)


def main():
    rows = json.load(open("scratch/name_verdicts2_stable.json", encoding="utf-8"))
    by_book = {}
    for r in rows:
        by_book.setdefault(r["book"], []).append((r["minor"], r["major"]))
    total = Counter()
    for book, subs in sorted(by_book.items()):
        path = BOOK2EPUB.get(book.replace("（坟头草译）", ""))
        if not path or not os.path.exists(path):
            print("  skip (no epub)", book)
            continue
        # 长的先替换，避免短串吃掉长串的一部分
        subs = sorted(set(subs), key=lambda p: -len(p[0]))
        tmp = path + ".tmp"
        n = Counter()
        with zipfile.ZipFile(path) as z, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as o:
            for it in z.infolist():
                data = z.read(it.filename)
                if it.filename.endswith((".xhtml", ".ncx", ".opf")):
                    s = data.decode("utf-8")
                    for old, new in subs:
                        k = s.count(old)
                        if k:
                            s = s.replace(old, new)
                            n[old] += k
                    data = s.encode("utf-8")
                o.writestr(it, data)
        shutil.move(tmp, path)
        total.update(n)
        if n:
            print("  %-24s %s" % (book[:24], " ".join("%s→%s:%d" % (a, b, c) for (a, b), c in
                                                      ((p, n[p[0]]) for p in subs) if c)))
    print("total replacements", sum(total.values()))


if __name__ == "__main__":
    main()
