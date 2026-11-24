# -*- coding: utf-8 -*-
"""《百年孤独》通读润色 第5批（capitulo011-013）。"""
import ast
import glob
import shutil

ROOT = 'E:/Translate/work_soledad/out'
BAK = '.bak_20261125'

EDITS = [
    # ---------------- capitulo011 ----------------
    ('capitulo011',
     '心想那音乐是在外面世上，而她自己却在编扎丧葬棕榈叶的花冠中耗尽',
     '心想那音乐属于外面那个世界，而她自己却要在编扎丧葬棕榈叶的花冠中耗尽',
     '①「那音乐是在外面世上」句子没搭稳，「在」与「是」撞在一起'),
    ('capitulo011',
     '一桩乌尔苏拉向来视为日常起居中最简朴不过的事，如今平添了这般庄严，遂造出一派拘板的气氛',
     '乌尔苏拉向来把吃饭当作日常起居里最简朴不过的事，如今却平添了这般庄严，遂造出一派拘板的气氛',
     '①「一桩……事，如今平添了……气氛」主语带到一半换了说法'),

    # ---------------- capitulo012 ----------------
    ('capitulo012',
     '每逢周三十一点准时抵达',
     '每逢星期三上午十一点准时抵达',
     '⑥「周三十一点」三字连读会切成「周三十·一点」，数字含混'),
    ('capitulo012',
     '充满了如此多的仪式般的动作细节',
     '充满那么多细碎的仪式动作',
     '①「仪式般的动作细节」里「动作」前后重复'),
    ('capitulo012',
     '他们额上的灰烬十字令人心生神圣的敬畏',
     '他们额上的灰十字令人心生神圣的敬畏',
     '⑤cruz de ceniza 全册作「灰十字」，「灰烬十字」仅此二处，归一'),
    ('capitulo012',
     '阿玛兰妲便发觉美人儿蕾梅黛丝因强烈的苍白而变得透明',
     '阿玛兰妲便发觉美人儿蕾梅黛丝苍白得透亮，整个人都变得透明',
     '③「因强烈的苍白而变得透明」是西语句法硬搬，中文里「苍白」不能作「因」的宾语'),
    ('capitulo012',
     '他送给他们几枚铸有自己头像的扣子别在翻领上，又还给他们一面沾满血与火药的脏旗盖棺材',
     '他送来几枚铸有自己头像的扣子，让他们别在翻领上，又把一面沾满血与火药的脏旗还给他们，盖在棺材上',
     '①「送……扣子别在翻领上，又还给……脏旗盖棺材」两个连动杂糅'),

    # ---------------- capitulo013 ----------------
    ('capitulo013',
     '有天夜里，她怀着他在腹中，听见他哭',
     '有天夜里，他还在她腹中，她听见他哭',
     '①「怀着他在腹中」动宾与处所挤在一处，读着绊'),
    ('capitulo013',
     '他死时哭了多少场，才把奄奄一息的奥雷里亚诺·布恩迪亚上校抬回来',
     '他的死又叫人哭了多少场，然后才把奄奄一息的奥雷里亚诺·布恩迪亚上校抬回来',
     '④「他死时哭了多少场」谁哭、哭谁都不明，与上句主语相撞'),
    ('capitulo013',
     '阿玛兰妲仿佛额上顶着童贞的灰烬十字',
     '阿玛兰妲仿佛额上顶着童贞的灰十字',
     '⑤cruz de ceniza 全册作「灰十字」，此处归一'),
    ('capitulo013',
     '佩特拉·科特斯已给他想穿着入殓的那双漆皮短靴打上黑鞋油',
     '佩特拉·科特斯已给他那双准备穿着入殓的漆皮短靴打上黑鞋油',
     '①「已给他想穿着入殓的那双……打上鞋油」定语夹在动宾之间，读不通'),
    ('capitulo013',
     '可压过这庞然体积的，是女性的柔情',
     '可盖过这庞然体积的，是女性的柔情',
     '⑥「压过体积」搭配生硬，「盖过」才通'),
    ('capitulo013',
     '“那畜生！”阿玛兰妲说明道。',
     '“那畜生！”阿玛兰妲解释道。',
     '⑥「说明道」用于此处不成话'),
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