"""Fold the proofreading revisions carried by the shipped EPUBs back into the work trees.

Why this exists
---------------
Earlier rounds repaired prose *inside the EPUB* — `apply_names3.py` and the two audits in
`REPAIR_2026-10-28*.md` rewrote paragraphs in `out/*.epub` directly (4,482 edits: mistranslations,
literal renderings, omissions, additions, numbers, punctuation). The work trees under
`work_*/` were never touched.

`sync_epub_to_work.py` / `sync2.py` tried to fix that by mirroring whole EPUBs back. That was the
wrong operation, and measuring it first is what showed why:

  * the EPUBs are *truncated*. `build_gutenberg.strip_front()` used to skip to the first paragraph
    of 500 chars / 200 hanzi in **every** chapter, so any chapter opening with shorter paragraphs
    lost its head — up to 26% of `maias`. Those EPUBs are a strict subset of the work trees.
  * what the EPUBs *do* carry exclusively is the repair rounds. Verified per paragraph: of the
    `maias` paragraphs that are not byte-identical to work, all are ≥0.96 similar — light edits
    ("清新田舍风味"→"田舍风味", "打罗勃"→"两局牌之间"), never new content.

So the transferable delta is `EPUB − WORK` restricted to paragraphs that **pair up with a work
paragraph**. Everything else the EPUB says is either work text it kept, or text it lost.

What this script does
---------------------
For each book: flatten the work paragraphs (in builder order), flatten the EPUB paragraphs, pair
them by content, and rewrite a work paragraph only when the EPUB has a close-but-different version
of it. Pure deletions and pure insertions are **reported, never applied** — in these books they are
almost always the truncation bug, and applying them would destroy prose.

The rewrite is surgical: it replaces one paragraph's text inside its `final.txt`, leaving the file's
paragraph count, blank-line separators, CRLF line endings and any other paragraph untouched.

Dry by default. `--apply` writes, keeping a copy of every touched file under
`_bak/work_revisions_<date>/`.
"""
from __future__ import annotations

import argparse
import difflib
import glob
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "pipeline_build"))
sys.path.insert(0, os.path.join(ROOT, "pipeline_gutenberg"))
sys.path.insert(0, os.path.join(ROOT, "pipeline_private"))
sys.path.insert(0, HERE)

import build_all as B                      # noqa: E402
import sync2 as S                          # noqa: E402

try:
    import books_meta                      # noqa: E402  (the 20 Gutenberg books)
except Exception:                          # noqa: BLE001
    books_meta = None

GUT = os.path.join(ROOT, "work_gutenberg")
PUB = os.path.join(ROOT, "work_pub")
OUT = os.path.join(ROOT, "out")
BAK = os.path.join(ROOT, "_bak", "work_revisions_20261030")
REPORT = os.path.join(HERE, "revisions_report.txt")

# A pair this similar is the same paragraph, proofread. Below it, the difference is too large to
# to attribute to editing, and rewriting on that basis would replace work text with a guess.
PAIR_MIN = 0.55
# Rewrites below this are checked against a length guard before they are accepted: measured repairs
# stay within a few percent of each other's length, while a mis-pairing (same slot, different text)
# tends to differ a lot. Everything measured above 0.80 is taken as a repair outright.
APPLY_MIN = 0.80
# Longest either side of a rewrite may drift from the other, as a fraction of the longer.
LEN_TOL = 0.35


# --------------------------------------------------------------------------- work paragraphs

def work_root(book: str) -> str | None:
    """Where this book's translation lives: the Gutenberg shelf or the public-domain one."""
    for base in (GUT, PUB):
        if os.path.isdir(os.path.join(base, book, "out")):
            return base
    return None


def work_units(book: str) -> list[dict]:
    """Every paragraph the builder reads, with where it lives, in read order.

    The unit is the `final.txt` file plus the paragraph index inside it, so a rewrite can be applied
    to exactly one paragraph. Chapter and block ids are kept for the report.

    The paragraph index is the one `splice_paragraph` will use, so this must count paragraphs the
    same way the splitter does — one per `build_all.paras` entry, per file.
    """
    base = work_root(book)
    if base is None:
        return []
    units = []
    for cid in sorted(os.path.basename(d) for d in glob.glob(os.path.join(base, book, "out", "c*"))):
        for f in sorted(glob.glob(os.path.join(base, book, "out", cid, "c*", "final.txt"))):
            blk = os.path.basename(os.path.dirname(f))
            try:
                raw = open(f, encoding="utf-8", newline="").read()
            except OSError:
                continue
            for i, p in enumerate(B.paras(raw)):
                units.append({"cid": cid, "blk": blk, "path": f, "idx": i,
                              "text": p, "norm": S.norm(p), "base": base})
    return units


