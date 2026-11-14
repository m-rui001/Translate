"""Shared helpers for the overhaul pass (Moby-Dick + Cien años de soledad).

The overhaul does not re-translate. It takes the delivered text, chapter by
chapter, and revises it against a written brief (the seven systemic faults the
reader reported), then verifies every touched paragraph against the source.

Layout under work_overhaul/<book>/:
    ch/<cid>.json    {id, title, paras:[{type, src, zh, rev}], edits:[...]}
    terms.json       canonical termbase + variants
    notes/<cid>.json footnotes for one chapter
"""
from __future__ import annotations

import json
import os
import re

ROOT = "E:/Translate"
WORK = os.path.join(ROOT, "work_overhaul")

CJK = re.compile(r"[\u4e00-\u9fff]")


def paras(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def han(s: str) -> int:
    return len(CJK.findall(s))


def load_json(path: str, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


# ────────────────────────────────────────────── whale

def whale_chapters() -> list[str]:
    ids = []
    idx = load_json(os.path.join(ROOT, "work_whale/chunks/index.json"), {})
    ids = list(idx.keys())
    order = ([c for c in ids if c in ("front_ety", "front_ext")] +
             sorted([c for c in ids if c.startswith("ch")], key=lambda x: int(x[2:])) +
             [c for c in ids if c.startswith("epi")])
    return order


def build_whale() -> None:
    for cid in whale_chapters():
        spec = load_json(os.path.join(ROOT, f"work_whale/chunks/{cid}.json"))
        blocks = [b for c in spec["chunks"] for b in c]
        md = os.path.join(ROOT, f"work_whale/out/{cid}/chapter.md")
        if not os.path.exists(md):
            print("  skip (no chapter.md)", cid)
            continue
        zh = paras(open(md, encoding="utf-8").read())
        if len(zh) != len(blocks):
            print(f"  !! {cid}: {len(blocks)} blocks vs {len(zh)} paragraphs")
            continue
        def src_of(b):
            if "text" in b:
                return b["text"]
            return "\n".join(b.get("lines") or [])

        out = {"id": cid, "title_en": spec.get("title_en", ""),
               "title_zh": spec.get("title_zh", ""), "book": "whale",
               "paras": [{"type": b["type"], "src": src_of(b), "zh": z}
                         for b, z in zip(blocks, zh)], "edits": []}
        save_json(os.path.join(WORK, "whale/ch", cid + ".json"), out)
    print("whale done")


# ────────────────────────────────────────────── soledad

def soledad_chapters() -> list[str]:
    d = os.path.join(ROOT, "work_soledad/src")
    return sorted(os.path.splitext(f)[0] for f in os.listdir(d)
                  if f.startswith("capitulo") and f.endswith(".json"))


def build_soledad() -> None:
    for cid in soledad_chapters():
        spec = load_json(os.path.join(ROOT, f"work_soledad/src/{cid}.json"))
        blocks = spec["blocks"]
        md = os.path.join(ROOT, f"work_soledad/out/{cid}/chapter.md")
        if not os.path.exists(md):
            print("  skip", cid)
            continue
        zh = paras(open(md, encoding="utf-8").read())
        head = [b["text"] for b in blocks if b.get("type") == "head"]
        body = [b for b in blocks if b.get("type") != "head"]
        out = {"id": cid, "title": "", "book": "soledad",
               "src_head": head[0] if head else "",
               "src_paras": [b["text"] for b in body],
               "zh": zh, "edits": []}
        save_json(os.path.join(WORK, "soledad/ch", cid + ".json"), out)
    print("soledad done")


# ────────────────────────────────────────────── lotr

def lotr_chapters() -> list[str]:
    d = os.path.join(ROOT, "work/src")
    return sorted(os.path.splitext(f)[0] for f in os.listdir(d) if f.endswith(".json"))


def build_lotr() -> None:
    for cid in lotr_chapters():
        spec = load_json(os.path.join(ROOT, f"work/src/{cid}.json"))
        md = os.path.join(ROOT, f"work/out/{cid}/chapter.md")
        if not os.path.exists(md):
            print("  skip", cid)
            continue
        ps = paras(open(md, encoding="utf-8").read())
        if ps and ps[0].startswith("#"):
            ps = ps[1:]
        blocks = spec["blocks"]

        def src_of(b):
            return b.get("text") or "\n".join(b.get("lines") or [])

        out = {"id": cid, "book": "lotr", "title_en": spec.get("title_en", ""),
               "title_zh": spec.get("title_zh", ""), "src_head": "",
               "src_paras": [src_of(b) for b in blocks],
               "src_types": [b.get("type", "p") for b in blocks],
               "zh": ps, "edits": []}
        save_json(os.path.join(WORK, "lotr/ch", cid + ".json"), out)
    print("lotr done")


def chapter_path(book: str, cid: str) -> str:
    return os.path.join(WORK, book, "ch", cid + ".json")


if __name__ == "__main__":
    os.makedirs(os.path.join(WORK, "whale/ch"), exist_ok=True)
    os.makedirs(os.path.join(WORK, "soledad/ch"), exist_ok=True)
    os.makedirs(os.path.join(WORK, "lotr/ch"), exist_ok=True)
    build_whale()
    build_soledad()
    build_lotr()
