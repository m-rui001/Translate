# -*- coding: utf-8 -*-
"""v4 chunk163 / chunk164 / chunk166 / chunk171 逐段润色（2026-11-26）

铁律：定位唯一子串 → 替换 → assert count==1；不整文件重写；
读写 newline='' 保持原换行符；备份 .bak_20261125 已存在则不覆盖。
"""
import ast
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = ".bak_20261125"


def han(s):
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


# chunk -> [(类别, old, new, 理由)]
EDITS = {
    "chunk163": [
        ("③",
         "德·夏尔吕先生害怕得像一个非得穿过林荫大道的外省人，打个比方说吧——这比喻远不如题材本身那么亵渎不敬，那题材就刻在科尔莱斯维尔古教堂前廊的雕饰上。",
         "德·夏尔吕先生害怕得像一个非得穿过林荫大道的外省人；打个比方吧，这比喻远不如科尔莱斯维尔古教堂门廊柱头上刻的那些题材来得亵渎不敬。",
         "原文 pour prendre une comparaison infiniment moins sacrilège que le sujet représenté dans les chapiteaux… 是比较结构带长定语；译文把括注拆成破折号后留下「这比喻远不如题材本身」一句，「题材本身」无着落，与后半句「那题材就刻在……」又重复指涉，整句读作半截。"),
        ("⑤",
         "被一位年迈的“总管”不断的叫嚷压了下去。那总管戴一顶深褐色的假发",
         "被一位年迈的“副女管事”不断的叫嚷压了下去。那副女管事戴一顶深褐色的假发",
         "sous-maîtresse 在 v6 chunk085 同一家妓院里译作「副女管事」（2 次）；此处作「总管」与全书 maître d'hôtel / 膳食总管（v3、v7 共 10 余处）混形，读者会当成男管家。"),
        ("⑤",
         "不厌其烦地重复着总管的吩咐",
         "不厌其烦地重复着副女管事的吩咐",
         "同上一条，同段内两处统一为「副女管事」。"),
        ("⑥",
         "这期间，莫雷尔其实是和盖尔芒特亲王在一起，亲王为了做做样子，装作走错了房间，进了一间有两个女人的屋子，她们急忙离开，让两位先生单独待着。",
         "这期间，莫雷尔其实是和盖尔芒特亲王在一起。为了做做样子，他装作走错了房间，进了一间有两个女人的屋子，她们急忙让开，留下两位先生单独待着。",
         "il avait, pour la forme, fait semblant de se tromper de chambre 的主语是 Morel（il 承前指莫雷尔），译文把「装作走错房间」派给了亲王，主语误置。"),
        ("⑥",
         "他在和三位女士在一起，他在给她们讲他的军旅生涯。",
         "他正和三位女士在一起，在给她们讲他的军旅生涯。",
         "「在和……在一起」两个「在」叠字，语法断裂（口语也不这么说）。il est avec trois dames。"),
        ("④",
         "到处重复着巫术的徽记。他离他几米远，侧着身子。",
         "到处重复着巫术的徽记。那个莫雷尔就在他几米之外，侧着身子。",
         "原句是 qui était à quelques mètres de lui, de profil 的定语尾巴，被括注断开后只剩两个「他」，指代打架；补出「那个莫雷尔」即指夏尔吕眼前的那一个。"),
        ("⑥",
         "女人们的问题接踵而来，可莫雷尔没有生气，没有力气回答。",
         "女人们的问题接踵而来，可莫雷尔僵在那里，没有力气回答她们。",
         "inanimé 是「毫无生气、僵死」，「没有生气」在中文里首先读成「不曾发怒」（生气＝发火），与前文「livide / figé」不合。"),
        ("①",
         "连一句低声说出的话那样的奇迹也没有发生。",
         "连低声咕哝一句这样的奇迹也没有出现。",
         "Le miracle même d'une parole murmurée：「一句低声说出的话那样的奇迹」把中心语「奇迹」压在一串定语之后，读不通。"),
        ("⑥",
         "盖尔芒特亲王已经化装成三位女士走了出去，而可怜的莫雷尔被安置在那儿",
         "人们已把盖尔芒特亲王打发出去，让他一变而为三位女士；可怜的莫雷尔则被安置在那儿",
         "on avait fait sortir le prince de Guermantes métamorphosé en trois femmes 是「亲王被打发走、位置由三位女士顶替」，「化装成三位女士」在中文里不成事实（一个男人扮成三个女人），误读。"),
    ],
    "chunk164": [
        ("①",
         "在格拉特瓦斯，他姐姐住在那里，他去那儿跟她共度了一个下午，有时会上来一位德·韦尔瑞斯先生，即克雷西伯爵（人们只称他克雷西伯爵），一位贫穷却极有教养的贵族，我是通过德·康布雷梅一家认识他的，尽管他跟他们并无多少交情。",
         "在格拉特瓦斯特，有时会上车的是一位皮埃尔·德·韦尔瑞斯先生，即克雷西伯爵（人们只称他克雷西伯爵）；他姐姐住在那儿，那天下午他就是去那儿跟她一起过的。这位贵族贫穷却气度极为不凡，我是通过德·康布雷梅一家认识他的，尽管他跟他们并无多少交情。",
         "À Grattevast, où habitait sa sœur, avec laquelle il était allé passer l'après-midi, montait quelquefois M. Pierre de Verjus… 主语（上车的人）在句末。译文照搬 où 从句在前，段首连着两个无所指的「他」，主句主语反而被推到「有时会上来一位……」，读来悬空；另补出原文的人名 Pierre。"),
        ("①",
         "但人们就这件事告诉我的那些回忆，已经被别的回忆取代了，因为巴尔贝克—贡布雷—诺曼底铁路重新开始它那“小火车”的行程",
         "但别人就这件事讲给我听的那些话，在我记忆里已经被别的回忆取代了，因为“B.C.N.”铁路重新开始它那“小火车”的行程",
         "souvenirs de ce qu'on m'avait raconté：「告诉我的回忆」搭配不通（回忆不是别人给的）；另 B. C. N. 是原作故意不给全称的缩写，v3 chunk070 处理 B. A. G. / T. S. N. 时亦保留西文缩写，此处「巴尔贝克—贡布雷—诺曼底」凭空添出「贡布雷」，属虚构。"),
        ("②",
         "他极有教养，表达极为出色，一头白发",
         "他十分精敏，谈吐极佳，一头白发",
         "同段上文已用「一位贫穷却极有教养的贵族」译 extrême distinction，此处 très fin et s'exprimant à merveille 又落成「极有教养」，一段里两个「极有教养」指同一人却分别对应两个法语词，改开。"),
        ("⑥",
         "“我们的纹章是一枝未熟葡萄枝，‘象征性的’，因为我姓韦尔瑞斯，‘带茎叶，绿色底’。”",
         "“我们的纹章是一枝未熟葡萄枝——‘象征性的’，因为我姓韦尔瑞斯——茎与叶皆为绿色。”",
         "tigellée et feuillée de sinople 说的是「茎与叶为绿色」（sinople＝纹章学之绿），不是「绿色底（色）」，词义误读；原法文引号错乱（« … « … « … »），译文照搬成一个个断开的引号，句读不成句。"),
        ("③",
         "便恳求莫雷尔——尽管他始终不愿让莫雷尔知道自己的身份——第二天夜里到他租下的那座小别墅幽会。",
         "便恳求莫雷尔第二天夜里到他租下的那座小别墅幽会，尽管他始终不愿让莫雷尔知道自己的身份。",
         "法语括注 sans toujours vouloir lui faire connaître qui il était 被搬成破折号插在「恳求莫雷尔」与「幽会」之间，把动词和它的补足语隔断；中文顺句或后置即可。"),
    ],
    "chunk166": [
        ("③",
         "而且不像盖尔芒特公爵那样在名字前加先生、太太或小姐，公爵用同样的方式、带着冷冰冰的鄙夷口吻谈论“伊薇特·吉尔贝尔小姐的歌曲”和“夏尔科先生的实验”。",
         "而且不像盖尔芒特公爵那样在名字前加先生、太太或小姐——公爵提起“伊薇特·吉尔贝尔小姐的歌曲”和“夏尔科先生的实验”，用的正是这种彬彬有礼而又轻蔑的口吻。",
         "lequel parlait du même ton cérémonieusement méprisant：译文「用同样的方式」悬空（同样的什么方式？），cérémonieusement（彬彬有礼地）也丢了，只余「冷冰冰」，与「公爵在名字前加先生、太太或小姐」这一礼貌习惯自相矛盾。"),
        ("⑤",
         "有弗雷瓦尔、玛丽·玛尼耶、巴隆的儿子。”",
         "有弗雷瓦尔、玛丽·玛尼耶、小巴隆。”",
         "Baron fils 是演员艺名（老巴隆之子），法文本不作所有格；「巴隆的儿子」在中文里读成一句人物关系说明而非艺名，改用通行的「小巴隆」。全册仅此一处，无冲突。"),
        ("①",
         "因为在他身上，贵族那种想表示鄙视的欲望，被省城人那种想显得熟稔的欲望压倒了。",
         "因为在他身上，无论对演员还是对一切巴黎的东西，贵族那种想表示鄙视的欲望，都被省城人那种想显得熟稔的欲望压倒了。",
         "à l'égard des acteurs comme de tout ce qui était parisien 这一范围状语被整句丢掉，剩下一句悬空的总括，读者不知这「鄙视」与「熟稔」是对谁而发。"),
    ],
    "chunk171": [
        ("①",
         "如果说布洛克一方面让我沮丧，因为他无法理解那个阻止我去拜访他父亲的原因，另一方面又通过坦白他在邦唐夫人那里损害了我的名声而让我恼火不已，我现在明白了为什么阿尔贝蒂娜从不曾向我提起那次午餐，当我跟她谈起布洛克对我的好感时她总是沉默不语。然而这位年轻的以色列人在德·夏尔吕先生身上所产生的印象却完全不同于厌烦。",
         "布洛克一方面让我难过，因为他怎么也弄不明白是什么原因使我没能去向他父亲致意；另一方面又向我承认，他在邦唐夫人那里把我弄得声名扫地，这让我恼火透了（我现在明白，为什么阿尔贝蒂娜从不曾向我提起那次午餐，我一跟她谈起布洛克对我的好感，她就默不作声）。不过这位年轻的以色列人在德·夏尔吕先生身上引起的印象，却完全不是厌烦。",
         "原文是 Si Bloch … m'avait exaspéré …, le jeune Israélite avait produit …：法语括注（je comprenais maintenant pourquoi…）夹在主句中间。译文把括注并入「如果说」这一条件从句，条件句因此永远等不到它的主句，末尾只好另起一句「然而……」收场，全段骨架断裂。"),
    ],
}


