# -*- coding: utf-8 -*-
"""v1 chunk054 / chunk055 / chunk075 逐段润色（2026-11-26 轮）。

用法：
    python _polish_20261126_054_075.py --dry   # 只跑断言，不落盘
    python _polish_20261126_054_075.py         # 落盘

铁律：定位唯一子串 -> assert count==1 -> 替换；不整文件重写；
读写用 encoding='utf-8', newline=''；备份已存在则不覆盖。
"""
import ast
import os
import shutil
import sys

BAK = 'final.txt.bak_20261125'
BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    'chunk054': [
        # ① 缺主语的流水句 / 用词： « pensant, prenant mon courage »
        ('又想，既然知道',
         '又想到，既然知道'),
        # ④ 指代不明：这个「他」是被藏在心底的那一个自己
        ('因为另一个勒格朗丹被他小心地藏在心底',
         '因为另一个勒格朗丹被他自己小心地藏在心底'),
        # ② 「的」字堆叠（…的势利眼的种种不光彩的底细）
        ('这一个勒格朗丹掌握着关于我们那个勒格朗丹、关于他的势利眼的种种不光彩的底细',
         '这一个勒格朗丹对我们那个勒格朗丹、对他的势利，掌握着种种不光彩的底细'),
        # ① 悬空：泄露出去的是底细，不是「自我」
        ('我们的朋友只能为自己的另一个自我泄露出去、给人留下坏印象而难过',
         '我们的朋友只能为自己的另一个自我把底细泄露出去、给人留下坏印象而难过'),
        # ① 语法断裂：「理解他想象这番居间的工作」
        ('因为别人没法理解他想象这番居间的工作',
         '因为别人没法理解他的想象所做的这番居间工作'),
    ],
    'chunk055': [
        # ④ 指代不明：前面最近的人物是父亲，此处实为勒格朗丹的姐姐
        ('她仿佛已经看见他姐姐康布雷梅夫人',
         '她仿佛已经看见勒格朗丹的姐姐康布雷梅夫人'),
        # ③ 法语括注被搬到主谓之间，把「日落…是平淡无奇的」割断
        ('有一个柔美迷人的小海湾，奥日地区的日落，那种红金的日落——况且我远不嫌弃它——在那里是平淡无奇的；',
         '有一个柔美迷人的小海湾，奥日地区那样的日落在那里是平淡无奇的，那种红金的日落我远不嫌弃；'),
        # ① 缺主语：「更美」的是「看着满天…」
        ('另一些随即落瓣，那时反而更美：满天撒着无数硫黄色或玫瑰色的花瓣。',
         '另一些随即落瓣，那时看着满天撒着无数硫黄色或玫瑰色的花瓣，反而更美。'),
        # ② 「凡是有…树丛的地方」把定语从句套两层，中间还有逗号
        ('“凡是有受伤而没有屈服、聚拢在一起，以一种动人的执拗共同向一个不怜悯它们的无情天空祈求的树丛的地方，都有我的朋友。”',
         '“哪里有受了伤却没有屈服、聚拢在一起、以一种动人的执拗共同向一个不怜悯它们的无情天空祈求的树丛，哪里就有我的朋友。”'),
        # ① 「需要不觉得」硬拼
        ('万一她需要不觉得在那边是身处异乡',
         '万一她需要让自己在那边不觉得是身处异乡'),
    ],
    'chunk075': [
        # ① 同位语用顿号接不上，且「在…时在脑中」两个「在」打结
        ('这种没有才华、这种在我寻找未来写作题目时在脑中挖出的黑洞',
         '这种没有才华，这种在我寻找未来写作题目时于脑中挖出的黑洞'),
        # ① 「穿着…穿的」重复
        ('上面印着她穿着她当年在莱昂亲王夫人府化装舞会上穿的那套服装。',
         '上面印着她当年在莱昂亲王夫人府化装舞会上穿的那套服装的样子。'),
    ],
}

STAT_KEYS = ('lines', 'paras', 'blank', 'crlf', 'open', 'close', 'ascii_q', 'mark')


def load(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()


def save(p, txt):
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(txt)


def stats(txt):
    norm = txt.replace('\r\n', '\n')
    lines = norm.split('\n')
    return {
        'lines': len(lines),
        'paras': sum(1 for x in lines if x.strip()),
        'blank': sum(1 for x in lines if not x.strip()),
        'crlf': txt.count('\r\n'),
        'open': txt.count('“'),
        'close': txt.count('”'),
        'ascii_q': txt.count('"'),
        'mark': txt.count('⟦'),
        'cjk': sum(1 for ch in txt if '\u4e00' <= ch <= '\u9fff'),
    }


def main():
    dry = '--dry' in sys.argv
    total_edits = total_repl = 0
    for name, edits in EDITS.items():
        d = os.path.join(BASE, name)
        f = os.path.join(d, 'final.txt')
        b = os.path.join(d, BAK)
        txt = load(f)
        before = stats(txt)
        if not dry and not os.path.exists(b):
            shutil.copy2(f, b)
        new = txt
        appl = 0
        for old, rep in edits:
            assert new.count(old) == 1, (name, 'count=%d' % new.count(old), old[:40])
            new = new.replace(old, rep)
            appl += 1
        after = stats(new)
        for k in STAT_KEYS:
            assert before[k] == after[k], (name, k, before[k], after[k])
        assert after['open'] == after['close'], (name, 'quote')
        assert after['ascii_q'] == 0, (name, 'ascii quote')
        print('%s: 段数 %d, 行数 %d, 改动 %d 条, 汉字 %d -> %d, %s'
              % (name, after['paras'], after['lines'], appl,
                 before['cjk'], after['cjk'], 'CRLF' if after['crlf'] else 'LF'))
        if not dry:
            save(f, new)
        total_edits += 1
        total_repl += appl
    print('--- %s: %d 个 chunk，共 %d 处替换'
          % ('DRY' if dry else 'WROTE', total_edits, total_repl))


main()
ast.parse(open(__file__, encoding='utf-8').read())