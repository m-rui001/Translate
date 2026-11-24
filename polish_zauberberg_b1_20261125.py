# -*- coding: utf-8 -*-
"""《魔山》通读润色 batch1：首尾与专名体例。定位唯一子串 -> 替换 -> 断言命中数。"""
import io, os, ast

BASE = 'E:/Translate/work_zauberberg/out'


def patch(rel, pairs, newline=''):
    path = os.path.join(BASE, rel)
    with io.open(path, 'r', encoding='utf-8-sig', newline=newline) as f:
        text = f.read()
    bang = path + '.bak_20261125'
    if not os.path.exists(bang):
        with io.open(bang, 'w', encoding='utf-8-sig', newline=newline) as f:
            f.write(text)
    n = 0
    for old, new in pairs:
        assert old in text, (rel, old[:40])
        assert text.count(old) == 1, (rel, old[:40], text.count(old))
        text = text.replace(old, new)
        n += 1
    with io.open(path, 'w', encoding='utf-8-sig', newline=newline) as f:
        f.write(text)
    print('patched', rel, n)


# 1) 前言：缺冠词，"这对故事并非不利"
patch('index_split_002/c00/final.txt', [
    ('这对故事并非不利', '这对一个故事并非不利'),
])

# 2) 第一章：德语 aus der ihm zugekehrten Seitentasche，改顺
patch('index_split_003/c01/final.txt', [
    ('从朝着表兄那一侧的乌尔斯特大衣口袋里抽出一半',
     '从靠表兄那一侧的乌尔斯特大衣侧兜里抽出半截'),
])

# 3) 第一章末：Sterilett 全册统一为“灭菌器”（前文已用“灭菌器”，“消毒”已被 Desinfiszieren 占用）
patch('index_split_003/c04/final.txt', [
    ('那显然该是她的“避孕器”', '那显然该是她的“灭菌器”'),
])
patch('index_split_013/c07/final.txt', [
    ('拿着“消毒器”的伊尔蒂斯太太', '拿着“灭菌器”的伊尔蒂斯太太'),
])

# 4) 第四章 X 光：被自己看见这件事（德语 Heftig bewegt von dem, was er sah, oder eigentlich davon, daß er es sah）
patch('index_split_008/c11/final.txt', [
    ('他被自己所看见的，或者说其实是被自己看见了这件事，强烈地搅动，感到自己的心被隐秘的怀疑刺痛',
     '叫他激动不已的，是他看见的东西，或者更确切地说，是他竟然看见了它这件事；他感到自己的心被隐秘的怀疑刺痛'),
])

# 5) “俄国桌”定名统一：以“好的俄国桌 / 坏的俄国桌”为 canon
patch('index_split_012/c04/final.txt', [
    ('好的俄国桌和差的俄国桌都有空缺', '好的俄国桌和坏的俄国桌都有空缺'),
])
patch('index_split_015/c15/final.txt', [
    ('坐在差的俄国桌上', '坐在坏的俄国桌上'),
])
patch('index_split_016/c03/final.txt', [
    ('他坐得离那张上好的俄国桌很近', '他坐得离那张好的俄国桌很近'),
])
patch('index_split_021/c12/final.txt', [
    ('最后他坐到了“劣等俄国桌”旁', '最后他坐到了“坏的俄国桌”旁'),
    ('单是把他调到“劣等俄国桌”这件事本身', '单是把他调到“坏的俄国桌”这件事本身'),
    ('对所谓的“劣等俄国桌”，绝无丝毫贬损之意', '对所谓的“坏的俄国桌”，绝无丝毫贬损之意'),
])
patch('index_split_021/c14/final.txt', [
    ('那是他在“劣等俄国桌”上留起来的', '那是他在“坏的俄国桌”上留起来的'),
    # 结尾两处：悬空分句 + Sturmband 误作“冲锋颏带”
    ('仍能以上千个声音的乌拉迎接胜利——尽管那些因倒下而离散的人。',
     '仍能以上千个声音的乌拉迎接胜利——不去管那些因倒下而离散的人。'),
    ('被冲锋颏带框住的面庞', '被盔带箍住的面庞'),
])

ast.parse(open(__file__, encoding='utf-8').read())
print('OK')