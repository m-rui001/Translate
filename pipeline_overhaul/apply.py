"""Apply verified edits and write the final chapter text.

Rules:
- an edit flagged loss/add/error is replaced by the checker's fix when one is
  given, otherwise the old paragraph is restored;
- an edit that the checker passed is applied as written.
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402
from revise import corrupted  # noqa: E402


def run(book: str) -> None:
    out_dir = os.path.join(common.WORK, book, "final")
    os.makedirs(out_dir, exist_ok=True)
    cids = sorted(os.path.splitext(f)[0] for f in
                  os.listdir(os.path.join(common.WORK, book, "ch")))
    stats = {"applied": 0, "reverted": 0, "fixed": 0}
    for cid in cids:
        ch = common.load_json(common.chapter_path(book, cid))
        base = ch["paras"] if "paras" in ch else ch["zh"]
        texts = [p["zh"] if "paras" in ch else p for p in base]
        rev = common.load_json(os.path.join(common.WORK, book, "rev", cid + ".json"), {})
        ver = common.load_json(os.path.join(common.WORK, book, "verify", cid + ".json"), {})
        vmap = {v["i"]: v for v in ver.get("verdicts", [])}
        for e in rev.get("edits", []):
            i = e["i"]
            if corrupted(e["old"], e["new"]):
                stats["reverted"] += 1
                continue
            v = vmap.get(i, {"verdict": "ok"})
            if v["verdict"] == "ok":
                texts[i] = e["new"]
                stats["applied"] += 1
            elif v.get("fix") and common.CJK.search(v["fix"]) and len(v["fix"]) > 20:
                texts[i] = v["fix"]
                stats["fixed"] += 1
            else:
                stats["reverted"] += 1
        notes = common.load_json(os.path.join(common.WORK, book, "notes", cid + ".json"), [])
        common.save_json(os.path.join(out_dir, cid + ".json"), {
            "id": cid, "book": book,
            "title_en": ch.get("title_en", ""), "title_zh": ch.get("title_zh", ""),
            "texts": texts,
            "types": ch.get("zh_types") or (["p"] * len(texts)),
            "notes": notes,
        })
    print(book, stats)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for b in sys.argv[1:] or ["whale", "soledad", "lotr"]:
        run(b)
