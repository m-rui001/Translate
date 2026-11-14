"""Find model chatter and duplicated paragraphs in the assembled prose.

Two defects that a reader notices immediately and no structural check catches.

**Meta-talk.** Once in a while the writer answers as a chatbot instead of translating:

    请问您是否想了解下一章（第四章）的主要故事情节概括？
    希望这个译本对您有帮助。

The paragraph is fluent Chinese, so nothing else flags it. The signatures are a
question addressed to the reader, or a closing offer of further help.

**Duplicated paragraphs.** When the chunker hands two overlapping windows to the
assembler, both copies land in the file. A whole paragraph repeated verbatim inside one
chapter is never intentional -- a translation does not repeat a 127-character sentence
by accident.

Scans `work_*/**/final.txt`, the JSON `texts` arrays, and the built EPUBs, so it finds
the defect wherever it lives. Reports only; repairing is a separate, deliberate step.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
import zipfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CJK = re.compile(r"[\u4e00-\u9fff]")
TAG = re.compile(r"<[^>]+>")

# Things a model says to a user, never to a reader of a novel. Kept narrow on purpose:
# `请问` alone occurs in dialogue ("请问您贵姓"), so it needs the reader-directed tail.
# Model chatter: text written to a *user of a chatbot*, never to a reader of a novel.
#
# Narrow on purpose. `很抱歉` and `当然` are ordinary dialogue openers -- "我很抱歉，甘姆吉
# 先生" said Frodo -- and an earlier, looser version of this list flagged sixty ordinary
# paragraphs for every real one. A pattern only belongs here if it cannot occur inside
# the story: it must talk about the task (translating, summarising, helping) rather than
# about the characters.
META = [
    re.compile(r"我(?:无法|不能|没法)为(?:这段|该段|本章|本段|以上)"),
    re.compile(r"(?:逐段|逐行|逐句)(?:对应)?的?(?:完整)?(?:中文)?翻译"),
    re.compile(r"请问您?是否(?:想|希望|需要)(?:了解|知道)"),
    re.compile(r"(?:主要)?故事情节概括|情节概括"),
    re.compile(r"(?:从|就)(?:文学|翻译)(?:与|和)(?:叙事|翻译)(?:角度|视角)"),
    re.compile(r"如果您?(?:还)?(?:想|需要|希望)(?:了解|知道)更多"),
    re.compile(r"如需(?:要)?(?:更多|进一步|其他)(?:信息|帮助|内容)"),
    re.compile(r"作为(?:一个)?(?:AI|人工智能|语言模型)"),
    re.compile(r"^好的[！!，,]\s*(?:以下|下面|我)"),
]


def texts_of_final(path: str) -> list[str]:
    t = open(path, encoding="utf-8", errors="replace").read()
    return [p.strip() for p in re.split(r"\n{2,}", t) if p.strip()]


def texts_of_json(path: str) -> list[str]:
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return []
    if isinstance(d, dict) and isinstance(d.get("texts"), list):
        return [x for x in d["texts"] if isinstance(x, str)]
    if isinstance(d, list):
        return [x for x in d if isinstance(x, str)]
    return []


def texts_of_epub(path: str):
    z = zipfile.ZipFile(path)
    for n in sorted(z.namelist()):
        if not n.endswith((".xhtml", ".html")) or "nav" in n or "toc" in n:
            continue
        html = z.read(n).decode("utf-8", "replace")
        m = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
        inner = m.group(1) if m else html
        inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
        inner = re.sub(r"</(?:p|h[1-6]|div|li|blockquote|tr)>|<br\s*/?>", "\n\n", inner)
        yield n, [p.strip() for p in re.split(r"\n{2,}", TAG.sub("", inner)) if p.strip()]


def scan(label: str, paras: list[str], hits: list[str], dups: list[str]) -> None:
    for i, p in enumerate(paras):
        for pat in META:
            if pat.search(p):
                hits.append(f"{label}[{i}] META {p[:70]!r}")
                break

    seen = Counter(p for p in paras if len(CJK.findall(p)) > 40)
    for p, n in seen.items():
        if n > 1:
            where = [i for i, x in enumerate(paras) if x == p]
            dups.append(f"{label} DUP x{n} at {where}: {p[:60]!r}")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    hits: list[str] = []
    dups: list[str] = []

    # 1. plain-text finals
    pats = ["work_*/out/**/final.txt", "work_*/final/*.txt"]
    files = sorted({f for pat in pats for f in glob.glob(os.path.join(ROOT, pat), recursive=True)})
    for f in files:
        if "_backup" in f or "_pre_writeback" in f:
            continue
        rel = os.path.relpath(f, ROOT)
        scan(rel, texts_of_final(f), hits, dups)

    # 2. chapter JSON -- the path has a variable number of levels: `work_overhaul/lotr/
    # final/` but also `work_pub/<key>/src/`, so glob recursively.
    for f in sorted(glob.glob(os.path.join(ROOT, "work_*", "**", "*.json"), recursive=True)):
        if f.endswith(".polished.json") or "_backup" in f or "_pre_writeback" in f:
            continue
        scan(os.path.relpath(f, ROOT), texts_of_json(f), hits, dups)

    # 3. the books themselves
    for f in sorted(glob.glob(os.path.join(ROOT, "out", "*.epub"))):
        base = os.path.basename(f)
        for doc, paras in texts_of_epub(f):
            scan(f"{base}:{doc}", paras, hits, dups)

    print(f"=== meta-talk ({len(hits)}) ===")
    for h in hits:
        print("  " + h)
    print(f"\n=== duplicated paragraphs ({len(dups)}) ===")
    for d in dups:
        print("  " + d)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
