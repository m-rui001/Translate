"""Blind A/B evaluation for the two new projects.

Compares our translation against the published Chinese one, window by window,
with the original-language text in front of the judge.

Differences from eval_whale.py, and why:
  * the reference is one flat paragraph list for the whole book, not one file
    per chapter, so chapters are located by a global length-ratio alignment
    instead of a per-file offset;
  * the reference EPUB carries CIP data at the front and a table of contents at
    the back — both are stripped before alignment, otherwise every offset is
    poisoned;
  * three judges from different families, and none of them is the model that
    wrote the polish pass.

Usage:
    python pipeline_new/eval_new.py --book soledad --windows 12
"""
from __future__ import annotations

import argparse
import bisect
import json
import os
import random
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pipeline"))
sys.path.insert(0, HERE)
import llm  # noqa: E402
from assemble_new import load_chapter  # noqa: E402
import polish2 as P2  # noqa: E402  (monotone DP paragraph aligner)

BOOKS = {
    "soledad": {
        "src": "E:/Translate/work_soledad/src",
        "out": "E:/Translate/work_soledad/out",
        "ref": "E:/Translate/work_soledad/ref_zh.json",
        "title": "《百年孤独》",
        "author": "加西亚·马尔克斯",
        "lang": "西班牙语",
        "note": "马尔克斯的文体是西班牙语文学的顶点：长句连绵、时态游走、"
                "魔幻与日常同一副笔调，叙述者从不惊讶。不要用现代白话小说的平滑标准"
                "去奖励“读起来顺”的译本。",
    },
    "zauberberg": {
        "src": "E:/Translate/work_zauberberg/src",
        "out": "E:/Translate/work_zauberberg/out",
        "ref": "E:/Translate/work_zauberberg/ref_zh.json",
        "title": "《魔山》",
        "author": "托马斯·曼",
        "lang": "德语",
        # the reference edition has no Einführung (so chapter one has nothing to
        # compare against), splits every line of dialogue into its own
        # paragraph, and carries the publisher's blurb and the footnotes in the
        # same list
        "skip_chapters": ["index_split_000", "index_split_001", "index_split_022"],
        "ref_head": "我们之所以想讲汉斯·卡斯托普的故事",
        "ref_drop": r"^\[\d+\]",
        "band_align": True,
        "note": "托马斯·曼的文体是德语散文的顶点：反讽的叙述者、绵长的从句、"
                "哲学论辩与日常生活交错，讽刺藏在庄重的句法里。不要用现代白话小说的"
                "平滑标准去奖励“读起来顺”的译本。",
    },
}

SEP = re.compile(r"\n\s*\n")
CJK = re.compile(r"[\u4e00-\u9fff]")
TOC = re.compile(r"^第[一二三四五六七八九十百零\d]+章$")

PROMPT = """你是资深文学翻译评委，{lang}与中文俱精。下面是{title}（{author}）的一段原文，
以及两份中文译文（甲、乙），出自两个不同的中文译本。

<source>
{source}
</source>

<甲>
{a}
</甲>

<乙>
{b}
</乙>

评判须知：
1. 两份译文覆盖的原文范围可能略有出入，请只就比较范围内彼此对应的部分评判，
   不要把范围差异算作漏译或增译。
2. 人名、地名的译法差异属于流派不同，不计入扣分。
3. {note}

按四个维度各打 0-10 分：
- 忠实：是否准确传达原文的信息、细节、因果、语气，有无漏译、误译、增译。
- 文学性：汉语是否有文学质地，节奏、意象、句法是否有分量。
- 中文自然度：是否像中文作品，有无翻译腔。
- 腔调：叙述者的声音是否立得住。

最后给出总体判断。严格按下面的格式输出，不要写别的：

甲 忠实: <分数>
甲 文学性: <分数>
甲 自然度: <分数>
甲 腔调: <分数>
乙 忠实: <分数>
乙 文学性: <分数>
乙 自然度: <分数>
乙 腔调: <分数>
胜者: 甲
理由: <一句话>
"""

DIMS = ["忠实", "文学性", "自然度", "腔调"]
_lock = threading.Lock()


def load_src(src_dir: str):
    ids = sorted(os.path.splitext(f)[0] for f in os.listdir(src_dir)
                 if f.endswith(".json") and f != "index.json")
    per = {}
    for cid in ids:
        d = json.load(open(os.path.join(src_dir, cid + ".json"), encoding="utf-8"))
        per[cid] = [b["text"].strip() for b in d["blocks"] if b["type"] == "p"]
    return per


