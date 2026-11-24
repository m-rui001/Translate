# -*- coding: utf-8 -*-
"""《约翰·塞伦斯医生奇案》第五案《秘传的崇拜》（Secret Worship）通读润色。"""
import json, ast, io

BASE = 'work_batch_20261124/'
EDITS = [
    # ⑥ 硬伤：「想起到为说英语减半口粮」掉字断句
    ('js_worship', 6, '他微笑着想起到为说英语减半口粮的惩罚',
     '他微笑着想起为说英语而被减半口粮的惩罚'),
    # ① 读不通：「交出了它们的亡魂」直搬 give up their dead，中文读作鬼话
    ('js_worship', 9, '较愉快的那几层记忆交出了它们的亡魂',
     '较愉快的那几层记忆便渐渐褪去了'),
    # ⑥ 硬伤：room-master 误作「宿务」（地名/「宿务」不成义）
    ('js_worship', 89, '酷似他从前的宿务导师帕格尔修士', '酷似他从前的舍监帕格尔修士'),
    ('js_worship', 107, '自然是他从前宿务导师帕格尔的翻版', '自然是他从前那位舍监帕格尔的翻版'),
    # ⑥ 硬伤：错字「写在网上」
    ('js_worship', 97, '钦佩与敬重分明写在网上。', '钦佩与敬重分明写在脸上。'),
    # ⑦ 体例：句末误用问号
    ('js_worship', 113, '宏大，威严，阴沉？它以缓慢的力量',
     '宏大，威严，阴沉。它以缓慢的力量'),
    # ⑥ 硬伤：「您们」非通语
    ('js_worship', 136, '竟给您们带来这么多快乐', '竟给诸位带来这么多快乐'),
    # ⑥ 硬伤：dreadful leer 误作「淫笑」，语域失当
    ('js_worship', 141, '脸上挂着可怕的淫笑', '脸上挂着可怕的狞笑'),
    # ① 读不通：「以礼其慷慨献身」缺动词
    ('js_worship', 163, '「以礼其慷慨献身。」', '「以敬其慷慨献身。」'),
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