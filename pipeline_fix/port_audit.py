"""Port the audit fixes the EPUB sync missed straight from `scratch/audit_applied.json`.

`sync_revisions` paired work paragraphs against EPUB paragraphs by content and landed
4,199 of the 4,482 reviewed fixes; the rest sat below the similarity floor (the work
paragraph had drifted too far to pair), and the 2026-10-30 EPUB rebuild then made them
disappear from `out/` — 254 verified missing. This script applies them as *verbatim
fragment splices*, which needs no pairing: the audit record carries the exact old and
new wording.

Guarantees, same as the sync pass:
  * one paragraph in -> one paragraph out, byte-count checked before any write;
  * a record whose old wording is absent is reported, never guessed;
  * chapter-file hints (OEBPS/cNNN.xhtml) only disambiguate, never override content;
  * dry run by default; `--apply` writes with a mirror backup.

    python pipeline_fix/port_audit.py            # dry run
    python pipeline_fix/port_audit.py --apply
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline_build"))
sys.path.insert(0, os.path.join(ROOT, "pipeline_fix"))

import sync_revisions as R   # noqa: E402
import sync2 as S            # noqa: E402

AUDIT = os.path.join(ROOT, "scratch", "audit_applied.json")
BACKUP = os.path.join(ROOT, "_bak", "work_auditport_20261030")
REPORT = os.path.join(ROOT, "pipeline_fix", "port_audit_report.txt")
WS = re.compile(r"\s")


def find_span(raw: str, needle_norm: str) -> tuple[int, int] | None:
    """Locate a whitespace-insensitive needle in `raw`; returns raw-text offsets."""
    imap = [i for i, ch in enumerate(raw) if not WS.match(ch)]
    rn = "".join(raw[i] for i in imap)
    pos = rn.find(needle_norm)
    if pos < 0:
        return None
    start = imap[pos]
    end = imap[pos + len(needle_norm) - 1] + 1
    return start, end


def cid_hint(file_field: str) -> str | None:
    m = re.search(r"c(\d+)\.xhtml", file_field or "")
    return "c%03d" % int(m.group(1)) if m else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    records = json.load(open(AUDIT, encoding="utf-8"))
    units_by_book: dict[str, list[dict]] = {}
    # (path, idx) -> list of (old_norm, new) splices, composed in order
    plan: dict[tuple[str, int], list[tuple[str, str]]] = {}
    done = skip_new = unresolved = ambiguous = splice_ok = 0
    notes: list[str] = []

    for rec in records:
        book, old, new = rec["book"], rec.get("old", ""), rec.get("new", "")
        if not old or not new:
            unresolved += 1
            continue
        if book not in units_by_book:
            units_by_book[book] = R.work_units(book)
        units = units_by_book[book]
        on, nn = S.norm(old), S.norm(new)
        have_new = [u for u in units if nn and nn in u["norm"]]
        if have_new:
            skip_new += 1
            continue
        cands = [u for u in units if on in u["norm"]]
        if not cands:
            unresolved += 1
            notes.append(f"NO-MATCH  {book}: {old[:60]}")
            continue
        if len(cands) > 1:
            hint = cid_hint(rec.get("file", ""))
            narrowed = [u for u in cands if hint and u["cid"] == hint] or cands
            if len(narrowed) > 1:
                ambiguous += 1
                notes.append(f"AMBIGUOUS {book}: {old[:50]}  ({len(narrowed)} cands)")
                continue
            cands = narrowed
        u = cands[0]
        # the splice target must exist in the *raw* paragraph too
        if find_span(u["text"], on) is None:
            unresolved += 1
            notes.append(f"RAW-MISS  {book}: {old[:60]}")
            continue
        plan.setdefault((u["path"], u["idx"]), []).append((on, new))
        splice_ok += 1
        done += 1

    # compose multiple splices inside one paragraph against the evolving text
    edits = []
    for (path, idx), splices in plan.items():
        # recover the paragraph text from whichever book's unit table holds the file
        text = None
        for us in units_by_book.values():
            hit = next((u for u in us if u["path"] == path and u["idx"] == idx), None)
            if hit:
                text = hit["text"]
                break
        if text is None:
            continue
        cur = text
        ok = True
        for on, new in splices:
            span = find_span(cur, on)
            if span is None:
                ok = False
                notes.append(f"SPLICE-MISS {path}#{idx}: {on[:40]}")
                break
            cur = cur[:span[0]] + new + cur[span[1]:]
        if ok:
            edits.append({"path": path, "idx": idx, "new": cur,
                          "cid": "", "blk": ""})

    lines = [
        f"audit records          : {len(records)}",
        f"already in work        : {skip_new}",
        f"splices planned        : {len(edits)}  ({splice_ok} records)",
        f"no match (unresolved)  : {unresolved}",
        f"ambiguous (skipped)    : {ambiguous}",
        "",
    ] + notes
    open(REPORT, "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines[:6]))
    print("report ->", REPORT)
    if not a.apply or not edits:
        print("(dry run -- nothing written)" if not a.apply else "(no edits)")
        return 0

    # backup every file about to change, mirror layout
    for path in {e["path"] for e in edits}:
        dst = os.path.join(BACKUP, os.path.relpath(path, "E:/Translate"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            shutil.copy2(path, dst)
    res = R.apply_edits(edits, apply=True)
    print("written:", res["written"], " problems:", res["problems"])
    return 1 if res["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