def main():
    dry = "--dry" in sys.argv
    total = 0
    for chunk, edits in EDITS.items():
        d = os.path.join(BASE, chunk)
        path = os.path.join(d, "final.txt")
        bak = path + BAK
        text = open(path, encoding="utf-8", newline="").read()
        nl = "\r\n" if "\r\n" in text else "\n"
        lines_before = len(text.split(nl)) - 1 if text.endswith(nl) else len(text.split(nl))
        han_before = han(text)

        if not os.path.exists(bak) and not dry:
            shutil.copy2(path, bak)
            print(f"  备份 {chunk}/final.txt{BAK}")
        elif os.path.exists(bak):
            print(f"  备份已存在，未覆盖：{chunk}/final.txt{BAK}")

        new = text
        for i, (cat, old, rep, why) in enumerate(edits, 1):
            assert new.count(old) == 1, f"{chunk} 第{i}条命中 {new.count(old)} 次：{old[:30]}"
            assert old != rep
            new = new.replace(old, rep)
        assert new.count(nl) == text.count(nl), f"{chunk} 行数变了"
        assert len(new.split(nl)) == len(text.split(nl)), f"{chunk} 段/行结构变了"
        assert han(new) > 0

        if not dry:
            open(path, "w", encoding="utf-8", newline="").write(new)
        total += len(edits)
        print(f"{chunk}: 改动 {len(edits)} 条；行数 {lines_before}=={lines_before}；"
              f"汉字 {han_before}→{han(new)}；换行 {'CRLF' if nl == chr(13) + chr(10) else 'LF'}")
    print(f"合计改动 {total} 条（dry={dry}）")


if __name__ == "__main__":
    main()
    ast.parse(open(__file__, encoding="utf-8").read())