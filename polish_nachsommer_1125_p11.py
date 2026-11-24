# -*- coding: utf-8 -*-
"""《晚夏》后半通读润色 —— p11：c016 全章（17 个分片）
含 30 处「款待者」→「东道主」、奥伊斯特赫／娜塔莉娅等异写、Cereus peruvianus 与
Echer/Echern 名物归一、以及 c016/c16 段首缺失的起引号。
"""
import os, shutil, ast

BASE = r'E:/Translate/work_gutenberg/nachsommer/out/c016'

PLAN = {
    'c00': [('款待者', '东道主', 6), ('娜塔莉亚', '娜塔莉', 1), ('玫瑰苑', '玫瑰屋', 2)],
    'c02': [('枫树庄', '枫树客栈', 1)],
    'c03': [('枫屋', '枫树客栈', 3), ('埃歇尔谷', '埃亨谷', 1), ('西米艾斯', '西米格冰川', 1)],
    'c04': [('娜塔莉亚', '娜塔莉', 5), ('玫瑰苑', '玫瑰屋', 2)],
    'c08': [('阿斯珀霍夫', '阿斯佩霍夫', 4), ('款待者', '东道主', 4), ('娜塔莉亚', '娜塔莉', 1),
            ('埃舍恩', '埃亨', 2), ('卡格山脊', '卡尔格拉特', 1), ('枫屋', '枫树客栈', 2)],
    'c10': [('款待者', '东道主', 8), ('奥伊斯特赫', '欧斯塔赫', 5), ('玫瑰苑', '玫瑰屋', 2),
            ('埃歇尔冰川', '埃亨冰川', 1), ('阿里茨林', '阿利茨林', 1)],
    'c11': [('款待者', '东道主', 5), ('东家', '东道主', 1), ('娜塔莉亚', '娜塔莉', 1),
            ('图画室', '画像室', 1), ('藏书厅', '书斋', 1), ('Cereus peruvianus', '秘鲁天轮柱', 2)],
    'c12': [('款待者', '东道主', 7), ('玫瑰苑', '玫瑰屋', 1), ('娜塔莉娅', '娜塔莉', 1),
            ('藏书室', '书斋', 2), ('读书室', '阅览室', 1)],
    'c13': [('阿斯佩尔迈尔', '阿斯佩尔迈耶', 2)],
    'c16': [('凡尚有选择余地之处——因为不必出去谋求所谓的面包——',
             '“凡尚有选择余地之处——因为不必出去谋求所谓的面包——', 1)],
}

log = []
for sub, items in PLAN.items():
    path = os.path.join(BASE, sub, 'final.txt')
    with open(path, encoding='utf-8', newline='') as fh:
        text = fh.read()
    lines0 = text.split('\n')
    n0, b0 = len(lines0), sum(1 for x in lines0 if x.strip() == '')
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
    lines1 = text.split('\n')
    assert len(lines1) == n0, (sub, 'linecount')
    assert sum(1 for x in lines1 if x.strip() == '') == b0, (sub, 'blank')
    if text != orig:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)

print('p11 done, edits:', len(log))
for r in log:
    print('  c016/%s  %s -> %s  x%d' % r)

ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse OK')