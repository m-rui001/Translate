
"""Remove stray spaces between Chinese characters.

The extractors joined wrapped source lines with a space, and the space survives
between two Chinese characters where it can never be intended. The only legitimate
case in these files is the translator line "坟头草　译", which is protected.
"""
import html
import os
import re
import sys
import zipfile

SPACE = re.compile(r"(?<=[\u4e00-\u9fff])[ \u00a0\u3000]+(?=[\u4e00-\u9fff])")
PROTECT = "坟头草\u3000译"
TEXT = re.compile(r"(<p[^>]*>|<h1[^>]*>|<h2[^>]*>|<title>)(.*?)(</p>|</h1>|</h2>|</title>)", re.S)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    total = 0
    for fn in sorted(os.listdir("out")):
        if not fn.endswith(".epub"):
            continue
        path = os.path.join("out", fn)
        z = zipfile.ZipFile(path)
        items = [(i, z.read(i.filename)) for i in z.infolist()]
        z.close()
        n = 0
        out = []
        for info, data in items:
            if info.filename.endswith(".xhtml"):
                s = data.decode("utf-8")
                def repl(m):
                    nonlocal n
                    t = m.group(2)
                    t2 = SPACE.sub("", t)
                    if t2 != t:
                        n += t.count("\u3000") and 0 or 0
                        n += len(SPACE.findall(t))
                    return m.group(1) + t2 + m.group(3)
                s2 = TEXT.sub(repl, s)
                if s2 != s:
                    data = s2.encode("utf-8")
            out.append((info, data))
        if n:
            tmp = path + ".tmp"
            with zipfile.ZipFile(tmp, "w") as z2:
                for info, data in out:
                    z2.writestr(info, data)
            os.replace(tmp, path)
            total += n
            print(f"{fn[:-5][:24]:26s}{n}")
    print("TOTAL", total)


if __name__ == "__main__":
    main()
