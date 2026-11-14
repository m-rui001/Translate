"""Blind A/B evaluation: our translation vs the published Chinese edition.

Design
- Windows of consecutive narrative paragraphs are compared, never whole chapters.
- Each judge sees the English source plus two anonymous Chinese versions
  ("甲"/"乙"), in a per-judge randomised order, and scores four dimensions plus
  an overall preference. We keep the mapping and aggregate win rates.
- Three judges from different model families reduce single-model bias.
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

import llm

REF = "E:/Translate/work/ref_zh"
OUT = "E:/Translate/work/out"
SRC = "E:/Translate/work/src"
REPORTS = "E:/Translate/reports"

CH2REF = {
    "prologue": "front003",
    "book1c01": "chapter001", "book1c02": "chapter002", "book1c03": "chapter003",
    "book1c04": "chapter004", "book1c05": "chapter005", "book1c06": "chapter006",
    "book1c07": "chapter007", "book1c08": "chapter008", "book1c09": "chapter009",
    "book1c10": "chapter010", "book1c11": "chapter011", "book1c12": "chapter012",
    "book2c01": "chapter013", "book2c02": "chapter014", "book2c03": "chapter015",
    "book2c04": "chapter016", "book2c05": "chapter017", "book2c06": "chapter018",
    "book2c07": "chapter019", "book2c08": "chapter020", "book2c09": "chapter021",
    "book2c10": "chapter022",
    "book3c01": "chapter024", "book3c02": "chapter025", "book3c03": "chapter026",
    "book3c04": "chapter027", "book3c05": "chapter028", "book3c06": "chapter029",
    "book3c07": "chapter030", "book3c08": "chapter031", "book3c09": "chapter032",
    "book3c10": "chapter033", "book3c11": "chapter034",
    "book4c01": "chapter035", "book4c02": "chapter036", "book4c03": "chapter037",
    "book4c04": "chapter038", "book4c05": "chapter039", "book4c06": "chapter040",
    "book4c07": "chapter041", "book4c08": "chapter042", "book4c09": "chapter043",
    "book4c10": "chapter044",
    "book5c01": "chapter046", "book5c02": "chapter047", "book5c03": "chapter048",
    "book5c04": "chapter049", "book5c05": "chapter050", "book5c06": "chapter051",
    "book5c07": "chapter052", "book5c08": "chapter053", "book5c09": "chapter054",
    "book5c10": "chapter055",
    "book6c01": "chapter056", "book6c02": "chapter057", "book6c03": "chapter058",
    "book6c04": "chapter059", "book6c05": "chapter060", "book6c06": "chapter061",
    "book6c07": "chapter062", "book6c08": "chapter063", "book6c09": "chapter064",
}

CJK = re.compile(r"[\u4e00-\u9fff]")


def narrative(paras: list[str], min_len: int = 30) -> list[str]:
    out = []
    for p in paras:
        p = p.strip()
        if not p or not CJK.search(p):
            continue
        if len(p) < min_len:
            continue
        out.append(p)
    return out


def load_ours(cid: str):
    p = os.path.join(OUT, cid, "chapter.md")
    if not os.path.exists(p):
        return []
    text = open(p, encoding="utf-8").read().replace(chr(13) + chr(10), chr(10))
    text = re.sub(r"<\s*/?\s*verse\s*>", "", text)
    paras = [l.strip().lstrip("#").strip() for l in text.split(chr(10))]
    paras = [x for x in paras if x]
    return narrative(paras)


def load_ref(cid: str):
    f = CH2REF.get(cid)
    if not f:
        return []
    p = os.path.join(REF, f + ".json")
    if not os.path.exists(p):
        return []
    d = json.load(open(p, encoding="utf-8"))
    blocks = d["blocks"]
    paras = []
    for b in blocks:
        if b["tag"].startswith("h"):
            continue
        t = b["text"]
        if re.fullmatch(r"[A-Za-z0-9 ,.'\-–—!?;:()]+", t or ""):
            continue
        paras.append(t)
    return narrative(paras)


def load_source(cid: str):
    d = json.load(open(os.path.join(SRC, cid + ".json"), encoding="utf-8"))
    paras = []
    for b in d["blocks"]:
        if b["type"] == "p":
            paras.append(b["text"].strip())
        else:
            paras.append("[诗] " + " / ".join(l.strip() for l in b["lines"]))
    return paras


def align(ours: list[str], ref: list[str]):
    """Index alignment with a small offset search; returns (offset, ok)."""
    if not ours or not ref:
        return 0, False
    best, best_score = 0, -1
    for off in range(-6, 7):
        n = min(len(ours), len(ref) - off)
        if n < 8:
            continue
        ratios = [len(ours[i]) / max(1, len(ref[i + off])) for i in range(0, n, 3)]
        med = statistics.median(ratios)
        if med <= 0:
            continue
        dev = sum(abs(r - med) for r in ratios) / len(ratios)
        score = 1.0 / (1.0 + dev / max(med, 1e-6))
        if score > best_score:
            best, best_score = off, score
    coverage = min(len(ours), len(ref) - best) / max(len(ours), len(ref) - best)
    return best, coverage > 0.85 and best_score > 0.5


JUDGE_PROMPT = """你是资深文学翻译评委。下面给出《魔戒》的一段英文原文，以及两份中文译文（甲、乙），来自不同译本。

<source>
{source}
</source>

（注：两份译文覆盖的原文范围可能略有出入，请只就比较范围内彼此对应的段落评判，不要把范围差异算作答译或漏译。）

<甲>
{a}
</甲>

<乙>
{b}
</乙>

