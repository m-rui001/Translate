# -*- coding: utf-8 -*-
"""逐段润色 v7 chunk124/125/126/127/129（普鲁斯特专轮 2026-11-26）。

只做「定位唯一子串 → 替换 → 断言命中数为 1」，不整文件重写。
用法：python _polish_20261126_v7_124_129.py
"""
import ast
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

EDITS = {
    # ---------------- chunk124 ----------------
    'chunk124': [
        # ⑥ 硬伤：il n'y a pas de fourreurs qui s'y connaissent aussi bien comme les mites
        #   原译读成「没人比蛀虫更懂皮毛商」，主宾颠倒。
        ('说再没有比蛀虫更懂皮毛商的了。',
         '说再没有比蛀虫更识货的皮毛商了。'),
        # ⑦ 体例：bœuf mode 是菜名（布夫·莫德＝焖牛肉），原译无标记，读来像人名。
        ('做那道布夫·莫德的办法',
         '做那道“布夫·莫德”的办法'),
        # ① 读不通：Par une brèche il l'aperçoit —— 主语「他」丢失，成流水句。
        ('忽然从一道缺口望见了湖，它整个呈现在眼前，他拿起画笔。',
         '忽然，他从一道缺口望见了湖，湖整个呈现在眼前，他拿起画笔。'),
        # ① 读不通：定语与中心语被「一种」隔断（d'une tension purement subjective des nerfs）。
        ('并非来自神经一种纯粹主观的紧绷',
         '并非来自神经的一种纯粹主观的紧绷'),
        # ① 读不通：des volontés … qu'ils détruisent … les rendent détestables，主语错置。
        ('有着截然不同意愿的人们，意外根本不知道这些意愿，却将它们摧毁，使意外变得可恨，',
         '另有一些截然不同的意愿，意外对它们一无所知便把它们摧毁，而正是这些意愿使意外显得可恨；'),
        # ⑥ 硬伤：ne pas faire de bruit / 惊醒熟睡的朋友，漏掉一个「不要」，语义反转。
        ('希望不要弄出声响，惊醒熟睡的朋友',
         '希望不要弄出声响、不要惊醒熟睡的朋友'),
    ],
    # ---------------- chunk125 ----------------
    'chunk125': [
        # ① 读不通：si indifférentes —— 死亡本身「无所谓」，不是「令人无动于衷」。
        ('一旦完成却又如此令人无动于衷、如此温柔',
         '一旦完成却又如此无所谓、如此温柔'),
        # ② 「的」字堆叠：dont le coffre-fort crevé eût laissé fuir ses richesses。
        ('使我成了一个囤积者，其被凿破的保险箱会让自己的财富逐渐漏掉。',
         '使我成了一个囤积者，而他的保险箱已被凿破，财富正一点点漏掉。'),
        # ② 「的」字堆叠＋① 悬空：两个「那种害怕……的恐惧」连缀，中心语被压没。
        ('也许，那种害怕自己已经几乎整整走完钟声敲响第一下之前那一分钟、而这一下已经在准备中的恐惧，也许这种害怕那一击正在我脑中发动的恐惧，',
         '也许，那种恐惧——怕自己几乎已经走完钟响第一下之前那整整一分钟，而第一下已在蓄势——也许这种害怕那一下正在我脑中发动的恐惧，'),
    ],
    # ---------------- chunk126 ----------------
    'chunk126': [
        # ⑥ 硬伤：ainsi que des morts récentes ＝「以及新近的死者」，原译误作「同近来死亡一样」。
        ('竟比在席间轻描淡写地谈起的、同近来死亡一样的种种不道德行为还要严重',
         '竟比席间人们轻描淡写地谈起的那些不道德行为、那些新近的死者还要严重'),
        # ⑤ 内部一致：同上段 scrupules 已译「顾虑」，此处 barbares scrupuleux 作「顾虑重重」；
        #    并理顺「谨慎而参加过」的拗口。
        ('正如所有谨慎而参加过城里晚餐的野蛮人一样',
         '正如所有顾虑重重、赴过这种城里晚餐的野蛮人一样'),
        # ⑥ 词义：perception des vérités 是「领悟」，非「感受」。
        ('甚至那些赞同我对那些真理的感受',
         '甚至那些赞同我对那些真理的领悟'),
    ],
    # ---------------- chunk127 ----------------
    'chunk127': [
        # ⑦ 体例/漏字：dans dix ans soi-même，缺一个「的」。
        ('十年以后自己，一百年以后自己的书',
         '十年以后的自己，一百年以后自己的书'),
        # ⑤ 专名：Sheriar 取《一千零一夜》通行汉译「山鲁亚尔」（全册仅此一见，见日志说明）。
        ('比舍里亚尔苏丹更少宽容',
         '比山鲁亚尔苏丹更少宽容'),
        # ① 读不通：marquerait la forme 是「打下／标示出形式」，「凸显出一种形式」主谓不搭。
        ('其性质必定会首先在这部作品中凸显出一种形式',
         '其性质必定会首先在这部作品中标示出那种形式'),
    ],
    # ---------------- chunk129 ----------------
    'chunk129': [
        # ⑥ 词义：point de repère 是「参照点」，非「坐标」。
        ('这个巨大维度中的一个坐标',
         '这个巨大维度中的一个参照点'),
        # ① 词序：仿佛我有几里格高 插在「堆着那么多年月」之前，状语悬空。
        ('我看见在我下方、同时又在我之内，仿佛我有几里格高，堆着那么多年月，不禁一阵眩晕。',
         '我看见在我下方、同时又在我之内堆着那么多年月，仿佛我有几里格高，不禁一阵眩晕。'),
        # ③ 外语句法：括注整块插在「打上印记」之后，且「以如此的力量强加于我」硬搬。
        ('我一定不会忘记给它打上时间的印记——今天这个时间的观念以如此的力量强加于我——',
         '我一定不会忘记给它打上这种时间的印记——今天，时间的观念正是如此有力地压在我身上——'),
        # ① 读不通：au contraire 是「恰恰相反」，原译「相反地」挂在定语里成赘语。
        ('要广大得多，那是一个相反地无限延展的位置，因为',
         '要广大得多；恰恰相反，那是一个无限延展的位置，因为'),
        # ③／⑦ 体例：法文 « … « 是作者插入语标记（同段前文作破折号），原译误作引号，
        #    且 dans le Temps 被关进引号里。
        ('同时触及他们经历过的时代，这些时代彼此相隔那么远，“其间曾有那么多日子在时间中插进来”。',
         '在时间中同时触及他们经历过的那些时代——这些时代彼此相隔如此遥远，其间曾有那么多日子插进来。'),
    ],
}


