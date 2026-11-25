# -*- coding: utf-8 -*-
"""2026-11-26 逐段润色：cent_a、cent_b（黑木《半人马》The Centaur 分片）。

对齐说明：两篇源文的章序行（I / II / ... / XI）单独成段，译稿未收，
故 offset 分别为 5 与 6；逐段对应为 zh[j] <-> src[去掉章序行后的第 j 项]。

落盘方式：定位唯一子串 → 替换 → 断言命中数，保留原 indent=1 与 CRLF。
"""
import ast
import json
import os
import re
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    'a': [
        # ⑥ 词义：big people 是「大个子」，非「大人物」
        ("他那体格并不像大人物常有的情形那样把人压得透不过气",
         "他那体格并不像大个子常有的情形那样把人压得透不过气"),
        # ⑥ 量词：「一个……个性」不成搭配（individuality）
        ("奥马利本人就是一个从庸众中站出来引人注目的个性。",
         "奥马利本人就是一个从庸众中站出来引人注目的个体。"),
        # ① 缺主语：「血管里」悬空（was in his blood）
        ("血管里有一种对荒野的贪求，热切，不可餍足。",
         "他血管里有一种对荒野的贪求，热切，不可餍足。"),
        # ⑥ 硬伤：bone label 是骨制标签，不是骨牌（domino）
        ("仔细地系着一块骨牌标签",
         "仔细地系着一块骨制的标签"),
        # ⑥ 量词：valley of dry bones 是谷地，不是「一条谷」
        ("不过是一条枯骨的谷。",
         "不过是一片枯骨的谷地。"),
        # ③ 插入语直搬（This clue, as he called it, crystallized ...）
        ("这条线索，他这样称呼它，把他自己心智的挣扎结晶得如此整齐、如此决断",
         "这条他所谓的线索，把他自己心智的挣扎结晶得如此整齐、如此决断"),
        # ③ irregular correspondence 是通信时断时续，非「信件不规则」
        ("爱尔兰人与施塔尔医生通信往还数月，信件颇不规则，彼此交锋",
         "爱尔兰人与施塔尔医生通信往还数月，信件时断时续，彼此交锋"),
        # ① 悬空同位语（I, who loved him and listened, yet never ...）
        ("我，爱他，也听他讲，却从未完全领会他的全部意思。",
         "我虽然爱他、也听他讲，却从未完全领会他的全部意思。"),
        # ① 感叹残句读不通（Living idea, that!）
        ("活的思想，那个！",
         "活生生的思想，正是这个！"),
        # ① 直搬 on the tip of his tongue，中文不成句
        ("这种时候，他舌头上就有着一句关于他们的话，或一个问题。",
         "这种时候，话就到了他舌尖上——一句关于他们的话，或一个问题。"),
        # ⑥ 硬伤：half-way down the table opposite 是「对面桌子中段」
        ("「我在看对面半桌子那两个人。",
         "「我在看对面桌子中段的那两个人。"),
        # ③ 抽象名词直搬（essential inarticulateness struggling into an utterance）
        ("更像是本质的不能言说在挣扎着发出一种对它是生疏的、不合适的语言。",
         "更像是本质上的不能言语，挣扎着要挤出一句对它生疏而不合的语言。"),
        # ⑥ 错字：「费着力」不成词
        ("把话一字一字凿出来，真费着力",
         "把话一字一字凿出来，真费着力气"),
        # ⑤ 全册 bridge 以「舰桥」为多数派（4:2），此处二处归一
        ("相当笨重的轻快往驾驶台去了",
         "相当笨重的轻快往舰桥去了"),
        ("不过有时候让我上驾驶台跟你抽支烟行吗？",
         "不过有时候让我上舰桥跟你抽支烟行吗？"),
        # ⑥ 搭配：deny himself 是「克制自己不去取用」，非「禁绝自己」
        ("这些贪求代表着灵魂的掳获物，而他必须禁绝自己。",
         "这些贪求代表着灵魂的掳获物，而他必须克制自己不去取用。"),
    ],
    'b': [
        # ⑥ 量词：smother of sham universal culture 是一股闷气，非「一堆」
        ("那堆伪普世文化的闷气",
         "那股伪普世文化的闷气"),
        # ① 缺中心语：the currents of wind and sea 是气流
        ("风与海的流先是经由他到达我",
         "风与海的气流先是经由他到达我"),
        # ② 三个「的」把中心语压没（那深深埋在我自身之中的东西的极端例子）
        ("他是那深深埋在我自身之中的东西的极端例子",
         "他是我自身深处那件东西的极端例子"),
        # ① 状语直搬（evaded him in terms of physical definition）
        ("虽然它们在形体界定上躲开他",
         "虽然它们在形体上总是躲开他"),
        # ① 定语串读不通（证实了他做了件鲁莽事的感觉）
        ("医生的态度证实了他做了件鲁莽事的感觉。",
         "医生的态度证实了他觉得自己做了件鲁莽事。"),
        # ⑥ 硬伤：so kindly ripened 是承它好意，非「好歹」
        ("虽然它们好歹让我们的相识熟成了友谊",
         "虽然它们竟如此好心地让我们的相识熟成了友谊"),
        # ③ 被动硬搬（placed him in the midst of humanity thus absolutely alone）
        ("并且使他被置于人类之中而绝对孤立",
         "并且使他在人类当中绝对孤立"),
        # ① 「是……的」框架套住长状语，句子散架
        ("施塔尔平静地讲着，他是如何被在疯人院和私人诊室里注意到的那些事实逼到某种这样的信念的。",
         "施塔尔平静地讲着，他如何被疯人院和私人诊室里注意到的那些事实逼到了这样一种信念。"),
        # ① 「被关押、戴镣在……里」动宾错位
        ("他不再被关押、戴镣在一个渺小人格的监牢里。",
         "他不再被关锁、被戴上镣铐，囚在一个渺小人格的牢里。"),
        # ① 「自觉得不可少的独处里」定语断裂
        ("奥马利在当晚自觉得不可少的独处里",
         "奥马利在那晚他觉得不可或缺的独处里"),
        # ① 「爱抚弄着它」歧义（played lovingly with it）
        ("他爱抚弄着它。",
         "他满怀爱意地反复玩味它。"),
        # ⑥ 词义：Hold up! 此处是「站住／别动」
        ("「撑住！」他听见耳语",
         "「站住！」他听见耳语"),
    ],
}


