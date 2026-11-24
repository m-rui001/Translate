# -*- coding: utf-8 -*-
"""《追忆似水年华》第一卷 chunk031-035 通读润色 p2e（2026-11-25 轮）

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
    # ---- chunk032 ----
    ('chunk032', '怕得跟她说话', '怕要跟她说话', '①',
     '«n’osant pas trop tourner les yeux de son côté de peur d’avoir à lui parler»：de peur d’avoir à 是「怕要」，原译「怕得」读成「怕得（不敢）」或「吓得」，意反'),
    ('chunk032', '就能替我免掉了。', '就能替我免去这一番。', '①',
     '«mon oncle aurait pu en dispenser un gamin comme moi»：en 指那番白守门前的工夫；原译「免掉了」缺宾语，句子断在半空'),
    # ---- chunk033 ----
    ('chunk033', '给它一转，给它一个珍贵的名目', '给它一个转法、一个珍贵的名目', '③',
     '«lui avait donné un tour, une appellation précieuse»：「给它一转」是 give it a turn 的字面照搬，中文不成话；两个并列宾语也不必重复「给它」'),
    # ---- chunk034 ----
    ('chunk034', '厨娘是一个法人般的存在', '厨娘是一种抽象人格般的存在', '⑥',
     '«la fille de cuisine était une personne morale»：personne morale 指「人格、道德实体」，不是法律上的「法人」；下句「一个常设的机构」正是在解释这层抽象'),
    ('chunk034', '我想问题人和大家一样，以为', '我像大家一样以为', '⑥',
     '«Je m’imaginais, comme tout le monde, que…»：「问题人」不成词，显系「像大家」一路的错简，句子主语与谓语都不通'),
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