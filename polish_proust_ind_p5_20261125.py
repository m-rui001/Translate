# -*- coding: utf-8 -*-
"""chunk061-084 逐段润色（v1 第一卷，通读润色轮）。
只做定位唯一子串替换；CRLF 原样保留；每条断命中数==1。"""
import ast, io, os, shutil, sys

BASE = "E:/Translate/work_proust/out_ind/v1"

# (chunk, [(old, new, 理由)])
EDITS = [
    (62, [
        ("在布洛克还没让我的眼睛和思想习惯更精微的和声之前",
         "在布洛克还没让我的眼睛和思想习惯于更精微的和声之前",
         "读不通：accoutumer qqn à qqch 译成“让…思想习惯更精微的和声”，动宾失配"),
    ]),
    (63, [
        ("这种人尽管在他一切道德偏见瓦解之际，却偏偏在别人的丑行里只找到一条理由去对那人施以善意",
         "这种人身上，一切道德偏见都已瓦解，于是别人的丑行反倒成了他们施以善意的理由",
         "读不通：“尽管…却偏偏…”架空了主语，且 le déliement de tout préjugé moral 是原因而非让步"),
        ("因此也就留给天气没准的日子走，梅塞格利斯那边的气候相当多雨，我们始终看得见鲁森维尔的林边，好钻进林中深处躲避。",
         "因此也就留给天气没把握的日子走。那边气候相当多雨，我们始终看得见鲁森维尔的林边，好在雨来时赶紧钻进林子深处躲避。",
         "读不通：逗号连缀两句，末句“好钻进林中深处躲避”悬空无主语"),
    ]),
    (65, [
        ("她抱歉说不会应答我那些理论，只说",
         "她便抱歉地说自己不会应答我那些理论，只说",
         "读不通：“她抱歉说不会应答…”缺状语，读起来像“抱歉说”"),
    ]),
    (66, [
        ("那些叫喊和挨打的墙树，都不过是一些使我兴奋的混沌念头",
         "那些叫喊，以及挨打的墙和树，都不过是一些使我兴奋的混沌念头",
         "硬伤：原文 les murs…, entendaient des cris joyeux, qui n'étaient, les uns et les autres… “墙、树”与“叫喊”并列，译文误并成“墙树”"),
    ]),
    (68, [
        ("他先是一心全然扑在照顾女儿的母亲和保姆职责上",
         "他先是一心扑在抚养女儿上，尽着慈母和保姆的双重职责",
         "硬伤：les soins de mère et de bonne d'enfant qu'il donnait à sa fille 意为“他给女儿的母亲般、保姆般的照料”，非“女儿的母亲”"),
        ("而在他为女儿牺牲它们之前；而这些作品大部分",
         "直到他为女儿牺牲了它们；而这些作品大部分",
         "读不通：“在他…之前；”半句悬空，与后句接不上"),
    ]),
    (71, [
        ("碰上眼看要一连串晴天的日子",
         "碰上看来要接连几个晴天的日子",
         "读不通：“眼看要一连串晴天”缺谓语"),
    ]),
    (72, [
        ("诺沃蓬、克莱枫丹、干马丹维尔、巴伊奥勒-莱克桑",
         "诺沃蓬、克莱枫丹、马丹维尔-勒塞克、巴伊奥勒-莱克桑",
         "专名：Martinville-le-Sec，本册 chunk078 作“马丹维尔-勒塞克”，此处误把 le Sec 意译成“干”"),
    ]),
    (73, [
        ("这产业的入口由产业主向公众开放，而产业主自己则乐在其中，做起了水生园艺",
         "这产业的入口由产业主向公众开放，而他本人则乐在其中，做起了水生园艺",
         "读不通：同句两出“产业主”，第二处宜用回指"),
    ]),
    (79, [
        ("「孤零零地从平原的平面上隆起", "“孤零零地从平原的平面上隆起", "体例：全册对话与引文一律用“”，此处孤例「」"),
        ("渐渐隐没在夜色里。」", "渐渐隐没在夜色里。”", "体例：同上"),
    ]),
    (81, [
        ("对我来说始终和我们平行度过的种种生活当中那一种连在一起——那一种最充满波折、最富于插曲，我说的就是智性生活——连着它的许多小事。",
         "对我来说始终与我们平行度过的那些生活里的某一种连在一起——最充满波折、最富于插曲的那一种，我说的就是智性生活——连着它的许多小事。",
         "读不通：“种种生活当中那一种”定语层层套叠，主句被压没"),
    ]),
    (82, [
        ("被窗帘上方被曙光竖起的手指画下的苍白记号赶得无影无踪",
         "被曙光举起的手指在窗帘上方画下的那点苍白记号赶得无影无踪",
         "外语句法：le doigt levé du jour 的属格链被逐字搬成双重“被”字句"),
        ("任何“新成员”——韦尔迪兰夫妇若不能让他们相信，不去他们家的人的晚会沉闷得像下雨，就立刻会被除名。",
         "任何“新成员”，只要韦尔迪兰夫妇不能让他相信不去他们家的人的晚会沉闷得像下雨，就立刻会被除名。",
         "指代＋读不通：插入语把“新成员”与谓语割断，且“他们”实指单数的新成员"),
    ]),
]


def main():
    total = 0
    for chunk, edits in EDITS:
        path = os.path.join(BASE, "chunk%03d" % chunk, "final.txt")
        bak = path + ".bak_20261125"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        with io.open(path, "r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        n_before = text.count("\r\n")
        done = 0
        for old, new, why in edits:
            if old not in text and new in text:
                continue  # 已应用（脚本可重入）
            assert old in text, (chunk, old[:30])
            assert text.count(old) == 1, (chunk, "not unique", old[:30])
            text = text.replace(old, new)
            total += 1
            done += 1
        edits = [e for e in edits]
        assert text.count("\r\n") == n_before, (chunk, "line structure changed")
        with io.open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print("chunk%03d: %d edits" % (chunk, done))
    print("TOTAL", total)


ast.parse(open(__file__, encoding="utf-8").read())
main()