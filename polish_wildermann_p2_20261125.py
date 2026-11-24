#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""《野人旅馆》通读润色 第 2 批：c008-c012（第 7-11 章）"""
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
    # ---- 第 7 章 ----
    'c008/c00/final.txt': [
        ('地区医生', '乡村医生', 3, '⑤职衔'),
        ('医士', '医生', 2, '⑤职衔'),
        ('多姆', '唐', 2, '⑤专名'),
        # ⑤ 地名：「坐过血椅」与全书「血椅岩」不合
        ('您这辈子可曾坐过血椅？', '您这辈子可曾坐过血椅岩？', 1, '⑤专名'),
    ],
    'c008/c01/final.txt': [
        ('地区医生', '乡村医生', 1, '⑤职衔'),
        ('多姆', '唐', 3, '⑤专名'),
    ],
    # ---- 第 8 章 ----
    'c009/c00/final.txt': [
        ('护林员', '林务官', 2, '⑤专名'),
        ('多姆', '唐', 2, '⑤专名'),
        # ① 原文 dem Freunde vom Blutstuhle：现译「血凳上的朋友」易读成坐在凳上的人
        ('把右手从血凳上的朋友手里抽出来', '把右手从那位血椅岩之交的手里抽出来', 1, '①读不通'),
        ('血凳', '血椅岩', 2, '⑤专名'),
        # ③ 「面对一切在院墙外边发生、进行的事情」直搬 Vorgänge，动词化
        ('面对一切在院墙外边发生、进行的事情却完全未成年', '面对院墙外边发生的一切却完全未成年', 1, '③外语句法'),
    ],
    'c009/c01/final.txt': [
        ('血凳', '血椅岩', 2, '⑤专名'),
        ('多姆', '唐', 1, '⑤专名'),
    ],
    # ---- 第 9 章 ----
    'c010/c00/final.txt': [
        ('阿戈斯蒂诺', '阿戈斯廷', 2, '⑤专名'),
        ('两位血椅上的朋友', '两位血椅岩之交', 1, '⑤专名'),
        ('白撒旦', '白魔鬼', 1, '⑤专名'),
        ('智利共和国巡航舰', '智利共和国三桅战舰', 1, '⑤专名'),
        # ③ sich allerlei um die Nase wehen lassen 直搬成「任其往鼻子上吹」
        ('各种东西他都任其往鼻子上吹', '各样风浪他都任它从鼻尖上刮过去', 1, '③外语句法'),
    ],
    # ---- 第 10 章 ----
    'c011/c00/final.txt': [
        ('多姆', '唐', 3, '⑤专名'),
        ('血椅子', '血椅岩', 1, '⑤专名'),
    ],
    # ---- 第 11 章 ----
    'c012/c00/final.txt': [
        ('阿戈斯蒂诺', '阿戈斯廷', 3, '⑤专名'),
        # ⑥ 硬伤：客人住楼上，此处是下楼（原文 auf der Treppe，上文「十分钟后下来」）
        ('已经听得见他上楼梯时那军人式的沉重脚步', '已经听得见他下楼梯时那军人式的沉重脚步', 1, '⑥硬伤'),
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