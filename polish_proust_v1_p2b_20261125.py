# -*- coding: utf-8 -*-
"""《追忆似水年华》第一卷 chunk016-020 通读润色 p2b（2026-11-25 轮）

只做「定位唯一子串 -> 替换 -> 断言命中数」的改法，不整文件重写。
行数/段数不变；已有 .bak_20261125 的不覆写。
"""
import io
import os
import shutil

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    'work_proust', 'out_ind', 'v1')

# (chunk, old, new, 类别, 理由)
EDITS = [
    # ---- chunk016 ----
    ('chunk016', '如此不同——，弗朗索瓦丝见', '如此不同——弗朗索瓦丝见', '⑦',
     '破折号后紧跟逗号，体例不合'),
    ('chunk016', '她从不曾对我有过任何动情', '她一向从不在我面前动感情', '⑥',
     'qui jamais ne se laissait aller à aucun attendrissement avec moi：attendrissement 指「动感情」，「对我动情」误作男女之情'),
    ('chunk016', '忽然被我的动情所感染', '忽然被我的感情感染', '③',
     'être gagnée par le mien 硬搬成「被……所感染」的被动式，且「动情」同上须改'),
    ('chunk016', '别让她这样劳累——，只得', '别让她这样劳累——只得', '⑦',
     '破折号后紧跟逗号，体例不合'),
    # ---- chunk018 ----
    ('chunk018', '——那些手法是《弗朗索瓦·勒尚皮》', '——而是《弗朗索瓦·勒尚皮》', '①',
     '原文 me paraissaient simples — à moi qui... — une émanation：插入语之后应接谓语「而是……」，译文另起「那些手法是」造成主语重复、句子断裂'),
    ('chunk018', '他是我忧伤的无意识的造成者', '他无意中造成我的忧伤', '③',
     'l’auteur inconscient de mes tristesses 逐字直搬，「……的造成者」中文不成话'),
    # ---- chunk020 ----
    ('chunk020', '也包括那枚糕点的小贝壳', '也包括那块小贝壳形的糕点', '⑥',
     'ce petit coquillage de pâtisserie 指做成小贝壳形状的糕点，译文误作「糕点的小贝壳」'),
]

def main():
    touched = {}
    for chunk, old, new, kind, why in EDITS:
        path = os.path.join(BASE, chunk, 'final.txt')
        text = io.open(path, encoding='utf-8', newline='').read()
        assert old in text and text.count(old) == 1, (chunk, old)
        bak = path + '.bak_20261125'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        raw = io.open(path, encoding='utf-8', newline='').read()
        assert len(raw.splitlines()) == len(raw.replace(old, new).splitlines()), chunk
        io.open(path, 'w', encoding='utf-8', newline='').write(raw.replace(old, new))
        touched.setdefault(chunk, []).append((kind, why))
    for chunk in sorted(touched):
        print(chunk, len(touched[chunk]))

if __name__ == '__main__':
    main()
    import ast
    ast.parse(io.open(__file__, encoding='utf-8').read())