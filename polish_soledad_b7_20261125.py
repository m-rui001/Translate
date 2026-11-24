# -*- coding: utf-8 -*-
"""《百年孤独》通读润色 第7批（capitulo017-020）＋收尾专名归一。"""
import ast
import glob
import shutil

ROOT = 'E:/Translate/work_soledad/out'
BAK = '.bak_20261125'

EDITS = [
    # ---------------- capitulo017 ----------------
    ('capitulo017',
     '“时间在流逝。”',
     '“时间在过啊。”',
     '5) 第七章同一句回声作「时间在过啊」（el tiempo pasa），此处统一'),
    ('capitulo017',
     '“是啊，”乌尔苏拉说，“可也没那么快。”',
     '“是啊，”乌尔苏拉说，“可也没过这么多。”',
     '5) 第七章同一句回声作「可也没过这么多」（pero no tanto），此处统一'),
    ('capitulo017',
     '于是乌尔苏拉屈服于事实了。',
     '于是乌尔苏拉认了这个事实。',
     '1) 「屈服于事实了」动宾与语气都不顺'),

    # ---------------- capitulo018 ----------------
    ('capitulo018',
     '诺斯特拉达姆斯的⟦i⟧Centurias⟦/i⟧及其对瘟疫的探究',
     '诺斯特拉达穆斯的⟦i⟧Centurias⟦/i⟧及其对瘟疫的探究',
     '⑤Nostradamus 全册作「诺斯特拉达穆斯」（×5），此处归一'),
    ('capitulo018',
     '那些金鱼藏在何处，只有她和奥雷里亚诺知道，就是士兵搜查房子的那一夜。',
     '那些金鱼藏在何处，只有她和奥雷里亚诺知道——还是士兵搜查房子的那一夜她才知道的。',
     '①末句「就是……那一夜」悬空，与前半句接不上'),
    ('capitulo018',
     '那笔遗产本该把他从贫困与肮脏中拯救出来，那是他在特拉斯提弗列一间阁楼里和两个朋友共度的日子。',
     '那笔遗产本该把他从贫困与肮脏中拯救出来——那贫困与肮脏，正是他在特拉斯提弗列一间阁楼里跟两个朋友共度的日子。',
     '①「那笔遗产……，那是……日子」后一「那」指代错位'),

    # ---------------- capitulo019 ----------------
    ('capitulo019',
     '又在扶手的陶盆里重栽蕨草、牛至和秋海棠',
     '又在栏杆上的陶盆里重栽蕨草、牛至和秋海棠',
     '①「扶手的陶盆」不知何指，原文是走廊栏杆上的花盆'),
    ('capitulo019',
     '得到的回答和何塞·阿尔卡蒂奥一样：“凡事皆可知。”',
     '得到的回答和何塞·阿尔卡蒂奥一样：“一切皆知。”',
     '⑤同一句回声（Todo se sabe）全册两译，归一'),
    ('capitulo019',
     '也像接生婆护短似地狂热争辩起来',
     '也像接生婆护自家孩子似的狂热争辩起来',
     '①「护短似地」状语生造，读不出比的是什么'),

    # ---------------- capitulo020 ----------------
    ('capitulo020',
     '但随着奥雷里亚诺渐渐失去希望，她也变得越来越看不见了',
     '但随着奥雷里亚诺渐渐失去希望，她的身影也越来越模糊',
     '③「她变得越来越看不见」是西语 se iba haciendo invisible 直搬，中文读成「她看不见」'),
    ('capitulo020',
     '他读到那个世上最美的女人肉身与灵魂一同升天的诞生被宣告',
     '他读到那个世上最美的女人肉身与灵魂一同升天的宣告',
     '①「升天的诞生被宣告」两层定语套死'),
]

GLOBAL = [
    ('阿尔丰索', '阿方索', '⑤同一人物全册两译（阿方索×3／阿尔丰索×2），归一'),
]

CHAPTERS = [f'capitulo{i:03d}' for i in range(1, 21)]


def main():
    by_chapter = {}
    for ch, old, new, why in EDITS:
        by_chapter.setdefault(ch, []).append((old, new, why))
    total = 0
    for ch in CHAPTERS:
        files = sorted(glob.glob(f'{ROOT}/{ch}/c*/final.txt'))
        texts = {}
        for f in files:
            with open(f, encoding='utf-8', newline='') as fh:
                texts[f] = fh.read()
        before = dict(texts)
        n = 0
        for old, new, why in by_chapter.get(ch, []):
            hits = [f for f, t in texts.items() if old in t]
            cnt = sum(t.count(old) for t in texts.values())
            assert len(hits) == 1 and cnt == 1, f'{ch} 定位失败: {why} | {old!r} n={cnt}'
            f = hits[0]
            texts[f] = texts[f].replace(old, new, 1)
            n += 1
        for old, new, why in GLOBAL:
            for f in texts:
                c = texts[f].count(old)
                if c:
                    texts[f] = texts[f].replace(old, new)
                    n += c
        if n:
            for f, t in texts.items():
                if t == before[f]:
                    continue
                shutil.copyfile(f, f + BAK)
                with open(f, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(t)
            print(f'{ch}: {n} 处')
            total += n
    print('total', total)


main()
ast.parse(open(__file__, encoding='utf-8').read())