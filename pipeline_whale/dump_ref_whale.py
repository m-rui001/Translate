"""Extract the published Chinese Moby-Dick (中央编译·罗山川译) as a reference.

Used strictly for (a) proper-name alignment and (b) blind A/B evaluation.
Paragraph text is never copied into our translation.

Output: work_whale/ref_zh/<id>.json  ->  {id, title_zh, paras:[...]}
Mapping: ref file text00007 == chapter 1, so text(6+n) == ch n, up to text00142.
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
import zipfile

from lxml import html as LH

EPUB = "E:/Translate/白鲸.epub"
OUT = "E:/Translate/work_whale/ref_zh"


def block_paras(raw: bytes) -> list[str]:
    doc = LH.fromstring(raw, parser=LH.HTMLParser(encoding="utf-8"))
    out = []
    for el in doc.xpath("//p"):
        txt = el.text_content()
        txt = txt.replace("\u00a0", " ")
        txt = re.sub(r"\[\d+\]", "", txt)
        txt = re.sub(r"\s+", "", txt)  # CJK: whitespace is layout noise
        if len(txt) >= 8:
            out.append(txt)
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(OUT, exist_ok=True)
    z = zipfile.ZipFile(EPUB)
    ncx = z.read("OEBPS/toc.ncx").decode("utf-8", "ignore")
    ents = re.findall(
        r'<navPoint[^>]*>\s*<navLabel>\s*<text>(.*?)</text>\s*</navLabel>\s*<content src="([^"]+)"',
        ncx, re.S)
    titles = {}
    for t, s in ents:
        f = s.split("#")[0]
        titles.setdefault(f, []).append(t.strip())
    titles = {k: v for k, v in titles.items()}

    for n in range(1, 136):
        f = f"OEBPS/text{6 + n:05d}.html"
        if f not in z.namelist():
            print("missing", f)
            continue
        paras = block_paras(z.read(f))
        # first paragraph is the running title; drop it
        if paras and ("章" in paras[0] or paras[0].startswith("第")) and len(paras[0]) < 20:
            paras = paras[1:]
        rec = {"id": f"ch{n:03d}", "title_zh": titles.get(f, [""])[0], "paras": paras}
        with open(os.path.join(OUT, f"ch{n:03d}.json"), "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False)
        print(f"ch{n:03d} paras={len(paras):4d} chars={sum(len(p) for p in paras):6d} "
              f"{rec['title_zh']}")
    for name, fid in (("front_ety", "OEBPS/text00005.html"),
                      ("front_ext", "OEBPS/text00006.html"),
                      ("epilogue", "OEBPS/text00142.html")):
        paras = block_paras(z.read(fid))
        rec = {"id": name, "title_zh": titles.get(fid, [""])[0], "paras": paras}
        with open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False)
        print(f"{name} paras={len(paras)}")


if __name__ == "__main__":
    main()
