# -*- coding: utf-8 -*-
"""cent_g 逐段润色（2026-11-26）。定位唯一子串 → 替换 → 断言命中数。"""
import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZH = os.path.join(HERE, 'cent_g_zh.json')
SRC = os.path.join(HERE, '_cent_g_paras.json')

# (zh 索引, 类别, 旧句, 新句)
EDITS = [
    # ① —— 悬空修饰语 / 抽象名词主语照搬
    (6, '①', '他四周摊着这整片开满花的、巨大而安静的高加索的存在，在闲暇里啜饮阳光。',
     '他四周摊着这整片开满花的高加索存在，巨大而安静，正闲暇地啜饮着阳光。'),
    # ① —— satisfy 误作「满足…满足」，同义反复
    (12, '①', '他没法满足，因为他不能满足。', '他没有回答，因为他答不上来。'),
    # ① —— 「微弱下去」接在「沉醉」后，动作主语失据
    (29, '①', '因锐利的欢乐而沉醉，微弱下去', '因锐利的欢乐而沉醉，渐渐低微下去'),
    # ① —— quicken to the view 误作「我活了起来」
    (33, '①', '以某种精神的方式，我活了起来，看清了', '在某种精神的方式上，我心中豁然一亮，看清了'),
    # ① —— untrue 直搬成「不真的」
    (39, '①', '它们是——不真的；', '它们是——假的；'),
    # ① —— chamber after chamber 的「室」不成词
    (45, '①', '它注满一间又一间室，', '它注满一间又一间屋子，'),
    # ① —— 抽象名词主语照搬，缺主谓
    (46, '①', '大地的种种性质也同样，如此轻易地，都装在他自己之内。',
     '大地的种种性质同样也在他自己之内，如此轻易地就容纳下了。'),
    # ① —— half breaking 直搬
    (54, '①', '某种类似的、上涌的欢喜也在我胸中半破开来', '某种相似的欢喜也在我胸中涌起，隐隐要破裂开来'),
    # ① —— 口语句「这总算点什么」
    (54, '①', '「这总算点什么——」', '「这总算一点什么——」'),
    # ① —— 「在它们巨人的美里永恒」谓语失据
    (66, '①', '在它们巨人的美里永恒。', '在它们那巨人的美中长存不朽。'),
    # ① —— 手势一项无谓语，悬在句首
    (92, '①', '接着又一声吼，一个既巨大又单纯的手势，他似乎立起来',
     '接着又一声吼，又做一个既巨大又单纯的手势，他似乎立起来'),
    # ① —— 「留在身后」与「留在别处」撞车
    (112, '①', '视觉毕竟只是一种不完整的认知形式——一样他已经留在身后的东西——留在别处了。',
     '视觉毕竟只是一种不完整的认知形式——一样他早已丢在身后、丢在别处的东西。'),
    # ① —— 形容词化的 tragedy
    (136, '①', '骄傲、强健而悲剧。', '骄傲、强健而悲怆。'),

    # ② —— 「的」字定语堆叠
    (28, '②', '我没法假装有超过一种模糊的同情的理解。',
     '我没法假装自己懂得更多，至多只是一种模糊而同情的领会。'),
    (30, '②', '它徒然搏动着，抵着文明铺下的伦敦砖石路面的窒息重压',
     '它徒然搏动着，顶着文明铺下的伦敦砖石路面那令人窒息的重压'),
    (61, '②', '空气因一片流动的色调的雾而变得灿烂。', '空气透过一片流动变幻的色雾，变得灿烂。'),
    (101, '②', '它以惊人的活力和深厚的信念之丰盈从他唇间倾出。',
     '它带着惊人的活力与丰盈深厚的信念，从他唇间倾出。'),
    (114, '②', '一阵风一般的力量的吼声充满了天空', '一片挟着风一般巨力的吼声充满了天空'),
    (133, '②', '无论他是否记得这些从已被抛在身后的外在世界来的、结巴却意味深长的话，它们所影射的真理升起来，把他接住了',
     '这些话结巴却意味深长，来自已被抛在身后的外在世界。无论他是否记得，它们所影射的真理都升起来，把他接住了'),

    # ③ —— 外语句法直搬（冠词式语序 / 抽象存在）
    (22, '③', '「不算坏的一个词，」他笑了；「当然，就其所及而言，也不算错的一个。',
     '「这词不算坏，」他笑了；「当然，就它所能及的而言，也算不上错。'),

    # ④ —— 代词／数量指代不明
    (69, '④', '与几个只比他略低的峰一起', '与几座只比它略低的峰一起'),
    (93, '④', '——对方脚下的声音已经融进那另一种更广大的踏地声里',
     '——那蹄声已经融进另一种更广大的踏地声里'),
    (143, '④', '它们那双大褐眼总欢喜地寻找他的眼睛。', '它们那两双大褐眼总欢喜地寻找他的眼睛。'),

    # ⑥ —— 硬伤：masquerading 主语读反
    (44, '⑥', '把它们的假象当作完整的化身摆在生命的边缘，而其实它们只是背后那些永恒原型的不完整的、象征性的表现',
     '看它们在生命的边缘冒充完整的化身，其实只是背后那些永恒原型的局部而象征性的表现'),
    # ⑥ —— years and minutes 误作「年年月月、分分秒秒」
    (52, '⑥', '还是年年月月、分分秒秒？——', '还是几年与几分钟？——'),
    # ⑥ —— withdrawn 被动读成主动
    (66, '⑥', '从未完全收回。', '从未被完全收回。'),
    # ⑥ —— silvery 误作「银灰色」
    (70, '⑥', '用她那银灰色的建筑群', '用她那银色的建筑群'),
    # ⑥ —— Forbidden thy Father to see 否定方向读反
    (78, '⑥', '却不许你的父被看见——', '却不许你的父看见——'),
    # ⑥ —— peak and dwindle 误作「憔悴萎缩」
    (98, '⑥', '「在这里我们只是憔悴萎缩，', '「在这里我们只是登顶又衰微，'),
    # ⑥ —— belittle 误作「贬小」
    (104, '⑥', '因为这些会限制、囚禁、贬小', '因为这些会限制、囚禁、贬低'),
]

