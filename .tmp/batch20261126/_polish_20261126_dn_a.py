# -*- coding: utf-8 -*-
"""dn_a 逐段通读润色（2026-11-26）。只改七类；数组长度与顺序不变。"""
import ast
import json
import os
import re
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
ZH = os.path.join(BASE, 'dn_a_zh.json')
BAK = ZH + '.bak_20261126'

assert os.path.exists(BAK), 'backup missing'

with open(ZH, encoding='utf-8', newline='') as f:
    d = json.load(f)
with open(BAK, encoding='utf-8', newline='') as f:
    orig = json.load(f)

n_before = len(d)
assert len(d) == len(orig) == 123

# (段号, 类别, 旧子串, 新子串, 理由, 英文原文)
EDITS = [
    (1, '①',
     '——不像这些年间每回追忆时，岁月都给那感觉添上一层可悲的减损。',
     '——不是带着这些年间每一回追忆时岁月给它添上的那层可悲的减损。',
     '「不像＋主语从句」读成了比较，原意是「不带那种减损」，补出谓语动词。',
     'not with that tragic lessening the interval had brought to each repetition of its memory'),
    (6, '⑥',
     '可声音不济了',
     '可嗓子不听使唤了',
     '「声音不济」不成话（「不济」指本事差），her voice failed 是气力接不上。',
     'but her voice failed'),
    (12, '⑤①',
     '把远处求爱那些日子里的每一处细节都热烈地记起来，那是在白色小花园门那边、不许人进出的牧师宅花园里。',
     '把远处那些求爱日子里的每一处细节都热烈地记起来——那些日子是在那扇白色小花园门外、不许人进的教区长宅花园里过的。',
     '（一）rectory 全篇与「教区长」并称，此处作「牧师宅」不统一；（二）「，那是在……」悬空修饰，改成同位说明。',
     'remembered passionately each detail of the far-off courtship days in the forbidden rectory garden beyond the small, white garden gate'),
    (15, '①',
     '他此来已不再是他自己所认为的、一桩体面的尽责之举；',
     '他此来已不再是为了他自己也许会认作体面尽责之举的那桩事；',
     '主语「他此来」与表语「一桩……之举」类别不合，主谓失配。',
     'No longer was he bound upon what he deemed, perhaps, an act of honourable duty'),
    (20, '③',
     '他有意识时并不觉得它们',
     '他并不曾自觉地意识到它们',
     'Consciously 是「自觉地」，译成「有意识时」读成时间状语。',
     'Consciously, he was not aware of them'),
    (20, '①',
     '他心不在焉地认出了它们，可以说；并不分析追究。',
     '他可以说是心不在焉地认出了它们；并不去分析、追究。',
     '「可以说」被甩在分号前，句子断裂；as it were 修饰的是「认出」。',
     'He recognised them absentmindedly, as it were; did not analyse or investigate them.'),
    (20, '①',
     '也升起某种不安的暗示，它在一两件无关紧要的举动上表现为轻微的迟疑或失算，把自己泄露出来。',
     '也升起某种不安的暗示，它借着在一两件无关紧要的举动上的轻微迟疑或失算，把自己泄露出来。',
     '「表现为……，把自己泄露出来」两个谓语并列，后一个悬空。',
     'a certain hint of insecurity that betrayed itself by a slight hesitancy or miscalculation in one or two unimportant actions'),
    (20, '⑥',
     '只因短短的半个钟头，就恰好——太迟了',
     '只差短短的半个钟头，就恰好——太迟了',
     'by a brief half-hour 是差半小时，非「因为」半小时。',
     'and, by a brief half-hour, was just--too late'),
    (21, '①',
     '也正因为这份急，他才有那些轻微的失算，或许。',
     '也正因为这份急，或许，他才有那些轻微的失算。',
     'possibly 是插入语，位置照搬英文句末，中文读着断气。',
     'And, due to this hurry, possibly, were the slight miscalculations that he made.'),
    (22, '⑥',
     '还要给他添上年岁的模样',
     '还要给他添上几岁年纪',
     'add to the appearance of the years he bore＝显老，「添上年岁的模样」不成话。',
     'add to the appearance of the years he bore'),
    (23, '⑥',
     '然后一路唱着、兴冲冲地顺着弯曲的小径出发了',
     '然后兴冲冲、急匆匆地顺着弯曲的小径出发了',
     '原文此处只说 gaily and impetuously，唱是下一句的事，「一路唱着」既误译又重复。',
     'set out gaily and impetuously along the winding lane'),
    (26, '⑤',
     '「往牧师宅」',
     '「往教区长宅」',
     'rectory 与 [22] 的「教区长」并称，统一为「教区长宅」。',
     '"To the Rectory."'),
    (26, '①',
     '每一个细小之处都满满装着亲爱联想的货。',
     '每一个细小之处都满载着亲昵的联想。',
     'cargo 直搬成「货」，中文不成话；改成动词句。',
     'each little detail brimmed with its cargo of fond association'),
    (29, '⑤',
     '看见了牧师宅的烟囱',
     '看见了教区长宅的烟囱',
     '同 [12][26]，rectory 归一为「教区长宅」。',
     'the chimneys of the rectory'),
    (30, '①',
     '这静、这沉寂，满在他四周。',
     '这静、这沉寂，遍布他的四周。',
     '「满在他四周」缺谓语搭配。',
     'This stillness, silence, was all about him.'),
    (31, '⑥③',
     '气急败坏、力竭一般扑在他眼前与她的眼睛之间那道微不足道的障碍上',
     '上气不接下气、力气用尽，扑在隔开他双眼与她双眼的那道微不足道的障碍上',
     '（一）breathless and exhausted 是喘不上气、力尽，「气急败坏」是恼怒；（二）「他眼前与她的眼睛之间」两截不对称。',
     'flung himself, breathless and exhausted, against the trivial barrier that stood between his eyes and--hers'),
    (33, '①',
     '他推那不肯让开的一层。',
     '他推那不肯让开的表面。',
     'surface 译作「一层」，量词与所指都不对。',
     'he pushed against the unyielding surface'),
    (38, '⑥',
     '他的声音怪异地不济；里面没有力气。',
     '他的声音怪异地提不起来；里面没有力气。',
     '同 [6]：His voice failed oddly，非「不济」。',
     'His voice failed oddly; there was no power in it.'),
    (41, '①',
     '他擂着、打着那扇白色小花园门那不肯让开的一层。',
     '他擂着、打着那扇白色小花园门不肯让开的表面。',
     '两个「那」连排、又用「一层」译 surface，读不通。',
     'he hammered and beat against the unyielding barrier of the small, white garden gate'),
    (53, '①⑦',
     '「你这样下去，一辈子也嫁不出去，孩子，更别想照你本该有的样子嫁人，」她说，「要是你脸上老挂着那副兔子的神情。现在到咱们家来住的那类体面年轻人，可不是这么钓的。',
     '「你要是脸上老挂着那副兔子的神情，一辈子也嫁不出去，孩子，更别想照你本该有的样子嫁人，」她说，「现在到咱们家来住的那类体面年轻人，可不是这么钓的。',
     '「要是……」被劈到后半句，还以句号收尾，条件句成了半截话；条件从句前置。',
     '"You\'ll never marry at all, child, much less marry as you might," she said, "if you go about with that rabbit expression on your face.'),
    (57, '①',
     '他们对待用人，',
     '他们对待用人的方式，',
     '并列项里只有这一项没谓语也没中心语，成了悬空短语。',
     'their treatment of the servants'),
    (57, '⑥',
     '也按这一伙人的风气行事，趁着她最后一场放荡——',
     '也按这一伙人的风气行事，纵情于她最后一场放荡——',
     'expected over her final fling 的 over 是「在……之际」，译作「趁着」把语气读反了。',
     'behaving as the tone of the clique expected over her final fling'),
    (58, '③',
     '他们已经进了容易说话的距离。',
     '他们已经近得能说话了。',
     'within easy speaking range 的 range 硬搬成「距离」。',
     'They were within easy speaking range.'),
    (64, '③',
     '「就跟她们恰恰是另一路一样确凿！」',
     '「正如她们恰恰是相反的一路，同样确凿无疑！」',
     'as surely as… 的比较框架直搬，中文看不出是「同样确凿」。',
     '"as surely as they are just the other thing!"'),
    (93, '①',
     '把他唤回那仿佛是当下的东西',
     '把他唤回那仿佛是当下的境地',
     '「唤回……东西」搭配不成，「present」是所处的现实。',
     'recalled him at length to what seemed the present'),
    (97, '①',
     '那种除自己以外谁都瞧不起，',
     '那种除自己以外谁都瞧不起的傲慢，',
     '并列名词短语缺中心语。',
     'the contempt of all others but themselves'),
    (97, '②',
     '那种被当作欢快的、没趣味的头脑的胡闹',
     '那种出自没趣味头脑、却被当作欢快的胡闹',
     '三个「的」串成「被当作欢快的／没趣味的头脑的／胡闹」，中心语读不出来。',
     'the horseplay of tasteless minds that passed for gaiety'),
    (102, '①',
     '花园躺在黑白里，满得溢出来的美，被古老的银色月光穿过，点缀着星星的旧金色。',
     '花园躺在黑白里，美得满溢出来，被古老的银色月光穿过，点缀着星星的旧金色。',
     '「满得溢出来的美」是悬空同位语，接不上后半句的主语链。',
     'In black and white the garden lay, brimmed full with beauty, shot by the ancient silver of the moon'),
    (104, '①',
     '于是失掉了度量所记事物的标准',
     '于是他失掉了衡量所记事物的标准',
     'so that 从句缺主语，与前句主语断链。',
     'so that he lost the standard of remembered things'),
    (104, '⑥',
     '跳过那些辛苦培植出来供人玩笑的花坛',
     '跳过那些费尽人工修剪出来、含着嘲弄意味的花坛',
     'shaped in mockery 是「以嘲弄（自然）的手法治成」，「供人玩笑」误读。',
     'they leaped the flower-beds, so laboriously shaped in mockery'),
    (106, '⑥',
     '他们手拉手一同跑过干净的夏月。',
     '他们手拉手一同跑过干净的夏日月光。',
     'moonlight 漏成「夏月」，与「六月黄昏」的时间线自相矛盾。',
     'they raced on together through the clean summer moonlight'),
    (119, '③',
     '他的眼睛把主宰放在她的眼睛上。',
     '他的目光压住她的目光，俨然是主宰。',
     'put mastery on 逐字搬，中文不成句。',
     'His eyes put mastery on her own.'),
    (121, '①',
     '崇拜的静穆偷上了她小小的脸',
     '崇拜的静穆悄悄爬上了她小小的脸',
     '「偷上了」动词不成词。',
     'the hush of worship stole upon her little face'),
]

