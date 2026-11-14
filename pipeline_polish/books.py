"""Per-book adapters: read the latest Chinese manuscript, polish it, write back.

Every book keeps its own on-disk shape; only the reading and writing is
adapted. The polishing itself is identical, so quality is uniform across the
seven volumes.

Read/write contract per book
    lotr      work_overhaul/lotr/final/*.json      ch["texts"]  (+verse types)
    whale     work_overhaul/whale/final/*.json     ch["texts"]
    soledad   work_overhaul/soledad/final/*.json   ch["texts"]
    zauberberg work_zauberberg/out/*/chapter.md     paragraphs
    camus     work_camus/out/*/final.txt           paragraphs
    chekhov   work_chekhov/out/*/final.txt         paragraphs
    proust    work_proust/out/*/chunk*/final.txt   paragraphs

Source text is fed alongside the Chinese wherever a reliable paragraph-level
alignment exists, because the model polishes far better when it can see what
the sentence is supposed to mean. Where the alignment is known to be broken
(LOTR 42 chapters, Zauberberg 14 sections, Soledad chapter titles) the pass
runs Chinese-only rather than risk pairing a paragraph with the wrong original.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine  # noqa: E402

ROOT = "E:/Translate"
CACHE = "E:/Translate/work_polish2"


# ─────────────────────────────────────────────────────────────── helpers
def paras_of(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def join_paras(ps: list[str]) -> str:
    return "\n\n".join(ps) + "\n"


def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_json(p, d):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


# ─────────────────────────────────────────────────────────────── LOTR
def lotr_units():
    """One unit per chapter chunk; Chinese only where src alignment is broken."""
    units = []
    for p in sorted(glob.glob(f"{ROOT}/work_overhaul/lotr/final/*.json")):
        cid = os.path.basename(p)[:-5]
        ch = load_json(p)
        srcp = f"{ROOT}/work_overhaul/lotr/ch/{cid}.json"
        src, types = None, ch.get("types") or []
        if os.path.exists(srcp):
            s = load_json(srcp)
            cand = s.get("src_paras") or s.get("src") or []
            if len(cand) == len(ch["texts"]):
                src = cand
        items = []
        for i, zh in enumerate(ch["texts"]):
            kind = types[i] if i < len(types) else "p"
            items.append({"zh": zh, "src": (src[i] if src else None), "kind": kind})
        for k, b in enumerate(engine.batch(items, char_budget=2400, max_paras=8)):
            units.append((f"{cid}/b{k:03d}", b))
    return units


def lotr_writeback():
    """Merge polished batches back into final/*.json."""
    changed = 0
    for p in sorted(glob.glob(f"{ROOT}/work_overhaul/lotr/final/*.json")):
        cid = os.path.basename(p)[:-5]
        ch = load_json(p)
        new = merge_batches("lotr", cid, ch["texts"])
        if new != ch["texts"]:
            ch["texts"] = new
            save_json(p, ch)
            changed += 1
    return changed


# ─────────────────────────────────────────────────────────────── whale / soledad
def json_chapter_units(book: str, budget=2400, maxp=8):
    units = []
    for p in sorted(glob.glob(f"{ROOT}/work_overhaul/{book}/final/*.json")):
        cid = os.path.basename(p)[:-5]
        ch = load_json(p)
        src = None
        sp = f"{ROOT}/work_overhaul/{book}/ch/{cid}.json"
        if os.path.exists(sp):
            s = load_json(sp)
            cand = s.get("src_paras") or []
            if len(cand) == len(ch["texts"]):
                src = cand
        items = [{"zh": t, "src": (src[i] if src else None)} for i, t in enumerate(ch["texts"])]
        for k, b in enumerate(engine.batch(items, char_budget=budget, max_paras=maxp)):
            units.append((f"{cid}/b{k:03d}", b))
    return units


def json_chapter_writeback(book: str) -> int:
    changed = 0
    for p in sorted(glob.glob(f"{ROOT}/work_overhaul/{book}/final/*.json")):
        cid = os.path.basename(p)[:-5]
        ch = load_json(p)
        new = merge_batches(book, cid, ch["texts"])
        if new != ch["texts"]:
            ch["texts"] = new
            save_json(p, ch)
            changed += 1
    return changed


# ─────────────────────────────────────────────────────────────── md / txt
def file_units(paths: list[str], relbase: str, src_map=None, skip_heads=True):
    """Paragraph units for chapter.md / final.txt style files.

    Heading lines (bare 第X章 / 抵达 / 前言) are left out of the polish and then
    re-inserted verbatim, so titles can never drift.
    """
    units = []
    for p in paths:
        rel = os.path.relpath(p, relbase).replace("\\", "/")
        ps = paras_of(open(p, encoding="utf-8").read())
        items = []
        for i, zh in enumerate(ps):
            is_head = (len(zh) <= 12 and "\n" not in zh
                       and not zh.endswith(("。", "！", "？", "…", "”")))
            if skip_heads and is_head:
                continue
            s = None
            if src_map:
                s = src_map(rel, i)
            items.append({"zh": zh, "src": s, "idx": i})
        for k, b in enumerate(engine.batch(items, char_budget=2400, max_paras=8)):
            units.append((f"{rel.replace('/', '_')}/b{k:03d}", b))
    return units


def file_writeback(paths: list[str], relbase: str, book: str,
                   skip_heads=True) -> int:
    changed = 0
    for p in paths:
        rel = os.path.relpath(p, relbase).replace("\\", "/")
        old = paras_of(open(p, encoding="utf-8").read())
        new = list(old)
        # rebuild index list identical to file_units
        idxs = []
        for i, zh in enumerate(old):
            is_head = (len(zh) <= 12 and "\n" not in zh
                       and not zh.endswith(("。", "！", "？", "…", "”")))
            if skip_heads and is_head:
                continue
            idxs.append(i)
        cid = rel.replace("/", "_")
        i = 0
        k = 0
        while True:
            f = batch_path(book, cid, k)
            if not os.path.exists(f):
                break
            d = load_json(f)
            for got in d["zh"]:
                if i < len(idxs):
                    new[idxs[i]] = got
                i += 1
            k += 1
        if new != old:
            open(p, "w", encoding="utf-8").write(join_paras(new))
            changed += 1
    return changed


def batch_path(book: str, cid: str, k: int) -> str:
    """Where engine.run stores one batch: <cache>/<book>/<uid with / -> _>.json.

    Kept as a single helper so units, writeback and retry code can never drift
    apart again.
    """
    return os.path.join(CACHE, book, f"{cid.replace('/', '_')}_b{k:03d}.json")


def merge_batches(book: str, cid: str, texts: list[str]) -> list[str]:
    """Apply cached batches for one chapter back onto its paragraph list."""
    out = list(texts)
    k = 0
    i = 0
    while True:
        f = batch_path(book, cid, k)
        if not os.path.exists(f):
            break
        d = load_json(f)
        for got in d["zh"]:
            if i < len(out):
                out[i] = got
            i += 1
        k += 1
    return out


# ─────────────────────────────────────────────────────────────── proust
def proust_units():
    units = []
    for v in ("v3", "v4", "v6", "v7"):
        for p in sorted(glob.glob(f"{ROOT}/work_proust/out/{v}/chunk*/final.txt")):
            cid = f"proust_{v}_" + os.path.basename(os.path.dirname(p))
            ps = paras_of(open(p, encoding="utf-8").read())
            items = [{"zh": zh} for zh in ps]
            for k, b in enumerate(engine.batch(items, char_budget=1800, max_paras=6)):
                units.append((f"{cid}/b{k:03d}", b))
    return units


