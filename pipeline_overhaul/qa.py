"""Post-build QA: the checks a second proofreader would run."""
from __future__ import annotations

import collections
import difflib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402
from names import MAPS  # noqa: E402


def run(book: str) -> dict:
    d = os.path.join(common.WORK, book, "final")
    ids = sorted(os.path.splitext(f)[0] for f in os.listdir(d))
    han = paras = notes = 0
    bad_names = collections.Counter()
    dup = []
    tags = 0
    open_q = 0
    for cid in ids:
        fin = common.load_json(os.path.join(d, cid + ".json"))
        texts = fin["texts"]
        han += common.han("".join(texts))
        paras += len(texts)
        notes += len(fin.get("notes") or [])
        joined = "\n".join(texts)
        for a, _ in MAPS[book]:
            n = joined.count(a)
            if n:
                bad_names[a] += n
        tags += len(re.findall(r"</?[a-zA-Z][a-zA-Z0-9_:-]*>", joined))
        if joined.count("“") != joined.count("”"):
            open_q += 1
        for i in range(len(texts)):
            if len(texts[i]) < 60:
                continue
            for j in range(i + 1, min(i + 4, len(texts))):
                if len(texts[j]) < 60:
                    continue
                r = difflib.SequenceMatcher(None, texts[i], texts[j]).ratio()
                if r > 0.6:
                    dup.append((cid, i, j, round(r, 2)))
    return {"chapters": len(ids), "paras": paras, "han": han, "notes": notes,
            "bad_names": dict(bad_names), "dup": dup, "tags": tags, "open_q": open_q}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    out = {}
    for b in sys.argv[1:] or ["whale", "soledad", "lotr"]:
        r = run(b)
        out[b] = r
        print(f"{b}: {r['chapters']} chapters, {r['paras']} paras, {r['han']:,} han, "
              f"{r['notes']} notes")
        print(f"   residual bad names: {r['bad_names']}")
        print(f"   duplicate pairs: {len(r['dup'])} {r['dup'][:4]}")
        print(f"   stray tags: {r['tags']}, chapters with unbalanced quotes: {r['open_q']}")
    common.save_json(os.path.join(common.WORK, "qa.json"), out)


if __name__ == "__main__":
    main()
