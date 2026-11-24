# -*- coding: utf-8 -*-
"""malte 逐片润色（c003/c00 c003/c01 c003/c03 c003/c05 c004/c00）——2026-11-26 批 B。

只用「定位唯一子串 → 替换 → 断言命中数」的改法；不整文件重写，段数/行数/换行符不变。
"""
import ast
import os
import sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')

# (chapter/piece, 类别, 旧串, 新串)
EDITS = [
    # ---- c003/c00 ----
    ('c003/c00', '①',
     '正是这位诗人，是我本也想成为的；',
     '正是这样一位诗人，我本也想成为；'),
    ('c003/c00', '⑥',
     '也说不定他卧房后墙那只大肚子五斗柜里有个抽屉',
     '也说不定他卧房深处那只大肚子五斗柜里有个抽屉'),
    ('c003/c00', '⑥',
     '再有一把靠背椅',
     '再有一把扶手椅'),

    # ---- c003/c01 ----
    ('c003/c01', '⑥',
     '塞纳河街',
     '塞纳街'),
    ('c003/c01', '①',
     '或是卖铜版画的，橱窗里塞得满满当当。',
     '或是卖铜版画的，橱窗里都塞得满满当当。'),
    ('c003/c01', '①',
     '都是极谦卑的人，穿深色制服、挂许多勋章的仆役容他们待着，他们就感恩不尽。',
     '都是极谦卑的人：穿深色制服、挂满勋章的仆役容他们待着，他们就感恩不尽。'),

    # ---- c003/c03（《约伯记》引文）----
    ('c003/c03', '⑤',
     '站在什么庞然大物面前',
     '站在什么巨大的东西面前'),
    ('c003/c03', '⑥',
     '他又像衣领的破口一样束住我',
     '他又像里衣的领口一样束住我'),
    ('c003/c03', '⑥',
     '我的琴变成了哀哭，我的笛变成了哭泣。',
     '我的琴音变成了悲音，我的笛声变成了哭声。'),
    ('c003/c03', '⑥',
     '如今我的灵魂倾覆在我身上',
     '如今我的灵魂倾倒在我身上'),

    # ---- c003/c05 ----
    ('c003/c05', '①②',
     '寂静中一个居高临下的、自得的、我觉得认得的声音说道：',
     '寂静中有个声音说起话来，居高临下，很自得，我觉得自己认得它：'),
    ('c003/c05', '⑥',
     '那边那么暧昧、那么绵软地嘟囔着',
     '那边那么温暖、那么绵软地嘟囔着'),
    ('c003/c05', '①',
     '像流过一个、同一个身体',
     '像流过同一个身体'),
    ('c003/c05', '①',
     '长到我嘴前，长到我最后那只眼睛上，已经笼着它边缘的阴影。',
     '长到我嘴前；在我最后那只眼睛上方，已经笼着它边缘的阴影。'),
    ('c003/c05', '②',
     '顺着一条又一条望不到头的围墙的林荫大道朝一个方向走上去',
     '顺着一条又一条望不到头、夹着高墙的林荫大道朝一个方向走上去'),
    ('c003/c05', '⑦',
     '——：就这样，在我床单上',
     '——就这样，在我床单上'),
    ('c003/c05', '①',
     '屋子里没有一处地方放它够安全',
     '屋子里哪一处放它都不够安全'),
    ('c003/c05', '①',
     '而长大一些，全然没有用。',
     '而长大几岁，全然没有用处。'),
    ('c003/c05', '②',
     '把他们红帆的船放进水里',
     '把他们挂着红帆的小船放进水里'),

    # ---- c004/c00 ----
    ('c004/c00', '⑤',
     '我在万神殿里看见了那位圣女',
     '我在先贤祠里看见了那位圣女'),
    ('c004/c00', '⑥',
     '我在那之前就哭了，不知该怎么好。',
     '我对着这一切哭，不知该怎么好。'),
    ('c004/c00', '①',
     '而且有一些差别在那儿，把我跟人们隔得更开，比此前的一切都更甚。',
     '而且有些差别把我同人们隔开，比此前的一切都隔得更远。'),
    ('c004/c00', '⑥',
     '那在一切存在者之下都有效的存在者',
     '那在一切存在者之中都有效的存在者'),
    ('c004/c00', '⑥',
     '一个人是否担得起自己，躺到那麻风病人身边去',
     '一个人能不能狠下心，躺到那麻风病人身边去'),
    ('c004/c00', '⑥',
     '这事不可能有别的结局，只会是好的。',
     '那不可能不是好的结局。'),
    ('c004/c00', '⑥',
     '你以为福楼拜写他的《圣朱利安》是偶然的吗？',
     '你以为福楼拜写他的《圣朱利安传奇》是偶然的吗？'),
    ('c004/c00', '⑥',
     '可梦把它推回来，把那些纹路描得更深',
     '可梦把睡眠挤开，又把那些纹路描深'),
    ('c004/c00', '①',
     '去试着做一切不可分辨之物沉重的心',
     '去试着成为那一切不可分辨之物沉重的心脏'),
    ('c004/c00', '③',
     '被管状地往上吸进',
     '像顺着细管一样被往上吸进'),
    ('c004/c00', '①',
     '不，你完完全全立在它前面；不是像一道帷幕',
     '可你来了，把那庞然巨物挡在身后，完完全全立在它前面；不像一道帷幕'),
    ('c004/c00', '①④',
     '那被一位神封住了听觉者的面容，好让除了他的声音之外再没有别的音响。',
     '那张脸：一位神封住了他的听觉，好让除了他自己的声音之外，再没有别的音响。'),
    ('c004/c00', '④',
     '他，在它那里有着清明与持久；',
     '他，那些音响的清明与持久就在他里面；'),
    ('c004/c00', '①',
     '我们的降水之上升',
     '我们这些降水的上升'),
    ('c004/c00', '⑥',
     '怕你开始。',
     '怕你弹奏起来。'),
    ('c004/c00', '③',
     '迷信着；',
     '满心迷信；'),
]


