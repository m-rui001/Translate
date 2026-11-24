# -*- coding: utf-8 -*-
"""《浮士德》第一部 润色落盘 p5（2026-11-26，续做轮）
覆盖：c00 c01 c04 c05（本轮分配）+ c02 c12 c13 c16（全书「教士」误改回改）
落盘方式：定位唯一子串 -> 替换 -> 断言全文命中数 == 1；行数/空行结构不变。
"""
import io, os, shutil, ast

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work_pub', 'faust', 'out', 'c001')

EDITS = {
    # ---- c00 献词 / 剧场序曲 / 天上序幕 / 夜（诗行，逐行不得并合） ----
    'c00': [
        # 「um schöne Stunden vom Glück getäuscht」＝在美好时光上受了命运的欺弄，原译读成「为换得美好时光」，语义反了
        ('为换得美好时光，已在我面前消逝无踪。',
         '在美好时光上受了命运的欺弄，已在我面前消逝无踪。'),
        # 同句「我一无所有」连说两遍（上一句已说），第二行属衍文
        ('我一无所有却又富足，有对真理的渴求，也有对幻象的乐趣。',
         '有对真理的渴求，也有对幻象的乐趣。'),
    ],
    # ---- c01 剧场序曲收尾 / 天上序幕 / 夜 ----
    'c01': [
        # Gärung＝内心的骚动/翻腾；「发酵催他」中文不成话
        ('发酵催他奔向远方', '内心的骚动催他奔向远方'),
        # des schnellen Laufes Kranz 是竞速之花冠，非「苦战」
        ('若远处有一顶须经苦战方能到达的终点花冠向你招手',
         '若远处那顶竞速的花冠从难以企及的终点向你招手'),
    ],
    # ---- c04 城门前 ----
    'c04': [
        # 说话人标签已有「兵士」一行，段内再冠「士兵们」为重复
        ('士兵们　高墙尖顶的城堡', '高墙尖顶的城堡'),
        # 同一叠句两处异文（报偿/酬报），归一到全书多数「报偿」
        ('冒险是豪壮的，酬报是辉煌的！', '冒险是豪壮的，报偿是辉煌的！'),
        # 「in Breit und Länge」误作「在宽处长处」，中文不成词
        ('又像河水一般，在宽处长处载着那么多欢快的小船，直到沉到吃水线',
         '又像一条河，凭它的宽广绵长漂动着那么多欢快的小舟，直到装载过重快要沉没'),
    ],
    # ---- c05 城门前收尾 / 书斋 ----
    'c05': [
        ('全是驯练出来的把戏', '全是训练出来的把戏'),
        # goldner Duft 是金色香雾，非「金色的香气」（搭配不伦）
        ('从金色的香气中降下来', '从金色的香雾里降下来'),
        # 启示「燃烧得更郑重」搭配失当；würdiger＝更庄严
        ('燃烧得更郑重、更美丽', '燃烧得更庄严、更美丽'),
    ],
    # ---- 全书「教士」回改：Pfarrer 布道语境作牧师 ----
    'c02': [
        ('一个戏子能教一个教士。', '一个戏子能教一个牧师。'),
        ('是的，倘若教士是个戏子', '是的，倘若牧师是个戏子'),
    ],
    # ---- 天主教忏悔/本堂语境：Pfaffe/Pfarrer 作神甫 ----
    'c12': [
        ('她刚打她教士那儿来，教士赦了她一切的罪',
         '她刚打她神甫那儿来，神甫赦了她一切的罪'),
    ],
    'c13': [
        ('竟叫一个教士一把抢了去', '竟叫一个神甫一把抢了去'),
        ('母亲叫了一个教士来', '母亲叫了一个神甫来'),
    ],
    'c16': [
        ('教士也是这么讲的', '神甫也是这么讲的'),
    ],
}

report = []
for ch, edits in EDITS.items():
    d = os.path.join(BASE, ch)
    path = os.path.join(d, 'final.txt')
    text = io.open(path, encoding='utf-8', newline='').read()
    bak = path + '.bak_20261125b'
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    before_lines = text.count('\n')
    before_blank = sum(1 for L in text.split('\n') if L.strip() == '')
    for old, new in edits:
        assert old in text, (ch, old)
        assert text.count(old) == 1, (ch, old, text.count(old))
        text = text.replace(old, new)
    after_lines = text.count('\n')
    after_blank = sum(1 for L in text.split('\n') if L.strip() == '')
    assert before_lines == after_lines, (ch, before_lines, after_lines)
    assert before_blank == after_blank, (ch, before_blank, after_blank)
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    report.append((ch, len(edits)))

print('OK', report)
ast.parse(io.open(__file__, encoding='utf-8').read())