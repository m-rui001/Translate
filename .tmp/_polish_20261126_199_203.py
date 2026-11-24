# -*- coding: utf-8 -*-
"""逐段润色落盘脚本：v3 chunk199-203（2026-11-26 轮）。

只做「定位唯一子串 → 替换 → 断言命中数」的改动；不整文件重写。
备份 final.txt.bak_20261125（已存在则不覆盖）。
"""
import ast
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

# chunk -> [(类别, old, new, 备注)]
EDITS = {
    199: [
        ('④',
         '他尽可以拿这个来推托',
         '这位尽可以拿这个来推托',
         '同段两个「他」分指圣约瑟夫与蒙塞尔弗伊将军，末句指代不明'),
        ('①④',
         '偏偏他要去办他斯万自己的婚事',
         '偏偏斯万要去办自己那桩婚事',
         '「他斯万自己」是法文 il fasse le mariage de Swann 的硬搬，指代也含混'),
    ],
    200: [
        ('⑤',
         '拉莫斯亲王妃当年取笑婆母趣味低劣的',
         '拉乌姆亲王夫人当年取笑婆母趣味低劣的',
         'princesse des Laumes，v3 内「拉乌姆」4 见、本处「拉莫斯」1 见，归多数；形制依 chunk174「拉乌姆亲王夫人」'),
        ('⑥',
         '可我的心思很不正经，您知道',
         '可我的想法很不正统，您知道',
         'très mal pensante 指思想不正统（与「很差的保王党」对举），非「不正经」'),
        ('①',
         '他们只是半惊半呆，因为他们知道',
         '他们只是半惊讶，因为他们知道',
         "n'étaient qu'à demi stupéfaits：只是半惊讶（并未全惊）；「半惊半呆」不成词"),
    ],
    201: [
        ('⑦①',
         '那打蜡刷子每天早上都得来一遍。斯万，”她说到年轻公爵的床，回到这个话题，'
         '“对这美人鱼跟居斯塔夫·莫罗《死神》的相似大为吃惊。不过再说，”',
         '那打蜡刷子每天早上都得来一遍。”斯万——她说到年轻公爵的床，又回到这个话题——'
         '对这美人鱼跟居斯塔夫·莫罗《死神》的相似大为吃惊。“不过再说，”',
         'Swann a été frappé 是叙述句主语，误做成称呼并塞进引号，读者会以为她在叫斯万'),
        ('①',
         '终究替代不了那道我们不明白人家要跟我们说什么时眼中所缺少的光。',
         '终究替代不了我们不明白人家要跟我们说什么时眼中所缺少的那道光。',
         '「那道……所缺少的……光」定语前后夹击，中心语被压没；调序即通'),
        ('⑥',
         '因为那不过是脑伤风',
         '因为那不过是鼻伤风',
         'rhume de cerveau＝鼻伤风（感冒），「脑伤风」非汉语说法'),
        ('①',
         '或者亲爱的布里戈德母亲年轻时候的事',
         '或者亲爱的布里戈德的母亲年轻时候的事',
         'de la mère du cher Brigode：缺「的」时「布里戈德母亲」易读成同位语'),
    ],
    202: [
        ('⑥',
         '可天知道我为了这幅画费了多少力气去论证',
         '可天知道我为了这幅画跟人打过多少场嘴仗',
         'rompre des lances pour＝为……力争、与人舌战，非「论证」'),
    ],
    203: [
        ('⑦',
         '路易—菲利普',
         '路易-菲利普',
         '复合专名用半角连字符（本册另 3 处均作「路易-菲利普」）'),
        ('①',
         '正如梅塞格利斯那边与盖尔芒特家那边之少。',
         '正如梅塞格利斯那边与盖尔芒特家那边的关联之少。',
         'aussi peu … que 的比较项缺中心语，「……之少」悬空'),
        ('①',
         '还有，唉，维贝尔，所感到的惊讶',
         '还有，唉，维贝尔时，所感到的惊讶',
         "j'éprouvais à y trouver … ：缺「时」，主谓断裂"),
        ('①',
         '我对他的作品没有看法，因为我并不认识',
         '我对他的作品没有看法，因为我没见过',
         'que je ne connais pas 指作品；原文「并不认识」易读成不认识埃尔斯蒂尔'),
    ],
}


def stats(txt):
    norm = txt.replace('\r\n', '\n')
    lines = norm.split('\n')
    paras = [x for x in lines if x.strip()]
    cjk = sum(1 for ch in txt if '\u4e00' <= ch <= '\u9fff')
    return len(lines), len(paras), cjk, ('CRLF' if '\r\n' in txt else 'LF')


def main():
    for n in sorted(EDITS):
        d = os.path.join(ROOT, 'chunk%d' % n)
        f = os.path.join(d, 'final.txt')
        b = os.path.join(d, BAK)
        if not os.path.exists(b):
            shutil.copy2(f, b)
            print('backup ->', b)
        else:
            print('backup exists, keep ->', b)
        with open(f, encoding='utf-8', newline='') as fh:
            text = fh.read()
        before = stats(text)
        cnt = 0
        for cat, old, new, why in EDITS[n]:
            assert old in text, (n, cat, old[:30])
            assert text.count(old) == 1, (n, cat, old[:30], text.count(old))
            text = text.replace(old, new)
            cnt += 1
        with open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)
        after = stats(text)
        print('chunk%d: 改动 %d 条 | 行数 %d->%d 段数 %d->%d 汉字 %d->%d %s'
              % (n, cnt, before[0], after[0], before[1], after[1],
                 before[2], after[2], after[3]))


main()
ast.parse(open(__file__, encoding='utf-8').read())