# -*- coding: utf-8 -*-
"""bm_b 逐段润色落盘脚本（2026-11-26）。

铁律：只「定位唯一子串 → 替换 → assert」，数组长度/顺序不变，indent=1 + LF 原样写回。
"""
import ast
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
ZH = os.path.join(BASE, 'bm_b_zh.json')
SRC = os.path.join(BASE, '_bm_b_paras.json')
BAK = ZH + '.bak_20261126'

# (段号, 旧子串, 新子串, 类别, 理由)
EDITS = [
    (3, '他还需要女人的一双巧手。', '他还需要女人的一份体贴。',
     '⑥硬伤', 'a woman\'s touch＝女人的细腻体贴，非「一双巧手」；词义误读。'),

    (5, '必定有价值，甚至可能具有启发，直至令人恍然。', '必定有价值，甚至可能极有启发，乃至近于启示。',
     '①读不通', '「具有启发，直至令人恍然」缺宾语且「直至」译 to the point of 太实；改为「极有启发，乃至近于启示」。'),

    (17, '梅森的水彩速写', '梅森的水彩写生',
     '⑥硬伤', 'water-colour sketch＝水彩写生／画稿；「速写」指炭笔速写一类，与水彩不搭。'),

    (24, '他抬起头，仿佛要追寻这突然新生的、明亮、迅捷、高效——几乎像是某种以一贯计划与体系建造起来的巨大力量——的意识；',
     '他抬起头，仿佛要追寻这突然生出的一种意识：明亮、迅捷、高效，几乎像是某种以一贯计划与体系建造起来的巨大力量；',
     '②的字堆叠', '「这突然新生的……的意识」跨破折号定语把中心语压到句末，读者要回读；中心语提前，破折号改冒号。'),

    (36, '另一个则是那台死机器非个人的、准确的胜任。', '另一个则是那台死机器非个人的、精准的效能。',
     '③外语句法', 'competence 作名词直搬成「胜任」不成话；改「效能」。'),

    (50, '他现在比我们三天前出发时还不累', '他现在反倒比三天前我们出发时还不觉得累',
     '⑥硬伤', '「比……还不累」否定套比较读不顺，加「反倒」「觉得」理顺。'),

    (52, '大概是父母，但被梅森刺激、任由其不受约束地生长。',
     '大概是父母，不过梅森又加以刺激，任其不受约束地生长。',
     '③外语句法', '被动式 hard-moved：一句里「被梅森刺激」与「任由其……」主语不一致。'),

    (76, '他只盖了一条床单，盖着那高大、温暖、柔韧的身体。', '他只拿一条床单盖住那高大、温暖、柔韧的身体。',
     '①读不通', '一句里两个「盖」，后半句谓语重复且悬空。'),

    (80, '他为潜意识自我的力量划下严厉的界限', '他为潜意识自我的力量划下严格的界限',
     '⑥硬伤', 'set drastic limits 是「严格／峻厉的界限」，「严厉」多用于人的态度。'),

    (115, '「我一点也不觉得挖苦。', '「我一点也不觉得自己在挖苦。',
     '⑥硬伤', 'I feel far from cynical＝我并不觉得自己在挖苦（回应上句「别挖苦」）；原译成了「不觉得被挖苦」。'),

    (122, '菲利里敏捷地表示赞赏。', '菲利里当即表示赞赏。',
     '③外语句法', 'with quick appreciation 的 quick 是「立刻」，非「敏捷地」。'),

    (152, '根本不可能睡过。', '根本不可能睡过觉。',
     '①读不通', '「睡过」缺宾语，孤零零像口语省略。'),

    (161, '他告诉那人，那是星象和天气图', '莱斯特便说，那是星象和天气图',
     '④指代不明', '前句主语已是「那官员」，此「他」实指莱斯特，一名两人易混。'),

    (161, '可在那种时候，这样一些纸片藏在箱底，样子又怪，而且',
     '可这样一些纸片，样子又怪，又偏在那种时候藏在箱底，而且',
     '①读不通', '「在那种时候……藏在箱底」把时间状语顶了话题位，句子读来断裂。'),

    (179, '他开口说：『我父亲也有，』他带着钦佩说，『一架大望远镜。这位先生是位天文学家。』」',
     '他开口说：『我父亲也有，』」他带着钦佩地说，「『一架大望远镜。这位先生是位天文学家。』」',
     '⑦体例', '说话人标签塞在引号内；按本篇 1、7 段既定体例，收引号—标签—开引号。'),

    (180, '「『是最伟大的之一，』我赶紧补了一句；『这些图对法国有无穷的价值。』我丝毫',
     '「『是最伟大的之一，』」我赶紧补了一句，「『这些图对法国有无穷的价值。』我丝毫',
     '⑦体例', '同上，说话人标签（我赶紧补了一句）不应裹在引号内。'),
]


def main():
    raw = open(ZH, 'rb').read()
    crlf = b'\r\n' in raw
    d = json.loads(raw.decode('utf-8'))
    bak = json.loads(open(BAK, 'rb').read().decode('utf-8'))
    n_before = len(d)
    assert len(d) == len(bak) == n_before, '数组长度与备份不同'

    stat = {}
    for idx, old, new, cat, why in EDITS:
        assert old in d[idx], 'miss [%d]: %r' % (idx, old[:30])
        assert d[idx].count(old) == 1, 'not unique [%d]: %r' % (idx, old[:30])
        d[idx] = d[idx].replace(old, new)
        assert new in d[idx]
        stat[cat] = stat.get(cat, 0) + 1

    out = json.dumps(d, ensure_ascii=False, indent=1)
    eol = '\r\n' if crlf else '\n'   # 原文件 LF，末尾带一个换行
    with open(ZH, 'w', encoding='utf-8', newline='') as f:
        f.write(out + eol)

    # ---- 自检 ----
    d2 = json.load(open(ZH, encoding='utf-8'))
    src = json.load(open(SRC, encoding='utf-8'))
    han = sum(1 for x in d2 for ch in x if '\u4e00' <= ch <= '\u9fff')
    print('paras %d (bak %d) src %d  han %d' % (len(d2), len(bak), len(src), han))
    assert len(d2) == len(bak), '长度变了'
    assert all(x.strip() for x in d2), '有空段'
    assert not any('"' in x or "'" in x for x in d2), '有 ASCII 引号'
    assert not any(re.search(r'(。。|，，|、、|；；|！！|？？)', x) for x in d2), '重复标点'
    assert not any(re.search(r'[\u4e00-\u9fff] [a-zA-Z]|[a-zA-Z] [\u4e00-\u9fff]', x) for x in d2), '残英文空格'
    assert not any('⟦' in x for x in d2), '有 ⟦⟧'
    bad = [i for i, x in enumerate(d2) if x.count('「') != x.count('」') or x.count('『') != x.count('』')]
    assert not bad, '引号不配对 %r' % bad
    newline = 'CRLF' if crlf else 'LF'
    print('改动 %d 条  %s' % (len(EDITS), ' / '.join('%s x%d' % (k, v) for k, v in sorted(stat.items()))))
    print('自检 ok：长度不变 无空段 无 ASCII 引号 无重复标点 无残英文 引号成对 换行=%s' % newline)


main()
ast.parse(open(__file__, encoding='utf-8').read())