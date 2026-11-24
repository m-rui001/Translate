# -*- coding: utf-8 -*-
"""v6 chunk025/026/029/030 逐段润色（2026-11-26 轮）

做法：定位唯一子串 -> assert count == 1 -> 替换。绝不整文件重写。
换行符 CRLF 原样保留（open(..., encoding='utf-8', newline='')）。
"""
import ast
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))

# chunk -> [(类别, old, new, 备注)]
EDITS = {}

EDITS["chunk025"] = [
    ("①",
     "在阿尔贝蒂娜死后一些时候，我瞥见了这个回忆",
     "在阿尔贝蒂娜死后过了些时候，我瞥见了这个回忆",
     "quelque temps après： 「一些时候」不成词，与前文「突然间」时距不合"),
    ("③",
     "舌头会奇怪地松开，轻易讲出一桩过错",
     "舌头会奇怪地松动，轻易讲出一桩过错",
     "les langues se délient：délier 是解缚、松动，非「松开」物件"),
    ("①",
     "——而这些转变在气压计、气球、电话等等的后世完善中，补救着人类发明那些几乎无法辨认的原始模型——",
     "——而这些转变，在气压计、气球、电话等等日后的改进中，弥补着人类那些几乎辨认不出的原始发明模型的不足——",
     "不得 passé par les transformations qui remédient aux modèles primitifs des inventions humaines：括注内主谓错配，「补救……模型」不成话"),
    ("①",
     "这些梦并不十分严重，第一个理由是它们所引发的悲伤在醒来后几乎只延续一个小时",
     "这些梦并不十分严重，第一个理由是：它们所引发的悲伤在醒来后几乎只延续一个小时",
     "pour une première raison, c'est que…：冒号缺失，「理由是」后直接接完整句，谓语断裂"),
    ("①",
     "——而这种样子是一种幻觉、一种细分投射到它们身上的，因为说“重影”还不足以说明。",
     "——而这种样子是由一种幻觉、一种细分投射上去的（因为只说“重影”还不足以说明）。",
     "que projette sur eux une illusion, une subdivision (car dédoublement ne serait pas assez dire)：被动关系照搬成「一种细分投射到……的」，定语悬空"),
    ("①",
     "但是，那种曾使我在她还在时顺从她的同样的疲惫、同样的怯懦，自从我再也见不到她以后，便阻止我着手任何事情。",
     "但是，当初使我在她还在时顺从她的那种疲惫、那种怯懦，自从我再也见不到她以后，便阻止我着手任何事情。",
     "「那种……同样的疲惫」两个限定词叠在一个中心语上；la même fatigue, la même lâcheté qui m'avaient fait…"),
    ("①",
     "我决定进行这项调查，至少它完全是自然的。",
     "我决定着手这项调查，至少它是再自然不过的事。",
     "au moins toute naturelle：「它完全是自然的」主谓搭配生硬"),
    ("⑥",
     "也激起那种悲伤：这不在是永恒的",
     "也激起那种悲伤：这种不在是永恒的",
     "缺指量词，「这不在是」易读作「这不在……」的否定"),
    ("②",
     "而是对那些充满信任的柔情时刻的温柔回忆",
     "而是对那些信任相依的柔情时分的温柔回忆",
     "le souvenir attendri des heures de tendresse confiante：三个「的」压在「回忆」前"),
    ("④",
     "这些时刻是与那个因她死去而真正让我失去的姐妹一起度过的",
     "这些时刻是与一位姐妹一起度过的——她的死让我真正失去了她",
     "la sœur que sa mort m'avait réellement fait perdre：句内「她」与「姐妹」同指一人却似两人，指代错乱"),
    ("①",
     "而是我那渴望参与爱情最普遍情感的心曾逐渐说服我她所是的那个样子",
     "而是我那渴望参与爱情最普遍情感的心，曾渐渐说服我她就是那个样子",
     "mon cœur … m'avait peu à peu persuadé qu'elle était：「说服我她所是的那个样子」宾语从句残缺"),
    ("①",
     "我现在感到其中被添加、融合进一种快感",
     "我现在感到其中有一种快感被添加、融合进去",
     "qu'était ajoutée, amalgamée une volupté：被动句主语（一种快感）被丢到介词后"),
]

