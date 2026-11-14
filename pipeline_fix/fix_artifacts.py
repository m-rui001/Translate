"""Deduplicate 7 splice artifacts: repeats our sync/port edits left mid-sentence.

Found by re-scanning every paragraph the 2026-10-30 passes edited for a pattern that
was *new* relative to the backup (2+ CJK chars repeated adjacently, AABB excluded).
Most hits were legitimate reduplication (一点一点/商量商量); these seven are not:

  effi         罗德的遗孀的遗孀          -> 的遗孀
  maias        两局牌之间两局牌之间        -> 两局牌之间
  buddenbrooks 隔着窗子隔着窗子朝          -> 隔着窗子朝
  buddenbrooks 其中其中大部分              -> 其中大部分
  toerless     并非并非因为                -> 并非因为
  maxhavelaar  我说我说我是                -> 我说我是
  buddenbrooks 请个请个女看护              -> 请个女看护   (backup: 请个护理妇)

Each replacement is asserted to occur exactly once in its file before anything is
written; paragraph counts are checked by re-splitting after the write.
"""
import glob
import os
import re
import shutil
import sys

ROOT = "E:/Translate"
BAK = os.path.join(ROOT, "_bak", "artifact_fix_20261030")

FIXES = [
    ("work_gutenberg/effi/out/c014/c02/final.txt", "登记官罗德的遗孀的遗孀三天前", "登记官罗德的遗孀三天前"),
    ("work_gutenberg/maias/out/c002/c05/final.txt", "在两局牌之间两局牌之间，", "在两局牌之间，"),
    ("work_pub/buddenbrooks/out/c002/c01/final.txt", "隔着窗子隔着窗子朝街上张望", "隔着窗子朝街上张望"),
    ("work_pub/buddenbrooks/out/c059/c02/final.txt", "其中其中大部分他打算出租", "其中大部分他打算出租"),
    ("work_pub/toerless/out/c003/c03/final.txt", "并非并非因为他是浪荡子", "并非因为他是浪荡子"),
    ("work_gutenberg/maxhavelaar/out/c002/c08/final.txt", "我说我说我是德罗斯托佩尔", "我说我是德罗斯托佩尔"),
    ("work_pub/buddenbrooks/out/c082/c00/final.txt", "请个请个女看护来", "请个女看护来"),
]


def paras(t: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    apply = "--apply" in sys.argv
    problems = []
    for rel, bad, good in FIXES:
        path = os.path.join(ROOT, rel.replace("/", os.sep))
        raw = open(path, encoding="utf-8", newline="").read()
        n = raw.count(bad)
        if n != 1:
            problems.append(f"{rel}: '{bad}' found {n}x (want 1)")
            continue
        if not apply:
            print(f"OK   {rel}")
            continue
        dst = os.path.join(BAK, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(path, dst)
        new_raw = raw.replace(bad, good)
        if len(paras(raw)) != len(paras(new_raw)):
            problems.append(f"{rel}: paragraph count changed, skipped")
            continue
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(new_raw)
        print(f"FIXED {rel}")
    if problems:
        print("\nPROBLEMS:")
        print("\n".join("  " + p for p in problems))
        return 1
    print("\n(applied)" if apply else "\n(dry run)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
