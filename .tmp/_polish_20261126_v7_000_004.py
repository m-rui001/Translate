# -*- coding: utf-8 -*-
"""逐段润色 v7 chunk000 / 001 / 002 / 004（2026-11-26）。

改法：定位唯一子串 -> 替换 -> assert count == 1。不整文件重写。
已落过的条目（chunk000/001 已在首轮写入）通过幂等判据跳过，便于重跑自查。
"""
import ast
import os
import re
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = ".bak_20261125"

EDITS = {}

EDITS["chunk000"] = [
    # ① 读不通：比较句「比从前……不回去向妈妈道晚安还要更用力」缺「为了」，悬空
    # FR: réprimer les battements de mon cœur plus encore peut-être que pour ne pas
    #     retourner dire bonsoir jadis à maman dans ce même Combray
    ("一遍遍问自己那个人究竟是谁，想到这件事，我不得不按捺住心跳，也许比从前在同一个贡布雷不回去向妈妈道晚安还要更用力。",
     "一遍遍问自己那个人究竟是谁，想到这件事，我不得不按捺住心跳——也许比当年在同一个贡布雷，为了不去向妈妈道晚安还要更用力。"),
    # ③ 外语句法直搬：s'entr'ouvrir 被搬成「树木正微微张开」，缺宾语、读不通
    # FR: croyant voir s'entr'ouvrir, s'animer les arbres
    ("以为看见树木正微微张开、正活起来。",
     "以为自己看见树木正徐徐绽开、活转过来。"),
    # ④ 指代不明：句中「它」与「她」并置，读者不易分清。曾试作「去理解自己所渴望的东西」，
    #   因同段已有「当时我那样热切渴望的东西」而「东西」两见，遂改回代词：句首名词短语把「它」
    #   锁死为「所渴望的东西」，「她」为鲁桑维尔那个姑娘，界限自此清楚。故本条净改动为 0，仅存记录。
    # FR: si j'eusse seulement su le comprendre et la retrouver
    # ⑥ 硬伤：「还不是」读成「尚未是」，原文是否定判断
    # FR: ce n'est même pas ce caprice d'enfant que je me reproche le plus
    ("就连这个孩子气的任性，也还不是我最责怪自己的事。",
     "就连这份孩子气的任性，也不是我最自责的事。"),
    # ① 外语句法直搬：pour halluciner les heures que vous passez au lit 被搬成
    #   「时光产生幻觉」，主语错位
    ("好让你躺在床上度过的时光产生幻觉。",
     "好让你躺在床上度过的那几个钟头恍恍惚惚。"),
    # ① 读不通：「就像某些男性之间的交情之于爱恋女人的男人那样」悬空无着落
    # FR: comme certaines camaraderies masculines pour les hommes qui aiment les femmes
    ("其实，许多女人挤满了他的生活；而且，就像某些男性之间的交情之于爱恋女人的男人那样，这些女人带着一种徒然设防、白白占了位置的性质，正如大多数宅子里那些毫无用处的物件一样。",
     "其实，许多女人占满了他的生活；而且，正如某些男人之间的交情之于爱恋女人的男人，这些女人之于他，也带着一种徒然设防、白白占了位置的性质，就像大多数宅子里那些毫无用处的物件一样。"),
]

