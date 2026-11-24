# -*- coding: utf-8 -*-
"""《吉姆博》润色 第 2 批：jb_d / jb_e"""
import json, io, ast

LOG = []


def load(p):
    with io.open(p, encoding='utf-8', newline='') as f:
        return json.load(f)


def save(p, data):
    with io.open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1).replace('\n', '\r\n') + '\r\n')


def sub(data, old, new, tag, note=''):
    n = sum(x.count(old) for x in data)
    assert n == 1, (tag, n, old[:40])
    for i, x in enumerate(data):
        if old in x:
            data[i] = x.replace(old, new)
            LOG.append((tag, i, note))
            return


# ---------------- jb_d ----------------
p = 'jb_d_zh.json'
d = load(p)
n0 = len(d)

sub(d, '有时他一直悬到身子往下掉，才靠着贴着水面划出一个极大的弧线，救了自己没落进水里',
    '有时他一直悬到身子往下掉，才贴着水面划出一个极大的弧线，救了自己没落进水里',
    '①', '「靠着贴着」两个动介词叠在一起，读不通')
sub(d, '他往下看时不免打了个寒噤，明白过不了多久他就得屈服于这股致命的力量',
    '他往下看时不免打了个寒噤，明白过不了多久就得屈服于这股致命的力量',
    '①', '「他」与前面「孩子」混指，且句内两个「他」指不同主语')
assert len(d) == n0
save(p, d)
print('jb_d', len(d))

# ---------------- jb_e ----------------
p = 'jb_e_zh.json'
d = load(p)
n0 = len(d)

sub(d, '他觉得自已被往屋里拉', '他觉得自己被往屋里拉', '⑥', '错字「自已」')
assert len(d) == n0
save(p, d)
print('jb_e', len(d))

for t, i, n in LOG:
    print(t, i, n)
ast.parse(open(__file__, encoding='utf-8').read())
print('AST ok')