BAK = ZH + '.bak_20261126'


def main():
    raw = open(ZH, 'rb').read().decode('utf-8')
    d = json.loads(raw)
    bak = json.loads(open(BAK, 'rb').read().decode('utf-8'))
    src = json.loads(open(SRC, 'rb').read().decode('utf-8'))
    n_before = len(d)

    applied = []
    for idx, cat, old, new in EDITS:
        txt = d[idx]
        assert old in txt, 'MISS zh[%d]: %r' % (idx, old[:40])
        assert txt.count(old) == 1, 'NOT UNIQUE zh[%d]: %r' % (idx, old[:40])
        d[idx] = txt.replace(old, new)
        applied.append((idx, cat, old, new))

    # 落盘沿用原 indent=2 / CRLF
    out = json.dumps(d, ensure_ascii=False, indent=2)
    with open(ZH, 'w', encoding='utf-8', newline='') as f:
        f.write(out.replace('\n', '\r\n'))

    # ---- 自检 ----
    d2 = json.loads(open(ZH, 'rb').read().decode('utf-8'))
    assert len(d2) == n_before == len(bak), 'len mismatch'
    assert all(x.strip() for x in d2), 'empty para'
    assert all('\n' not in x or True for x in d2)
    for i, x in enumerate(d2):
        assert '"' not in x, 'ASCII quote in zh[%d]' % i
        assert not re.search(r'[。，、；：]{2,}', x.replace('……', '')), 'dup punct zh[%d]' % i
        assert '⟦' not in x and '⟧' not in x
        for m in re.finditer(r'[\u4e00-\u9fff] [A-Za-z]{2,} [\u4e00-\u9fff]', x):
            raise AssertionError('残留英文 zh[%d]: %s' % (i, m.group(0)))
    # 段落换行（诗行）数量不变
    for i in range(n_before):
        assert bak[i].count('\n') == d2[i].count('\n'), 'line count changed zh[%d]' % i

    print('篇: cent_g')
    print('段数: %d -> %d ✓' % (n_before, len(d2)))
    print('汉字: %d' % sum(len(re.findall(r'[\u4e00-\u9fff]', x)) for x in d2))
    print('改动: %d 条（涉及 %d 段）' % (len(applied), len({a[0] for a in applied})))
    from collections import Counter
    c = Counter(a[1] for a in applied)
    print('分类: ' + ' '.join('%s×%d' % (k, c[k]) for k in sorted(c)))
    print('换行符: CRLF')
    print('自检: JSON ✓ 长度 ✓ 无空段 ✓ 无 ASCII 引号 ✓ 无重复标点 ✓ 无 ⟦⟧ ✓ 诗行数不变 ✓')
    return applied


if __name__ == '__main__':
    ap = main()
    src_paras = json.loads(open(SRC, 'rb').read().decode('utf-8'))
    with open(os.path.join(HERE, '_polish_20261126_cent_g_out.txt'), 'w', encoding='utf-8') as f:
        for idx, cat, old, new in ap:
            f.write('[zh %d][%s]\nOLD: %s\nNEW: %s\n\n' % (idx, cat, old, new))
    sys.stdout.flush()

ast.parse(open(__file__, encoding='utf-8').read())