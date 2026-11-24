# -*- coding: utf-8 -*-
"""v6 chunk047-050 逐段润色（2026-11-26）。
只做「定位唯一子串 → 替换 → count 断言」，不整文件重写。
"""
import os, shutil, ast

BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    "chunk047": [
        # ① 比较句缺谓语：「赋予……的真实，超过它赋予……的真实」悬空
        ("正如贡布雷的回忆赋予金凤花和山楂花的真实，超过它赋予新花的真实。",
         "正如贡布雷的回忆使金凤花和山楂花比新开的花更加真实。",
         "①", "donnoit plus de réalité qu'aux fleurs nouvelles；「赋予A的真实，超过赋予B的真实」比较句搭不上，改动词句"),
        # ② 「的」字三层叠：需要…的需要，…的温柔的需要
        ("我对阿尔贝蒂娜给我的同一种温柔的需要，对一个相当有教养、同时又像姊妹一样的姑娘的温柔的需要，正如对与阿尔贝蒂娜同一阶层的女人的需要一样，",
         "我对阿尔贝蒂娜给予我的那种温柔的需要，也就是对一个相当有教养、同时又像姊妹一样的姑娘的温柔的需要，正如对与阿尔贝蒂娜同一阶层的女人的需要一样，",
         "②", "la tendresse d'une fille assez cultivée… 是前一项的同位语，原译并列两个「需要」使三个「的」层叠难解，补「也就是」明示同位"),
    ],
    "chunk048": [
        # ⑥ grands deuils 误读为「隆重丧事」
        ("因为有些小说就像一场场短暂的隆重丧事，废掉了习惯",
         "因为有些小说就像一场场短暂的沉痛哀悼，废掉了习惯",
         "⑥", "de grands deuils momentanés＝一阵阵短暂的深切哀悼（deuil 为「哀悼、丧亲之痛」），非「隆重丧事」"),
        # ⑥ l'ignorance heureuse de l'espérance 关系读反
        ("保留着当时那种对希望浑然不觉的幸福——那希望曾向一个如今已成过去的时间奔去",
         "保留着希望本身那种幸福的浑然不觉——那希望正向一个如今已成过去的时间奔去",
         "⑥", "l'ignorance heureuse de l'espérance 是「希望自身的幸福的浑然不觉」，原译成「对希望浑然不觉的幸福」把主体颠倒了"),
    ],
    "chunk049": [
        # ⑤ 同段 arrêts 先作「停歇」后作「驿站」
        ("曾有过三处停歇；我记得它们",
         "曾有过三处驿站；我记得它们",
         "⑤", "同段下文作「这几处驿站中的第一处」，arrêts 归一为「驿站」"),
        # ③ 关系从句链被直搬，「仅限于凡……东西——……由此与它发生联系」尾句悬空重复
        ("仅限于凡在我们经历一场炽爱之前本就存于心灵之中的东西——或者滋养它，或者对抗它，或者与它一道为我们善于分析的理智构成意象上的反差，由此与它发生联系。",
         "仅限于这样一点：凡在我们经历一场炽爱之前本就存于心灵之中的东西，总要同这爱情相连——或者滋养它，或者对抗它，或者与它一道为我们善于分析的理智构成意象上的反差。",
         "③", "dans la mesure où ce qui était déjà dans notre âme… s'associe à lui, soit… 的链条照搬，句末又补一句「由此与它发生联系」把谓语重说一遍；改顺"),
        # ② 「一个我出了门的晴朗的万圣节星期日」四层定语
        ("始于初冬一个我出了门的晴朗的万圣节星期日。",
         "始于初冬一个晴朗的万圣节星期日，那天我出了门。",
         "②", "un beau dimanche de Toussaint où j'étais sorti 的关系从句塞进定语，拆为后置分句"),
        # ②④ 「她弹得最为频繁、习惯于……」定语挂错主语
        ("有时，在那些她弹得最为频繁、习惯于发表当时我觉得十分迷人的某句议论、引起某种追忆的段落里，我会自语道：",
         "有时，在那些她弹得最为频繁、又惯于在其中说一句当时我觉得十分迷人的议论、勾起某种追忆的段落里，我会自语道：",
         "②", "où elle avait l'habitude de faire telle réflexion… 的「习惯于」主语是她，原译读成定语修饰「段落」"),
        # ④ 「它们」误指战栗，实指小径
        ("原本不足以使它们重新焕发生机",
         "原本不足以使这些小径重新焕发生机",
         "④", "les renouveler 的 les 指 ces allées；上句刚出「战栗」，代词会误认"),
    ],
    "chunk050": [
        # ⑥ dans lequel elles s'étaient condensées 方向读反
        ("如今，我的爱情曾凝聚在她们身上，那颗正在消逝的星辰又重新散成这片四散的星云尘埃，难道不自然吗？",
         "如今，我的爱情这颗正在消逝的星辰——她们曾凝聚于其中——又重新化作这片弥散的星云尘埃，难道不自然吗？",
         "⑥", "l'étoile… de mon amour, dans lequel elles s'étaient condensées＝她们凝聚在「我的爱情」这颗星辰里，原译反成「爱情凝聚在她们身上」；「散成……四散」亦复沓"),
        # ③ 一句法文被切成两句，末句「而对我来说……」悬空
        ("再说，在巴尔贝克，我最初想认识阿尔贝蒂娜，不正是因为她在我看来代表了那些少女吗？我在街上、大路上常常因为看见她们而停下脚步，而对我来说，她能够概括她们的生活。",
         "再说，在巴尔贝克，我最初想认识阿尔贝蒂娜，不正是因为她在我看来代表了那些少女——我在街上、大路上常常因为看见她们而停下脚步——而且对我来说，她能够概括她们的生活吗？",
         "③", "法文是一个 n'était-ce pas parce que… et que… ? 的问句，原译断成两句后「而对我来说」无所依附，用破折号收进原句"),
        # ① 「在处处」不成话
        ("我心中携带的形象使我在处处重新找到她",
         "我心中携带的形象使我处处重新找到她",
         "①", "la faisant retrouver partout，「在处处」不成词"),
        # ① 「如此分毫不差地相同」搭配重复
        ("她使我如此强烈地想起阿尔贝蒂娜，身段又如此分毫不差地相同",
         "她使我如此强烈地想起阿尔贝蒂娜，身段又与她分毫不差",
         "①", "était si exactement de la même corpulence，「分毫不差地相同」语义重复且缺比较对象"),
        # ③ 宾语前置 + 代词复指
        ("我并非只用眼睛确认它，像确认那种在散步过程中常常展开的表面外观那样",
         "我并非只用眼睛去确认，像确认那种在散步途中常常展开的表面外观那样",
         "③", "je ne le constatais pas seulement avec mes yeux 的宾语前置加代词复指照搬，去「它」"),
    ],
}


