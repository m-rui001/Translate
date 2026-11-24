# -*- coding: utf-8 -*-
"""v7 chunk020-023 逐段润色落盘脚本（2026-11-26）。

改法：定位唯一子串 → 替换 → assert count == 1；不整文件重写。
读写 newline='' 保持 CRLF。
"""
import ast
import os
import shutil

VOL = 'v7'
BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    '020': [
        # ⑥ 搭配：「饶有」不与「品味」搭配（饶有风趣／饶有兴致）
        ('为我饶有品味地记下风景',
         '为我颇有品味地记下风景'),
        # ⑥ 增译：「immobilisé」只是「动弹不得／停驻」，原文未说「因伤」
        ('因伤滞留在一片沼泽森林边缘时',
         '在一片沼泽森林边缘停留不动时'),
        # ①②「她这一次完全如实地说出的前线生活」三个「的」压住中心语
        ('而且她从此过着她这一次完全如实地说出的前线生活。',
         '而且，正如她这一次完全如实所说的，过起了前线的生活。'),
        # ③ 关系从句（où nous sommes allés si souvent ensemble）被甩在句末，改用破折号作补注
        ('正在进行大规模战斗，我们曾常常一起去那里。',
         '正在进行大规模战斗——我们曾常常一起去那里。'),
        # ①「……的程度不如……的那样」悬空比较句
        ('它让您回忆起童年的程度不如您所希望的那样',
         '它没能像您希望的那样唤起您对童年的回忆'),
        # ③ 引语嵌进定语（法语括注直搬），去掉句内「而且，」
        ('这个“而且，永远也当不了一个好肉铺伙计”的小伙子',
         '这个“永远也当不了一个好肉铺伙计”的小伙子'),
    ],
    '021': [
        # ⑥ 量词错：根须用「层」；且与下句「这层根须」同一指称
        ('那层深刻印象和思想的根须',
         '那根深刻印象和思想的根须'),
        ('而正是这层根须赋予事物以真正的意义',
         '而正是这根须赋予事物以真正的意义'),
        # ⑥ 搭配：「增加……无足轻重」（accroître l'insignifiance）
        ('进一步增加他们言语的无足轻重',
         '进一步加深他们言语的无足轻重'),
        # ⑥ 词义误读：au front ＝ 额头上，非「脸上」
        ('他脸上还留着一道伤疤',
         '他额头上还留着一道伤疤'),
        # ①「怀疑……究竟是不是……，不如说是……」缺转折词
        ('不如说是女武神',
         '倒不如说是女武神'),
        # ② 一句两个「地面」，「在房屋贴近地面的地方」别扭
        ('不过，在房屋贴近地面的地方，仍有一些地面角落亮了起来',
         '不过，在紧贴房屋的地方，仍有一些地面的角落亮了起来'),
        # ②「费拉里式人物」连出两遍，第二处改为回指
        ('——那个费拉里式人物的社交新闻',
         '——此人的社交新闻'),
    ],
    '022': [
        # ⑦ 年份用「〇」（全册 9 处「一八七〇年」，仅此作「零」）
        ('一八七零年战争', '一八七〇年战争'),
        ('一八零零年', '一八〇〇年'),
        # ①「就其为如此而言」义不可通（pour autant que cela est）
        ('因为就其为如此而言，这并不必然表明错误',
         '因为既然确实如此，这并不必然表明错误'),
        # ③ 法语括注（2 juillet 1918）插在主谓之间，改顺句
        ('于是比杜奇怪地，一九一八年七月二日，解释某些要害点',
         '于是比杜在一九一八年七月二日奇怪地解释某些要害点'),
        # ①「胜利性决断」（décisions victorieuses）
        ('最后又使人相信胜利性决断是可能的',
         '最后又使人相信决定性的胜利是可能的'),
    ],
    '023': [
        # ⑥ 否定反转：「ne l'eût pas dépassé」＝并未胜过他，非「高过他」
        ('他舅父唯一高过他的地方，是那种圣日耳曼区的心态',
         '他舅父唯一没有胜过他的地方，是那种圣日耳曼区的心态'),
        # ①「正如另一个多疑而嫉妒」缺「的那样」，对举落空
        ('但另一方面，他的性情和蔼可亲、迷人，正如另一个多疑而嫉妒。',
         '但另一方面，他的性情和蔼可亲、迷人，一如另一个的多疑与嫉妒。'),
    ],
}


def han(s):
    return sum(1 for ch in s if '\u4e00' <= ch <= '\u9fff')


def main():
    for chunk, edits in EDITS.items():
        d = os.path.join(BASE, 'chunk' + chunk)
        f = os.path.join(d, 'final.txt')
        bak = f + '.bak_20261125'
        if not os.path.exists(bak):
            shutil.copy2(f, bak)
        with open(f, encoding='utf-8', newline='') as fh:
            text = fh.read()
        before_lines, before_han = text.count('\n'), han(text)
        crlf = '\r\n' in text
        n = 0
        for old, new in edits:
            assert text.count(old) == 1, (chunk, old, text.count(old))
            text = text.replace(old, new)
            n += 1
        with open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)
        after_lines, after_han = text.count('\n'), han(text)
        assert after_lines == before_lines, (chunk, 'line count changed')
        print('chunk%s: 改动 %d 条 | 行数 %d -> %d | 汉字 %d -> %d | %s'
              % (chunk, n, before_lines, after_lines,
                 before_han, after_han, 'CRLF' if crlf else 'LF'))


assert __name__ == '__main__'
main()
ast.parse(open(__file__, encoding='utf-8').read())