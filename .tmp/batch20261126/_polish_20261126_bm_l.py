# -*- coding: utf-8 -*-
"""bm_l 逐段润色（2026-11-26）。只改元素值，不动数组长度与顺序。
落盘体例：indent=1, ensure_ascii=False, LF（照原文件）。
"""
import ast
import json
import os
import shutil

PATH = 'bm_l_zh.json'
BAK = 'bm_l_zh.json.bak_20261126'
N = 182

# (段号, 旧子串, 新子串, 类别, 理由, 原文)
EDITS = [
    (1,
     '就已经怀着下沉的心感到它的预兆',
     '就已经心里一沉，预感到了这件事',
     '③', 'with a sinking heart 直搬成「怀着下沉的心」，中文无此搭配。',
     'already felt its prophecy with a sinking heart when he planned bringing them together'),
    (4,
     '这年轻人站在她对面，任那阵骚动在她心里和脑海里翻涌。',
     '这年轻人站在她对面；这时那阵骚动正在她心里和脑海里翻涌。',
     '①', '「任」的主语落在年轻人身上，把她的内心骚动写成了他的动作，主谓错接。',
     'The youth stood facing her while this tumult surged within her heart and mind.'),
    (4,
     '他半对自己、半对她地重复道：',
     '他既像对自己、又像对她，重复道：',
     '①', '「半对自己、半对她地」状语叠用不成话。',
     'as he repeated, half to himself and half to her:'),
    (8,
     '听到另一个名字的响声',
     '听到提起另一个名字',
     '①', '「名字的响声」是 at the sound of the name 的死译，中文说「听到提起」。',
     'At the sound of the other name a breath of sadness'),
    (15,
     '这话颤颤地贴着她实际的胸口',
     '这话颤颤地抵着她的胸口',
     '③', 'actual 在此只是强调「真切的胸口接触」，硬译为「实际的」反而添出对照义。',
     'The words trembled against her actual breast, so close she was now leaning against him.'),
    (17,
     '那声音深沉饱满，却并不响亮，却使她浑身颤栗。',
     '那声音深沉饱满，却并不响亮，使她浑身颤栗。',
     '①', '一句两个「却」，转折重复，句子塌了。',
     'The voice deep and full, yet without loudness, thrilled her.'),
    (28,
     '他像一阵风的火的飓风，转向她。',
     '他朝她转过身来，像一股挟着风的火焰飓风。',
     '①', '「一阵风的火的飓风」连缀四个名词，定语链条断掉，读不成句。',
     'He turned upon her like a hurricane of windy fire.'),
    (37,
     '渴望有权利去抚平那奇异的头发',
     '渴望有权利去梳理那奇异的头发',
     '⑥', 'brush hair 是「梳」，不是「抚平」；下句「掀开眼皮、用吻合上」皆具体动作，此处也应具体。',
     'to have the right to brush that wondrous hair'),
    (50,
     '眼睛探进她的脸',
     '眼睛往她脸上探看',
     '①', '「眼睛探进脸」主谓错位（peering into 是看，不是探入）。',
     'his eyes peering into her face'),
    (53,
     '朱利安曾在某种未言明的默契上替她开了门——她失去了他，因为她不敢不顾一切地跟从他所引的路',
     '朱利安替她开门时，神态里含着某种未言明的默契——她失去了他，因为她不敢不顾一切地跟他所引的路',
     '①', 'opened the door upon some unspoken understanding 被直搬成「在默契上开门」，介词关系读不出。',
     'that Julian had opened the door upon some unspoken understanding that she had lost him because she dared not follow recklessly where he led'),
    (66,
     '她用来说要留住我的这种爱，是什么？',
     '她想用来留住我的这种爱，究竟是什么？',
     '①', '「用来说要留住我」两个动词挤在一处，读不出 seekest to hold me with 的意思。',
     'What is this love she seeks to hold me with, saying that I need it?'),
    (83,
     '他想起同事那惊人的供认——那一触即发的恐慌。',
     '他想起同事那惊人的供认——那一丝恐慌的战栗。',
     '⑥', 'the touch of panic terror 的 touch 是「一丝」，误作「一触即发」，意思反了。',
     'He recalled his colleague\'s startling admission--the touch of panic terror.'),
    (88,
     '它还为热而柔软',
     '它因热而松软',
     '①', '「为热而柔软」介词误用（soft with heat 表原因）。',
     'It was soft with heat when I was summoned'),
    (94,
     '与其说对菲利里、不如说对自己地喊出来：',
     '与其说是对菲利里说、不如说是对自己喊出来的：',
     '①', '「不如说对自己地」为硬凑的状语，句子断在「地」上。',
     'exclaimed more to himself than to Fillery:'),
    (106,
     '关于一位会跌倒的人格化神祇的僵死神学',
     '关于一位摇摇欲坠的人格化神祇的僵死神学',
     '⑥', 'tumbling Deity 指「摇摇欲坠、随时会倒的神」，译作「会跌倒」变成神自己摔跤。',
     'the dead theology of man-made notions concerning a tumbling personal Deity'),
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
        assert i == 100 or t.rstrip()[-1] in '。！？…：—」』）', ('end punct', i, t.rstrip()[-6:])
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
    print('JSON 可解析: OK；无空段: OK；无 ASCII 引号: OK；无重复标点: OK；无拉丁残留: OK；引号成对: OK；段末标点: OK（100 为星号行，豁免）')


if __name__ == '__main__':
    main()
    ast.parse(open(__file__, encoding='utf-8').read())
    print('ast self-check: OK')