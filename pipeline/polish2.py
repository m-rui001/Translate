"""Alignment-tolerant polish pass.

polish.py refuses any chapter whose paragraph count differs from the source
block count. That guard is right, but the count differs for two legitimate
reasons:

  * the PDF extractor typed most lines of a poem as `p`, so one Chinese verse
    paragraph legitimately covers ~10 "blocks";
  * the translator occasionally split one long block into two paragraphs, or
    merged two short ones.

Neither is corruption, so the chapter should still be polished. This driver
aligns blocks to paragraphs with a monotone DP scored on the Chinese/English
length ratio, then polishes only runs of consecutive 1:1 matches. Everything
else (poems, ambiguous stretches) is left byte-identical.

The alignment is deliberately conservative: a pair is used only when it sits in
a run of at least MIN_RUN consecutive (block, paragraph) pairs. A wrong pair
would hand the model the wrong English for a Chinese paragraph, and the
structural checks cannot catch that — they only see lengths and punctuation.

Cache lives in work/polish2 so a stale polish.py cache can never be applied to
a different set of paragraphs.

Usage:
    python pipeline/polish2.py --all --apply
    python pipeline/polish2.py --chapters book3c01 --dry
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
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import polish as P  # PROMPT/SYS/check_chunk/call_model/call_one/log

OUT = P.OUT
SRC = P.SRC
CACHE = "E:/Translate/work/polish2"
LOG = "E:/Translate/work/polish2_calls.jsonl"

PARAS_PER_CALL = 26
MIN_RUN = 3
# Chinese/English character ratio is ~0.3, not ~1.7: the English side counts
# spaces and Latin letters, the Chinese side only han characters. The band is
# expressed relative to the chapter's own aggregate ratio so it survives
# differences in prose density and verse.
RATIO_LO_REL, RATIO_HI_REL = 0.55, 1.90

_sem = threading.Semaphore(int(os.environ.get("POLISH_CONCURRENCY", "4")))
_lock = threading.Lock()

CJK = re.compile(r"[\u4e00-\u9fff]")


def clean_para(p: str) -> str:
    """One paragraph must stay one paragraph: a model that emits a blank line
    inside its answer would otherwise split the paragraph on assembly and
    silently change the chapter's block structure."""
    p = p.replace("\r", "")
    p = re.sub(r"\n\s*\n+", " ", p)
    p = re.sub(r"[ \t]+\n", "\n", p)
    return p.strip()


def log(rec: dict) -> None:
    with _lock, open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ────────────────────────────────────────────────────────────── alignment
def _len_en(b: dict) -> int:
    t = b.get("text") or " ".join(b.get("lines") or [])
    return max(1, len(t))


def _len_zh(p: str) -> int:
    return len(CJK.findall(p))


EN_QUOTE = "‘“\"'«»„—"
ZH_QUOTE = "“「『\"—"


def _is_dialogue_en(b: dict) -> bool:
    t = (b.get("text") or " ".join(b.get("lines") or [])).lstrip()
    return bool(t) and t[0] in EN_QUOTE


def _is_dialogue_zh(p: str) -> bool:
    t = p.lstrip()
    return bool(t) and t[0] in ZH_QUOTE


def _sent_en(b: dict) -> int:
    t = b.get("text") or " ".join(b.get("lines") or [])
    return max(1, len([s for s in re.split(r"(?<=[.!?])[\s’'\"]+", t) if s.strip()]))


def _sent_zh(p: str) -> int:
    t = re.sub(r"<verse>|</verse>", "", p)
    return max(1, len([s for s in re.split(r"(?<=[。！？])", t) if s.strip()]))


