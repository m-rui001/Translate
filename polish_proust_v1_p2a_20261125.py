# -*- coding: utf-8 -*-
"""《追忆似水年华》第一卷 chunk011-015 通读润色 p2a（2026-11-25 轮）

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
    # ---- chunk011 ----
    ('chunk011', '或者像一句莫里哀的诗句', '或者被感知为一句莫里哀的诗句', '①',
     '「被我们感知为一个……小姑娘，或者像一句……」并列项失配，补出被感知，使两项平行'),
    ('chunk011', '把牙痛这个念头身上一切', '把牙痛这个念头的一切', '①',
     '「这个念头身上」搭配不成立（直搬 de l’idée de rage de dents），删去「身上」'),
    ('chunk011', '至少让我看不见地、满心欢喜地', '至少让我神不知鬼不觉地、满心欢喜地', '③',
     'entrer invisible 直搬成「看不见地」，中文不成话，改作「神不知鬼不觉地」'),
    # ---- chunk012 ----
    ('chunk012', '她要去品尝那些未知欢乐的、我们进不去的折磨人的时刻',
     '那些她要去品尝未知欢乐、而我们进不去的折磨人的时刻', '②',
     '三个「的」串在中心语前，且「未知欢乐的」与「折磨人的」同挂「时刻」易读错，改为两个并列谓语'),
    ('chunk012', '几乎变得成全我们了', '几乎变得对我们有利了', '①',
     'presque propice 译作「变得成全我们」动词宾语不成立'),
    # ---- chunk015 ----
    ('chunk015', '她须与以撒那边分开', '她得跟以撒分开', '①',
     'se départir du côté d’Isaac 直搬作「与……那边分开」，动宾不搭；「须」亦生硬'),
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
        nl = '\r\n' if '\r\n' in raw else '\n'
        assert len(raw.splitlines()) == len(raw.replace(old, new).splitlines()), chunk
        io.open(path, 'w', encoding='utf-8', newline='').write(raw.replace(old, new))
        touched.setdefault(chunk, []).append((kind, why))
    for chunk in sorted(touched):
        print(chunk, len(touched[chunk]))

if __name__ == '__main__':
    main()
    ast_self = __file__
    import ast
    ast.parse(io.open(ast_self, encoding='utf-8').read())