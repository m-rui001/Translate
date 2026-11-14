"""Translate the sixteen newly fetched public-domain titles.

Same chain as `pipeline_gutenberg/run_all.py` -- `workflow.translate_chunk` with the
whale glossary disabled -- pointed at `work_pub` instead of `work_gutenberg`, with two
changes that came out of this week's measurements:

  * **audit off.** On the Proust volumes, auditing fired `repair` on 137 of 151 audits,
    which makes it a second rewrite rather than a check, at 4.3 requests per chunk
    instead of 2. Blind comparison was 2:2 with no-audit and cost 2.5x the time.
  * **concurrency 64.** Measured ceiling is about 4.5 requests/second; 64 workers reach
    it without the 429s that start appearing at 100.

Chinese chapter titles come from the book metadata where the source chapter title is a
number or a publisher's word, and from a short hand-written table where the source has
real titles worth keeping (`Betrachtung`'s thirteen prose pieces, `Neue Gedichte`'s
cycles). Anything unmatched falls back to a position ordinal, because printing
"Erstes Kapitel" or "I" in a Chinese table of contents is worse than printing nothing.

Usage:
    python pipeline_pub/run_pub.py --books prozess,malte --workers 64
    python pipeline_pub/run_pub.py --all
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "pipeline_gutenberg"))
sys.path.insert(0, os.path.join(ROOT, "pipeline_whale"))
sys.path.insert(0, os.path.join(ROOT, "pipeline_private"))

import workflow as wf          # noqa: E402
import chunk as chunktool      # noqa: E402
import books as booklist       # noqa: E402

# Measured on real 8425-character chunks through :8317 on 2026-10-27 afternoon.
#
#   cf-llama3.1-70b  7/7 ok  77 s      cf-llama4-scout  5/5 ok  83 s
#   or-nemotron-3-ultra  2/5 ok 150-200 s read timeouts
#   or-north-mini-code   3/12 ok, six "empty content"
#   every ms-* id: HTTP 400 "insufficient balance" -- the ModelScope account is spent
#   every sf-* id: HTTP 402 -- the SiliconFlow account is spent too
#
# So the free capacity on this box is one Cloudflare key, one OpenRouter key, one spent
# ModelScope key and one spent SiliconFlow key (grep E:/tools/freeai/.env.keys: there are
# no second accounts). Cloudflare's free allocation is 10 000 *neurons* a day and an 8k
# chunk on the 70b burns plenty of them, so this list goes dead during the day rather
# than gradually slowing. `xm:`/`ox:` answer fast but spend reseller credits, which this
# batch must not do. `lc` shares one semaphore of 10 across all gateway ids, so workers
# past ten only queue.
WRITER = ["lc:cf-llama3.1-70b",
          "lc:cf-llama4-scout"]

# The supervisor probes the gateway each cycle and hands over only the ids that actually
# answered, so a quota that returns at the daily reset gets used without editing this
# file. Without it the static list above is the default.
if os.environ.get("PUB_WRITER"):
    WRITER = [m.strip() for m in os.environ["PUB_WRITER"].split(",") if m.strip()]
_print_lock = threading.Lock()

# Publisher furniture and provenance lines, used only to decide whether a very short
# chapter is front matter or a poem. Deliberately narrow: an earlier version included
# `^[A-Z ]{3,}$` to catch all-caps imprints, but that also matched poetry titles
# ("DAVID SINGT VOR SAUL") and deleted two real poems from `Neue Gedichte`. Only the
# words that literally name a publisher, a printer, a copyright or a proofreading team
# are allowed here.
IMPRINT = re.compile(
    r"(?:VERLAG|Verlag|Copyright|Printed|PRINTED|Buchdruck|Druck von|"
    r"Proofreading|Distributed Proofreading|Gutenberg|Alle Rechte|"
    r"Rechte vorbehalten|Insel-Verlag|Harcourt|"
    # French imprint furniture. `Notre-Dame de Paris` carries a 265-character page
    # reading "TOUS DROITS RÉSERVÉS ... ÉDITION DÉFINITIVE ... ŒUVRES COMPLÈTES DE
    # VICTOR HUGO", none of which the German/English markers above would touch, so the
    # chapter was being translated as if it were prose.
    r"TOUS DROITS|DROITS RÉSERVÉS|ÉDITION DÉFINITIVE|ŒUVRES COMPLÈTES|"
    r"IMPRIMERIE|ACHEVÉ D'IMPRIMER|DEPOSÉ LEGAL|Tous droits|"
    r"http://www\.pgdp\.net|www\.gutenberg\.org)", re.I)

# A sentence, for deciding that a short block is a title rather than text. German and
# English both end sentences this way, and Chinese translations of these files do too.
SENTENCE = re.compile(r"[.!?。！？…][\s\"'»«”’）)]*$")


def log(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def chunk_plan(key: str) -> dict:
    """Chunk every chapter once, cached under work_pub/<key>/chunks."""
    src = os.path.join(ROOT, "work_pub", key, "src")
    cdir = os.path.join(ROOT, "work_pub", key, "chunks")
    os.makedirs(cdir, exist_ok=True)
    plan = {}
    for p in sorted(glob.glob(os.path.join(src, "c*.json"))):
        cid = os.path.splitext(os.path.basename(p))[0]
        cache = os.path.join(cdir, cid + ".json")
        if os.path.exists(cache):
            plan[cid] = json.load(open(cache, encoding="utf-8"))
            continue
        d = json.load(open(p, encoding="utf-8"))
        chunks = merge_tiny(chunktool.chunk_blocks(d["blocks"]))
        spec = {"id": cid, "title_src": d.get("title", ""),
                "title_zh": d.get("title", ""), "chunks": chunks}
        json.dump(spec, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
        plan[cid] = spec
    return plan


def merge_tiny(chunks: list[list[dict]], min_words: int = 60) -> list[list[dict]]:
    """Fold a token-sized chunk into its neighbour.

    `chunk_blocks` splits at a word cap and emits what is left over, so a chapter whose
    first paragraph is only the title line produced a chunk of 13 characters followed by
    a chunk of 9,857. `translate_chunk` correctly refuses to call 13 characters a
    translation (`no usable first translation`), which is how `Ein Landarzt` and the
    fifth chapter of `Der Prozess` failed while everything around them succeeded.

    A stub joins the chunk *after* it -- a heading belongs with the text it heads. A
    trailing stub has nothing after it, so it joins the chunk before.
    """
    if len(chunks) < 2:
        return chunks

    def words(c: list[dict]) -> int:
        return sum(chunktool.block_words(b) for b in c)

    out: list[list[dict]] = []
    pending: list[dict] | None = None
    for c in chunks:
        if pending is not None:
            # the stub has just been merged forward; this chunk is a normal one
            out.append(pending + c)
            pending = None
            continue
        if words(c) < min_words:
            pending = c
            continue
        out.append(c)
    if pending is not None:
        if out:
            out[-1] = out[-1] + pending
        else:
            out.append(pending)
    return out


def is_front_matter(spec: dict) -> bool:
    """True for a chapter that is only a title page, with no prose behind it.

    `Der Prozess` opens with a chapter of three lines -- FRANZ KAFKA / DER PROZESS ROMAN
    / VERLAG DIE SCHMIEDE BERLIN 1925 -- that the extractor kept because it is separated
    from the text like any chapter. Translating it produces a Chinese imprint page in the
    middle of the front matter, and no amount of prompting makes it a chapter.

    Length alone will not do it. A first attempt used "longest paragraph under 120
    characters and whole chapter under 400", which also deleted a genuine three-stanza
    poem from `Neue Gedichte` -- verse is short by nature, as is a page of aphorisms.

    What actually distinguishes an imprint is content: no word in it begins a sentence,
    and it carries publisher furniture. So the test is: short *and* every paragraph looks
    like a name, a title, a date, a place or a provenance line.
    """
    allp = [b["text"] for c in spec.get("chunks", []) for b in c]
    paras = [t for t in allp if t.strip()]
    if not paras:
        return True
    longest = max(len(t) for t in paras)
    total = sum(len(t) for t in paras)
    if total >= 900:
        return False
    # One imprint marker in a chapter this short is enough. Requiring almost every line
    # to match was wrong: a title page is half furniture and half the book's own title,
    # subtitle, dedication and print run, none of which carry a publisher's name. Two
    # clean hits -- "Proofreading Team at ..." and "Insel-Verlag / Leipzig / 1918" -- are
    # conclusive for 264 characters of text, while a three-stanza poem has none at all.
    if any(IMPRINT.search(t) for t in paras):
        return True
    # A table of contents on its own is also front matter. `Betrachtung` and `Ein Landarzt`
    # each open with one: title, publisher, copyright, dedication, then "目录" and fourteen
    # entries. `The Voyage Out` opens with a run of nothing but "CHAPTER I. CHAPTER II. ..."
    # to CHAPTER XXVII. Nothing in either is prose, and translating them puts a second
    # contents list in the middle of the book, contradicting the one the builder generates.
    joined = " ".join(paras)
    if "目录" in joined and longest < 200:
        return True
    if re.search(r"Contents", joined, re.I) and joined.count("CHAPTER") >= 5:
        return True
    # A contents page whose entries are story titles rather than numbered chapters. The
    # rule above only fires when the word CHAPTER appears five times, but `Dubliners`
    # lists fifteen story names instead -- "Contents The Sisters An Encounter Araby
    # Eveline ..." -- and its 221 characters went straight into translation. What makes
    # such a page unmistakable is that it holds no sentence at all: every entry is a bare
    # title, so the joined text has no terminal punctuation anywhere.
    if (re.search(r"\bContents\b", joined) and total < 600
            and not any(SENTENCE.search(t) for t in paras)):
        return True
    if re.match(r"^[\sA-Za-z0-9,.\-]*$", joined) and "CHAPTER" in joined:
        return True
    # Last resort for imprints that name no publisher at all. `Die Aufzeichnungen des
    # Malte Laurids Brigge` opens with two lines -- a typesetter's code (`Ver.04.29.93*END*`)
    # and the title -- sixty characters in total, no prose anywhere. Nothing that short
    # and without a single sentence in it can be a chapter, whatever words it uses.
    #
    # The 200-character ceiling matters. `Neue Gedichte` opens with 4,747 characters that
    # also begin "NEUE GEDICHTE / Von / RAINER MARIA RILKE / IM INSEL-VERLAG" -- but they
    # go on into the first poems of the collection. Shorter than 200 is a title page;
    # longer than that and there is text inside it worth translating.
    if total < 200 and not any(SENTENCE.search(t) for t in paras):
        return True
    return False


def run_book(key: str, workers: int, resume: bool, polish: bool = False) -> dict:
    work = os.path.join(ROOT, "work_pub", key)
    out_root = os.path.join(work, "out")
    os.makedirs(out_root, exist_ok=True)

    # No glossary: these sixteen titles share no proper nouns with the Moby-Dick /
    # Solitude / Proust glossary, and an irrelevant name table only costs prompt tokens
    # and invites the model to substitute a familiar name for the right one.
    wf.rel_gl = lambda source: []
    wf.render_gl = lambda entries: ""

    plan = chunk_plan(key)
    units = []
    skipped = []
    for cid, spec in plan.items():
        os.makedirs(os.path.join(out_root, cid), exist_ok=True)
        if is_front_matter(spec):
            skipped.append(cid)
            continue
        for i, blocks in enumerate(spec["chunks"]):
            units.append((cid, i, blocks))

    pools = {"writer": WRITER, "auditor": [], "polisher": WRITER, "explorer": []}
    t0 = time.time()
    ok = cached = fail = 0

    def one(u):
        cid, i, blocks = u
        od = os.path.join(out_root, cid, f"c{i:02d}")
        try:
            r = wf.translate_chunk(blocks, od, pools, f"{key}:{cid}/c{i:02d}",
                                   nums=True, resume=resume, audit=False,
                                   polish=polish, analysis_text="")
            return "cached" if r.get("cached") else "ok"
        except Exception as e:        # noqa: BLE001
            log(f"  [{key}/{cid}/c{i:02d}] FAIL {str(e)[:110]}")
            return "fail"

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(one, u) for u in units]
        done = 0
        for f in as_completed(futs):
            r = f.result()
            done += 1
            ok += r == "ok"
            cached += r == "cached"
            fail += r == "fail"
            if done % 20 == 0 or done == len(units):
                log(f"  {key}: {done}/{len(units)} chunks "
                    f"(new={ok} cached={cached} fail={fail})")

    for cid in plan:
        if cid in skipped:
            continue
        assemble_chapter(key, cid, out_root)
    log(f"[{key}] done {len(plan) - len(skipped)} chapters / {len(units)} chunks in "
        f"{time.time() - t0:.0f}s (new={ok} cached={cached} fail={fail}"
        f"{', skipped front matter ' + str(skipped) if skipped else ''})")
    return {"book": key, "chapters": len(plan) - len(skipped), "chunks": len(units),
            "ok": ok, "cached": cached, "fail": fail}


def assemble_chapter(key: str, cid: str, out_root: str) -> int:
    d = os.path.join(out_root, cid)
    parts = []
    for p in sorted(glob.glob(os.path.join(d, "c*", "final.txt"))):
        t = open(p, encoding="utf-8").read().strip()
        if t:
            parts.append(t)
    if not parts:
        return 0
    body = "\n\n".join(parts)
    open(os.path.join(d, "chapter.md"), "w", encoding="utf-8").write(body + "\n")
    return len(body)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", default="")
    ap.add_argument("--all", action="store_true")
    # 12 was measured, not guessed: two xiaomi keys at 6-wide each sustain 3.37 ok/s
    # with zero transport failures, while 16 drops to 2.88 and 8-per-key to 0.13 as the
    # shared host starts queueing. The old default of 64 belonged to cssmapi, which had
    # a 160-wide semaphore and is now dead.
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--no-resume", action="store_true")
    # A second polish pass with the *same* model was measured three times and never
    # changed the text: similarity stayed between 0.988 and 1.000, so the pass costs a
    # full extra API call per chunk for nothing. Off by default here.
    ap.add_argument("--polish", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    want = [b for b in a.books.split(",") if b] if a.books else []
    metas = [m for m in booklist.PUBLIC if a.all or not want or m["key"] in want]
    if a.dry_run:
        tot = 0
        for m in metas:
            plan = chunk_plan(m["key"])
            n = sum(len(s["chunks"]) for s in plan.values())
            tot += n
            print(f"  {m['key']:15s} ch={len(plan):3d} chunks={n:4d}")
        print(f"TOTAL chunks={tot}")
        return

    results = []
    for m in metas:
        try:
            results.append(run_book(m["key"], a.workers, not a.no_resume, a.polish))
        except Exception as e:                       # noqa: BLE001
            log(f"[{m['key']}] ERROR {str(e)[:140]}")
    print("\n=== summary ===")
    for r in results:
        print(f"  {r['book']:15s} ch={r['chapters']:3d} chunks={r['chunks']:4d} "
              f"new={r['ok']:3d} cached={r['cached']:3d} fail={r['fail']:2d}")
    print(f"TOTAL new={sum(r['ok'] for r in results)} "
          f"cached={sum(r['cached'] for r in results)} "
          f"fail={sum(r['fail'] for r in results)}")


if __name__ == "__main__":
    main()
