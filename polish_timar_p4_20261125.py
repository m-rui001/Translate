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

allof(P('out/c029/c00/final.txt'), '斯卡拉穆奇', '斯卡拉梅利', 3, '⑤')
allof(P('out/c029/c00/final.txt'), '第里雅斯特', '的里雅斯特', 2, '⑤')
allof(P('out/c029/c01/final.txt'), '斯卡拉穆奇', '斯卡拉梅利', 3, '⑤')
allof(P('out/c029/c01/final.txt'), '莱韦廷茨基', '莱韦廷齐', 3, '⑤')
allof(P('out/c029/c03/final.txt'), '西奥多', '特奥多尔', 1, '⑤')
allof(P('out/c030/c00/final.txt'), '米迦勒', '迈克尔', 10, '⑤')
allof(P('out/c030/c01/final.txt'), '米歇尔', '迈克尔', 8, '⑤')
allof(P('out/c030/c03/final.txt'), '米迦勒', '迈克尔', 2, '⑤')
allof(P('out/c031/c02/final.txt'), '米迦勒', '迈克尔', 11, '⑤')
allof(P('out/c032/c01/final.txt'), '米歇尔', '迈克尔', 7, '⑤')
allof(P('out/c032/c02/final.txt'), '米哈伊尔', '迈克尔', 5, '⑤')
allof(P('out/c032/c02/final.txt'), '纳西萨', '娜西莎', 1, '⑤')
allof(P('out/c033/c02/final.txt'), '米迦勒', '迈克尔', 6, '⑤')
allof(P('out/c033/c02/final.txt'), '提玛', '蒂马尔', 13, '⑤')
allof(P('out/c033/c03/final.txt'), '米迦勒', '迈克尔', 3, '⑤')
allof(P('out/c034/c00/final.txt'), '特蕾莎', '特蕾泽', 2, '⑤')
allof(P('out/c037/c01/final.txt'), '米哈伊尔', '迈克尔', 1, '⑤')
allof(P('out/c037/c02/final.txt'), '米迦勒', '迈克尔', 3, '⑤')
allof(P('out/c038/c00/final.txt'), '米哈伊尔', '迈克尔', 1, '⑤')
allof(P('out/c038/c01/final.txt'), '米哈伊尔', '迈克尔', 2, '⑤')
allof(P('out/c038/c01/final.txt'), '潘乔瓦', '潘切沃', 1, '⑤')
allof(P('out/c038/c03/final.txt'), '米哈伊尔', '迈克尔', 1, '⑤')
allof(P('out/c038/c04/final.txt'), '米哈伊尔', '迈克尔', 1, '⑤')
allof(P('out/c039/c00/final.txt'), '米哈伊尔', '迈克尔', 1, '⑤')
allof(P('out/c039/c00/final.txt'), '西奥多', '特奥多尔', 1, '⑤')
allof(P('out/c039/c00/final.txt'), '多多尔', '多迪', 1, '⑤')
allof(P('out/c042/c00/final.txt'), '米迦勒', '迈克尔', 14, '⑤')
allof(P('out/c043/c00/final.txt'), '米迦勒', '迈克尔', 1, '⑤')
allof(P('out/c043/c01/final.txt'), '米哈伊尔', '迈克尔', 2, '⑤')
allof(P('out/c043/c01/final.txt'), '多多迪', '多迪', 1, '⑤')
allof(P('out/c043/c01/final.txt'), '莱韦廷茨基', '莱韦廷齐', 1, '⑤')
allof(P('out/c045/c01/final.txt'), '米哈伊尔', '迈克尔', 2, '⑤')

print(len(log), 'edits')
for l in log:
    print(l[0], l[1], l[2], '->', l[3])

ast.parse(open(__file__, encoding='utf-8').read())