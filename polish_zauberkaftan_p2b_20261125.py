# -*- coding: utf-8 -*-
"""zauberkaftan polish p2b (续 p2 剩余条目)"""
import ast, io

BASE = 'work_gutenberg/zauberkaftan/out/'
EDITS = []


def rep(path, old, new, n=1):
    EDITS.append((path, old, new, n))


rep('c006/c00', '邦达，匈牙利皮袄。', '[十一] 邦达，匈牙利皮袄。')   # ⑦ 脚注序号补齐
rep('c006/c00', '于是他把正往外走的几位长老拉住他们的外套下摆',
    '于是他拉住正往外走的几位长老的外套下摆')                          # ① 把字句套宾，动宾失配

rep('c006/c01', '钦娜', '齐娜', 11)                                     # ⑤ Czinna 归一

rep('c006/c02', '利铁咔嚓作响，那一头浓发便剪了下来',
    '锋利的铁刃咔嚓作响，那一头浓发便剪了下来')                        # ③ 「das scharfe Eisen」直搬成不成词的「利铁」

rep('c007/c00', '就在当晚，布达的消息便长了翅膀', '就在当晚，奥芬的消息便长了翅膀')
rep('c007/c00', '只消走到布达的帕夏那里', '只消走到奥芬的帕夏那里')
rep('c007/c00', '若是布达帕夏的心肠硬', '若是奥芬帕夏的心肠硬')
rep('c007/c00', '卡耳加苏丹', '卡尔加苏丹')
rep('c007/c00', '平提厄', '平蒂厄', 2)
rep('c007/c00', '萨穆埃尔·霍莱齐', '塞缪尔·霍莱齐')
rep('c007/c00', '普特诺基一楞', '普特诺基一愣')

rep('c007/c01', '有一队声名狼藉的加尔加苏丹的人马', '有一队声名狼藉的卡尔加苏丹的人马')
rep('c007/c01', '三人执政团把那帕夏的信匆匆看过，便软了下来；他甚至吓得摸了摸自己的脖子',
    '三人执政团把那帕夏的信匆匆看过，便软了下来；普特诺基甚至吓得摸了摸自己的脖子')

rep('c007/c02', '莱斯提亚克', '莱什蒂亚克', 8)
rep('c007/c02', '钦娜', '齐娜', 7)
rep('c007/c02', '从乔拉诺什湖那边', '从查拉诺什湖那边')
rep('c007/c02', '血在血管里气得发滚', '血在血管里沸腾')
rep('c007/c02', '“或许真是这样也说不定；”他搓着额头。',
    '“或许真是这样也说不定，”他搓着额头。')

for path, old, new, n in EDITS:
    f = BASE + path + '/final.txt'
    text = io.open(f, encoding='utf-8', newline='').read()
    cnt = text.count(old)
    assert cnt == n, (f, old, cnt, n)
    io.open(f, 'w', encoding='utf-8', newline='').write(text.replace(old, new))
    print('ok', path, cnt, old[:16], '->', new[:16])

print('total edits:', len(EDITS))
ast.parse(io.open(__file__, encoding='utf-8').read())