EDITS["chunk001"] = [
    # ① 读不通 + 重复：两处「相反」，且「而且到了他从未有过的程度」悬空
    # FR: tout au contraire, mais, opérant en lui un changement inverse, lui avait donné
    #     l'aspect désinvolte d'un officier de cavalerie ... à un point qu'il n'avait jamais eu
    ("他的生活并没有像德·夏尔吕先生那样使他发福，恰恰相反，在他身上起了相反的作用，给了他一副骑兵军官那种随随便便的神气——尽管他结婚时就辞去了军职——而且到了他从未有过的程度。",
     "他的生活并没有像德·夏尔吕先生那样使他发福，恰恰相反，它在他身上所起的作用正好相反，给了他一副骑兵军官那种随随便便的神气——尽管他结婚时就辞去了军职——这神气在他身上到了从未有过的程度。"),
    # ① 读不通：「才能在那里施展不开」中「才能」歧义（能力/刚刚）
    # FR: les gens trop intelligents pour la vie relativement oisive qu'ils mènent
    #     et où leurs facultés ne se réalisent pas
    ("他们太聪明，过的是相对闲散的生活，才能在那里施展不开，于是永远无聊，永远腻味。",
     "他们过于聪明，与他们所过的相对闲散的生活不相称，才干在其中无从施展，于是永远无聊，永远腻味。"),
    # ④ 指代不明：「他说自己是到这一带来歇一个月的」的「他」实为那位先生，易误作罗贝尔
    # FR: ... qui, précisément rencontré dans la soirée près de Combray, dévoilait
    #     involontairement le mensonge ... en disant qu'il était venu dans le pays
    #     se reposer pour un mois
    ("——而这位先生恰好晚上在贡布雷附近被人碰见，无意中拆穿了罗贝尔的谎，因为罗贝尔疏忽了，没跟他串好——他说自己是到这一带来歇一个月的，在这以前不回巴黎。",
     "——而这位先生恰好晚上在贡布雷附近被人碰见，随口说自己来这一带是要歇上一个月，在这以前不回巴黎，无意中拆穿了罗贝尔的谎，因为罗贝尔疏忽了，没跟他串好口供——"),
    # ① 读不通：「莫雷尔在圣卢家去的所有地方」定语压住主语
    # FR: pourquoi il se faisait que Morel fût reçu comme l'enfant de la maison
    #     partout où étaient les Saint-Loup
    ("再说，我就更不明白，为什么莫雷尔在圣卢家去的所有地方——巴黎也好，当松维尔也好——都被当作家里的孩子一样接待。",
     "再说，我就更不明白，为什么凡有圣卢夫妇在的地方——巴黎也好，当松维尔也好——莫雷尔都被当作家里的孩子一样接待。"),
    # ③ 外语句法直搬：mais plutôt « comme Legrandin aidait beaucoup Théodore » 的
    #   对比结构照搬，引语无着落
    ("反倒觉得“勒格朗丹也很帮泰奥多尔的忙”，她这个如此守道德、如此满是偏见的人",
     "反倒宁可以为不过是“勒格朗丹也很帮泰奥多尔的忙”一类的事，她这个如此守道德、如此满是偏见的人"),
]

EDITS["chunk002"] = [
    # ③ 外语句法直搬：关系从句后置（Théodore, qui vivait maintenant dans le Midi）
    ("就在这样的一次谈话里，我问起泰奥多尔如今住在南方，他的姓是什么，这才猛然明白：",
     "就在这样的一次谈话里，我问起泰奥多尔的姓氏——他如今住在南方——这才猛然明白："),
    # ① 读不通：「要不是我出其不意地赶到，就把她……救了出来」主语断裂
    # FR: un soir où elle se sentait si triste que je l'avais, en arrivant à
    #     l'improviste, miraculeusement sauvée du désespoir
    ("那个晚上她本来那么伤心，要不是我出其不意地赶到，就把她奇迹般地从绝望中救了出来，“也许是从最坏的境地”，他补了一句。",
     "那个晚上她本来那么伤心，是我出其不意地赶到，才奇迹般把她从绝望中救了出来，“也许是从最坏的境地”，他补了一句。"),
    # ④ 指代不明：一句里两个「他」指不同人（罗贝尔/他另爱的那个女人）
    # FR: la femme qu'il aimait aussi, il l'aimait moins qu'elle et romprait bientôt
    ("他另有一个女人他也爱，但他爱她不如爱妻子，而且很快就会跟她断掉。",
     "他另外还爱着一个女人，但他爱那女人不如爱自己的妻子，而且很快就会跟她断了。"),
]

