"""Apply verified proofreading edits to the EPUBs and to the work_* segments.

The audit ran against work_*/out/*/final.txt, but the EPUB text has since taken the
name unifications (凡特伊 → 凡德伊). So each edit is tried twice: verbatim, then with
the book's name map applied to both sides. An edit is dropped unless it lands in
exactly one place.
"""
import json, os, re, shutil, sys, zipfile
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_names3 import FIX

NAME = {k.replace("（坟头草译）", ""): v for k, v in FIX.items()}
BOOK2EPUB = {}
BOOK2CN = {}
for f in os.listdir("out"):
    if f.endswith(".epub"):
        BOOK2EPUB[f[:-5].replace("（坟头草译）", "")] = os.path.join("out", f)

# 工作目录名（bovary / emma …）→ 中文书名，取自各书 index.json 的 title_zh
import glob as _glob
for idx in _glob.glob("work_*/*/src/index.json"):
    try:
        d = json.load(open(idx, encoding="utf-8"))
    except Exception:
        continue
    key = idx.replace("\\", "/").split("/")[1]
    t = d.get("title_zh") or ""
    if t:
        BOOK2EPUB[key] = os.path.join("out", t + "（坟头草译）.epub")
        BOOK2CN[key] = t


def apply_names(s, book):
    for a, b in NAME.get(BOOK2CN.get(book, book), []):
        s = s.replace(a, b)
    return s


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "scratch/audit_verified.jsonl"
    recs = [json.loads(l) for l in open(path, encoding="utf-8")]
    by_book = defaultdict(list)
    for r in recs:
        for x in r["issues"]:
            by_book[r["book"]].append(x)

    stats = Counter()
    report = []
    for book, issues in sorted(by_book.items()):
        epub = BOOK2EPUB.get(book)
        if not epub:
            stats["no_epub"] += len(issues)
            continue
        with zipfile.ZipFile(epub) as z:
            files = {n: z.read(n).decode("utf-8") for n in z.namelist() if n.endswith(".xhtml")}
            order = [n for n in z.namelist()]
            raw = {n: z.read(n) for n in order}

        changed = Counter()
        for x in issues:
            if x.get("type", "").startswith("专名"):
                stats["skip_name"] += 1
                continue
            r = len(x["fix"]) / max(1, len(x["zh"]))
            if not (0.45 <= r <= 2.2):
                stats["skip_len"] += 1
                continue
            if any(k in x["fix"] for k in ("原文", "译注", "（译者", "抱歉")):
                stats["skip_meta"] += 1
                continue
            cands = [(x["zh"], x["fix"])]
            alt = (apply_names(x["zh"], book), apply_names(x["fix"], book))
            if alt != cands[0]:
                cands.append(alt)
            done = False
            for old, new in cands:
                if not old or old == new:
                    continue
                hits = [(n, s.count(old)) for n, s in files.items() if old in s]
                total = sum(c for _, c in hits)
                if total == 0 or total > 2:
                    continue
                n, _ = hits[0]
                files[n] = files[n].replace(old, new, 1)
                changed[x["type"]] += 1
                report.append({"book": book, "file": n, "type": x["type"],
                               "old": old, "new": new, "why": x.get("why", "")})
                done = True
                break
            if not done:
                stats["unplaced"] += 1

        if not changed:
            continue
        tmp = epub + ".tmp"
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as o:
            for n in order:
                data = files[n].encode("utf-8") if n in files else raw[n]
                o.writestr(n, data)
        shutil.move(tmp, epub)
        stats["applied"] += sum(changed.values())
        print("  %-24s %3d  %s" % (book[:24], sum(changed.values()), dict(changed)))

    json.dump(report, open("scratch/audit_applied.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(dict(stats))


if __name__ == "__main__":
    main()
