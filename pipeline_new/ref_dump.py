"""Dump a reference Chinese translation into a flat paragraph list.

The blind A/B pass needs the published translation paragraph-aligned to our
own output, and the only thing it needs from the reference is the text in
reading order — no chapter structure, no markup.

Usage:
    python pipeline_new/ref_dump.py --epub "百年孤独.epub" --out work_soledad/ref_zh.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile

from lxml import html as LH

WS = re.compile(r"\s+")


def text_of(el) -> str:
    parts = []

    def walk(node):
        tag = node.tag if isinstance(node.tag, str) else ""
        if tag in ("em", "i"):
            parts.append(node.text_content())
            return
        if node.text:
            parts.append(node.text)
        for ch in node:
            walk(ch)
            if ch.tail:
                parts.append(ch.tail)

    walk(el)
    return WS.sub(" ", "".join(parts).replace("\u00a0", " ")).strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epub", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--glob", default="*.xhtml")
    ap.add_argument("--skip-first", type=int, default=0)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    z = zipfile.ZipFile(a.epub)
    names = sorted(n for n in z.namelist()
                   if n.lower().endswith((".xhtml", ".html", ".htm"))
                   and re.fullmatch(a.glob.replace("*", ".*"), os.path.basename(n)))
    names = names[a.skip_first:]
    paras: list[str] = []
    for n in names:
        doc = LH.fromstring(z.read(n))
        body = doc.find(".//body")
        if body is None:
            continue
        for el in body.iter("p"):
            t = text_of(el)
            if not t or re.fullmatch(r"[\d\s\-–—]+", t):
                continue
            paras.append(t)
    han = sum(1 for ch in "".join(paras) if "\u4e00" <= ch <= "\u9fff")
    json.dump({"paras": paras}, open(a.out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=0)
    print(f"{len(names)} files -> {len(paras):,} paragraphs, han={han:,}")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
