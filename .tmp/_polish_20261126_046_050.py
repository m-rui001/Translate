# -*- coding: utf-8 -*-
"""逐段润色脚本：out_ind/v1 chunk046 / chunk047 / chunk050（2026-11-26 轮）

改法铁律：定位唯一子串 → 断言 count == 1 → 替换 → 落盘（不整文件重写）。
备份：final.txt.bak_20261125（已存在则不覆盖）。
用法：python _polish_20261126_046_050.py [--dry]
结尾 ast.parse 自查。
"""
import ast
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'
DRY = '--dry' in sys.argv

EDITS = {
    'chunk046': [
        # ① 「很觉得少了她就难受」搭配生硬，manquer 的主语关系也含糊
        ('姑妈很觉得少了她就难受',
         '姑妈着实想念她'),
        # ⑥ 「知道」误代「得知」（apprendre），宾语是「我听见的话」
        ('我听见的这些话，她也好，任何人也好，都始终不曾知道。',
         '我听见的这些话，她也好，任何人也好，都始终不曾得知。'),
    ],
    'chunk047': [
        # ⑤ traintrain：046 已定为「小规矩」（原书加了引号的自造称呼），此处归一
        ('我姑妈的生活节奏从不会有任何变化',
         '我姑妈的“小规矩”从不会有任何变化'),
        # ① 「把这……破例的事养得如此之深」不能搭配（prendre l’habitude）
        ('我姑妈把这每周一次破例的事养得如此之深，以至于守着这习惯跟守着别的习惯一样牢。',
         '我姑妈对这每周一次的破例已经习惯得如此之深，以至于守着这习惯跟守着别的习惯一样牢。'),
        # ⑥ 「一桩忘性」量词与词义皆误（cet oubli = 这件忘事）
        ('把这桩忘性讲给我姑妈听',
         '把这桩忘事讲给我姑妈听'),
        # ① 破折号括注后重复「看见钟声经过」，主句被割断（en voyant passer…, tout le monde répondait）
        ('——这时看见圣伊莱尔钟楼的两响钟声经过（这两下钟声惯于',
         '——就在他望着圣伊莱尔钟楼的两响钟声经过（这两下钟声惯于'),
        ('）——看见钟声经过，大家就齐声回他：',
         '）的时候，大家就齐声回他：'),
        # ⑤ grand’tante：全册 35 处「姑祖母」，此处孤例「姨祖母」
        ('连我姨祖母也放下手里的活计',
         '连我姑祖母也放下手里的活计'),
    ],
    'chunk050': [
        # ① ce n’est pas que… que… 双重否定叠成死结，读不出肯定意
        ('然而也并非她有时不渴望更大的变动，不也有那样一些例外的时候：',
         '然而这也并非说她有时就不渴望更大的变动，也不是说她没有过那样一些例外的时候：'),
        # ① 「这消息发生在她……的时候」主谓失配（survenant à un moment où elle se sentait bien,
        #    la nouvelle que… a dû hanter ses espérances）：把时间从句退回状语位置
        ('要是这消息发生在她身子舒坦、没有出汗的时候：听说房子成了大火的猎物',
         '听说房子成了大火的猎物'),
        ('逃出来——这样的消息想必常常萦绕于她的希望之中',
         '逃出来——这样的消息要是正好发生在她身子舒坦、没有出汗的时候，想必常常萦绕于她的希望之中'),
        # ⑥ l’eût désespérée 是条件式「会叫她绝望」，原文并非已然的过去
        ('东西一出现，她早就受不了了）',
         '东西一出现，她准会受不了的）'),
        # ① 「把一种变动一劳永逸地做出来」（accomplir un de ces changements）动词搭配不成
        ('这场灾变会逼她把一种变动一劳永逸地做出来',
         '这场灾变会逼她一劳永逸地完成一种变动'),
        # ⑥ 「又想着怎么瞒住她」主语倒置：瞒人的是弗朗索瓦丝（chercher à lui cacher）
        ('只想着时时刻刻猜出弗朗索瓦丝可能做什么，又想着怎么瞒住她。',
         '只想着时时刻刻猜出弗朗索瓦丝可能做什么、又想瞒着她什么。'),
        # ③ attachait à… une attention 直搬成「把……放在一种注意里」
        ('弗朗索瓦丝越来越把姑妈最细微的话、最细微的动作，都放在一种非同寻常的注意里。',
         '弗朗索瓦丝越来越对姑妈最细微的话、最细微的动作，都抱着一种非同寻常的注意。'),
        # ④ 一句里三个「她」分指两人
        ('竭力从她脸上的神情猜出她想了什么、会怎么决定。',
         '竭力从姑妈脸上的神情猜出她想了什么、会怎么决定。'),
        # ⑥ feu de paille（稻草火／昙花一现）被拆成「稻草点的一把火」
        ('只是稻草点的一把火，很快就灭了',
         '只是一把稻草火，很快就灭了'),
        # ① voyait… prendre 的「看见」丢了，全句比喻的对照（艺术家／老妇人）落空
        ('却从没想过路易十四，就把自己一天里最无关紧要的事',
         '却从没想过路易十四，就看见自己一天里最无关紧要的事'),
        # ① 「就像……时的样子」悬空，且 aussi… que 的「同样」未落
        ('在弗朗索瓦丝方面，正是热烈而又畏怯地议论的对象，就像国王的沉默、好脾气和高傲，'
         '在某个廷臣甚至最显赫的爵爷在小径拐弯处向他递上呈文时的样子。',
         '在弗朗索瓦丝这一边，也正是热烈而又畏怯地议论的对象，正如国王的沉默、好脾气和高傲，'
         '在某个廷臣甚至最显赫的爵爷于小径拐弯处向他递上呈文时一样。'),
    ],
}


