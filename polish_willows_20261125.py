# -*- coding: utf-8 -*-
"""《柳林》(willows_a / willows_b) 通读润色 2026-11-25。

原则：只改「读不通 / 的字堆叠 / 外语句法 / 指代 / 专名 / 硬伤 / 体例」七类；
不重译、不加形容词、不把暗示写成明说。定位唯一子串 → 替换 → 断言命中数 == 1。
不 commit、不 push、不改 MEMORY.md、不动 out/*.epub。
"""
import ast
import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent / 'work_batch_20261124'

EDITS = {
    # ── 上册 ─────────────────────────────────────────────────────────────
    'willows_a': [
        # ⑤ 专名：多瑙河（Danube）全册误作「多瑶河」，仅「多瑙艾辛根」写对
        ('多瑶河便进入一片异常孤寂荒凉', '多瑙河便进入一片异常孤寂荒凉'),
        ('多瑶河乐于溜出严峻河岸', '多瑙河乐于溜出严峻河岸'),
        ('但多瑶河比我熟悉的任何河流', '但多瑙河比我熟悉的任何河流'),
        ('连水位都各不相同，多瑶河干脆拒绝认', '连水位都各不相同，多瑙河干脆拒绝认'),
        ('多瑶河被推来搡去，撞在崖壁上', '多瑙河被推来搡去，撞在崖壁上'),
        ('稍有不同，多瑶河变得严肃了些', '稍有不同，多瑙河变得严肃了些'),
        ('多瑶河上出现一条小船', '多瑙河上出现一条小船'),
        ('而多瑶河涨水时没有舵就是自杀', '而多瑙河涨水时没有舵就是自杀'),
        # ⑥ 硬伤：帕绍汇入的是 Inn（因河），不是伊瑟尔河（Iser）
        ('因为伊瑟尔河在那里以雷霆般的力量闯', '因为因河在那里以雷霆般的力量闯'),
        ('但伊瑟尔河给这条老河上了一课', '但因河给这条老河上了一课'),
        # ① 读不通：We were the first human influences upon this island
        ('我们是这岛上第一批人的影响，而我们是不被需要的',
         '我们是这座岛头一拨来打搅的人，而我们是不被需要的'),
        # ① 读不通：to bring him indirectly to a partial confession
        ('想找个话头把他间接引到某程度的部分坦白上去',
         '想找个话头，好歹间接引他作一部分坦白'),
        # ③ 外语句法：the dignity of a westerly gale，两个「风」撞车
        ('够得上西风大风的规模', '够得上一场西风大风的气派'),
        # ① 读不通：两个「地」叠在一处
        ('不间断地成流地往上升', '不间断地汇成一股往上升'),
        # ① 读不通：but what it was they made so much to-do about belonged to…
        ('但它们这样闹腾的究竟是什么，属于它们所居住的那片大平原的秘密生活',
         '但它们这样闹腾的究竟是什么，却属于它们所居住的那片大平原的秘密生活'),
    ],
    # ── 下册 ─────────────────────────────────────────────────────────────
    'willows_b': [
        # ⑤ 专名：同上
        ('多瑶河畔那营地的一片孤寂', '多瑙河畔那营地的一片孤寂'),
        # ③ 外语句法：the withdrawal suddenly of bright sunlight
        ('也真是奇怪，明亮阳光忽然一撤', '也真是奇怪，明亮的阳光忽然一撤'),
        # ① 读不通：dryly → 「干干地」不成词
        ('他干干地答道', '他干巴巴地答道'),
        # ① 读不通：when a stray puff prolonged itself
        ('在一阵游风拖长了、仿佛风又要起来的时候',
         '在一阵游风拖得长长、仿佛又要起风的时候'),
        # ② 的字堆叠 + 同一个「纱」字两次
        ('一层像剧院后台纱幕似的薄纱', '一层仿佛剧院布景纱幕的薄纱'),
        # ③ 外语句法：in a helpless, frantic manner → 「用……样子说」
        ('他用一种无助又狂乱的样子说', '他用一种无助又狂乱的神气说'),
    ],
}


def main():
    total = 0
    for key, pairs in EDITS.items():
        p = BASE / (key + '_zh.json')
        bak = p.with_name(p.name + '.bak_20261125')
        if not bak.exists():
            shutil.copy2(p, bak)
        text = p.read_text(encoding='utf-8', newline='')
        before = json.loads(text)
        n_par = len(before)
        for old, new in pairs:
            hit = text.count(old)
            assert hit == 1, 'not unique: %s -> %r (%d)' % (key, old[:24], hit)
            text = text.replace(old, new)
        data = json.loads(text)
        assert len(data) == n_par, (key, n_par, len(data))
        assert all(isinstance(s, str) and s.strip() for s in data), key
        changed = [i for i, (a, b) in enumerate(zip(before, data)) if a != b]
        assert 0 < len(changed) <= len(pairs), (key, len(changed))
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        total += len(pairs)
        print('%s: %d 处改动（涉及 %d 段）, 段数 %d（改前==改后）'
              % (key, len(pairs), len(changed), n_par))
    print('合计 %d 处' % total)


main()
ast.parse(open(__file__, encoding='utf-8').read())