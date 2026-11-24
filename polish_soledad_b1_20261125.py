# -*- coding: utf-8 -*-
"""《百年孤独》通读润色 第1批（capitulo001-003）。
定位唯一子串 → 替换 → 断言命中数；落盘后 ast 自查。
"""
import ast
import glob
import shutil
import sys

ROOT = 'E:/Translate/work_soledad/out'
BAK = '.bak_20261125'

EDITS = [
    # ---------------- capitulo001 ----------------
    ('capitulo001',
     '当他熟练掌握了仪器的使用和操作，对空间有了新的认识，不用离开密室就能航行于未知的海洋，造访无人之境，与辉煌的生灵结交。',
     '等他熟练掌握了仪器的使用和操作，便对空间有了新的认识：不用离开密室就能航行于未知的海洋，造访无人之境，与辉煌的生灵结交。',
     '①「当……」状语从句后面没有主句，句子悬空'),
    ('capitulo001',
     '他犯了一场新的坏脾气，不再按时吃饭',
     '他又闹起一阵坏脾气，不再按时吃饭',
     '⑥「犯了一场坏脾气」量词与搭配皆误'),
    ('capitulo001',
     '那是宣告在一座帐篷门口的，据说那帐篷曾属于所罗门王。',
     '那奇迹是在一座帐篷门口宣告的，据说那帐篷曾属于所罗门王。',
     '①「那是宣告在……的」定语悬空，读不通'),
    ('capitulo001',
     '退还了多布隆金币换回放大镜',
     '退还了达布隆金币换回放大镜',
     '⑤doblón 全册两处译名不一（达布隆／多布隆），归一'),
    ('capitulo001',
     '人们花五个雷阿尔',
     '人们花五个里亚尔',
     '⑤real 全册两处译名不一（里亚尔×4／雷阿尔×1），归一'),
    ('capitulo001',
     '和一台吉卜赛人自己按照犹太女子马利亚三臂蒸馏器的现代图样造出的蒸馏器组成',
     '和一台蒸馏器组成，那是吉卜赛人自己照着犹太女子马利亚三臂蒸馏器的现代图样造的',
     '②三个「的」串成长定语，中心语被压没'),
    ('capitulo001',
     '不受时间侵蚀之弊与鸟儿筑巢之习的侵扰',
     '不受时间的侵蚀，也不受鸟儿筑巢的搅扰',
     '⑥vicios del tiempo 误读为「侵蚀之弊」，且「之弊／之习」文白夹生'),

    # ---------------- capitulo002 ----------------
    ('capitulo002',
     '就把一切都告诉了他弟弟',
     '就把一切都告诉了弟弟',
     '④「告诉了他弟弟」易误读为「告诉了 他弟弟」，去「他」'),
    ('capitulo002',
     '昔日的同谋与健谈，如今变得讳莫如深，满怀敌意。',
     '从前那副同谋般的热络，如今变成了讳莫如深和满怀敌意。',
     '①「同谋与健谈」名词与形容词并列作主语，读不通'),
    ('capitulo002',
     '全是些纯粹而简单的尘世附属物，由日常现实的商贩们毫无夸饰地兜售。',
     '全是些普普通通的尘世日用之物，由做日用买卖的商贩不加夸饰地摆出来卖。',
     '③puros y simples 副词短语被硬搬成「纯粹而简单」的定语'),

    # ---------------- capitulo003 ----------------
    ('capitulo003',
     '姐弟俩托付给比西塔西翁',
     '两个孩子托付给比西塔西翁',
     '⑥阿尔卡蒂奥长于阿玛兰妲，「姐弟」辈序颠倒'),
    ('capitulo003',
     '让那副被数月操弄折腾得疲惫不堪的物事歇了下来',
     '让那团被数月操弄折腾得疲惫不堪的物质歇了下来',
     '⑤⑥物质（materia）全册作「物质」，「那副物事」量词与用词皆误'),
    ('capitulo003',
     '他的种种离谱，与阿尔卡蒂奥和阿玛兰妲勉强可比',
     '他这些出格举动，比起阿尔卡蒂奥和阿玛兰妲的也不相上下',
     '⑥「离谱」作名词用，词性失当'),
    ('capitulo003',
     '隔离之有效，终于到了这么一天，紧急状态被视作天经地义',
     '隔离竟如此有效，以致到了这么一天，紧急状态已被视作天经地义',
     '①「隔离之有效」后无谓语，句子断裂'),
    ('capitulo003',
     '他给何塞·阿尔卡蒂奥·布恩迪亚喝下颜色柔和的物事，记忆里便有了光。',
     '他给何塞·阿尔卡蒂奥·布恩迪亚喝下一剂颜色柔和的东西，那人的记忆里便有了光。',
     '④后半句主语跳成「记忆」，读者会错认'),
    ('capitulo003',
     '梅尔基亚德斯则往诺查丹玛斯的预言里越钻越深',
     '梅尔基亚德斯则往诺斯特拉达穆斯的预言里越钻越深',
     '⑤Nostradamus 全册两译（诺斯特拉达穆斯×4／诺查丹玛斯×1），归一'),
    ('capitulo003',
     '他把一家人安顿在雅各布旅馆',
     '他把一家人安顿在雅各旅馆',
     '⑤Hotel de Jacob 全册作「雅各」（×6），「雅各布」×4 归一'),
    ('capitulo003',
     '里正的小女儿蕾梅黛丝的影像',
     '镇长的小女儿蕾梅黛丝的影像',
     '⑤corregidor 全册作「镇长」（×15），「里正」归一'),
    ('capitulo003',
     '这器具的根据，是每天早晨从头到尾把一生所获的全部知识重温一遍',
     '这器具的原理，是每天早晨从头到尾把一生所获的全部知识重温一遍',
     '⑥consistía en 译作「根据」，词义走偏'),
    ('capitulo003',
     '他看见汉子弗朗西斯科像一只独石的变色龙，坐在一圈好奇的人中间',
     '他看见汉子弗朗西斯科像一尊石雕般纹丝不动的变色龙，坐在一圈好奇的人中间',
     '③camaleón monolítico 直搬成「独石的变色龙」，读者不知所云'),
]


def main():
    by_chapter = {}
    for ch, old, new, why in EDITS:
        by_chapter.setdefault(ch, []).append((old, new, why))

    applied = 0
    for ch, items in by_chapter.items():
        files = sorted(glob.glob(f'{ROOT}/{ch}/c*/final.txt'))
        texts = {}
        for f in files:
            with open(f, encoding='utf-8', newline='') as fh:
                texts[f] = fh.read()
        for old, new, why in items:
            hits = [f for f, t in texts.items() if old in t]
            total = sum(t.count(old) for t in texts.values())
            assert len(hits) == 1, f'{ch} 定位失败/不唯一: {why} | {old!r} hits={hits} n={total}'
            f = hits[0]
            texts[f] = texts[f].replace(old, new, 1)
            assert texts[f].count(old) == 0
            applied += 1
        for f, t in texts.items():
            shutil.copyfile(f, f + BAK)
            with open(f, 'w', encoding='utf-8', newline='') as fh:
                fh.write(t)
        print(f'{ch}: {len(items)} 条 -> {len(files)} 文件')
    print('applied', applied)


main()
ast.parse(open(__file__, encoding='utf-8').read())