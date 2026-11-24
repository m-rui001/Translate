# -*- coding: utf-8 -*-
"""v5 chunk115/117/122/125 逐段润色落盘脚本（2026-11-26）。"""
import ast
import os

BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    "chunk117": [
        # ① 宾语悬空：「讨要」无宾语，le demander（求取乐趣）落成动词时需补出
        ("我也会去向陌生的女人讨要",
         "我也会去向陌生的女人寻求"),
        # ③ reçu que j'allais être par la personne 被动直搬，改主动「由…接纳」
        ("因为我马上就要被那个人接过去",
         "因为我马上就要由那个人接纳"),
        # ③ sont chargés de 的字面直搬（「负责歪曲」），招供不「负责」，改「所要」
        ("还没等你弄清它们负责歪曲、开脱的那件实情",
         "还没等你弄清它们所要歪曲、开脱的那件实情"),
    ],
    "chunk122": [
        # ① 「和…所构想的、也与…所描绘的那个都不相同的」并列错位，读不通
        ("一个和我的理智所构想的、也与她自己的话所描绘的那个都不相同的阿尔贝蒂娜",
         "一个与我的理智所构想的不同、也与她自己的话所描绘的那个不同的阿尔贝蒂娜"),
    ],
    "chunk125": [
        # ③ contredites par son idée 被动直搬 + 「即以为」主语不明
        ("会被她那个念头顶回去，即以为",
         "会被她那个念头抵消掉：她以为"),
    ],
}


def cjk(s):
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def main():
    total = 0
    for chunk, edits in EDITS.items():
        path = os.path.join(BASE, chunk, "final.txt")
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        before = text
        lines_before = text.count("\n")
        cjk_before = cjk(text)
        n = 0
        for old, new in edits:
            assert old in text, (chunk, old)
            assert text.count(old) == 1, (chunk, old, text.count(old))
            text = text.replace(old, new)
            n += 1
        assert text.count("\n") == lines_before, chunk
        assert text.count("\r\n") == before.count("\r\n"), chunk
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print(f"{chunk}: 改动 {n} 条  行数 {lines_before}->{text.count(chr(10))}"
              f"  汉字 {cjk_before}->{cjk(text)}"
              f"  换行符 {'CRLF' if chr(13) + chr(10) in text else 'LF'}")
        total += n
    print("合计改动", total, "条")


main()
ast.parse(open(__file__, encoding="utf-8").read())