def proust_writeback() -> int:
    changed = 0
    for v in ("v3", "v4", "v6", "v7"):
        for p in sorted(glob.glob(f"{ROOT}/work_proust/out/{v}/chunk*/final.txt")):
            cid = f"proust_{v}_" + os.path.basename(os.path.dirname(p))
            old = paras_of(open(p, encoding="utf-8").read())
            new = merge_batches("proust", cid, old)
            if new != old:
                open(p, "w", encoding="utf-8").write(join_paras(new))
                changed += 1
    return changed


# ─────────────────────────────────────────────────────────────── 魔山
def zauberberg_paths():
    return sorted(glob.glob(f"{ROOT}/work_zauberberg/out/*/chapter.md"))


# ─────────────────────────────────────────────────────────────── 鼠疫 / 第六病室
def camus_paths():
    return sorted(glob.glob(f"{ROOT}/work_camus/out/c*/final.txt"))


def chekhov_paths():
    return sorted(glob.glob(f"{ROOT}/work_chekhov/out/sec*/final.txt"))


BOOKS = {
    "lotr": (lotr_units, lotr_writeback),
    "whale": (lambda: json_chapter_units("whale"), lambda: json_chapter_writeback("whale")),
    "soledad": (lambda: json_chapter_units("soledad"), lambda: json_chapter_writeback("soledad")),
    "zauberberg": (lambda: file_units(zauberberg_paths(), f"{ROOT}/work_zauberberg/out"),
                   lambda: file_writeback(zauberberg_paths(), f"{ROOT}/work_zauberberg/out",
                                          "zauberberg")),
    "camus": (lambda: file_units(camus_paths(), f"{ROOT}/work_camus/out"),
              lambda: file_writeback(camus_paths(), f"{ROOT}/work_camus/out", "camus")),
    "chekhov": (lambda: file_units(chekhov_paths(), f"{ROOT}/work_chekhov/out"),
                lambda: file_writeback(chekhov_paths(), f"{ROOT}/work_chekhov/out",
                                       "chekhov")),
    "proust": (proust_units, proust_writeback),
}


