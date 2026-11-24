#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""《野人旅馆》润色 第 2 批补漏：c010 两处「林务员」"""
import ast
import io
import os

BASE = os.path.join('work_gutenberg', 'wilderMann', 'out')
p = os.path.join(BASE, 'c010/c00/final.txt')
with io.open(p, 'r', encoding='utf-8', newline='') as f:
    text = f.read()
lines = text.split('\n')
before = (len(lines), sum(1 for l in lines if l.strip() == ''))
mark = (text.count(u'⟦i⟧'), text.count(u'⟦/i⟧'))

old, new, expect = '林务员', '林务官', 2
logs = []
for _ in range(expect):
    i = text.find(old)
    assert i >= 0
    lo, hi = i, i + len(old)
    while text.count(text[lo:hi]) > 1:
        if lo > 0:
            lo -= 1
        if text.count(text[lo:hi]) > 1 and hi < len(text):
            hi += 1
    win = text[lo:hi]
    assert text.count(win) == 1, win
    logs.append(win.strip())
    text = text[:i] + new + text[i + len(old):]
assert old not in text
lines = text.split('\n')
assert (len(lines), sum(1 for l in lines if l.strip() == '')) == before
assert (text.count(u'⟦i⟧'), text.count(u'⟦/i⟧')) == mark
with io.open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(text)
for l in logs:
    print('  ·', l)
print('total edits: 2')
ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse ok')
