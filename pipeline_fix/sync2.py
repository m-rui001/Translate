#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync2.py - write repaired EPUB prose back into the work_* trees.

Why this exists
---------------
The 2026-10-28 repair rounds (see REPAIR_2026-10-28.md / REPAIR_2026-10-28b.md)
edited `out/*.epub` only. All 4,482 audit fixes, the name merges and the verse
reflow live in the EPUBs and nowhere else; rebuilding from `work_*` would throw
every one of them away. This script copies the EPUB text back.

Why it is not `sync_epub_to_work.py`
------------------------------------
That script aligns EPUB chapters to work out-units by chapter id (`num`), by
volume (`vol`) or by position (`pos`), then overwrites a whole unit with the
concatenation of the EPUB chapters mapped onto it. Two problems turned up when
it was actually measured:

* **Chapter ids and paragraph counts do not line up.** 644 chapters have equal
  paragraph counts, 1,172 do not (双城记 c002: EPUB 60 paragraphs vs work 7;
  乌略亚庄园 c001: 25 vs 48; 浮士德 verse lines were merged into prose). It also
  shifts by a whole chapter: 双城记 `work_pub/twocities/out/c002` holds 7
  paragraphs beginning 题：第一章时代 — the same text as EPUB `c001`. Writing
  unit-by-unit from such an offset silently scrambles the book.
* Work trees hold phantom units the EPUB does not have (双城记 has 48 out dirs
  for 45 real chapters), so `len(units) == n` is not proof of correct alignment.

So this version aligns **paragraph sequences for the whole book**, not chapters.
Paragraph text survives the repair intact except for the ~5% that were edited,
so a patience-style anchor diff (unique paragraphs that occur exactly once on
both sides, kept in increasing order) pins the mapping down, and each short gap
between anchors is diffed with difflib. An edited paragraph then lands on its own
slot instead of shifting its whole chapter.

Layout safety: work file boundaries are preserved. A file keeps the same number
of paragraphs it had; only the text of matched slots is replaced. Paragraphs that
only exist on one side are counted and reported, never inserted or deleted —
that keeps the writeback from destroying content when the diff is wrong.