EDITS["chunk026"] = [
    ("①",
     "艺术并非唯一能把魅力和神秘放进最微不足道的事物里的东西，",
     "并非只有艺术才把魅力和神秘放进最微不足道的事物里；",
     "L'art n'est pas seul à mettre…：「艺术并非唯一……的东西」把艺术物化为「东西」"),
    ("①",
     "不曾投以任何注意，如今却满眼含泪，转向它的美，转向它那庄重的温柔。",
     "不曾投以任何注意；如今我却满眼含泪，转眼看它的美，看它那庄重的温柔。",
     "et vers la beauté, la grave douceur duquel je tournais maintenant des yeux pleins de larmes：主句主语在前半句已滑走，「转向」悬空"),
    ("①",
     "但人并不是在它于这些印象中间迷失时，才能认清它。",
     "但人并不是在它迷失于这些印象之中时就能认清它的。",
     "ce n'est pas perdue au milieu d'elles qu'on peut s'en rendre compte：「并不是……才能」把否定辖域读反"),
]

EDITS["chunk029"] = [
    ("①",
     "只在往头发上洒香水、为了讨我喜欢这件事上稍微耽搁了一会儿！",
     "只为了讨我喜欢，往头发上洒些香水，才稍微耽搁了一会儿！",
     "se retardant seulement à verser de l'odeur dans ses cheveux pour me plaire：目的状语被塞进「在……这件事上」"),
    ("⑥",
     "我的心便不再停止跳动",
     "我的心就跳个不停",
     "mon cœur ne cessait plus de battre：ne…plus de 是「不住地」，读成「不再停止」则义反"),
    ("⑥",
     "在我的心理学上提出新的、越来越痛苦的问题",
     "在我的心理上提出新的、越来越痛苦的问题",
     "à ma psychologie：此处指「我的心理」，非作为学科的「心理学」"),
    ("①",
     "那种仿佛相信自己被关闭在自身之中、因而发出的绵长哀诉",
     "那种仿佛相信自己被关闭在自身之中而发出的绵长哀诉",
     "l'âme qui croit vivre enfermée en elle-même：「因而」把定语读成因果"),
    ("①",
     "由于我们共同经历了完全不同的生活，在一整块思想中，由于一种痛苦的忧虑维持着持久的凝聚，任何分心和遗忘的裂缝都不可能潜入其中，所以",
     "由于我们共同过的是一种完全不同的生活，而在一整块思想里，一种痛苦的忧虑维持着持久的凝聚，任何分心与遗忘的裂缝都无法潜入其中，所以",
     "une vie … où n'avait pu se glisser, dans un bloc de pensées où une douloureuse préoccupation maintenait une cohésion permanente, aucune fissure：括注式插入把「生活」与「裂缝」隔断"),
    ("⑤",
     "只要斯泰尔玛丽亚小姐在我本来应当同她一起到布瓦岛吃晚饭的那个晚上没有临时取消约会",
     "只要斯泰尔玛丽亚小姐在我本来应当同她一起到树林岛吃晚饭的那个晚上没有临时取消约会",
     "île du Bois：canon 取全库多数「树林岛」（3 处，v3 同景），少数派「布瓦岛」归一"),
    ("⑤",
     "斯泰尔玛丽亚小姐拒绝到布瓦岛来吃晚饭",
     "斯泰尔玛丽亚小姐拒绝到树林岛来吃晚饭",
     "同上，同一专名同段内归一"),
    ("②",
     "倘若对于拥有一切可以使她与我之间的距离无限扩大的条件的德·盖尔芒特夫人，我曾经由于认为",
     "倘若对于德·盖尔芒特夫人——她身上的一切都能使她和我的距离无限扩大——我曾经由于认为",
     "Mme de Guermantes comblée de tout ce qui pouvait rendre infinie la distance entre elle et moi：四个「的」把「德·盖尔芒特夫人」压没；破折号后不加逗号"),
]

