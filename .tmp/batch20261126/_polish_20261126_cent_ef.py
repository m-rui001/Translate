# -*- coding: utf-8 -*-
"""cent_e / cent_f 逐段通读润色（2026-11-26 第二轮）。

改法：读原始字节 -> 唯一子串定位替换（全篇唯一）-> 断言数组长度/无空段 -> 原样写回。
CRLF + indent=1 保持不动（不做 json.dump 重排）。
"""
import ast
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

E_EDITS = [
    # ① 「回答」被前置后缺指示词，读起来像主宾错置
    ("回答他几乎没接住，只感到那人的目光沉沉地压在他身上",
     "那回答他几乎没接住，只感到那人的目光沉沉地压在他身上"),
    # ⑥ background 误作「底板」（木器/地板义），此处是「模糊的背景」
    ("你把它从潜意识的整个底板里提举出来",
     "你把它从那片潜意识的模糊背景里提举出来"),
    # ③/⑥ singularly undefiled 直搬成「异常未染」，不成词
    ("一种异常未染的纯真——一种原初的、自发的纯真",
     "一种异样地未曾被沾染的纯真——一种原初的、自发的纯真"),
    # ① sank down into him 直搬「沉进了他里面」
    ("这话沉进了他里面。", "这话沉进他心里。"),
    # ⑥ quote 是动词「引用」，不能写成名词「引文」
    ("显然他是在引文。", "显然他是在引书上的话。"),
    # ① 「源于……有多远」不成句（the distance men had traveled）
    ("都源于人离开世界之灵魂有多远——",
     "全在于人离开世界之灵魂走了多远——"),
    # ⑤ transliminal 全册他处作「超阈」（cent_f 两见），此篇「越限」归一
    ("从那新醒来的意识的越限深处",
     "从那新醒来的意识的超阈深处"),
    # ⑤ inner catastrophe 本册 canon 作「内在灾变」（d/e/f 共五见），此篇两写不一
    ("当那「内在的灾变」自己完成", "当那「内在灾变」自己完成"),
    # ① 一句两个「那」，主语悬空
    ("那否认至少对他而言，那才是真正守在他门槛上的东西。",
     "那否认，至少对他而言，才是真正守在他门槛上的东西。"),
    # ⑥ exact height 误作「确实高度」（确实不作定语）
    ("山的确实高度、河的长度", "山的准确高度、河的长度"),
    # ③ so far as practical details are concerned 后置状语照搬
    ("在他心里是朦胧的，就实际细节而言；因为他发觉自己",
     "就实际细节而言，在他心里是朦胧的；因为他发觉自己"),
    # ① 「那是……一个念头」指代悬空（原意：那些字句是大地借他倾泻的念头）
    ("施塔尔的眼神已经变了——那是大地有一刻借他倾泻而出的一个念头。",
     "施塔尔的眼神已经变了——那些字句，是大地有一刻借他倾泻而出的一个念头。"),
    # ② 一句话里四个「的」把「那一页」压没，拆成同位语
    ("因为对着铁路事故、活活烧死的人、爆炸、大罢工、摔扁的飞行家，"
     "以及现代发明献给热病般进步的祭坛的其他无数恐怖的那一页上，"
     "他读到一篇自满地夸口的社论",
     "因为就在那一页上——满是铁路事故、活活烧死的人、爆炸、大罢工、"
     "摔扁的飞行家，以及现代发明献给热病般进步之祭坛的其他无数恐怖——"
     "他读到一篇自满地夸口的社论"),
    # ① 两个「进到」叠用，第二处改「到不了」
    ("因为它的消息不肯进到屋里去，进不到那受灵感的作者心里",
     "因为它的消息不肯进到屋里去，到不了那受灵感的作者心里"),
    # ⑦ 星号分隔行全册 canon 为「＊　＊　＊　＊　＊」（全角空格；a/g/h/i 共十余处），
    #    本篇与 cent_d 用半角空格，归一
    ("＊       ＊       ＊       ＊       ＊",
     "＊\u3000＊\u3000＊\u3000＊\u3000＊"),
]

