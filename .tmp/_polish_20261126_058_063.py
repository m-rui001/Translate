# -*- coding: utf-8 -*-
"""v3 chunk058/059/060/062/063 逐段润色（2026-11-26 轮）。

用法：
    python _polish_20261126_058_063.py --dry   # 只验断言与字数，不落盘
    python _polish_20261126_058_063.py         # 落盘

铁律：定位唯一子串 → 替换 → assert text.count(old) == 1；不整文件重写；
     读写 newline='' 保原换行符；不改段数/行数/空行结构。
"""
import ast
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

# 每条：(chunk, 类别, old, new)
EDITS = [
    # ---------------- chunk058 ----------------
    ('chunk058', '①',
     '一旦她不再有什么可指望他，她就会离开他，或者至少会随心所欲地生活',
     '一旦她再也不能从他身上指望什么，她就会离开他，或者至少会随心所欲地生活'),
    ('chunk058', '①',
     '一旦她不再有什么可指望他，她就会急忙',
     '一旦她再也不能从他身上指望什么，她就会急忙'),
    ('chunk058', '③',
     '；而它们也让人想到水库的房间，或人为了某种捕鱼或牡蛎养殖而划分开的大海的一些部分，'
     '当人们看到依照朝向，光线在枝条上、在树篱上嬉戏，如同在春水上，'
     '并四处涌起那闪烁的、在枝条那透空的格架与蔚蓝之间翻腾的白色泡沫'
     '——一朵沐浴阳光、泛着泡沫的花的泛白泡沫——时。',
     '；而每当人们看到光线依着朝向在枝条上、在树篱上嬉戏，如同在春水上，'
     '并四处涌起那闪烁的、在枝条那透空的格架与蔚蓝之间翻腾的白色泡沫'
     '——一朵沐浴阳光、泛着泡沫的花的泛白泡沫——时，'
     '它们便也让人想到水库的房间，或人为了某种捕鱼或牡蛎养殖而划分开的大海的一些部分。'),
    ('chunk058', '③',
     '她的容貌并不出众，我看得很清楚，他想的是完全相反，他说这话只是为了让我对她的赞赏更加浓烈，'
     '她尤其有一种奇妙的判断力。',
     '她的容貌并不出众（我看得很清楚，他想的是完全相反，他说这话只是为了让我对她的赞赏更加浓烈），'
     '她尤其有一种奇妙的判断力。'),

    # ---------------- chunk059 ----------------
    ('chunk059', '⑥',
     '就是几年前那个女人，——“那一边的女人，境遇变起来真快，女人的境遇尤其如此，”',
     '就是几年前那个女人，——“那一行里，女人的境遇变起来快得很，一旦变起来就是这样，”'),
    ('chunk059', '⑥',
     '我本来可以听说她跟罗贝尔有过许多次幽会',
     '我本来可以打听到她跟罗贝尔有过多少回床笫之事'),
    ('chunk059', '①',
     '这女人的脸便是这样一小块，只要想象力是先认识她的；',
     '这女人的脸便是这样一小块，只要先认识她的是想象力；'),
    ('chunk059', '①',
     '即使她没有察觉、尤其是她察觉了，一场可怕的游戏便开始了',
     '即使她没有察觉，尤其若她察觉到了，一场可怕的游戏便开始了'),
    ('chunk059', '⑥',
     '的确，罗贝尔和我同时望着她，却看不见她处在同一面的神秘之中。',
     '的确，罗贝尔和我同时望着她，却不是从神秘的同一面看她的。'),

    # ---------------- chunk060 ----------------
    ('chunk060', '④',
     '而它也确实有几分以同样的方式打动了我',
     '而它们的美也确实有几分以同样的方式打动了我'),

    # ---------------- chunk062 ----------------
    ('chunk062', '③',
     '“可你很清楚我有很多工作要做——她把戏剧艺术看得很认真。再说，你家里会怎么说呢？”',
     '“可你很清楚我有很多工作要做（她把戏剧艺术看得很认真）。再说，你家里会怎么说呢？”'),
    ('chunk062', '⑤',
     '虚伪的本堂神甫',
     '虚伪的本堂神父'),
    ('chunk062', '②',
     '人们如今几乎只能在那些过时的小剧院那卑微地具有历史意义的门厅里所展出的肖像收藏中',
     '人们如今几乎只能在那些卑微地具有历史意义的过时小剧院门厅里所展出的肖像收藏中'),

    # ---------------- chunk063 ----------------
    ('chunk063', '①',
     '领班们一个个都长着那样的面孔，仿佛随着王宫剧院整整一代卓绝演员的消逝而一同消失了',
     '领班们一个个都长着那种仿佛随王宫剧院整整一代卓绝演员一同消失了的面孔'),
    ('chunk063', '①',
     '正如已经到场的法兰西学会院士们，一面交换几句听不见的话，一面向公众投来那样的目光。',
     '正如已经到场的法兰西学会院士们一面交换几句听不见的话、一面向公众投去的那种目光。'),
    ('chunk063', '⑥',
     '要是我错了，我就不说了，这倒没关系。',
     '要是我错了，算我没说，这倒没关系。'),
]

CHUNKS = ['chunk058', 'chunk059', 'chunk060', 'chunk062', 'chunk063']


def cjk(t):
    return sum(1 for ch in t if '\u4e00' <= ch <= '\u9fff')


def main(dry):
    stats = {}
    for c in CHUNKS:
        p = os.path.join(HERE, c, 'final.txt')
        with open(p, encoding='utf-8', newline='') as f:
            text = f.read()
        before_cjk = cjk(text)
        n_before = text.count('\r\n') if '\r\n' in text else 0
        for ch, cat, old, new in [e for e in EDITS if e[0] == c]:
            cnt = text.count(old)
            assert cnt == 1, f'{c} {cat} 命中 {cnt} 次: {old[:40]}'
            text = text.replace(old, new)
        after_cjk = cjk(text)
        lines = text.replace('\r\n', '\n').split('\n')
        paras = [x for x in lines if x.strip()]
        stats[c] = (len(lines), len(paras), before_cjk, after_cjk,
                    sum(1 for e in EDITS if e[0] == c),
                    'CRLF' if n_before else 'LF', text, p)
    total = 0
    for c in CHUNKS:
        ln, pa, b, a, n, nl, text, p = stats[c]
        total += n
        print(f'{c}: lines {ln} paras {pa} cjk {b}->{a} edits {n} {nl}')
    frm = {}
    for _, cat, _, _ in EDITS:
        frm[cat] = frm.get(cat, 0) + 1
    print('合计改动', total, '条：', ' '.join(f'{k} {v}' for k, v in sorted(frm.items())))
    if dry:
        print('[dry-run] 未落盘')
        return 0
    for c in CHUNKS:
        ln, pa, b, a, n, nl, text, p = stats[c]
        bpath = os.path.join(HERE, c, BAK)
        if not os.path.exists(bpath):
            shutil.copy2(p, bpath)
            print('backup ->', bpath)
        else:
            print('backup exists, not overwritten:', bpath)
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        print('written', p)
    return 0


if __name__ == '__main__':
    rc = main('--dry' in sys.argv)
    ast.parse(open(__file__, encoding='utf-8').read())
    sys.exit(rc)