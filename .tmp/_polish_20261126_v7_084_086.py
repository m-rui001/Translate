# -*- coding: utf-8 -*-
"""逐段润色 v7 chunk084 / chunk086（定位唯一子串替换，绝不整文件重写）。"""
import ast
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))

FIX = {
    "chunk084": [
        # ③ 括注破折号插在「显露出来」与主语谓语之间，割断句子
        ("那么相反，有些男人身上，衰老却因不施脂粉而显露出来——在他们的脸上，"
         "我从未明确注意到衰老——可他们自从对讨人喜欢感到灰心、不再用脂粉以来，我觉得确实变了许多。",
         "那么相反，有些男人身上的衰老却因不施脂粉而显露出来；我从未在他们的脸上明确注意到过衰老，"
         "可自从他们对讨人喜欢感到灰心、不再施脂粉以来，我觉得他们确实变了许多。"),
        # ③ 关系从句被搬成破折号，插在主语「……的消失」与谓语「使」之间
        ("他嘴唇和双颊上那玫瑰色的消失——我从未疑心这玫瑰色是人工的——使他面容显得灰暗，"
         "使他拉长而阴郁的线条具有埃及神祇线条那种雕刻般、碑刻般的精确。",
         "他嘴唇和双颊上的玫瑰色褪去了，我从未疑心过这玫瑰色是人工的；这使他面容显得灰暗，"
         "使他拉长而阴郁的线条具有埃及神祇线条那种雕刻般、碑刻般的精确。"),
        # ⑦ 顿号误用于分句之间
        ("那无足轻重的“亡灵”、而通灵者却仍向它提出",
         "那无足轻重的“亡灵”，而通灵者却仍向它提出"),
        # ① 悬空修饰：「使他……竖起的」主语错置
        ("那些使他双颊和头顶同样竖起的粗硬毛发",
         "那些在他双颊和头顶同样竖起的粗硬毛发"),
    ],
    "chunk086": [
        # ① 「口子间」不成词，entrebâillement 是「半开的缝隙」
        ("仿佛在自己的墓穴半开的口子间",
         "仿佛在自家墓穴半开的缝隙里"),
        # ⑤ 同段 parabole 前译「弧线」此处译「抛物线」，统一为「弧线」
        ("没有什么能抗拒这道抛物线带着她们往前去",
         "没有什么能抗拒这道弧线带着她们往前去"),
        # ① 「显出……眼睑」动宾失配
        ("已经显出那些垂死之人的僵硬和紧闭的眼睑，嘴唇不停地哆嗦",
         "已经显出那些垂死之人的僵硬，眼睑紧闭，嘴唇不停地哆嗦"),
    ],
}


def han(s):
    return sum(1 for c in s if "\u4e00" <= c <= "\u9fff")


def main():
    for name, pairs in FIX.items():
        d = os.path.join(BASE, name)
        p = os.path.join(d, "final.txt")
        bak = os.path.join(d, "final.txt.bak_20261125")
        if not os.path.exists(bak):
            shutil.copy2(p, bak)
        with open(p, encoding="utf-8", newline="") as f:
            text = f.read()
        crlf = "\r\n" in text
        before_lines = len([l for l in text.split("\n") if l.strip()])
        before_han = han(text)
        n = 0
        for old, new in pairs:
            assert text.count(old) == 1, (name, old[:30], text.count(old))
            text = text.replace(old, new)
            n += 1
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        after_lines = len([l for l in text.split("\n") if l.strip()])
        print(f"{name}: 改动 {n} 条 | 行数 {before_lines}->{after_lines} | "
              f"汉字 {before_han}->{han(text)} | 换行符 {'CRLF' if crlf else 'LF'}")
        assert before_lines == after_lines
    print("done")


main()
ast.parse(open(__file__, encoding="utf-8").read())