Backends
--------
  out-tree   work_*/<book>/out/<unit>/[<block>/]final.txt      (most books)
  proust     work_proust/{out,out_ind}/v<N>/chunkNNN/final.txt (v2, v5 live in
             out_ind; the volume table is copied from assemble_proust.py)
  lotr-json  work_overhaul/lotr/final/*.json  "texts" field    (no out/ tree)

Usage
-----
    python pipeline_fix/sync2.py                 # dry run, writes report only
    python pipeline_fix/sync2.py --apply         # back up, then write
    python pipeline_fix/sync2.py --only 白鲸,鼠疫
"""
from __future__ import annotations

import argparse
import difflib
import glob
import html
import json
import os
import re
import shutil
import sys
import zipfile
from collections import Counter, defaultdict
from xml.etree import ElementTree as ET

ROOT = "E:/Translate"
OUT_EPUB_DIR = os.path.join(ROOT, "out")
REPORT = os.path.join(ROOT, "pipeline_fix", "sync_report2.txt")
BACKUP = os.path.join(ROOT, "_bak", "work_prewrite_20261029")
NS = "{http://www.idpf.org/2007/opf}"

ITAL_OPEN = "\u27e6i\u27e7"
ITAL_CLOSE = "\u27e6/i\u27e7"
NL = "\n"
BLANK = "\n\n"

CONTENT_THRESH = 0.55
SIM_THRESH = 0.55          # a replace-block pair below this is not applied
UNIQUE_MIN_LEN = 12        # anchors must be at least this long, else too generic

# assemble_proust.py VOL: (vol, base kind). v1/v2/v5 are in out_ind, rest in out.
PROUST_VOL_BASE = {"v1": "out_ind", "v2": "out_ind", "v3": "out",
                   "v4": "out", "v5": "out_ind", "v6": "out", "v7": "out"}
PROUST_VOL_ORDER = ["v1", "v2", "v3", "v4", "v5", "v6", "v7"]


# ── text helpers ───────────────────────────────────────────────────────────────
def hanzi_count(t: str) -> int:
    return sum(1 for ch in t if "\u4e00" <= ch <= "\u9fff")


def hanzi_only(t: str) -> str:
    return "".join(ch for ch in t if "\u4e00" <= ch <= "\u9fff")


def bg_counter(t: str) -> Counter:
    h = hanzi_only(t)
    return Counter(h[i:i + 2] for i in range(len(h) - 1))


def norm(t: str) -> str:
    """Comparison key: whitespace-insensitive, nothing else."""
    return re.sub(r"\s+", "", t)


def natsorted(names):
    return sorted(names, key=lambda s: [int(x) if x.isdigit() else x
                                        for x in re.split(r"([0-9]+)", s)])


def split_paras(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


# ── EPUB reading (same normalisation the builder uses, in reverse) ─────────────
def epub_chapter_order(f: str):
    z = zipfile.ZipFile(f)
    opf = [n for n in z.namelist() if n.endswith("content.opf")][0]
    root = ET.fromstring(z.read(opf))
    items = {it.get("id"): it.get("href") for it in root.iter(NS + "item")}
    spine = [s.get("idref") for s in root.iter(NS + "itemref")]
    base = os.path.dirname(opf)
    res = []
    for sid in spine:
        href = items.get(sid)
        if not (href and href.endswith(".xhtml")):
            continue
        bn = os.path.basename(href)
        if bn in ("nav.xhtml", "title.xhtml", "copyright.xhtml"):
            continue
        full = os.path.normpath(os.path.join(base, href)).replace(os.sep, "/")
        try:
            data = z.read(full).decode("utf-8", "ignore")
        except Exception:
            continue
        if ('<div class="titlepage"' in data or '<div class="copyright"' in data
                or "<nav" in data):
            continue
        res.append((bn, full, data))
    return res, z


def unmark_sup(inner: str) -> str:
    m = re.search(r"\[([0-9]+)\]", re.sub(r"<[^>]+>", "", inner))
    return ("[[" + m.group(1) + "]]") if m else ""


def extract_paragraphs(z, name, data=None) -> list[str]:
    if data is None:
        data = z.read(name).decode("utf-8")
    out = []
    for _attrs, inner in re.findall(r"<p([^>]*)>(.*?)</p>", data, re.S):
        t = re.sub(r"<sup[^>]*>(.*?)</sup>", lambda m: unmark_sup(m.group(1)),
                   inner, flags=re.S)
        t = re.sub(r"<br[^>]*>", NL, t)
        t = re.sub(r"<em[^>]*>(.*?)</em>",
                   lambda m: ITAL_OPEN + m.group(1) + ITAL_CLOSE, t, flags=re.S)
        t = re.sub(r"<[^>]+>", "", t)
        out.append(html.unescape(t))
    return out


def epub_paragraphs(f: str):
    """[(chapter_name, [para, ...]), ...] in spine order, plus bigram counter."""
    order, z = epub_chapter_order(f)
    chaps = []
    for bn, full, data in order:
        ps = extract_paragraphs(z, full, data)
        if ps:
            chaps.append((bn, ps))
    z.close()
    flat = [p for _bn, ps in chaps for p in ps]
    return chaps, flat, bg_counter("".join(flat))


# ── work backends: each returns (slots, files) ────────────────────────────────
# A slot is one addressable work paragraph. `files` maps a path to the list of
# paragraph texts that file currently holds; slots reference (path, index) so a
# writeback can rewrite a file without changing its paragraph count.
class Slot:
    __slots__ = ("path", "idx", "text")

    def __init__(self, path, idx, text):
        self.path = path
        self.idx = idx
        self.text = text


def discover_work_books() -> dict[str, str]:
    """book key -> layout tag, for every work tree we can write back to."""
    books = {}
    for wroot in sorted(glob.glob(os.path.join(ROOT, "work_*"))):
        if not os.path.isdir(wroot):
            continue
        base = os.path.basename(wroot)
        for sub in sorted(os.listdir(wroot)):
            od = os.path.join(wroot, sub, "out")
            if os.path.isdir(od):
                books[base + "/" + sub] = "out-tree"
        if base == "work_proust":
            books[base] = "proust"
            continue
        od = os.path.join(wroot, "out")
        if os.path.isdir(od):
            books[base] = "out-tree"
    if os.path.isdir(os.path.join(ROOT, "work_overhaul", "lotr", "final")):
        books["work_overhaul/lotr-json"] = "lotr-json"
    return books


def out_units(out_dir: str) -> list[list[str]]:
    """Same unit shape as build_all/sync: [[final.txt, ...], ...]."""
    units = []
    top = [d for d in os.listdir(out_dir) if os.path.isdir(os.path.join(out_dir, d))]
    for u in natsorted(top):
        ud = os.path.join(out_dir, u)
        subs = [s for s in os.listdir(ud) if os.path.isdir(os.path.join(ud, s))]
        blocks = [os.path.join(ud, b, "final.txt") for b in natsorted(subs)]
        blocks = [b for b in blocks if os.path.isfile(b)]
        if not blocks:
            fp = os.path.join(ud, "final.txt")
            if os.path.isfile(fp):
                blocks = [fp]
        if blocks:
            units.append(blocks)
    return units


def slots_from_out_tree(out_dir: str):
    files = {}
    slots = []
    for unit in out_units(out_dir):
        for fp in unit:
            ps = split_paras(open(fp, encoding="utf-8").read())
            files[fp] = ps
            for i, p in enumerate(ps):
                slots.append(Slot(fp, i, p))
    return slots, files


def slots_from_proust():
    files, slots = {}, []
    for vol in PROUST_VOL_ORDER:
        base = os.path.join(ROOT, "work_proust", PROUST_VOL_BASE[vol], vol)
        if not os.path.isdir(base):
            continue
        for cd in natsorted(os.listdir(base)):
            fp = os.path.join(base, cd, "final.txt")
            if not os.path.isfile(fp):
                continue
            ps = split_paras(open(fp, encoding="utf-8").read())
            files[fp] = ps
            for i, p in enumerate(ps):
                slots.append(Slot(fp, i, p))
    return slots, files


def lotr_json_paths() -> list[str]:
    fs = [f for f in glob.glob(os.path.join(ROOT, "work_overhaul", "lotr",
                                            "final", "*.json"))
          if not f.endswith(".polished.json")]
    fs = [f for f in fs
          if os.path.basename(f).startswith("book") or os.path.basename(f) == "prologue.json"]
    # build_all sorts by (id != prologue, id[:5], id)
    fs.sort(key=lambda p: (os.path.basename(p) != "prologue.json",
                           os.path.basename(p)[:5], os.path.basename(p)))
    return fs


def slots_from_lotr_json():
    files, slots = {}, []
    for fp in lotr_json_paths():
        d = json.load(open(fp, encoding="utf-8"))
        texts = list(d.get("texts") or [])
        files[fp] = texts
        for i, p in enumerate(texts):
            slots.append(Slot(fp, i, p))
    return slots, files


def load_book(key: str, layout: str):
    if layout == "proust":
        return slots_from_proust()
    if layout == "lotr-json":
        return slots_from_lotr_json()
    wroot, sub = key.split("/", 1) if "/" in key else (key, None)
    out_dir = os.path.join(ROOT, wroot, sub, "out") if sub else os.path.join(ROOT, key, "out")
    return slots_from_out_tree(out_dir)


# ── alignment ─────────────────────────────────────────────────────────────────
def lcs_anchors(pairs: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Longest strictly-increasing subsequence of (i, j) pairs (patience step)."""
    if not pairs:
        return []
    tails, tail_idx, prev = [], [], [-1] * len(pairs)
    for n, (i, j) in enumerate(pairs):
        lo, hi = 0, len(tails)
        while lo < hi:
            mid = (lo + hi) // 2
            if tails[mid] < j:
                lo = mid + 1
            else:
                hi = mid
        if lo == len(tails):
            tails.append(j)
            tail_idx.append(n)
        else:
            tails[lo] = j
            tail_idx[lo] = n
        prev[n] = tail_idx[lo - 1] if lo else -1
    out = []
    n = tail_idx[-1]
    while n != -1:
        out.append(pairs[n])
        n = prev[n]
    return out[::-1]


def align(W: list[str], E: list[str]):
    """Return [(w_index, e_index, kind)] with kind in {equal, replace}."""
    wkey = [norm(p) for p in W]
    ekey = [norm(p) for p in E]
    wpos, epos = defaultdict(list), defaultdict(list)
    for i, k in enumerate(wkey):
        wpos[k].append(i)
    for j, k in enumerate(ekey):
        epos[k].append(j)

    # anchor candidates: paragraphs long enough and unique on both sides
    cand = []
    for k, wi in wpos.items():
        if len(wi) == 1 and len(k) >= UNIQUE_MIN_LEN:
            ej = epos.get(k)
            if ej is not None and len(ej) == 1:
                cand.append((wi[0], ej[0]))
    cand.sort()
    anchors = lcs_anchors(cand)

    pairs = []
    prev_w = prev_e = -1
    for (aw, ae) in anchors + [(len(W), len(E))]:
        wgap = list(range(prev_w + 1, aw))
        egap = list(range(prev_e + 1, ae))
        if wgap or egap:
            sub = difflib.SequenceMatcher(None, [wkey[i] for i in wgap],
                                          [ekey[j] for j in egap], autojunk=False)
            for tag, i1, i2, j1, j2 in sub.get_opcodes():
                if tag == "equal":
                    for a, b in zip(wgap[i1:i2], egap[j1:j2]):
                        pairs.append((a, b, "equal"))
                elif tag == "replace":
                    for a, b in zip(wgap[i1:i2], egap[j1:j2]):
                        pairs.append((a, b, "replace"))
        if aw < len(W) and ae < len(E):
            pairs.append((aw, ae, "equal"))
        prev_w, prev_e = aw, ae
    pairs.sort()
    return pairs


def apply_pairs(slots: list[Slot], files: dict, E: list[str], pairs) -> dict:
    stat = Counter()
    changed = 0
    for wi, ei, kind in pairs:
        old = slots[wi].text
        new = E[ei]
        if kind == "equal" or norm(old) == norm(new):
            stat["matched"] += 1
            continue
        ratio = difflib.SequenceMatcher(None, norm(old), norm(new)).ratio()
        if ratio < SIM_THRESH:
            stat["low_similarity"] += 1
            continue
        files[slots[wi].path][slots[wi].idx] = new
        stat["replaced"] += 1
        changed += 1
    stat["changed"] = changed
    return stat


# ── reporting / writing ───────────────────────────────────────────────────────
def write_files(files: dict, backups: dict, do_write: bool) -> int:
    n = 0
    for rel, ps in files.items():
        text = BLANK.join(ps) + NL
        try:
            old = open(rel, encoding="utf-8").read()
        except Exception:
            old = None
        if old is not None and old.strip() == text.strip():
            continue
        n += 1
        if not do_write:
            continue
        if rel not in backups:
            dst = os.path.join(BACKUP, os.path.relpath(rel, ROOT))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if old is not None:
                with open(dst, "w", encoding="utf-8") as fo:
                    fo.write(old)
            backups[rel] = dst
        os.makedirs(os.path.dirname(rel), exist_ok=True)
        with open(rel, "w", encoding="utf-8") as fo:
            fo.write(text)
    return n


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually write files")
    ap.add_argument("--only", default="", help="comma separated epub name fragments")
    args = ap.parse_args()

    only = [s for s in args.only.split(",") if s]
    layouts = discover_work_books()
    print("work targets: %d" % len(layouts))
    for k, v in sorted(layouts.items()):
        print("   %-34s %s" % (k, v))

    # preload work paragraphs once (bigram + slot list), keyed by book
    cache = {}
    for key, layout in layouts.items():
        try:
            slots, files = load_book(key, layout)
        except Exception as e:                     # noqa: BLE001
            print("  LOAD FAIL %s: %s" % (key, e))
            continue
        cache[key] = {"layout": layout, "slots": slots, "files": files,
                      "bg": bg_counter("".join(s.text for s in slots))}
    print("loaded %d work books" % len(cache))

    epubs = sorted(glob.glob(os.path.join(OUT_EPUB_DIR, "*.epub")))
    rows, review, backups = [], [], {}
    total_changed = total_files = 0

    for f in epubs:
        title = os.path.basename(f)
        if only and not any(o in title for o in only):
            continue
        chaps, flat, ebg = epub_paragraphs(f)
        if not flat:
            review.append((title, "no content chapters"))
            continue
        best, best_sc = None, -1.0
        for key, info in cache.items():
            c = info["bg"]
            uni = sum((ebg | c).values())
            sc = (sum((ebg & c).values()) / uni) if uni else 0.0
            if sc > best_sc:
                best_sc, best = sc, key
        if best is None or best_sc < CONTENT_THRESH:
            review.append((title, "unmatched (score=%.2f)" % best_sc))
            continue

        info = cache[best]
        slots = info["slots"]
        W = [s.text for s in slots]
        pairs = align(W, E=flat)
        stat = apply_pairs(slots, info["files"], flat, pairs)
        old_han = sum(hanzi_count(s.text) for s in slots)
        new_han = sum(hanzi_count(p) for ps in info["files"].values() for p in ps)
        e_han = sum(hanzi_count(p) for p in flat)
        delta = abs(new_han - e_han) / e_han if e_han else 0.0
        status = "OK" if delta <= 0.01 else "MISMATCH"
        if status != "OK":
            review.append((title, "delta=%.4f vs %s" % (delta, best)))
        nfiles = write_files(info["files"], backups, args.apply)
        total_changed += stat["changed"]
        total_files += nfiles
        rows.append((title, best, info["layout"], len(W), len(flat),
                     len(flat) - len(W), old_han, new_han, e_han,
                     round(delta, 4), stat["matched"], stat["replaced"],
                     stat["low_similarity"], nfiles, status, round(best_sc, 3)))

    lines = []
    lines.append("=" * 118)
    lines.append("SYNC2  EPUB -> WORK  (%s)" % ("APPLIED" if args.apply else "DRY RUN"))
    lines.append("=" * 118)
    lines.append("epubs scanned        : %d" % len(rows))
    lines.append("paragraphs replaced  : %d" % total_changed)
    lines.append("files to rewrite     : %d" % total_files)
    lines.append("books needing review : %d" % len(review))
    lines.append("")
    lines.append("%-30s %-22s %-11s %6s %6s %6s %8s %8s %8s %7s %6s %6s %5s %5s %s" % (
        "epub", "work book", "layout", "wPara", "ePara", "gap", "oldHan",
        "newHan", "epubHan", "delta", "match", "repl", "low", "files", "stat"))
    lines.append("-" * 118)
    for r in sorted(rows):
        lines.append("%-30s %-22s %-11s %6d %6d %6d %8d %8d %8d %7.3f %6d %6d %5d %5d %s" % (
            r[0][:29], r[1][:21], r[2], r[3], r[4], r[5], r[6], r[7], r[8],
            r[9], r[10], r[11], r[12], r[13], r[14]))
    lines.append("")
    if review:
        lines.append("NEEDS REVIEW:")
        for t, why in review:
            lines.append("  %s  (%s)" % (t, why))
    if not args.apply:
        lines.append("")
        lines.append("DRY RUN: nothing written. Re-run with --apply to write; old files")
        lines.append("are copied to %s first." % BACKUP)

    txt = "\n".join(lines)
    print(txt)
    with open(REPORT, "w", encoding="utf-8") as fo:
        fo.write(txt)
    print("\nreport -> %s" % REPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