F_EDITS = [
    # ③/① 比较从句照搬（a force made visible as literally as a house was...）
    ("花是一个被造得可见的力，其确实的程度不下于一幢房子是建筑师心灵所造得可见的力。",
     "对这颗富于想象的心来说，花就是一个变得可见的力——它的字面为真，"
     "正如一幢房子是建筑师的心使它变得可见的一个力。"),
    # ⑥ 量词错：界限不能论「张」
    ("过了哪一步便算越出一张人为成规的界限",
     "过了哪一步便算越出了人为成规的界限"),
    # ① 「脑子以眼睛察觉」主谓错配，悬空状语还原
    ("他那部分活跃的脑子以略有些迷蒙的眼睛，察觉这行进中的动在静静伫立的树下、"
     "在月光照亮的林间空地上往来移动。",
     "眼睛还有些迷蒙，他脑中那活跃的一部分却察觉：这行进中的动作正在静静伫立的树下、"
     "在月光照亮的林间空地上往来移动。"),
    # ① 「加重语气地说」不成话
    ("他加重语气地说，在初醒的那一刻", "他强调说，在初醒的那一刻"),
    # ① 同位语被破折号切断，末句悬空（the message ... --the rush and murmur of the Urwelt calling）
    ("他所有的感官都接到那黄金时代的消息——那正是他的渴慕一向所求的——"
     "原初世界奔涌的声息在召唤。",
     "他所有的感官都接到那黄金时代的消息——他长久渴慕所求的消息——"
     "原初世界的奔涌与低语在召唤。"),
    # ① 「第一座、也是巨人的花园」顿号处断裂
    ("那时一切都还是第一座、也是巨人的花园。",
     "那时一切都还是第一座花园，也是巨人的花园。"),
    # ② 三个「的」串在「感觉」上
    ("这种分裂的自我的感觉对他并不新鲜",
     "这种自我分裂之感对他并不新鲜"),
    # ① 「说出一种镇定」动宾失配（He spoke with a confidence he hardly felt）
    ("他说出一种自己几乎并未感到的镇定。",
     "他说话的口气里带着一种自己几乎并未感到的镇定。"),
    # ⑥ stuffed the clothes against his ears 误作「塞到耳朵上」
    ("他把衣服塞到耳朵上等着", "他把衣服捂在耳朵上等着"),
    # ① 状语「含混地对着地面」挂在「听见」上，位置错
    ("他听见那话含混地对着地面咕哝。", "他听见那声音贴着地面含混地咕哝。"),
    # ⑥ wicked 误作「毒」，且「并非邪……而是诡邪」自相抵牾
    ("有什么东西经过了，并非恶、并非毒、并非邪，而是奇异与异类——诡邪。",
     "有什么东西经过了，与其说是恶、是坏、是邪，不如说是奇异、异类——诡异。"),
    # ① 「叩拜刮地」不成词（bowing to the ground with flattened palms）
    ("朝麦加叩拜刮地，呻吟着", "朝麦加匍匐叩拜，额头蹭着地面，呻吟着"),
    # ③ with a kind of sudden spring 直搬成「突然的弹跳」
    ("那人带着一种突然的弹跳猛地站起。", "那人猛地一弹，骤然站起。"),
    # ① 「百万花与草的气味」基数词错位（smells of a million flowers and weeds）
    ("用它更浓烈的百万花与草的气味把它闷住之前",
     "用它更浓烈的、百万种花草的气味把它闷住之前"),
    # ① 主语连同三个插入语一起被「又使话语含混不清」拖断
    ("而那复杂的回答，嘴唇几乎贴地，跪着时头只微微转动，又使话语含混不清。",
     "而那复杂的回答——嘴唇几乎贴着地面，跪着时头只微微转动——字句又一次被闷住了。"),
    # ① 「具备……东西」中心语失配
    ("而奥马利看来恰好具备那种判断与占卜的分量——如古时的希伯来先知——"
     "正是造就一个真正明眼人的东西。",
     "而奥马利看来恰好有那种判断与占卜的分量——如古时的希伯来先知——"
     "那正是造就一个真正明眼人的东西。"),
    # ① 「以其品级之名为……」语序倒错（had for the title of their order）
    ("古代不列颠的吟游诗人以其品级之名为『那些在全世界自由的人』。",
     "古代不列颠的吟游诗人以『那些在全世界自由的人』为他们的等级称号。"),
]


def apply(key, edits):
    p = os.path.join(BASE, '%s_zh.json' % key)
    with open(p, 'r', encoding='utf-8', newline='') as f:
        txt = f.read()
    before = len(json.loads(txt))
    hits = 0
    for old, new in edits:
        c = txt.count(old)
        assert c == 1, ('not unique/not found: %d' % c, old[:50], key)
        txt = txt.replace(old, new, 1)
        hits += 1
    arr = json.loads(txt)
    assert len(arr) == before, ('para count changed', before, len(arr), key)
    assert all(isinstance(x, str) and x.strip() for x in arr), 'empty paragraph: ' + key
    assert '\r\n' in txt, 'CRLF lost: ' + key
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(txt)
    nhan = sum(1 for ch in ''.join(arr) if '\u4e00' <= ch <= '\u9fff')
    print('%-8s edits=%2d paras=%d han=%d ok' % (key, hits, len(arr), nhan))
    return hits


def selfcheck(keys):
    bad = 0
    for key in keys:
        p = os.path.join(BASE, '%s_zh.json' % key)
        d = json.load(open(p, encoding='utf-8'))
        bak = json.load(open(p + '.bak_20261126', encoding='utf-8'))
        assert len(d) == len(bak), key
        for i, s in enumerate(d):
            if not s.strip():
                print(key, i, 'EMPTY'); bad += 1
            if '"' in s:
                print(key, i, 'ASCII quote'); bad += 1
            if '。。' in s or '，，' in s or '、、' in s or '；；' in s:
                print(key, i, 'dup punct'); bad += 1
            if s.count('「') != s.count('」'):
                print(key, i, 'quote unbalanced'); bad += 1
            if s.count('『') != s.count('』'):
                print(key, i, 'nest quote unbalanced'); bad += 1
            if '⟦' in s or '⟧' in s:
                print(key, i, 'bracket'); bad += 1
            if s != s.strip():
                print(key, i, 'leading/trailing ws'); bad += 1
            if '  ' in s.replace('\u3000', ' '):
                print(key, i, 'double space'); bad += 1
    print('selfcheck problems:', bad)


if __name__ == '__main__':
    n = apply('cent_e', E_EDITS)
    n += apply('cent_f', F_EDITS)
    print('total edits =', n)
    selfcheck(['cent_e', 'cent_f'])
    ast.parse(open(__file__, encoding='utf-8').read())
    print('ast.parse ok')