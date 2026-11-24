# -*- coding: utf-8 -*-
"""《人类的和声》润色 第 1 批：hc_a / hc_b / hc_c
只做「定位唯一子串 → 替换 → 断言命中数」，不重写整文件。
"""
import json, io, sys

LOG = []


def load(p):
    with io.open(p, encoding='utf-8', newline='') as f:
        raw = f.read()
    return json.loads(raw), raw


def save(p, data):
    with io.open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1).replace('\n', '\r\n'))
    # 保尾换行
    with io.open(p, 'rb') as f:
        b = f.read()
    if not b.endswith(b'\r\n'):
        with io.open(p, 'ab') as f:
            f.write(b'\r\n')


def sub(data, old, new, tag, note=''):
    n = sum(x.count(old) for x in data)
    if n == 0:                      # 幂等：已应用过则跳过
        assert sum(x.count(new) for x in data) >= 1, (tag, 'missing', old[:40])
        LOG.append((tag, '已应用', note))
        return
    assert n == 1, (tag, n, old[:40])
    for i, x in enumerate(data):
        if old in x:
            data[i] = x.replace(old, new)
            LOG.append((tag, i, note))
            return


def sub_all(data, old, new, expect, tag, note=''):
    n = sum(x.count(old) for x in data)
    if n == 0:
        assert sum(x.count(new) for x in data) >= expect, (tag, 'missing', old[:40])
        LOG.append((tag, '已应用', note))
        return
    assert n == expect, (tag, n, old[:40])
    for i, x in enumerate(data):
        if old in x:
            data[i] = x.replace(old, new)
            LOG.append((tag, i, note))


# ---------------- hc_a ----------------
p = 'hc_a_zh.json'
d, _ = load(p)
n0 = len(d)

sub(d,
    '而对一个八岁的男孩来说，从十点到凌晨四点他悄悄爬回育儿室自己那个角落为止，那些寒冷而闹鬼似的钟点一定漫长得没有尽头。',
    '而对一个八岁的男孩来说，从十点到凌晨四点——直到他悄悄爬回育儿室自己那个角落——那些寒冷而闹鬼似的钟点一定漫长得没有尽头。',
    '①', '「从…到…为止」夹在时间状语里，主谓断裂，改插入语')
sub(d, '而是跑进自己那片内心的草原大声喊', '而是跑进自己那片心智草原大声喊',
    '⑤', '术语统一：mental prairie 作「心智草原」')
sub(d,
    '是某种能证实——哪怕不能真的替代——他少年时沉醉其中的那片惊奇与欢悦的内里国土的东西，而那片国土早已被教育',
    '是某种东西，能证实——哪怕不能真的替代——他少年时沉醉其中的那片惊奇与欢悦的内里国土；而那片国土早已被教育',
    '②', '「某种……的东西」长定语压住中心语，拆成判断句')
assert len(d) == n0
save(p, d)
print('hc_a done', len(d))

# ---------------- hc_b ----------------
p = 'hc_b_zh.json'
d, _ = load(p)
n0 = len(d)

sub(d, '跑到童蒙时代那片广大的内心草原上去', '跑到童蒙时代那片广大的心智草原上去', '⑤', '术语统一')
sub(d, '少年时代那片内心草原的远方', '少年时代那片心智草原的远方', '⑤', '术语统一')
sub(d, '那时他认识温基。', '那时他认识「眨眨」。', '⑤', '专名归一：Winky＝「眨眨」（全册 28 处，此 1 处作「温基」）')
sub(d, '号令着耳朵尚未安家的那一片空间。', '号令着耳朵尚未安家的那一片空间。」', '⑦', '跨段引语按段闭合（诗行段补收引号）')
sub(d, '木、石、金属、皮、纤维、膜，每一种迅速振动的物质，自身都含有乐音的潜能。',
    '木、石、金属、皮、纤维、膜，每一种迅速振动的物质，自身都含有乐音的潜能。」', '⑦', '同上')
sub(d, '有朝一日，一千年之后，我们会知道这宏伟和声的全部范围。',
    '有朝一日，一千年之后，我们会知道这宏伟和声的全部范围。」', '⑦', '同上')
sub(d, '等着知晓它、并且敢于大大冒险的人去释放。',
    '等着知晓它、并且敢于大大冒险的人去释放。」', '⑦', '同上')
sub(d,
    '弦音是能够这样抵达一个人的精神中心、使他应和超出他寻常音域的思想的微妙振动的……',
    '弦音竟能这样抵达一个人的精神中心，使他应和那些超出他寻常音域的思想的微妙振动……',
    '①②', '「思想の微妙振動の…」三「的」叠加且以「的……」收尾，改拆句')
assert len(d) == n0
save(p, d)
print('hc_b done', len(d))

# ---------------- hc_c ----------------
p = 'hc_c_zh.json'
d, _ = load(p)
n0 = len(d)

sub_all(d, '教士', '牧师', 26, '⑤', '职衔归一：hc_a/b/d/e/f 全作「牧师」，hc_c 独用「教士」26 处')
sub(d, '扫清了他听者心中所有的疑虑', '扫清了他的听者心中所有的疑虑', '①', '脱字')
sub_all(d, '萨拉莫尔', '萨拉·莫尔', 3, '⑤', '专名体例：Mrs. Mawle 作「萨拉·莫尔」')
sub(d,
    '在斯凯尔那座群山之间孤零零的宅子的那间茶室里，背上照着一炉人间之火的温暖',
    '在群山之间那座孤零零的斯凯尔宅子的茶室里，背上照着一炉人间之火的温暖',
    '②', '四「的」连缀，改拆')
sub(d,
    '对那向他显示了他的真我可以容纳何等荣光的男人和姑娘的感激之感如此强烈，以致他发出一声',
    '对那个男人和那个姑娘的感激之情如此强烈——是他们向他显示了他的真我可以容纳何等荣光——以致他发出一声',
    '②③', '关系从句后置＋「的」堆叠，改为插入语')
assert len(d) == n0
save(p, d)
print('hc_c done', len(d))

print('--- 改动清单 ---')
for t, i, note in LOG:
    print(t, i, note)

ast_ok = True
import ast
ast.parse(open(__file__, encoding='utf-8').read())
print('AST ok')