# -*- coding: utf-8 -*-
"""逐段润色 dn_b（2026-11-26）。只改 d[i] 的值，不改长度/顺序。"""
import ast
import json
import re
import os

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dn_b_zh.json')
BAK = PATH + '.bak_20261126'

# (段号, 类别, 旧子串, 新子串, 英文原文 / 理由 说明)
EDITS = [
    (2, '⑥', '它随风雨一同落下', '它随了风与水一同落下',
     'fallen "with the wind and water" 指风与水两种元素，前文亦作「风与水」，非「风雨」'),
    (3, '①', '「他来了……他来了……！」随着风与水的低语，从无数低垂的头顶上升起。',
     '「他来了……他来了……！」这喊声随了风与水的低语，从无数低垂的头顶上升起。',
     '"rose with the murmur of the wind and water" 主语是呼声，原译悬空无主语'),
    (9, '⑥', '恶德化装成快活的丑模样', '恶德化装成快感那副丑陋的形状',
     'Vice masqueraded in the ugly shape of pleasure——pleasure 是「快感」，非「快活」'),
    (12, '④', '把等级的抛光敷在她们的手上、脸上', '把等级的抛光敷在他们的手上、脸上',
     'laid the polish of caste upon their hands and faces；上文主语是「他们」（两性），此处突转为「她们」，指代断裂'),
    (17, '①', '「也许他们只能感到我们在。」', '「也许他们只能感到我们在场。」',
     'feel our presence——「感到我们在」不成句'),
    (20, '⑥', '跟着他走过那条湿长的草地', '跟着他走过那条长长的湿草地',
     'the strip of long wet grass——「湿长」生造'),
    (21, '⑥', '「天哪，赫迈厄妮，你真是神人，」', '「天哪，赫迈厄妮，你简直不是凡人，」',
     'By Jove, Hermione, but you\'re divine——divine 是赞其美，译作「神人」易误读为「怪人」'),
    (26, '①', '她望了望四围的树一阵', '她望了望四围的树，好一会儿',
     'looked at the encircling trees a moment——「望了望……一阵」语序破碎'),
    (27, '⑥', '她设法打了个寒噤', '她刻意打了个寒噤',
     'She contrived to shudder——contrived 是「故意做出」，非「设法」'),
    (36, '①', '她好看的脚踝，她推拒的样子恰好证明她练熟了，「你爱的不是我，」',
     '她好看的脚踝；她推拒的样子，恰好证明她练熟了。「你爱的不是我，」',
     '「证明她练熟了」后接引语，逗号连缀成流水句'),
    (40, '①', '她又一顿，猛地一震。', '她话又断了，猛地一惊。',
     'She broke off with another start——「一顿」「一震」重复且不成句'),
    (46, '①', '「别这么会想。我照得住你。」', '「别这么爱幻想。我照得住你。」',
     'Don\'t be so imaginative——「别这么会想」不成话'),
    (55, '⑥', '「那是一步。哦，哦，就在我们旁边。', '「那是脚步声。哦，哦，就在我们旁边。',
     'That was a step——a step 是脚步声，「那是一步」词义误读'),
    (58, '①', '「来了！我又看见了。我确定。有什么从我身边过去了，穿过空气。」',
     '「在那儿！我又看见了。我确定。有什么东西从我身边穿过空气过去了。」',
     'There! I saw it again. Something went past me through the air'),
    (63, '①', '他的想象多么奇，多么没必要的念头！', '他的念头多么富有想象，多么没有必要！',
     'Such imaginative, unnecessary ideas he had——原译主语与谓语失配'),
    (68, '③', '又都是他们医生的绝望。', '又都让他们的医生束手无策。',
     'all were the despair of their doctors——抽象名词主语硬搬'),
    (69, '①', '有一次，沙漠上空来了些飞机，正向本地人炫耀双翼机时，他说，',
     '有一次，几个飞行员驾着双翼机在沙漠上空向本地人炫耀的时候，他说，',
     'the airmen came to astonish the natives with their biplanes over the desert'),
    (73, '⑥', '重力就只是一个育儿室里的把戏', '重力就只是一个哄孩子的把戏',
     'a mere nursery trick——nursery trick 是哄小孩的戏法，非「育儿室里的」'),
    (83, '⑥', '把笑声与掌声扑灭了', '把那一阵阵笑声扑灭了',
     'extinguished the claps of laughter——claps of laughter 是「一阵阵笑声」，非「掌声」'),
    (92, '①', '他既不像呆子，也不像羞愧。', '他既不像呆子，也不显得羞愧。',
     'He looked neither foolish nor abashed——「不像羞愧」搭配不通'),
    (93, '③', '还有一样人不大经验到的东西在他身上', '还有一样人们不常经历的东西在他身上',
     'Another thing, not commonly experienced by men——experience 作动词直搬为「经验到」'),
    (96, '①', '想逃开一只大追鹰', '想逃开一只扑来的大鹰',
     'trying to escape from a great pursuing hawk——「一只大追鹰」不成词'),
    (97, '③', '他是个坚强、安静的人格；', '他是个坚强而沉静的人；',
     'He was a strong, quiet personality——personality 直搬为「人格」'),
    (99, '⑥', '他们说他是个未被发现的宗师', '他们说他是个未被发现的大师',
     'an undiscovered master——master 此处指技艺大师，「宗师」过重'),
    (110, '⑥', '「你也听不见吗？」女孩低声说。', '「你也听见了吗？」女孩低声说。',
     'Do you not hear it, too?——否定反转，原译读反'),
    (121, '①', '因为他所爱的必须在它所崇拜的那里崇拜', '因为他所爱之物，必得在他所崇拜之处敬拜',
     'For what he loved must worship where he worshipped——原译「在……那里」错乱'),
    (123, '①', '他穿过空处落下，被脖子抓住。', '他被抓住脖子，穿过空处落下。',
     'Through empty space he fell, caught by the neck——被动补语悬空'),
    (124, '⑥', '它已是陈史。', '它早已是陈年旧事。',
     'it was already ancient history——「陈史」为硬造词'),
    (125, '⑥', '却找不到相当的表现', '却找不到相称的表现',
     'finds no adequate expression——adequate 是「相称」，非「相当」'),
    (125, '③', '一片田地，让他那胀满的想象的才华能在那里结出果实',
     '一个领域，让他那胀满的想象的才华能在那里结出果实',
     'a field wherein his bursting imaginative genius can produce results——field 直搬为「田地」'),
    (127, '⑥', '也不射它们，也不把它做成标本', '也不射杀它们，也不把它们做成标本',
     'neither keeps them in cages nor shoots them nor stuffs them——单复数混用'),
    (127, '①', '你跟着我吗？还不太懂。', '你明白我的意思吗？怕是不太明白。',
     'You follow me? Not quite.——后半句是医生自道，原译变成对方的话'),
    (131, '①', '她觉得自己站在自身以外某样东西的边上。', '她觉得自己已站到了自己理解之外某样东西的边缘。',
     'She felt upon the edge of things beyond her——「自身以外」误作空间义'),
    (133, '⑥', '「跟才能一样稀有，连伟大的才能都是常见的。', '「其稀有，正如才能——乃至伟大的才能——之常见。',
     'as rare as talent, even great talent, is common——原译把「才能之常见」读成「才能稀有」，比较关系反转'),
    (133, '①', '那么一切对它在那一秒生动的实现里都是可能的。',
     '那么在那一秒生动的实现里，一切对它都是可能的。',
     'all is possible to it--in that second of vivid realisation——状语位置错乱'),
    (148, '②', '肩头颤着一对鸽色的淡色小翅', '肩头扑着一对淡如鸽羽的小翅',
     'a pair of little dove-pale wings fluttering from her shoulders——「鸽色的淡色」叠床架屋'),
    (149, '②', '那些盘桓尼罗河上、成百地在开罗和萧索的莫卡塔姆山上翱翔的大黑鸢',
     '尼罗河上那种大黑鸢——成百只地在开罗和萧索的莫卡塔姆山上空翱翔——',
     'the large black kites that haunt the Nile, soaring in their hundreds over Cairo and the bleak Mokattam Hills——三「的」长定语压没中心语'),
    (151, '③', '一种传心的兴趣到处建立起来。', '一种近乎心灵感应的兴趣到处建立起来。',
     'A kind of telepathic interest——telepathic 直搬为「传心的」'),
    (156, '①', '留下那只鹰，垂头丧气，败下阵来，在旁观者的窃笑中。',
     '留下那只鹰在旁观者的窃笑中垂头丧气，败下阵来。',
     'leaving the Hawk, disconsolate and vanquished, amid the titters of the onlookers——介词短语悬置句末'),
    (159, '③', '混乱抓住了所有舞者的脚。', '混乱绊住了所有舞者的脚步。',
     'Confusion caught the feet of all the dancers——catch the feet 直搬'),
]

