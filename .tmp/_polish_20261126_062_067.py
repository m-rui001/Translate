# -*- coding: utf-8 -*-
"""v4 chunk062/063/065/066/067 逐段润色（2026-11-26）。

改法：定位唯一子串 -> 替换 -> 断言命中数 == 1。绝不整文件重写。
"""
import ast
import os
import re
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    "chunk062": [
        # ① 悬空状语：法文 « rien qu'à sentir… » 是「只消……便看见」的条件式，原译「仅仅因为……闻到」
        # 无谓语可依，成悬空从句。
        ("——仅仅因为洗手时隔了那么久，第一次又闻到大旅馆那种香气过浓的肥皂的特殊气味。",
         "——而这一切，只消我在洗手时，隔了那么久第一次又闻到大旅馆那种香气过浓的肥皂的特殊气味。"),
        # ⑥ bourrique 是「母驴」，经理说的是 bourrique（蠢驴）却指 barrique（大桶），笑点在此；
        # 原译直接作「桶」并加注，笑点全失。
        ("我在楼下有一‘桶’（他多半想说 barrique，酒桶）",
         "我在楼下有一‘头驴’（他多半想说 barrique，酒桶）"),
        # ⑥ induire 是 enduire（涂抹）的错用，原译只作「抹了油」，双关落空。
        ("我已经给它‘抹’了油",
         "我已经给它‘导’了油（他本想说 enduire，涂上）"),
    ],
    "chunk063": [
        # ③ 法文 « qu'elle avait demandé la permission, accordée avec quelle joie, d'amener »
        # 的插入语被照搬，中文里主谓被「而……而……」拆断，读不通。
        ("身后跟着她的儿媳、眼下住在她家的宾客——那还是她征得许可、而许可又是获准得多么欢欣才带来的",
         "身后跟着她的儿媳，以及当时住在她家的几位宾客——她带她们来是请准过的，而主人准许时又是何等欣喜"),
        # ③ « toutes portes fermées à clef » 一个状语被拆成「关紧家门、锁上所有门闩」两个同义动宾，
        # 语义叠床架屋。
        ("那条他们自己将关紧家门、锁上所有门闩、阖家炮制的短讯",
         "那条他们自己将要关起门来、全家动手炮制的短讯"),
        # ① « ne s'est séparé qu'après avoir fait promettre » 的 ne…que 体被读散，
        # 「宾主直到请主人答应……方才散去」主谓错乱。
        ("那场超精选的午后聚会，宾主直到请主人答应不久再办一次，方才散去",
         "那场超精选的午后聚会，宾主非逼着主人答应不久再办一次不肯散去"),
        # ① 同位语断裂：「那与费泰尔讷截然不同的：拉斯普利埃」中心语悬空。
        ("其中尤其是头一次租出了她的一处产业，那与费泰尔讷截然不同的：拉斯普利埃。",
         "其中尤其是头一次租出去的一处产业，那地方与费泰尔讷截然不同：拉斯普利埃。"),
        # ① « comme la sienne » 被压成「一如它们之于她」，读不出比较项。
        ("它们以荆棘之冠环绕我的灵魂并使之高贵，一如它们之于她。",
         "它们以荆棘之冠环绕我的灵魂并使之高贵，一如环绕她的一样。"),
    ],
    "chunk065": [
        # ① 语序倒置：「撞见带着几个女儿来的一位贡布雷太太」，定语与数量词打架。
        ("在沙滩上撞见带着几个女儿来的一位贡布雷太太",
         "在沙滩上撞见一位带着几个女儿的贡布雷太太"),
        # ⑤ 绰号前后不一：后文引语作「到时你就有得说了」，此处却作「到时你就知道了」；
        # 法文两处同为 « Tu m'en diras des nouvelles »。
        ("不过私下里我们只叫她“到时你就知道了”",
         "不过私下里我们只叫她“到时你就有得说了”"),
        # ⑥ cueiller 只是 cuiller 的软化读法，非「采撷」；「采撷」是采摘之意，与银器无涉。
        ("因此说成“采撷”（cueiller）",
         "因此改口说成“勺儿”（cueiller）"),
        # ⑥ 法文以 Fénelon / Fénélon 两种拼法立区别（后者多一尖音符），中文两处均作「费内隆」，
        # 「尖音符」云云遂无所指，须以西文标出。
        ("而普桑夫人从来只说“费内隆”，觉得那尖音符平添几分柔美。",
         "而普桑夫人从来只说“Fénélon”，觉得那尖音符平添几分柔美。"),
        # ⑥ « emporta la caisse » 是卷走款项（caisse 此处指钱柜里的钱），「卷走钱柜」量词失当。
        ("卷走了钱柜", "卷走了钱款"),
        # ⑥ 「会得一场……病」不成话，改「也得上一场……」。
        ("等你会得一场厉害的眼炎", "等你也得上一场厉害的眼炎"),
        ("等你会得一场厉害的甲沟炎", "等你也得上一场厉害的甲沟炎"),
    ],
    "chunk066": [
        # ① 长串并列被逗号一路顿下去，「那扇楼梯门」失所依，改用冒号引出例证。
        ("以及一切与之相关的事情，那扇楼梯门——",
         "以及一切与之相关的事情：那扇楼梯门——"),
        # ③ 法文括注被搬成破折号插在主语与谓语之间（「景象——……——都像」），
        # 按判例改顺句，把插入语移到句末。
        ("可是每走一步，赌场或那条街上某个被遗忘的景象——第一个晚上，我在那条街上一边等她，"
         "一边一直走到迪盖-特鲁安纪念碑——都像一阵无法抗拒的风，拦住我的脚步，我低下头，免得看见。",
         "可是每走一步，赌场或那条街上某个被遗忘的景象都像一阵无法抗拒的风，拦住我的脚步，"
         "我只好低下头，免得看见——第一个晚上，我在那条街上一边等她，一边一直走到迪盖-特鲁安纪念碑。"),
        # ⑥ « leur cadet » 是最小的弟弟，非泛指的「他们的弟弟」（同段前已出现两个哥哥、一个姐姐）。
        ("只有他们的弟弟留了下来，没人要他，因为他斜视。",
         "只有他们最小的弟弟留了下来，没人要他，因为他斜视。"),
    ],
    "chunk067": [
        # ④ 弗朗索瓦丝口中「她」前一段指阿尔贝蒂娜，此处指外祖母；改用「夫人」——她在同一段里
        # 正是这样称呼外祖母的（「夫人，可不能这样说话」）。
        ("‘尤其是，弗朗索瓦丝，’她对我嘱咐道，‘千万别让我的小外孙知道。’",
         "‘尤其是，弗朗索瓦丝，’夫人当时嘱咐我说，‘千万别让我的小外孙知道。’"),
        # ④ 同段「夫人」既指外祖母又指妈妈（« prévenir Madame d'arriver »），读者必错认；
        # 后者改称「妈妈」，与全段叙述用词一致。
        ("有些日子，她想给夫人捎信，让她来一趟，好再见一面。可她又怕突兀地撞见她，因为她什么也没跟夫人说。",
         "有些日子，她想给妈妈捎个信，让她来一趟，好再见一面。可她又怕这样会惊着妈妈，因为她什么也没跟妈妈提起过。"),
        # ① « Ce n'est pas une personne pour ici » 原译「这可不是能将就这儿的人」语序拧了。
        ("这可不是能将就这儿的人。", "她可不是能将就这种地方的人。"),
    ],
}


def han(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def main():
    report = []
    for chunk, edits in EDITS.items():
        d = os.path.join(BASE, chunk)
        path = os.path.join(d, "final.txt")
        bak = path + ".bak_20261125"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)

        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        before_han = han(text)
        before_lines = text.count("\n")

        applied = 0
        for old, new in edits:
            assert old in text, (chunk, old[:24])
            assert text.count(old) == 1, (chunk, text.count(old), old[:24])
            text = text.replace(old, new, 1)
            applied += 1

        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)

        after_han = han(text)
        after_lines = text.count("\n")
        assert before_lines == after_lines, (chunk, before_lines, after_lines)
        crlf = text.count("\r\n")
        eol = "CRLF" if crlf and crlf == after_lines else ("LF" if crlf == 0 else "MIXED")
        report.append((chunk, before_lines, after_lines, before_han, after_han, applied, eol))

    for r in report:
        print("%s 行 %d->%d 汉字 %d->%d 改动 %d 换行 %s" % r)


main()
ast.parse(open(__file__, encoding="utf-8").read())