def book_texts(book: str) -> list[str]:
    """The book's current Chinese paragraphs, for term mining and reporting."""
    if book in ("lotr", "whale", "soledad"):
        out = []
        for p in sorted(glob.glob(f"{ROOT}/work_overhaul/{book}/final/*.json")):
            out.extend(load_json(p)["texts"])
        return out
    pats = {"zauberberg": zauberberg_paths, "camus": camus_paths,
            "chekhov": chekhov_paths}
    if book in pats:
        out = []
        for p in pats[book]():
            out.extend(paras_of(open(p, encoding="utf-8").read()))
        return out
    if book == "proust":
        out = []
        for v in ("v3", "v4", "v6", "v7"):
            for p in sorted(glob.glob(f"{ROOT}/work_proust/out/{v}/chunk*/final.txt")):
                out.extend(paras_of(open(p, encoding="utf-8").read()))
        return out
    return []


def put_book_texts(book: str, texts: list[str]) -> int:
    """Write a flat list of paragraphs back into the book's own file layout.

    Only used by deterministic passes (term unification), which never change the
    paragraph count. A length mismatch is a bug, so it raises instead of
    silently shifting every paragraph after the damage.
    """
    i = 0
    files = 0
    if book in ("lotr", "whale", "soledad"):
        for p in sorted(glob.glob(f"{ROOT}/work_overhaul/{book}/final/*.json")):
            ch = load_json(p)
            n = len(ch["texts"])
            ch["texts"] = texts[i:i + n]
            if len(ch["texts"]) != n:
                raise RuntimeError(f"{book}: paragraph drift at {p}")
            i += n
            save_json(p, ch)
            files += 1
    else:
        pats = {"zauberberg": zauberberg_paths, "camus": camus_paths,
                "chekhov": chekhov_paths}
        if book == "proust":
            paths = [p for v in ("v3", "v4", "v6", "v7")
                     for p in sorted(glob.glob(
                         f"{ROOT}/work_proust/out/{v}/chunk*/final.txt"))]
        else:
            paths = pats[book]()
        for p in paths:
            old = paras_of(open(p, encoding="utf-8").read())
            n = len(old)
            open(p, "w", encoding="utf-8").write(join_paras(texts[i:i + n]))
            i += n
            files += 1
    if i != len(texts):
        raise RuntimeError(f"{book}: put_book_texts consumed {i} of {len(texts)}")
    return files
