# -*- coding: utf-8 -*-
"""《魔山》batch2：职称/称谓归一（专名体例）。整册范围替换，逐文件断言替换数==预统计数。"""
import io, os, glob, ast
from collections import Counter

BASE = 'E:/Translate/work_zauberberg/out'
files = sorted(glob.glob(BASE + '/index_split_*/c*/final.txt'))

RULES = [
    ('舒夏特夫人', '舒夏特太太'),        # Frau Chauchat：以“太太”(143) 为 canon
    ('施托尔夫人', '施托尔太太'),
    ('贝伦斯顾问', '宫廷顾问贝伦斯'),    # Hofrat Behrens：以“宫廷顾问”(274) 为 canon
    ('克罗科夫斯基医生', '克罗科夫斯基博士'),
    ('克罗科夫斯基大夫', '克罗科夫斯基博士'),
    ('中尉', '少尉'),                    # Leutnant，约阿希姆；以“少尉”(16) 为 canon
]

total = 0
for path in files:
    with io.open(path, 'r', encoding='utf-8-sig', newline='') as f:
        text = f.read()
    orig = text
    hits = Counter()
    for old, new in RULES:
        while old in text:
            text = text.replace(old, new, 1)
            hits[old] += 1
    if not hits:
        continue
    # 校验：替换数必须等于原文本中的出现数
    for old, _ in RULES:
        assert orig.count(old) == hits[old], (path, old)
    bak = path + '.bak_20261125'
    if not os.path.exists(bak):
        with io.open(bak, 'w', encoding='utf-8-sig', newline='') as f:
            f.write(orig)
    with io.open(path, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(text)
    print(os.path.basename(os.path.dirname(path)), dict(hits), 'lines', orig.count('\n'), '->', text.count('\n'))
    total += sum(hits.values())

print('total replacements', total)
ast.parse(open(__file__, encoding='utf-8').read())
print('OK')