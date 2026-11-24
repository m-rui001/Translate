# -*- coding: utf-8 -*-
"""v6 chunk031-034 逐段润色（2026-11-26 轮）

做法：定位唯一子串 -> assert count == 1 -> 替换。绝不整文件重写。
换行符 CRLF 原样保留（open(..., newline='')）。
"""
import ast
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

# chunk -> [(类别, old, new, 备注)]
EDITS = {}

EDITS["chunk031"] = [
    ("⑥",
     "不过全都局限在我们那可怜的虚伪之中。",
     "不过全都封闭在我们那可怜的不真诚之中。",
     "insincérité 是「不真诚/不坦率」，非「虚伪」（hypocrisie）"),
    ("①",
     "“我感到我可以对您的心灵有所帮助”，在巴黎对她说",
     "我又对她说：“我感到我可以对您的心灵有所帮助”；在巴黎，我对她说",
     "引语悬空：上一句已收，此处直接起引号，无主句承托（法语并列引语）"),
    ("③",
     "而现在，难道她的聪慧、她的善良、她的美丽，不正是托付给了我的忠贞，"
     "托付给了我的力量，虽说我的记忆的力量也是脆弱的吗？",
     "而现在，难道她的聪慧、她的善良、她的美丽，不正是托付给了我记忆的忠贞、"
     "托付给了我记忆的力量吗？——唉，那力量也同样是脆弱的。",
     "à la fidélité, aux forces, fragiles hélas aussi, de ma mémoire：忠贞与力量同属「我记忆的」，"
     "「hélas aussi」是插入的叹语，被搬成让步句「虽说」"),
    ("①",
     "，现实在吞没了一个人以后重新变得平坦，便在那一处连一丝涟漪也没有地伸展开来",
     "；一旦吞没了一个人，现实便重新变得平坦，在那一处连一丝涟漪也没有地铺展开来",
     "逗号连缀：上句「比死本身更残酷」未完，此处另起主谓（moins que…que s'étend une réalité）"),
]

EDITS["chunk032"] = [
    ("⑥",
     "而这样想不仅更温柔，也更美。",
     "而这样反倒不仅更温柔，也更美。",
     "plus doux, mais plus beau 说的是「事情不完整」这件事，不是「这样想」；主语被换成「想」"),
    ("⑥",
     "足以抵消失想到她知道一切时的恐惧吗？",
     "足以抵消想到她知道一切时的恐惧吗？",
     "「抵消失想到」衍字（「失」），读不通"),
    ("②",
     "但我仍然继续为这些短暂的好奇心那残酷的满足牺牲一切",
     "但我仍然继续为这些短暂的好奇心所带来的残酷满足牺牲一切",
     "「好奇心那残酷的满足」两个限定语硬接，中心语被压没"),
    ("②",
     "会把我带到与我和吉尔贝特自愿分离所造成的那种同样的无动于衷。",
     "会让我陷入与我和吉尔贝特自愿分离时同样的无动于衷。",
     "「带到与……所造成的那种同样的无动于衷」四个「的」串叠，中心语「无动于衷」被压没"),
]

EDITS["chunk033"] = [
    ("⑥",
     "因为没有死亡，它们终究也会变得乏味",
     "因为即便没有死亡，它们终究也会变得乏味",
     "sans elle ils auraient fini par s'émousser：sans＝「即使没有」，非因果「因为」"),
    ("①",
     "既符合记忆那天然的、又是武断的界限，而记忆是无法走出过去的。",
     "既符合记忆那种天然而又武断的界限——它本来就无法走出过去。",
     "「既……、又是……」把 limites naturelles et arbitraires 拆成递进，且「而」字转折无理"),
    ("③",
     "但出于某些富有传奇色彩的理由，就像那些人们长久以来以为已经死去的人物，"
     "有时确实发生过的情形，她不愿让我知道自己已经痊愈",
     "但出于某些富有传奇色彩的理由——就像那些人们长久以为已经死去的人物，"
     "有时确实会有这种情形——她不愿让我知道自己已经痊愈",
     "法语括注（et comme… il est quelquefois arrivé）被平铺进主句，插在主谓之间，读来断裂"),
    ("③",
     "我却还是想知道——“因为是那些人，是圣卢对我说起过的那些人，是那些在我眼里有各自独特存在的人”"
     "——那个常去妓院的姑娘，以及普特布斯夫人的女佣。",
     "我却还是想知道那个常去妓院的姑娘，以及普特布斯夫人的女佣"
     "——因为是那些人，是圣卢对我说起过的那些人，是那些在我眼里有各自独特存在的人。",
     "括注插在「想知道」与宾语之间，把宾语隔断；移到句末"),
    ("①",
     "正如它曾让我碰上那次关于睡袍的谈话，却全靠阿尔贝蒂娜脸红才得以如此。",
     "正如它凭阿尔贝蒂娜的脸红，让我碰上了那次关于睡袍的谈话。",
     "comme il l'avait fait pour cette conversation… grâce à la rougeur：因果被倒成「却全靠……才得以如此」，悬空"),
    ("⑤",
     "那个替人淋浴的女人所说的话",
     "那个淋浴女工所说的话",
     "doucheuse：全册（chunk034/036/037/044/077）作「淋浴女工」，此处归一"),
]