def stats(txt):
    norm = txt.replace('\r\n', '\n')
    lines = norm.split('\n')
    paras = [x for x in lines if x.strip()]
    cjk = sum(1 for ch in txt if '\u4e00' <= ch <= '\u9fff')
    return len(lines), len(paras), txt.count('\r\n'), cjk


def main():
    files = {}
    for piece, cat, old, new in EDITS:
        f = os.path.join(BASE, piece, 'final.txt')
        if f not in files:
            with open(f, encoding='utf-8', newline='') as fh:
                files[f] = fh.read()
    changed = {}
    for piece, cat, old, new in EDITS:
        f = os.path.join(BASE, piece, 'final.txt')
        text = files[f]
        assert text.count(old) == 1, (piece, cat, old, text.count(old))
        files[f] = text.replace(old, new)
        changed[piece] = changed.get(piece, 0) + 1
    total = 0
    for f, text in files.items():
        p = os.path.join(os.path.dirname(f))
        bak = os.path.join(p, 'final.txt.bak_20261126')
        assert os.path.exists(bak), 'no backup: ' + bak
        with open(bak, encoding='utf-8', newline='') as fh:
            before = stats(fh.read())
        after = stats(text)
        assert before[0] == after[0], ('lines', f, before, after)
        assert before[1] == after[1], ('paras', f, before, after)
        assert before[2] == after[2], ('crlf', f, before, after)
        with open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)
        total += changed.get(os.path.relpath(p, BASE).replace(os.sep, '/'), 0)
        print('{:10s} lines {}/{} paras {}/{} crlf {}/{} cjk {}->{}  改动 {}'.format(
            os.path.relpath(p, BASE), before[0], after[0], before[1], after[1],
            before[2], after[2], before[3], after[3],
            changed.get(os.path.relpath(p, BASE).replace(os.sep, '/'), 0)))
    print('总改动条目:', len(EDITS), '落盘:', total)


ast.parse(open(__file__, encoding='utf-8').read())

if __name__ == '__main__':
    sys.exit(main())