EDITS["chunk004"] = [
    # ③/⑦ 法语括注被照搬成破折号插在主谓之间，把一句话拆成两轮对话
    # FR: En tout cas si je l'ai dit — mais vous faites erreur — je parlais au contraire
    #     d'amourettes avec des jeunes gens.
    ("无论如何，即使我说过——”“可您错了——”“我说的倒是她和年轻男子之间那些风流韵事。再说，在那个年纪，这种事大概也不会走得很远。”",
     "无论如何，就算我说过，我说的也是她和年轻男子之间那些风流韵事——是您弄错了。再说，在那个年纪，这种事大概也不会走得很远。”"),
    # ① 读不通：「话……走的都是一条相反的路」，主语与谓语失配
    # FR: les paroles de Gilberte ... suivaient une marche inverse des affirmations d'Albertine
    ("吉尔贝特的话，从当年所谓“风气不好”，到今天替她开出的品行端正的证明，走的都是一条与阿尔贝蒂娜的说法相反的路",
     "吉尔贝特的话，从当年所谓的“风气不好”，到今天替她担保品行端正，与阿尔贝蒂娜的说法恰恰走的是相反的路"),
    # ④ 指代不明：「让她听从自己心意」的「自己」指阿尔贝蒂娜还是那些人
    # FR: toutes celles qui auraient pu lui faire faire ce qu'elles auraient voulu
    ("凡是本来可以让她听从自己心意的人",
     "凡是本来能让她按她们的心意行事的人"),
    # ⑥ 硬伤：absurde 是「荒唐」，译作「不合理」弱化且反义偏移
    # FR: Aucune de ces hypothèses n'était absurde
    ("上述种种猜想没有一种是不合理的",
     "上述种种猜想没有一种是荒唐的"),
    # ① 读不通：「奇怪的是，而我也无法在这里详述的是」双「的是」直搬
    # FR: Ce qui est curieux et ce sur quoi je ne puis m'étendre, c'est...
    ("奇怪的是，而我也无法在这里详述的是，大约就在那个时候，",
     "说来奇怪，而我在这里也无法细说：大约就在那个时候，"),
    # ⑥ 硬伤：que j'eusse reçue sans plaisir 被读成「不会愉悦地接待」，语义偏移
    ("我也不会愉悦地接待她",
     "我接待她也不会觉得高兴"),
    # ⑥ 错别字/词义：mauvais sort 是「厄运」（恶咒），非「恶运」
    # FR: qu'aimer est un mauvais sort
    ("爱情是一种恶运",
     "爱情是一种厄运"),
]


def hanzi(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def work(chunk):
    d = os.path.join(BASE, chunk)
    p = os.path.join(d, "final.txt")
    bak = p + BAK
    if not os.path.exists(bak):
        shutil.copy2(p, bak)
    with open(p, encoding="utf-8", newline="") as f:
        text = f.read()
    nl = "\r\n" if "\r\n" in text else "\n"
    h0 = hanzi(text)
    lines0 = text.count(nl) + 1
    n = 0
    skipped = 0
    for old, new in EDITS[chunk]:
        c_old = text.count(old)
        c_new = text.count(new)
        if c_old == 0 and c_new == 1:
            skipped += 1          # 幂等：上一轮已落盘
            continue
        assert c_old == 1, (chunk, old[:24], c_old)
        text = text.replace(old, new)
        n += 1
    assert text.count(nl) + 1 == lines0, (chunk, "line count changed")
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    h1 = hanzi(text)
    print("%s: 本轮改动 %d 条 (已落 %d) | 行数 %d | 汉字 %d -> %d (%+d) | %s"
          % (chunk, n, skipped, lines0, h0, h1, h1 - h0,
             "CRLF" if nl == "\r\n" else "LF"))
    for bad in ('"', " '", "...", " -- ", "\u3000"):
        if bad in text:
            print("  WARN 残留:", repr(bad))
    print("  引号：左“%d 右”%d | 左‘%d 右’%d"
          % (text.count("\u201c"), text.count("\u201d"),
             text.count("\u2018"), text.count("\u2019")))
    return n


if __name__ == "__main__":
    total = 0
    for c in ("chunk000", "chunk001", "chunk002", "chunk004"):
        total += work(c)
    print("本轮合计改动 %d 条" % total)
    ast.parse(open(__file__, encoding="utf-8").read())