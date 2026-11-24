# -*- coding: utf-8 -*-
"""修 polish_effi_p1 在 c020/c00 祝酒词处留下的重复语（一枚真正当之无愧的戒指，一枚真正当之无愧的戒指——）"""
import os, ast

ROOT = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(ROOT, 'work_gutenberg', 'effi', 'out', 'c020', 'c00', 'final.txt')

old = '一枚真正当之无愧的戒指，一枚真正当之无愧的戒指——它把'
new = '一枚真正当之无愧的戒指——它把'

with open(path, encoding='utf-8', newline='') as f:
    text = f.read()
assert text.count(old) == 1, text.count(old)
lines_before = len(text.split('\n'))
text = text.replace(old, new)
assert len(text.split('\n')) == lines_before
with open(path, 'w', encoding='utf-8', newline='') as f:
    f.write(text)
print('fixed')
ast.parse(open(__file__, encoding='utf-8').read())