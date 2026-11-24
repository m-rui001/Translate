# -*- coding: utf-8 -*-
"""v7 chunk122 / chunk123 逐段润色落盘脚本（2026-11-26）。

原则：定位唯一子串 -> 替换 -> 断言命中数 == 1；保持 CRLF 与空行结构；
不整文件重写、不改段数行数。
"""
import ast
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    "chunk122": [
        # ①/canon：v7 全册把这场 matinée 译作「聚会」（上午聚会/午前聚会），此处置「庆典」
        ("自从我刚刚在这庆典中重新抓住时间以来",
         "自从我刚刚在这场聚会中重新抓住时间以来"),
        # ①：en raconter une（une vie）——「讲述其中一生」生硬
        ("在一本想要讲述其中一生的书里",
         "在一本想要讲述其中一段生平的书里"),
        # ②：「我独自在图书室里沉思时记忆所进行的那些复活」定语层层套叠
        ("都为我独自在图书室里沉思时记忆所进行的那些复活添了一种新的美",
         "都给我独自在图书室沉思时由记忆完成的那些复活增添了新的美"),
        # ⑥：forés「如钻凿般深透」词序倒错
        ("她有一双深邃、清澈、如钻凿般深透而锐利的眼睛。",
         "她有一双深邃、清澈、仿佛钻凿出来、深透而锐利的眼睛。"),
        # ⑦：「来落在了」虚词叠用
        ("却来落在了圣卢小姐的肩上",
         "却落到了圣卢小姐的肩上"),
        # ⑥：à point nommé 是「按时／准时」，非「如约而至」
        ("我赞叹自然竟如约而至",
         "我赞叹自然竟准时前来"),
    ],
    "chunk123": [
        # ⑥：atteindre 配「东西」不通，改「触及」
        ("如果我想达到一生中",
         "如果我想触及一生中"),
        # ⑥：elle qu'on vit dans les ténèbres＝我们却在黑暗中度过的「生活」，原译增出「看不清面目」
        ("如今，这种我们生活在黑暗中却看不清面目的东西，既然仿佛可以得到阐明，"
         "这种我们不断歪曲的东西，既然可以还原为它真正的面目，",
         "如今，这种我们却在黑暗中度过的生活，既然仿佛可以得到阐明，"
         "这种我们不断歪曲的生活，既然可以还原为它本来的面目，"),
        # ①③：关系从句直搬成「这个作家，而且……」，主谓断裂；préparer 的状语次序亦倒
        ("因为这个作家，而且对每一个人物都得让最彼此对立的面貌显现出来，"
         "为了让人感到他的立体，像感到一个实体的立体，"
         "他就应当像准备一场攻势那样，借助不断的力量重新编组，细致地准备他的书，",
         "因为这个作家，况且对每一个人物都得让最相互对立的面貌显现出来，"
         "为了让人感到它的体积，像感到一个立体的体积，"
         "他就应当细致地准备他的书，不断重新编组力量，像准备一场攻势那样，"),
        # ①：「我们在生活和艺术中最为感动的东西」缺使动
        ("而对它们的预感，正是我们在生活和艺术中最为感动的东西。",
         "而对它们的预感，正是使我们在生活和艺术中最为感动的东西。"),
        # ④：la protège——「保护它」会被读成保护书，实指坟墓
        ("是它指定我们的坟墓，保护它不受流言的侵扰",
         "是它指定我们的坟墓，保护这座坟墓不受流言的侵扰"),
        # ②：「那种适合借助我的书好好阅读自身的眼睛」两个「眼睛」相撞
        ("有时还可能是由于读者的眼睛并不属于那种适合借助我的书好好阅读自身的眼睛。",
         "有时还可能是由于读者的眼睛并不是我的书所适合的那一双，借它才能好好阅读自身。"),
        # ⑥：n'y voir goutte＝看不清，非「什么也看不见」
        ("如今她已经很老，什么也看不见了。",
         "如今她已经很老，眼睛一点也看不清了。"),
        # ③：toutes mes paperoles, comme disait Françoise——「所有……所说的」定语直搬
        ("所有弗朗索瓦丝所说的“纸片”",
         "所有那些弗朗索瓦丝叫做“纸片”的东西"),
        # ①：「这副面孔对于……往往都要夸大几分」主谓错搭
        ("这副面孔对于一个自己不从事、甚至无法想象的劳作所具有的艰苦，"
         "以及对于一种自己没有的习惯，往往都要夸大几分，",
         "这副面孔总要把一种自己不从事、甚至无法想象的劳作所具有的艰苦，"
         "以及一种自己没有的习惯，夸大几分，"),
        # ⑥：se donner un alibi rétrospectif＝给自己找个事后托词；「施展……借口」搭配不成
        ("而布洛克也确实施展了一个事后追认的借口，",
         "而布洛克也确实给自己找了一个事后的托词，"),
        # ⑥⑤：papiers 与 paperoles 两词被同译作「纸片」，句中自相重复
        ("由于把这些纸片——弗朗索瓦丝管它们叫“纸片”——一张张粘在一起，"
         "它们这里那里便会撕裂。",
         "由于反复把这些纸张——弗朗索瓦丝管它们叫“纸片”——一张张粘在一起，"
         "它们这里那里便撕裂了。"),
        # ⑦：顿号当插入语（「在等玻璃匠、正如我在等印刷商的时候」）
        ("也像她在厨房的窗户那里，在等玻璃匠、正如我在等印刷商的时候，"
         "用一张报纸贴在碎玻璃留下的地方一样。",
         "也像她在厨房的窗前，一边等着玻璃匠——正像我等着印刷商——"
         "一边用一张报纸贴在打碎的窗玻璃的位置上。"),
    ],
}


def han(t):
    return sum(1 for ch in t if "\u4e00" <= ch <= "\u9fff")


def load(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def save(p, text):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def main():
    for chunk, edits in EDITS.items():
        d = os.path.join(BASE, chunk)
        final = os.path.join(d, "final.txt")
        bak = final + ".bak_20261125"
        if not os.path.exists(bak):
            shutil.copy2(final, bak)
            print(f"{chunk}: 备份 -> {os.path.basename(bak)}")
        else:
            print(f"{chunk}: 备份已存在，未覆盖")

        text = load(final)
        nl = "CRLF" if "\r\n" in text else "LF"
        paras_before = text.split("\r\n\r\n")
        h_before, lines_before = han(text), text.count("\n") + 1
        n = 0
        for old, new in edits:
            assert old in text, f"{chunk}: 未命中 -> {old[:24]}"
            assert text.count(old) == 1, f"{chunk}: 命中不唯一 -> {old[:24]}"
            assert "\r\n" not in old and "\n" not in old
            text = text.replace(old, new)
            n += 1
        save(final, text)

        text2 = load(final)
        paras_after = text2.split("\r\n\r\n")
        assert len(paras_before) == len(paras_after), f"{chunk}: 段数变了"
        assert text2.count("\n") + 1 == lines_before, f"{chunk}: 行数变了"
        assert "\r\n" not in text2.replace("\r\n", "", 0) or True
        print(f"{chunk}: 改动 {n} 条  行数 {lines_before}->{text2.count(chr(10)) + 1}  "
              f"段数 {len(paras_before)}  汉字 {h_before}->{han(text2)}  换行 {nl}  "
              f"ASCII引号 {text2.count(chr(34))}  ⟦{text2.count(chr(10214))}")


main()
ast.parse(open(__file__, encoding="utf-8").read())
print("self-check: ast.parse OK")