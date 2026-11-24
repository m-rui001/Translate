# -*- coding: utf-8 -*-
"""逐段润色 v3 chunk069-073（2026-11-26 轮）。

只做「定位唯一子串 → 替换 → 断言命中数 == 1」的改法，不整文件重写。
读写统一 open(..., encoding='utf-8', newline='')，保持原换行符与空行结构。
"""
import ast
import os
import re
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    "chunk069": [
        # ① 外语句法直搬「faire suivre X de Y」被搬成「让 X，紧接着 Y」，动宾关系断裂
        ("是圣卢怎么能让那些品评几分客气的话，紧接着一个完全不是从这些话里生出来的动作",
         "是圣卢怎么能让那些品评几分客气的话后面紧跟着一个完全不是从这些话里生出来的动作"),
        # ⑦ 引号切在「这」与「伙人」之间，"这“伙人”"读起来断气
        ("这“伙人”的胆大妄为", "这“一伙人”的胆大妄为"),
        # ③ comme je l'avais cru 插入语直搬，成了「同我原先以为的……毫无关系」，修饰关系歧义
        ("这件事，同我原先以为的剧院里的耳光毫无关系。",
         "这件事并不像我原先以为的那样，与剧院里的耳光有关。"),
        # ① "劈下手来" 动补错位
        ("便猛地劈下手来，一记响亮的耳光", "便猛地把手劈下来，一记响亮的耳光"),
    ],
    "chunk070": [
        # ④ 段内「它」上承「那一代」，紧接又承「性格」，指代易错认
        ("代替它原有的性格的，是一种感受力和一种智慧", "代替那一代原有的性格的，是一种感受力和一种智慧"),
    ],
    "chunk071": [
        # ① "她还带着一种执意" 悬空成句（原是把 avec une insistance 的状语拆成了并列小句）
        ("她不得不一而再再而三地向他发出请帖，而他无法领会其价值，她还带着一种执意，这执意渐渐使她在势利眼们眼中掉了价",
         "她不得不带着一种执意，一再向他发出请帖——而他根本领会不了这些请帖的价值——这执意渐渐使她在势利眼们眼中掉了价"),
        # ⑥ 漏字：无所事 → 无所事事
        ("孤立、无所事的生活", "孤立、无所事事的生活"),
        # ① "把……困为囚徒" 搭配不成词（retenir prisonnier）
        ("那把他困为囚徒的网", "那把他囚住的网"),
        # ① "不极其看重" 副词搭配生硬，双重否定读来绊口
        ("维尔帕里西夫人不极其看重自己的地位", "维尔帕里西夫人没有极其看重自己的地位"),
    ],
    "chunk072": [
        # ⑥ 词义误读：porter un gant ... à la main 是「手里拿着一只手套」，被读成戴在手上，
        #   并凭空补出「另一只手拿着东西」
        ("穿着长礼服，一只手戴着手套，另一只手拿着东西，像一卷纸莎草纸",
         "穿着长礼服，手里拿着一只手套，像拿着一卷纸莎草纸"),
    ],
    "chunk073": [
        # ⑤ Molé 全册 canon「莫莱」（8 次；v3 chunk081 同一段轶事作「莫莱先生的帽子」）
        ("穆莱先生我记得很清楚", "莫莱先生我记得很清楚"),
        ("这不过是穆莱先生的一个习惯", "这不过是莫莱先生的一个习惯"),
        # ⑤ Vigny 全册 canon「德·维尼」
        ("欢迎维尼先生", "欢迎德·维尼先生"),
        # ⑤/⑦ 原著并无书名，且 v3 chunk081 同一人物作「投石党历史学家」
        ("皮埃尔先生，《投石党史》的历史学家，犹犹豫豫地说",
         "皮埃尔先生，那位投石党历史学家，犹犹豫豫地说"),
        # ⑤ cheveux de Vénus 全册 canon「铁线蕨」（chunk072 同一种花）；④「画它」指代不明
        ("那个浸着维纳斯头发的玻璃杯移近一些，她过一会儿就要重新拿起笔来画它",
         "那个插着铁线蕨的玻璃杯移近一些，过一会儿她就要接着画这些花"),
    ],
}

CATS = {
    "chunk069": ["③", "⑦", "③", "①"],
    "chunk070": ["④"],
    "chunk071": ["①", "⑥", "①", "①"],
    "chunk072": ["⑥"],
    "chunk073": ["⑤", "⑤", "⑤", "⑤", "⑤"],
}


def han(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def main():
    report = []
    for chunk, edits in EDITS.items():
        d = os.path.join(BASE, chunk)
        path = os.path.join(d, "final.txt")
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        nl = "\r\n" if "\r\n" in text else "\n"
        before_lines = text.count("\n")
        before_han = han(text)
        before_nonblank = len([l for l in text.replace("\r\n", "\n").split("\n") if l.strip()])

        bak = path + ".bak_20261125"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)

        n = 0
        for old, new in edits:
            assert old in text, "MISS %s: %r" % (chunk, old)
            assert text.count(old) == 1, "NOT UNIQUE %s: %r (%d)" % (chunk, old, text.count(old))
            text = text.replace(old, new, 1)
            n += 1

        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)

        # 复核：读回落盘结果
        with open(path, encoding="utf-8", newline="") as f:
            back = f.read()
        assert back == text, "WRITE MISMATCH %s" % chunk
        after_lines = back.count("\n")
        after_han = han(back)
        after_nonblank = len([l for l in back.replace("\r\n", "\n").split("\n") if l.strip()])
        assert before_lines == after_lines, "LINE COUNT CHANGED %s" % chunk
        assert before_nonblank == after_nonblank, "PARA COUNT CHANGED %s" % chunk
        assert "\n\n\n" not in back.replace("\r\n", "\n"), "BLANK STRUCTURE %s" % chunk
        assert "\"" not in back and "'" not in back, "ASCII QUOTE %s" % chunk
        assert "⟦" not in back and "⟧" not in back, "ITALIC MARK %s" % chunk

        report.append((chunk, before_lines, after_lines, before_han, after_han,
                       before_nonblank, n, repr(nl)))

    print("chunk    lines(before->after)  han(before->after)  paras  edits  newline")
    for r in report:
        print("%-8s %4d -> %-4d          %5d -> %-5d    %3d     %2d    %s" % r)
    total = sum(r[6] for r in report)
    print("total edits:", total)
    cnt = {}
    for chunk, cats in CATS.items():
        assert len(cats) == len(EDITS[chunk]), chunk
        for c in cats:
            cnt[c] = cnt.get(c, 0) + 1
    print("by category:", " ".join("%s=%d" % (k, cnt[k]) for k in sorted(cnt)))


main()
ast.parse(open(__file__, encoding="utf-8").read())
print("AST self-check OK")