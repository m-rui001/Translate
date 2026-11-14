#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_epub_to_work.py - mirror current EPUB text back into work_*/out final.txt.

Purely mechanical, offline (no network / no LLM).

Strategy
--------
1. BOOK SELECTION is content-discriminative: a character-bigram (hanzi only)
   Jaccard between the EPUB full text and each work book's full text.  The real
   source book scores ~0.9-1.0; unrelated books score <=0.40.  This avoids the
   earlier bug where any fully-mapped wrong book scored ~1.0.
2. CHAPTER ALIGNMENT (only inside the chosen book) maps EPUB chapters to work
   out-units by:
     * id/number  - c045 -> out/c045 (also ch045/sec045/v1... normalized to num)
     * volume     - vV_C epub chapters -> out volume folder vV (Proust)
     * positional - equal counts, no id overlap (Camus parts, Zauberberg)
3. LAYOUT MIRROR (exact round-trip):
     per-chapter  : out/<unit>/final.txt           -> paragraphs joined by blank line
     per-paragraph: out/<unit>/<block>/final.txt   -> paragraphs split contiguously
   The builder's paras() splits each file on blank lines, so this reproduces the
   same paragraph sequence on rebuild and preserves the EPUB repair edits.

Validation: hanzi (U+4E00-U+9FFF) of the concatenated mirror must equal the hanzi
count of the EPUB chapter <p> texts within 1 percent.  A non-zero delta means some
EPUB chapters had no corresponding work out-unit (a genuine source gap) and the
book is flagged for manual review.

