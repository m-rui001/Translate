# -*- coding: utf-8 -*-
"""《鼠疫》润色收尾之三：段末悬逗号改句号（6 处，均为分片切点残留）。"""
import ast, os, shutil

OUT = r"E:/Translate/work_camus/out"
FIX = [
    ("c010", "红光闪烁的火葬堆，", "红光闪烁的火葬堆。"),
    ("c057", "孩子渐渐放松下来，", "孩子渐渐放松下来。"),
    ("c065", "太阳在地平线上落下，", "太阳在地平线上落下。"),
    ("c075", "让附近一家餐馆把饭送上来。只有晚上，", "让附近一家餐馆把饭送上来。只有晚上。"),
    ("c076", "塔鲁直挺挺地躺着，沉重的脑袋压陷了长枕，", "塔鲁直挺挺地躺着，沉重的脑袋压陷了长枕。"),
    ("c082", "里厄和格朗能看得很远，", "里厄和格朗能看得很远。"),
]
n = 0
for chunk, old, new in FIX:
    p = os.path.join(OUT, chunk, "final.txt")
    bak = p + ".bak_20261125"
    if not os.path.exists(bak):
        shutil.copy2(p, bak)
    with open(p, encoding="utf-8", newline="") as fh:
        t = fh.read()
    assert old in t and t.count(old) == 1, (chunk, old)
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(t.replace(old, new))
    n += 1
print("applied", n)
ast.parse(open(__file__, encoding="utf-8").read())
