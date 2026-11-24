"""《魔戒》润色 第 2 批：三章的半角引号体例，及四处残留音写地名。

book2c01 / book5c03 / book6c09 三章的对话用了半角 " 与 '，全册其余各章都是 “ ” ‘ ’。
这里逐段做「引号成对化」：按出现次序把半角引号折成中文成对引号，其余字符一个不动，
用 fold 的不变量校验（去掉引号后两段必须完全相同），段落数与段序一律不动。
"""
from __future__ import annotations

import ast
import json
import os
import sys

FINAL = "work_overhaul/lotr/final"

QUOTE_CHAPTERS = ["book2c01", "book5c03", "book6c09"]

# 音写地名归一：米歇尔·戴尔文/Michel Delving 与克里克霍洛/Crickhollow 都只有一处，
# 全册其他地方作米丘窟（10 处）与溪谷地（11 处）；巴克兰是 Buckland 的音写，
# 全书其余 8 处作雄鹿地（雄鹿堡是 Bucklebury 的村子，另一个地名，不动）。
FIX_CHAPTERS = ["book1c09", "book6c09"]
FIXES = [("米歇尔·戴尔文", "米丘窟", 1), ("克里克霍洛", "溪谷地", 1), ("巴克兰", "雄鹿地", 1)]


def load(p: str) -> dict:
    with open(p, encoding="utf-8", newline="") as f:
        return json.load(f)


def dump(p: str, d: dict) -> None:
    with open(p, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")


def strip_quotes(s: str) -> str:
    for q in "\"'“”‘’":
        s = s.replace(q, "")
    return s


def fold(text: str) -> str:
    """把半角引号按出现次序折成中文成对引号。"""
    out = []
    dq_open = True
    sq_open = True
    for ch in text:
        if ch == '"':
            out.append("“" if dq_open else "”")
            dq_open = not dq_open
        elif ch == "'":
            out.append("‘" if sq_open else "’")
            sq_open = not sq_open
        else:
            out.append(ch)
    return "".join(out)


def main(apply: bool) -> None:
    changed = 0
    docs: dict[str, dict] = {}
    for name in sorted(set(QUOTE_CHAPTERS) | set(FIX_CHAPTERS)):
        docs[name] = load(os.path.join(FINAL, name + ".json"))
    for ch in QUOTE_CHAPTERS:
        texts = docs[ch]["texts"]
        n = 0
        for i, t in enumerate(texts):
            if '"' not in t and "'" not in t:
                continue
            new = fold(t)
            # 不变量：除了引号字符，段落一字未改
            assert strip_quotes(t) == strip_quotes(new), (ch, i)
            assert t.count('"') + t.count("'") == \
                new.count("“") + new.count("”") + new.count("‘") + new.count("’"), (ch, i)
            texts[i] = new
            n += 1
            changed += 1
            if not apply:
                print(f"{ch}[{i}]\n  旧: {t[:80]}\n  新: {new[:80]}")
        print(f"{ch}: {n} 段改引号")
    for old, new, expect in FIXES:
        got = 0
        for name in FIX_CHAPTERS:
            texts = docs[name]["texts"]
            for i, t in enumerate(texts):
                c = t.count(old)
                if not c:
                    continue
                assert old not in new
                texts[i] = t.replace(old, new)
                got += c
                changed += 1
        print(f"{old}->{new}: {got} (expect {expect})")
        assert got in (0, expect), (old, got)
    print("total paragraph edits:", changed)
    if apply:
        for name, d in docs.items():
            dump(os.path.join(FINAL, name + ".json"), d)
    print("done")


if __name__ == "__main__":
    main("--apply" in sys.argv)
    ast.parse(open(__file__, encoding="utf-8").read())