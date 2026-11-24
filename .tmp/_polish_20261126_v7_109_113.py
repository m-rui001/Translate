# -*- coding: utf-8 -*-
"""v7 chunk109 / chunk112 / chunk113 逐段润色落盘脚本（2026-11-26）。

铁律：只做「定位唯一子串 → 替换 → 断言命中数 == 1」，不整文件重写；
读写 newline='' 保持 CRLF；备份 final.txt.bak_20261125 已存在时不覆盖。
"""
import os
import ast

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

EDITS = {
    'chunk109': [
        # ③ 法语括注被搬成破折号，插在连动结构「走到…身边 / 问她」中间
        (
            '德·莫里安瓦尔夫人走到德·圣卢夫人身边——她知道这位夫人很有文学修养，'
            '却没太想起她还承袭了父亲那种机敏而讥诮的心思——问她：“这确实是拉封丹的寓言吧？”',
            '德·莫里安瓦尔夫人素知德·圣卢夫人很有文学修养，'
            '却没太想起她还承袭了父亲那种机敏而讥诮的心思，便走到她身边问道：“这确实是拉封丹的寓言吧？”',
        ),
        # ① 状语缺介词，「一个人身上掠过……之后」悬空
        (
            '听见一个人身上掠过“三十年的舞台生涯”之后加给他的所有东西',
            '听见“三十年的舞台生涯”在一个人身上掠过之后给他添上的所有东西',
        ),
    ],
    'chunk112': [
        # ① 两个「以至于」接排，第二处实为结果，改「因而」
        (
            '她却浑然不觉，以至于她可以假定我不但在她家认识斯万',
            '她却浑然不觉，因而她可以假定我不但在她家认识斯万',
        ),
        # ① 「被遗忘」主语悬空（受「对……来说」结构影响）
        (
            '况且，无论过去多么遥远，对一个像公爵夫人这样有头脑的女人来说，也未必会被遗忘。',
            '况且，过去无论多么遥远，对一个像公爵夫人这样有头脑的女人来说，也未必就会被遗忘。',
        ),
        # ④ 一句里两个「她」，「不会比她更在意」指代崩坏
        (
            '正如公爵夫人倘若知道那个让我进不了她家门的姑娘就是阿尔贝蒂娜，也不会比她更在意。',
            '正如公爵夫人倘若知道那个让我进不了她家门的姑娘就是阿尔贝蒂娜，她对阿尔贝蒂娜也不会更在意。',
        ),
        # ⑥ survivance 是「残存」，非「残存者」
        (
            '这便是残存者最后几副模样，也谈不上令人羡慕。',
            '这便是残存的最后几副模样，也谈不上令人羡慕。',
        ),
    ],
    'chunk113': [
        # ③ 破折号插入语跨在引号内外，把「当……的时候」割断，且破折号悬空
        (
            '比如我的新表亲，”她一边说一边嘲讽地指着盖尔芒特亲王夫人，'
            '而在奥里亚娜看来，这位亲王夫人始终是韦尔迪兰夫人——“本会让她饿死也不屑于听她的时候',
            '比如我的新表亲——”她一边说一边嘲讽地指着盖尔芒特亲王夫人，'
            '而在奥里亚娜看来，这位亲王夫人始终是韦尔迪兰夫人，“本会让她饿死也不屑于听她的时候',
        ),
        # ① 「这在我身上产生的效果」指代含混，改「它」
        (
            '也被这在我身上产生的效果所触动',
            '也被它在我身上产生的效果所触动',
        ),
    ],
}


def han(txt):
    return sum(1 for ch in txt if '\u4e00' <= ch <= '\u9fff')


def main():
    total = 0
    for chunk, pairs in EDITS.items():
        d = os.path.join(BASE, chunk)
        path = os.path.join(d, 'final.txt')
        bak = os.path.join(d, BAK)
        with open(path, encoding='utf-8', newline='') as f:
            text = f.read()

        if not os.path.exists(bak):
            with open(bak, 'w', encoding='utf-8', newline='') as f:
                f.write(text)
            made = '新建'
        else:
            made = '已存在(未覆盖)'

        lines_before = len(text.replace('\r\n', '\n').split('\n'))
        han_before = han(text)
        crlf = text.count('\r\n')

        n = 0
        for old, new in pairs:
            assert old in text, f'{chunk}: 未找到待改子串 -> {old[:30]}'
            assert text.count(old) == 1, f'{chunk}: 待改子串不唯一 -> {old[:30]}'
            text = text.replace(old, new)
            n += 1

        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(text)

        lines_after = len(text.replace('\r\n', '\n').split('\n'))
        assert lines_before == lines_after, f'{chunk}: 行数变了 {lines_before}->{lines_after}'
        assert text.count('\r\n') == crlf, f'{chunk}: 换行符变了'
        total += n
        print(f'{chunk}: 改动 {n} 条 | 行数 {lines_before}->{lines_after} | '
              f'汉字 {han_before}->{han(text)} | CRLF {crlf} | 备份{made}')

    print(f'合计 {total} 条')


main()
ast.parse(open(__file__, encoding='utf-8').read())
print('ast 自查 OK')