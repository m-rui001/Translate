# -*- coding: utf-8 -*-
"""《晚夏》后半通读润色 —— p10：c014、c015 两章（15 个分片）"""
import os, shutil, ast

BASE = r'E:/Translate/work_gutenberg/nachsommer/out'

PLAN = {
    ('c014', 'c03'): [('星院', '星苑', 1)],
    ('c014', 'c04'): [('西门一带', '西米一带', 1)],          # Gegend der Simmen
    ('c014', 'c05'): [('阿斯珀庄', '阿斯佩霍夫', 3), ('星院', '星苑', 1),
                      ('居停主人', '东道主', 4)],
    ('c014', 'c06'): [('齐特尔琴', '齐特琴', 2)],
    ('c014', 'c07'): [('居停主人', '东道主', 2)],
    ('c015', 'c00'): [('英苑', '英格霍夫', 1)],              # Inghof
    ('c015', 'c05'): [('罗特摩尔', '红沼', 3)],              # Rothmoor
}

log = []
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
        assert old in text, (chap, sub, old)
        got = text.count(old)
        assert got == exp, (chap, sub, old, 'expect %d got %d' % (exp, got))
        text = text.replace(old, new)
        log.append((chap, sub, old, new, got))
    lines1 = text.split('\n')
    assert len(lines1) == n0, (chap, sub, 'linecount')
    assert sum(1 for x in lines1 if x.strip() == '') == b0, (chap, sub, 'blank')
    if text != orig:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)

print('p10 done, edits:', len(log))
for r in log:
    print('  %s/%s  %s -> %s  x%d' % r)

ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse OK')