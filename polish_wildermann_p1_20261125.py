#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""《野人旅馆》(Zum wilden Mann) 通读润色 第 1 批：c002-c007（第 1-6 章）

改法：定位唯一子串 -> 替换 -> 断言命中数；行数、空行数、⟦i⟧ 标记数量不变。
"""
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
    """定位 old 的每一次出现；每次之前先取唯一窗口断言 count==1，再替换。"""
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
    # ---- 第 1 章 ----
    'c002/c00/final.txt': [
        # ⑥ 硬伤：错字「十足够」（原文 sie genügt ... vollkommen）
        ('这条巷子已经十足够了', '这条巷子已经十分足够了', 1, '⑥错字'),
    ],
    # ---- 第 2 章 ----
    'c003/c00/final.txt': [
        # ③ ein Menschenalter über ein Menschenalter hinaus：直搬「一个世代越过一个世代地」
        ('只要能这样一个世代越过一个世代地往回看', '只要能这样一代越过一代地往回看', 1, '③外语句法'),
    ],
    # ---- 第 3 章 ----
    'c004/c00/final.txt': [
        ('林务员', '林务官', 6, '⑤专名'),
        ('地方医生', '乡村医生', 1, '⑤职衔'),
    ],
    # ---- 第 4 章 ----
    'c005/c00/final.txt': [
        ('林务员', '林务官', 4, '⑤专名'),
    ],
    'c005/c01/final.txt': [
        ('林务员', '林务官', 2, '⑤专名'),
    ],
    # ---- 第 5 章 ----
    'c006/c00/final.txt': [
        ('林务员', '林务官', 3, '⑤专名'),
    ],
    # ---- 第 6 章 ----
    'c007/c00/final.txt': [
        ('护林人', '林务官', 5, '⑤专名'),
        ('血椅号', '血椅岩', 2, '⑤专名'),
        ('老姐', '老小姐', 2, '⑦语域'),
        # ① 断句：「这一个人的世代，在这个风暴之夜谈了这么多的一代」
        ('整整三十年，这一个人的世代，在这个风暴之夜谈了这么多的一代。',
         '整整三十年；这一代人的光阴，今晚这场风暴里谈来谈去谈的正是它。', 1, '①读不通'),
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
    after_stats = stats(text)
    after_mark = (text.count(u'⟦i⟧'), text.count(u'⟦/i⟧'))
    assert before_stats == after_stats, ('line structure changed', rel, before_stats, after_stats)
    assert before_mark == after_mark, ('italic markers changed', rel)
    assert not any(ord(c) < 128 and c in '"\'' for c in text), ('ascii quote', rel)
    save(p, text)
    LOGS.append((rel, log))

for rel, log in LOGS:
    print(rel)
    for line in log:
        print(line)
print('total edits:', sum(len(l) for _, l in LOGS))

ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse ok')