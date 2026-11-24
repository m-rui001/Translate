import ast, os

BASE = 'E:/Translate/work_gutenberg/timar'
n_ = 0
log = []

def rd(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()

def wr(p, t):
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(t)

def one(path, old, new, tag):
    global n_
    t = rd(path)
    assert t.count(old) == 1, (path, old, t.count(old))
    wr(path, t.replace(old, new))
    n_ += 1
    log.append((tag, os.path.basename(os.path.dirname(path)), old, new))

def allof(path, old, new, expect, tag):
    t = rd(path)
    before = t.count(old)
    assert before == expect, (path, old, before)
    wr(path, t.replace(old, new))
    assert len(rd(path).split('\n')) == len(t.split('\n'))
    log.append((tag, os.path.basename(os.path.dirname(path)), old + '×' + str(expect), new))

P = lambda rel: os.path.join(BASE, rel)

# p2 误伤修正：阿塔纳什 -> 阿塔纳斯；莫诺什托尔尔 -> 莫诺什托尔
allof(P('out/c022/c02/final.txt'), '阿塔纳斯什', '阿塔纳斯', 1, '⑤修')
allof(P('out/c022/c02/final.txt'), '莫诺什托尔尔', '莫诺什托尔', 3, '⑤修')

for l in log:
    print(l[0], l[1], l[2], '->', l[3])
print(sum(1 for _ in log), 'edits')

ast.parse(open(__file__, encoding='utf-8').read())