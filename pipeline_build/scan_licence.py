"""Find Project Gutenberg licence pages that shipped as book chapters.

Two books had one. `effi` chapter 1 was the notice itself ("The Project Gutenberg eBook
of Effi Briest / Title: ... / Release date: ..."), translated in full; because it took the
first chapter's slot, every real chapter was numbered one too high and the table of
contents had a bogus opening entry. `diana` chapter 2 was the same page, and there the
writer refused to translate it, so the refusal shipped as prose.

Both are now dropped at assembly time by `build_gutenberg.chapter_ids`, so this checks the
finished EPUBs rather than the intermediate JSON -- the intermediate files are still on
disk as evidence, and a checker that reports them would never go green.

Decisive test: a page that contains Gutenberg licence wording *and* almost no Chinese.
A real chapter that quotes a notice in an epigraph has prose in it and is not reported.
"""
from __future__ import annotations

import glob
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "out")

CJK = re.compile(r"[\u4e00-\u9fff]")

LICENCE = re.compile(
    r"Release date:|Most recently updated|eBook #\d+|"
    r"Project Gutenberg|^\s*(?:Language|Credits|Title|Author):",
    re.I | re.M)

# a chapter with fewer Chinese characters than this is not a translated chapter
MIN_CJK = 80


def body(xhtml: str) -> str:
    m = re.search(r"<body[^>]*>(.*)</body>", xhtml, re.S)
    if not m:
        return ""
    inner = re.sub(r"</(?:p|h[1-6]|div|li|blockquote|tr)>|<br\s*/?>", "\n\n", m.group(1))
    return re.sub(r"<[^>]+>", "", inner)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    bad = 0
    for p in sorted(glob.glob(os.path.join(OUT, "*.epub"))):
        try:
            z = zipfile.ZipFile(p)
        except Exception:  # noqa: BLE001
            continue
        for n in z.namelist():
            if not re.match(r"OEBPS/c\d+\.xhtml$", n):
                continue
            try:
                t = body(z.read(n).decode("utf-8", errors="replace"))
            except Exception:  # noqa: BLE001
                continue
            if not LICENCE.search(t):
                continue
            if len(CJK.findall(t)) >= MIN_CJK:
                continue
            bad += 1
            print(f"{os.path.basename(p)} :: {n}")
            head = " ".join(t.split())[:140]
            print(f"    {head!r}")

    print(f"\n{bad} licence pages shipped as chapters")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
