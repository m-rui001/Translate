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

def allof(path, old, new, expect, tag):
    t = rd(path)
    before = t.count(old)
    if before == 0 and new in t:
        return
    assert before == expect, (path, old, before, expect)
    t2 = t.replace(old, new)
    assert t2.count(old) == expect * new.count(old), (path, old, t2.count(old))
    assert len(t2.split('\n')) == len(t.split('\n')), ('行数变了', path)
    wr(path, t2)
    log.append((tag, path.split('out/')[1], old + '×' + str(expect), new))

P = lambda rel: os.path.join(BASE, rel)

# ---- ⑤ 专名 ----
allof(P('out/c029/c02/final.txt'), '加拉姆博茨', '加兰博什', 2, '⑤')
for sub, k in (('c038/c00', 4), ('c038/c01', 1), ('c038/c02', 1), ('c038/c03', 1), ('c038/c04', 1)):
    allof(P('out/%s/final.txt' % sub), '克里斯强', '克里斯蒂安', k, '⑤')
allof(P('out/c038/c03/final.txt'), '泰蕾兹', '特蕾泽', 1, '⑤')
allof(P('out/c033/c00/final.txt'), '泰蕾兹', '特蕾泽', 3, '⑤')
allof(P('out/c038/c04/final.txt'), '娜奥米', '诺埃米', 13, '⑤')
allof(P('out/c039/c00/final.txt'), '阿达莉', '阿塔莉', 1, '⑤')
allof(P('out/c041/c00/final.txt'), '米哈伊', '迈克尔', 2, '⑤')
allof(P('out/c041/c00/final.txt'), '加兰博斯', '加兰博什', 1, '⑤')
allof(P('out/c045/c00/final.txt'), '阿塔莉耶', '阿塔莉', 19, '⑤')

# ---- ⑥ 硬伤／体例：梭鲈 的括注与空格 ----
one(P('out/c037/c00/final.txt'), '咱们连 梭鲈 之王也能捉上来', '咱们连梭鲈之王也能捉上来', '⑦')
one(P('out/c037/c00/final.txt'), '那是一条老 梭鲈，湖上每个渔夫', '那是一条老梭鲈，湖上每个渔夫', '⑦')
allof(P('out/c037/c01/final.txt'), '梭鲈（梭鲈）', '梭鲈', 2, '⑥')

print(len(log), 'edits')
for l in log:
    print(l[0], l[1], l[2], '->', l[3])

ast.parse(open(__file__, encoding='utf-8').read())