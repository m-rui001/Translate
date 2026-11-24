# -*- coding: utf-8 -*-
"""v3 chunk102/110/112/124/125 逐段润色落盘脚本（2026-11-26 轮）。

改法：只用「定位唯一子串 → 替换 → assert count == 1」，不整文件重写；
读写 newline='' 保持原换行符（CRLF/LF）与空行结构。
备份：final.txt.bak_20261125（已存在则不覆盖）。
"""
import ast
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

# (chunk, category, old, new, note)
EDITS = [
    # ---------------- chunk102 ----------------
    ('chunk102', '③',
     '（亲王长长舒了一口气，如释重负）——而他知道我是有朋友的。',
     '（亲王长长舒了一口气，如释重负），而他知道我是有朋友的。',
     '法语括注 (le prince eut un profond soupir) et il sait… 被照搬成“）——而”，'
     '破折号插在括注与连词之间，割断句子；改为逗号顺接。'),

    # ---------------- chunk110 ----------------
    ('chunk110', '⑥',
     '况且，被人包养的女人里，又有多少虽说靠情人供养，却因这种生活中滋生的一点雅致，'
     '亲手为情人的慷慨划下千百道小小的界限！',
     '况且，那些既然靠人供养、也就贪图实利的女人里，又有多少因这种生活中滋生的一点雅致，'
     '亲手为情人的慷慨划下千百道小小的界限！',
     'combien de femmes intéressées, puisqu’elles sont entretenues… ：puisque 是“既然/因为”，'
     '译成“虽说”把因果读成了让步，逻辑反转；intéressées 亦漏译。'),

    # ---------------- chunk112 ----------------
    ('chunk112', '③',
     '您竟愿意如此关照我，设法对我有用，我深受感动。',
     '您竟愿意如此关照我，设法为我出力，我深受感动。',
     'm’être utile 直搬成“对我有用”，中文里“人对我有用”是贬义（可资利用）；'
     '改“为我出力”才是原意。'),
    ('chunk112', '②',
     '我希望您不会对我即将向您提出的建议的纯粹无私和慈善的性质产生误解。',
     '我希望您不要误解我即将向您提出的建议：它是纯粹无私、出于善意的。',
     '一句里“我／向您提出的／建议的／纯粹无私和慈善的／性质”，四层“的”把中心语压没；'
     '拆成冒号句。'),
    ('chunk112', '①',
     '向我问起布洛克，在维尔帕里西夫人家人们谈到过布洛克，而他当时似乎没有听见，',
     '向我问起布洛克，刚才在维尔帕里西夫人家，人们谈到过布洛克，而他当时似乎没有听见，',
     '“在维尔帕里西夫人家人们谈到过布洛克”里“家”与“人们”直接相连，读作“家人们”，'
     '主谓断裂；补逗号并加“刚才”点明时间层次。'),
    ('chunk112', '①',
     '布洛克要是听见了，就会比面对德·诺普瓦先生时更加为难——但原因完全不同——'
     '要弄明白德·夏尔吕先生究竟是支持还是反对德雷福斯。',
     '布洛克要是听见了，要弄明白德·夏尔吕先生究竟是支持还是反对德雷福斯，'
     '就会比面对德·诺普瓦先生时更加为难，只是原因完全不同。',
     '法语 eût été plus en peine … de savoir si 的后置不定式被照样搬来，'
     '中文“为难……要弄明白”断了宾语的着落；把“要弄明白”提到“为难”之前，'
     '并把插入的括注改成句末分句。'),

    # ---------------- chunk124 ----------------
    ('chunk124', '⑥',
     '于是她想，不该让妈妈为难，要在妈妈至今经历过的最痛苦的时刻陪着她。',
     '于是她不愿对妈妈失职，要在妈妈至今经历过的最痛苦的时刻陪着她。',
     'elle voulut ne pas faire faute à maman：faire faute à qqn 是“对某人失职/缺位”，'
     '与“让某人为难”无关；原译把意思读偏。'),
    ('chunk124', '⑥',
     '这正像一种本能的感情，曾使我想，安德烈那么怜惜阿尔贝蒂娜，正是因为她并不十分爱她。',
     '这也是出于同一种本能的情感——那种情感曾使我想，安德烈对阿尔贝蒂娜怜惜得过了头，'
     '也就不会十分爱她。',
     'le même sentiment instinctif qui m’avait fait supposer qu’Andrée plaignait trop '
     'Albertine pour l’aimer beaucoup：trop … pour 是“过度到不能”，原译倒成“因为不爱所以怜惜”，'
     '因果与否定双双反转。'),

    # ---------------- chunk125 ----------------
    ('chunk125', '⑥',
     '却也增加了蛋白的剂量',
     '却也增加了白蛋白的量',
     'la dose d’albumine 指尿中白蛋白含量，“剂量”是药量量词，误用；'
     '本册 chunk116 作“白蛋白数值”，此处归一。'),
    ('chunk125', '⑥',
     '在蛋白剂量过大的日子里',
     '在白蛋白过多的日子里',
     '同上，albumine 非可“服”之药，无“剂量过大”可言。'),
    ('chunk125', '①',
     '我们打向那个在外祖母身上安顿下来的病魔的打击，总是落空；',
     '我们本是冲着那个在外祖母身上扎下根来的病魔下手的，可打击总是落空；',
     'Les coups que nous destinions au mal qui s’était installé… 的“打击的”三重定语'
     '把主语压成名词堆；改成动词句。'),
    ('chunk125', '②',
     '叫人分不清那是一个吻的刻刀、一声呜咽的刻刀还是一抹微笑的刻刀雕出来的。',
     '叫人分不清那是被一个吻、一声呜咽还是一抹微笑的刻刀雕出来的。',
     'le ciseau d’un baiser, d’un sanglot ou d’un sourire 的关系被逐项复制成三个“的刻刀”，'
     '中文读来叠床架屋；刻刀只说一次。'),
]


