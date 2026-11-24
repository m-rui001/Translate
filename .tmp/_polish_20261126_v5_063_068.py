# -*- coding: utf-8 -*-
"""润色 v5 chunk063 / 066 / 067 / 068（2026-11-26）

只做「定位唯一子串 → 替换」，不重写整文件；保持 CRLF 与空行结构。
"""
import ast
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))

CHUNKS = {
    "063": [
        # ① 判断句后半截缺「说是」，「或者是自然在某个瞬间的面貌给我们的印象」主宾失配
        ("一个存在，或者是自然在某个瞬间的面貌给我们的印象。",
         "一个存在，或者说是自然的某个瞬间面貌给我们的印象。"),
        # ③ 法语关系从句后置（dont pourtant la nostalgie m'était donnée par ce flot sonore）
        #    被搬成「而……给我的」，主语（乡愁）与给予者（声响）对不上
        ("那种我在生活里、在旅行中徒然寻找的多样性，而旅行的乡愁恰恰是这片声响给我的，它那阳光般的波涛就在我身旁一个个碎掉。",
         "那种我在生活里、在旅行中徒然寻找的多样性；然而，恰恰是这片声响给了我旅行的乡愁，它阳光般的波涛就在我身旁一个个碎掉。"),
    ],
    "066": [
        # ③ tel fut encore… celui que… 的比较结构照搬，中文主语被挤到「不亚于」之后，读不出谁比谁
        ("家人与家居：我随后同她散步时所感到的，不亚于我等阿尔贝蒂娜时那份带来如此多安宁的感情，也正是这样的东西。",
         "家人与家居：我随后同她散步时所感到的感情，也正是这样的，并不亚于我在等候阿尔贝蒂娜时那份给我带来如许安宁的感情。"),
    ],
    "067": [
        # ③ 法语括注（aussi séparé d'elles…）插在「看清」与其宾语之间，且「她们」先于所指出现
        ("我几乎来不及看清她们——我和她们之间隔着车窗，就跟我隔着自己房间的窗户一样——一个卖水果的姑娘，一个卖奶品的女人，立在自家门前，被好天气照得通亮，像一位女主角，",
         "我几乎来不及看清立在自家门前的一个卖水果的姑娘、一个卖奶品的女人——我和她们之间隔着车窗，就跟我隔着自己房间的窗户一样——她被好天气照得通亮，像一位女主角，"),
        # ① 「才」把「已经看不见了」读成因果，原文是「眼睛此前不过勉强辨出过」
        ("而那些年轻女人已经看不见了，我的眼睛才勉强辨出她们的五官，",
         "而那些年轻女人已经看不见了；我的眼睛只勉强辨出过她们的五官，"),
        # ③ bien loin de… ils n'ont fait que… 的「非但…只是」搭配不成立
        ("他们非但没有渎神，只是给她们添上、只是把她们被剥夺的品质和种种不同属性还给她们。",
         "他们非但没有渎神，反倒只是给她们添上、只是把她们被剥夺的品质和种种不同属性还给她们。"),
        # ① 「知道得很」作应答不成话（Très bien）
        ("“知道得很。”",
         "“清楚得很。”"),
        # ⑥ 宾语误读：déchirent l'air torride 是「划破灼热的空气」，不是「撕开一道口子」
        ("用一声像樱桃气味一样尖利的叫喊撕开那道口子？",
         "用一声像樱桃气味一样尖利的叫喊，撕破那灼热的空气？"),
        # ⑥ 错别字：给自由「划上」句号
        ("我清点着阿尔贝蒂娜给我自由画上的句号使我失去的种种快乐",
         "我清点着阿尔贝蒂娜给我自由划上的句号使我失去的种种快乐"),
        # ① 比较项残缺：aussi précieuses que pour l'archéologue le désordre d'une terre…
        ("对贪欢的人，就跟对考古学家一样珍贵——一片土地，发掘会让古币显露出来。",
         "对贪欢的人，就跟一片土地对考古学家一样珍贵——发掘会让古币显露出来。"),
        # ③ sans en parler à Albertine 是伴随状语，被搬成插在主谓之间的插入语
        ("因为，我没跟阿尔贝蒂娜提这件事，我已经决定晚上去韦尔迪兰家。",
         "因为我已经决定晚上去韦尔迪兰家，只是这事我没跟阿尔贝蒂娜提。"),
    ],
    "068": [
        # ③ si j'avais été seul 的括注被搬成破折号插入，且 tantôt（今天下午）丢失
        ("那么至少，我本来还可以——倘若我是独自一人——去认识那些散落在这个美好星期日阳光下的年轻女工，",
         "那么至少，倘若我是独自一人，今天下午我本来还可以去认识那些散落在这个美好星期日阳光里的年轻女工，"),
        # ① faire entrer dans la beauté de qui… 的宾语关系倒置，「归给了……生活」不通
        ("而在她们的美貌中，我把很大一部分归给了驱动着她们的那种未知的生活。",
         "而在她们的美貌里，有一大部分我要归于驱动着她们的那种未知的生活。"),
        # ① 缺「的」，「觉得自己渴望是清白的」读成「渴望（某事）是清白的」
        ("人总觉得自己渴望是清白的，而对方渴望则是可憎的。",
         "人总觉得自己的渴望是清白的，而对方的渴望则是可憎的。"),
        # ② 三个「的」串成的悬空定语（凡涉及……的，同涉及……的，这两者之间的对照）
        ("而且，凡涉及我们自己的，同涉及我们所爱之人的，这两者之间的对照，不只关乎欲望，也关乎说谎。",
         "而且，凡涉及我们自己的事与涉及我们所爱之人的事，这两者之间的对照，不只关乎欲望，也关乎说谎。"),
        # ① quelque chose d'aussi différent… d'aussi désirable que… 的比较句断裂
        ("在我看来——如同在一切不曾因实现的容易而磨钝了构想力的人看来那样——同我所熟悉的东西之不同，之令人向往，一如旅行所许诺的最神奇的城市。",
         "在我看来——如同在一切不曾因实现的容易而磨钝了构想力的人看来那样——是某种东西，它同我所熟悉的东西之不同、之令人向往，一如旅行所许诺的最神奇的城市。"),
    ],
}


def cjk(s):
    return sum(1 for c in s if "\u4e00" <= c <= "\u9fff")


def main():
    total = 0
    for name in ["063", "066", "067", "068"]:
        path = os.path.join(BASE, "chunk" + name, "final.txt")
        bak = path + ".bak_20261125"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        raw = open(path, "rb").read()
        nl = "CRLF" if b"\r\n" in raw else "LF"
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        before_lines = text.count("\n")
        before_cjk = cjk(text)
        n = 0
        for old, new in CHUNKS[name]:
            assert old in text, (name, old)
            assert text.count(old) == 1, (name, old)
            text = text.replace(old, new)
            n += 1
        assert text.count("\n") == before_lines, (name, "line count changed")
        assert "\r\n" in text if nl == "CRLF" else True
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        total += n
        print("chunk%s: 改动 %d 条 | 行数 %d→%d | 汉字 %d→%d | %s"
              % (name, n, before_lines, text.count("\n"), before_cjk, cjk(text), nl))
    print("合计改动 %d 条" % total)


ast.parse(open(__file__, encoding="utf-8").read())
main()