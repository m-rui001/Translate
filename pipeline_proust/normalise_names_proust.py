"""Deterministic name/terminology normalisation for the Proust supplement.

Zhou Kexi's own renderings are canonical for anything he translated; for names
that only appear in volumes 3/4/6/7 we fix one form and enforce it everywhere.
Longer variants are applied first so '维尔帕里西斯夫人' is never half-replaced.
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import sys

OUT = "E:/Translate/work_proust/out"

# variant -> canonical (longest first)
NAMES = {
    # --- people -------------------------------------------------------------
    "盖尔芒特-巴维埃尔": "盖尔芒特-巴伐利亚",
    "盖尔芒特-巴伐利": "盖尔芒特-巴伐利亚",
    "维尔帕里西西斯夫人": "维尔帕里西斯夫人",
    "维尔帕里西西斯": "维尔帕里西斯",
    "诺波瓦": "诺普瓦",
    "费代尔纳夫人": "费泰尔讷夫人",
    "费代尔纳": "费泰尔讷",
    "费特尔纳": "费泰尔讷",
    "费特尔纳夫人": "费泰尔讷夫人",
    "费泰纳": "费泰尔讷",
    "费泰纳夫人": "费泰尔讷夫人",
    "费特恩": "费泰尔讷",
    "费特恩夫人": "费泰尔讷夫人",
    "康芒贝尔": "康布雷梅",
    "康芒贝尔夫人": "康布雷梅夫人",
    "斯泰尔玛丽亚小姐": "斯泰尔玛丽亚夫人",
    "斯泰尔玛丽亚小姐": "斯泰尔玛丽亚夫人",
    "斯台尔玛丽亚": "斯泰尔玛丽亚",
    "斯泰尔马里亚": "斯泰尔玛丽亚",
    "科塔尔医生": "科塔尔",
    "科塔尔教授": "科塔尔",
    "科塔尔大夫": "科塔尔",
    "普鲁斯特": "普鲁斯特",
    "弗朗索瓦丝": "弗朗索瓦丝",
    "弗朗索瓦": "弗朗索瓦丝",
    "阿尔让库尔": "阿尔让库尔",
    "马桑特": "马桑特",
    "吉尔贝特": "吉尔贝特",
    "吉尔贝特·": "吉尔贝特·",
    "维尔迪兰": "韦尔迪兰",
    "维尔迪兰夫人": "韦尔迪兰夫人",
    "维尔迪兰夫妇": "韦尔迪兰夫妇",
    "夏吕斯": "夏尔吕",
    "夏吕斯先生": "德·夏尔吕先生",
    "德夏尔吕": "德·夏尔吕",
    "格里菲尼": "格里菲尼",
    "格雷戈瓦": "格雷戈瓦",
    "盖尔芒特亲王": "盖尔芒特亲王",
    "盖尔芒特公爵夫人": "盖尔芒特公爵夫人",
    "盖尔芒特公爵": "盖尔芒特公爵",
    "布洛什": "布洛克",
    "布洛赫": "布洛克",
    "贝格特": "贝戈特",
    "贝尔戈特": "贝戈特",
    "圣卢伯爵": "圣卢伯爵",
    "圣卢的": "圣卢的",
    "埃勒斯蒂尔": "埃尔斯蒂尔",
    "艾尔斯蒂尔": "埃尔斯蒂尔",
    "帕尔马公主": "帕尔马亲王夫人",
    "帕尔马的": "帕尔马的",
    "维尔帕里西斯侯爵夫人": "维尔帕里西斯夫人",
    "邦当夫人": "邦唐夫人",
    "邦当": "邦唐",
    "奥丽亚娜": "奥里亚娜",
    "朱皮安": "絮比安",
    "若尔热特": "若尔热特",
    "斯万夫人": "斯万夫人",
    "奥黛特": "奥黛特",
    "贡布雷": "贡布雷",
    "巴尔贝克": "巴尔贝克",
    "当松维尔": "当松维尔",
    "唐松维尔": "当松维尔",
    "勒卡特莱": "勒卡特莱",
    "蒙茹万": "蒙茹万",
    "拉斯普利埃": "拉斯普利埃",
    "里夫贝尔": "里夫贝尔",
    "当西埃尔": "当西埃尔",
    "韦里耶尔": "韦里耶尔",
    "伊利耶": "伊利耶",
    "埃特尔塔": "埃特尔塔",
    "特鲁维尔": "特鲁维尔",
    "米乌斯": "米乌斯",
    # --- terms --------------------------------------------------------------
    "玛德莱娜小蛋糕": "玛德莱娜小蛋糕",
    "马德莱娜": "玛德莱娜",
    "小乐句": "小乐句",
    "非自主记忆": "非自主记忆",
    "无意记忆": "非自主记忆",
}

# apply longest first
_KEYS = sorted(NAMES, key=len, reverse=True)


def normalise_text(text: str) -> str:
    for k in _KEYS:
        v = NAMES[k]
        if k != v:
            text = text.replace(k, v)
    return text


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    touched = 0
    for f in sorted(glob.glob(os.path.join(OUT, "*", "chunk*", "final.txt"))):
        raw = io.open(f, encoding="utf-8").read()
        new = normalise_text(raw)
        if new != raw:
            io.open(f, "w", encoding="utf-8").write(new)
            touched += 1
    print(f"normalised {touched} chunks")
    # report what is still inconsistent
    left = {}
    for f in glob.glob(os.path.join(OUT, "*", "chunk*", "final.txt")):
        t = io.open(f, encoding="utf-8").read()
        for k in NAMES:
            if NAMES[k] != k and k in t:
                left[k] = left.get(k, 0) + t.count(k)
    print("still present:", left if left else "none")


if __name__ == "__main__":
    main()
