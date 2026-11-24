# -*- coding: utf-8 -*-
"""v3 chunk003 / chunk004 / chunk007 逐段润色落盘（2026-11-26 轮）

准则：E:/Translate/POLISH_BRIEF_2026-11-25.md
canon：E:/Translate/scratch/rev2026/proust_canon_1125.md
只做「定位唯一子串 → 替换 → assert count==1」，不整文件重写；
newline='' 读写，段数/行数/空行结构/换行符一律不动。
"""
import ast
import os
import shutil

BASE = r'E:/Translate/work_proust/out/v3'
CHUNKS = ['003', '004', '007']
BAK = '.bak_20261125'

# ---------------------------------------------------------------- 改动清单
EDITS = {
    '003': [
        # ③ 外语句法直搬：括注式插入语（mais d'une façon peu déchiffrable）
        #    插在动宾之间，读者断句失败；改为把插入语收在句末，补出主语
        ('上面布满楔形的小红痕，向外摊开着——只是难以辨认——她那长篇的诉苦备忘录和不满的深层缘由。',
         '上面布满楔形的小红痕，这些红痕向外摊开着她那长篇的诉苦备忘录和不满的深层缘由，只是难以辨认。'),
        # ⑥ 硬伤：双重否定写成「不有」
        ('因为看来没有哪个省份不有自己的“南方”',
         '因为看来没有哪个省份没有自己的“南方”'),
    ],
    '004': [
        # ① 读不通：介词「对」带不了双宾语
        ('有本事招来夫人对她“整整一章”',
         '有本事招来夫人给她“整整一章”'),
        # ① 读不通：「其强烈（程度）与……快活不相上下」比较项错位，缺「程度」「时」
        ('其强烈与我们真要置办一辆马车她会得到的快活不相上下',
         '其强烈程度与我们真要置办一辆马车时她会得到的快活不相上下'),
        # ③ 外语句法直搬：法文破折号插入语落在「构成了」与宾语之间，中文须前置
        ('正是这些满足构成了——再加上她被公认有权按古老习俗自由奉行午餐后那套仪式：吃完在窗口吸一小口空气，上街买东西时闲逛一阵，星期天出门去看她的外甥女——她生活中不可或缺的那份快活。',
         '正是这些满足，再加上她被公认有权按古老习俗自由奉行午餐后那套仪式——吃完在窗口吸一小口空气，上街买东西时闲逛一阵，星期天出门去看她的外甥女——构成了她生活中不可或缺的那份快活。'),
    ],
    '007': [
        # ⑥ 硬伤（否定反转）：non qu'il ne fût parfaitement honnête = 并非「他不诚实」
        ('倒不是因为他自己为人十分诚实',
         '倒不是因为他自己为人不够诚实'),
        # ⑥ 硬伤：opale 是蛋白石/乳白色，「乳白石」非词
        ('那是惠斯勒画中的乳白石海湾',
         '那是惠斯勒画中的乳白色海湾'),
    ],
}


def han(s):
    return sum(1 for ch in s if '\u4e00' <= ch <= '\u9fff')


def shape(text):
    """返回 (行数, 段数, 空行数, 换行符)"""
    crlf = '\r\n' in text
    lines = text.split('\r\n') if crlf else text.split('\n')
    return len(lines), len([l for l in lines if l.strip()]), \
        len([l for l in lines if not l.strip()]), ('CRLF' if crlf else 'LF')


report = []
for ch in CHUNKS:
    path = os.path.join(BASE, 'chunk%s' % ch, 'final.txt')
    bak = path + BAK
    if not os.path.exists(bak):
        shutil.copyfile(path, bak)          # 已存在则不覆盖
        report.append('chunk%s 备份新建 %s' % (ch, os.path.basename(bak)))
    else:
        report.append('chunk%s 备份已存在，未覆盖' % ch)

    with open(path, encoding='utf-8', newline='') as f:
        text = f.read()

    before_shape = shape(text)
    before_han = han(text)

    n = 0
    for old, new in EDITS[ch]:
        assert old in text, 'chunk%s 未命中：%r' % (ch, old[:24])
        assert text.count(old) == 1, 'chunk%s 命中数 %d' % (ch, text.count(old))
        text = text.replace(old, new)
        n += 1

    after_shape = shape(text)
    assert before_shape == after_shape, 'chunk%s 结构变了：%r → %r' % (
        ch, before_shape, after_shape)
    assert '⟦' not in text and '\u3000' not in text

    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)

    report.append('chunk%s 改动 %d 条 | 行数 %d=%d 段数 %d=%d 空行 %d | 汉字 %d→%d | %s'
                  % (ch, n, before_shape[0], after_shape[0], before_shape[1],
                     after_shape[1], after_shape[2], before_han, han(text),
                     after_shape[3]))

print('\n'.join(report))

ast.parse(open(__file__, encoding='utf-8').read())
print('AST OK')