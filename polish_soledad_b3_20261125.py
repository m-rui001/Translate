# -*- coding: utf-8 -*-
"""《百年孤独》通读润色 第3批（capitulo007-009）。"""
import ast
import glob
import shutil

ROOT = 'E:/Translate/work_soledad/out'
BAK = '.bak_20261125'

EDITS = [
    # ---------------- capitulo007 ----------------
    ('capitulo007',
     '士兵们拼命用枪托砸开泛滥的人群',
     '士兵们拼命用枪托砸开汹涌的人群',
     '⑥muchedumbre desbordada 直搬作「泛滥的人群」，中文不成搭配'),
    ('capitulo007',
     '他就以为死亡一定会以一种明确的、毫不含糊的、不可挽回的信号来宣告',
     '他就以为死亡一定会以一种确凿、决绝、无可挽回的信号来宣告',
     '①「明确的、毫不含糊的」同义叠用，三个「的」并列拖沓'),

    # ---------------- capitulo008 ----------------
    ('capitulo008',
     '时时刻刻、处处地地，将她化作实体',
     '时时刻刻、在在处处，将她化作实体',
     '⑥「处处地地」是错字，「地地」不成词'),
    ('capitulo008',
     '听她说这话的人，也是她头一个拿信给他看的人，乃保守派将军何塞·拉凯尔·蒙卡达',
     '听她说这话的，正是她头一个把信拿给他看的人——保守派将军何塞·拉凯尔·蒙卡达',
     '①「听她说这话的人，也是她头一个拿信给他看的人」两个判断句硬拼'),
    ('capitulo008',
     '他试着对阿玛兰妲用上轻蔑疗法。',
     '他试着对阿玛兰妲用上冷淡疗法。',
     '⑥tratamiento del desprecio 译作「轻蔑疗法」，读者不知是故意冷淡'),
    ('capitulo008',
     '阿玛兰妲被她的猎犬追逼着，这样对他说',
     '阿玛兰妲被他那猛犬般的追逐逼得走投无路，这样对他说',
     '③acosada por sus perros de presa 直搬成「被她的猎犬追逼」，猎犬指谁全乱了'),
    ('capitulo008',
     '庇拉尔·特尔内拉已失掉全部希望的踪迹。',
     '庇拉尔·特尔内拉心里早已没了希望的踪影。',
     '①「失掉全部希望的踪迹」动宾不搭'),
    ('capitulo008',
     '肚子和大腿成了她那无可挽回的众人共享之女人命运的牺牲品',
     '肚子和大腿成了那无可挽回的命数的牺牲品——她命中注定为众人共享',
     '②「她……众人共享之女人命运的牺牲品」三个「的」叠死，中心语被压没'),
    ('capitulo008',
     '一股与脏腑的冷酷脱不了干系的生气，护着他免于即将到来的衰老。',
     '一股生气护着他免于临近的衰老，这生气与他骨子里的冷酷脱不了干系。',
     '②「一股与……脱不了干系的生气」长定语压在句首，读者要等到「生气」才落地'),
    ('capitulo008',
     '跟他们打了这么多仗，想了他们这么多，到头来自己也跟他们一模一样了',
     '跟他们打了这么多仗，琢磨了他们这么久，到头来自己也跟他们一模一样了',
     '①「想了他们这么多」搭配不成话'),

    # ---------------- capitulo009 ----------------
    ('capitulo009',
     '“明白了，奥雷里亚诺，”他在电键上收束道',
     '“明白了，奥雷里亚诺，”他在电键上敲出最后一句',
     '①「在电键上收束道」生造，中文无此说法'),
    ('capitulo009',
     '有人通报他党内一个获准前来讨论战争十字路口的委员会到了时',
     '有人通报他党内一个获准前来讨论战争何去何从的委员会到了时',
     '③discutir la encrucijada de la guerra 直搬作「讨论战争十字路口」'),
    ('capitulo009',
     '硬拖着那头饿死的骡子',
     '硬拖着那头饿得半死的骡子',
     '⑥mula muerta de hambre 是「饿得要死」，译成「饿死的」与「拖着」自相矛盾'),
    ('capitulo009',
     '是加强那支借口保护早已布置在他家门口的卫队，并禁止一切探访',
     '是加强那支早已布置在他家门口、借口保护他的卫队，并禁止一切探访',
     '①状语错位，「借口保护早就布置在」读不出谁保护谁'),
]


def main():
    by_chapter = {}
    for ch, old, new, why in EDITS:
        by_chapter.setdefault(ch, []).append((old, new, why))
    total = 0
    for ch, items in sorted(by_chapter.items()):
        files = sorted(glob.glob(f'{ROOT}/{ch}/c*/final.txt'))
        texts = {}
        for f in files:
            with open(f, encoding='utf-8', newline='') as fh:
                texts[f] = fh.read()
        n = 0
        for old, new, why in items:
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
        total += n
    print('total', total)


main()
ast.parse(open(__file__, encoding='utf-8').read())