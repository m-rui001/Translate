# -*- coding: utf-8 -*-
"""逐段润色：v3 chunk213-217（2026-11-26）

只做「定位唯一子串 -> 替换 -> assert 命中一次」，不重写文件、不动段数行数。
"""
import ast
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)

EDITS = {
    "chunk213": [
        # ⑥ 硬伤 poele=华盖（婚礼/葬礼上由人举着的天篷），非「炉子」
        (
            "至于那炉子——布洛克大概会以为点炉子只用于葬礼，因为报上的丧仪报道里总要提到“灵堂炉边的绦带”"
            "——德·盖尔芒特先生却还记得，自己还是孩子的时候，就见过那炉子摆在德·马伊-内勒先生的婚礼上。",
            "至于那顶华盖——布洛克大概会以为它只用于葬礼，因为报上的丧仪报道里总要提到“华盖的绦带”"
            "——德·盖尔芒特先生却还记得，自己还是孩子的时候，就见过它在德·马伊-内勒先生的婚礼上被人举着。",
        ),
        # ⑥ 硬伤 enfants voues au bleu ＝ 许愿穿蓝衣（献给圣母）的孩子，非「献给旧派」
        ("圣约瑟夫式的领带、献给旧派的孩子，等等", "圣约瑟夫式的领带、许愿穿蓝衣的孩子，等等"),
    ],
    "chunk214": [
        # ③ 法语 s'il était monte plus tot 的后置条件被塞成破折号括注，隔断动宾与目的从句
        (
            "便借着最荒唐的借口去为男爵办一件差事——如果他上楼早了些——指望当晚能被委以递烛台或递衬衫的差事。",
            "便借着最荒唐的借口，趁男爵上楼早些时去为他办一件差事，指望当晚能被委以递烛台或递衬衫的差事。",
        ),
        # ⑥ en effet ＝ 的确/实在，非「果然」（他并无预言在先）
        ("而他的脸果然痉挛发白", "而他的脸的确痉挛发白"),
        # ① 原句把 je forcerais le sens des mots ... en vous disant 拆成两句，重复「过分引申字义」
        (
            "我不瞒您说，我本指望得更好些，我也许会稍稍过分引申字义——这是不应该做的，即便对方不懂字义的价值，"
            "单是出于自尊也不该这样做——我若说我对您曾有过好感，便是在过分引申字义了。",
            "我不瞒您说，我本指望得更好些；我若说我对您曾有过好感，也许是稍稍强用了字义"
            "——这是不应该做的，即便对方不懂字义的分量，单是出于自尊也不该这样做。",
        ),
    ],
    "chunk215": [
        # ⑥ compas ＝ 圆规（圆规两脚大张的跨度），非「罗盘」
        ("他的才智以罗盘般张开的幅度", "他的才智以圆规般大张的跨度"),
        # ⑥ n'en etait pas moins superieur de cent coudres ＝ 仍高出百尺，译文弱化成「不矮一头」
        ("并且丝毫不因此就比他兄弟、他嫂嫂等等矮一头。", "还照样比他兄弟、他嫂嫂等人高出百尺。"),
        # ③ 两个「正如」并列（Comme dans les Lances / comme le doit tout etre noble），改掉第二个
        (
            "胜利者向那最谦卑的人走去，正如任何一个高贵者都该做的那样",
            "胜利者向那最谦卑的人走去，这本是一切高贵者都该做的",
        ),
        # ⑦ 体例：夏尔吕这一整段引语在段末仍未收引号（法文此行末亦脱 »），补齐
        (
            "您说过很不一样的话。" + NL,
            "您说过很不一样的话。”" + NL,
        ),
    ],
    "chunk216": [
        # ⑤ 同一场景，213 作「长沙发」，此处作「长椅」，归一
        ("一边在方才一直躺着不动的长椅上猛地挺直身子", "一边在方才一直躺着不动的长沙发上猛地挺直身子"),
        # ⑥ un instant auparavant ＝ 片刻之前，非「一刻钟前」
        ("他忘了一刻钟前谈到“他那威严的脚趾”时", "他忘了片刻之前谈到“他那威严的脚趾”时"),
        # ⑥ laissai passer le mot chatier ＝ 不计较这个词，非「让他把字说过去」
        ("我让他把“罚”这个字说过去", "我没有计较“罚”这个字"),
        # ① 「却一个也找不到，我可能对谁谈起过……」逗号断在宾语从句中间
        (
            "一边最后一次在脑子里搜寻，却一个也找不到，我可能对谁谈起过德·夏尔吕先生。",
            "一边最后一次在脑子里搜寻，却一个也找不到自己可能对谁谈起过德·夏尔吕先生。",
        ),
        # ① dire quelque chose qui ne soit pas exactement rien
        ("说点什么，别说的恰恰全是空无。", "说些不完全是空无的话。"),
    ],
    "chunk217": [],
}


def main():
    report = []
    for name, edits in EDITS.items():
        d = os.path.join(BASE, name)
        path = os.path.join(d, "final.txt")
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        bak = path + ".bak_20261125"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        before_lines = text.count("\n") + (0 if text.endswith("\n") else 1)
        before_zh = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
        crlf = "\r\n" in text

        applied = 0
        for old, new in edits:
            if text.count(old) == 0 and text.count(new) == 1:
                continue  # 幂等：已落过盘
            assert text.count(old) == 1, (name, old[:40], text.count(old))
            text = text.replace(old, new)
            applied += 1

        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        after_lines = text.count("\n") + (0 if text.endswith("\n") else 1)
        after_zh = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
        assert before_lines == after_lines, (name, before_lines, after_lines)
        report.append((name, applied, before_lines, after_lines, before_zh, after_zh,
                       "CRLF" if crlf else "LF"))

    print("chunk\tedits\tlines(before->after)\thanzi(before->after)\teol")
    for r in report:
        print("%s\t%d\t%d->%d\t%d->%d\t%s" % r)


main()
ast.parse(open(__file__, encoding="utf-8").read())
print("self-check ast.parse OK")