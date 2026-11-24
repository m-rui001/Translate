# -*- coding: utf-8 -*-
"""逐段润色 v1 chunk031 / chunk035 / chunk039（2026-11-26 轮）。

只做「定位唯一子串 → 替换 → 断言命中数」的改法；不改段数、行数、空行结构与换行符。
"""
import ast
import io
import os

BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    'chunk031': [
        # ⑥ 词义误读：se représenter 是「想象」，不是「描绘」；兼解②「的」字连缀
        ('我把自己想象的在剧院里尝到的乐趣描绘得那么不准确，以至于',
         '我把人们在剧院里尝到的乐趣想象得那么不准确，以至于'),
        # ① 读不通：「我和同学们谈起的话」缺谓语中心
        ('我和同学们谈起的话，全都离不开那些演员。',
         '我和同学们谈话，话题总离不开那些演员。'),
        # ③ 外语句法直搬：关系从句「la première forme … sous laquelle se laissait pressentir par moi, l'Art」
        #    被拆成两个并列谓语、且后一半把意思读成了「艺术全部形式中的第一种」
        ('他们的艺术我虽然还不了解，却是一切艺术得以被我预感到的第一种形式，'
         '是艺术所采取的全部形式中的第一种。',
         '他们的艺术我虽然还不了解，却是艺术所采取的一切形式中，'
         '让我最先预感什么是艺术的那一种形式。'),
    ],
    'chunk035': [
        # ③ 法文括注（dans notre salle d'études）被照搬成破折号，插在主谓与宾语之间
        ('我却始终无法从端详它们当中得到任何乐趣——那是在我们的自习室里，'
         '墙上挂着他给我带回来的这些画的复制品。',
         '我却始终无法从端详这些人物当中得到任何乐趣——这些复制品就挂在我们自习室的墙上，'
         '是他给我带回来的。'),
        # ⑥ mesquinement régulier：「小气、寒酸」，不是「吝啬」
        ('五官规整得近乎吝啬', '五官规整得近乎小家子气'),
        # ②③ 「……的方式」「……的东西」「……的含义」三层定语压住中心语；关系从句硬搬
        ('而它被表现的方式不是作为象征——因为被象征的思想并未表达出来——'
         '而是作为真实的东西，当作确实承受着或物质地被摆弄着的东西，这一事实使作品的含义更字面、更精确',
         '而它之被表现，不是作为象征——因为被象征的思想并未表达出来——'
         '而是作为真实之物，当作确实承受着的、或实实在在被摆弄着的东西：这一事实使作品的含义更字面、更精确'),
        # ⑥ 漏译 pressé（匆忙的）：神气与身份的关系也理顺
        ('他们通常有一副轻快、务实、漠然而生硬的外科医生的神气',
         '他们通常都有一种轻快、务实、漠然而生硬的神气，像个匆匆忙忙的外科医生'),
        # ② 「我的休息由于书中讲述的、前来扰动它的那些奇遇」三个「的」，中心语被压没
        ('我的休息由于书中讲述的、前来扰动它的那些奇遇，像一只不动的手伸在流水之中，'
         '承受着一股奔涌的活力的冲击与激荡。',
         '我的休息被书中讲述的奇遇搅动着，却像流水中间一只不动的手，'
         '承受着一股活动之流的冲击与荡漾。'),
    ],
    'chunk039': [
        # ② 「时间-那种-约定俗成-的划分-的左右」两层「的」
        ('也不受时间那种约定俗成的划分的左右',
         '也不受时间那套约定俗成的划分所左右'),
        # ① 主谓错位：「他们替我物色的伙伴，宁可不要布洛克」
        ('他们替我物色的伙伴，宁可不要布洛克这样的人：',
         '他们宁可给我找些别的伙伴，而不是布洛克：'),
        # ⑥ pencher la balance＝让天平倾斜，「压天平」不成话
        ('就把义务与友谊要求的那架公正的天平往我这边压',
         '就让义务与友谊那架公正的天平朝我这边倾斜'),
        # ⑥ plus proche parente＝最亲的亲属，「最近」误作距离
        ('因为那是她最近的亲属', '因为那是她最亲的亲属'),
        # ④/① 「他们应尽的那一份」指代含糊（应为「欠我们、该给我们的那一份」）
        ('连我们的过错都很难让这些人放弃他们应尽的那一份',
         '即便我们有什么过错，也很难让这类人少给我们该得的那一份'),
        # ①「那些关于……那种毫无意义的美所生的无解难题」名词串读不通
        ('我脑子里那些关于弥诺斯与帕西法厄之女那种毫无意义的美所生的无解难题，比起跟他再谈几次话来，',
         '我为弥诺斯与帕西法厄之女那毫无意义的美给自己出的那些无解难题，比起跟他再谈几次话来，'),
        # ①③ 比较状语（comme un air de musique…）被搬到句首，与主句错接
        ('就像一段日后会让人着迷、当时却还分辨不清的旋律，我本该那么喜爱的那种文笔，'
         '并没有在我眼前显现出来。',
         '我在他文笔里本该那么喜爱的东西，并没有显现出来，'
         '就像一段日后会让人着迷、当时却还分辨不清的旋律。'),
        # ⑥ 漏译 flot（流）：un flot caché d'harmonie
        ('那时有一股隐藏的和谐、一段内心的序曲',
         '那时有一股隐秘的和谐之流、一段内心的序曲'),
    ],
}


def han(s):
    return sum(1 for ch in s if '\u4e00' <= ch <= '\u9fff')


def main():
    report = []
    for chunk, edits in EDITS.items():
        path = os.path.join(BASE, chunk, 'final.txt')
        with open(path, encoding='utf-8', newline='') as f:
            text = f.read()
        crlf = '\r\n' in text
        lines_before = len(text.split('\r\n')) if crlf else len(text.split('\n'))
        han_before = han(text)
        n = 0
        for old, new in edits:
            assert old in text, (chunk, old[:20])
            assert text.count(old) == 1, (chunk, 'not unique', old[:20])
            assert old != new
            text = text.replace(old, new)
            n += 1
        lines_after = len(text.split('\r\n')) if crlf else len(text.split('\n'))
        han_after = han(text)
        assert lines_before == lines_after, (chunk, lines_before, lines_after)
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        report.append((chunk, lines_before, lines_after, han_before, han_after, n,
                       'CRLF' if crlf else 'LF'))
    for r in report:
        print('%-9s 行 %d→%d  汉字 %d→%d  改动 %d  换行 %s' % r)


main()
ast.parse(open(__file__, encoding='utf-8').read())