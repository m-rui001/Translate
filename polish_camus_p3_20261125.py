# -*- coding: utf-8 -*-
"""《鼠疫》润色收尾：引号成对（3 处硬伤）＋ 段内嵌套引号改单引号。"""
import ast, os, shutil

OUT = r"E:/Translate/work_camus/out"
BAK = ".bak_20261125"

FIXES = [
    ("c002", "“等你回来，一切都会好的。我们重新开始。””",
     "“等你回来，一切都会好的。我们重新开始。”", "⑦", "上一轮补引号时重复加了一个后引号"),
    ("c017", "封闭城市。”", "“封闭城市。”", "⑦", "题词段只剩后引号，无前引号"),
    ("c052", "这种满足可以表达为一句：“你们尽管说吧，我比你们先经历过。”",
     "这种满足可以表达为一句：‘你们尽管说吧，我比你们先经历过。’", "⑦",
     "外层引文未收口，内层引语应改用单引号"),
    ("c083", "别人说：“这是鼠疫，我们得过鼠疫。”差一点",
     "别人说：‘这是鼠疫，我们得过鼠疫。’差一点", "⑦", "对白内嵌套引语改用单引号"),
    ("c083", "可鼠疫究竟是什么意思？那就是生活，如此而已。",
     "可鼠疫究竟是什么意思？那就是生活，如此而已。”", "⑦", "老人这段话缺后引号"),
]

n = 0
for chunk, old, new, tag, why in FIXES:
    path = os.path.join(OUT, chunk, "final.txt")
    bak = path + BAK
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    assert old in text, (chunk, old[:24])
    assert text.count(old) == 1, (chunk, text.count(old), old[:24])
    text = text.replace(old, new)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    n += 1
print("applied", n)
ast.parse(open(__file__, encoding="utf-8").read())