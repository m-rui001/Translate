# -*- coding: utf-8 -*-
"""《晚夏》后半通读润色 —— p8：c011 全章（13 个分片）
落盘方式：定位唯一子串 -> 断言命中数 -> 替换；备份 .bak_20261125；行数/空行不变。
"""
import os, shutil, ast

BASE = r'E:/Translate/work_gutenberg/nachsommer/out/c011'

PLAN = {
    'c00': [
        # 专名：Asperhof / Sternenhof
        ('阿斯珀霍夫', '阿斯佩霍夫', 1),
        ('星院', '星苑', 2),
    ],
    'c03': [
        ('奥伊施塔赫', '欧斯塔赫', 1),          # Eustach
    ],
    'c04': [
        ('齐特尔琴', '齐特琴', 1),              # Zither
    ],
    'c08': [
        ('阿斯珀宅', '阿斯佩霍夫', 1),
        ('星院', '星苑', 1),
    ],
    'c09': [
        ('阿斯珀霍夫', '阿斯佩霍夫', 4),
        ('星院', '星苑', 3),
    ],
    'c10': [
        ('星院', '星苑', 2),
        # 承接 c09 末段未收的话（玛蒂尔德语），补起引号与收引号
        ('当这些花的细叶还在这里尽情舒展、终至枯萎凋落的时候，我们的管家',
         '“当这些花的细叶还在这里尽情舒展、终至枯萎凋落的时候，我们的管家', 1),
        ('而能够爱一个人，对于有这份感情的人说来，就是一大收获。',
         '而能够爱一个人，对于有这份感情的人说来，就是一大收获。”', 1),
    ],
    'c12': [
        ('阿斯珀霍夫', '阿斯佩霍夫', 1),
    ],
    'c13': [
        ('星院', '星苑', 4),
    ],
}

log = []
for sub, items in PLAN.items():
    path = os.path.join(BASE, sub, 'final.txt')
    with open(path, encoding='utf-8', newline='') as fh:
        text = fh.read()
    before_lines = text.split('\n')
    before_nl = len(before_lines)
    before_blank = sum(1 for x in before_lines if x.strip() == '')
    bak = path + '.bak_20261125'
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    orig = text
    for old, new, exp in items:
        assert old in text, (sub, old)
        got = text.count(old)
        assert got == exp, (sub, old, 'expect %d got %d' % (exp, got))
        text = text.replace(old, new)
        log.append((sub, old, new, got))
    after_lines = text.split('\n')
    assert len(after_lines) == before_nl, (sub, 'linecount')
    assert sum(1 for x in after_lines if x.strip() == '') == before_blank, (sub, 'blank')
    if text != orig:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)

print('p8 done, edits:', len(log))
for r in log:
    print('  c011/%s  %s -> %s  x%d' % r)

ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse OK')