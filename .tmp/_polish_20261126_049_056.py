# -*- coding: utf-8 -*-
"""v3 chunk049/050/052/053/056 逐段润色落盘脚本（2026-11-26 轮）。

准则：E:/Translate/POLISH_BRIEF_2026-11-25.md
落盘方式：定位唯一子串 → 替换 → assert count==1，绝不整文件重写。
备份：final.txt.bak_20261125（已存在则跳过，不覆盖）。
"""
import ast
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

EDITS = {
    'chunk049': [
        # ①/③ 法文括注 (pour ma grand'mère c'était Paris) 被搬成逗号夹在定语链里，
        # 读者会把「外祖母」误当成主句主语；改回括注，与全册 53 处括注体例一致。
        ('而那个人原本还坐在他所居住的城市里，外祖母住在巴黎，坐在自己的桌旁，',
         '而那个人原本还坐在他所居住的城市里（对外祖母来说，那城市就是巴黎），坐在自己的桌旁，'),
    ],
    'chunk050': [
        # ② 一句里五个「的」，中心语「东西」被压到句尾；改动词句，让「抵消」直接作谓语。
        ('平日里她时时刻刻对我下的命令、禁令，服从时的厌烦，反抗时的焦躁，'
         '这些曾抵消了我对她的温情的东西，此刻全消失了',
         '平日里她时时刻刻对我下的命令和禁令、我服从时的厌烦、反抗时的焦躁，'
         '这些原本抵消了我对她的温情，此刻全消失了'),
        # ⑥ effet direct d'un autre isolement 译作「回响着另一种孤独」是误读（且一句两「回响」）；
        # ① 「`Non pas ; mais plutôt que`」不是「与其说A不如说B」的对举。
        ('不，与其说是声音，不如说这孤独的声音只是一个象征、一种唤起、一个直接的回响，'
         '回响着另一种孤独，我祖母的孤独，她第一次和我分开了。',
         '不；更确切地说，声音的这种孤立本身就像是一个象征、一种召唤，是另一种孤独的直接结果，'
         '那另一种孤独就是我祖母的孤独，她第一次和我分开了。'),
        # ① 「le jeune prince amateur de peinture impressionniste et chauffeur」＝亲王兼司机，
        # 「年轻亲王司机」四字连写读作职衔；补「兼」。
        ('那位爱好印象派绘画的年轻亲王司机——博罗迪诺上尉的侄子——',
         '那位爱好印象派绘画的年轻亲王兼司机——博罗迪诺上尉的侄子——'),
    ],
    'chunk052': [
        # ① 照搬 qu'on surprend ... qu'elle cachera si on entre，成了「已被人撞见」又要「一旦有人进来便藏」，
        # 自相矛盾；还原为「正做着活计、一有人进来便会藏起来的女人」。
        ('就像一个被人撞见正在做一件活计的女人，一旦有人进来便会把它藏起来，',
         '就像一个正做着活计、一有人进来便会把它藏起来的女人，'),
        # ⑥ `ne ... que` 误读：「我们从来不会在……中看见所爱的人」把限定句读成了否定句。
        ('我们从来不会在活生生的系统里、在我们不间歇的温情的永恒运动中看见所爱的人',
         '我们从来都只在活生生的系统里、在我们不间歇的温情的永恒运动中看见所爱的人'),
        # ① 同位语链里夹一个悬空的「戴着旅行帽、穿着旅行外套」，不知修饰谁；并入「陌生人」一项。
        ('那里只有证人、观察者，戴着旅行帽、穿着旅行外套，那个不属于这个家的陌生人',
         '那里只有证人、观察者，那个戴着旅行帽、穿着旅行外套、不属于这个家的陌生人'),
        # ① 宾语「那些动作」前置后，「我们想要让他……执行」缺「把」，主谓断裂；去掉重复的「我们」「的」。
        ('而当我们在精神里让另一个人反复做过的那些动作——那些使他按我们意愿行事的动作——'
         '我们想要让他在生活中真正执行时',
         '而当我们在精神里让另一个人反复做过那些动作——那些使他按我们意愿行事的动作——'
         '想要他在生活中真正执行时'),
        # ①「厌恶」一句出现两次，后一句悬空（那男人爱她，他让她感到……厌恶）；并为一句带同位语。
        ('无疑是一个不爱某个男人的女人身上所能生出的厌恶，那男人爱她，'
         '他让她感到无法忍受的、令人作呕的厌恶：',
         '无疑是一个不爱某个男人的女人身上所能生出的厌恶——爱她的那个男人让她感到的、'
         '无法忍受而又令人作呕的厌恶：'),
    ],
    'chunk053': [
        # ③ `sans même avoir reconnu` 是伴随状态，被搬成了让步句「尽管」；改并列。
        ('来陪伴我在内心倾听的这位音乐家，尽管我甚至没有立刻认出他弹的是什么。',
         '来陪伴这位我在内心倾听的音乐家，而我甚至还没有立刻认出他弹的是什么。'),
        # ① `n'en eusse pas moins manqué de me promener`＝我照样会去散步；「不会不在」三重否定读来绊人。
        ('我也照样不会不在这个时候出去散步',
         '我也照样会在这个时候出去散步'),
        # ① `ce qu'elle eût retrouvé, c'était elle` 被搬成条件句「她若重新找到什么」；还原为关系句。
        ('而她在我的心里恼怒地感到，她若重新找到什么，找到的恰恰是她自己。',
         '而她在我的心里恼怒地感到，她能重新找到的，恰恰是她自己。'),
        # ① 「看见的走路、打开阳伞、穿过街道的女人」缺介词，动词短语直接做定语读不通；补「在」。
        ('那个我从远处看见的走路、打开阳伞、穿过街道的女人',
         '那个我从远处看见在走路、打开阳伞、穿过街道的女人'),
        # ③ `avec la même curiosité que ...` 后置成「那种好奇，正如……」悬在句末；改为状语前置意。
        ('我看着她扶正手笼，向一个穷人施舍，从一个女商贩那里买一束紫罗兰，'
         '那种好奇，正如我看一位大画家挥笔作画时会有的好奇。',
         '我看着她扶正手笼，向一个穷人施舍，从一个女商贩那里买一束紫罗兰，'
         '带着我看一位大画家挥笔作画时才会有的那种好奇。'),
        # ⑥ `la claustration que la violence de la couleur mettait autour d'elle et le reste du monde`
        # ＝在她以及其余世界四周罩上的幽闭，不是「在她和其余世界之间」的隔绝。
        ('因为那种强烈的色彩在她和其余世界之间造成的仿佛幽闭般的隔绝',
         '因为那种强烈的色彩在她周围以及其余世界周围造成的仿佛幽闭般的隔绝'),
    ],
    'chunk056': [
        # ⑥ `avait-il été impressionné` 是「深为震动」，译作「耿耿于怀」把震动读成了记恨。
        ('父亲看在眼里，怎能不耿耿于怀？',
         '父亲当时不由得心里一沉。'),
    ],
}


