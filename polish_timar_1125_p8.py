#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""金人（timar）通读润色 后半 p8：叶 93–107（c034/c02 … c038/c03）。"""
import os, re, shutil, ast

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'work_gutenberg', 'timar', 'out')
BAK = '.bak_20261125'

def P(ch, sub):
    return os.path.join(OUT, ch, sub, 'final.txt')

OPS = {
    ('c035', 'c00'): [
        ('蒂玛', '蒂梅娅', 7, False),
        ('米夏埃尔', '迈克尔', 9, False),
    ],
    ('c036', 'c00'): [
        ('米夏埃尔', '迈克尔', 2, False),
    ],
    ('c037', 'c00'): [
        ('连 梭鲈 之王也能捉上来', '连梭鲈之王也能捉上来', 1, False),
        ('那是一条老 梭鲈', '那是一条老梭鲈', 1, False),
    ],
    ('c037', 'c01'): [
        ('米哈伊尔', '迈克尔', 1, False),
        ('梭鲈（梭鲈）', '梭鲈', 2, False),
    ],
    ('c037', 'c02'): [
        ('米迦勒', '迈克尔', 3, False),
        ('四围', '四周', 3, False),
        ('韦斯普里姆', '维什普里姆', 1, False),
    ],
    ('c038', 'c00'): [
        ('克里斯强', '克里斯蒂安', 4, False),
        ('米哈伊尔', '迈克尔', 1, False),
    ],
    ('c038', 'c01'): [
        ('克里斯强', '克里斯蒂安', 1, False),
        ('米哈伊尔', '迈克尔', 2, False),
        ('潘乔瓦', '潘切沃', 1, False),
    ],
    ('c038', 'c02'): [
        ('克里斯强', '克里斯蒂安', 1, False),
        ('四围', '四周', 1, False),
        ('那逃兵接着说', '那逃犯接着说', 1, False),
    ],
    ('c038', 'c03'): [
        ('克里斯强', '克里斯蒂安', 1, False),
        ('米哈伊尔', '迈克尔', 1, False),
        ('泰蕾兹', '特蕾泽', 1, False),
        ('被你要子的情人砍破脑袋', '被你妻子的情人砍破脑袋', 1, False),
    ],
}

DONEF = os.path.join(ROOT, '_pol', 'p8_done.txt')
done = set()
if os.path.exists(DONEF):
    done = set(open(DONEF, encoding='utf-8').read().split())

total = 0
report = []
for (ch, sub), ops in OPS.items():
    if f'{ch}/{sub}' in done:
        report.append(f'{ch}/{sub}\tSKIP(已落盘)')
        continue
    path = P(ch, sub)
    with open(path, encoding='utf-8', newline='') as f:
        text = f.read()
    orig_lines = text.count('\n')
    orig_paras = len(text.split('\n'))
    bak = path + BAK
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    new = text
    for old, rep, n, is_re in ops:
        if is_re:
            got = len(re.findall(old, new))
            assert got == n, (ch, sub, old, got, n)
            new = re.sub(old, rep, new)
        else:
            assert old in new and new.count(old) == n, (ch, sub, old, new.count(old), n)
            new = new.replace(old, rep)
        total += n
        report.append(f'{ch}/{sub}\t{n}\t{old} -> {rep}')
    assert new.count('\n') == orig_lines, (ch, sub, '行数变了')
    assert len(new.split('\n')) == orig_paras, (ch, sub, '段数变了')
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(new)
    with open(DONEF, 'a', encoding='utf-8') as f:
        f.write('%s\n' % (ch + '/' + sub))

print('p8 改动条数:', total)
print('\n'.join(report))
ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse ok')