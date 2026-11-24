# -*- coding: utf-8 -*-
"""逐段润色 v1 chunk051-053：定位唯一子串 → 替换 → 断言命中数，逐 chunk 立即落盘。"""
import ast
import os
import shutil
import sys

VOL = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

EDITS = {
    'chunk051': [
        # ⑤ 本堂神甫 → 本堂神父（v1 canon 13:7；邻段 chunk043-045 全作「神父」）
        ('本堂神甫', '本堂神父'),
        # ⑥ condoléances 是慰问，不是责怪运气
        ('母亲对她说些安慰的话，怪她运气不好，客人总是约好了似的一齐来：',
         '母亲对她说些安慰的话，说她运气不好，客人总是约好了似的一齐来：'),
        # ⑤ grand'tante 全册作「姑祖母」(36:3)；⑥ 「好事成堆」非谚，Abondance de biens ne nuit pas = 多了不碍事
        ('姑婆打断了她：“好事成堆……”',
         '姑祖母打断了她：“东西多了不碍事……”'),
        # ① 「打招呼几乎只是敷衍了一下」主谓搭配断裂；à peine dit bonjour = 几乎没打招呼
        ('今天早上他跟我打招呼，几乎只是敷衍了一下。',
         '今天早上他几乎没跟我打招呼。'),
        # ⑥ petit veston droit 是挺直的小外套，droit ≠ 紧身；与 chunk053「笔挺的上衣」取一致
        ('他穿着那件紧身小外套', '他穿着那件笔挺的小外套'),
        # ① 「就在她身边的篮子里」悬空（篮子里的是芦笋，不是女仆）
        ('被弗朗索瓦丝派去剥芦笋，就在她身边的篮子里；',
         '被弗朗索瓦丝派去剥芦笋，那些芦笋就放在她身边的篮子里；'),
    ],
    'chunk052': [
        # ⑤ 同段他处两作「厨房女佣」，fille de cuisine 非「厨娘」
        ('就在厨娘生孩子之后不久，那女佣肚子疼得厉害',
         '就在厨房女佣生孩子之后不久，那女佣肚子疼得厉害'),
        # ⑥ ciboire 是圣体盒，calice 才是圣餐杯
        ('从圣餐杯似的腔子里滴出珍贵的汁水', '从圣体盒似的腔子里滴出珍贵的汁水'),
        # ① 后半「在……厌烦与恼怒中，只觉又烦又气」叠床架屋，主语流断
        ('也得不到任何同一类的乐趣，在半夜为厨房女佣起床的厌烦与恼怒中，只觉又烦又气；',
         '也得不到任何同一类的乐趣；半夜为厨房女佣起身，她又厌烦又恼怒；'),
        # ① 「也真得上帝扔下不管的一个小子，才……」语法断裂
        ('也真得上帝扔下不管的一个小子，才去跟这种东西混。',
         '也真得是上帝扔下不管，一个小子才会去跟这种东西混。'),
        # ⑥/⑦ 全书「其他」15:1，归一
        ('而其它生命机能并不依赖的神经中枢', '而其他生命机能并不依赖的神经中枢'),
        # ⑤ 同句先说「掘土蜂」，后文却作「胡蜂」，同一只蜂
        ('胡蜂把卵产在它旁边', '掘土蜂把卵产在它旁边'),
    ],
    'chunk053': [
        # ⑤ 古皮尔夫人 8:3、佩尔塞皮埃 6:3（v1 内多数）
        ('以致古皮尔太太、佩尔塞皮耶太太', '以致古皮尔夫人、佩尔塞皮埃夫人'),
        # ⑥ 领带量词错：une lavallière 是「一条」
        ('一圈被广场上的风吹得飘动的圆点花纹拉瓦利埃领带',
         '一条被广场上的风吹得飘动的圆点花纹拉瓦利埃领带'),
        # ⑤ 同册「母亲」169:13
        ('我们快到家时，妈妈发觉', '我们快到家时，母亲发觉'),
        # ⑥ à tout mettre au pis = 往最坏处想，非「把话说到底」
        ('就算把话说到底，他当真失礼了', '就算往最坏处想，他当真失礼了'),
    ],
}


def cjk(t):
    return sum(1 for ch in t if '\u4e00' <= ch <= '\u9fff')


def main():
    for chunk, edits in EDITS.items():
        d = os.path.join(VOL, chunk)
        f = os.path.join(d, 'final.txt')
        b = os.path.join(d, BAK)
        if not os.path.exists(b):
            shutil.copy2(f, b)
        with open(f, encoding='utf-8', newline='') as fh:
            text = fh.read()
        before_cjk = cjk(text)
        before_lines = len(text.replace('\r\n', '\n').split('\n'))
        n = 0
        for old, new in edits:
            assert old in text and text.count(old) == 1, (chunk, old)
            text = text.replace(old, new)
            n += 1
        with open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)
        after_lines = len(text.replace('\r\n', '\n').split('\n'))
        assert after_lines == before_lines, chunk
        print(f'{chunk}: edits={n} lines={before_lines}->{after_lines} '
              f'cjk={before_cjk}->{cjk(text)} crlf={text.count(chr(13) + chr(10))}')


if __name__ == '__main__':
    main()
    ast.parse(open(__file__, encoding='utf-8').read())
    print('self-check ast OK')