def han(s):
    return sum(1 for ch in s if '\u4e00' <= ch <= '\u9fff')


def main():
    total = 0
    for name in ("chunk047", "chunk048", "chunk049", "chunk050"):
        d = os.path.join(BASE, name)
        fp = os.path.join(d, "final.txt")
        bak = fp + ".bak_20261125"
        if not os.path.exists(bak):
            shutil.copy2(fp, bak)
        else:
            print("backup exists, skip cp:", bak)
        with open(fp, encoding="utf-8", newline="") as f:
            text = f.read()
        nl = "\r\n" if "\r\n" in text else "\n"
        lines_before = len(text.split(nl))
        han_before = han(text)
        n = 0
        for old, new, cls, why in EDITS[name]:
            assert "\r\n" not in old and "\r\n" not in new
            if old not in text:                      # 已改过，重跑时跳过
                assert new in text, (name, old[:30])
                continue
            assert text.count(old) == 1, (name, old[:30], text.count(old))
            text = text.replace(old, new)
            n += 1
        with open(fp, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        total += n
        print("%s: 改动 %d 条 | 行数 %d→%d | 汉字 %d→%d | 换行 %s"
              % (name, n, lines_before, len(text.split(nl)), han_before, han(text),
                 "CRLF" if nl == "\r\n" else "LF"))
    print("总改动条数:", total)


main()
ast.parse(open(__file__, encoding="utf-8").read())