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
    assert before == expect, (path, old, before, expect)
    t2 = t.replace(old, new)
    assert t2.count(old) == expect * new.count(old), (path, old, t2.count(old))
    assert len(t2.split('\n')) == len(t.split('\n')), ('行数变了', path)
    wr(path, t2)
    log.append((tag, path.split('out/')[1], old + '×' + str(expect), new))

P = lambda rel: os.path.join(BASE, rel)

allof(P('out/c020/c00/final.txt'), '米夏埃尔', '迈克尔', 1, '⑤')
# c024/c00：蒂迈尔 -> 蒂马尔，米夏埃尔 -> 迈克尔，阿利·乔尔巴吉 -> 阿里·乔尔巴吉
allof(P('out/c024/c00/final.txt'), '蒂迈尔', '蒂马尔', 8, '⑤')
allof(P('out/c024/c00/final.txt'), '米夏埃尔', '迈克尔', 5, '⑤')
allof(P('out/c024/c00/final.txt'), '阿利·乔尔巴吉', '阿里·乔尔巴吉', 2, '⑤')
allof(P('out/c024/c01/final.txt'), '米哈尔', '迈克尔', 5, '⑤')
allof(P('out/c027/c02/final.txt'), '克丽丝蒂扬', '克里斯蒂安', 2, '⑤')
allof(P('out/c030/c02/final.txt'), '米夏埃尔', '迈克尔', 6, '⑤')
allof(P('out/c032/c03/final.txt'), '米夏埃尔', '迈克尔', 25, '⑤')
allof(P('out/c035/c00/final.txt'), '米夏埃尔', '迈克尔', 9, '⑤')
allof(P('out/c036/c00/final.txt'), '米夏埃尔', '迈克尔', 2, '⑤')

print(len(log), 'edits')
for l in log:
    print(l[0], l[1], l[2], '->', l[3])

ast.parse(open(__file__, encoding='utf-8').read())