def load_ours(cfg: dict, cid: str):
    # the chunk outputs, not chapter.md: a re-run chunk leaves the chapter file
    # stale and the judge would be shown text the pipeline no longer produces
    paras = load_chapter(cfg, cid)
    return [x for x in (paras or []) if CJK.search(x)]


def load_ref(path: str, cfg: dict):
    """Body paragraphs of the published translation, in reading order.

    The EPUBs carry publisher front matter at the front and the maker's notes,
    footnotes or a table of contents at the back. Both have to go, and nothing
    else: an earlier version also dropped every paragraph shorter than 25
    characters, which silently deleted most of the dialogue — the reference
    then no longer lined up with the source, and every alignment downstream
    drifted.
    """
    paras = [(t or "").strip() for t in json.load(open(path, encoding="utf-8"))["paras"]]
    head = cfg.get("ref_head")
    if head:
        head = next((i for i, t in enumerate(paras) if t.startswith(head)), 0)
    else:
        head = next((i for i, t in enumerate(paras) if t.startswith("多年以后")), 0)
    tails = cfg.get("ref_tail") or ["以下内容为原PDF", "制作说明"]
    tail = next((i for i, t in enumerate(paras)
                 if i > head and any(t.startswith(x) for x in tails)), len(paras))
    body = paras[head:tail]
    drop = re.compile(cfg["ref_drop"]) if cfg.get("ref_drop") else None
    return [t for t in body if t and CJK.search(t) and not (drop and drop.match(t))]


def han_len(s: str) -> int:
    return sum(1 for c in s if CJK.match(c))


def banded_align(src: list[str], paras: list[str], base: float, band: int = 30):
    """Monotone DP restricted to a band around the proportional position.

    A free DP over a reference that is three times finer than the source has
    too much freedom — every short paragraph can match every other short
    paragraph, and the alignment wanders. Anchoring each source paragraph to
    where the cumulative lengths say it must lie, and letting the DP move only
    within `band` paragraphs of that, keeps the local freedom that dialogue
    splits need without letting a bad match survive to the end of the book.
    """
    n, m = len(src), len(paras)
    if not n or not m:
        return []
    zh = [han_len(p) for p in paras]
    cum_ref = [0]
    for x in zh:
        cum_ref.append(cum_ref[-1] + x)
    exp, acc = [], 0.0
    for t in src:
        acc += len(t) * base
        exp.append(min(m - 1, bisect.bisect_left(cum_ref, acc)))

    SKIP = -0.12
    rows: list[dict] = []
    backs: list[dict] = []
    for i in range(n + 1):
        lo = 0 if i == 0 else max(0, exp[i - 1] - band)
        hi = m if i == 0 else min(m, exp[i - 1] + band)
        prev, prev_back = (rows[i - 1], backs[i - 1]) if i else ({0: 0.0}, {0: 0})
        cur, back = {}, {}
        run = -1e9
        for j in range(lo, hi + 1):
            best, how = -1e9, 0
            if i:
                run = max(run + SKIP, prev.get(j, -1e9))
                best, how = run, 1
            if j and (j - 1) in cur:
                v = cur[j - 1] + SKIP
                if v > best:
                    best, how = v, 2
            if i and j:
                pv = prev.get(j - 1)
                if pv is not None:
                    r = zh[j - 1] / max(1, len(src[i - 1]))
                    if 0.55 * base <= r <= 1.9 * base:
                        v = pv + 1.0
                        if v > best:
                            best, how = v, 3
            cur[j], back[j] = best, how
        rows.append(cur)
        backs.append(back)

    pairs, i, j = [], n, min(m, exp[-1] + band) if exp else m
    j = max(backs[-1]) if backs else 0
    while i > 0 and j >= 0:
        how = backs[i].get(j, 0)
        if how == 3:
            pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif how == 1:
            i -= 1
        elif how == 2:
            j -= 1
        else:
            break
    pairs.reverse()
    return pairs


