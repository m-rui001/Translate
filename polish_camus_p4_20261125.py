# -*- coding: utf-8 -*-
"""《鼠疫》润色收尾之二：长引文（塔鲁笔记、帕纳卢讲道、塔鲁自述）逐段收口。

本册把长段引语排成「每段起“、整块末尾收”」的法国式体例，但多数段落的收口符在转写中丢失，
读者无从判断一段话说到哪里。此处对 34 个「段末已有句末标点、且只差一个后引号」的段落补上
后引号；另有 6 段以冒号、单引号结尾或句子未竟，确属跨段续引，一律不动。
"""
import ast, glob, os, shutil

OUT = r"E:/Translate/work_camus/out"
BAK = ".bak_20261125"
END = "。！？…"

changed = []
for f in sorted(glob.glob(os.path.join(OUT, "c*", "final.txt"))):
    with open(f, encoding="utf-8", newline="") as fh:
        text = fh.read()
    ps = text.split("\n\n")
    hit = 0
    for i, p in enumerate(ps):
        if p.count("“") - p.count("”") == 1 and p and p[-1] in END:
            ps[i] = p + "”"
            hit += 1
    if hit:
        bak = f + BAK
        if not os.path.exists(bak):
            shutil.copy2(f, bak)
        with open(f, "w", encoding="utf-8", newline="") as fh:
            fh.write("\n\n".join(ps))
        changed.append((os.path.basename(os.path.dirname(f)), hit))

print(sum(h for _, h in changed), changed)
ast.parse(open(__file__, encoding="utf-8").read())
