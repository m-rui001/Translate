# -*- coding: utf-8 -*-
"""《晚夏》后半通读润色 —— p12：c017、c018 两章（31 个分片）
含「星宅／星园／施特恩霍夫」→「星苑」、「罗森豪斯」→「玫瑰屋」、
「德伦霍夫」→「德伦多夫」、「秘鲁仙人掌」→「秘鲁天轮柱」、以及 c017/c10 引号串层。
"""
import os, shutil, ast

BASE = r'E:/Translate/work_gutenberg/nachsommer/out'

PLAN = {
    ('c017', 'c04'): [('玛蒂尔达', '玛蒂尔德', 3)],
    ('c017', 'c05'): [('玛克罗登', '马克洛登', 1)],
    ('c017', 'c06'): [('海因巴赫的居停同他们', '海因巴赫的住户同他们', 1)],
    ('c017', 'c08'): [('海恩巴赫', '海因巴赫', 2), ('齐特尔琴', '齐特琴', 1)],
    ('c017', 'c10'): [
        # 外层引号被写成了内层单引号（同段又重复了一次起引号），归回“”
        ('‘‘古斯塔夫，古斯塔夫’，她答道，‘', '“古斯塔夫，古斯塔夫，”她答道，“', 1),
        ('也撕不开它。’’', '也撕不开它。”', 1),
        # 其后三段是叙述，句首的孤立单引号是串层残留，删去（同文件第 6 段即裸排叙述）
        ('‘我抓住她的手，一个灼热的吻', '我抓住她的手，一个灼热的吻', 1),
        ('‘我和阿尔弗雷德一起做他该学的东西', '我和阿尔弗雷德一起做他该学的东西', 1),
        ('‘初春时，我们又像去年一样乘车到海因巴赫去', '初春时，我们又像去年一样乘车到海因巴赫去', 1),
    ],
    ('c017', 'c15'): [('海恩巴赫', '海因巴赫', 3)],
    ('c017', 'c17'): [('星园', '星苑', 3)],
    ('c017', 'c18'): [('星宅', '星苑', 6), ('英格庄', '英格霍夫', 1), ('阿斯佩庄', '阿斯佩霍夫', 3)],
    ('c018', 'c00'): [('施特恩霍夫', '星苑', 1), ('罗森豪斯', '玫瑰屋', 2)],
    ('c018', 'c01'): [('施特恩霍夫', '星苑', 1)],
    ('c018', 'c02'): [('施特恩霍夫', '星苑', 1), ('罗森豪斯', '玫瑰屋', 2)],
    ('c018', 'c03'): [('施特恩霍夫', '星苑', 2)],
    ('c018', 'c04'): [('藏书室', '书斋', 1)],
    ('c018', 'c05'): [('施特恩霍夫', '星苑', 1), ('罗森豪斯', '玫瑰屋', 1),
                      ('阿斯珀霍夫', '阿斯佩霍夫', 2), ('因格霍夫', '英格霍夫', 2),
                      ('迈尔霍夫', '田庄', 1)],
    ('c018', 'c06'): [('施特恩霍夫', '星苑', 4), ('阿斯珀霍夫', '阿斯佩霍夫', 6)],
    ('c018', 'c07'): [('藏书室', '书斋', 1)],
    ('c018', 'c08'): [('阿斯珀霍夫', '阿斯佩霍夫', 2), ('奥伊施塔赫', '欧斯塔赫', 3),
                      ('德伦霍夫', '德伦多夫', 2)],
    ('c018', 'c09'): [('奥伊施塔赫', '欧斯塔赫', 2), ('秘鲁仙人掌', '秘鲁天轮柱', 4),
                      ('德伦霍夫', '德伦多夫', 1), ('护壁板', '镶板', 2)],
    ('c018', 'c10'): [('施特恩霍夫', '星苑', 5)],
    ('c018', 'c11'): [('施特恩霍夫', '星苑', 1), ('阿斯珀霍夫', '阿斯佩霍夫', 3)],
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

print('p12 done, edits:', len(log))
for r in log:
    print('  %s/%s  %s -> %s  x%d' % r)

ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse OK')