Output is written to a SANDBOX under E:/Translate/_sync_test/<book>/... that
recreates the work_*/out layout.  Only a few pilot books are physically written,
but every matched book is validated in memory.  Nothing under work_*/ or out/ changes.
"""

import os
import re
import html
import json
import zipfile
import glob
from collections import Counter, defaultdict
from xml.etree import ElementTree as ET

ROOT = "E:/Translate"
OUT_EPUB_DIR = os.path.join(ROOT, "out")
SYNC_TEST_DIR = os.path.join(ROOT, "_sync_test")
NS = "{http://www.idpf.org/2007/opf}"

ITAL_OPEN = "⟦i⟧"
ITAL_CLOSE = "⟦/i⟧"
BLANK = chr(10) + chr(10)
NL = chr(10)

PILOT_N = 5
CONTENT_THRESH = 0.55


def natsorted(names):
    return sorted(names, key=lambda s: [int(t) if t.isdigit() else t
                                       for t in re.split(r"([0-9]+)", s)])


def hanzi_count(text):
    return sum(1 for ch in text if 0x4E00 <= ord(ch) <= 0x9FFF)


def hanzi_only(text):
    return "".join(ch for ch in text if 0x4E00 <= ord(ch) <= 0x9FFF)


def bg_counter(text):
    h = hanzi_only(text)
    return Counter(h[i:i + 2] for i in range(len(h) - 1))


def paras_of_file(path):
    try:
        t = open(path, encoding="utf-8").read()
    except Exception:
        return []
    return [p.strip() for p in re.split(BLANK, t) if p.strip()]


def unit_hanzi(blocks):
    return sum(hanzi_count(p) for bf in blocks for p in paras_of_file(bf))


def chapter_key_num(name):
    mv = re.search(r"^v([0-9]+)$", name)
    if mv:
        return ("vol", int(mv.group(1)))
    m = re.search(r"([0-9]+)", name)
    return ("num", int(m.group(1))) if m else ("name", name)


def chapter_key_vol(name):
    m = re.search(r"v([0-9]+)_([0-9]+)", name)
    if m:
        return ("vol", int(m.group(1)), int(m.group(2)))
    return chapter_key_num(name)


def find_work_books():
    books = {}
    for wroot in sorted(glob.glob(os.path.join(ROOT, "work_*"))):
        if not os.path.isdir(wroot):
            continue
        placed = False
        for sub in sorted(os.listdir(wroot)):
            od = os.path.join(wroot, sub, "out")
            if os.path.isdir(od):
                books[os.path.basename(wroot) + "/" + sub] = od
                placed = True
        if not placed:
            od = os.path.join(wroot, "out")
            if os.path.isdir(od):
                books[os.path.basename(wroot)] = od
    return books


def build_units(out_dir):
    units = []
    is_index = False
    top = [d for d in os.listdir(out_dir) if os.path.isdir(os.path.join(out_dir, d))]
    for u in natsorted(top):
        ud = os.path.join(out_dir, u)
        if "index_split" in u:
            is_index = True
        subdirs = [s for s in os.listdir(ud) if os.path.isdir(os.path.join(ud, s))]
        if subdirs:
            blocks = []
            for b in natsorted(subdirs):
                fp = os.path.join(ud, b, "final.txt")
                if os.path.isfile(fp):
                    blocks.append(fp)
            if blocks:
                units.append(blocks)
        else:
            fp = os.path.join(ud, "final.txt")
            if os.path.isfile(fp):
                units.append([fp])
    if is_index:
        units = group_by_heading(units)
    src = os.path.join(out_dir, "..", "src", "chunks.json")
    if os.path.isfile(src):
        heads = []
        try:
            heads = [d.get("head", "") for d in json.load(open(src, encoding="utf-8"))]
        except Exception:
            heads = []
        if heads and len(heads) == len(units):
            units = group_by_heads(units, heads)
    return units


def group_by_heading(units):
    grouped = []
    cur = None
    HEAD = re.compile(r"^[一二三四五六七八九十百零0-9]{1,4}[章回节部卷]$")
    for blocks in units:
        first_text = ""
        for bf in blocks:
            ps = paras_of_file(bf)
            if ps:
                first_text = ps[0]
                break
        is_head = (bool(first_text) and len(first_text) <= 24
                   and NL not in first_text
                   and not first_text.startswith(ITAL_OPEN))
        if is_head or cur is None:
            cur = []
            grouped.append(cur)
        cur.extend(blocks)
    return [g for g in grouped if g]


def group_by_heads(units, heads):
    grouped = []
    cur = None
    cur_key = None
    for i, blocks in enumerate(units):
        h = heads[i] if i < len(heads) else ""
        key = h if h else cur_key
        if key != cur_key or cur is None:
            cur = []
            grouped.append(cur)
            cur_key = key
        cur.extend(blocks)
    return [g for g in grouped if g]


def unit_key(unit, out_dir):
    # unit[0] is out_dir/<unit>/final.txt (per-chapter) or
    # out_dir/<unit>/<block>/final.txt (per-paragraph).  The chapter-id folder
    # is always the FIRST path component beneath out_dir, regardless of how many
    # block levels sit underneath.  (Using len(unit)==1 was wrong: a
    # per-paragraph unit with a single block looked identical to a per-chapter
    # unit and yielded the block folder name instead of the chapter id.)
    rel = os.path.relpath(os.path.dirname(unit[0]), out_dir)
    folder = rel.split(os.sep)[0]
    return chapter_key_num(folder)


def read_all_final(out_dir):
    parts = []
    for dp, _, fs in os.walk(out_dir):
        for fn in fs:
            if fn == "final.txt":
                try:
                    parts.append(open(os.path.join(dp, fn), encoding="utf-8").read())
                except Exception:
                    pass
    return "".join(parts)


def precompute_work():
    info = {}
    for key, od in find_work_books().items():
        units = build_units(od)
        per = [unit_hanzi(b) for b in units]
        full = read_all_final(od)
        keys = [unit_key(u, od) for u in units]
        info[key] = {"out_dir": od, "units": units, "per_hanzi": per,
                     "keys": keys, "bg": bg_counter(full)}
    return info


def epub_chapter_order(f):
    z = zipfile.ZipFile(f)
    opf = [n for n in z.namelist() if n.endswith("content.opf")][0]
    root = ET.fromstring(z.read(opf))
    items = {it.get("id"): it.get("href") for it in root.iter(NS + "item")}
    spine = [s.get("idref") for s in root.iter(NS + "itemref")]
    base = os.path.dirname(opf)
    res = []
    for sid in spine:
        href = items.get(sid)
        if href and href.endswith(".xhtml"):
            bn = os.path.basename(href)
            if bn in ("nav.xhtml", "title.xhtml", "copyright.xhtml"):
                continue
            full = os.path.normpath(os.path.join(base, href)).replace(os.sep, "/")
            try:
                data = z.read(full).decode("utf-8", "ignore")
            except Exception:
                continue
            if '<div class="titlepage"' in data or '<div class="copyright"' in data or '<nav' in data:
                continue
            res.append((bn, full, data))
    return res, z


def footnote_marker(sup_inner):
    m = re.search(chr(92) + "[" + "([0-9]+)" + chr(92) + "]", sup_inner)
    return ("[[" + m.group(1) + "]]") if m else ""


def extract_paragraphs(z, name, data=None):
    if data is None:
        data = z.read(name).decode("utf-8")
    paras = []
    for attrs, inner in re.findall(r"<p([^>]*)>(.*?)</p>", data, re.S):
        t = inner
        t = re.sub(r"<sup[^>]*>(.*?)</sup>",
                   lambda m: footnote_marker(m.group(1)), t, flags=re.S)
        t = re.sub(r"<br[^>]*>", NL, t)
        t = re.sub(r"<em[^>]*>(.*?)</em>",
                   lambda m: ITAL_OPEN + m.group(1) + ITAL_CLOSE, t, flags=re.S)
        t = re.sub(r"<[^>]+>", "", t)
        t = html.unescape(t)
        paras.append(t)
    return paras


def select_book(epub_bg, work_info):
    best = None
    best_sc = -1.0
    for key, info in work_info.items():
        c = info["bg"]
        inter = sum((epub_bg & c).values())
        uni = sum((epub_bg | c).values())
        sc = (inter / uni) if uni else 0.0
        if sc > best_sc:
            best_sc = sc
            best = key
    if best is None or best_sc < CONTENT_THRESH:
        return None, best_sc
    return best, best_sc


def align_chapters(epub_keys, work_info):
    units = work_info["units"]
    wkeys = work_info["keys"]
    n = len(epub_keys)

    e_num = defaultdict(list)
    w_num = defaultdict(list)
    for i, k in enumerate(epub_keys):
        if k[0] == "num":
            e_num[k[1]].append(i)
    for j, k in enumerate(wkeys):
        if k[0] == "num":
            w_num[k[1]].append(j)
    cmap = [-1] * n
    cov = 0
    for num, eis in e_num.items():
        if num in w_num:
            wj = w_num[num][0]
            for ei in eis:
                cmap[ei] = wj
                cov += 1

    e_vol = defaultdict(list)
    w_vol = {}
    for i, k in enumerate(epub_keys):
        if k[0] == "vol":
            e_vol[k[1]].append(i)
    for j, k in enumerate(wkeys):
        if k[0] == "vol":
            w_vol[k[1]] = j
    vmap = [-1] * n
    vc = 0
    for V, eis in e_vol.items():
        if V in w_vol:
            wj = w_vol[V]
            for ei in eis:
                vmap[ei] = wj
                vc += 1

    if cov == n:
        return "num", cmap
    if len(units) == n:
        return "pos", list(range(n))
    if cov >= max(1, n // 2):
        return "num", cmap
    if vc >= max(1, n // 2):
        return "vol", vmap
    return None, None


def distribute(paragraphs, nblocks):
    n = len(paragraphs)
    if nblocks <= 1:
        return [BLANK.join(paragraphs)]
    out = []
    for i in range(nblocks):
        start = i * n // nblocks
        end = (i + 1) * n // nblocks
        out.append(BLANK.join(paragraphs[start:end]))
    return out


def build_mirror(epub_chaps, work_units, maparr):
    unit_paras = defaultdict(list)
    for ei, wj in enumerate(maparr):
        if wj < 0:
            continue
        unit_paras[wj].extend(epub_chaps[ei][1])
    files = {}
    for wj, blocks in enumerate(work_units):
        nblocks = len(blocks)
        texts = distribute(unit_paras.get(wj, []), nblocks)
        for j, txt in enumerate(texts):
            rel = os.path.relpath(blocks[j], ROOT)
            files[rel] = txt
    return files


def main():
    print("Precomputing work books ...")
    work_info = precompute_work()
    print("  work books found:", len(work_info))

    epubs = sorted(glob.glob(os.path.join(OUT_EPUB_DIR, "*.epub")))
    print("  epubs found:", len(epubs))

    report = []
    matched = 0
    unmatched = []
    mismatched = []
    layout_counter = Counter()
    seen_combo = set()
    pilot_written = 0

    for f in epubs:
        title = os.path.basename(f)
        chap_order, z = epub_chapter_order(f)
        if not chap_order:
            unmatched.append((title, "no content chapters"))
            continue
        epub_chaps = []
        epub_keys = []
        epub_hanzi = []
        epub_parts = []
        for bn, xname, data in chap_order:
            ps = extract_paragraphs(z, xname, data)
            epub_chaps.append((bn, ps))
            epub_keys.append(chapter_key_vol(bn))
            epub_hanzi.append(hanzi_count(BLANK.join(ps)))
            epub_parts.append(BLANK.join(ps))
        epub_bg = bg_counter("".join(epub_parts))
        epub_hanzi_total = sum(epub_hanzi)

        best, best_sc = select_book(epub_bg, work_info)
        if best is None:
            unmatched.append((title, "no source (content score=%.2f)" % best_sc))
            continue
        matched += 1
        info = work_info[best]
        amode, amap = align_chapters(epub_keys, info)
        if amap is None:
            # The work book matched by content but has no 1:1 chapter structure
            # (e.g. a single combined unit).  When there is exactly one out-unit,
            # bulk-distribute every EPUB paragraph into it so all repaired text is
            # preserved; we cannot reconstruct per-chapter structure that the work
            # tree does not have.
            if len(info["units"]) == 1:
                amode, amap = "bulk", [0] * len(epub_chaps)
            else:
                matched -= 1
                unmatched.append((title, "matched %s but no chapter alignment" % best))
                continue
        work_units = info["units"]
        layout = "per-chapter" if all(len(b) == 1 for b in work_units) else "per-paragraph"
        layout_counter[layout] += 1

        mirror = build_mirror(epub_chaps, work_units, amap)
        mirror_hanzi = sum(hanzi_count(t) for t in mirror.values())
        delta = (abs(mirror_hanzi - epub_hanzi_total) / epub_hanzi_total) if epub_hanzi_total else 0.0
        ok = delta <= 0.01
        status = "OK" if ok else "MISMATCH"
        if not ok:
            mismatched.append((title, best, delta, amode))
        report.append((title, best, layout, amode, len(work_units), len(epub_chaps),
                       epub_hanzi_total, mirror_hanzi, round(delta, 4), status, round(best_sc, 3)))

        combo = (layout, amode)
        if pilot_written < PILOT_N and combo not in seen_combo:
            for rel, txt in mirror.items():
                dst = os.path.join(SYNC_TEST_DIR, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, "w", encoding="utf-8") as fo:
                    fo.write(txt)
            pilot_written += 1
            seen_combo.add(combo)

    lines = []
    lines.append("=" * 86)
    lines.append("SYNC EPUB -> WORK  SUMMARY")
    lines.append("=" * 86)
    lines.append("EPUBs total             : %d" % len(epubs))
    lines.append("Matched to a work book  : %d" % matched)
    lines.append("Unmatched (no source)   : %d" % len(unmatched))
    lines.append("Layouts used            : %s" % dict(layout_counter))
    okc = sum(1 for r in report if r[9] == "OK")
    lines.append("Mirrored OK (<1pct)      : %d" % okc)
    lines.append("Mismatched (>1pct delta) : %d" % len(mismatched))
    lines.append("Pilot books written     : %d (sandbox: %s)" % (min(PILOT_N, pilot_written), SYNC_TEST_DIR))
    lines.append("")
    lines.append("Per-book report:")
    lines.append("-" * 86)
    lines.append("%-32s %-20s %-12s %-5s %5s %5s %7s %7s %6s %s" % (
        "epub", "work_book", "layout", "algn", "uChap", "eChap", "eHanz", "mHanz", "delta", "stat"))
    for r in sorted(report, key=lambda x: x[0]):
        lines.append("%-32s %-20s %-12s %-5s %5d %5d %7d %7d %6.3f %s" % (
            r[0][:31], r[1][:19], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]))
    lines.append("")
    if mismatched:
        lines.append("BOOKS NEEDING MANUAL REVIEW (>1pct hanzi delta):")
        for t, k, d, am in mismatched:
            lines.append("  %s  ->  %s  delta=%.4f  align=%s" % (t, k, d, am))
    lines.append("")
    if unmatched:
        lines.append("UNMATCHED EPUBS (no confident source work book):")
        for t, why in unmatched:
            lines.append("  %s  (%s)" % (t, why))

    summary = chr(10).join(lines)
    print(summary)
    with open(os.path.join(ROOT, "pipeline_fix", "sync_report.txt"), "w", encoding="utf-8") as fo:
        fo.write(summary)
    print(chr(10) + "Report written to pipeline_fix/sync_report.txt")
    return summary


if __name__ == "__main__":
    main()
