"""One index of every translated unit in the workspace, and its French/German/...
source, so that polish runs can be driven from a single place.

The workspace now holds three separate bodies of work that all need the same
treatment — an editorial polish pass over what already exists, not a retranslation:

* ``work_proust/out``         — four Proust volumes, 632 chunks
* ``work_gutenberg/<book>/out`` — twenty public-domain novels, 2,121 chunks
* ``work_polish2``            — the seven earlier books (already delivered as EPUB)

A polish pass needs, per unit: the existing Chinese text, and — when it can be
reliably aligned — the source paragraphs, because the polisher checks the
translation against the original. Alignment is the fragile part: a chunk's source
blocks include ``head``/``num`` blocks (chapter headings, numerals) that the
translator folded into the first translated paragraph or dropped, so counting raw
blocks overstates the paragraph count. This module therefore derives the expected
paragraph count from the *prose* blocks only, and reports a unit as aligned or not
rather than silently guessing.

Usage:
    python -X utf8 pipeline_polish/index_units.py            # summary
    python -X utf8 pipeline_polish/index_units.py --json out.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

ROOT = "E:/Translate"
GUT = os.path.join(ROOT, "work_gutenberg")
PROUST_CHUNKS = os.path.join(ROOT, "work_proust", "chunks")
PROUST_OUT = os.path.join(ROOT, "work_proust", "out")
PROUST_OUT_IND = os.path.join(ROOT, "work_proust", "out_ind")
POLISH2 = os.path.join(ROOT, "work_polish2")


def paras(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def src_paras_from_blocks(blocks) -> int:
    """Paragraph count the translator was asked to produce.

    Only ``p`` blocks count. ``head``/``num`` blocks are chapter headings and
    numerals: the model renders them as a short heading line, and whether that
    becomes its own paragraph varies. Excluding them keeps the count honest.
    """
    n = 0
    for b in blocks:
        if not isinstance(b, dict):
            continue
        if b.get("type") != "p":
            continue
        n += len([x for x in (b.get("text") or "").split("\n\n") if x.strip()])
    return n


# ── collectors ──────────────────────────────────────────────────────────

def collect_gutenberg() -> list[dict]:
    out = []
    for book in sorted(os.listdir(GUT)):
        cdir = os.path.join(GUT, book, "chunks")
        if not os.path.isdir(cdir):
            continue
        for cf in sorted(glob.glob(os.path.join(cdir, "*.json"))):
            cid = os.path.basename(cf)[:-5]
            spec = json.load(open(cf, encoding="utf-8"))
            chunks = spec.get("chunks") if isinstance(spec, dict) else spec
            for i, blocks in enumerate(chunks):
                fp = os.path.join(GUT, book, "out", cid, f"c{i:02d}", "final.txt")
                if not os.path.exists(fp) or os.path.getsize(fp) == 0:
                    continue
                zh = open(fp, encoding="utf-8").read()
                zp = paras(zh)
                sp = src_paras_from_blocks(blocks)
                out.append({
                    "corpus": "gutenberg", "book": book, "chapter": cid,
                    "unit": i, "path": fp,
                    "src_paras": sp, "zh_paras": len(zp),
                    "aligned": sp == len(zp),
                    "zh_chars": len(zh),
                    "title": (spec.get("title_zh") or spec.get("title_src") or "")
                    if isinstance(spec, dict) else "",
                })
    return out


def collect_proust(outdir: str, corpus: str) -> list[dict]:
    out = []
    if not os.path.isdir(outdir):
        return out
    for vol in sorted(os.listdir(outdir)):
        vdir = os.path.join(outdir, vol)
        if not os.path.isdir(vdir):
            continue
        spec_path = os.path.join(PROUST_CHUNKS, vol, "chunks.json")
        spec = json.load(open(spec_path, encoding="utf-8")) if os.path.exists(spec_path) else {}
        for cf in sorted(glob.glob(os.path.join(vdir, "*", "final.txt"))):
            if os.path.getsize(cf) == 0:
                continue
            name = os.path.basename(os.path.dirname(cf))       # chunk000
            m = re.search(r"(\d+)", name)
            if not m:
                continue
            k = str(int(m.group(1)))
            units = spec.get(k)
            zh = open(cf, encoding="utf-8").read()
            zp = paras(zh)
            sp = len(units) if units else 0
            out.append({
                "corpus": corpus, "book": vol, "chapter": "",
                "unit": int(k), "path": cf,
                "src_paras": sp, "zh_paras": len(zp),
                "aligned": bool(sp) and sp == len(zp),
                "zh_chars": len(zh), "title": "",
            })
    return out


def collect_polish2() -> list[dict]:
    """The seven earlier books. Their shapes differ per book, so just locate the
    text files that the polish engine already knows how to read."""
    out = []
    for book in sorted(os.listdir(POLISH2)):
        bdir = os.path.join(POLISH2, book)
        if not os.path.isdir(bdir) or book.startswith("_"):
            continue
        files = []
        for pat in ("final/*.json", "final.txt", "chapter.md", "**/final.txt"):
            files.extend(glob.glob(os.path.join(bdir, pat), recursive=True))
        files = [f for f in files if os.path.isfile(f)]
        if not files:
            continue
        n = 0
        for f in files:
            try:
                n += len(open(f, encoding="utf-8").read())
            except Exception:                                     # noqa: BLE001
                pass
        out.append({"corpus": "polish2", "book": book, "files": len(files),
                    "chars": n})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    g = collect_gutenberg()
    p = collect_proust(PROUST_OUT, "proust")
    pi = collect_proust(PROUST_OUT_IND, "proust_ind")
    o = collect_polish2()

    for name, units in (("gutenberg", g), ("proust", p), ("proust_ind", pi)):
        al = sum(u["aligned"] for u in units)
        ch = sum(u["zh_chars"] for u in units)
        print(f"{name:12s} units={len(units):5d} aligned={al:5d} "
              f"({al * 100 // max(1, len(units)):3d}%)  chars={ch:,}")
    print(f"{'polish2':12s} books={len(o)}")
    for b in o:
        print(f"    {b['book']:16s} files={b['files']:4d} chars={b['chars']:,}")

    total = sum(u["zh_chars"] for u in g) + sum(u["zh_chars"] for u in p) \
        + sum(u["zh_chars"] for u in pi) + sum(b["chars"] for b in o)
    print(f"\nTOTAL existing Chinese text: {total:,} chars")

    if a.json:
        json.dump({"gutenberg": g, "proust": p, "proust_ind": pi, "polish2": o},
                  open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"wrote {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
