"""Apply `titles_pub` to every index.json and report what could not be resolved."""
from __future__ import annotations

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "pipeline_private"))

import titles_pub as T          # noqa: E402
import books as booklist        # noqa: E402

TITLE_ZH = {b["key"]: b["title_zh"] for b in booklist.PUBLIC}


CN = "零一二三四五六七八九十"


def cn(n: int) -> str:
    if n <= 10:
        return CN[n]
    if n < 20:
        return "十" + CN[n - 10]
    return CN[n // 10] + "十" + (CN[n % 10] if n % 10 else "")


def part_prefix(titles: list[str]) -> list[str]:
    """Disambiguate a contents list whose chapter numbers restart.

    Buddenbrooks numbers its chapters from one in each of eleven parts, Les
    Misérables and Notre-Dame restart per book, and the extractor kept only the
    chapter numbers. Printed flat, the list reads 第一章 … 第十一章, 第一章 … — the
    reader cannot tell one part's chapter three from another's. The restart itself is
    the part boundary, so it is used as one: everything from the second part on is
    prefixed 第二部 / 第三部, and no chapter text is touched.
    """
    nums = []
    for t in titles:
        m = re.fullmatch(r"第([一二三四五六七八九十百]+)章", t.strip())
        nums.append(None if not m else m.group(1))
    out = list(titles)
    part = 1
    prev = None
    for i, t in enumerate(titles):
        n = nums[i]
        if n is not None and prev is not None and (n == "一" or len(n) < len(prev)):
            part += 1
        prev = n if n is not None else prev
        if part > 1 and n is not None:
            out[i] = f"第{cn(part)}部 {t}"
    return out


# Chapters the extractor mislabelled and no rule can recover: Notre-Dame's file c004
# opens with the publisher's imprint and the 1832 preface, not with Book I chapter i.
OVERRIDE = {("notredame", "c004"): "序"}

PART_RE = re.compile(
    r"(?i)^(?:LIVRE|TOME|PARTIE|PARTE|BUCH|TEIL|BOOK|PART|VOLUME|VOL\.?|"
    r"ERSTER|ZWEITER|DRITTER|VIERTER|FÜNFTER|SECHSTER|SIEBENTER|ACHTER|"
    r"NEUNTER|ZEHNTER|ELFTER|PRIMO|SECONDO|TERZO)\b"
    r"|^第[一二三四五六七八九十]+[部卷]")


def detect_parts(book_dir: str) -> dict[str, int]:
    """Which chapters open a part, from the source's own part headings.

    The extractor kept one file per chapter and left the part headings inside the
    chapter file where they fell: usually at the head of the part's first chapter, but
    sometimes at the tail of the previous one, because the heading sat between two
    chapter breaks. A heading in the last fifth of a file therefore starts the *next*
    chapter's part, not that one's.
    """
    files = sorted(glob.glob(os.path.join(book_dir, "c*.json")))
    ids = [os.path.basename(p)[:-5] for p in files]
    starts = set()
    for p, cid in zip(files, ids):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:                                        # noqa: BLE001
            continue
        blocks = d.get("blocks") or []
        for i, b in enumerate(blocks):
            t = (b.get("text") or "").strip()
            if t and len(t) < 60 and PART_RE.match(t):
                nxt = ids.index(cid) + (1 if i > 0.8 * max(1, len(blocks)) else 0)
                if nxt < len(ids):
                    starts.add(ids[nxt])
                break
    if not starts:
        return {}
    out, part = {}, 0
    for cid in ids:
        if cid in starts:
            part += 1
        out[cid] = part
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    bad: list[str] = []
    for p in sorted(glob.glob(os.path.join(ROOT, "work_pub", "*", "src", "index.json"))):
        d = json.load(open(p, encoding="utf-8"))
        book = d["book"]
        bt = TITLE_ZH.get(book, d.get("title_zh", book))
        single = len(d["chapters"]) == 1
        body = 0
        for pos, c in enumerate(d["chapters"], 1):
            front = pos == 1 and not c.get("title", "").strip()
            if not front:
                body += 1
            c["title_zh"] = T.title_zh(book, c.get("title", ""), pos, bt,
                                       skip_numbering=front, single_chapter=single,
                                       body_pos=body)
        for c in d["chapters"]:
            if (book, c["id"]) in OVERRIDE:
                c["title_zh"] = OVERRIDE[(book, c["id"])]
                continue
            t0 = c["title_zh"] or ""
            t1 = re.sub(r"^第[一二三四五六七八九十]+部\s*", "", t0)
            c["title_zh"] = t1 if t1.strip() else t0
            # A wrapped line once split a heading in the middle ("第三 章"); a space
            # between two Chinese characters is never intentional in a title.
            c["title_zh"] = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "",
                                   c["title_zh"])
        if book != "urteil":
            parts = detect_parts(os.path.join(ROOT, "work_pub", book, "src"))
            if parts and max(parts.values()) > 1:
                for c in d["chapters"]:
                    pn = parts.get(c["id"], 1)
                    if pn > 1:
                        c["title_zh"] = f"第{cn(pn)}部 {c['title_zh']}"
            else:
                fixed = part_prefix([c["title_zh"] for c in d["chapters"]])
                for c, t in zip(d["chapters"], fixed):
                    c["title_zh"] = t
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        bad.extend(T.verify(d))
        print(f"{book:15s} {len(d['chapters']):3d} chapters: "
              + " / ".join(c["title_zh"] for c in d["chapters"][:5])
              + (" ..." if len(d["chapters"]) > 5 else ""))
    print()
    if bad:
        print(f"PROBLEMS ({len(bad)}):")
        for b in bad:
            print("  " + b)
    else:
        print("all chapter titles resolved")


if __name__ == "__main__":
    main()
