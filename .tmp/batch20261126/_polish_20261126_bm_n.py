# -*- coding: utf-8 -*-
"""bm_n 逐段润色（2026-11-26）。只改元素值，不动数组长度与顺序。
落盘体例：indent=1, ensure_ascii=False, LF（照原文件）。
"""
import ast
import json
import os
import shutil

PATH = 'bm_n_zh.json'
BAK = 'bm_n_zh.json.bak_20261126'
N = 148

# (段号, 旧子串, 新子串, 类别, 理由, 原文)
EDITS = [
    (4,
     '只有小鸟在雏菊间可见。',
     '雏菊之间只看得见小鸟。',
     '①', 'Only the birds were visible among the daisies 的语序直搬，「在……间可见」中文不成句。',
     'Only the birds were visible among the daisies.'),
    (15,
     '菲利里被一种他既不能界定也不能控制的情感所震颤，把他领到窗前。',
     '菲利里被一种他既不能界定也不能控制的情感搅得浑身发颤，把「N. H.」领到窗前。',
     '①', '前句已用被动，后半句「把他」的施动者悬空，读者会误以为被领的是那个「他」。',
     'Trembling with emotions he could neither define nor control, Fillery led him to the window.'),
    (19,
     '一件新的载体',
     '一件新的载具',
     '⑤', 'bml/bmm 一律作「载具」（vehicle），本册术语须归一。',
     'a new vehicle, through which your powers can express themselves'),
    (28,
     '「保罗，」主任很快地说',
     '「保罗，」上司很快地说',
     '⑤', 'the chief（指菲利里）在同一篇里「主任」「上司」两译并用，平票取通行者「上司」。',
     '"Paul," said the chief quickly'),
    (52,
     '仍旧坚硬僵硬地在你里面',
     '仍旧在你里面又硬又僵',
     '①', '「坚硬僵硬地」两个同义形容词叠成状语，读来打结。',
     'your complex against humanity lies hard and rigid in you still'),
    (55,
     '新的生命载体',
     '新的生命载具',
     '⑤', '同上，vehicle 统一作「载具」。',
     'new vehicles for life, for God, to manifest through'),
    (65,
     '主任喃喃地说',
     '上司喃喃地说',
     '⑤', '同段 28，the chief 归一作「上司」。',
     '"Bless you, old fellow," murmured the chief.'),
    (68,
     '驾御着生活的不确定',
     '驾驭着生活的不确定',
     '⑥', '「驾御」为「驾驭」的错写。',
     'dominating the uncertainties of life with calm, steady power.'),
    (74,
     '可他庆慰自己',
     '可他暗自宽慰自己',
     '⑥', '「庆慰」不成词（he flattered himself＝自我宽慰）。',
     'his normal, earthly faculties, he flattered himself, were in no sense permanently disorganized'),
    (74,
     '德文汉姆那明智、控制性的一触的魔力，仿佛在每一个细节里',
     '德文汉姆那明智的、善于掌控的一触，其魔力仿佛在每一个细节里',
     '②', '「明智、控制性的一触的魔力」三个「的」串成一条定语，中心语被压没。',
     'The magic of Devonham\'s wise, controlling touch lay in every detail, it seemed....'),
    (107,
     '他无法自己。',
     '他也没有办法。',
     '①', 'He cannot help himself 直搬，「他无法自己」缺谓语落点。',
     'He cannot help himself.'),
    (117,
     '接着来了些仿佛引向他等待的那句作为信号的他偏爱的话的东西——无论如何，更接近它了：',
     '接着来了些话，仿佛正引向他所等待的那句信号般的话——他偏爱的那句——无论如何，离它更近了：',
     '②', '一句里四个「的」层层嵌套（引向…的…作为信号的他偏爱的话的东西），中心语读不出。',
     'Then came something that seemed leading up to the pet sentence that was the signal he waited for--nearer to it, at any rate:'),
]


def main():
    if not os.path.exists(BAK):
        shutil.copyfile(PATH, BAK)

    with open(PATH, encoding='utf-8', newline='') as f:
        d = json.load(f)
    with open(BAK, encoding='utf-8', newline='') as f:
        d0 = json.load(f)
    assert len(d) == len(d0) == N, (len(d), len(d0))

    n, skipped = 0, 0
    for idx, old, new, cat, why, src in EDITS:
        if new in d[idx] and old not in d[idx]:
            skipped += 1
            continue
        assert old in d[idx], (idx, old)
        assert d[idx].count(old) == 1, (idx, old)
        d[idx] = d[idx].replace(old, new)
        n += 1

    import re
    for i, t in enumerate(d):
        assert t.strip(), ('empty', i)
        assert '\r' not in t, ('CR', i)
        for bad in ('"', "'"):
            assert bad not in t, ('ascii quote', i, bad)
        for bad in ('。。', '，，', '、、', '；；', '！！', '？？', '：：'):
            assert bad not in t, ('dup punct', i, bad)
        assert t.count('「') == t.count('」'), ('quote', i)
        assert t.count('『') == t.count('』'), ('nested quote', i)
        assert i in (78, 91, 94) or t.rstrip()[-1] in '。！？…：—」』）', ('end punct', i, t.rstrip()[-6:])
        assert not re.search(r'[\u4e00-\u9fff] [a-z]{2,} [\u4e00-\u9fff]', t), ('latin residue', i)

    with open(PATH, 'w', encoding='utf-8', newline='') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write('\n')

    with open(PATH, encoding='utf-8', newline='') as f:
        d2 = json.load(f)
    assert len(d2) == N and d2 == d
    han = sum(1 for t in d2 for ch in t if '\u4e00' <= ch <= '\u9fff')

    print('本次落盘改动条数:', n, '（已改跳过:', skipped, '）')
    print('数组长度: %d（备份 %d）OK' % (len(d2), len(d0)))
    print('汉字数:', han)
    print('JSON 可解析: OK；无空段: OK；无 ASCII 引号: OK；无重复标点: OK；无拉丁残留: OK；引号成对: OK；段末标点: OK（78/91/94 为星号行，豁免）')


if __name__ == '__main__':
    main()
    ast.parse(open(__file__, encoding='utf-8').read())
    print('ast self-check: OK')