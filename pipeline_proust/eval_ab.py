"""Blind A/B evaluation: our supplement vs Zhou Kexi's published translation.

The pairing problem: our text and Zhou's text are separate files with different
paragraph segmentation, so "the same paragraph" must be recovered, not assumed.
We align by character-bigram Jaccard, accept only pairs above a floor (real
correspondence) and drop pairs where one side is untranslatable noise (footnotes,
chapter heads).

Why blind: the judge must not know which text is ours. Each pair is shown as 甲/乙
with the assignment randomised per pair and seeded, so a rerun is reproducible but
the judge cannot learn a positional bias. Scores are 5-dimension 1-10 plus a
holistic verdict; we report per-dimension means and win rate.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, "E:/Translate/pipeline")
import llm

REF = "E:/Translate/work_proust/ref_zhou.json"
OURS = "E:/Translate/work_proust/book/book_r3.md"
OUT = "E:/Translate/work_proust/eval6"

DIMS = ["忠实度", "文学性", "中文流畅度", "长句驾驭", "细节与意象"]

SYS = """你是资深法语文学翻译评审，读过普鲁斯特原文，也读过多位中译者。
现在有两份同一段落的中译，分别标为甲、乙（来源未知，评价时不得猜测）。
请只依据文本本身打分，不要因为译文风格不同就认为有错。"""

PROMPT = """【法语原文（供核对忠实度，可以不逐字比对，但漏译/增译要看得出大意）】
{fr}

【甲】
{a}

【乙】
{b}

请从下面五个维度分别给甲、乙各打 1-10 分（10 为最佳），并给出综合判断：
1. 忠实度：是否漏译、增译、误译；普鲁斯特的从句层次是否还在。
2. 文学性：语言是否有文学质地，意象是否准确生动。
3. 中文流畅度：作为中文读起来是否顺，有无翻译腔、生硬欧化句法。
4. 长句驾驭：长句是否撑得住，堆叠是否过载，层次是否可读。
5. 细节与意象：物件、光线、动作、气味等细节是否保留且清晰。

