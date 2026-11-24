# -*- coding: utf-8 -*-
"""《百年孤独》通读润色 第6批（capitulo014-016）＋两项全册专名归一。"""
import ast
import glob
import shutil

ROOT = 'E:/Translate/work_soledad/out'
BAK = '.bak_20261125'

EDITS = [
    # ---------------- capitulo016 ----------------
    ('capitulo016',
     '结果乌尔苏拉便合情合理地断定，这毛病不在子宫，而在肠子，于是劝她空腹服一纸包甘汞。',
     '结果乌尔苏拉便合情合理地断定，这毛病不在子宫，而在肠子，劝她空腹服一纸包甘汞。',
     '①「结果……于是」一句里把因果讲了两遍'),
    ('capitulo016',
     '费尔南达看他那样干活——那是从未听说过他能这么干的——便以为他的鲁莽是勤勉',
     '费尔南达看他那样干活——那是谁也不曾听说他能干的活——便以为他的鲁莽是勤勉',
     '①「那是从未听说过他能这么干的」主语虚悬，补出「活」才立得住'),
]

# 全册专名归一（出现次数多者为 canon）
GLOBAL = [
    ('隐形医生', '看不见的医生', '⑤同指一事全册两译（看不见的医生×10／隐形医生×4），归一'),
    ('雅各布', '雅各', '⑤Hotel de Jacob 全册两译（雅各×6／雅各布×3），归一'),
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