def align(blocks: list[dict], paras: list[str],
          base: float | None = None) -> list[tuple[int, int]]:
    """Monotone DP alignment on length ratio. Returns matched (block, para) pairs.

    `base` is the expected han-per-source-char ratio. Leave it None when the two
    lists cover the same text (the polish pass): the aggregate ratio is then the
    right expectation. Pass it when one side covers more text than the other —
    a window of a flat reference, say — because the aggregate ratio of a
    mismatched pair of lists is meaningless and lets the DP match anything.
    """
    n, m = len(blocks), len(paras)
    if not n or not m:
        return []
    en = [_len_en(b) for b in blocks]
    zh = [_len_zh(p) for p in paras]
    den = [_is_dialogue_en(b) for b in blocks]
    dzh = [_is_dialogue_zh(p) for p in paras]
    sen = [_sent_en(b) for b in blocks]
    szh = [_sent_zh(p) for p in paras]
    if base is None:
        base = sum(zh) / max(1, sum(en))
    lo, hi = RATIO_LO_REL * base, RATIO_HI_REL * base
    # score matrix: reward a plausible ratio, forbid the impossible. Narration
    # never pairs with dialogue, and the sentence counts have to agree — those
    # two bits stop the off-by-one slips a pure length signal cannot see.
    SKIP = -0.12
    NEG = -1e9
    score = [[0.0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            if den[i] != dzh[j]:
                continue
            r = zh[j] / en[i]
            if not (lo <= r <= hi):
                continue
            if abs(sen[i] - szh[j]) > max(1, sen[i] // 4):
                continue
            score[i][j] = 1.0
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    bt = [[0] * (m + 1) for _ in range(n + 1)]  # 0 diag, 1 up(skip block), 2 left(skip para)
    for i in range(1, n + 1):
        dp[i][0] = dp[i - 1][0] + SKIP
        bt[i][0] = 1
    for j in range(1, m + 1):
        dp[0][j] = dp[0][j - 1] + SKIP
        bt[0][j] = 2
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            best, how = dp[i - 1][j] + SKIP, 1
            v = dp[i][j - 1] + SKIP
            if v > best:
                best, how = v, 2
            s = score[i - 1][j - 1]
            if s > NEG:
                v = dp[i - 1][j - 1] + s
                if v > best:
                    best, how = v, 0
            dp[i][j], bt[i][j] = best, how
    pairs, i, j = [], n, m
    while i > 0 and j > 0:
        h = bt[i][j]
        if h == 0:
            pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif h == 1:
            i -= 1
        else:
            j -= 1
    pairs.reverse()
    return pairs


def trusted_runs(pairs: list[tuple[int, int]], min_run: int = MIN_RUN):
    """Consecutive (i,j) runs — both indices advancing by one — of length >= min_run."""
    runs, cur = [], []
    for bi, pi in pairs:
        if cur and bi == cur[-1][0] + 1 and pi == cur[-1][1] + 1:
            cur.append((bi, pi))
        else:
            if len(cur) >= min_run:
                runs.append(cur)
            cur = [(bi, pi)]
    if len(cur) >= min_run:
        runs.append(cur)
    return runs


def batches(runs):
    """Split runs into model calls of <= PARAS_PER_CALL, never crossing a run."""
    out = []
    for run in runs:
        for k in range(0, len(run), PARAS_PER_CALL):
            out.append(run[k:k + PARAS_PER_CALL])
    return out


# ──────────────────────────────────────────────────────────────── driver
def polish_chapter(cid: str, apply: bool = False, dry: bool = False) -> dict:
    src = json.load(open(os.path.join(SRC, cid + ".json"), encoding="utf-8"))
    blocks = src["blocks"]
    ch_path = os.path.join(OUT, cid, "chapter.md")
    if not os.path.exists(ch_path):
        return {"cid": cid, "skip": "no chapter.md"}
    raw = open(ch_path, encoding="utf-8").read()
    title, body = raw.split("\n", 1)
    draft = P.split_paras(body)

    pairs = align(blocks, draft)
    runs = trusted_runs(pairs)
    covered = sum(len(r) for r in runs)
    if not runs:
        return {"cid": cid, "skip": f"no trusted alignment (blocks={len(blocks)} "
                                    f"paras={len(draft)} pairs={len(pairs)})"}

    final = list(draft)
    changed = 0
    reasons: list[str] = []
    os.makedirs(os.path.join(CACHE, cid), exist_ok=True)
    for grp in batches(runs):
        start, stop = grp[0][1], grp[-1][1] + 1
        cache_p = os.path.join(CACHE, cid, f"p{start:03d}-{stop:03d}.json")
        if os.path.exists(cache_p):
            res = json.load(open(cache_p, encoding="utf-8"))
        else:
            idx = [pi for _bi, pi in grp]
            blk = [blocks[bi] for bi, _pi in grp]
            en = "\n\n".join(f"[{k + 1}] {P.render_src(b)}" for k, b in enumerate(blk))
            zh = "\n\n".join(f"[{k + 1}] {draft[i]}" for k, i in enumerate(idx))
            tag = f"{cid}:{start}-{stop}"
            new = P.call_model(en, zh, len(idx), tag)
            if new is None:
                res = {"accepted": [draft[i] for i in idx], "reasons": ["call failed"],
                       "ok": False, "changed": 0}
            else:
                acc, why = P.check_chunk([draft[i] for i in idx], new, blk)
                for w in list(why):
                    mm = re.match(r"\[(\d+)\]\s*(.+)", w)
                    if not mm:
                        continue
                    k = int(mm.group(1)) - 1
                    i = idx[k]
                    again = P.call_one(P.render_src(blk[k]), draft[i], mm.group(2),
                                       f"{tag}:retry{k + 1}")
                    if again is None:
                        continue
                    _a2, why2 = P.check_chunk([draft[i]], [again], [blk[k]])
                    if not why2:
                        acc[k] = again
                        why = [x for x in why if x != w]
                res = {"accepted": acc, "reasons": why, "ok": True,
                       "changed": sum(1 for a, b in zip(acc, [draft[i] for i in idx]) if a != b)}
            json.dump(res, open(cache_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        for k, i in enumerate([pi for _bi, pi in grp]):
            final[i] = clean_para(res["accepted"][k]) or draft[i]
        changed += res.get("changed", 0)
        reasons += res.get("reasons", [])

    if dry:
        for i, (a, b) in enumerate(zip(draft, final)):
            if a != b:
                print(f"  [{i+1}] OLD: {a[:70]}")
                print(f"       NEW: {b[:70]}")
    if apply:
        open(ch_path, "w", encoding="utf-8").write(title + "\n\n" + P.join_paras(final) + "\n")
    return {"cid": cid, "paras": len(draft), "blocks": len(blocks),
            "aligned": covered, "changed": changed, "rejected": len(reasons),
            "reasons": reasons[:8]}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    if a.chapters:
        cids = [c.strip() for c in a.chapters.split(",") if c.strip()]
    else:
        cids = sorted(os.path.basename(d) for d in glob.glob(OUT + "/*") if os.path.isdir(d))
        cids = [c for c in cids if os.path.exists(os.path.join(OUT, c, "chapter.md"))]
    if not a.all and not a.chapters:
        ap.error("pass --all or --chapters")

    print(f"{len(cids)} chapters, workers={a.workers}, apply={a.apply}", flush=True)
    t0 = time.time()
    done = 0
    tot_ch = tot_al = 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(polish_chapter, c, a.apply, a.dry): c for c in cids}
        for n, (fut, cid) in enumerate(futs.items(), 1):
            try:
                r = fut.result()
            except Exception as e:  # noqa: BLE001
                print(json.dumps({"cid": cid, "error": str(e)[:160]}, ensure_ascii=False), flush=True)
                continue
            print(json.dumps(r, ensure_ascii=False), flush=True)
            done += 1
            tot_ch += r.get("changed", 0)
            tot_al += r.get("aligned", 0)
            if n % 10 == 0:
                print(f"-- {n}/{len(cids)} {time.time() - t0:.0f}s", flush=True)
    print(f"chapters {done} aligned_paras {tot_al} changed {tot_ch} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
