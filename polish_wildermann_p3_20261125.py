#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""《野人旅馆》通读润色 第 3 批：c013-c017（第 12-16 章）"""
import ast
import io
import os

BASE = os.path.join('work_gutenberg', 'wilderMann', 'out')


def load(rel):
    p = os.path.join(BASE, rel)
    with io.open(p, 'r', encoding='utf-8', newline='') as f:
        return p, f.read()


def save(p, text):
    with io.open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def stats(t):
    lines = t.split('\n')
    return len(lines), sum(1 for l in lines if l.strip() == '')


def sub(text, old, new, expect, label, log):
    for _ in range(expect):
        i = text.find(old)
        assert i >= 0, ('not found', label, old)
        lo, hi = i, i + len(old)
        while text.count(text[lo:hi]) > 1:
            if lo > 0:
                lo -= 1
            if text.count(text[lo:hi]) > 1 and hi < len(text):
                hi += 1
        win = text[lo:hi]
        assert text.count(win) == 1, ('window not unique', label, win)
        log.append('    · %s | …%s…' % (label, win.strip()))
        text = text[:i] + new + text[i + len(old):]
    if old not in new:
        assert old not in text, ('leftover', label, old)
    return text


JOBS = {
    # ---- 第 12 章 ----
    'c013/c00/final.txt': [
        ('堂·', '唐·', 3, '⑤专名'),
        ('血凳之交', '血椅岩之交', 1, '⑤专名'),
    ],
    'c013/c01/final.txt': [
        ('堂·', '唐·', 1, '⑤专名'),
    ],
    # ---- 第 13 章 ----
    'c014/c00/final.txt': [
        ('地方医生', '乡村医生', 1, '⑤职衔'),
        ('多萝西娅', '多罗特娅', 1, '⑤专名'),
        ('堂·阿戈斯丁', '唐·阿戈斯廷', 1, '⑤专名'),
        # ⑦ 异体字：象／像混用，本册多数作「像」
        ('这可不象朋友', '这可不象朋友'.replace('象', '像'), 1, '⑦异体字'),
        ('也不象兄弟', '也不像兄弟', 1, '⑦异体字'),
        ('我象孩子一样高兴', '我像孩子一样高兴', 1, '⑦异体字'),
        ('远远地象应许之地', '远远地像应许之地', 1, '⑦异体字'),
        ('象突然双目失明', '像突然双目失明', 1, '⑦异体字'),
    ],
    # ---- 第 14 章 ----
    'c015/c00/final.txt': [
        ('唐·阿戈斯廷·阿戈斯蒂纳', '唐·阿戈斯廷·阿戈尼斯塔', 1, '⑤专名'),
        ('地方医生', '乡村医生', 1, '⑤职衔'),
    ],
    'c015/c01/final.txt': [
        # ⑤ 原文 Ehren-Pantoffeln / Ehrenstuhl，与全书「荣誉椅」统一
        ('备用的光荣拖鞋', '备用的荣誉拖鞋', 1, '⑤专名'),
        ('那张光荣椅上', '那张荣誉椅上', 1, '⑤专名'),
    ],
    # ---- 第 15 章 ----
    'c016/c00/final.txt': [
        ('阿戈斯丁', '阿戈斯廷', 3, '⑤专名'),
        ('塞纽拉', '塞尼奥拉', 1, '⑤专名'),
        # ① 「还是想也别想的」句尾悬空
        ('动身他往，还是想也别想的。', '动身他往，是想也不必想的。', 1, '①读不通'),
    ],
    # ---- 第 16 章 ----
    'c017/c00/final.txt': [
        ('阿戈斯蒂姆', '阿戈斯廷', 2, '⑤专名'),
        ('我血椅上的朋友', '我血椅岩之交', 1, '⑤专名'),
        ('你那位血椅上的朋友', '你那位血椅岩之交', 1, '⑤专名'),
    ],
}

LOGS = []
for rel in sorted(JOBS):
    p, text = load(rel)
    before_stats = stats(text)
    before_mark = (text.count(u'⟦i⟧'), text.count(u'⟦/i⟧'))
    log = []
    for old, new, expect, label in JOBS[rel]:
        text = sub(text, old, new, expect, label, log)
    assert stats(text) == before_stats, ('line structure changed', rel)
    assert (text.count(u'⟦i⟧'), text.count(u'⟦/i⟧')) == before_mark, ('italic markers changed', rel)
    assert not any(c in '"\'' for c in text), ('ascii quote', rel)
    save(p, text)
    LOGS.append((rel, log))

for rel, log in LOGS:
    print(rel)
    for line in log:
        print(line)
print('total edits:', sum(len(l) for _, l in LOGS))

ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse ok')