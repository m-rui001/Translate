# -*- coding: utf-8 -*-
"""bm_m 逐段润色（2026-11-26）。只改元素值，不动数组长度与顺序。
落盘体例：indent=1, ensure_ascii=False, LF（照原文件）。
"""
import ast
import json
import os
import shutil

PATH = 'bm_m_zh.json'
BAK = 'bm_m_zh.json.bak_20261126'
N = 156

# (段号, 旧子串, 新子串, 类别, 理由, 原文)
EDITS = [
    (9,
     '「这不怕你？」他问',
     '「这不叫你害怕吗？」他问',
     '⑥', 'It does not frighten you? 的主客关系读反：不是「它怕你」，是「你不怕它」。',
     'He looked at the girl sharply with unconcealed admiration. "It does not frighten you?" he asked'),
    (13,
     '他还被我们对死亡的恐惧弄糊涂了',
     '他还弄不懂我们为什么怕死',
     '③', 'be puzzled by 硬搬成「被……弄糊涂」，主语悬空、被动无施动者。',
     'he is puzzled by our dread of it'),
    (37,
     '而那声音，起初虽微弱遥远，却证实了他。',
     '而那声音，起初虽微弱遥远，却叫他确信无疑。',
     '①', 'confirmed him 译作「证实了他」，宾语错位（证实的是他自己的判断）。',
     'and the sound, though faint and distant at first, confirmed him.'),
    (44,
     '它们竭力想通过一个容不下它们使用的有限形体表达自己，却徒然。',
     '它们竭力想通过一个不足以供它们使用的有限形体表达自己，却徒然。',
     '①', '「容不下它们使用」主谓错接，inadequate to their use 说的是形体不够用。',
     'straining, but vainly, to express themselves through a limited form that was inadequate to their use'),
    (44,
     '都被给了一推、一驱、一冲，刺激了那人最主要的特征，把它强化。',
     '都会得到一记推、一股驱力、一次冲击，那刺激正落在那人最主要的特征上，把它强化。',
     '③', '「被给了」是无施动者的被动硬搬，三个量词也失当。',
     'was given a push, a drive, an impetus that stimulated that individual\'s chief characteristic, intensifying it.'),
    (48,
     '别的被同样居住着的人身',
     '别的人身，里面住着同样的住客',
     '③', '「被同样居住着的人身」是 similarly inhabited 的被动直搬，中文不成话。',
     'other human bodies similarly inhabited'),
    (65,
     '一个我们所谓的历时期',
     '一个我们所谓的历史时期',
     '⑥', '「历时期」漏字，当作「历史时期」（a period of history）。',
     'a period of history, as we call it'),
    (101,
     '而这增涨的活力之洪流',
     '而这增长的活力之洪流',
     '⑥', '「增涨」为错字，当作「增长」。',
     'this flood of increased vitality'),
    (105,
     '把世界变成一个巨大而美味的花园',
     '把世界变成一个巨大而美妙的花园',
     '⑥', 'delicious 此处指「妙不可言」，译「美味」误作可食。',
     'turning the world into a vast, delicious garden.'),
    (106,
     '它细小的根吸取了它所需的生活',
     '它细小的根吸取了它所需的生命',
     '⑥', 'the life it needed 是「生命」，误作「生活」。',
     'Through the huge mass of earth\'s body its tiny roots had drawn the life it needed.'),
    (127, '一种神圣不死的感觉得着他。', '一种神圣不死的感觉得着了他。',
     '⑥', '「感觉得着他」缺「了」，句子断在动词后。',
     'A sensation of divine deathlessness possessed him.'),
    (127,
     '逃脱的意义在他变得明白。',
     '逃脱的意义在他心里变得明白了。',
     '①', '「在他变得明白」主语悬空，缺方位与语气词。',
     'The meaning of escape became plain to him.'),
    (143,
     '他被震到了核心。',
     '他被震到了骨子里。',
     '③', 'shaken to the core 直搬「震到核心」，中文说「骨子里」。',
     'He was shaken to the core.'),
    (153,
     '他们停了一会儿，其中一个人感到了难以置信的感觉。',
     '他们停了一会儿，其中一人有了难以置信的感受。',
     '①', '「感到……感觉」同根重复，且「其中一个人」拖沓。',
     'To one man came incredible sensations as they paused a moment.'),
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
        assert i in (38, 46) or t.rstrip()[-1] in '。！？…：—」』）', ('end punct', i, t.rstrip()[-6:])
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
    print('JSON 可解析: OK；无空段: OK；无 ASCII 引号: OK；无重复标点: OK；无拉丁残留: OK；引号成对: OK；段末标点: OK（38/46 为星号行，豁免）')


if __name__ == '__main__':
    main()
    ast.parse(open(__file__, encoding='utf-8').read())
    print('ast self-check: OK')