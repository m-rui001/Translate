import ast, os, sys

BASE = 'E:/Translate/work_gutenberg/timar'

def rd(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()

def wr(p, t):
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(t)

def one(path, old, new, tag):
    global n_
    """唯一子串替换，断言 count==1"""
    t = rd(path)
    assert t.count(old) == 1, (path, old, t.count(old))
    t2 = t.replace(old, new)
    assert len(t2.split('\n')) == len(t.split('\n')), ('行数变了', path, old)
    wr(path, t2)
    n_ += 1
    log.append((tag, path, old, new))

def allof(path, old, new, expect, tag):
    global n_
    """全文件同名替换：逐处构造唯一窗口并断言，再一次性落盘"""
    t = rd(path)
    assert t.count(old) == expect, (path, old, t.count(old), expect)
    idx = [i for i in range(len(t)) if t.startswith(old, i)]
    edits = []
    for i in idx:
        for w in (8, 16, 30):
            s = t[max(0, i - w): i + len(old) + w]
            if t.count(s) == 1:
                break
        else:
            raise AssertionError(('窗口不唯一', path, old, i))
        edits.append((s, s.replace(old, new)))
    for s, r in sorted(edits, key=lambda x: -t.index(x[0])):
        i = t.index(s)
        t = t[:i] + r + t[i + len(s):]
    assert t.count(old) == 0, (path, old)
    assert len(t.split('\n')) == len(rd(path).split('\n')), ('行数变了', path, old)
    wr(path, t)
    n_ += 1
    log.append((tag, path, f'{old}×{expect}', new))

n_ = 0
log = []

P = lambda rel: os.path.join(BASE, rel)

# ---------- ① 读不通 ----------
one(P('out/c004/c00/final.txt'), '塞尔维亚一侧的那条，是货船上行走的', '塞尔维亚一侧的那条，是货船行走的', '①')
one(P('out/c004/c00/final.txt'), '舵手熟得就像他才量过这条河近几周涨了多少水', '舵手熟得就像他方才量过这条河这几周涨了多少水', '①')
one(P('out/c007/c01/final.txt'), '这是从哪个魔鬼那里听说过，一只狗竟替猎人捡起猎物来的？', '他打哪儿听说过，一只狗竟会替猎人捡起猎物来的？', '①')
one(P('out/c014/c00/final.txt'), '迈克尔除了夜里隔着薄薄的板壁传来她的深长叹息，别的什么也听不见',
    '迈克尔夜里隔着薄薄的板壁只听得见她的深长叹息，别的什么也听不见', '①')

# ---------- ⑤ 专名 ----------
allof(P('out/c002/c01/final.txt'), '阿塔纳修斯', '阿塔纳斯', 1, '⑤')

allof(P('out/c004/c00/final.txt'), '提玛', '蒂马尔', 6, '⑤')
allof(P('out/c004/c01/final.txt'), '克罗采', '克罗伊策', 3, '⑤')

allof(P('out/c005/c00/final.txt'), '埃乌特米奥', '欧泰米奥', 3, '⑤')
allof(P('out/c005/c00/final.txt'), '阿坦·布拉佐维奇', '阿塔纳斯·布拉佐维奇', 1, '⑤')

allof(P('out/c007/c01/final.txt'), '欧塞米奥', '欧泰米奥', 3, '⑤')
allof(P('out/c008/c00/final.txt'), '欧忒弥俄', '欧泰米奥', 2, '⑤')

allof(P('out/c009/c00/final.txt'), '塔纳修斯', '阿塔纳斯', 3, '⑤')
allof(P('out/c009/c00/final.txt'), '潘乔瓦', '潘切沃', 2, '⑤')
allof(P('out/c009/c01/final.txt'), '斯坦布尔', '君士坦丁堡', 1, '⑤')
allof(P('out/c009/c02/final.txt'), '斯坦布尔', '君士坦丁堡', 1, '⑤')
allof(P('out/c009/c02/final.txt'), '泰蕾兹', '特蕾泽', 4, '⑤')
allof(P('out/c010/c00/final.txt'), '斯坦布尔', '君士坦丁堡', 2, '⑤')
allof(P('out/c013/c00/final.txt'), '欧塞米奥', '欧泰米奥', 2, '⑤')

# ---------- ⑤ 宗教称谓（东正教本堂神父一线） ----------
allof(P('out/c009/c00/final.txt'), '主任牧师', '本堂神父', 1, '⑤')
one(P('out/c009/c00/final.txt'), '去求她的牧师们安葬这不幸的人', '去求教士们安葬这不幸的人', '⑤')
allof(P('out/c009/c02/final.txt'), '主任牧师们', '本堂神父们', 1, '⑤')
allof(P('out/c012/c00/final.txt'), '主任牧师', '本堂神父', 5, '⑤')
one(P('out/c012/c00/final.txt'), '有教堂的钟和神甫', '有教堂的钟和神父', '⑤')
one(P('out/c012/c00/final.txt'), '找个牧师来给他下葬', '找个神父来给他下葬', '⑤')
one(P('out/c012/c00/final.txt'), '我来求牧师先生过去一趟', '我来求神父先生过去一趟', '⑤')
one(P('out/c012/c00/final.txt'), '可牧师先生要是不能给他一块祝圣过的坟地', '可神父先生要是不能给他一块祝圣过的坟地', '⑤')

# ---------- ⑥ 外文残留 ----------
one(P('out/c004/c01/final.txt'), 'Mashallah！我们没法跟到那儿去。', '真主在上！我们没法跟到那儿去。', '⑥')

print(n_, 'edits')
for l in log:
    print(l[0], os.path.basename(os.path.dirname(os.path.dirname(l[1]))) + '/' + os.path.basename(os.path.dirname(l[1])), l[2], '->', l[3])

ast.parse(open(__file__, encoding='utf-8').read())