"""Judge terminology candidates: same entity, or two different things?

The miner only reports *shape*: two transliterations of equal length that
differ in one character. Some are genuine drift (克莱费尔德/克莱费尔特,
拉达曼提斯/拉达曼迪斯); some are two different people (伊欧墨/伊欧蒙), and
some are not names at all (座高塔/座高高). A blind global replace would
therefore corrupt the book.

Each candidate is sent to the model together with one sentence from the book
showing each form. The model answers with a verdict, which is cached, so the
whole termbase can be settled once and re-used by every later pass.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine  # noqa: E402
import terms   # noqa: E402

ROOT = "E:/Translate"
REPORTS = os.path.join(ROOT, "reports")

SYS_JUDGE = """你是译稿的专名校对。我给你两组中文写法，以及它们在书里出现的句子。
你只需判断：这是不是**同一个**人名/地名/术语的两种写法。

判断一律从严：
- 若是两个人（例如 伊欧墨 Éomer 与 伊欧蒙 Éomund）、两个地方、两个概念，答 DIFFERENT。
- 若其中一个是普通词语被误当成专名（例如「座高塔」「片树林」），答 NOT_NAME。
- 只有确实是同一对象、写法有出入时，才答 SAME，并指出应当统一成哪一种。

只输出一行，三种格式之一：
SAME <统一后的写法>
DIFFERENT
NOT_NAME"""


def snippet(texts: list[str], needle: str, width=26) -> str:
    for t in texts:
        i = t.find(needle)
        if i >= 0:
            return t[max(0, i - width):i + len(needle) + width].replace("\n", " ")
    return ""


def judge_pair(a: str, b: str, texts: list[str]) -> dict:
    prompt = (f"写法一：{a}\n例句：{snippet(texts, a)}\n\n"
              f"写法二：{b}\n例句：{snippet(texts, b)}")
    for _ in range(3):
        try:
            raw = engine.call([{"role": "system", "content": SYS_JUDGE},
                               {"role": "user", "content": prompt}],
                              temperature=0.0, max_tokens=60, retries=3)
        except Exception:
            continue
        line = (raw or "").strip().split("\n")[0].strip()
        m = re.match(r"^\s*(SAME|DIFFERENT|NOT_NAME)\b\s*(.*)$", line, re.I)
        if not m:
            continue
        verdict = m.group(1).upper()
        unify = (m.group(2) or "").strip()
        return {"a": a, "b": b, "verdict": verdict, "unify": unify}
    return {"a": a, "b": b, "verdict": "UNKNOWN", "unify": ""}


def run_book(book: str, texts: list[str], workers=60) -> dict:
    from concurrent.futures import ThreadPoolExecutor

    cand_path = os.path.join(REPORTS, f"terms_{book}.json")
    if not os.path.exists(cand_path):
        return {}
    cand = json.load(open(cand_path, encoding="utf-8"))
    pairs, seen = [], set()
    for c in cand["auto"] + cand["manual"]:
        key = tuple(sorted((c["major"], c["minor"])))
        if key in seen:
            continue
        seen.add(key)
        pairs.append((c["major"], c["minor"]))

    out_path = os.path.join(REPORTS, f"term_rules_{book}.json")
    done = {}
    if os.path.exists(out_path):
        for r in json.load(open(out_path, encoding="utf-8")).get("judged", []):
            done[tuple(sorted((r["a"], r["b"])))] = r
    todo = [(a, b) for a, b in pairs if tuple(sorted((a, b))) not in done]
    print(f"[{book}] {len(pairs)} candidates, {len(todo)} to judge", flush=True)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(judge_pair, a, b, texts): (a, b) for a, b in todo}
        for f in futs:
            r = f.result()
            done[tuple(sorted((r["a"], r["b"])))] = r

    judged = list(done.values())
    rules = []
    for r in judged:
        if r["verdict"] != "SAME":
            continue
        u = r.get("unify") or ""
        if u not in (r["a"], r["b"]):
            # model named a third form: pick whichever of the two it matches
            u = r["a"] if r["a"] in u else (r["b"] if r["b"] in u else "")
        if not u:
            continue
        loser = r["b"] if u == r["a"] else r["a"]
        if loser == u:
            continue
        rules.append({"minor": loser, "major": u,
                      "n_major": None, "n_minor": None, "why": "judge"})
    payload = {"book": book, "judged": judged, "rules": rules}
    json.dump(payload, open(out_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"[{book}] {sum(1 for r in judged if r['verdict']=='SAME')} SAME, "
          f"{sum(1 for r in judged if r['verdict']=='DIFFERENT')} DIFFERENT, "
          f"{sum(1 for r in judged if r['verdict']=='NOT_NAME')} NOT_NAME -> "
          f"{len(rules)} rules", flush=True)
    return payload


def load_rules(book: str) -> list[dict]:
    p = os.path.join(REPORTS, f"term_rules_{book}.json")
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding="utf-8")).get("rules") or []


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    import books as B
    names = sys.argv[1:] or list(B.BOOKS)
    for b in names:
        ts = B.book_texts(b)
        run_book(b, ts, workers=60)
