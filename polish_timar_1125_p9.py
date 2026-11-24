#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""金人（timar）通读润色 后半 p9：叶 108–124（c038/c04 … c047/c03）。"""
import os, re, shutil, ast

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'work_gutenberg', 'timar', 'out')
BAK = '.bak_20261125'

def P(ch, sub):
    return os.path.join(OUT, ch, sub, 'final.txt')

OPS = {
    ('c038', 'c04'): [
        ('娜奥米', '诺埃米', 13, False),
        (r'米哈伊(?:尔)?', '迈克尔', 1, True),
        ('克里斯强', '克里斯蒂安', 1, False),
    ],
    ('c039', 'c00'): [
        ('西奥多·克里斯蒂安', '特奥多尔·克里斯蒂安', 1, False),
        ('阿达莉', '阿塔莉', 1, False),
        ('多多尔', '多迪', 1, False),
        (r'米哈伊(?:尔)?', '迈克尔', 1, True),
        ('普拉滕湖', '巴拉顿湖', 2, False),
        ('蒂豪尼', '蒂哈尼', 1, False),
    ],
    ('c041', 'c00'): [
        (r'米哈伊(?:尔)?', '迈克尔', 2, True),
        ('老加兰博斯', '老加兰博什', 1, False),
        ('普拉滕湖', '巴拉顿湖', 1, False),
    ],
    ('c042', 'c00'): [
        ('米迦勒', '迈克尔', 14, False),
    ],
    ('c043', 'c00'): [
        ('米迦勒', '迈克尔', 1, False),
        ('弗劳·索菲', '索菲太太', 2, False),
        ('弗罗伊莱因·阿塔莉', '阿塔莉小姐', 1, False),
    ],
    ('c043', 'c01'): [
        (r'米哈伊(?:尔)?', '迈克尔', 2, True),
        ('莱韦廷茨基', '莱韦廷齐', 1, False),
        ('多多迪', '多迪', 1, False),
    ],
    ('c045', 'c00'): [
        ('阿塔莉耶', '阿塔莉', 19, False),
    ],
    ('c045', 'c01'): [
        (r'米哈伊(?:尔)?', '迈克尔', 2, True),
    ],
    ('c046', 'c00'): [
        ('神甫', '神父', 1, False),
    ],
    ('c047', 'c00'): [
        ('四围', '四周', 1, False),
    ],
}

DONEF = os.path.join(ROOT, '_pol', 'p9_done.txt')
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

print('p9 改动条数:', total)
print('\n'.join(report))
ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse ok')