def map_ref(chaps, src_by, ours_by, ref, src_chars_all, cfg):
    """our paragraph index → (source paragraph index, reference paragraph index).

    Both hops are measured against the original language — ours→src and
    src→ref — because Chinese↔Chinese character counts carry no signal. The DP
    needs an explicit `base`: the reference covers the whole book while only
    part of it is translated, so the aggregate ratio of the two lists is not
    the ratio of any pair inside them.
    """
    src_all = [t for cid in chaps for t in src_by[cid]]
    src_chars = sum(len(t) for t in src_all)
    base_ref = sum(han_len(t) for t in ref) / max(1, src_chars_all)
    base_ours = sum(han_len(p) for cid in chaps for p in ours_by[cid]) / max(1, src_chars)
    print(f"base: ours {base_ours:.3f} ref {base_ref:.3f} han per source char")

    if cfg.get("band_align"):
        p_ref = banded_align(src_all, ref, base_ref)
    else:
        blocks = [{"type": "p", "text": t} for t in src_all]
        p_ref = P2.align(blocks, ref, base=base_ref)
    p_src = P2.align([{"type": "p", "text": t} for t in src_all],
                     [p for cid in chaps for p in ours_by[cid]], base=base_ours)
    print(f"src↔ref pairs {len(p_ref)}/{len(src_all)}  "
          f"src↔ours pairs {len(p_src)}/{len(src_all)}")

    ref_of_src = dict(p_ref)
    m = {oi: (si, ref_of_src[si]) for si, oi in p_src if si in ref_of_src}
    return m, base_ref, base_ours


