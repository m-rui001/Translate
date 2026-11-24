import ast, os

BASE = 'E:/Translate/work_gutenberg/timar'
log = []

def rd(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()

def wr(p, t):
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(t)

def one(path, old, new, tag):
    t = rd(path)
    if t.count(old) == 0 and new in t:
        return
    assert t.count(old) == 1, (path, old, t.count(old))
    t2 = t.replace(old, new)
    assert len(t2.split('\n')) == len(t.split('\n')), ('行数变了', path)
    wr(path, t2)
    log.append((tag, path.split('out/')[1], old, new))

P = lambda rel: os.path.join(BASE, rel)

# ③ 外语句法直搬 / ① 读不通
one(P('out/c035/c03/final.txt'), '可这个人在他作为一家之主这一点上，有许多话要说。',
    '可关于他做一家之主的情形，那人还有许多话要说。', '③')
one(P('out/c010/c00/final.txt'), '而是为了两样东西，我成熟待割了；这两样就是我的钱和我的女儿。',
    '而是为了两样东西，我像熟透的庄稼一样等着开镰；这两样就是我的钱和我的女儿。', '①')
one(P('out/c019/c00/final.txt'), '从来不曾有一个人这样落到他眼前',
    '从来不曾有一个人这样站到他面前', '①')
# ⑤ 专名体例：连字符改中圆点（全书其余均作“蒂马尔·莱韦廷齐”）
one(P('out/c019/c00/final.txt'), '迈克尔·蒂马尔-莱韦廷齐略一沉吟',
    '迈克尔·蒂马尔·莱韦廷齐略一沉吟', '⑤')

print(len(log), 'edits')
for l in log:
    print(l[0], l[1], l[2], '->', l[3])

ast.parse(open(__file__, encoding='utf-8').read())