def load(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()


def save(p, s):
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(s)


def stats(t):
    lines = t.replace('\r\n', '\n').split('\n')
    return len(lines), sum(1 for x in lines if x.strip()), sum(1 for ch in t if '\u4e00' <= ch <= '\u9fff')


def main(dry=False):
    total = 0
    for chunk, edits in sorted(EDITS.items()):
        d = os.path.join(BASE, chunk)
        fp = os.path.join(d, 'final.txt')
        bp = os.path.join(d, BAK)
        text = load(fp)
        before = stats(text)
        if not dry and not os.path.exists(bp):
            shutil.copy2(fp, bp)
        for old, new in edits:
            assert text.count(old) == 1, (chunk, old[:30], text.count(old))
            text = text.replace(old, new)
        after = stats(text)
        assert before[0] == after[0] and before[1] == after[1], (chunk, before, after)
        if not dry:
            save(fp, text)
        total += len(edits)
        print('%-9s 改动 %d 条 | 行数 %d=%d 段数 %d=%d | 汉字 %d->%d | 换行 %s'
              % (chunk, len(edits), before[0], after[0], before[1], after[1],
                 before[2], after[2], 'CRLF' if '\r\n' in text else 'LF'))
    print('合计 %d 条%s' % (total, '（dry-run，未落盘）' if dry else ''))


if __name__ == '__main__':
    import sys
    main(dry='--dry' in sys.argv)
    ast.parse(open(__file__, encoding='utf-8').read())