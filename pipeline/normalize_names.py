"""Deterministic normalization of established Tolkien names in the Chinese text.

The drafting models drift between transliterations (吉米利/金雳, 弗罗多/佛罗多 …).
This pass re-imposes one canonical set so the whole book reads consistently, and
is idempotent so it can be run repeatedly on finished chapters.
"""
from __future__ import annotations

import glob
import os
import re
import sys

# wrong/variant -> canonical
VARIANTS = {
    # hobbits
    "弗罗多": "佛罗多",
    "弗罗多·": "佛罗多·",
    "梅里雅达克": "梅里雅达克",
    "山姆怀斯": "山姆怀斯",
    # company
    "吉米利": "金雳", "吉姆利": "金雳", "金雳·": "金雳·",
    "格洛芬德尔": "葛罗芬戴尔", "格罗芬德尔": "葛罗芬戴尔", "格罗芬戴尔": "葛罗芬戴尔",
    "格洛因": "葛罗音", "格罗因": "葛罗音",
    "莱戈拉斯": "勒苟拉斯",
    "波洛米尔": "波罗莫", "博罗米尔": "波罗莫",
    "阿拉冈": "阿拉贡", "亚拉冈": "阿拉贡",
    "爱隆": "埃尔隆德", "艾隆": "埃尔隆德",
    "加拉德瑞尔": "凯兰崔尔", "凯兰崔尔女王": "凯兰崔尔",
    "凯勒布林博": "凯勒布理鹏",
    # villains
    "咕噜": "咕鲁", "古鲁姆": "咕鲁", "格鲁姆": "咕鲁",
    "史麦戈": "史麦戈",
    "萨茹曼": "萨鲁曼", "萨鲁曼": "萨鲁曼",
    "奥克": "半兽人", "奥库": "半兽人",
    "乌鲁克族": "强兽人", "乌鲁克": "强兽人",
    # Rohan / Gondor
    "塞奥顿": "希优顿", "赛奥顿": "希优顿",
    "伊奥温": "伊欧玟", "艾欧温": "伊欧玟",
    "伊奥梅尔": "伊欧墨", "艾欧墨": "伊欧墨",
    "德内梭尔": "迪耐瑟", "迪内瑟": "迪耐瑟",
    "法拉米尔": "法拉墨",
    "格里马·沃姆舌": "格里马",
    "贝瑞贡德": "贝尔贡", "贝雷贡": "贝尔贡",
    # places
    "洛丝罗瑞恩": "罗斯洛立安", "洛瑞恩": "罗斯洛立安", "罗瑞安": "罗斯洛立安",
    "艾森加德": "艾辛格", "埃森加德": "艾辛格",
    "摩利亚": "摩瑞亚",
    "米那斯魔窟": "米那斯魔窟",
    "米那斯提力斯": "米那斯提力斯",
    "欧斯吉利亚斯": "奥斯吉力亚斯", "奥斯吉力亚": "奥斯吉力亚斯",
    "海尔姆深谷": "圣盔谷", "圣盔谷": "圣盔谷",
    "帕蓝提尔": "真知晶球", "帕兰提尔": "真知晶球", "真知晶球": "真知晶球",
    "奇立斯乌苟": "西力斯昂哥", "奇立斯昂哥": "西力斯昂哥",
    "希洛布": "尸罗",
    "埃雅仁迪尔": "埃雅仁迪尔",
    "梅隆树": "梅隆树",
    "凯兰崔尔之瓶": "凯兰崔尔之瓶",
    "大步佬": "大步佬", "神行客": "大步佬",
}

# order matters: longer variants first
_KEYS = sorted(VARIANTS, key=len, reverse=True)


def normalize(text: str) -> str:
    for k in _KEYS:
        if k != VARIANTS[k]:
            text = text.replace(k, VARIANTS[k])
    text = re.sub(r"\s+", " ", text) if False else text
    return text


def main(paths):
    touched = 0
    for p in paths:
        raw = open(p, encoding="utf-8").read()
        new = normalize(raw)
        if new != raw:
            open(p, "w", encoding="utf-8").write(new)
            touched += 1
    print(f"normalized {touched}/{len(paths)} files")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    files = []
    for pat in ("E:/Translate/work/out/*/chunk*/final.txt",
                "E:/Translate/work/out/*/chunk*/11_clean.txt"):
        files += glob.glob(pat)
    main(files)
