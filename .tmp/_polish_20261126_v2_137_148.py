#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""逐段润色：追忆似水年华 卷二 out_ind/v2 chunk137 / 138 / 147 / 148（2026-11-26 轮）。

体例：只允许「定位唯一子串 → 替换 → 断言命中数 == 1」，段数/行数/空行结构不变。
法文源：work_proust/chunks/v2/chunks.json（键 "137"/"138"/"147"/"148"）。
"""
import ast
import io
import os
import shutil

BAK = "final.txt.bak_20261125"

EDITS = {
    "chunk137": [
        # ⑤专名：「Sainte Vierge」全库 125 作「圣母」，此处「圣处女」为孤例；
        # ①读不通：「更早的话」不成词（plus anciennement encore）
        ("更早的话还算上圣处女",
         "再往上推，还算上圣母"),
        # ③外语句法：法语插入语（assez mince d'ailleurs）被照搬成破折号，
        # 正插在「那一份……」与它的同位语之间，把宾语隔断；改为先出中心语、插入语收尾
        ("在自己的感情里划出那一份——其实很微薄——可能来自我犹太出身的部分。",
         "在自己的感情里，把可能来自我犹太出身的那一份划出来——其实很微薄。"),
        # ①读不通：分号后「而」是法语 et 的机械承接，转折实为「只不过」
        ("；而这份真话，他同时又顺势大大地打了折扣",
         "；只是这份真话，他同时又顺势大大地打了折扣"),
    ],
    "chunk138": [
        # ①读不通：「在我说来」不通（pour moi = 若换作我），且「会被」与时态不合
        ("这心愿是我培养起来的，在我说来，它会被布洛克看作最可憎的势利",
         "这心愿是我一手培养起来的；可要是搁在我身上，布洛克就会把它看作最可憎的势利"),
        # ①读不通：「布洛克先生做父亲的」是 M. Bloch, le père 的直搬，中文不成短语
        ("只有布洛克先生做父亲的懂得摆弄它，或者说，至少有权摆弄它。",
         "懂得摆弄它的，只有布洛克先生这位做父亲的；或者说，至少他有权摆弄它。"),
        # ⑥硬伤：les jours où il y avait gala et domestiques mâles en extra —— 「添男仆」是
        # 「设盛大宴会」同一日的条件，不是另起一事；原译读成两件事
        ("再说他也难得动用，只在用得着的时候，赶上设盛大宴会的日子，还额外添了男仆。",
         "再说他也难得动用，只在用得着的时候才用，也就是设盛大宴会、额外添了男仆的日子。"),
        # ①读不通：si + 条件式（si les vues avaient été prises...）被译成「即便」，
        # 让步从句没有主句承接，句子悬空
        ("这威望不可能更大，即便那些景片是布洛克先生亲手拍摄、机器由他本人发明。",
         "这威望不可能更大：即便那些景片是布洛克先生亲手拍摄、机器由他本人发明，也不会更大。"),
        # ①读不通：「电报局在那儿」是口语插句，动作（送电报送去）被拆散丢失
        ("甚至托我到安卡维尔去一趟，电报局在那儿，他要每天给情妇发一封电报。",
         "甚至托我跑一趟安卡维尔——电报局设在那里——把他每天发给情妇的那封电报送去。"),
        # ⑥硬伤：cabinet du Vatican 指梵蒂冈的珍藏/陈列之所，非「教廷内阁」（内阁误作 cabinet 的
        # 现代政治义）；上文正以 médaillier、pinacothèque 为喻
        ("从梵蒂冈的教廷内阁一代代传到",
         "从梵蒂冈的珍藏室一代代传到"),
        # ①读不通：「语法威严的立法者」定语错位（les augustes législatrices des grammaires）
        ("这些肢解后来成了语法威严的立法者",
         "这些肢解后来成了语法的威严立法者"),
        # ⑤专名：les trois Grâces 通译「美惠三女神」，「三美惠」词序不成词（全库仅此一处）
        ("所以人们管他们叫“三美惠”",
         "所以人们管他们叫“美惠三女神”"),
    ],
    "chunk147": [
        # ⑥硬伤：non sans répéter deux ou trois fois le dernier mot —— 是「边笑边重复」，非「笑完之后」
        ("——因为这位老先生笑完之后，总要把最后那个词重复两三遍",
         "——因为这位老先生每笑一声，总不忘把最后那个词重复两三遍"),
        # ⑥硬伤：qu'il valait la peine d'éblouir —— éblouir 是「镇住/使之目眩」，「为之一震」把
        # 施受关系读反（是父亲去震客人，不是客人自震）
        ("那种日子，是小布洛克领回一个值得为之一震的人来的日子",
         "那种日子，是小布洛克领回一个值得抖出本事去震一震的客人来的日子"),
        # ①读不通：「仿佛那是非说不可的，聪明人只该用这种话」并列项残缺
        ("仿佛那是非说不可的，聪明人只该用这种话",
         "仿佛那是非说不可的语言，聪明人只能用它"),
        # ①读不通：ce chichi-là 是「扭捏作态」，「这小题大做的是什么呀」不成句
        ("这小题大做的是什么呀？",
         "这装腔作势算怎么回事？"),
        # ①读不通：「反而增添」缺宾语
        ("不确切、不在行，非但不减自信，反而增添。",
         "不确切、不在行，非但不减自信，反而增添自信。"),
        # ①读不通：连用两个「而」，第二个「而这就足够」读断
        ("可人们这么说，并非只是耍手腕，而是因为真有这种感觉，而这就足够取消那段距离",
         "可人们这么说，并非只是耍手腕，而是因为真有这种感觉，单凭这一点就够取消那段距离"),
    ],
    "chunk148": [
        # ⑤专名：d'Aumale 全库 10:7，out_ind/v2 邻章 chunk149 亦作「奥马尔公爵」
        ("假奥马勒公爵",
         "假奥马尔公爵"),
        # ①读不通：「最近的亲属圈子」定语悬空（la famille la plus proche = 最亲近的家人）
        ("在最近的亲属圈子里，大家跟他相处得格外愉快",
         "在最亲近的亲属圈子里，大家跟他相处得格外愉快"),
    ],
}

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = []

for name, pairs in EDITS.items():
    path = os.path.join(HERE, name, "final.txt")
    bak = os.path.join(HERE, name, BAK)
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    before = (text.count("\n") + 1, sum(1 for c in text if "\u4e00" <= c <= "\u9fff"))
    done = 0
    for old, new in pairs:
        if old not in text:                      # 幂等：该条已落盘
            assert text.count(new) >= 1, (name, "LOST", old[:20])
            continue
        assert text.count(old) == 1, (name, "NOT UNIQUE", old[:20])
        text = text.replace(old, new)
        done += 1
    assert text.count("\n") + 1 == before[0], (name, "LINE COUNT CHANGED")
    after = (text.count("\n") + 1, sum(1 for c in text if "\u4e00" <= c <= "\u9fff"))
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    REPORT.append((name, done, before, after, "CRLF" if "\r\n" in text else "LF"))

for name, done, before, after, nl in REPORT:
    print("%s: %d 处 | 行 %d->%d | 汉字 %d->%d | %s"
          % (name, done, before[0], after[0], before[1], after[1], nl))
print("TOTAL", sum(r[1] for r in REPORT))

ast.parse(io.open(os.path.abspath(__file__), encoding="utf-8").read())
print("ast.parse ok")