def epub_flat(path: str) -> list[str]:
    return [p for _bn, ps in S.epub_paragraphs(path)[0] for p in ps]


# Books whose work paragraphs are *re-flowed* at build time, so EPUB paragraph boundaries are the
# builder's, not the translator's. Pairing work paragraphs against EPUB paragraphs directly would
# read `verse_lines`' sentence-per-line split as hundreds of "revisions".
VERSE = {"neuegedichte"}


def split_like_builder(text: str) -> list[str]:
    """The lines `build_pub.verse_lines` would make of one work paragraph."""
    return [x.strip() for x in re.split(r"(?<=[。！？；])", text) if x.strip()]


def expand_verse(units: list[dict]) -> tuple[list[dict], list[tuple[int, int]]]:
    """Work paragraphs -> lines, plus each line's (paragraph index, line index)."""
    lines, owner = [], []
    for ui, u in enumerate(units):
        for li, ln in enumerate(split_like_builder(u["text"])):
            lines.append({"text": ln, "norm": S.norm(ln), "cid": u["cid"], "blk": u["blk"],
                          "path": u["path"], "idx": u["idx"], "unit": ui, "line": li})
            owner.append((ui, li))
    return lines, owner


def reflow_edits(units: list[dict], ep: list[str]) -> tuple[list[dict], list[dict], int]:
    """Verse books: pair line to line, then reassemble each paragraph from its lines.

    A paragraph is only rewritten when *every* one of its lines pairs, in order, with one EPUB
    line — otherwise the line count changed and the difference is the builder's re-flow again.
    """
    lines, owner = expand_verse(units)
    pairs = pair(lines, ep)
    by_unit: dict[int, list[tuple[int, int, float]]] = {}
    for wi, ej, r in pairs:
        if wi < len(lines):
            by_unit.setdefault(lines[wi]["unit"], []).append((lines[wi]["line"], ej, r))

    rev, amb = [], []
    for ui, u in enumerate(units):
        got = sorted(by_unit.get(ui, []))
        want = len(split_like_builder(u["text"]))
        if len(got) != want or [g[0] for g in got] != list(range(want)):
            continue
        new_text = "".join(ep[ej] for _li, ej, _r in got)
        if S.norm(new_text) == u["norm"]:
            continue
        worst = min(r for _li, _ej, r in got)
        rec = {"path": u["path"], "idx": u["idx"], "cid": u["cid"], "blk": u["blk"],
               "old": u["text"], "new": new_text, "ratio": worst}
        (rev if worst >= APPLY_MIN else amb).append(rec)
    return rev, amb, len(lines) - len(pairs)


# --------------------------------------------------------------------------- pairing

def pair(work: list[dict], ep: list[str]) -> list[tuple[int, int, float]]:
    """Monotone pairing of work paragraphs to EPUB paragraphs.

    Both lists are the same book in the same order, so `difflib` over normalised text recovers the
    correspondence and refuses to cross a truncated section instead of matching noise across it.
    """
    a = [u["norm"] for u in work]
    b = [S.norm(x) for x in ep]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    pairs = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                pairs.append((i1 + k, j1 + k, 1.0))
        elif tag == "replace":
            # pair the overlapping middle; leftovers stay unpaired
            n = min(i2 - i1, j2 - j1)
            off_i = (i2 - i1 - n) // 2
            off_j = (j2 - j1 - n) // 2
            for k in range(n):
                wi, ej = i1 + off_i + k, j1 + off_j + k
                r = difflib.SequenceMatcher(None, a[wi], b[ej]).ratio()
                pairs.append((wi, ej, r))
    return pairs


# --------------------------------------------------------------------------- rewrite

