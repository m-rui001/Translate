"""Curated name/term unification.

Automatic extraction proposes far too many false pairs (Cape -> 科德角/好望角,
Isaiah -> 以赛亚/以赛亚书), so the maps below are hand-checked against the text
and the published conventions. Each entry is (wrong form, right form); the
right form must be the form the book already uses in the majority of places.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

MAPS = {
    "whale": [
        # units and craft terms the reader flagged
        ("数浪", "数英寻"),
        ("浔", "英寻"),
        ("英尺", "呎"),
        ("英寸", "吋"),
        ("箱索", "箱中线"),
        ("托处", "托座"),
        ("笨座板", "抵膝木"),
        ("抹香鲸捕捞业", "抹香鲸渔业"),
        ("新贝德福德", "新贝德福"),
        ("比勒达", "比尔达"),
        ("特兰克岛", "特兰克"),
        ("盖伊岬", "盖伊角"),
    ],
    "soledad": [
        ("何塞·劳尔·蒙卡达", "何塞·拉克尔·蒙卡达"),
        ("何塞·拉凯尔·蒙卡达", "何塞·拉克尔·蒙卡达"),
        ("罗克·卡尼塞罗", "罗克·卡尔尼塞罗"),
        ("隐形医生", "看不见的医生"),
        ("处处地地", "处处"),
        ("试验性幽闭", "关起门来做试验"),
    ],
    # LOTR: unify to the form the delivered text already uses in the great
    # majority of places, so the book keeps its own naming school (it follows
    # 朱学恒 for most names: 佛罗多/勒苟拉斯/金雳/迪耐瑟/努曼诺尔). Only the
    # strays are rewritten. Two exceptions where the majority form is itself the
    # error: 阿蒙罗 (Amon Lhaw is 阿蒙劳) and 埃奥蒙德 (Éomund, beside 伊欧墨).
    "lotr": [
        ("弗罗多", "佛罗多"),
        ("甘吉", "甘姆吉"),
        ("阿蒙罗", "阿蒙劳"),
        ("伊奥梅尔", "伊欧墨"),
        ("伊奥温", "伊欧玟"),
        ("埃奥蒙德", "伊欧蒙德"),
        ("塞格尔", "森格尔"),
        ("赫鲁因", "希鲁因"),
        ("阿尔雯", "阿尔温"),
        ("埃罗希尔", "埃洛希尔"),
        ("洛比莉亚", "罗贝拉"),
        ("白兰地鹿", "烈酒鹿"),
        ("雄鹿地", "烈酒鹿地"),
        ("白兰地河", "烈酒河"),
        ("水边镇", "傍水镇"),
        ("努门诺尔", "努曼诺尔"),
        ("阿那瑞安", "阿纳瑞安"),
        ("凯勒布林博", "凯勒布理鹏"),
        ("费艾诺", "费诺"),
        ("辛葛", "庭葛"),
        ("莱戈拉斯", "勒苟拉斯"),
        ("吉姆利", "金雳"),
        ("德内梭尔", "迪耐瑟"),
        ("法拉米尔", "法拉墨"),
        ("小胖", "胖墩"),
        ("乌骨陆", "乌格鲁克"),
        # holbytla is not a caveman: it is Old English for "hole-builder"
        ("穴居人老爷", "掘洞者"),
    ],
}


def apply(book: str, dry: bool = False) -> None:
    rules = sorted(MAPS[book], key=lambda r: -len(r[0]))
    total = 0
    rows = []
    d = os.path.join(common.WORK, book, "ch")
    for fn in sorted(os.listdir(d)):
        p = os.path.join(d, fn)
        ch = common.load_json(p)
        hit = 0
        if "paras" in ch:
            for item in ch["paras"]:
                t = item["zh"]
                for a, b in rules:
                    if a in t:
                        hit += t.count(a)
                        t = t.replace(a, b)
                item["zh"] = t
        for key in ("zh",):
            if key in ch:
                for i, t in enumerate(ch[key]):
                    for a, b in rules:
                        if a in t:
                            hit += t.count(a)
                            t = t.replace(a, b)
                    ch[key][i] = t
        if hit:
            rows.append((ch["id"], hit))
            total += hit
            if not dry:
                common.save_json(p, ch)
    print(f"{book}: {len(rules)} rules, {total} replacements in {len(rows)} chapters"
          + (" (dry)" if dry else ""))
    for cid, n in rows[:40]:
        print("   ", cid, n)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, choices=list(MAPS))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    apply(a.book, dry=not a.apply)
