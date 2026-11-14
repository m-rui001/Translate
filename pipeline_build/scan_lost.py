"""Find chapters that are not actually translations.

`clean_check.py` asks "is this Chinese". This asks a blunter question: "did the writer
translate at all". Three signatures, none of which need the source text or a model:

1. **Refusal.** The model answered the prompt instead of doing the job -- "I cannot
   translate this", "please send the original", "this is not the body text".
2. **Placeholder.** The reply is `题段段段段段段` or `待译` or a run of one repeated
   character. Something upstream meant to fill this in later and never did.
3. **Collapse.** The Chinese is a small fraction of the source length. A chapter that
   should be 3,000 characters arriving as 200 is not a terse translation.

The distinction that matters is *whole chapter gone* versus *paragraphs legally merged*.
`zh_cjk / src_chars` cannot tell them apart on its own -- merging four paragraphs into one
lowers the paragraph count without lowering the character count. So the collapse test
compares against the **book's own median ratio**, not an absolute floor: a book whose
normal ratio is 0.45 flags a chapter at 0.12, while a terse book whose normal ratio is
0.30 does not flag a chapter at 0.25.

Scans both shapes of body text on this shelf, because the three assembly lines read from
different places:

* `work_*/**/*.json`  -- `src_paras` + `zh`/`texts` (overhaul books, Proust, pub)
* `work_*/**/final.txt` -- bare paragraphs, one per blank-line-separated block
  (`build_gutenberg.py` and `build_pub.py` read these, and until now nothing checked them:
  6,589 files were going unexamined)
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CJK = re.compile(r"[\u4e00-\u9fff]")

REFUSAL = [
    # "我不能为此流亡出去" is ordinary narrative; a refusal addresses the user.
    re.compile(r"我(?:无法|不能|没法)为(?:您|你|用户)"),
    re.compile(r"请(?:您)?(?:把|提供|发来).{0,20}(?:原文|英文|段落)"),
    re.compile(r"(?:并非|不是).{0,12}正文"),
    re.compile(r"我(?:无法|不能)(?:翻译|处理|继续)"),
    re.compile(r"作为(?:一个)?(?:AI|人工智能|语言模型)"),
    re.compile(r"不符(?:合|于).{0,10}(?:要求|准则|格式)"),
]

PLACEHOLDER = re.compile(r"^(.)\1{5,}$|^(?:题段|待译|TODO|占位)")

# A chapter is "lost" when its Chinese is this much shorter than the book's own norm.
LOST_FRACTION = 0.60

# Below this many source characters the ratio is too noisy to judge.
MIN_SRC_CHARS = 400

SKIP = ("_backup", "_pre_writeback", "_backup_polish3", ".polished.json",
        "_bak", "_out_bak", "_pre_")


def paras_of_text(raw: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n{2,}", raw) if p.strip()]


def load(path: str):
    """Return (paragraphs, src_chars) or None when the file is not body text."""
    if path.endswith(".json"):
        try:
            d = json.load(open(path, encoding="utf-8"))
        except Exception:
            return None
        if not isinstance(d, dict):
            return None
        zh = d.get("zh") or d.get("texts")
        if not isinstance(zh, list) or not zh:
            return None
        zh = [x for x in zh if isinstance(x, str)]
        if not zh:
            return None
        src = d.get("src_paras")
        src_chars = (sum(len(s) for s in src if isinstance(s, str))
                     if isinstance(src, list) else 0)
        return zh, src_chars
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    ps = paras_of_text(raw)
    if not ps:
        return None
    return ps, 0


def check(path: str):
    """Return (problems, ratio, n_paras, zh_cjk) or None when not body text."""
    loaded = load(path)
    if loaded is None:
        return None
    zh, src_chars = loaded
    out: list[str] = []

    for i, t in enumerate(zh):
        for pat in REFUSAL:
            if pat.search(t):
                out.append(f"[{i}] REFUSAL {t[:80]!r}")
                break
        if PLACEHOLDER.match(t.strip()):
            out.append(f"[{i}] PLACEHOLDER {t[:40]!r}")

    zh_cjk = sum(len(CJK.findall(t)) for t in zh)
    ratio = (zh_cjk / src_chars) if src_chars >= MIN_SRC_CHARS else 0.0
    return out, ratio, len(zh), zh_cjk, src_chars


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")

    files = []
    for pat in ("work_*/**/*.json", "work_*/**/final.txt"):
        for f in glob.glob(os.path.join(ROOT, pat), recursive=True):
            if any(s in f for s in SKIP):
                continue
            files.append(f)
    files.sort()

    results = []
    for f in files:
        r = check(f)
        if r is not None:
            results.append((f, r))

    # per-directory median ratio, so a book is judged against itself
    by_dir: dict[str, list[float]] = {}
    for f, (_, ratio, _n, _z, _sc) in results:
        if ratio > 0:
            by_dir.setdefault(os.path.dirname(f), []).append(ratio)
    median = {}
    for k, v in by_dir.items():
        v = sorted(v)
        median[k] = v[len(v) // 2]

    bad = 0
    total = 0
    for f, (probs, ratio, n, zc, sc) in results:
        probs = list(probs)
        med = median.get(os.path.dirname(f))
        if med and ratio > 0 and ratio < med * LOST_FRACTION:
            probs.append(f"LOST: {n} paras, {zc} cjk / {sc} src chars "
                         f"ratio={ratio:.2f} (dir median {med:.2f})")
        if probs:
            bad += 1
            total += len(probs)
            print(f"{os.path.relpath(f, ROOT)}  ({len(probs)})")
            for p in probs[:8]:
                print(f"    {p}")
            if len(probs) > 8:
                print(f"    ... {len(probs) - 8} more")

    print(f"\n{bad} files broken, {total} problems "
          f"({len(results)} scanned)")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
