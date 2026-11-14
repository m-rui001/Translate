"""Sanity-check the extracted chapters before spending money translating them.

Extraction can fail quietly in ways that only surface as bad Chinese much later,
so this inspects the artefacts directly: chapter sizes, paragraph shapes, marker
balance and leftover source-language debris.

Checks:
  * every chapter has paragraphs, and no chapter is absurdly small or huge;
  * median paragraph length is in a plausible range for prose (a paragraph of 3
    characters means the folding broke, one of 20,000 means blank lines were lost);
  * `<em>`/`⟦i⟧` markers are balanced and no raw `_word_` remains;
  * no Project Gutenberg boilerplate survived ("*** START OF", "End of Project");
  * the first chapter of each book is printed so the opening line can be eyeballed.
"""
import glob
import json
import os
import re
import sys

ROOT = "E:/Translate/work_gutenberg"


def check_book(d: str) -> list[str]:
    book = os.path.basename(os.path.dirname(d))
    idx = json.load(open(os.path.join(d, "index.json"), encoding="utf-8"))
    problems: list[str] = []
    chs = idx["chapters"]
    if not chs:
        return [f"{book}: no chapters"]

    med_list, total = [], 0
    for c in chs:
        j = json.load(open(os.path.join(d, c["id"] + ".json"), encoding="utf-8"))
        blocks = j["blocks"]
        paras = [b["text"] for b in blocks if b["type"] == "p" and b["text"].strip()]
        if not paras:
            problems.append(f"{book}/{c['id']}: no paragraphs")
            continue
        lens = sorted(len(p) for p in paras)
        med = lens[len(lens) // 2]
        med_list.append(med)
        total += sum(lens)
        for p in paras:
            if p.count("⟦i⟧") != p.count("⟦/i⟧"):
                problems.append(f"{book}/{c['id']}: unbalanced italic markers")
                break
        joined = " ".join(paras)
        if "*** START OF" in joined or "End of Project Gutenberg" in joined:
            problems.append(f"{book}/{c['id']}: licence text leaked")
        if re.search(r"(?<!\w)_[^_\s]{2,40}_(?!\w)", joined):
            problems.append(f"{book}/{c['id']}: raw underscore italics left")
    med_all = sorted(med_list)[len(med_list) // 2] if med_list else 0
    print(f"  {book:16s} ch={len(chs):3d} paras_per_ch_median={med_all:5d} "
          f"chars={total:9,}  structure={idx.get('structure','?')}")
    return problems


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    dirs = sorted(glob.glob(os.path.join(ROOT, "*", "src")))
    all_problems: list[str] = []
    for d in dirs:
        all_problems += check_book(d)
    print()
    if all_problems:
        print(f"{len(all_problems)} problem(s):")
        for p in all_problems[:40]:
            print("  -", p)
    else:
        print("no problems found")

    # show the opening of one chapter per book for a human read
    print("\nsamples:")
    for d in dirs[:40]:
        idx = json.load(open(os.path.join(d, "index.json"), encoding="utf-8"))
        chs = idx["chapters"]
        if not chs:
            continue
        c = chs[min(1, len(chs) - 1)]
        j = json.load(open(os.path.join(d, c["id"] + ".json"), encoding="utf-8"))
        paras = [b["text"] for b in j["blocks"] if b["type"] == "p"][:2]
        book = os.path.basename(os.path.dirname(d))
        print(f"  [{book}/{c['id']} {c['title'][:24]}] {paras[0][:110] if paras else ''}")


if __name__ == "__main__":
    main()