def apply(key, edits):
    p = os.path.join(BASE, 'cent_%s_zh.json' % key)
    bak = p + '.bak_20261126'
    if not os.path.exists(bak):
        shutil.copy2(p, bak)
        print('backup made:', os.path.basename(bak))
    else:
        print('backup exists, kept:', os.path.basename(bak))
    with open(p, 'r', encoding='utf-8', newline='') as f:
        txt = f.read()
    assert '\r\n' in txt, 'CRLF expected'
    before = json.loads(txt)
    n = 0
    for old, new in edits:
        c = txt.count(old)
        assert c == 1, ('hit count %d' % c, old[:40])
        txt = txt.replace(old, new, 1)
        n += 1
    after = json.loads(txt)
    assert len(after) == len(before), ('paras changed', len(before), len(after))
    assert all(x.strip() for x in after), 'empty paragraph'
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(txt)
    return n, after


def checks(key, d):
    t = '\n'.join(d)
    bad = []
    if '"' in t:
        bad.append('ASCII quote')
    if re.search(r'[。，、；：！？]{2,}', t):
        bad.append('dup punct')
    if re.search(r'[\u4e00-\u9fff] [a-z]{2,} ', t):
        bad.append('latin residue')
    if not all(x.strip() for x in d):
        bad.append('empty para')
    print('  checks:', 'OK' if not bad else ' / '.join(bad))
    return not bad


if __name__ == '__main__':
    for key in ('a', 'b'):
        n, d = apply(key, EDITS[key])
        han = sum(1 for ch in ''.join(d) if '\u4e00' <= ch <= '\u9fff')
        print('cent_%s: edits=%d paras=%d han=%d' % (key, n, len(d), han))
        checks(key, d)
    ast.parse(open(__file__, encoding='utf-8').read())
    print('ast.parse OK')