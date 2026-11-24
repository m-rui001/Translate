# -*- coding: utf-8 -*-
"""逐段润色 chunk080/081/083/084/085（2026-11-26 轮）。

规则：定位唯一子串 → 替换 → assert count == 1；不改段数/行数/空行结构；
读写均 newline=''，保持 CRLF。
"""
import ast
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

EDITS = {
    '080': [
        # ①/中: une étrangeté 名词化悬空
        ('会带有一种中世纪挂毯、哥特式彩绘玻璃的奇异',
         '会带有一种中世纪挂毯、哥特式彩绘玻璃的奇异气息'),
        # ⑥ énorme 用于人
        ('她变得庞大无比', '她胖得吓人'),
        # ⑥ par acquit de conscience = 敷衍了事、为尽本分
        ('意思是她为求心安而窃笑', '意思是她在敷衍了事地窃笑'),
        # ⑥ humanité intelligente = 有才智的人们，非「人类」
        ('他属于有才智的人类', '他属于有才智之人的行列'),
        # ③ faire un plaisir 直搬
        ('那会给我一份愉悦', '那会让我非常高兴'),
    ],
    '081': [
        # ① 条件句收束，缺「会」
        ('结果多半恰恰相反', '结果大概会恰恰相反'),
        # ②/① 「想象中的他们的」三层定语
        ('他以为自己应当好心帮一帮他想象中的他们的笨拙和羞怯',
         '他觉得自己应当出于好心，去帮他臆想出来的那份笨拙和羞怯'),
        # ③ 独立分词短语（rassuré par l'intervention…）被搬成并列流水句
        ('投石党历史学家说。维尔帕里西夫人插了话，他稍稍放下心来',
         '投石党历史学家说，他因维尔帕里西夫人的插话稍稍放下心来'),
    ],
    '083': [
        # ① 「对……来说」与强调式「正是在……」断裂，主谓错位
        ('对维尔帕里西夫人来说，“由于缺少那部分不上她家来的优雅世界”，正是在这个圈子里才有活动',
         '正是这个圈子，对维尔帕里西夫人来说，“由于缺少那部分不上她家来的优雅世界”，才有活动'),
        # ① 「只是……或者得到……」结构失衡
        ('只是他们的到场，或者得到在五点钟的招待会上谈论他们的机会',
         '只是他们的到场，或者一个在五点钟的招待会上谈论他们的机会'),
    ],
    '084': [
        # ② 「暴发户外来人」两名词硬粘
        ('他是个被上流社会容忍的暴发户外来人', '他是个被上流社会容忍的暴发户、外来人'),
        # ③ une mentalité que je connais mal 直搬
        ('那里有一种我了解得很差的心理状态', '那里面有一种我不太了解的心态'),
    ],
    '085': [
        # ②/① 「交给他为……转达的吩咐」双介词套叠
        ('没有完全执行刚才交给他为德·诺普瓦先生转达的吩咐',
         '没有完全照办刚才吩咐他转告德·诺普瓦先生的事'),
        # ⑥ appliquer des manières 误作「行使」
        ('最后也是为了行使这种对某个特定男人更加生分、更加正式的举止方式',
         '最后也是为了把这种更生分、更正式的举止用在某一个特定的男人身上'),
        # ③ 关系从句误接：「好让我去」被接到「拒绝给我」之后
        ('他也许会把那份他曾拒绝给我、好让我去斯万先生家的助力',
         '他也许会把当初我要去斯万先生家时他拒绝给我的那份帮助'),
    ],
}


def main():
    total = 0
    for chunk, edits in EDITS.items():
        d = os.path.join(ROOT, 'chunk' + chunk)
        f = os.path.join(d, 'final.txt')
        b = os.path.join(d, BAK)
        if not os.path.exists(b):
            shutil.copy2(f, b)
            bak_note = 'backup created'
        else:
            bak_note = 'backup kept'
        with open(f, encoding='utf-8', newline='') as fh:
            text = fh.read()
        before = text
        n = 0
        for old, new in edits:
            assert old in text, (chunk, old)
            assert text.count(old) == 1, (chunk, old, text.count(old))
            text = text.replace(old, new)
            n += 1
        assert text != before
        with open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)
        norm_a = before.replace('\r\n', '\n').split('\n')
        norm_b = text.replace('\r\n', '\n').split('\n')
        pa = [x for x in norm_a if x.strip()]
        pb = [x for x in norm_b if x.strip()]
        assert len(norm_a) == len(norm_b)
        assert len(pa) == len(pb)
        cjk_a = sum(1 for ch in before if '\u4e00' <= ch <= '\u9fff')
        cjk_b = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')
        print('chunk%s: 改动 %d 条 | 行 %d->%d | 段 %d->%d | 汉字 %d->%d | %s | CRLF=%d'
              % (chunk, n, len(norm_a), len(norm_b), len(pa), len(pb),
                 cjk_a, cjk_b, bak_note, text.count('\r\n')))
        total += n
    print('合计改动 %d 条' % total)


main()
ast.parse(open(__file__, encoding='utf-8').read())