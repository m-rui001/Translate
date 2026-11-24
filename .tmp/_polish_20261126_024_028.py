# -*- coding: utf-8 -*-
"""v3 chunk024 / chunk025 / chunk028 逐段润色（2026-11-26 轮）

准则：E:/Translate/POLISH_BRIEF_2026-11-25.md（只改七类，不重译、不动情节、不动段数）
canon：E:/Translate/scratch/rev2026/proust_canon_1125.md

落盘方式：定位唯一子串 -> 替换 -> assert text.count(old) == 1，绝不整文件重写。
换行符：newline='' 读写，CRLF/LF 原样保留。
"""
import ast
import io
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# (chunk, 类别, old, new)
EDITS = [
    # ---------------- chunk025 ----------------
    ("025", "③",
     "而那位军官，尽管他始终没有靠近，他仍不慌不忙地抬起手来，朝军帽致意；",
     "而那位军官没有走近，也抬起手来朝着军帽致意，只是不慌不忙；"),
    # l'officier, sans se rapprocher, ... leva, lui aussi, mais sans se hâter, la main vers son képi
    # 独立分词短语 sans se rapprocher 被搬成「尽管……他仍」的让步复句：原意是伴随状态「没有走近」，
    # 无转折可言；且「靠近」不成条件，整句读作两个判断打架。改回并列动作，保留 lui aussi（也）
    # 与 mais sans se hâter（只是不慌不忙）。

    ("025", "①",
     "我走进楼梯，每走一步都差点在钉着铆钉的台阶上滑倒",
     "我走进楼梯间，每走一步都差点在钉着铆钉的台阶上滑倒"),
    # je m'engageai dans l'escalier：escalier 在此是可进入的空间（楼梯间），
    # 「走进楼梯」中文搭配不成句，补「间」即立。

    # ---------------- chunk028 ----------------
    ("028", "⑤",
     "比如一个自由思想家在牧师住宅里吃着一顿精美的晚餐",
     "比如一个自由思想家在本堂神父的住宅里吃着一顿精美的晚餐"),
    # d'un libre penseur faisant un dîner exquis dans un presbytère：presbytère 是天主教本堂神父住宅，
    # 「牧师」为基督教新教称谓，按 BRIEF 二·5（宗教语境不用「牧师」）与全书 canon「本堂神父」归一。

    ("028", "⑥",
     "可不管它醒得多早，我推开窗时看见的，却不像从城堡窗口望出去那样，从池塘那边看，它还裹在柔白如晨衣的雾气里",
     "可不管它醒得多早，我推窗朝池塘那边望去，看见的却一如从城堡窗口望出去：它还裹在柔白如晨衣的雾气里"),
    # Mais de si bonne heure qu'elle fût éveillée, je ne la vis pourtant en ouvrant la croisée,
    # comme on la voit d'une fenêtre de château, du côté de l'étang, qu'emmitouflée encore dans ...
    # 原文是 ne ... que（只见它裹在雾里）＋ comme（正如从城堡窗口望去），译文把 ne...que 读成否定，
    # 写成「却不像……那样」，否定了原本的比喻，语义反转；「从池塘那边看」也悬空无着落。

    ("028", "⑥",
     "但我知道，等院子里照料马匹的士兵刷洗完毕，它就会把那件衣裳脱掉。",
     "但我知道，不等院子里照料马匹的士兵刷洗完毕，它就会把那件衣裳脱掉了。"),
    # avant que les soldats ... eussent fini leur pansage, elle l'aurait dévêtue：
    # avant que ＋ 条件式过去先将来时，是「等不到……就已经」；译文作「等……完毕，它就会」，
    # 时序读反。补「不」「了」把先后关系摆正，句长与结构不变。

    ("028", "①",
     "它像一股令人窒息的芳香，自我出生以来，每一间新房间——也就是说任何房间——都向我散发出这股香气：",
     "它就像自我出生以来每一间新房间——也就是说任何房间——都向我散发出的一股令人窒息的芳香："),
    # Elle était comme un arôme irrespirable que ... exhalait pour moi toute chambre nouvelle：
    # 关系从句 que 的先行词是 arôme，译成两个并列分句后，「它像一股……芳香」缺少收束，
    # 后半句主语换成「每一间新房间」，「这股香气」又重复指代，主谓失配。合成一句定语即通。

    ("028", "①",
     "这个“我”我隔上若干年才能重新找到",
     "这个“我”，我隔上若干年才能重新找到"),
    # ce « Moi » que je ne retrouvais qu'à des années d'intervalles：两个「我」紧贴，
    # 中文读作叠字口吃，加逗号断开（不改字词）。

    ("028", "①",
     "过着一种虽无声、却必须去碰见、去回避、去迎接的生活，每次回来都是如此。",
     "过着一种虽然无声、但每次回来我们都必须去碰见、去回避、去迎接的生活。"),
    # d'une vie il est vrai silencieuse, mais qu'on était obligé de rencontrer, d'éviter,
    # d'accueillir, quand on rentrait：qu' 指那些「房间」，不是「生活」；
    # 原译让「生活」同时充当「过着」的宾语和「碰见／回避／迎接」的宾语，主语在句中丢失，
    # 只好用「每次回来都是如此」兜底。补出「我们」并前置时间从句，句意落实，不添不减。
]

chunks = sorted({c for c, _, _, _ in EDITS} | {"024"})
report = []


def load(chunk):
    path = os.path.join(BASE, "chunk%s" % chunk, "final.txt")
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        return path, f.read()


def stats(text):
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)
    han = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return nl, len(lines), sum(1 for l in lines if l.strip()), han


for chunk in chunks:
    path, text = load(chunk)
    nl0, ln0, ne0, han0 = stats(text)
    n = 0
    for c, cat, old, new in EDITS:
        if c != chunk:
            continue
        assert old in text, "NOT FOUND [%s] %s" % (chunk, old[:30])
        assert text.count(old) == 1, "NOT UNIQUE [%s] %s (%d)" % (
            chunk, old[:30], text.count(old))
        text = text.replace(old, new, 1)
        n += 1
    nl1, ln1, ne1, han1 = stats(text)
    assert nl0 == nl1, "newline changed"
    assert ln0 == ln1, "line count changed %d->%d" % (ln0, ln1)
    assert ne0 == ne1, "non-empty line count changed"
    assert text.count("\u27e6") == 0
    assert '"' not in text and "'" not in text
    if n:  # 0 改动的 chunk 不动磁盘
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
    report.append((chunk, n, ln0, ln1, ne0, han0, han1, "CRLF" if nl0 == "\r\n" else "LF"))

print("chunk | edits | lines(before=after) | paras | hanzi | newline")
for r in report:
    print("%s | %d | %d=%d | %d | %d->%d | %s" % r)

# 自查：脚本本身可解析
ast.parse(io.open(__file__, encoding="utf-8").read())
print("self-check ast.parse OK; total edits =", sum(r[1] for r in report))