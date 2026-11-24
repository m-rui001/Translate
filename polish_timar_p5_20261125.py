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

# ---- ① 读不通 ----
one(P('out/c031/c01/final.txt'), '把枪往肩上一挎，也不等主人露面，便出了牧师住宅',
    '把枪往肩上一挎，也不等主人露面，便出了教长的宅子', '⑤')

# ---- ⑤ 专名 ----
allof(P('out/c035/c00/final.txt'), '蒂玛', '蒂梅娅', 7, '⑤')
allof(P('out/c032/c03/final.txt'), '泰蕾兹', '特蕾泽', 6, '⑤')
allof(P('out/c031/c02/final.txt'), '多多', '多迪', 7, '⑤')
allof(P('out/c033/c03/final.txt'), '多多', '多迪', 4, '⑤')
allof(P('out/c035/c00/final.txt'), '新瑟尼', '乌伊瑟尼', 1, '⑤')
allof(P('out/c037/c00/final.txt'), '新瑟尼', '乌伊瑟尼', 1, '⑤')
allof(P('out/c033/c02/final.txt'), '富雷德', '菲赖德', 1, '⑤')

print(len(log), 'edits')
for l in log:
    print(l[0], l[1], l[2], '->', l[3])

ast.parse(open(__file__, encoding='utf-8').read())