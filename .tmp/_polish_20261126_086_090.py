# -*- coding: utf-8 -*-
"""逐段润色落盘：v3 chunk086-090（2026-11-26 专轮）。

改法：定位唯一子串 → 替换 → assert 命中数 == 1；保持 CRLF 与空行结构不变。
"""
import ast
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

EDITS = {
    'chunk086': [
        # ④ 指代不明：「是(她)头一个领教了那女人的可笑」——两个「她」指不同人
        ('她还是高兴让人知道，是她头一个领教了那女人的可笑',
         '她还是高兴让人知道，那女人的可笑之处，头一个领教的正是她'),
        # ① 悬空比较：比喻句没有落到中心语上，谓语被甩在后面
        ('脸上挂着一丝永不消退的微笑，像微醺的伊弗托善良国王；',
         '脸上挂着伊弗托那位善良国王式的长驻微笑，微微带着醉意；'),
        # ③ 直搬 indistinctement：「一样地握」是副词硬搬
        ('任凭老朋友和介绍给他的陌生人一样地握',
         '任凭老朋友和刚介绍给他的陌生人一视同仁地握'),
        # ① ne...que 直搬成「只有走了」，中文不成话
        ('“好了，我只有走了，”', '“好了，我只得走了，”'),
        # ① plus de fétichisme que de bonheur 的机械照搬＋破折号插在主谓之间
        ('对于阿尔卑斯山那边邻居的那句‘Farà da se’——一切靠自己——学院奉行得与其说尝到了甜头，不如说近于迷信。',
         '学院奉行阿尔卑斯山那边邻居的那句‘Farà da se’——一切靠自己——，与其说是行之有效，不如说近乎迷信。'),
    ],
    'chunk087': [
        # ①「绝望、惊慌得变本加厉」——状语挂错，读不通
        ('便以为可以使那个人绝望、惊慌得变本加厉',
         '便以为可以使那个人更加绝望、更加惊慌'),
    ],
    'chunk088': [
        # ① 逗号流水句：关系从句被拆成并列小句，主语悬空
        ('也许只是觉得发笑的人可爱，她用一种亲昵的目光望着他',
         '也许只是觉得发笑的人可爱，于是用一种亲昵的目光望着他'),
    ],
    'chunk089': [
        # ⑤ Grandin：全库 96 处作「格朗丹」，此处 4 处作「格兰丹」，归一
        ('娘家姓格兰丹', '娘家姓格朗丹'),
        ('他们是格兰丹·德·莱普雷维耶家的人', '他们是格朗丹·德·莱普雷维耶家的人'),
        ('这一家只是格兰丹，什么都不是的格兰丹。', '这一家只是格朗丹，什么都不是的格朗丹。'),
        # ⑥ bovine 误读为「迟钝」，与全段的奶牛戏谑脱钩
        ('她也够迟钝的', '她也颇有几分牛气'),
        # ① on ne voyait chez moi que...：主语错位（名片写成人）
        ('在我家出没的只有‘康布雷梅侯爵先生暨夫人’，地址我记不得',
         '我家里到处只见到‘康布雷梅侯爵先生暨夫人’的字样，地址我记不得'),
    ],
    'chunk090': [
        # ⑤ 同一人同段换形：中校/上校（全册作「皮卡尔上校」）
        ('这两位就是亨利中校和皮卡尔中校。', '这两位就是亨利上校和皮卡尔上校。'),
        # ① concours général 与 baccalauréat 都译成「会考」，读者无法分辨
        ('就像去参加会考或中学毕业会考', '就像去参加全国会考或中学毕业会考'),
    ],
}


def stats(txt):
    norm = txt.replace('\r\n', '\n')
    lines = norm.split('\n')
    paras = [x for x in lines if x.strip()]
    cjk = sum(1 for ch in txt if '\u4e00' <= ch <= '\u9fff')
    return len(lines), len(paras), cjk


def main():
    total = 0
    for chunk, edits in EDITS.items():
        d = os.path.join(BASE, chunk)
        f = os.path.join(d, 'final.txt')
        b = os.path.join(d, BAK)
        if not os.path.exists(b):
            shutil.copy2(f, b)
        with open(f, encoding='utf-8', newline='') as fh:
            text = fh.read()
        l0, p0, c0 = stats(text)
        n = 0
        for old, new in edits:
            assert old in text, f'{chunk}: NOT FOUND {old[:20]}'
            assert text.count(old) == 1, f'{chunk}: NOT UNIQUE {old[:20]} ({text.count(old)})'
            text = text.replace(old, new)
            n += 1
        with open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)
        l1, p1, c1 = stats(text)
        assert (l0, p0) == (l1, p1), f'{chunk}: structure changed {l0},{p0} -> {l1},{p1}'
        print(f'{chunk}: 改动 {n} 条 | 行 {l0}->{l1} | 段 {p0}->{p1} | 汉字 {c0}->{c1}')
        total += n
    print('TOTAL 改动', total, '条')
    return 0


if __name__ == '__main__':
    sys.exit(main())

ast.parse(open(__file__, encoding='utf-8').read())