EDITS["chunk030"] = [
    ("④",
     "——当我得知她认识凡德伊小姐以后，安德烈便被阿尔贝蒂娜取代——",
     "——在我得知阿尔贝蒂娜认识凡德伊小姐以后，安德烈就被她取代——",
     "d'Andrée, remplacée par Albertine quand j'avais appris que celle-ci avait connu Mlle Vinteuil：段内「她」先于「阿尔贝蒂娜」出现，指代不明"),
    ("⑥",
     "一个人与其说是被另一个人打动，不如说是被那个人的遗弃打动",
     "一个人与其说是因某个人而坠入爱情，不如说是因一场遗弃而坠入爱情",
     "on soit rendu moins amoureux par un être que par un abandon：amoureux 是「爱上」，「打动」弱化了语义"),
    ("③",
     "在这种情形下，既然徒然的等待、一个拒绝的字眼固定了选择，痛苦便鞭策着想象",
     "在这种情形下，一场徒然的等待、一个拒绝的字眼便固定了选择，而痛苦鞭策着想象",
     "où c'est une attente vaine, un mot de refus qui fixe un choix：强调句式被搬成「既然」因果句，逻辑错置"),
    ("①",
     "那个没能赶上心灵的理智便惊讶起来，叫喊道",
     "那个没能追上心儿的理智便惊讶起来，嚷道",
     "l'intelligence, qui n'a pu rattraper le cœur：「赶上心灵」搭配不当"),
    ("①",
     "无论是社会条件，还是智慧所作的预见，说到底，我们对于另一个人的生活是没有任何把握的。",
     "社会条件也好，智慧的预见也罢，说到底，对于另一个人的生活，我们是没有任何把握的。",
     "Que ce soient les conditions sociales, les prévisions de la sagesse： 「无论是……还是……」缺呼应词，句式悬空"),
    ("①",
     "可是现在我明白了，我们并不能自由地不替自己铸造这些不幸",
     "可是现在我明白了，我们并不能不为自己铸造这些不幸",
     "nous ne sommes pas libres de ne pas nous les forger：双重否定照搬，中文读不通"),
]


def han_count(s):
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def run():
    report = []
    for chunk, edits in EDITS.items():
        d = os.path.join(BASE, chunk)
        path = os.path.join(d, "final.txt")
        bak = path + ".bak_20261125"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
            bak_state = "新建"
        else:
            bak_state = "已存在（未覆盖）"
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        before_han = han_count(text)
        nl = "\r\n" if "\r\n" in text else "\n"
        before_lines = text.count(nl)
        before_paras = len([p for p in text.replace("\r\n", "\n").split("\n\n") if p.strip()])
        for cat, old, new, note in edits:
            assert old in text, (chunk, "未命中", old[:40])
            assert text.count(old) == 1, (chunk, "命中多次", old[:40])
            text = text.replace(old, new)
        after_lines = text.count(nl)
        after_paras = len([p for p in text.replace("\r\n", "\n").split("\n\n") if p.strip()])
        report.append((chunk, len(edits), before_lines, after_lines,
                       before_han, han_count(text), before_paras, after_paras,
                       bak_state, "CRLF" if nl == "\r\n" else "LF"))
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)

    print("chunk | 改动 | 行数 前→后 | 汉字 前→后 | 段数 前→后 | 备份 | 换行")
    for r in report:
        print("%s | %d | %d→%d | %d→%d | %d→%d | %s | %s" % r)
    print("合计改动 %d 条" % sum(len(v) for v in EDITS.values()))
    from collections import Counter
    print("分类:", dict(Counter(c for v in EDITS.values() for c, *_ in v)))


if __name__ == "__main__":
    ast.parse(open(__file__, encoding="utf-8").read())
    run()