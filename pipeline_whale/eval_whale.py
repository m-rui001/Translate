"""Blind A/B evaluation of our Moby-Dick against the published Chinese edition.

Design (same discipline as the LOTR eval, adapted to this book):

- Windows of consecutive *narrative* paragraphs are compared, never whole chapters.
  Moby-Dick mixes narrative, verse, sermons, stage directions and encyclopaedia
  entries; comparing a hymn against a hymn is meaningless, so only prose paragraphs
  that exist in both versions are used.
- Windows are anchored on source paragraph indices, then mapped into each version's
  own paragraph list with a per-chapter offset search (Chinese is uniformly shorter
  than English, so a constant length ratio is a reliable alignment signal).
- Each judge sees the English source plus two anonymous Chinese versions (甲/乙) in a
  per-judge randomised order. Judges come from different model families.
- Proper-name differences are not scored: the prompt says so explicitly, because the
  two译本 legitimately render 塔希蒂格 / 塔斯蒂哥 differently.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import llm

SRC = "E:/Translate/work_whale/src"
REF = "E:/Translate/work_whale/ref_zh"
OUT = "E:/Translate/work_whale/out"
REPORTS = "E:/Translate/reports_whale"
SEP = re.compile(r"\n\s*\n")
CJK = re.compile(r"[\u4e00-\u9fff]")

JUDGE_PROMPT = """你是资深文学翻译评委，中英文俱精。下面是《白鲸》(Moby-Dick) 的一段英文原文，
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
2. 人名、船名、地名的译法差异（例如 塔希蒂格/塔斯蒂哥、莫比—迪克/莫比·迪克）
   属于流派不同，不计入扣分。
3. 麦尔维尔的文体是十九世纪美国散文的顶点：长句盘旋、破折号频繁、圣经腔与
   莎士比亚腔交错、时有反讽与戏仿。请据此判断，不要用现代白话小说的平滑标准
   去奖励“读起来顺”的译本。

按四个维度各打 0-10 分：

- 忠实：是否准确传达原文的信息、细节、因果、语气，有无漏译、误译、增译。
- 文学性：汉语是否有文学质地，节奏、意象、句法是否有分量。
- 中文自然度：是否像中文作品，有无翻译腔。
- 腔调：叙述者的沉思、亚哈的狂怒、水手的粗野、讲道的经文腔是否各得其声。

最后给出总体判断。

严格按下面的格式输出，不要写别的：