def main():
    by_chunk = {}
    for chunk, cat, old, new, note in EDITS:
        by_chunk.setdefault(chunk, []).append((cat, old, new, note))

    for chunk, edits in by_chunk.items():
        d = os.path.join(ROOT, chunk)
        f = os.path.join(d, 'final.txt')
        b = os.path.join(d, BAK)
        if not os.path.exists(b):
            shutil.copy2(f, b)
            print('%s: backup created' % chunk)
        else:
            print('%s: backup exists, kept' % chunk)

        with open(f, encoding='utf-8', newline='') as fh:
            text = fh.read()
        before = text
        before_cjk = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')

        applied = 0
        for cat, old, new, note in edits:
            assert old in text, (chunk, 'NOT FOUND', old[:30])
            assert text.count(old) == 1, (chunk, 'NOT UNIQUE', old[:30])
            text = text.replace(old, new)
            applied += 1
            print('  [%s] %s → %s' % (cat, old[:24], new[:24]))

        # 结构校验：行数、段数、空行数、CRLF 数不变
        def stats(t):
            norm = t.replace('\r\n', '\n')
            lines = norm.split('\n')
            return (len(lines), sum(1 for x in lines if x.strip()),
                    sum(1 for x in lines if not x.strip()), t.count('\r\n'))

        assert stats(before) == stats(text), (chunk, 'STRUCTURE CHANGED',
                                              stats(before), stats(text))
        assert '\n\n\n' not in text.replace('\r\n', '\n'), (chunk, 'triple newline')

        with open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)
        after_cjk = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')
        print('%s: %d edits, lines %d, cjk %d→%d, %s'
              % (chunk, applied, stats(text)[0], before_cjk, after_cjk,
                 'CRLF' if text.count('\r\n') else 'LF'))


ast.parse(open(__file__, encoding='utf-8').read())
main()