"""Terminology control: canonical forms, variant mining, and per-batch guarding.

Two jobs:

1. *Feed* the polish model the canonical rendering of every name that actually
   occurs in the paragraph it is editing, so it cannot drift.

2. *Guard* the result. If a canonical name was in the draft and comes back in a
   different form, the batch is rejected. Separately, a global miner compares
   same-length, same-first-character CJK strings that differ by one character
   and reports the minority form — that is exactly how 夏尔吕/夏吕斯 and
   圣厄韦尔特/圣厄弗特 get caught without a dictionary.

The miner is deliberately conservative about *applying*: 3+ characters only,
majority form wins, and the loser must not be a substring of the winner.
Two-character cases go to a report for a human to settle.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = "E:/Translate"
REPORT = os.path.join(ROOT, "reports")

# Split transliterated names at Chinese function characters. A naive CJK-run
# scan glues a name to the next word (米那斯提力斯的 / 塞特姆布里尼说) and buries
# the real variants under tens of thousands of false pairs.
STOP = set("的了是在和与也就都而及或其之这那有不没很更最又还只把被从对向为于如但所")
STOP |= set("以然才刚曾会能可要得着过们个些种样时里外中后前后见说答喊问想道来去")
STOP |= set("上下大小多少全半再便却并给让使即则仍尚太稍甚颇也许大概一己")
CJK_RUN = re.compile(r"[\u4e00-\u9fff]{2,}")

# characters that overwhelmingly appear in transliterated names
TRANS = set(
    "阿埃艾爱安昂奥巴拜班邦保鲍贝本比毕彼宾波伯勃博布查达戴丹道德登迪蒂丁东杜敦多"
    "厄恩尔法凡菲费芬佛弗福伏符盖甘冈高戈格根古瓜圭果哈海罕豪赫亨胡华霍基吉加贾杰"
    "捷金卡凯坎康考柯科克肯孔库夸奎拉莱赖兰朗劳勒雷黎里利连列林隆卢鲁路伦罗洛马玛"
    "迈麦曼芒梅门蒙米明莫姆穆纳奈南内尼涅宁纽努诺欧帕潘庞培佩彭皮平珀普齐奇乔切琴"
    "丘萨塞森沙尚舍施什史舒斯松苏索塔泰坦汤唐陶特提田廷图托瓦万旺威韦维温文沃乌武"
    "西希锡夏谢辛休徐雅亚扬耶叶伊因英尤于约泽扎詹兹佐佐")


# ────────────────────────────────────────────────────────── canned glossaries
def _load_file_glossary(path: str) -> dict[str, str]:
    if not os.path.exists(path):
        return {}
    d = json.load(open(path, encoding="utf-8"))
    out = {}
    for k, v in d.items():
        if k.startswith("_"):
            continue
        if isinstance(v, str):
            out[k] = v
        elif isinstance(v, dict) and v.get("zh"):
            out[k] = v["zh"]
    return out


def _load_module_glossary(path: str, attr="G") -> dict[str, str]:
    if not os.path.exists(path):
        return {}
    spec = importlib.util.spec_from_file_location(
        "g_" + os.path.basename(path).replace(".py", ""), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    g = getattr(m, attr, {}) or {}
    return {k: v for k, v in g.items() if isinstance(v, str)}


# Hand-settled on top of the model judge. Each entry is (wrong, right) and is
# applied before and after polishing, in addition to the model's own rules.
#   zauberberg 克莱费尔特/克莱费尔德 are the same patient (Hermine Kleefeld);
#   克莱费尔德 is the majority form.
OVERRIDES = {
    "zauberberg": [("克莱费尔特", "克莱费尔德")],
    "lotr": [],
    "whale": [],
    "soledad": [],
    "proust": [],
    "camus": [],
    "chekhov": [],
}


def termbase(book: str) -> dict[str, str]:
    """EN -> ZH (or ZH -> ZH when the source is not English)."""
    if book == "lotr":
        return _load_module_glossary(f"{ROOT}/pipeline/glossary.py")
    if book == "whale":
        return _load_module_glossary(f"{ROOT}/pipeline_whale/glossary.py")
    if book == "soledad":
        return _load_file_glossary(f"{ROOT}/work_soledad/glossary.json")
    if book == "zauberberg":
        return _load_file_glossary(f"{ROOT}/work_zauberberg/glossary.json")
    if book == "proust":
        g = _load_module_glossary(f"{ROOT}/pipeline_proust/glossary_proust.py", "ALL")
        if g:
            return g
        a = _load_module_glossary(f"{ROOT}/pipeline_proust/glossary_proust.py", "_ZHOU")
        b = _load_module_glossary(f"{ROOT}/pipeline_proust/glossary_proust.py", "_REST")
        return {**b, **a}
    if book == "camus":
        return _load_file_glossary(f"{ROOT}/work_camus/glossary.json")
    if book == "chekhov":
        return _load_file_glossary(f"{ROOT}/work_chekhov/glossary.json")
    return {}


# ────────────────────────────────────────────────────────── variant mining
def name_like(s: str) -> bool:
    return sum(1 for c in s if c in TRANS) >= max(1, int(len(s) * 0.6))


def name_tokens(text: str, min_len=3, max_len=8):
    """Maximal transliteration-looking runs, split at function characters."""
    for run in CJK_RUN.findall(text):
        cur = ""
        for ch in run:
            if ch in STOP:
                if min_len <= len(cur) <= max_len:
                    yield cur
                cur = ""
            else:
                cur += ch
        if min_len <= len(cur) <= max_len:
            yield cur


def mine_ngrams(texts: list[str], min_len=3, max_len=8):
    cnt: Counter = Counter()
    for t in texts:
        for tok in name_tokens(t, min_len, max_len):
            if name_like(tok):
                cnt[tok] += 1
    return cnt


def near_variants(cnt: Counter, min_count=2):
    """Pairs (major, minor) of equal length differing in exactly one position.

    The differing character must be a transliteration syllable on both sides.
    Otherwise every name glued to a verb produces a false pair
    (卡斯托普看 / 卡斯托普尽), which is how the manual list filled with junk.
    """
    by = defaultdict(list)
    for g, c in cnt.items():
        if c >= min_count:
            by[(len(g), g[:2])].append(g)
    out = []
    for key, gs in by.items():
        for i in range(len(gs)):
            a = gs[i]
            ca = cnt[a]
            for j in range(i + 1, len(gs)):
                b = gs[j]
                diff = [k for k in range(len(a)) if a[k] != b[k]]
                if len(diff) != 1:
                    continue
                k = diff[0]
                if not (a[k] in TRANS and b[k] in TRANS):
                    continue
                if a[k] in STOP or b[k] in STOP:
                    continue
                major, minor = (a, b) if ca >= cnt[b] else (b, a)
                out.append((major, minor, cnt[major], cnt[minor]))
    out.sort(key=lambda r: (r[3], -r[2]))
    return out


def guard_terms(zh: str, tb: dict[str, str]) -> list[str]:
    """Canonical ZH names that occur in this paragraph."""
    hits = []
    for en, zhn in tb.items():
        if zhn and zhn in zh:
            hits.append(zhn)
    return sorted(set(hits), key=len, reverse=True)[:14]


def term_prompt(hits: list[str], tb_inv: dict[str, list[str]]) -> str:
    if not hits:
        return ""
    lines = []
    for h in hits:
        srcs = tb_inv.get(h) or []
        lines.append(f"「{h}」" + (f"（{'/'.join(srcs[:3])}）" if srcs else ""))
    return ("本段涉及以下专名，必须原样使用，不得换用别的译法：" + "、".join(lines))


def check_terms(before: str, after: str, hits: list[str]) -> str | None:
    lost = [h for h in hits if h in before and h not in after]
    if lost:
        return "term dropped: " + "/".join(lost)
    return None


def invert(tb: dict[str, str]) -> dict[str, list[str]]:
    inv: dict[str, list[str]] = defaultdict(list)
    for en, zh in tb.items():
        if zh:
            inv[zh].append(en)
    return inv


# ────────────────────────────────────────────────────────── report / apply
def audit_book(book: str, texts: list[str], tb: dict[str, str] | None = None) -> dict:
    """Find minority name variants across one book's Chinese text."""
    tb = tb if tb is not None else termbase(book)
    canon = set(v for v in tb.values() if v and 2 <= len(v) <= 8)
    cnt = mine_ngrams(texts)
    pairs = near_variants(cnt, min_count=2)
    auto, manual = [], []
    for major, minor, cmaj, cmin in pairs:
        if major in canon and minor not in canon:
            (auto if len(major) >= 3 else manual).append(
                {"major": major, "minor": minor, "n_major": cmaj, "n_minor": cmin})
        elif minor in canon and major not in canon:
            manual.append({"major": minor, "minor": major,
                           "n_major": cmin, "n_minor": cmaj})
        elif major in canon and minor in canon:
            continue
        else:
            manual.append({"major": major, "minor": minor,
                           "n_major": cmaj, "n_minor": cmin})
    return {"book": book, "auto": auto, "manual": manual,
            "n_auto": len(auto), "n_manual": len(manual)}


def all_rules(book: str) -> list[dict]:
    """Judged rules + hand overrides, as {minor, major} dicts."""
    rules = []
    p = os.path.join(REPORT, f"term_rules_{book}.json")
    if os.path.exists(p):
        for r in json.load(open(p, encoding="utf-8")).get("rules") or []:
            rules.append({"minor": r["minor"], "major": r["major"]})
    for wrong, right in OVERRIDES.get(book, []):
        rules.append({"minor": wrong, "major": right})
    uniq = {}
    for r in rules:
        uniq[r["minor"]] = r
    # longest minor first so 库尔瓦西埃家 is fixed before 库尔瓦西埃
    return sorted(uniq.values(), key=lambda r: -len(r["minor"]))


def apply_variants(texts: list[str], rules: list[dict]) -> tuple[list[str], int]:
    rules = sorted(rules, key=lambda r: -len(r["minor"]))
    n = 0
    for i, t in enumerate(texts):
        for r in rules:
            if r["minor"] in t:
                n += t.count(r["minor"])
                t = t.replace(r["minor"], r["major"])
        texts[i] = t
    return texts, n
