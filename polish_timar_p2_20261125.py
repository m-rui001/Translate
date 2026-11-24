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
    t2 = t.replace(old, new)
    assert len(t2.split('\n')) == len(t.split('\n')), ('行数变了', path)
    wr(path, t2)
    n_ += 1
    log.append((tag, path, old, new))

def allof(path, old, new, expect, tag):
    global n_
    t = rd(path)
    before = t.count(old)
    assert before == expect, (path, old, before, expect)
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
    assert t.count(old) == before - expect + expect * new.count(old), (path, old, t.count(old))
    assert len(t.split('\n')) == len(rd(path).split('\n')), ('行数变了', path)
    wr(path, t)
    n_ += 1
    log.append((tag, path, f'{old}×{expect}', new))

P = lambda rel: os.path.join(BASE, rel)

# ---- c015 ----
allof(P('out/c015/c01/final.txt'), '克莱泽', '克罗伊策', 1, '⑤')
# ---- c016 ----
one(P('out/c016/c00/final.txt'), '那时你就有了一万默尔登的谷子', '那时你就有了一万袋谷子', '⑥')
allof(P('out/c016/c01/final.txt'), '克鲁采', '克罗伊策', 1, '⑤')
# ---- c017 ----
allof(P('out/c017/c00/final.txt'), '蒂马', '蒂马尔', 14, '⑤')
allof(P('out/c017/c00/final.txt'), '丘尔巴吉', '乔尔巴吉', 2, '⑤')
allof(P('out/c017/c00/final.txt'), '坎迪亚', '干地亚', 1, '⑤')
allof(P('out/c017/c01/final.txt'), '蒂马', '蒂马尔', 3, '⑤')
allof(P('out/c017/c01/final.txt'), '康莫恩', '科莫恩', 1, '⑤')
one(P('out/c017/c01/final.txt'), '一辆四匹马拉的驿车沿着敞式大路疾驰', '一辆四匹马拉的驿车沿着通往乌伊瑟尼的大路疾驰', '⑥')
# ---- c018 ----
allof(P('out/c018/c00/final.txt'), '卡楚卡', '卡丘卡', 1, '⑤')
allof(P('out/c018/c01/final.txt'), '潘乔瓦', '潘切沃', 1, '⑤')
# ---- c019 ----
allof(P('out/c019/c01/final.txt'), '恰伊基斯', '柴基斯特', 1, '⑤')
allof(P('out/c019/c01/final.txt'), '神甫', '神父', 3, '⑤')
# ---- c021 ----
allof(P('out/c021/c00/final.txt'), '莱韦廷采', '莱韦廷齐', 1, '⑤')
allof(P('out/c021/c00/final.txt'), '阿塔纳', '阿塔纳斯', 5, '⑤')
allof(P('out/c021/c00/final.txt'), '乌伊-Szöny', '乌伊瑟尼', 2, '⑥')
# ---- c022 ----
allof(P('out/c022/c01/final.txt'), '苏菲', '索菲', 7, '⑤')
allof(P('out/c022/c02/final.txt'), '莫诺斯托', '莫诺什托尔', 3, '⑤')
allof(P('out/c022/c02/final.txt'), '阿塔纳', '阿塔纳斯', 1, '⑤')
# ---- c023 ----
allof(P('out/c023/c02/final.txt'), '苏菲', '索菲', 9, '⑤')
allof(P('out/c023/c02/final.txt'), '米迦勒', '迈克尔', 3, '⑤')
allof(P('out/c023/c03/final.txt'), '苏菲', '索菲', 6, '⑤')
# ---- c024 ----
allof(P('out/c024/c00/final.txt'), '布拉索维奇', '布拉佐维奇', 2, '⑤')
allof(P('out/c024/c01/final.txt'), '提玛', '蒂马尔', 3, '⑤')
# ---- c025 ----
for sub, k in (('c025/c00', 4), ('c025/c01', 8), ('c025/c02', 8)):
    allof(P('out/%s/final.txt' % sub), '米哈伊尔', '迈克尔', k, '⑤')
# ---- c026 ----
allof(P('out/c026/c00/final.txt'), '米迦勒', '迈克尔', 9, '⑤')
allof(P('out/c026/c00/final.txt'), '纳西萨', '娜西莎', 7, '⑤')
allof(P('out/c026/c01/final.txt'), '泰蕾兹', '特蕾泽', 10, '⑤')
allof(P('out/c026/c01/final.txt'), '纳西萨', '娜西莎', 2, '⑤')
allof(P('out/c026/c03/final.txt'), '米迦勒', '迈克尔', 2, '⑤')
# ---- c027 ----
for sub, k in (('c027/c00', 4), ('c027/c01', 2), ('c027/c02', 1), ('c027/c03', 3)):
    allof(P('out/%s/final.txt' % sub), '米哈伊尔', '迈克尔', k, '⑤')

print(n_, 'edits')
for l in log:
    print(l[0], l[1].split('out/')[1], l[2], '->', l[3])

ast.parse(open(__file__, encoding='utf-8').read())