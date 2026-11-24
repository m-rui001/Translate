import ast, os

BASE = 'E:/Translate/work_gutenberg/timar'
log = []

def rd(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()

def wr(p, t):
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(t)

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

allof(P('out/c028/c00/final.txt'), '蒂马', '蒂马尔', 6, '⑤')
allof(P('out/c029/c01/final.txt'), '潘乔瓦', '潘切沃', 2, '⑤')
allof(P('out/c026/c00/final.txt'), '斯坦布尔', '君士坦丁堡', 1, '⑤')
allof(P('out/c038/c01/final.txt'), '斯坦布尔', '君士坦丁堡', 1, '⑤')
allof(P('out/c038/c04/final.txt'), '斯坦布尔', '君士坦丁堡', 1, '⑤')

print(len(log), 'edits')
for l in log:
    print(l[0], l[1], l[2], '->', l[3])

ast.parse(open(__file__, encoding='utf-8').read())