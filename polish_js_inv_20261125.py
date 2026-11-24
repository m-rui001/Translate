# -*- coding: utf-8 -*-
"""《约翰·塞伦斯医生奇案》第一案《灵异入侵》（A Psychical Invasion）通读润色。"""
import json, ast, io

BASE = 'work_batch_20261124/'
EDITS = [
    # ⑥ 硬伤：错字「专暗」（vast dark countenance）
    ('js_inv_b', 95, '一张庞大专暗的面容的残骸', '一张庞大幽暗的容颜的残骸'),
    # ① 读不通：「邪恶魔蛊惑」掉字，「入怠惰不动」生造
    ('js_inv_b', 98, '它们已被邪恶魔蛊惑入怠惰不动；', '它们早已被邪异地催入死寂的怠惰；'),
    # ① 读不通：「法术之术」叠字
    ('js_inv_c', 11, '一种精于下等法术之术的心智', '一个精于下等法术的心智'),
    # ⑦ 体例：塞伦斯一段长话三段连排，按本书体例段段闭合引号
    ('js_inv_c', 10, '仍能作用于适当准备好了的头脑。', '仍能作用于适当准备好了的头脑。」'),
    ('js_inv_c', 11, '还会继续积聚下去的。', '还会继续积聚下去的。」'),
    # ① 读不通：「药性格外烈」缺字，句尾引号亦缺
    ('js_inv_c', 12, '凑巧是一种药性格外烈的药物促成的。', '凑巧是一味药性格外猛烈的药物促成的。」'),
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