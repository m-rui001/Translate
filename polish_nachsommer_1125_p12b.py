# -*- coding: utf-8 -*-
"""《晚夏》后半通读润色 —— p12b：补漏（Ahorn 客店一名四写、Karspitze、Echertal）
p8–p12 落盘后残留扫描出的最后 9 处异写。
"""
import os, shutil, ast

BASE = r'E:/Translate/work_gutenberg/nachsommer/out'

PLAN = {
    ('c011', 'c07'): [('枫树旅馆', '枫树客栈', 2)],            # Ahornwirtshaus
    ('c011', 'c08'): [('枫宅', '枫树客栈', 1)],
    ('c012', 'c05'): [('枫树居', '枫树客栈', 2)],
    ('c013', 'c01'): [('卡斯峰', '卡尔峰', 1)],                # Karspitze
    ('c018', 'c09'): [('埃歇尔谷', '埃亨谷', 1)],              # Echertal
    ('c018', 'c10'): [('阿霍恩客店', '枫树客栈', 2)],
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

print('p12b done, edits:', len(log))
for r in log:
    print('  %s/%s  %s -> %s  x%d' % r)

ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse OK')