甲 忠实: <分数>
甲 文学性: <分数>
甲 自然度: <分数>
甲 腔调: <分数>
乙 忠实: <分数>
乙 文学性: <分数>
乙 自然度: <分数>
乙 腔调: <分数>
胜出: 甲/乙/相当
理由: <两三句话>
"""


def parse_verdict(text: str) -> dict:
    def sc(label, dim):
        m = re.search(label + r"\s*" + dim + r"\s*[:：]\s*([0-9]+(?:\.[0-9])?)", text)
        return float(m.group(1)) if m else None

    out = {}
    for lab in ("甲", "乙"):
        for dim in ("忠实", "文学性", "自然度", "腔调"):
            out[f"{lab}_{dim}"] = sc(lab, dim)
    m = re.search(r"胜出\s*[:：]\s*(甲|乙|相当)", text)
    out["winner"] = m.group(1) if m else None
    m = re.search(r"理由\s*[:：]\s*(.+)", text, re.S)
    out["reason"] = (m.group(1).strip()[:400] if m else "")
    return out


def load_src(cid):
    d = json.load(open(os.path.join(SRC, cid + ".json"), encoding="utf-8"))
    return [b["text"].strip() for b in d["blocks"] if b["type"] == "p"]


def load_ours(cid):
    """Our prose paragraphs, in source order, using the chunk block structure."""
    chdir = os.path.join(OUT, cid)
    spec = os.path.join(chdir, "blocks.json")
    if os.path.exists(spec):
        blocks = json.load(open(spec, encoding="utf-8"))
    else:
        blocks = None
    md = os.path.join(chdir, "chapter.md")
    if not os.path.exists(md):
        return []
    text = open(md, encoding="utf-8").read().replace("\r\n", "\n")
    parts = [p.strip() for p in SEP.split(text) if p.strip()]
    if blocks and len(parts) == len(blocks):
        return [p for p, b in zip(parts, blocks) if b["type"] == "p" and CJK.search(p)]
    # fallback: treat every non-empty block as a paragraph
    return [p for p in parts if CJK.search(p) and len(p) >= 30]


def load_ref(cid):
    p = os.path.join(REF, cid + ".json")
    if not os.path.exists(p):
        return []
    d = json.load(open(p, encoding="utf-8"))
    out = []
    for t in d["paras"]:
        t = (t or "").strip()
        if t and CJK.search(t) and len(t) >= 30:
            out.append(t)
    return out


def find_offset(zh, en) -> tuple[int, float]:
    """Best (offset, quality) mapping zh[i+off] ~ en[i], judged by length ratio spread."""
    if not zh or not en:
        return 0, 0.0
    best_off, best_q = 0, -1.0
    for off in range(-8, 9):
        n = min(len(en), len(zh) - off)
        if n < 10:
            continue
        idx = list(range(0, n, max(1, n // 25)))
        ratios = []
        for i in idx:
            e = len(en[i])
            z = len(zh[i + off])
            if e > 20 and z > 10:
                ratios.append(z / e)
        if len(ratios) < 6:
            continue
        med = statistics.median(ratios)
        if med <= 0:
            continue
        dev = statistics.median([abs(r - med) / med for r in ratios])
        q = 1.0 / (1.0 + dev)
        if q > best_q:
            best_off, best_q = off, q
    return best_off, best_q


def run(cid, judges, windows, window_size, seed, min_quality=0.72):
    src, ours, ref = load_src(cid), load_ours(cid), load_ref(cid)
    rec = {"chapter": cid, "src": len(src), "ours": len(ours), "ref": len(ref),
           "samples": [], "skipped": None}
    if len(src) < window_size + 2 or len(ours) < window_size or len(ref) < window_size:
        rec["skipped"] = "too short"
        print(f"[{cid}] skip (src={len(src)} ours={len(ours)} ref={len(ref)})")
        return rec
    off_ours, q_ours = find_offset(ours, src)
    off_ref, q_ref = find_offset(ref, src)
    rec.update({"off_ours": off_ours, "q_ours": round(q_ours, 2),
                "off_ref": off_ref, "q_ref": round(q_ref, 2)})
    if q_ours < min_quality or q_ref < min_quality:
        rec["skipped"] = "alignment"
        print(f"[{cid}] skip: alignment weak (ours q={q_ours:.2f} off={off_ours}, "
              f"ref q={q_ref:.2f} off={off_ref})")
        return rec
    print(f"[{cid}] src={len(src)} ours={len(ours)}(off {off_ours}, q={q_ours:.2f}) "
          f"ref={len(ref)}(off {off_ref}, q={q_ref:.2f})")

    n = min(len(src), len(ours) - off_ours, len(ref) - off_ref)
    picks, step = [], max(1, (n - window_size) // max(1, windows))
    for w in range(windows):
        start = min(max(0, 2 + w * step), max(0, n - window_size))
        picks.append(start)

    for si, start in enumerate(picks):
        e = start + window_size
        a_p = ours[start + off_ours:e + off_ours]
        b_p = ref[start + off_ref:e + off_ref]
        if len(a_p) < window_size - 1 or len(b_p) < window_size - 1:
            continue
        source = "\n\n".join(src[start:e])
        sample = {"chapter": cid, "window": si, "start": start,
                  "source": source, "ours": "\n\n".join(a_p),
                  "ref": "\n\n".join(b_p), "judgements": []}
        for judge in judges:
            if llm.benched(judge):
                continue
            flip = random.Random(f"{seed}{cid}{si}{judge}").random() < 0.5
            a_text = sample["ref"] if flip else sample["ours"]
            b_text = sample["ours"] if flip else sample["ref"]
            prompt = JUDGE_PROMPT.format(source=source[:7000], a=a_text[:4500], b=b_text[:4500])
            try:
                out, used = llm.chat([{"role": "user", "content": prompt}], judge,
                                     max_tokens=4000, temperature=0.2,
                                     tag=f"judge:{cid}:{si}", retries=2, timeout=300)
            except Exception as ex:  # noqa: BLE001
                print(f"  judge {judge} failed: {str(ex)[:90]}")
                continue
            v = parse_verdict(out)
            v["judge"] = judge
            v["flipped"] = flip
            w = v["winner"]
            v["winner_true"] = ("tie" if w == "相当" else
                                None if w is None else
                                ("ref" if (w == "甲") == flip else "ours"))
            for dim in ("忠实", "文学性", "自然度", "腔调"):
                for lab, key in (("甲", "ref" if flip else "ours"),
                                 ("乙", "ours" if flip else "ref")):
                    v[f"{key}_{dim}"] = v.pop(f"{lab}_{dim}", None)
            sample["judgements"].append(v)
        rec["samples"].append(sample)
        print(f"[{cid}] window {si + 1} judged by {len(sample['judgements'])}")
    return rec


def summarize(records):
    dims = ("忠实", "文学性", "自然度", "腔调")
    ours = {d: [] for d in dims}
    ref = {d: [] for d in dims}
    wins = {"ours": 0, "ref": 0, "tie": 0}
    per_judge = {}
    for r in records:
        for s in r["samples"]:
            for v in s["judgements"]:
                for d in dims:
                    if v.get(f"ours_{d}") is not None:
                        ours[d].append(v[f"ours_{d}"])
                    if v.get(f"ref_{d}") is not None:
                        ref[d].append(v[f"ref_{d}"])
                if v.get("winner_true"):
                    wins[v["winner_true"]] += 1
                    pj = per_judge.setdefault(v["judge"], {"ours": 0, "ref": 0, "tie": 0})
                    pj[v["winner_true"]] += 1
    n_dec = wins["ours"] + wins["ref"] + wins["tie"]
    return {
        "verdicts": wins,
        "ours_win_rate": round(wins["ours"] / n_dec, 3) if n_dec else None,
        "mean_scores": {d: {"ours": round(statistics.mean(ours[d]), 2) if ours[d] else None,
                            "ref": round(statistics.mean(ref[d]), 2) if ref[d] else None,
                            "n": len(ours[d])} for d in dims},
        "by_judge": per_judge,
        "chapters_evaluated": [r["chapter"] for r in records if r["samples"]],
        "chapters_skipped": {r["chapter"]: r["skipped"] for r in records if r.get("skipped")},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", default="auto")
    ap.add_argument("--judges", default="ox:gemini-3.8-flash,xm:mimo-v2.6-flash,oxd:deepseek-v4.1-flash"
                                        "xm:mimo-v2.6-flash")
    ap.add_argument("--windows", type=int, default=2)
    ap.add_argument("--window-size", type=int, default=8)
    ap.add_argument("--seed", default="whale")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(REPORTS, exist_ok=True)

    if a.chapters == "auto":
        ids = sorted(os.path.basename(os.path.dirname(p))
                     for p in glob.glob(os.path.join(OUT, "*", "chapter.md")))
    else:
        ids = a.chapters.split(",")
    judges = a.judges.split(",")
    records = [run(cid, judges, a.windows, a.window_size, a.seed) for cid in ids]
    summary = summarize(records)
    tag = a.out or ("eval_" + "-".join(ids)[:60])
    path = os.path.join(REPORTS, re.sub(r"[^A-Za-z0-9_.-]", "_", tag) + ".json")
    json.dump({"summary": summary, "records": records},
              open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n== SUMMARY ==")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("report:", path)


if __name__ == "__main__":
    main()