EDITS["chunk034"] = [
    ("④",
     "尽管它赋予它们一种形式，却并不相信它们",
     "尽管心灵赋予它们一种形式，却并不相信它们",
     "「它」前有「假设／心灵」两可，法语 il 指 mon esprit"),
    ("⑦",
     "这痛苦同那些情景，同唉，阿尔贝蒂娜本人的形象，凝成了一种化学上所谓的沉淀物",
     "这痛苦同那些情景、同阿尔贝蒂娜本人的形象（唉！）凝成了一种化学上所谓的沉淀物",
     "« l'image hélas, d'Albertine » 的叹语被塞进并列成分之间，读来碎裂"),
    ("⑥",
     "先生托我去见的那位小姐外出了两天",
     "先生托我去见的那个人外出了两天",
     "la personne que Monsieur m'avait chargé de voir＝托我去见的那个人（淋浴女工），非「小姐」"),
    ("⑥",
     "我刚刚总算同这位小姐谈过",
     "我刚刚总算同这个人谈过",
     "同上：cette personne，不是小姐"),
    ("⑥",
     "那位灰衣女人至少给同她谈话的那个人十法郎小费",
     "那位灰衣女人至少给和我谈过话的那位十法郎小费",
     "à la personne avec qui j'ai causé＝与「我」（艾梅）交谈的那位，不是「同她谈话」"),
    ("⑥",
     "那女人带着一面手镜",
     "那女人拿着一副长柄眼镜",
     "un face-à-main＝长柄眼镜（lorgnette），非「手镜」（miroir de poche）"),
    ("⑥",
     "吩咐把隔间的门留着，说",
     "吩咐把隔间的门开着，说",
     "laisser la porte ouverte＝让门开着，「留着」意反"),
    ("①",
     "所以，艾梅的答复所触及的，虽然不是一个概括性的回答，而是一个具体的回答，正因为如此，"
     "所触及的恰恰是我内心深处的阿尔贝蒂娜。",
     "所以，艾梅的答复所触及的，虽然不是一个概括性的回答，而是一个具体的回答——"
     "却正因为如此——恰恰正是我内心深处的阿尔贝蒂娜。",
     "「所触及的，虽然……，所触及的恰恰是」主谓两次起头而收不住（not…but… 直搬）"),
]


def main():
    for chunk, edits in EDITS.items():
        d = os.path.join(BASE, chunk)
        f = os.path.join(d, 'final.txt')
        b = os.path.join(d, BAK)
        with open(f, encoding='utf-8', newline='') as fh:
            text = fh.read()
        before_han = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        before_lines = text.count('\n')
        if not os.path.exists(b):
            shutil.copy2(f, b)
            backed = 'new'
        else:
            backed = 'kept'
        n = 0
        for cat, old, new, why in edits:
            assert old in text, (chunk, cat, old[:30])
            assert text.count(old) == 1, (chunk, 'dup', old[:30])
            text = text.replace(old, new)
            n += 1
        with open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)
        after_han = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        after_lines = text.count('\n')
        print('%-9s edits=%2d lines %d->%d han %d->%d bak=%s'
              % (chunk, n, before_lines, after_lines, before_han, after_han, backed))
        assert before_lines == after_lines, chunk


main()
ast.parse(open(__file__, encoding='utf-8').read())