def cjk(s):
    return sum(1 for ch in s if '\u4e00' <= ch <= '\u9fff')


def main():
    report = []
    for chunk, pairs in EDITS.items():
        d = os.path.join(BASE, chunk)
        f = os.path.join(d, 'final.txt')
        with open(f, encoding='utf-8', newline='') as fh:
            text = fh.read()
        before = text
        n_before_lines = len(text.replace('\r\n', '\n').split('\n'))
        n_before_cjk = cjk(text)

        for old, new in pairs:
            assert old in text, (chunk, 'NOT FOUND', old)
            assert text.count(old) == 1, (chunk, 'NOT UNIQUE', old, text.count(old))
            text = text.replace(old, new, 1)

        n_lines = len(text.replace('\r\n', '\n').split('\n'))
        n_paras_before = len([x for x in before.replace('\r\n', '\n').split('\n') if x.strip()])
        n_paras = len([x for x in text.replace('\r\n', '\n').split('\n') if x.strip()])
        assert n_lines == n_before_lines, (chunk, 'lines changed')
        assert n_paras == n_paras_before, (chunk, 'paras changed')
        assert text.count('“') == text.count('”'), (chunk, 'quotes')
        assert '"' not in text, (chunk, 'ascii quote')
        assert text.count('⟦') == before.count('⟦'), (chunk, '⟦')

        report.append((chunk, len(pairs), n_before_lines, n_lines,
                       n_before_cjk, cjk(text), text.count('\r\n')))

        if DRY:
            continue
        bak = os.path.join(d, BAK)
        if os.path.exists(bak):
            print(f'{chunk}: 备份已存在，未覆盖')
        else:
            shutil.copy2(f, bak)
            print(f'{chunk}: 备份 -> {BAK} ({os.path.getsize(bak)}B)')
        with open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)
        print(f'{chunk}: 落盘 OK')

    print('chunk | 改动 | 行数 | 汉字 | CRLF')
    for r in report:
        print(f'{r[0]} | {r[1]} | {r[2]}->{r[3]} | {r[4]}->{r[5]} | {r[6]}')
    print('DRY' if DRY else '已落盘')


main()
ast.parse(open(__file__, encoding='utf-8').read())