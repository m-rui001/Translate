# -*- coding: utf-8 -*-
"""《狗营》补录：① lagoon 全篇统一作「潟湖」（原 dog_d 另用「湖湾」5 处）；
⑦ 分节行字距统一为全书多数的「＊　　＊」。"""
import json, ast, io

BASE = 'work_batch_20261124/'
EDITS = [
    ('js_dog_d', 91, '不久便转过湖湾，不见了。', '不久便转过潟湖，不见了。'),
    ('js_dog_d', 168, '「在湖湾那边，」', '「在潟湖那边，」'),
    ('js_dog_d', 187, '一只独木舟正沿着湖湾的内岸', '一只独木舟正沿着潟湖的内岸'),
    ('js_dog_d', 190, '湖湾对岸也响起一声应答的呼号', '潟湖对岸也响起一声应答的呼号'),
    ('js_dog_d', 191, '他已经跳进独木舟，划到了湖湾中央。', '他已经跳进独木舟，划到了潟湖中央。'),
    ('js_inv_b', 14, '＊\u3000＊\u3000＊\u3000＊\u3000＊', '＊\u3000\u3000＊\u3000\u3000＊\u3000\u3000＊\u3000\u3000＊'),
    ('js_inv_b', 34, '＊\u3000＊\u3000＊\u3000＊\u3000＊', '＊\u3000\u3000＊\u3000\u3000＊\u3000\u3000＊\u3000\u3000＊'),
    ('js_sor_d', 20, '＊\u3000＊\u3000＊\u3000＊\u3000＊', '＊\u3000\u3000＊\u3000\u3000＊\u3000\u3000＊\u3000\u3000＊'),
]

cache = {}
def load(k):
    if k not in cache:
        cache[k] = json.load(io.open(BASE + k + '_zh.json', encoding='utf-8', newline=''))
    return cache[k]

for k, i, old, new in EDITS:
    d = load(k)
    p = d[i]
    assert old in p, (k, i, old)
    assert p.count(old) == 1, (k, i, 'not unique')
    d[i] = p.replace(old, new)

for k, d in cache.items():
    with io.open(BASE + k + '_zh.json', 'w', encoding='utf-8', newline='') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(k, len(d))

ast.parse(open(__file__, encoding='utf-8').read())