def judge(idx, src_text, a_text, b_text, model, seed, cfg, ours_is_a):
    prompt = PROMPT.format(lang=cfg["lang"], title=cfg["title"], author=cfg["author"],
                           note=cfg["note"], source=src_text, a=a_text, b=b_text)
    rec = {"idx": idx, "judge": model}
    try:
        out, used = llm.chat([{"role": "user", "content": prompt}], models=[model],
                             temperature=0.2, max_tokens=1200,
                             tag=f"eval:{idx}", timeout=300)
    except Exception as e:  # noqa: BLE001
        rec["err"] = str(e)[:200]
        return rec
    rec["judge"] = used

    def num(prefix):
        d = {}
        for dim in DIMS:
            m = re.search(rf"{prefix}\s*{dim}\s*[:：]\s*([\d.]+)", out)
            if m:
                d[dim] = float(m.group(1))
        return d or None

    x, y = num("甲"), num("乙")
    if not x or not y:
        rec["err"] = "unparsed"
        rec["raw"] = out[:300]
        return rec
    rec["ours"] = x if ours_is_a else y
    rec["ref"] = y if ours_is_a else x
    w = re.search(r"胜者\s*[:：]\s*([甲乙])", out)
    if w:
        rec["winner"] = ("ours" if w.group(1) == "甲" else "ref") if ours_is_a else \
                        ("ours" if w.group(1) == "乙" else "ref")
    else:
        rec["winner"] = "tie"
    m = re.search(r"理由\s*[:：]\s*(.+)", out)
    rec["why"] = (m.group(1).strip()[:300] if m else "")
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, choices=sorted(BOOKS))
    ap.add_argument("--windows", type=int, default=12)
    ap.add_argument("--window-size", type=int, default=4)
    ap.add_argument("--judges", default="ox:gemini-3.8-flash,xm:mimo-v2.6-flash,oxd:deepseek-v4.1-flash")
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--dry-run", action="store_true", help="print aligned windows, no judging")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    cfg = BOOKS[a.book]

    per = load_src(cfg["src"])
    skip = set(cfg.get("skip_chapters") or [])
    chaps, ours_by, src_by = [], {}, {}
    for cid, src in per.items():
        if cid in skip:
            continue
        o = load_ours(cfg, cid)
        if not o:
            # stop at the first gap: the reference is one flat list, so a
            # chapter missing from the middle would shift every expectation
            # after it and the whole alignment would drift out of its band
            break
        chaps.append(cid)
        ours_by[cid], src_by[cid] = o, src
    ours = [p for cid in chaps for p in ours_by[cid]]
    loc = [(cid, i) for cid in chaps for i in range(len(ours_by[cid]))]
    ref = load_ref(cfg["ref"], cfg)
    print(f"src chapters={len(per)} translated={len(chaps)} "
          f"ours={len(ours)} ref={len(ref)}")
    if not ours:
        print("nothing translated yet")
        return

    print("aligning ours ↔ src ↔ ref")
    src_chars_all = sum(len(t) for src in per.values() for t in src)
    ref_of, base_ref, base_ours = map_ref(chaps, src_by, ours_by, ref, src_chars_all, cfg)
    src_flat = [t for cid in chaps for t in src_by[cid]]
    print(f"mapped paragraphs: {len(ref_of)}/{len(ours)}")

    jobs = []
    i = 0
    while i + a.window_size <= len(ours):
        win = list(range(i, i + a.window_size))
        ok = all(w in ref_of for w in win)
        if ok:
            # The source side has to advance one paragraph at a time, or the
            # original text stops covering exactly what the judge is shown.
            si = [ref_of[w][0] for w in win]
            rj = [ref_of[w][1] for w in win]
            ok = all(si[k] == si[0] + k for k in range(1, len(win)))
            # The reference side only has to advance. Some editions set every
            # line of dialogue as its own paragraph, so one paragraph here can
            # be three there; taking the span up to the next match keeps all of
            # it instead of throwing the extra paragraphs away.
            ok = ok and all(rj[k] > rj[k - 1] for k in range(1, len(win)))
        if ok:
            src_text = "\n\n".join(src_flat[ref_of[w][0]] for w in win)
            a_text = "\n\n".join(ours[w] for w in win)
            b_text = "\n\n".join(
                "\n\n".join(ref[ref_of[win[k]][1]:ref_of[win[k + 1]][1]
                                if k + 1 < len(win) else ref_of[win[k]][1] + 1])
                for k in range(len(win)))
            # A reference span that covers far more or far less text than the
            # source it is paired with is not the same passage. Without this
            # the judge sees a 乙 that is three paragraphs of the wrong scene
            # and scores it zero, which says nothing about the translation.
            n_src = sum(len(src_flat[ref_of[w][0]]) for w in win)
            if not (0.55 * base_ref * n_src <= han_len(b_text) <= 1.9 * base_ref * n_src):
                ok = False
        if ok:
            jobs.append((len(jobs), loc[win[0]][0], src_text, a_text, b_text))
            i += a.window_size
        else:
            i += 1
    print(f"aligned windows available: {len(jobs)}")
    if a.dry_run:
        step = max(1, len(jobs) // 6)
        for w, cid, st, at, bt in jobs[::step][:6]:
            print(f"\n-- window {w} ({cid})")
            print("  SRC", st.split("\n")[0][:70])
            print("  OUR", at.split("\n")[0][:70])
            print("  REF", bt.split("\n")[0][:70])
        return
    if len(jobs) > a.windows:
        random.seed(a.seed)
        jobs = sorted(random.sample(jobs, a.windows), key=lambda x: x[0])

    judges = a.judges.split(",")
    recs = []
    with ThreadPoolExecutor(max_workers=len(judges) * 2) as ex:
        futs = []
        for w, cid, src_text, at, bt in jobs:
            for j, m in enumerate(judges):
                ours_is_a = (w + j) % 2 == 0
                futs.append(ex.submit(judge, w, src_text, at if ours_is_a else bt,
                                      bt if ours_is_a else at, m, a.seed, cfg, ours_is_a))
        for f in as_completed(futs):
            recs.append(f.result())
    recs.sort(key=lambda r: (r["idx"], r.get("judge", "")))
    ok = [r for r in recs if "err" not in r]
    print(f"\n{len(ok)}/{len(recs)} judged")
    for dim in DIMS:
        o = [r["ours"][dim] for r in ok if r.get("ours") and dim in r["ours"]]
        z = [r["ref"][dim] for r in ok if r.get("ref") and dim in r["ref"]]
        if o and z:
            print(f"  {dim:6s} ours {sum(o)/len(o):.2f}  ref {sum(z)/len(z):.2f}  "
                  f"Δ {sum(o)/len(o)-sum(z)/len(z):+.2f}")
    win = sum(1 for r in ok if r.get("winner") == "ours")
    loss = sum(1 for r in ok if r.get("winner") == "ref")
    tie = len(ok) - win - loss
    print(f"  win {win} / loss {loss} / tie {tie}")
    if ok:
        print(f"  mean total ours {sum(sum(r['ours'].values()) for r in ok)/len(ok):.2f}  "
              f"ref {sum(sum(r['ref'].values()) for r in ok)/len(ok):.2f}")
    out = a.out or f"E:/Translate/reports_new/{a.book}_eval.json"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"summary": {"win": win, "loss": loss, "tie": tie}, "records": recs},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("report:", out)


if __name__ == "__main__":
    main()
