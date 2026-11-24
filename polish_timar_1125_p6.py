#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""金人（timar）通读润色 后半 p6：叶 63–77（c026/c03 … c030/c03）。
改法：逐文件定位 → 断言命中数 → 替换；行数不变；改前备份 .bak_20261125。
"""
import os, re, shutil, sys, ast

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'work_gutenberg', 'timar', 'out')
BAK = '.bak_20261125'

def P(ch, sub):
    return os.path.join(OUT, ch, sub, 'final.txt')

# (old, new, expected_count, is_regex)
OPS = {
    ('c026', 'c03'): [
        ('米迦勒', '迈克尔', 2, False),
    ],
    ('c027', 'c00'): [
        ('米哈伊尔', '迈克尔', 4, False),
        ('求肯在蜂房里过夜', '恳求在蜂房里过夜', 1, False),
    ],
    ('c027', 'c01'): [
        ('米哈伊尔', '迈克尔', 2, False),
    ],
    ('c027', 'c02'): [
        ('米哈伊尔', '迈克尔', 1, False),
        ('克丽丝蒂扬', '克里斯蒂安', 2, False),
        ('每一路得五百杜卡特——十路就是五千杜卡特',
         '每一批得五百杜卡特——十批就是五千杜卡特', 1, False),
    ],
    ('c027', 'c03'): [
        ('米哈伊尔', '迈克尔', 3, False),
    ],
    ('c028', 'c00'): [
        (r'蒂马(?!尔)', '蒂马尔', 6, True),
        ('四围', '四周', 1, False),
    ],
    ('c029', 'c00'): [
        ('斯卡拉穆奇', '斯卡拉梅利', 3, False),
        ('第里雅斯特', '的里雅斯特', 2, False),
    ],
    ('c029', 'c01'): [
        ('斯卡拉穆奇', '斯卡拉梅利', 3, False),
        ('莱韦廷茨基', '莱韦廷齐', 3, False),
        ('潘乔瓦', '潘切沃', 2, False),
    ],
    ('c029', 'c02'): [
        ('情欲与自意', '情欲与意志', 1, False),
    ],
    ('c029', 'c03'): [
        ('西奥多从木屋里向他开枪', '特奥多尔从木屋里向他开枪', 1, False),
        ('四围', '四周', 1, False),
    ],
    ('c030', 'c00'): [
        ('米迦勒', '迈克尔', 10, False),
    ],
    ('c030', 'c01'): [
        ('米歇尔', '迈克尔', 8, False),
    ],
    ('c030', 'c02'): [
        ('米夏埃尔', '迈克尔', 6, False),
    ],
    ('c030', 'c03'): [
        ('米迦勒', '迈克尔', 2, False),
    ],
}

DONEF = os.path.join(ROOT, '_pol', 'p6_done.txt')
done = set()
if os.path.exists(DONEF):
    done = set(open(DONEF, encoding='utf-8').read().split())

total = 0
report = []
for (ch, sub), ops in OPS.items():
    if f'{ch}/{sub}' in done:
        report.append(f'{ch}/{sub}	SKIP(已落盘)')
        continue
    path = P(ch, sub)
    with open(path, encoding='utf-8', newline='') as f:
        text = f.read()
    orig_lines = text.count('\n')
    orig_paras = len([x for x in text.split('\n')])
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
    # 红线自查
    assert new.count('\n') == orig_lines, (ch, sub, '行数变了')
    assert len(new.split('\n')) == orig_paras, (ch, sub, '段数变了')
    assert '⟦i⟧' in new or '⟦i⟧' not in text, 'i标记异常'
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(new)
    with open(DONEF, 'a', encoding='utf-8') as f:
        f.write('%s\n' % (ch + '/' + sub))

print('p6 改动条数:', total)
print('\n'.join(report))
ast_ok = True
ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse ok')