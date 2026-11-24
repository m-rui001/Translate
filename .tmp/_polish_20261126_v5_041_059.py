# -*- coding: utf-8 -*-
"""润色 v5 chunk041 / chunk043 / chunk057 / chunk059（2026-11-26）

只做「定位唯一子串 → 替换」，不重写整文件；保持 CRLF 与空行结构。
"""
import ast
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))

CHUNKS = {
    "041": [
        # ① 语言/腔调 指代错位：语言仍是「话」，后文才是语调
        ("——那是别人过去对我用过的那套腔调，带着讥诮和斥责",
         "——那是别人过去对我用过的那套话，带着讥诮和斥责"),
        # ① 缺宾语，「憎恶」悬空
        ("他岂不是更加憎恶！",
         "他岂不是对这些缺点更加憎恶！"),
        # ⑥ amie 是「朋友」，非「芳邻」（下文「姑妈从来就不认识安弗维尔的什么人」）
        ("您姑妈那个住在安弗维尔的芳邻一样",
         "您姑妈那位住在安弗维尔的朋友一样"),
    ],
    "043": [
        # ① 「碰不到」弱化 qui ne me rencontrait pas，且两句主语含混
        ("可今晚这个吻里没有她本人，这吻也没有碰到我，叫我好不安",
         "可今晚她的吻里没有她本人，那吻也没有触及我，叫我好不安"),
        # ① 「一……时」缺「就」，读来断裂
        ("那是她一完全正面朝向我时就变成的样子",
         "那是她一旦完全正面朝着我时就变成的样子"),
    ],
    "057": [
        # ⑥ 施受反转：是斗牛士用刺戳激怒公牛，不是公牛拿角刺人；「它」误指公牛
        ("而那个用它刺人的高傲耀眼的家伙早已不在，残忍的围观者还在赞叹它的威风和狡诈。",
         "而那个用刺戳激怒它的高傲耀眼的家伙早已不在，残忍的围观者却还在赞叹他的威风和狡诈。"),
    ],
    "059": [
        # ③ 被动式硬搬「被通知到」
        ("我的记忆没有及时被通知到；它曾认为不必留存副本。",
         "我的记忆没有事先得到提醒；它曾觉得不必留存副本。"),
        # ⑦ 引号只该圈住「四分之一拍」，误把「沉默」圈进去
        ("在“四分之一拍沉默”之后",
         "在“四分之一拍”的沉默之后"),
    ],
}


def cjk(s):
    return sum(1 for c in s if "\u4e00" <= c <= "\u9fff")


def main():
    total = 0
    for name in ["041", "043", "057", "059"]:
        path = os.path.join(BASE, "chunk" + name, "final.txt")
        bak = path + ".bak_20261125"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        raw = open(path, "rb").read()
        nl = "CRLF" if b"\r\n" in raw else "LF"
        before_lines = text.count("\n")
        before_cjk = cjk(text)
        n = 0
        for old, new in CHUNKS[name]:
            assert old in text, (name, old)
            assert text.count(old) == 1, (name, old)
            text = text.replace(old, new)
            n += 1
        assert text.count("\n") == before_lines, (name, "line count changed")
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        total += n
        print("chunk%s: 改动 %d 条 | 行数 %d→%d | 汉字 %d→%d | %s"
              % (name, n, before_lines, text.count("\n"), before_cjk, cjk(text), nl))
    print("合计改动 %d 条" % total)


ast.parse(open(__file__, encoding="utf-8").read())
main()