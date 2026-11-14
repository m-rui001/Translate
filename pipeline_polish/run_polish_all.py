"""Polish every finished translation in the workspace, in place.

The scope is deliberately broad: four Proust volumes, twenty Gutenberg novels, and
the seven earlier books. All of them are *already translated*; this pass runs over
the existing Chinese and lifts the register without touching content.

Alignment
---------
Each unit is checked first. If the source paragraph count matches the Chinese
paragraph count, the source is passed along and the polisher may also fix
mistranslation. If it does not match, the unit is polished as pure Chinese — the
polisher then has no licence to add or drop anything, which is the correct
behaviour for heading runs and merged dialogue.

Resume
------
A sidecar `<unit>.polished.json` records that the unit was handled, so re-running
is cheap and idempotent. `--force` redoes everything.

Cost control
------------
Two levers matter under per-token billing with caching:
  * a byte-identical system prompt (done, in polish_engine.SYS);
  * not sending a unit that is already good — units shorter than `--min-chars`
    (headings, single lines) are skipped outright.

Usage
-----
    python -X utf8 pipeline_polish/run_polish_all.py --dry-run
    python -X utf8 pipeline_polish/run_polish_all.py --corpora gutenberg
    python -X utf8 pipeline_polish/run_polish_all.py --all --workers 24
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import polish_engine as PE

ROOT = "E:/Translate"
GUT = os.path.join(ROOT, "work_gutenberg")
PROUST_CHUNKS = os.path.join(ROOT, "work_proust", "chunks")
PROUST_OUT = os.path.join(ROOT, "work_proust", "out")
BACKUP = os.path.join(ROOT, "work_polish2", "_backup_polish3")

_lock = threading.Lock()
STATS = {"ok": 0, "skip": 0, "fail": 0, "kept": 0, "chars": 0, "cached": 0}
# Dialogue-heavy units are normally polished a paragraph at a time, which is safest
# but costs one call per line. Under a short-prompt pool the batch path is cheap
# enough, so the flag exists to turn the per-paragraph path off.
ONE_BY_ONE = True


def log(m: str) -> None:
    with _lock:
        print(m, flush=True)


def paras(t: str) -> list[str]:
    return [p.strip() for p in t.split("\n\n") if p.strip()]


def sidecar(path: str) -> str:
    return path + ".polished.json"


# ── unit discovery ──────────────────────────────────────────────────────

def gutenberg_units(books: list[str] | None) -> list[dict]:
    units = []
    for book in sorted(os.listdir(GUT)):
        if books and book not in books:
            continue
        cdir = os.path.join(GUT, book, "chunks")
        if not os.path.isdir(cdir):
            continue
        for fn in sorted(os.listdir(cdir)):
            if not fn.endswith(".json"):
                continue
            cid = fn[:-5]
            spec = json.load(open(os.path.join(cdir, fn), encoding="utf-8"))
            chunks = spec.get("chunks") if isinstance(spec, dict) else spec
            for i, blocks in enumerate(chunks):
                fp = os.path.join(GUT, book, "out", cid, f"c{i:02d}", "final.txt")
                if not os.path.exists(fp) or os.path.getsize(fp) == 0:
                    continue
                src_n, src_text = 0, ""
                for b in blocks:
                    if isinstance(b, dict) and b.get("type") == "p":
                        for x in (b.get("text") or "").split("\n\n"):
                            if x.strip():
                                src_n += 1
                                src_text += x.strip() + "\n\n"
                units.append({"corpus": "gutenberg", "book": book,
                              "key": f"{book}/{cid}/c{i:02d}",
                              "path": fp, "src_paras": src_n,
                              "src": src_text.strip()})
    return units


def proust_units() -> list[dict]:
    units = []
    if not os.path.isdir(PROUST_OUT):
        return units
    for vol in sorted(os.listdir(PROUST_OUT)):
        vdir = os.path.join(PROUST_OUT, vol)
        if not os.path.isdir(vdir):
            continue
        sp_path = os.path.join(PROUST_CHUNKS, vol, "chunks.json")
        spec = {}
        if os.path.exists(sp_path):
            spec = json.load(open(sp_path, encoding="utf-8"))
        for d in sorted(os.listdir(vdir)):
            fp = os.path.join(vdir, d, "final.txt")
            if not os.path.exists(fp) or os.path.getsize(fp) == 0:
                continue
            m = [c for c in d if c.isdigit()]
            k = str(int("".join(m))) if m else ""
            units_src = spec.get(k) or []
            units.append({"corpus": "proust", "book": vol, "key": f"{vol}/{d}",
                          "path": fp, "src_paras": len(units_src),
                          "src": "\n\n".join(units_src)})
    return units


# The five books from the first overhaul keep their text in one of two shapes:
# a directory of `final.txt` files, or a JSON chapter with parallel `texts`/`types`
# arrays. `form` tells `do_unit` which writer to use.
PLAIN_BOOKS = {
    "whale": "work_whale", "soledad": "work_soledad", "camus": "work_camus",
    "chekhov": "work_chekhov", "zauberberg": "work_zauberberg",
}


def plain_units() -> list[dict]:
    units = []
    for book, sub in PLAIN_BOOKS.items():
        root = os.path.join(ROOT, sub, "out")
        if not os.path.isdir(root):
            continue
        for f in sorted(glob.glob(os.path.join(root, "**", "final.txt"),
                                 recursive=True)):
            if os.path.getsize(f) == 0:
                continue
            key = os.path.relpath(f, root).replace(os.sep, "/")[:-len("/final.txt")]
            units.append({"corpus": "plain", "book": book, "key": f"{book}/{key}",
                          "path": f, "form": "txt", "src_paras": 0, "src": ""})
    return units


PUB = os.path.join(ROOT, "work_pub")


def pub_units(books: list[str] | None) -> list[dict]:
    """One final.txt per chunk of the public-domain batch.

    Verse-bearing units are left out: a polisher told to preserve the block count
    will still turn a stanza into prose, and those books need a different pass.
    A unit that opens with its chapter heading keeps that line verbatim (`lead`).
    """
    units = []
    if not os.path.isdir(PUB):
        return units
    for book in sorted(os.listdir(PUB)):
        if books and book not in books:
            continue
        cdir = os.path.join(PUB, book, "chunks")
        if not os.path.isdir(cdir):
            continue
        for fn in sorted(os.listdir(cdir)):
            if not fn.endswith(".json"):
                continue
            cid = fn[:-5]
            try:
                spec = json.load(open(os.path.join(cdir, fn), encoding="utf-8"))
            except Exception:                                     # noqa: BLE001
                continue
            for i, blocks in enumerate(spec.get("chunks") or []):
                fp = os.path.join(PUB, book, "out", cid, f"c{i:02d}", "final.txt")
                if not os.path.exists(fp) or os.path.getsize(fp) == 0:
                    continue
                blocks = [b for b in blocks if isinstance(b, dict)]
                types = [b.get("type") for b in blocks]
                if any(t not in ("p", "head") for t in types):
                    continue
                lead = 1 if types[:1] == ["head"] else 0
                src = "\n\n".join((b.get("text") or "").strip() for b in blocks[lead:])
                units.append({"corpus": "pub", "book": book,
                              "key": f"{book}/{cid}/c{i:02d}", "path": fp,
                              "lead": lead, "src_paras": len(blocks) - lead,
                              "src": src})
    return units


def lotr_units() -> list[dict]:
    root = os.path.join(ROOT, "work_overhaul", "lotr", "final")
    units = []
    if not os.path.isdir(root):
        return units
    for f in sorted(glob.glob(os.path.join(root, "*.json"))):
        units.append({"corpus": "plain", "book": "lotr",
                      "key": f"lotr/{os.path.basename(f)[:-5]}",
                      "path": f, "form": "json", "src_paras": 0, "src": ""})
    return units


def batch(plist: list[str], limit_chars: int) -> list[list[str]]:
    """Group paragraphs into batches of at most `limit_chars` characters."""
    out, cur, n = [], [], 0
    for p in plist:
        if cur and n + len(p) > limit_chars:
            out.append(cur)
            cur, n = [], 0
        cur.append(p)
        n += len(p)
    if cur:
        out.append(cur)
    return out


def do_unit(u: dict, limit_chars: int, force: bool, min_chars: int) -> str:
    fp = u["path"]
    sc = sidecar(fp)
    if not force and os.path.exists(sc):
        return "skip"

    # LotR keeps its paragraphs in a JSON chapter with parallel texts/types arrays.
    # Titles and verse lines are left alone: they are not prose and the polisher
    # has nothing to improve in a four-character heading.
    form = u.get("form", "txt")
    if form == "json":
        doc = json.load(open(fp, encoding="utf-8"))
        texts, types = doc.get("texts") or [], doc.get("types") or []
        idx = [i for i, t in enumerate(texts)
               if (types[i] if i < len(types) else "p") == "p" and t.strip()
               and len(t) >= 60]
        if not idx:
            with open(sc, "w", encoding="utf-8") as f:
                json.dump({"skip": "no prose"}, f)
            return "skip"
        zh = "\n\n".join(texts[i] for i in idx)
    else:
        zh = open(fp, encoding="utf-8").read()

    if len(zh) < min_chars:
        with open(sc, "w", encoding="utf-8") as f:
            json.dump({"skip": "short"}, f)
        return "skip"

    zp = paras(zh)
    if form == "json":
        idx = idx[:len(zp)]
    # A pub unit opens with its chapter heading, which belongs to the unit's output
    # shape but has no source paragraph of its own. It is kept verbatim and the rest
    # of the run is polished against the source.
    lead = min(u.get("lead", 0), max(0, len(zp) - 1))
    head_zh, body = zp[:lead], zp[lead:]
    # Only hand the source over when it lines up paragraph for paragraph *and* the
    # pairing is plausible. Equal counts are not enough: a chapter that gains or loses
    # a heading shifts every pair after it, and a polisher shown the wrong foreign
    # paragraph will summarise it instead of editing the Chinese.
    aligned = u["src_paras"] == len(body) and u["src_paras"] > 0
    src_p = paras(u["src"]) if aligned else []
    if aligned:
        ratios = [len(y) / max(1, len(x)) for x, y in zip(src_p, body)]
        ref = sorted(ratios)[len(ratios) // 2]
        if ref <= 0 or min(ratios) < 0.12 * ref or max(ratios) > 8 * ref:
            aligned, src_p = False, []

    metas: list[dict] = []
    out: list[str] = []

    def run_batch(plist: list[str], slist: list[str], depth: int = 0) -> list[str]:
        """Polish one batch. On paragraph drift, split in half and retry.

        Long batches are where the count goes wrong: the model loses track somewhere
        in the middle and emits one paragraph fewer. Halving converges quickly and
        costs nothing extra when the batch was already fine.
        """
        t, m = PE.polish_unit("\n\n".join(plist), "\n\n".join(slist),
                              f"{u['key']}#{len(out)}")
        metas.append(m)
        got = paras(t)
        if "failed" not in m and len(got) == len(plist):
            return got
        if len(plist) <= 2:
            # A single long paragraph cannot be split further. Retry it alone with a
            # higher temperature so the model does not repeat the same truncated cut.
            t2, m2 = PE.polish_unit(plist[0], slist[0] if slist else "",
                                    f"{u['key']}#solo", temperature=0.55)
            metas.append(m2)
            got2 = paras(t2)
            if "failed" not in m2 and len(got2) == len(plist):
                return got2
            metas[-1]["gave_up"] = m2.get("failed", "drift")
            return plist                                     # keep the original
        mid = len(plist) // 2
        a = run_batch(plist[:mid], slist[:mid] if len(slist) == len(plist) else [],
                      depth + 1)
        b = run_batch(plist[mid:], slist[mid:] if len(slist) == len(plist) else [],
                      depth + 1)
        return a + b

    # Dialogue-heavy chapters defeat batching: consecutive short lines get merged by
    # the model even though the count is enforced, because it reads them as one
    # utterance. Such a chapter is polished one paragraph at a time instead.
    short = sum(1 for p in body if len(p) < 60)
    one_by_one = ONE_BY_ONE and short >= max(4, len(body) // 4)

    if one_by_one:
        # Ask for one paragraph at a time. `run_batch` is not used here: its retry
        # halves the list, and a one-paragraph list has nothing to halve, so a single
        # unlucky reply would discard the whole chapter.
        for i, p in enumerate(body):
            src_i = src_p[i] if aligned and i < len(src_p) else ""
            got = None
            for temp in (0.35, 0.55, 0.7):
                t, m = PE.polish_unit(p, src_i, f"{u['key']}#{i}", temperature=temp)
                metas.append(m)
                cand = paras(t)
                if "failed" not in m and len(cand) == 1:
                    got = cand[0]
                    break
            out.append(got if got is not None else p)
    else:
        for g in batch(body, limit_chars):
            s = src_p[len(out):len(out) + len(g)] if aligned else []
            out.extend(run_batch(g, s))

    if len(out) != len(body) or not PE.no_displacement(body, out):
        # refuse to write a mangled manuscript; keep the original
        with open(sc, "w", encoding="utf-8") as f:
            json.dump({"kept": True, "reason": "count or displacement",
                       "metas": metas}, f, ensure_ascii=False)
        with _lock:
            STATS["kept"] += 1
        return "kept"

    final = head_zh + out
    if form == "json":
        PE.write_json_unit(fp, final, idx, BACKUP)
    else:
        PE.write_unit(fp, "\n\n".join(final), BACKUP)
    with open(sc, "w", encoding="utf-8") as f:
        json.dump({"aligned": aligned, "paras": len(out),
                   "cached": sum(m.get("cached", 0) for m in metas),
                   "gave_up": sum(1 for m in metas if "gave_up" in m),
                   "metas": metas}, f, ensure_ascii=False)
    with _lock:
        STATS["chars"] += len("\n\n".join(out))
        STATS["cached"] += sum(m.get("cached", 0) for m in metas)
    return "ok"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpora", default="gutenberg,proust")
    ap.add_argument("--books", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--batch-chars", type=int, default=6000)
    ap.add_argument("--min-chars", type=int, default=200)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--no-one-by-one", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if a.no_one_by_one:
        globals()["ONE_BY_ONE"] = False

    libs = [x.strip() for x in a.corpora.split(",") if x.strip()]
    books = [x.strip() for x in a.books.split(",") if x.strip()] or None
    units: list[dict] = []
    if "gutenberg" in libs:
        units += gutenberg_units(books)
    if "proust" in libs:
        units += proust_units()
    if "plain" in libs:
        units += plain_units()
    if "lotr" in libs:
        units += lotr_units()
    if "pub" in libs:
        units += pub_units(books)

    todo = [u for u in units if a.force or not os.path.exists(sidecar(u["path"]))]
    if a.limit:
        todo = todo[:a.limit]
    tot = sum(os.path.getsize(u["path"]) for u in units)
    print(f"units={len(units)}  todo={len(todo)}  chars={tot:,}")
    if a.dry_run:
        by = {}
        for u in units:
            by[u["corpus"]] = by.get(u["corpus"], 0) + 1
        for k, v in sorted(by.items()):
            print(f"  {k:12s} {v}")
        return 0
    if not todo:
        return 0

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(do_unit, u, a.batch_chars, a.force, a.min_chars): u
                for u in todo}
        done = 0
        for f in as_completed(futs):
            u = futs[f]
            done += 1
            try:
                r = f.result()
            except Exception as e:                                # noqa: BLE001
                r = "fail"
                log(f"  FAIL {u['key']}: {str(e)[:110]}")
            with _lock:
                STATS[r] = STATS.get(r, 0) + 1
            if done % 20 == 0 or done == len(todo):
                el = time.time() - t0
                log(f"  {done}/{len(todo)} ok={STATS['ok']} skip={STATS['skip']} "
                    f"kept={STATS['kept']} fail={STATS['fail']} "
                    f"{el:.0f}s ({done / max(el, 1) * 60:.0f}/min)")

    el = time.time() - t0
    print(f"\nDONE {el:.0f}s  ok={STATS['ok']} skip={STATS['skip']} "
          f"kept={STATS['kept']} fail={STATS['fail']}  "
          f"chars={STATS['chars']:,}  cached_tok={STATS['cached']:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
