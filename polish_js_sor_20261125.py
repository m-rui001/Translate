# -*- coding: utf-8 -*-
"""《约翰·塞伦斯医生奇案》第二案《古老巫术》（Ancient Sorceries）通读润色。"""
import json, ast, io

BASE = 'work_batch_20261124/'
EDITS = [
    # ④ 指代：一句之内「世人」后接「它」，读者会错认主语
    ('js_sor_a', 2, '甚至近乎震惊。它那自满的裁断被粗鲁地搅乱了。',
     '甚至近乎震惊。世人那自满的裁断被粗鲁地搅乱了。'),
    # ⑦ 体例：一段长话分三段排出，段末引号缺失（本书体例逐段闭合）
    ('js_sor_a', 48, '她只是在装作卖东西。', '她只是在装作卖东西。」'),
    ('js_sor_a', 49, '点燃了引线，一路烧到我心头那场大火。',
     '点燃了引线，一路烧到我心头那场大火。」'),
    ('js_sor_a', 52, '一层外表的安恬，遮掩着内在强烈的活动与图谋。',
     '一层外表的安恬，遮掩着内在强烈的活动与图谋。」'),
    # ① 读不通：「宾客同桌饭当前的进度」主谓宾语全乱
    ('js_sor_b', 35, '眼看就要赶上宾客同桌饭当前的进度',
     '眼看就要赶上席上众人的进度'),
    # ⑥ 硬伤：「矮身礼」不成词（curtsey/小屈膝礼）
    ('js_sor_b', 37, '他只觉得她向他道了声极可爱的矮身礼',
     '他只觉得她向他行了极可爱的屈膝礼'),
    # ⑥ 硬伤：人称滑为第三人称（原话是「我」说的）
    ('js_sor_c', 7, '光是知道她也在同一座房子里生活、睡觉，就让他满心异样的欢喜。',
     '光是知道她也在同一座房子里生活、睡觉，就叫我满心异样的欢喜。'),
    # ⑥ 硬伤：Mademoiselle 被误读成人名「梅多」（全篇他处均作「伊尔塞」）
    ('js_sor_c', 12, '与「梅多小姐」的交谈', '与「伊尔塞小姐」的交谈'),
    ('js_sor_c', 17, '尤其是梅多·伊尔塞小姐来了之后。', '尤其是伊尔塞小姐来了之后。'),
    ('js_sor_c', 25, '「梅多·伊尔塞小姐今天要赏光', '「伊尔塞小姐今天要赏光'),
    # ⑥ 硬伤：衍字「地图图」
    ('js_sor_c', 102, '像一张梦中之国的银色地图图。', '像一张梦中之国的银色地图。'),
    # ① 读不通：「挣住自己」不成词
    ('js_sor_c', 112, '维济尼堪堪从那可怕的一跃边缘挣住自己',
     '维济尼堪堪在那可怕的一跃边缘收住自己'),
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