counts = {k: 0 for k in '①②③④⑤⑥⑦'}
for idx, cat, old, new, why, eng in EDITS:
    t = d[idx]
    assert old in t, (idx, old)
    assert t.count(old) == 1, (idx, old, t.count(old))
    d[idx] = t.replace(old, new)
    for c in cat:
        counts[c] += 1

# ---- 自检 ----
assert len(d) == n_before == 123
assert all(p.strip() for p in d)
for i, p in enumerate(d):
    assert '"' not in p, i
    assert not re.search(r'[。，]{2,}', p), i
    assert '⟦' not in p and '⟧' not in p, i
    assert not re.search(r'[\u4e00-\u9fff] [a-z]+ ', p), i
    if i not in (7, 43, 56):           # 分段星号行不带标点
        assert p[-1] in '。！？……」—' or p.endswith('：') or p.endswith('：') or p[-1] in '：', i

with open(ZH, 'w', encoding='utf-8', newline='') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write('\n')

# 复核落盘
with open(ZH, encoding='utf-8', newline='') as f:
    chk = json.load(f)
assert len(chk) == 123 and chk == d

hanzi = sum(len(re.findall(r'[\u4e00-\u9fff]', p)) for p in d)
print('length=', len(chk), ' edits=', len(EDITS), ' hanzi=', hanzi)
print('by category:', counts)
ast.parse(open(__file__, encoding='utf-8').read())
print('ast ok')