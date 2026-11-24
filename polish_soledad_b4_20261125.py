# -*- coding: utf-8 -*-
"""《百年孤独》通读润色 第4批（capitulo010）。"""
import ast
import glob
import shutil

ROOT = 'E:/Translate/work_soledad/out'
BAK = '.bak_20261125'

EDITS = [
    ('capitulo010',
     '一个渔夫向邻居借了一块渔网用的铅坠，后来用来报答他的那条鱼肚子里有一颗钻石',
     '一个渔夫向邻居借了一只网坠，后来还他的却是一条肚里含着一颗钻石的鱼',
     '①「后来用来报答他的那条鱼肚子里有……」主谓错位，句子断了'),
    ('capitulo010',
     '穿着那件不合时宜的背心和帽檐如乌鸦翅膀般的帽子',
     '穿着那件不合时宜的背心，戴着帽檐如乌鸦翅膀的帽子',
     '①「穿着……帽子」动宾失配'),
    ('capitulo010',
     '觉得那是流浪汉的乐器，是汉子弗朗西斯科那类人的后裔才摆弄的',
     '觉得那是流浪汉的乐器，是汉子弗朗西斯科那些传人才摆弄的东西',
     '⑥herederos 误作「后裔」，「那类人的后裔才摆弄的」也读不通'),
    ('capitulo010',
     '他的情妇，她的爱有本事激怒自然',
     '他的情妇，她的爱有本事把自然逼得发狂',
     '③exasperar a la naturaleza 直搬作「激怒自然」，中文里没有这个说法'),
    ('capitulo010',
     '可奥雷里亚诺第二被扮成老虎的一时兴起鼓动得兴致勃勃，把安东尼奥·伊莎贝尔神父请到家里',
     '可奥雷里亚诺第二正迷着扮老虎的把戏，兴致勃勃地把安东尼奥·伊莎贝尔神父请到家里',
     '①「被……一时兴起鼓动得兴致勃勃」两个「兴」叠架，主谓绕成一团'),
    ('capitulo010',
     '如此看来，布恩迪亚这个姓氏因美人儿蕾梅黛丝加冕而重现于众所惹起的不安，其实并无实据。',
     '如此看来，布恩迪亚这个姓氏因美人儿蕾梅黛丝加冕而重现于众，所惹起的不安其实并无实据。',
     '②「重现于众所惹起的不安」三个「的」加一个歧义切分，读者会把「众所」读成词'),
]


def main():
    for ch in sorted({e[0] for e in EDITS}):
        files = sorted(glob.glob(f'{ROOT}/{ch}/c*/final.txt'))
        texts = {}
        for f in files:
            with open(f, encoding='utf-8', newline='') as fh:
                texts[f] = fh.read()
        n = 0
        for c, old, new, why in EDITS:
            if c != ch:
                continue
            hits = [f for f, t in texts.items() if old in t]
            cnt = sum(t.count(old) for t in texts.values())
            assert len(hits) == 1 and cnt == 1, f'{ch} 定位失败: {why} | {old!r} n={cnt}'
            f = hits[0]
            texts[f] = texts[f].replace(old, new, 1)
            n += 1
        for f, t in texts.items():
            shutil.copyfile(f, f + BAK)
            with open(f, 'w', encoding='utf-8', newline='') as fh:
                fh.write(t)
        print(f'{ch}: {n} 条')


main()
ast.parse(open(__file__, encoding='utf-8').read())