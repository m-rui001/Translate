"""Hand-adjudicated corrections, replayed on every rebuild.

final.txt is regenerated from 05_polish.txt by clean(), so a correction typed straight
into final.txt survives only until the next reclean. Every fix adjudicated by hand lives
in fixes.json and is re-applied here.

Matching is paragraph-exact. Substring matching was tried and rejected: a two-character
entry like 库克→厨子, replayed with str.replace(), rewrites every 库克 in the chapter,
including the ones that mean Captain Cook.

Entries are applied in ledger order and they chain. Two fixes can land in the same
paragraph; the second one's `old` was recorded against the paragraph as it stood after
the first was applied. A dict keyed by `old` therefore loses the second fix.
"""
from __future__ import annotations

import json
import os
import re

LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixes.json")
SEP = chr(10) + chr(10)

_cache = None


def _load():
    global _cache
    if _cache is None:
        if os.path.exists(LEDGER):
            _cache = json.load(open(LEDGER, encoding="utf-8"))
        else:
            _cache = []
    return _cache


def _paras(t: str):
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    return [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]


def replay(text: str, cid: str, chunk: str) -> str:
    """Apply fixes.json entries for this chunk. Returns text unchanged if none."""
    entries = [e for e in _load() if e["cid"] == cid and e["chunk"] == chunk]
    if not entries:
        return text

    body = text
    whole = [e for e in entries if e.get("whole")]
    if whole:
        body = whole[-1]["new"]

    ps = _paras(body)
    for e in entries:
        if e.get("whole"):
            continue
        if e["old"] in ps:
            ps[ps.index(e["old"])] = e["new"]
    body = SEP.join(ps)

    return body.strip() + chr(10) if body.strip() else body


def report():
    """Entries that did not land.

    A chained paragraph makes this hard to answer by searching for `new`: after fix A
    lands, fix B's `old` still matches and B replaces it, so A's `new` is gone again by
    the time anyone looks. The honest test is whether the original text is still sitting
    there untouched — if `old` is still a whole paragraph, nothing landed.
    """
    bad = []
    for e in _load():
        path = f"E:/Translate/work_whale/out/{e['cid']}/{e['chunk']}/final.txt"
        if not os.path.exists(path):
            bad.append((e["cid"], e["chunk"], "no final.txt"))
            continue
        ps = _paras(open(path, encoding="utf-8").read())
        if e.get("whole"):
            if e["new"] not in SEP.join(ps):
                bad.append((e["cid"], e["chunk"], "whole-chunk not applied"))
        elif e["old"] in ps:
            bad.append((e["cid"], e["chunk"], "old still present: " + e["old"][:50]))
    return bad


if __name__ == "__main__":
    entries = _load()
    print(f"{len(entries)} entries in ledger")
    for cid, chunk, why in report():
        print(f"  FAILED {cid}/{chunk}: {why}")
