#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""金人（timar）通读润色 后半 p7：叶 78–92（c031/c00 … c034/c01）。"""
import os, re, shutil, ast

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'work_gutenberg', 'timar', 'out')
BAK = '.bak_20261125'

def P(ch, sub):
    return os.path.join(OUT, ch, sub, 'final.txt')

# (old, new, expected_count, is_regex)
OPS = {
    ('c031', 'c01'): [
        ('在教长那里住了一夜', '在本堂神父那里住了一夜', 1, False),
        ('便出了牧师住宅', '便出了本堂神父的住宅', 1, False),
    ],
    ('c031', 'c02'): [
        ('多多', '多迪', 7, False),
        ('米迦勒', '迈克尔', 11, False),
    ],
    ('c032', 'c00'): [
        ('比阿里茨', '比亚里茨', 1, False),
    ],
    ('c032', 'c01'): [
        ('米歇尔', '迈克尔', 7, False),
    ],
    ('c032', 'c02'): [
        ('米哈伊尔', '迈克尔', 5, False),
    ],
    ('c032', 'c03'): [
        ('米夏埃尔', '迈克尔', 25, False),
        ('泰蕾兹', '特蕾泽', 6, False),
    ],
    ('c032', 'c04'): [
        ('阴沉地沉默良久', '阴沉着脸，沉默良久', 1, False),
    ],
    ('c033', 'c00'): [
        ('泰蕾兹', '特蕾泽', 3, False),
    ],
    ('c033', 'c01'): [
        ('普拉滕湖', '巴拉顿湖', 2, False),
    ],
    ('c033', 'c02'): [
        ('提玛', '蒂马尔', 13, False),
        ('米迦勒', '迈克尔', 6, False),
        ('四围', '四周', 2, False),
        ('普拉滕湖', '巴拉顿湖', 1, False),
        ('富雷德', '菲赖德', 1, False),
    ],
    ('c033', 'c03'): [
        ('多多', '多迪', 4, False),
        ('米迦勒', '迈克尔', 3, False),
    ],
    ('c034', 'c00'): [
        ('尊敬的桑多罗维奇先生，那位领过勋章的教长', '尊敬的桑多罗维奇先生，那位领过勋章的本堂神父', 1, False),
        ('他夺去了特蕾莎的信任', '他夺去了特蕾泽的信任', 1, False),
    ],
    ('c034', 'c01'): [
        ('教长', '本堂神父', 4, False),
        ('身分', '身份', 1, False),
    ],
}

DONEF = os.path.join(ROOT, '_pol', 'p7_done.txt')
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

print('p7 改动条数:', total)
print('\n'.join(report))
ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse ok')