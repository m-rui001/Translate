# -*- coding: utf-8 -*-
"""高老头 c042-c044 润色（p6）。定位唯一子串 → 替换 → 断言命中数。"""
import os, shutil, ast

BASE = 'work_pub/goriot/out/c001'
EDITS = [
    # --- c41 补：诨名 Trompe-la-Mort 归一 ---
    ('c41', '倘若他就是那个骗死鬼', '倘若他就是那个死不了', '专名：Trompe-la-Mort 全册作“死不了”（10 次），“骗死鬼”归一'),
    ('c41', '耳朵里被“骗死鬼”这个颇为别致的字眼撞了一下', '耳朵里被“死不了”这个颇为别致的字眼撞了一下', '专名：同上'),
    ('c41', '倘若伏脱冷先生就是那个骗死鬼', '倘若伏脱冷先生就是那个死不了', '专名：同上'),
    # --- c42 ---
    ('c42', '“先生们，”克利斯托夫喊道', '“先生们，”克里斯托夫喊道', '专名：全册作“克里斯托夫”（61 次），“克利斯托夫”归一'),
    ('c42', '米舍诺小姐，”他发觉老姑娘正打量他', '米旭诺小姐，”他发觉老姑娘正打量他', '专名：全册作“米旭诺”（69 次），“米舍诺”归一'),
    # --- c43 ---
    ('c43', '一小瓶‘瓶儿阵仗’的波尔多', '一小瓶‘瓶儿全景’的波尔多',
            '硬伤：balzac 自造词 bouteillorama（bouteille＋-rama／全景）译成“瓶儿阵仗”不成词，改“瓶儿全景”'),
    # --- c44 ---
    ('c44', '名叫贡德莱的高级警官', '名叫贡杜罗的高级警官', '专名：Gondureau 归一到“贡杜罗”'),
    ('c44', '贡德雷便向她解释', '贡杜罗便向她解释', '专名：同上，同章内“贡德莱／贡德雷”两写，今归一'),
    ('c44', '伏盖夫人对自己的房客说', '伏盖太太对自己的房客说', '专名：全册作“伏盖太太”，“伏盖夫人”归一'),
    ('c44', '“拉雪兹神甫公墓的维纳斯”这个绰号', '“拉雪兹神父公墓的维纳斯”这个绰号', '专名：Père-Lachaise 通译“拉雪兹神父公墓”，与 c43 一致'),
    ('c44', '忘了向米旭诺小姐打听“骗死人不偿命”的事', '忘了向米旭诺小姐打听“死不了”的事', '专名：同一诨名前后三称，归一到“死不了”'),
]


def main():
    for ch, old, new, why in EDITS:
        p = os.path.join(BASE, ch, 'final.txt')
        bak = p + '.bak_20261125b'
        if not os.path.exists(bak):
            shutil.copy2(p, bak)
        with open(p, encoding='utf-8', newline='') as f:
            t = f.read()
        assert old in t, ('MISS', ch, old)
        assert t.count(old) == 1, ('DUP', ch, old, t.count(old))
        n0 = t.count('\n')
        t2 = t.replace(old, new)
        assert t2.count('\n') == n0, ('NL', ch, why)
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(t2)
        print('OK', ch, why)
    print('total', len(EDITS))


main()
ast.parse(open(__file__, encoding='utf-8').read())
print('ast ok')