严格按以下 JSON 输出，不要写 JSON 以外的任何内容：
{{"甲":{{"忠实度":0,"文学性":0,"中文流畅度":0,"长句驾驭":0,"细节与意象":0}},
"乙":{{"忠实度":0,"文学性":0,"中文流畅度":0,"长句驾驭":0,"细节与意象":0}},
"胜者":"甲或乙或平","理由":"一句到三句，指出关键差异"}}"""


def bigrams(s: str) -> set[str]:
    s = re.sub(r"\s+", "", s)
    return {s[i:i + 2] for i in range(len(s) - 1)}


def jacc(a: set, b: set) -> float:
    return len(a & b) / max(1, len(a | b))


def load():
    ref = json.load(open(REF, encoding="utf-8"))
    ours_raw = open(OURS, encoding="utf-8").read()
    ours = [p.strip() for p in re.split(r"\n\s*\n", ours_raw) if len(p.strip()) >= 60]
    return ref, ours


def build_pairs(min_j: float = 0.10, lo: int = 120, hi: int = 1600):
    """Greedy one-to-one alignment, best Jaccard first."""
    ref, ours = load()
    cand = []
    ob = [(i, bigrams(o)) for i, o in enumerate(ours)]
    for f, ps in ref.items():
        for k, rp in enumerate(ps):
            if not (lo <= len(rp) <= hi):
                continue
            rb = bigrams(rp)
            if len(rb) < 40:
                continue
            for i, obb in ob:
                j = jacc(rb, obb)
                if j >= min_j:
                    cand.append((j, f, k, i))
    cand.sort(reverse=True)
    used_o, used_r, pairs = set(), set(), []
    for j, f, k, i in cand:
        if i in used_o or (f, k) in used_r:
            continue
        used_o.add(i)
        used_r.add((f, k))
        pairs.append({"j": round(j, 3), "ref": [f, k], "our": i,
                      "zhou": ref[f][k], "ours": ours[i]})
    return pairs


def load_fr():
    """French source is not segmented per paragraph here; return None-safe stub."""
    return None


def judge_one(idx, pair, model, seed=7):
    rnd = random.Random(seed * 1000 + idx)
    ours_is_a = rnd.random() < 0.5
    a = pair["ours"] if ours_is_a else pair["zhou"]
    b = pair["zhou"] if ours_is_a else pair["ours"]
    prompt = PROMPT.format(fr="（略，见译文内容判断）", a=a, b=b)
    t0 = time.time()
    try:
        out, mdl = llm.chat([{"role": "system", "content": SYS},
                             {"role": "user", "content": prompt}],
                            models=[model], max_tokens=1200, temperature=0.2,
                            tag="eval", timeout=200)
    except Exception as e:  # noqa: BLE001
        return {"idx": idx, "err": str(e)[:150]}
    m = re.search(r"\{.*\}", out, re.S)
    if not m:
        return {"idx": idx, "err": "no json", "raw": out[:200]}
    try:
        d = json.loads(m.group(0))
    except Exception:  # noqa: BLE001
        return {"idx": idx, "err": "bad json", "raw": m.group(0)[:200]}
    rec = {"idx": idx, "j": pair["j"], "secs": round(time.time() - t0, 1),
           "ours_is_a": ours_is_a, "judge": mdl,
           "ours": d.get("甲" if ours_is_a else "乙"),
           "zhou": d.get("乙" if ours_is_a else "甲"),
           "winner_raw": d.get("胜者", ""), "why": d.get("理由", "")}
    w = d.get("胜者", "")
    if w in ("甲", "乙"):
        rec["winner"] = "ours" if (w == "甲") == ours_is_a else "zhou"
    else:
        rec["winner"] = "tie"
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=int, default=2)
    ap.add_argument("--min-j", type=float, default=0.10)
    ap.add_argument("--model", default="ox:gemini-3.8-flash")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--dump", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    pairs = build_pairs(a.min_j)
    print(f"aligned {len(pairs)} pairs (j>={a.min_j})")
    # prefer long, well-contextualised pairs
    pairs = [p for p in pairs if 200 <= len(p["zhou"]) <= 1200]
    print(f"usable {len(pairs)}")
    sel = pairs[:a.pairs]
    if a.dump:
        for i, p in enumerate(sel):
            print("=" * 70, i, "j=", p["j"], "our#", p["our"], "ref", p["ref"])
            print("Z:", p["zhou"][:200])
            print("O:", p["ours"][:200])
        json.dump(sel, open(f"{OUT}/pairs.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        return
    recs = []
    with ThreadPoolExecutor(max_workers=len(sel)) as ex:
        futs = [ex.submit(judge_one, i, p, a.model, a.seed) for i, p in enumerate(sel)]
        for f in as_completed(futs):
            recs.append(f.result())
    recs.sort(key=lambda r: r.get("idx", 0))
    json.dump(recs, open(f"{OUT}/result.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    ok = [r for r in recs if "err" not in r]
    if not ok:
        print("all failed:", recs)
        return
    print(f"\n{len(ok)} judged")
    for dim in DIMS:
        o = [r["ours"][dim] for r in ok if r.get("ours")]
        z = [r["zhou"][dim] for r in ok if r.get("zhou")]
        print(f"  {dim:8s} ours {sum(o)/len(o):.2f}  zhou {sum(z)/len(z):.2f}  "
              f"Δ {sum(o)/len(o)-sum(z)/len(z):+.2f}")
    wins = sum(1 for r in ok if r["winner"] == "ours")
    loss = sum(1 for r in ok if r["winner"] == "zhou")
    tie = len(ok) - wins - loss
    print(f"  win {wins} / loss {loss} / tie {tie}")
    print(f"  mean total: ours "
          f"{sum(sum(r['ours'].values()) for r in ok)/len(ok):.2f}  "
          f"zhou {sum(sum(r['zhou'].values()) for r in ok)/len(ok):.2f}")
    for r in ok:
        print(f"\n[{r['idx']}] j={r['j']} winner={r['winner']}  {r['why']}")


if __name__ == "__main__":
    main()
