"""Dump the existing Chinese edition (epub) to plain text, per chapter.

Used ONLY for (a) terminology cross-checking, (b) blind comparison in evaluation.
"""
from __future__ import annotations

import json
import os
import re
import zipfile

EPUB = "E:/Translate/魔戒 ([英]J.R.R.托尔金) (z-library.sk, 1lib.sk, z-lib.sk).epub"
OUT = "E:/Translate/work/ref_zh"


def html_to_blocks(raw: str):
    body = raw.split("<body", 1)[-1]
    blocks = []
    for m in re.finditer(r"<(h[1-6]|p|div)\b[^>]*>(.*?)</\1>", body, re.S):
        txt = re.sub(r"<[^>]+>", "", m.group(2))
        txt = (
            txt.replace("&nbsp;", " ")
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&quot;", '"')
        )
        txt = re.sub(r"\s+", " ", txt).strip()
        if txt:
            blocks.append({"tag": m.group(1), "text": txt})
    return blocks


def main():
    os.makedirs(OUT, exist_ok=True)
    z = zipfile.ZipFile(EPUB)
    names = sorted(n for n in z.namelist() if n.startswith("OEBPS/Text/"))
    index = []
    for n in names:
        raw = z.read(n).decode("utf-8", errors="ignore")
        title = re.search(r"<title>(.*?)</title>", raw, re.S)
        title = re.sub(r"\s+", " ", title.group(1)).strip() if title else n
        blocks = html_to_blocks(raw)
        base = os.path.basename(n).replace(".html", "")
        with open(os.path.join(OUT, base + ".json"), "w", encoding="utf-8") as f:
            json.dump({"file": base, "title": title, "blocks": blocks}, f, ensure_ascii=False, indent=1)
        chars = sum(len(b["text"]) for b in blocks)
        index.append({"file": base, "title": title, "chars": chars, "blocks": len(blocks)})
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    for it in index:
        print(it["file"], it["chars"], it["title"][:40])


if __name__ == "__main__":
    main()
