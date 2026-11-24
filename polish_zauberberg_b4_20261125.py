# -*- coding: utf-8 -*-
"""《魔山》batch4：Sorgenkind des Lebens（塞特姆布里尼给卡斯托普起的绰号）全册统一为“生命的忧患之子”。"""
import io, os, ast

BASE = 'E:/Translate/work_zauberberg/out'


def patch(rel, pairs):
    path = os.path.join(BASE, rel)
    with io.open(path, 'r', encoding='utf-8-sig', newline='') as f:
        text = f.read()
    bak = path + '.bak_20261125'
    if not os.path.exists(bak):
        with io.open(bak, 'w', encoding='utf-8-sig', newline='') as f:
            f.write(text)
    for old, new, cnt in pairs:
        assert old in text, (rel, old)
        assert text.count(old) == cnt, (rel, old, text.count(old))
        text = text.replace(old, new)
    with io.open(path, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(text)
    print('patched', rel, len(pairs))


if False: patch('index_split_011/c01/final.txt', [
    ('我生来就是生活的忧患之子', '我生来就是生命的忧患之子', 1),
])
if False: patch('index_split_012/c03/final.txt', [
    ('才再一次走近这个忧患门生', '才再一次走近这个忧患之子', 1),
])
patch('index_split_013/c02/final.txt', [
    ('所谓生命的忧患儿', '所谓生命的忧患之子', 1),
    ('是某种生命的忧患儿', '是某种生命的忧患之子', 1),
])
patch('index_split_015/c05/final.txt', [
    ('生命对他这个迷途甚远的忧患孩子还是怀着善意', '生命对他这个迷途甚远的忧患之子还是怀着善意', 1),
])
patch('index_split_016/c02/final.txt', [
    ('称其为“生命的忧患儿”', '称其为“生命的忧患之子”', 1),
])
patch('index_split_017/c14/final.txt', [
    ("觉得我是个‘生命的忧患儿’", "觉得我是个‘生命的忧患之子’", 1),
    ("把我当作‘生命的忧患儿’", "把我当作‘生命的忧患之子’", 1),
])

ast.parse(open(__file__, encoding='utf-8').read())
print('OK')