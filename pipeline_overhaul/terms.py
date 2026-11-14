"""Build a book-wide termbase and unify the name variants.

Stage 1  extract  one call per chapter: source + translation -> [{src, zh, kind}]
Stage 2  merge    group by source form, count Chinese variants, pick a canonical
Stage 3  unify    replace the losing variants across the book (longest first)

The extraction is deliberately narrow: only proper names, ships, places,
allusions and craft terms. Common nouns are left alone, because a termbase of
ordinary words poisons the prose.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "pipeline_whale"))

import llm  # noqa: E402
import common  # noqa: E402

MODEL = "xm:mimo-v2.6-flash"

SYS = """你是双语编辑，正在为一部译作建立专名表。只做抽取，不做评论。
从给出的原文与译文里，找出所有专名与行业术语，输出 JSON 数组，每项：
{"src": "原文写法", "zh": "译文里的写法", "kind": "人名|地名|船名|典故|术语|机构"}
要求：
- 只收原文中确实出现、译文里确实有对应译法的条目；
- 人名收全名，也收书中反复单独使用的姓氏形式（分别列项）；
- 典故指圣经、神话、历史、文学出处（如 Kraken、Anak、Tamar）；
- 术语指行业词（如 crotch、box line、ambergris）；
- 不确定的不要收；最多 40 条；只输出 JSON 数组，不要解释。"""


def chapter_prompt(book: str, ch: dict) -> str:
    if book == "whale":
        pairs = []
        for i, p in enumerate(ch["paras"]):
            pairs.append(f"[{i}] EN: {p['src']}\n    ZH: {p['zh']}")
        return "\n".join(pairs)
    src = "\n\n".join(ch["src_paras"])
    zh = "\n\n".join(ch["zh"])
    return f"原文（西班牙语）：\n{src[:9000]}\n\n译文：\n{zh[:9000]}"


def extract_one(book: str, cid: str) -> list[dict]:
    path = os.path.join(common.WORK, book, "terms_raw", cid + ".json")
    if os.path.exists(path):
        return common.load_json(path, [])
    ch = common.load_json(common.chapter_path(book, cid))
    if not ch:
        return []
    body = chapter_prompt(book, ch)
    try:
        text, _ = llm.chat(
            [{"role": "system", "content": SYS},
             {"role": "user", "content": body[:12000] + "\n\n请输出 JSON 数组。"}],
            MODEL, max_tokens=2500, temperature=0.1, tag=f"{book}:terms:{cid}",
            timeout=240)
        m = re.search(r"\[.*\]", text, re.S)
        items = json.loads(m.group(0)) if m else []
        items = [x for x in items if isinstance(x, dict) and x.get("src") and x.get("zh")]
    except Exception as e:  # noqa: BLE001
        print("  !!", cid, str(e)[:100])
        items = []
    common.save_json(path, items)
    return items


def extract(book: str, cids: list[str], workers: int = 8) -> None:
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(lambda c: extract_one(book, c), cids))
    print("extract done", book)


# ────────────────────────────────────────────── merge

def norm(src: str) -> str:
    s = src.strip().strip(".,;:!?\"'“”‘’()[]")
    s = re.sub(r"^(the|a|an|el|la|los|las)\s+", "", s, flags=re.I)
    return s.lower()


def merge(book: str, base: dict) -> dict:
    """-> {src_key: {src, kind, zh_counts, canonical}}"""
    groups: dict[str, dict] = {}
    raw_dir = os.path.join(common.WORK, book, "terms_raw")
    for fn in sorted(os.listdir(raw_dir)):
        for it in common.load_json(os.path.join(raw_dir, fn), []):
            k = norm(it["src"])
            if not k:
                continue
            g = groups.setdefault(k, {"src": it["src"], "kind": it.get("kind", ""),
                                      "zh": Counter(), "forms": Counter()})
            g["zh"][it["zh"].strip()] += 1
            g["forms"][it["src"].strip()] += 1
    for src, zh in base.items():
        if src.startswith("_"):
            continue
        k = norm(src)
        g = groups.setdefault(k, {"src": src, "kind": "", "zh": Counter(),
                                  "forms": Counter()})
        g["zh"][zh] += 3          # the curated base outvotes the extractor
        g["forms"][src] += 1
    for k, g in groups.items():
        g["canonical"] = g["zh"].most_common(1)[0][0]
    return groups


def report(book: str, groups: dict) -> None:
    multi = {k: g for k, g in groups.items() if len(g["zh"]) > 1}
    print(f"{book}: {len(groups)} terms, {len(multi)} with variants")
    for k, g in sorted(multi.items(), key=lambda kv: -sum(kv[1]["zh"].values())):
        print("  ", g["src"], "->", g["canonical"], "|", dict(g["zh"]))


# ────────────────────────────────────────────── unify

def unify(book: str, groups: dict, apply: bool = False) -> list[dict]:
    # every canonical form, to protect longer names from short-form replacement
    canons = {g["canonical"] for g in groups.values()}
    plan = []
    for k, g in groups.items():
        if len(g["zh"]) < 2:
            continue
        target = g["canonical"]
        for variant, n in g["zh"].items():
            if variant == target or len(variant) < 3:
                continue
            # a short form that is a piece of some other canonical name must not
            # be touched: replacing 何塞·阿尔卡蒂奥 would wreck 何塞·阿尔卡蒂奥·布恩迪亚
            if any(variant != c and variant in c for c in canons):
                continue
            plan.append({"src": g["src"], "from": variant, "to": target, "count": n})
    plan.sort(key=lambda x: -len(x["from"]))
    if not plan:
        return []
    changed = 0
    files = sorted(os.listdir(os.path.join(common.WORK, book, "ch")))
    for fn in files:
        p = os.path.join(common.WORK, book, "ch", fn)
        ch = common.load_json(p)
        hit = 0
        for item in ch.get("paras", []):
            t = item["zh"]
            for r in plan:
                if r["from"] in t:
                    hit += t.count(r["from"])
                    t = t.replace(r["from"], r["to"])
            item["zh"] = t
        if "zh" in ch:
            for i, t in enumerate(ch["zh"]):
                for r in plan:
                    if r["from"] in t:
                        hit += t.count(r["from"])
                        t = t.replace(r["from"], r["to"])
                ch["zh"][i] = t
        if hit:
            changed += hit
            if apply:
                common.save_json(p, ch)
    print(f"{book}: {len(plan)} replacement rules, {changed} hits"
          + ("" if apply else " (dry run)"))
    return plan


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, choices=["whale", "soledad"])
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    if a.book == "whale":
        from glossary import G as base
        cids = common.whale_chapters()
    else:
        base = common.load_json(os.path.join(common.ROOT, "work_soledad/glossary.json"), {})
        cids = common.soledad_chapters()

    os.makedirs(os.path.join(common.WORK, a.book, "terms_raw"), exist_ok=True)
    extract(a.book, cids)
    groups = merge(a.book, base)
    report(a.book, groups)
    plan = unify(a.book, groups, apply=a.apply)
    common.save_json(os.path.join(common.WORK, a.book, "terms.json"), {
        "groups": {k: {"src": g["src"], "kind": g["kind"], "canonical": g["canonical"],
                       "variants": dict(g["zh"])} for k, g in groups.items()},
        "plan": plan,
    })


if __name__ == "__main__":
    main()
