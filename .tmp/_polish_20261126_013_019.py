# -*- coding: utf-8 -*-
"""润色 v1 chunk013 / chunk017 / chunk019（定位唯一子串 → 替换 → 断言命中数）。

用法：python _polish_20261126_013_019.py [--dry]
红线：段数/行数/空行结构不变；不整文件重写；备份只在缺失时创建。
"""
import ast
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'
DRY = '--dry' in sys.argv

EDITS = {
    'chunk013': [
        # 1 ① ③ 括注（自尊心所执着的那套谎话）被照搬成破折号，横插在主谓之间，
        #        且「我拿……当借口」与「这个谎话总得圆上」两个分句各有主语，句读断裂。
        ('而且全然不顾我的自尊心——我拿“找东西”当借口，还说是她让我找、回头要向她报告结果，'
         '这个谎话总得圆上——她让弗朗索瓦丝过来传话：“没有回话。”',
         '而且全然不顾我的自尊心——我一心要让这套谎话不至于当场戳穿：我说我在找东西，'
         '还说是她让我找的，回头要向她报告结果——她让弗朗索瓦丝过来传话：“没有回话。”'),
        # 2 ⑥ aminci（变薄/变细）被读成「拉长」，à la fois（同时）被读成「一会儿……一会儿」。
        ('把景物一会儿拉长一会儿放大，像一幅一直卷着的画，被人展开。',
         '让景物变得既薄又大，像一幅一直卷着的画，被人展开。'),
        # 3 ① ② 定语层层嵌套（双亲那里能有的／后果最严重的／一桩），中心语被压没。
        ('是双亲那里能有的后果最严重的一桩，其实比一个外人所能设想的还要严重得多',
         '是会让父母给我最严重后果的那一种，其实比一个外人所能设想的还要严重得多'),
    ],
    'chunk017': [
        # 4 ① 「因为那是以……方式，让她觉得可爱」缺主句谓语，读到「因为」后无着落。
        ('也因为那是以我们已经不习惯的方式，让她觉得可爱',
         '也因为那方式我们已不再习惯，才叫她觉得可爱'),
        # 5 ① ② 「一处有哥特式鸽舍或这类古老东西中某一件的产业」定语三层套叠；
        #      「给它以在时间中做不可能旅行的怀念」动宾搭配不成立（donner la nostalgie）。
        ('就像她宁可租一处有哥特式鸽舍或这类古老东西中某一件的产业，这些东西对精神有一种良好影响，'
         '给它以在时间中做不可能旅行的怀念。',
         '就像她宁可租下一处产业，只要那里面有哥特式鸽舍，或者这类古老东西中的一件；'
         '这些东西对精神有一种良好影响，叫它怀念起在时间中不可能实现的旅行。'),
    ],
    'chunk019': [
        # 6 ① 「我把面前清空」缺所属（je fais le vide devant lui＝在他面前把一切清空），
        #      与下句「重新摆到它面前」的「它」接不上。
        ('然后第二次，我把面前清空，把那第一口茶还新鲜的味道重新摆到它面前',
         '然后第二次，我在它面前清空一切，把那第一口茶还新鲜的味道重新摆到它面前'),
        # 7 ① 悬空的「人已经被……压得没了力气」夹在主谓之间，主语从「我」漂到「人」。
        ('很快，我机械地舀了一勺茶送到唇边，茶里泡着一块玛德莱娜小蛋糕，'
         '人已经被阴郁的一天以及对凄凉明日的预期压得没了力气。',
         '很快，我被阴郁的一天以及对凄凉明日的预期压得没了力气，机械地舀了一勺茶送到唇边，'
         '茶里泡着一块玛德莱娜小蛋糕。'),
        # 8 ⑥ se débattre trop loin, trop confusément＝在太远、太混乱的地方挣扎；
        #      「挣扎得太远、太模糊」把处所读成程度。
        ('可是它挣扎得太远、太模糊', '可是它挣扎的地方太远，也太模糊'),
    ],
}


def load(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()


def cjk(t):
    return sum(1 for ch in t if '\u4e00' <= ch <= '\u9fff')


def main():
    total = 0
    for name, edits in EDITS.items():
        d = os.path.join(BASE, name)
        fp = os.path.join(d, 'final.txt')
        bp = os.path.join(d, BAK)
        text = load(fp)
        before_lines = len(text.replace('\r\n', '\n').split('\n'))
        before_paras = len([x for x in text.replace('\r\n', '\n').split('\n') if x.strip()])
        before_cjk = cjk(text)
        eol = 'CRLF' if '\r\n' in text else 'LF'

        n = 0
        for old, new in edits:
            assert old in text, f'{name}: 未命中 {old[:30]}'
            assert text.count(old) == 1, f'{name}: 命中数 != 1 {old[:30]}'
            text = text.replace(old, new)
            n += 1

        after_lines = len(text.replace('\r\n', '\n').split('\n'))
        after_paras = len([x for x in text.replace('\r\n', '\n').split('\n') if x.strip()])
        assert before_lines == after_lines, f'{name}: 行数 {before_lines}->{after_lines}'
        assert before_paras == after_paras, f'{name}: 段数 {before_paras}->{after_paras}'

        print(f'{name}: 改动 {n} 条 | 行 {before_lines}={after_lines} | '
              f'段 {before_paras}={after_paras} | 汉字 {before_cjk}->{cjk(text)} | {eol}')
        total += n

        if DRY:
            continue
        if not os.path.exists(bp):
            shutil.copy2(fp, bp)
            print(f'  备份 -> {BAK}')
        else:
            print(f'  备份已存在，未覆盖')
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        print('  已落盘')

    print(f'合计 {total} 条')


if __name__ == '__main__':
    main()
    ast.parse(open(__file__, encoding='utf-8').read())