请只依据文本本身评判，不要猜测译者或版本。按四个维度各打 0-10 分：

- 忠实：是否准确传达原文的信息、细节、因果与语气，有无漏译、误译、增译。
- 文学性：汉语是否有文学质地，节奏、意象、用词是否出色。
- 中文自然度：是否像中文原作，有无翻译腔。
- 腔调：叙述者与人物的语气是否贴切。

最后给出总体判断：哪一份更好，以及理由（两三句话）。

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


def parse_verdict(text: str):
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
    out["reason"] = (m.group(1).strip()[:300] if m else "")
    return out


def source_paras(cid):
    """Narrative source paragraphs, in order (verse and one-liners dropped)."""
    src = load_source(cid)
    return [p for p in src if not p.startswith("[诗]") and len(p.split()) > 8]


def run(cid, judges, windows, window_size, seed):
    ours, ref = load_ours(cid), load_ref(cid)
    srcn = source_paras(cid)
    off, ok = align(ours, ref)
    rec = {"chapter": cid, "ours": len(ours), "ref": len(ref), "offset": off, "aligned": ok,
           "samples": []}
    print(f"[{cid}] ours={len(ours)} ref={len(ref)} src={len(srcn)} off={off} aligned={ok}")
    if not ok:
        print(f"[{cid}] alignment failed (ours={len(ours)} ref={len(ref)} off={off})")
        return rec

    n = min(len(ours), len(ref) - off)
    picks = []
    step = max(1, n // (windows + 1))
    for w in range(windows):
        start = min(n - window_size, 5 + w * step)
        start = max(0, start)
        picks.append(start)

    for si, start in enumerate(picks):
        a_paras = ours[start:start + window_size]
        b_paras = ref[start + off:start + off + window_size]
        # source window: same paragraph indices (translations preserve paragraphs)
        s_start = int(start / max(1, len(ours)) * len(srcn))
        source = "\n\n".join(srcn[s_start:s_start + window_size])
        sample = {"chapter": cid, "window": si, "start": start,
                  "source": source, "ours": "\n\n".join(a_paras),
                  "ref": "\n\n".join(b_paras), "judgements": []}

        for judge in judges:
            flip = random.Random(f"{seed}{cid}{si}{judge}").random() < 0.5
            a_text, b_text = (sample["ref"], sample["ours"]) if flip else (sample["ours"], sample["ref"])
            prompt = JUDGE_PROMPT.format(source=source[:6000], a=a_text[:4000], b=b_text[:4000])
            try:
                out, used = llm.chat([{"role": "user", "content": prompt}], models=[judge],
                                     max_tokens=900, temperature=0.2, tag=f"judge:{cid}:{si}",
                                     retries=3, timeout=360)
            except Exception as e:  # noqa: BLE001
                print(f"  judge {judge} failed: {str(e)[:80]}")
                continue
            v = parse_verdict(out)
            v["judge"] = judge
            v["flipped"] = flip
            # map back to "ours"/"ref"
            if v["winner"] == "相当":
                v["winner_true"] = "tie"
            elif v["winner"] == "甲":
                v["winner_true"] = "ref" if flip else "ours"
            elif v["winner"] == "乙":
                v["winner_true"] = "ours" if flip else "ref"
            else:
                v["winner_true"] = None
            for dim in ("忠实", "文学性", "自然度", "腔调"):
                for lab, key in (("甲", "ref" if flip else "ours"), ("乙", "ours" if flip else "ref")):
                    v[f"{key}_{dim}"] = v.pop(f"{lab}_{dim}", None)
            sample["judgements"].append(v)
        rec["samples"].append(sample)
        print(f"[{cid}] window {si+1}/{windows} judged by {len(sample['judgements'])}")
    return rec


def summarize(records):
    dims = ("忠实", "文学性", "自然度", "腔调")
    ours, ref = {d: [] for d in dims}, {d: [] for d in dims}
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
                if v.get("winner_true"):
                    pj[v["winner_true"]] += 1
    summary = {
        "verdicts": wins,
        "mean_scores": {d: {"ours": round(statistics.mean(ours[d]), 2) if ours[d] else None,
                            "ref": round(statistics.mean(ref[d]), 2) if ref[d] else None,
                            "n_ours": len(ours[d]), "n_ref": len(ref[d])} for d in dims},
        "by_judge": per_judge,
        "chapters_evaluated": [r["chapter"] for r in records if r["samples"]],
    }
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", default="auto", help="comma ids or auto (all translated)")
    ap.add_argument("--judges", default="ox:gemini-3.8-flash,ox:gpt-6.1-sol,ms-qwen3.5-27b")
    ap.add_argument("--windows", type=int, default=2)
    ap.add_argument("--window-size", type=int, default=10)
    ap.add_argument("--seed", default="lotr")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(REPORTS, exist_ok=True)
    if a.chapters == "auto":
        ids = [os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(OUT, "*", "chapter.md"))]
    else:
        ids = a.chapters.split(",")
    ids = [i for i in ids if i in CH2REF]
    judges = a.judges.split(",")

    records = []
    for cid in sorted(ids):
        records.append(run(cid, judges, a.windows, a.window_size, a.seed))
    summary = summarize(records)
    tag = a.out or ("eval_" + "-".join(sorted(ids))[:40].replace(",", "_"))
    path = os.path.join(REPORTS, re.sub(r"[^A-Za-z0-9_.-]", "_", tag) + ".json")
    json.dump({"summary": summary, "records": records}, open(path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\n== SUMMARY ==")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("report:", path)


if __name__ == "__main__":
    main()
