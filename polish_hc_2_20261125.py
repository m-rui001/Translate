# -*- coding: utf-8 -*-
"""《人类的和声》润色 第 2 批：hc_d / hc_e / hc_f"""
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


# ---------------- hc_d ----------------
p = 'hc_d_zh.json'
d = load(p)
n0 = len(d)

sub(d,
    '否则他也许会认出那种原始的、祖传的恐惧——他远古的祖先在潮汐的不可解释的恐怖或日食压倒他们、使他们整个已知宇宙面临改变的威胁时所感到的恐惧。',
    '否则他也许会认出那种原始的、祖传的恐惧——当年潮汐那种不可解释的恐怖，或者一场日食，以整个已知宇宙行将改易的威胁压倒他远古的祖先时，他们所感到的就是这个。',
    '①③', '破折号后「所感到的恐惧」套「的恐惧」、状语层层后置，读者断不开；改时间从句')
sub(d,
    '而她以她那颗亲爱的小心灵全部的力量，给了他他所渴求的消息',
    '而她以她那颗亲爱的小心灵全部的力量，把他所渴求的消息给了他',
    '①④', '「他他所」叠字；且两个「他」指两方，改语序')
assert len(d) == n0
save(p, d)
print('hc_d', len(d))

# ---------------- hc_e ----------------
p = 'hc_e_zh.json'
d = load(p)
n0 = len(d)

sub(d, '「斯凯尔走得太远了」，这或许最能概括他日增的忧虑每日的分量。',
    '「斯凯尔走得太远了，」这或许最能概括他日增的忧虑每日的分量。',
    '⑦', '引号内点号体例统一（全书对话收「，」在引号内）')
assert len(d) == n0
save(p, d)
print('hc_e', len(d))

# ---------------- hc_f ----------------
p = 'hc_f_zh.json'
d = load(p)
n0 = len(d)

sub(d, '安全地握在我手里，随时可用。', '安全地握在我手里，随时可用。」',
    '⑦', '跨段长引语按段闭合（该段开引号未收）')
assert len(d) == n0
save(p, d)
print('hc_f', len(d))

for t, i, n in LOG:
    print(t, i, n)
ast.parse(open(__file__, encoding='utf-8').read())
print('AST ok')