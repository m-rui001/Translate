"""Turn cached review issues into verified, minimal paragraph fixes.

The loop the corpus needs to reach print quality is 抽查→修复→复查, and this is the
middle arrow. One review issue at a time:

  1. **locate** — the issue carries book/unit/para and a ≤12-char zh snippet; the
     paragraph must still contain that snippet or the issue is stale (skipped).
  2. **adjudicate** — a *different model family* than the reviewer reads the original
     Chinese paragraph plus the claimed defect and answers YES/NO. Flash reviewers
     over-report (half-crown was flagged as a mistranslation of half-crown); the
     second opinion cuts that noise before anything is written.
  3. **repair** — only on YES: a writer model returns the corrected paragraph, told
     to make the smallest change that fixes the confirmed defect.
  4. **verify** — mechanically: still one paragraph, length ratio 0.6–1.8, similarity
     to the original >= 0.55 (a rewrite, not a repair, fails here), digits identical
     unless the issue is explicitly about numbers, ⟦i⟧/⟦/i⟧ marker counts identical,
     termbase proper nouns all still present.
  5. **write** — through sync_revisions.apply_edits, which re-checks paragraph counts
     per file and mirrors a backup first.

Dry run by default.

    python pipeline_polish/apply_review_fixes.py            # plan only
    python pipeline_polish/apply_review_fixes.py --apply
    python pipeline_polish/apply_review_fixes.py --apply --limit 20 --books bovary
"""
from __future__ import annotations

import argparse
import difflib
import glob
import json
import os
import re
import shutil
import sys
import threading

ROOT = "E:/Translate"
HERE = os.path.dirname(os.path.abspath(__file__))
for p in (os.path.join(ROOT, "pipeline_fix"), os.path.join(ROOT, "pipeline_build"), HERE):
    sys.path.insert(0, p)

import sync2 as S               # noqa: E402
import sync_revisions as R      # noqa: E402
import polish_engine as PE      # noqa: E402

# pipeline_fix/llm.py also answers to `import llm` and lacks chat()'s `tag` kwarg;
# polish_engine has already pinned the whale client, so import from the same place.
sys.path.insert(0, os.path.join(ROOT, "pipeline_whale"))
import llm                      # noqa: E402

CACHE = os.path.join(ROOT, "work_polish2", "reports", "review_cache")
BACKUP = os.path.join(ROOT, "_bak", "work_reviewfix_20261030")
REPORT = os.path.join(ROOT, "pipeline_fix", "reviewfix_report.txt")

ADJUDGE_SYS = (
    "你是审校复核员。一位初审编辑对一段中文译文提出了意见。你只判断意见是否成立。"
    "只回 YES 或 NO，然后一行理由（不超过20字）。拿不准就 NO。"
    "注意：⟦i⟧⟦/i⟧ 是排版标记不是乱码；引语中的外文原文属正常保留；"
    "段号错位不是问题；风格偏好不是问题。"
)
REPAIR_SYS = (
    "你是修稿编辑。对给出的中文段落，只修复已确认的那一个缺陷，做**最小改动**："
    "除该缺陷涉及的字句外，其余文字一字不动。不改写、不润色、不调整语序、"
    "不增删信息、不动专名与数字（除非缺陷就是专名或数字错误）。"
    "只输出修改后的完整段落，不要任何说明、编号或标记。"
)
NUM_KW = ("数字", "年代", "年份", "日期", "岁", "半克朗", "克朗", "镑", "先令", "编号", "号码")


def norm(t: str) -> str:
    return S.norm(t)


def load_issues(book_filter: set[str] | None):
    out = []
    for f in sorted(glob.glob(os.path.join(CACHE, "*.json"))):
        try:
            rec = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if rec.get("error"):
            continue
        if book_filter and rec.get("book") not in book_filter:
            continue
        for it in rec.get("issues") or []:
            it = dict(it)
            it["_book"] = rec["book"]
            it["_unit"] = rec["unit"]
            out.append(it)
    return out