def stats(txt):
    norm = txt.replace('\r\n', '\n')
    lines = norm.split('\n')
    return (len(lines), sum(1 for x in lines if x.strip()),
            sum(1 for ch in txt if '\u4e00' <= ch <= '\u9fff'))


def main():
    total = 0
    for chunk in ('chunk124', 'chunk125', 'chunk126', 'chunk127', 'chunk129'):
        d = os.path.join(BASE, chunk)
        f = os.path.join(d, 'final.txt')
        b = os.path.join(d, BAK)
        if not os.path.exists(b):
            shutil.copy2(f, b)
            made = 'created'
        else:
            made = 'kept'
        with open(f, encoding='utf-8', newline='') as fh:
            text = fh.read()
        before = stats(text)
        n = 0
        for old, new in EDITS[chunk]:
            assert old in text, (chunk, old)
            assert text.count(old) == 1, (chunk, old, text.count(old))
            text = text.replace(old, new)
            n += 1
        with open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)
        after = stats(text)
        assert before[0] == after[0] and before[1] == after[1], (chunk, before, after)
        print(f'{chunk}: edits {n}, lines {before[0]}->{after[0]}, paras {before[1]}->{after[1]}, '
              f'cjk {before[2]}->{after[2]}, backup {made}')
        total += n
    print('total edits', total)


if __name__ == '__main__':
    main()
    ast.parse(open(__file__, encoding='utf-8').read())
    print('ast self-check OK')
    sys.exit(0)