with open(PATH, encoding='utf-8', newline='') as f:
    d = json.load(f)
with open(BAK, encoding='utf-8', newline='') as f:
    orig = json.load(f)

assert len(d) == len(orig), (len(d), len(orig))

cnt = 0
by_kind = {}
for i, kind, old, new, note in EDITS:
    assert old in d[i], (i, old)
    assert d[i].count(old) == 1, (i, old)
    assert new.strip(), (i, new)
    d[i] = d[i].replace(old, new)
    assert new in d[i]
    cnt += 1
    by_kind[kind] = by_kind.get(kind, 0) + 1

# 校验：长度、无空段、无 ASCII 直引号、无重复标点、无残留英文
assert len(d) == len(orig)
assert all(s.strip() for s in d)
for i, s in enumerate(d):
    assert '"' not in s, i
    assert not re.search(r'(。。|，，|、、|！！|？？)', s), i
    assert not re.search(r'[\u4e00-\u9fff] +[a-z]+ +[\u4e00-\u9fff]', s), i
    # \n 数量不变（诗行保留）
    assert s.count('\n') == orig[i].count('\n'), i

with open(PATH, 'w', encoding='utf-8', newline='') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write('\n')

print('dn_b: 改动 %d 条, 数组长度 %d (备份 %d)' % (cnt, len(d), len(orig)))
print('分类:', dict(sorted(by_kind.items())))
ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse OK')