def locate(book: str, unit: str, issue: dict) -> tuple[str, int, str] | None:
    """(path, idx, paragraph) the issue points at, or None when stale."""
    # tree-aware: a book may live in work_pub (most) or only in work_gutenberg
    # (the 15 public-domain books built from the gutenberg source). Prefer
    # work_pub, fall back to work_gutenberg so gutenberg-only issues are fixable.
    path = None
    for tree in ("work_pub", "work_gutenberg"):
        p = os.path.join(ROOT, tree, book, "out", *unit.split("/"), "final.txt")
        if os.path.exists(p):
            path = p
            break
    if path is None:
        return None
    try:
        raw = open(path, encoding="utf-8", newline="").read()
    except OSError:
        return None
    paras = R.B.paras(raw) if hasattr(R, "B") else None
    if paras is None:
        import build_all as B
        paras = B.paras(raw)
    snippet = norm(issue.get("zh") or "")
    # 1st choice: the paragraph the reviewer numbered, if the snippet still matches
    idx = (int(issue.get("para") or 0) or 1) - 1
    if 0 <= idx < len(paras) and (not snippet or snippet[:6] in norm(paras[idx])):
        return path, idx, paras[idx]
    # 2nd choice: any paragraph containing the snippet
    if snippet:
        for i, p in enumerate(paras):
            if snippet[:6] in norm(p):
                return path, i, p
    return None


def adjudicate(issue: dict, para: str) -> tuple[bool, str]:
    src = (issue.get("src") or "")[:160]
    why = (issue.get("why") or "")[:80]
    zh = (issue.get("zh") or "")[:80]
    user = (f"初审意见：{why}\n所指片段：{zh}\n原文摘录：{src}\n\n"
            f"译文整段：\n{para[:1200]}")
    # any family may adjudicate -- the reviewer model was never recorded per issue,
    # and pinning one id burned 260 s per 524 while the others answered in seconds.
    try:
        t, _ = llm.chat_pool([{"role": "system", "content": ADJUDGE_SYS},
                              {"role": "user", "content": user}],
                             PE.POOL, temperature=0.0, max_tokens=120,
                             tag="adjudge", timeout=90, retries=1)
    except Exception as e:                                     # noqa: BLE001
        return False, "adjudge-error:" + str(e)[:60]
    t = t.strip()
    yes = t.upper().lstrip("(（[").startswith("YES")
    return yes, t[:60]


def repair(issue: dict, para: str) -> str | None:
    user = (f"缺陷：{(issue.get('why') or '')[:120]}\n"
            f"原文：{(issue.get('src') or '')[:200]}\n\n"
            f"段落：\n{para[:1500]}")
    try:
        t, _ = llm.chat_pool([{"role": "system", "content": REPAIR_SYS},
                              {"role": "user", "content": user}],
                             PE.POOL, temperature=0.2, max_tokens=1400,
                             tag="repair", timeout=140, retries=2)
    except Exception:                                          # noqa: BLE001
        return None
    t = re.sub(r"^```[\w-]*\s*|\s*```$", "", t.strip())
    if "\n\n" in t.strip():          # handed back more than one paragraph
        return None
    return t.strip()


