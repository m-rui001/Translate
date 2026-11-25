# -*- coding: utf-8 -*-
"""cent_d 逐段润色（2026-11-26，第二轮通读：只动残留 12 处）。

对齐：zh[i] <-> src[i + off]，off 随章号段（XVIII…XXII）被丢弃而阶跃
      阶梯点 zh[17]→2、zh[42]→3、zh[62]→4、zh[82]→5、zh[93]→6（同 _align_cd_20261126.py）。

改法：只改元素值；数组长度/顺序/`\\n` 不变；定位唯一子串 → 替换 → 断言命中 1 次。
用法：python _polish_20261126_cent_d.py [--dry]
"""
import ast
import io
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
KEY = 'cent_d'

# (zh 索引, 旧子串, 新子串, 类别, 英文原文)
EDITS = [
    (0, '他为这个想法举出的若干理由，施塔尔都讲了；',
        '他为这个想法举出的若干理由，奥马利讲了一些；', '⑥',
        'Some of Fechner\'s reasons for thinking the Earth a being superior in the scale to ourselves, he gave'),
    (19, '搜寻希腊的第一眼',
         '盼着第一眼望见希腊', '①',
         'the tourists turned their glasses eastwards, searching for a first sight of Greece'),
    (22, '再加上手势、面部表情和——沉默的转释',
         '还要靠手势、面部表情，以及——沉默——来转释', '①',
         'interpreted too by gesture, facial expression, and--silence'),
    (46, '这条伸向星辰、风与大地的那片更宽广意识的边缘',
         '这条向星辰、风与大地伸展出去的更宽广意识的边缘', '①',
         'this fringe of wider consciousness, stretching to the stars and winds and earth'),
    (52, '全都清一色地玫瑰红，活生生的',
         '全都泛着精致的玫瑰红，活生生的', '①',
         'treeless peaks and shoulders ... all exquisitely rosy and alive'),
    (61, '他看着他那蹒跚的身影消失在楼梯下面',
         '他看着施塔尔那蹒跚的身影消失在楼梯下面', '④',
         'he watched his shambling figure disappear down the stairway'),
    (62, '他都必须全副用心',
         '他都必须倾注全副心力', '①',
         'To everything that a man does he must give his undivided attention'),
    (75, '仿佛她那胸上所有森林之上，长长的甜风都去低语他的名字',
         '仿佛她胸上所有森林之间，长长的甜风都在低语他的名字', '①',
         'as though across all the forests on her breast the long sweet winds went whispering his name'),
    (78, '两岸的岸线都离得很近',
         '两边的岸线都离得很近', '①',
         'The line of the shore lay close on either side'),
    (93, '他讲得激情而半带混乱',
         '他讲得激昂而半带混乱', '①',
         'What followed he relates with passion, half confused'),
    (102, '这桩事的一角从彼外渗了过来',
          '这桩事的一角从更远处渗了过来', '①',
          'A broken piece of the occurrence filtered through from beyond'),
    (104, '随一股声的风胀起，把那一片片天空、海与星辰都吸着同来',
          '随一股声流胀起，把整片整片的天空、海与星辰都一同吸了过来', '①',
          'swelling with a draught of sound that sucked whole spaces of sky and sea and stars with it'),
]


def run(dry=False):
    zh_path = os.path.join(BASE, KEY + '_zh.json')
    bak_path = zh_path + '.bak_20261126_cent_d'
    if not os.path.exists(bak_path):
        bak_path = zh_path + '.bak_20261126'

    raw = io.open(zh_path, encoding='utf-8', newline='').read()
    bak_raw = io.open(bak_path, encoding='utf-8', newline='').read()
    crlf_before = raw.count('\r\n')
    d = json.loads(raw)
    b = json.loads(bak_raw)
    assert len(d) == len(b) == 132, '段数不是 132'
    n0 = len(d)

    for idx, old, new, cat, _en in EDITS:
        whole = json.dumps(d, ensure_ascii=False)
        assert whole.count(old) == 1, '全册不唯一: %r (%d)' % (old, whole.count(old))
        assert old in d[idx], '第 %d 段里没有该子串: %r' % (idx, old)
        d[idx] = d[idx].replace(old, new, 1)
        print('[%s] zh[%d]\n     - %s\n     + %s' % (cat, idx, old, new))

    out = json.dumps(d, ensure_ascii=False, indent=1)
    if crlf_before:
        out = out.replace('\n', '\r\n')
    if not dry:
        io.open(zh_path, 'w', encoding='utf-8', newline='').write(out)

    # ---------------- 自检 ----------------
    d2 = json.loads(io.open(zh_path, encoding='utf-8', newline='').read()) if not dry else d
    raw2 = io.open(zh_path, encoding='utf-8', newline='').read() if not dry else out
    assert len(d2) == n0 == len(b), '段数变了'
    assert all(x.strip() for x in d2), '有空段'
    t = ''.join(d2)
    assert '"' not in t, '有 ASCII 直引号'
    assert "'" not in t, '有 ASCII 单引号'
    for bad in ('。。', '，，', '；；', '：：', '、、', '——。', '；——', '：——'):
        assert bad not in t, '重复/叠加标点 %s' % bad
    assert t.count('「') == t.count('」'), '引号不成对'
    assert t.count('『') == t.count('』'), '嵌套引号不成对'
    assert not any(ch in t for ch in '⟦⟧'), '有 ⟦⟧ 残留'
    # 汉字＋空格＋小写英文＋空格＋汉字（专名/引文除外：本篇无）
    import re
    m = re.search(r'[\u4e00-\u9fff] [a-z]+ [\u4e00-\u9fff]', t)
    assert m is None, '残留英文: %r' % (m and m.group(0))
    # 段末标点（两处星号分隔行 zh[55]/zh[124] 豁免）
    tail = '。！？…—」』：、；＊*'
    for i, x in enumerate(d2):
        if i in (55, 124):
            continue
        assert x.rstrip()[-1] in tail, '段 %d 段末无标点: %r' % (i, x[-12:])
    han = sum(1 for c in t if '\u4e00' <= c <= '\u9fff')
    crlf = raw2.count('\r\n')
    diff = [i for i in range(n0) if d2[i] != b[i]]
    print('---')
    print('%s: 段数 %d（改前 %d） 改动 %d 条 汉字 %d CRLF %d 行'
          % (KEY, len(d2), len(b), len(EDITS), han, crlf))
    print('与备份(%.0f)不同的段: %s' % (len(b), diff))
    print('自检: JSON 可解析 ✓ 段数/段序不变 ✓ 无空段 ✓ 无 ASCII 引号 ✓ '
          '「」『』成对 ✓ 无重复标点 ✓ 无残留英文 ✓ 段末标点齐全 ✓ 无 ⟦⟧ ✓')
    return 0


if __name__ == '__main__':
    run(dry='--dry' in sys.argv)
    ast.parse(open(__file__, encoding='utf-8').read())
    print('ast.parse ✓')