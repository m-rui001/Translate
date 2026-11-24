# -*- coding: utf-8 -*-
"""《晚夏》后半通读润色 —— p9：c012、c013 两章（14 个分片）
（p9 首跑在 c012/c03 因「阿斯佩尔庄园」已吃掉「阿斯佩尔庄」而中止，此为本版修正＋幂等版）
"""
import os, shutil, ast

BASE = r'E:/Translate/work_gutenberg/nachsommer/out'

PLAN = {
    ('c012', 'c00'): [('阿斯佩庄', '阿斯佩霍夫', 4), ('星院', '星苑', 4), ('玫瑰苑', '玫瑰屋', 1)],
    ('c012', 'c01'): [('星院', '星苑', 4)],
    ('c012', 'c03'): [('阿斯佩尔庄园', '阿斯佩霍夫', 1), ('玫瑰苑', '玫瑰屋', 1)],
    ('c012', 'c04'): [('星院', '星苑', 3)],
    ('c012', 'c05'): [('阿斯佩尔庄园', '阿斯佩霍夫', 1), ('玫瑰苑', '玫瑰屋', 1)],
    ('c013', 'c00'): [('护壁板', '镶板', 3)],
    ('c013', 'c01'): [('罗兰德', '罗兰', 3), ('护壁板', '镶板', 2),
                      ('玫瑰庐', '玫瑰屋', 2), ('枞林', '冷杉林', 1)],
    ('c013', 'c02'): [('奥伊施塔赫', '欧斯塔赫', 1)],
    ('c013', 'c03'): [('星院', '星苑', 1)],
    ('c013', 'c04'): [('阿斯佩庄', '阿斯佩霍夫', 2)],
    ('c013', 'c06'): [('娜塔莉亚', '娜塔莉', 5)],
}

log, skipped = [], []
for (chap, sub), items in PLAN.items():
    path = os.path.join(BASE, chap, sub, 'final.txt')
    with open(path, encoding='utf-8', newline='') as fh:
        text = fh.read()
    lines0 = text.split('\n')
    n0, b0 = len(lines0), sum(1 for x in lines0 if x.strip() == '')
    bak = path + '.bak_20261125'
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    orig = text
    for old, new, exp in items:
        got = text.count(old)
        if got == 0:
            skipped.append((chap, sub, old))
            continue
        assert got == exp, (chap, sub, old, 'expect %d got %d' % (exp, got))
        text = text.replace(old, new)
        log.append((chap, sub, old, new, got))
    lines1 = text.split('\n')
    assert len(lines1) == n0, (chap, sub, 'linecount')
    assert sum(1 for x in lines1 if x.strip() == '') == b0, (chap, sub, 'blank')
    if text != orig:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)

print('p9 done, edits:', len(log), 'skipped:', len(skipped))
for r in log:
    print('  %s/%s  %s -> %s  x%d' % r)
for r in skipped:
    print('  (skip) %s/%s  %s' % r)

ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse OK')