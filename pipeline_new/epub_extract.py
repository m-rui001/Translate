"""Generic EPUB -> per-chapter JSON extractor.

Built for the two new projects (Cien años de soledad, Der Zauberberg) whose
sources are ordinary reflowable EPUBs rather than the hand-tuned Penguin file
the whale pipeline had to reverse-engineer.

Output: <out>/<id>.json
    {id, title, blocks: [{type: p|head|verse, text} | {type: verse, lines}]}

Italics are preserved as ⟦i⟧…⟦/i⟧ because both novels use them semantically
(stream of consciousness, foreign words, letters). Blank paragraphs and page
numbers are dropped; nothing else is rewritten.

Usage:
    python pipeline_new/epub_extract.py --epub "Cien años de soledad.epub" \
        --out work_soledad/src --glob "capitulo*.xhtml"
"""
from __future__ import annotations

import argparse
import glob as g
import json
import os
import re
import sys
import zipfile

from lxml import html as LH

WS = re.compile(r"\s+")


def text_of(el) -> str:
    """Inner text with italics marked and whitespace collapsed."""
    parts = []

    def walk(node):
        tag = node.tag if isinstance(node.tag, str) else ""
        if tag in ("em", "i"):
            parts.append("⟦i⟧")
            parts.append(node.text_content())
            parts.append("⟦/i⟧")
            return
        if node.text:
            parts.append(node.text)
        for ch in node:
            walk(ch)
            if ch.tail:
                parts.append(ch.tail)

    walk(el)
    s = "".join(parts)
    s = s.replace("\u00a0", " ").replace("\u2019", "’")
    return WS.sub(" ", s).strip()


def blocks_of(doc) -> list[dict]:
    out = []
    body = doc.find(".//body")
    if body is None:
        return out
    for el in body.iter():
        tag = el.tag if isinstance(el.tag, str) else ""
        if tag in ("h1", "h2", "h3", "h4"):
            t = text_of(el)
            if t:
                out.append({"type": "head", "text": t})
        elif tag == "p":
            cls = el.get("class") or ""
            t = text_of(el)
            if not t:
                continue
            # drop running heads / page numbers that calibre leaves behind
            if re.fullmatch(r"[\d\s\-–—]+", t):
                continue
            if "calibre" in cls and len(t) < 3:
                continue
            out.append({"type": "p", "text": t})
        elif tag == "blockquote":
            lines = [text_of(p) for p in el.iter("p")]
            lines = [l for l in lines if l]
            if lines:
                out.append({"type": "verse", "lines": lines})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epub", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--glob", default="*.xhtml")
    ap.add_argument("--skip-first", type=int, default=0)
    ap.add_argument("--id-prefix", default="")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(a.out, exist_ok=True)

    z = zipfile.ZipFile(a.epub)
    names = sorted(n for n in z.namelist() if g.fnmatch.fnmatch(os.path.basename(n), a.glob))
    names = names[a.skip_first:]
    total_paras = 0
    index = []
    for n in names:
        raw = z.read(n).decode("utf-8", "replace")
        doc = LH.fromstring(raw.encode("utf-8"))
        title = ""
        h = doc.find(".//h1") or doc.find(".//h2")
        if h is not None:
            title = text_of(h)
        bl = blocks_of(doc)
        if not bl:
            continue
        stem = os.path.splitext(os.path.basename(n))[0]
        cid = a.id_prefix + stem
        json.dump({"id": cid, "title": title, "blocks": bl},
                  open(os.path.join(a.out, cid + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        paras = sum(1 for b in bl if b["type"] == "p")
        chars = sum(len(b.get("text", "")) + sum(len(x) for x in b.get("lines", [])) for b in bl)
        total_paras += paras
        index.append({"id": cid, "title": title, "paras": paras, "chars": chars})
        print(f"{cid:24s} blocks={len(bl):4d} paras={paras:4d} chars={chars:7d}  {title[:40]}")

    json.dump(index, open(os.path.join(a.out, "index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n{len(index)} chapters, {total_paras:,} paragraphs, "
          f"{sum(i['chars'] for i in index):,} chars")


if __name__ == "__main__":
    main()