def splice_paragraph(raw: str, idx: int, new_text: str) -> str:
    """Replace paragraph `idx` of `raw`, keeping separators, line endings and all other text.

    `build_all.paras` splits on `\\n\\s*\\n`, which also matches the CRLF blank lines these files
    carry, so the splitter here has to accept an intervening `\\r` for the same reason — without it
    a CRLF file looks like one giant paragraph and every rewrite would collapse it.
    """
    parts = re.split(r"(\n[ \t\r]*\n)", raw)
    seen = -1
    out = []
    for chunk in parts:
        if not chunk:
            continue
        if re.fullmatch(r"\n[ \t\r]*\n", chunk):
            out.append(chunk)
            continue
        if chunk.strip():
            seen += 1
            if seen == idx:
                lead = chunk[:len(chunk) - len(chunk.lstrip())]
                trail = chunk[len(chunk.rstrip()):]
                out.append(lead + new_text + trail)
                continue
        out.append(chunk)
    return "".join(out)


def apply_edits(edits: list[dict], apply: bool) -> dict:
    """Write the accepted rewrites, one file at a time, verifying paragraph counts."""
    by_file: dict[str, list[dict]] = {}
    for e in edits:
        by_file.setdefault(e["path"], []).append(e)

    written = 0
    problems = []
    for path, es in by_file.items():
        try:
            raw = open(path, encoding="utf-8", newline="").read()
        except OSError as exc:
            problems.append(f"{path}: {exc}")
            continue
        before = len(B.paras(raw))
        new_raw = raw
        # apply from the bottom so earlier indices stay valid
        for e in sorted(es, key=lambda x: -x["idx"]):
            new_raw = splice_paragraph(new_raw, e["idx"], e["new"])
        after = len(B.paras(new_raw))
        if after != before:
            problems.append(f"{path}: paragraph count {before} -> {after}, not written")
            continue
        if not apply:
            written += len(es)
            continue
        dst = os.path.join(BAK, os.path.relpath(path, ROOT))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            shutil.copy2(path, dst)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(new_raw)
        written += len(es)
    return {"written": written, "problems": problems}


# --------------------------------------------------------------------------- driver

def epub_for(book: str) -> tuple[str, str] | tuple[None, None]:
    """(EPUB path, title) for a book key on either shelf."""
    if books_meta is not None and book in books_meta.BOOKS:
        name = books_meta.BOOKS[book]["title_zh"]
        return os.path.join(OUT, f"{name}（坟头草译）.epub"), name
    try:
        import books as booklist
        meta = {b["key"]: b for b in booklist.PUBLIC}.get(book)
    except Exception:  # noqa: BLE001
        meta = None
    if meta:
        name = meta["title_zh"]
        return os.path.join(OUT, f"{name}（坟头草译）.epub"), name
    return None, None


def run(book: str, apply: bool) -> dict:
    ep_path, name = epub_for(book)
    if ep_path is None:
        return {"book": book, "skip": "unknown book key"}
    if not os.path.exists(ep_path):
        return {"book": book, "skip": "no EPUB"}

    work = work_units(book)
    ep = epub_flat(ep_path)
    if not work or not ep:
        return {"book": book, "skip": "empty"}

    if book in VERSE:
        edits, amb_recs, _un = reflow_edits(work, ep)
        kept = apply_edits(edits, apply)
        return {"book": book, "name": name, "work": len(work), "epub": len(ep),
                "pairs": 0, "revised": len(edits), "ambiguous": len(amb_recs),
                "unpaired_work": 0, "written": kept["written"], "problems": kept["problems"],
                "edits": edits,
                "amb": [({"cid": a["cid"], "blk": a["blk"], "idx": a["idx"],
                          "text": a["old"]}, a["new"], a["ratio"]) for a in amb_recs],
                "lost": []}

    pairs = pair(work, ep)
    rev, amb = [], []
    for wi, ej, r in pairs:
        if wi >= len(work):
            continue
        w, etext = work[wi], ep[ej]
        if r >= 1.0 and w["norm"] == S.norm(etext):
            continue
        if r < PAIR_MIN:
            amb.append((w, etext, r))
            continue
        if r >= APPLY_MIN:
            rev.append((w, etext, r))
            continue
        # 0.55–0.80: accept only when the two are interchangeable in size, which is what a
        # proofreading repair looks like. A same-slot paragraph of a different text does not pass.
        lo, hi = sorted((len(w["norm"]), len(S.norm(etext))))
        if hi and (hi - lo) / hi <= LEN_TOL:
            rev.append((w, etext, r))
        else:
            amb.append((w, etext, r))

    edits = [{"path": w["path"], "idx": w["idx"], "cid": w["cid"],
              "blk": w["blk"], "old": w["text"], "new": etext, "ratio": r}
             for w, etext, r in rev]

    paired_w = {wi for wi, _ej, _r in pairs}
    lost = [work[i] for i in range(len(work)) if i not in paired_w]
    kept = apply_edits(edits, apply)

    return {
        "book": book, "name": name, "work": len(work), "epub": len(ep),
        "pairs": len(pairs), "revised": len(edits), "ambiguous": len(amb),
        "unpaired_work": len(lost), "written": kept["written"],
        "problems": kept["problems"], "edits": edits, "amb": amb, "lost": lost,
    }