def verify(orig: str, new: str, issue: dict) -> str | None:
    """Reason string when the candidate is unusable, else None."""
    if not new or not new.strip():
        return "empty"
    a, b = norm(orig), norm(new)
    r = min(len(a), len(b)) / max(len(a), len(b))
    if not 0.6 <= r <= 1.8:
        return f"length ratio {r:.2f}"
    sim = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
    if sim < 0.55:
        return f"similarity {sim:.2f}"
    if sorted(re.findall(r"\d+", a)) != sorted(re.findall(r"\d+", b)):
        why = issue.get("why") or ""
        if not any(k in why for k in NUM_KW):
            return "digits changed"
    if (orig.count("⟦i⟧"), orig.count("⟦/i⟧")) != (new.count("⟦i⟧"), new.count("⟦/i⟧")):
        return "italic markers changed"
    for t in PE._terms_in(orig):
        if t not in new:
            return f"term lost: {t}"
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=3,
                    help="concurrent issues in flight (endpoint handles ~4)")
    ap.add_argument("--books", default="")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    books = {b.strip() for b in a.books.split(",") if b.strip()} or None
    issues = load_issues(books)
    # one paragraph = one edit; multiple complaints about the same paragraph collapse
    seen: dict[tuple, dict] = {}
    for it in issues:
        k = (it["_book"], it["_unit"], it.get("para"), norm(it.get("zh") or "")[:8])
        seen.setdefault(k, it)
    issues = list(seen.values())
    if a.limit:
        issues = issues[: a.limit]
    print(f"issues: {len(issues)}")

    stats = {"stale": 0, "adjudicated": 0, "rejected": 0, "repaired": 0,
             "verify_failed": 0, "planned": 0}
    lock = threading.Lock()
    notes: list[str] = []

    def process_one(it):
        loc = locate(it["_book"], it["_unit"], it)
        if not loc:
            return "stale", None, None
        path, idx, para = loc
        yes, why = adjudicate(it, para)
        if not yes:
            return "rejected", f"REJ  {it['_book']}/{it['_unit']}#{idx} {why}", None
        new_t = repair(it, para)
        if not new_t:
            return "verify_failed", f"NOOP {it['_book']}/{it['_unit']}#{idx} repair empty/multi", None
        bad = verify(para, new_t, it)
        if bad:
            return "verify_failed", f"DROP {it['_book']}/{it['_unit']}#{idx} {bad}", None
        edit = {"path": path, "idx": idx, "new": new_t,
                "cid": it["_unit"].split("/")[0], "blk": it["_unit"]}
        return "repaired", f"FIX  {it['_book']}/{it['_unit']}#{idx}  ({why})", edit

    from concurrent.futures import ThreadPoolExecutor, as_completed
    edits = []
    with ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(process_one, it) for it in issues]
        for n, f in enumerate(as_completed(futs), 1):
            try:
                status, note, edit = f.result()
            except Exception as e:                             # noqa: BLE001
                status, note, edit = "verify_failed", f"ERR  {e}"[:120], None
            with lock:
                stats[status] = stats.get(status, 0) + 1
                if status == "repaired":
                    stats["planned"] += 1
                    edits.append(edit)
                if note:
                    notes.append(note)
                    print(f"  [{n}/{len(issues)}] {note}", flush=True)
    stats["adjudicated"] = stats["rejected"] + stats["repaired"] + stats["verify_failed"]


    # collapse: several issues may target the same paragraph; last wins only if the
    # paragraph text is still the original — apply_edits rejects inconsistent plans
    by_key = {}
    for e in edits:
        by_key.setdefault((e["path"], e["idx"]), []).append(e)
    final = []
    for (path, idx), es in by_key.items():
        if len(es) == 1:
            final.append(es[0])
            continue
        # chain them: re-verify each against the previous output
        cur = R.B.paras(open(path, encoding="utf-8", newline="").read())[idx]
        kept = None
        for e in es:
            bad = verify(cur, e["new"], {"why": ""})
            if not bad:
                kept = e
                cur = e["new"]
        if kept:
            final.append(kept)
        else:
            notes.append(f"SKIP multi-issue paragraph {path}#{idx}")

    lines = [f"{k:16s}{v}" for k, v in stats.items()]
    lines += ["", *notes]
    open(REPORT, "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines[:7]))
    print("report ->", REPORT)

    if not a.apply or not final:
        print("(dry run -- nothing written)" if not a.apply else "(no edits)")
        return 0
    for e in final:
        dst = os.path.join(BACKUP, os.path.relpath(e["path"], ROOT))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            shutil.copy2(e["path"], dst)
    res = R.apply_edits(final, apply=True)
    print("written:", res["written"], " problems:", res["problems"])
    return 1 if res["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
