# -*- coding: utf-8 -*-
"""bm_k 逐段润色（2026-11-26）。只改元素值，不动数组长度与顺序。
落盘体例：indent=1, ensure_ascii=False, LF（照原文件）。
"""
import ast
import json
import os
import shutil

PATH = 'bm_k_zh.json'
BAK = 'bm_k_zh.json.bak_20261126'
N = 165

# (段号, 旧子串, 新子串, 类别, 理由, 原文)
EDITS = [
    (6,
     '他会认出那是由于他想去帮助',
     '他就会认出那是由于莱斯特想去帮助',
     '④', '同段两个「他」分指菲利里与莱斯特，前一处易被读成同一人。',
     'but which Fillery, had he been present, would have recognized as due to his desire to help a pitiful and hungry creature'),
    (26,
     '他又说了另一件事；这一句在一个搏动的瞬间里，并且是她有生以来第一次，让她自己的毫无价值变得可怖地清楚。',
     '他又说了另一件事；在一个搏动的瞬间里，她自己的毫无价值变得可怖地清楚——这是她有生以来第一次。',
     '①', '英语把「for the first time in her life」塞进主谓之间，中文照搬后主谓被插入语拆断。',
     'he also said another thing that for one pulsing second, and for the first time in her life, made her own utter worthlessness become appallingly clear to her.'),
    (29,
     '它们的暴烈那么浪费。',
     '它们的暴烈又那么徒劳无益。',
     '①', '「暴烈那么浪费」缺宾语、不成句；wasteful 指白费力气。',
     'Their violence was so wasteful.'),
    (41,
     '我没有认出你的在场在召唤我。',
     '我没有认出你的在场，也没有认出它在召唤我。',
     '①', '「在场在召唤」两个「在」相撞，动宾读不出。',
     'I did not recognize your presence calling me.'),
    (55,
     '他的低音久久地把那洪亮的振动倾注在房间里。',
     '他那低沉的嗓音久久地把洪亮的振动倾注在房间里。',
     '①', '「他的低音」作施动者不成话（deep tones＝低沉的嗓音）。',
     'For a long time his deep tones poured their resonant vibration through the room.'),
    (68,
     '她觉得自己宽宏大量、慷慨、心肠也大，便写信给他。',
     '她觉得自己宽宏大量、慷慨，心地也宽厚，便写信给他。',
     '①', '「心肠也大」口语悬空，与前面两个形容词并列失配。',
     'feeling magnanimous and generous, big-hearted too, she wrote to him.'),
    (79,
     '他们是无个性的。',
     '他们是非个人的。',
     '⑤', 'impersonal 在本册固定译作「非个人」（「非个人的娜扬」「非个人的服务」），此处不应另造「无个性」。',
     'They are impersonal.'),
    (90,
     '安排了娜扬的来访紧跟在格里森夫人造访的脚跟之后',
     '安排了娜扬的来访紧接在格里森夫人来访之后',
     '③', '英语 on the very heels of 直搬成「脚跟之后」，中文不成话。',
     'planned that Nayan\'s visit should follow upon the very heels of Lady Gleeson\'s call'),
    (91,
     '她在朱利安·莱斯特于画室中那番举动之后第一次来访，其中没有自私的动机。',
     '这是朱利安·莱斯特在画室里有过那番举动之后，她第一次去看他；其中没有自私的动机。',
     '③', '「在……于……之后」三重介词嵌套，主语与状语缠死。',
     'Her first visit to Julian LeVallon after his behaviour in the Studio had no selfish motive in it.'),
    (92,
     '她能看出后一点，也许正是她对男人有力量对付的秘密。',
     '她能看出后一点，也许正是她对男人拥有支配力的秘密。',
     '①', '「对男人有力量对付」主谓错位，句子读不出意思。',
     'That she divined this latter was, perhaps, the secret of her power over men.'),
    (101,
     '房间那头，她要见的那个人高立起来',
     '房间那头，她要见的那个人的高大身影立了起来',
     '①', '「那个人高立起来」把「tall figure」拆成主谓，动作施动者错位（下句另有「他起身了」）。',
     'Across the room rose the tall figure of the man she had come to see'),
    (105,
     '这虽只是模糊地意识到，却扰乱了她清明的头脑，她坐进他让出的椅子；那信念是：她必须照料、关怀，甚至爱这个奇特的青年，仿佛他身在流放之中',
     '这念头虽只是模糊地意识到，却扰乱了她清明的头脑；她坐进他让出的椅子时，那信念是：她必须照料、关怀，甚至爱这个奇特的青年，仿佛他身在流放之中',
     '①', '英语把「as she took the chair」插在主句中间，中文照搬后「这虽只是模糊地意识到」缺主语、后半句悬空。',
     'Realized though dimly, this troubled her clear mind, as she took the chair he offered, the conviction that she must tend and care for, even love this strange youth'),
    (118,
     '「而我现在仍旧忘着，」',
     '「而我仍旧在遗忘，」',
     '①', '「仍旧忘着」为硬凑的进行体，中文不成立。',
     '"And I still forget,"'),
    (119,
     '他声音一停，一个奇怪的、空寂无生命的空洞，仿佛落进了他们之间的房间。',
     '他声音一停，仿佛有一个奇怪的、没有生命的空洞，落进了他们之间的房间里。',
     '①', '「一个……空洞……落进了房间」主谓与「仿佛」的位置颠倒，读来像断言而非比拟。',
     'A curious hollow, empty of life, seemed to drop into the room between them as his voice ceased.'),
    (132,
     '她的头脑、她的心、她的经验、她最深的女人天性，她在一个奇异地占卜的灼亮瞬间意识到，在她身上是互相冲突的。',
     '她的头脑、她的心、她的经验、她最深的女人天性，在她身上互相冲突；她在一个灼亮而近于占卜的瞬间意识到了这一点。',
     '①', '并列主语与「她……意识到」两个主语挤在一句，主谓失配；「奇异地占卜的」亦不成定语。',
     'Her mind, her heart, her experience, her deepest womanly nature, these, she realized in a glowing instant of extraordinary divination, were at variance in her.'),
    (143,
     '仿佛轻化她的是热，载她向上的是风。',
     '仿佛使她变轻的是热，载她向上的是风。',
     '①', '「轻化」为生造词，且与「载」不对仗。',
     'as if it was heat that lightened, and wind that bore her upwards.'),
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
        assert t.rstrip()[-1] in '。！？…：—」』）', ('end punct', i, t.rstrip()[-6:])
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
    print('JSON 可解析: OK；无空段: OK；无 ASCII 引号: OK；无重复标点: OK；无拉丁残留: OK；引号成对: OK；段末标点: OK')


if __name__ == '__main__':
    main()
    ast.parse(open(__file__, encoding='utf-8').read())
    print('ast self-check: OK')