def all_books() -> list[str]:
    """Every book that has both a work tree and a shipped EPUB."""
    keys = []
    if books_meta is not None:
        keys += list(books_meta.BOOKS)
    try:
        import books as booklist
        keys += [b["key"] for b in booklist.PUBLIC]
    except Exception:  # noqa: BLE001
        pass
    out = []
    for k in sorted(set(keys)):
        p, _n = epub_for(k)
        if p and os.path.exists(p) and work_root(k):
            out.append(k)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("books", nargs="*", help="book keys (default: all Gutenberg books)")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--dump", metavar="DIR", help="write per-book edit samples here")
    args = ap.parse_args(argv)

    books = args.books or all_books()
    if not books:
        print("no books")
        return 1
    if args.apply:
        os.makedirs(BAK, exist_ok=True)

    lines = ["=" * 86,
             "EPUB REVISIONS -> WORK   (%s)" % ("APPLIED" if args.apply else "DRY RUN"),
             "=" * 86,
             "%-14s %6s %6s %8s %8s %8s %8s" % (
                 "book", "work", "epub", "pairs", "revised", "unsure", "unpaired")]
    total_rev = total_w = 0
    payload = {}
    for b in books:
        r = run(b, args.apply)
        if r.get("skip"):
            lines.append("%-14s  skipped: %s" % (b, r["skip"]))
            continue
        payload[b] = r
        total_rev += r["revised"]
        total_w += r["written"]
        lines.append("%-14s %6d %6d %8d %8d %8d %8d" % (
            b, r["work"], r["epub"], r["pairs"], r["revised"], r["ambiguous"], r["unpaired_work"]))
        for p in r["problems"]:
            lines.append("      !! %s" % p)

    lines += ["", "-" * 86,
              "revisions found : %d" % total_rev,
              "revisions %s: %d" % ("written" if args.apply else "to write", total_w),
              "backup          : %s" % (BAK if args.apply else "(none, dry run)")]

    samples = []
    for b, r in payload.items():
        for e in r["edits"][:3]:
            samples += ["", "  %s %s/%s#%d  r=%.3f" % (b, e["cid"], e["blk"], e["idx"], e["ratio"]),
                        "    - %s" % e["old"][:150],
                        "    + %s" % e["new"][:150]]
        for w, t, rr in r["amb"][:2]:
            samples += ["", "  ? %s %s/%s#%d  r=%.3f  NOT APPLIED" % (b, w["cid"], w["blk"], w["idx"], rr),
                        "    - %s" % w["text"][:150],
                        "    + %s" % t[:150]]
    lines += samples

    text = "\n".join(lines) + "\n"
    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write(text)
    if args.dump:
        os.makedirs(args.dump, exist_ok=True)
        for b, r in payload.items():
            with open(os.path.join(args.dump, f"{b}.json"), "w", encoding="utf-8") as fh:
                json.dump({"book": b, "revised": r["revised"], "ambiguous": r["ambiguous"],
                           "edits": r["edits"],
                           "amb": [{"cid": w["cid"], "blk": w["blk"], "idx": w["idx"],
                                    "ratio": rr, "old": w["text"], "new": t}
                                   for w, t, rr in r["amb"]]},
                          fh, ensure_ascii=False, indent=1)
    print(text)
    print("report -> %s" % REPORT)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
