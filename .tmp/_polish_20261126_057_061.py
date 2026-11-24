# -*- coding: utf-8 -*-
"""逐段润色 v4 chunk057–061（2026-11-26 轮）。
定位唯一子串 → 替换 → assert count==1；不整文件重写；保持 CRLF 与空行结构。
"""
import ast
import io
import os

BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    "chunk057": [
        # ⑥ 硬伤：sa maîtresse 是「乔尔乔内」（贴身女仆）的女主人，不是「他的情妇」
        ("而那封信在“乔尔乔内”看来，本会相当于当晚在韦尔迪兰家与他的情妇共进晚餐。",
         "而那封信在这位“乔尔乔内”眼里，本会相当于当晚在韦尔迪兰家与她的女主人共进晚餐。"),
        # ① 读不通：ce qu'il avait été pour un de leurs neveux 缺中心语
        ("也许是感激他在当西埃尔对他们一个侄子所曾有过的一切",
         "也许是感激他在当西埃尔对他们一个侄子的那份情谊"),
        # ③ ne manqueraient pas de 双重否定机械照搬
        ("而如果这次拜访拖得太久，他们一定不会不来找我，邀请我参加他们的花园聚会。",
         "而如果这次拜访拖得太久，他们一定会找上门来，邀我参加他们的花园聚会。"),
    ],
    "chunk058": [
        # ① 语法断裂：一句里两个「请他」
        ("并且为了更稳妥，请他让他的员工在第一天晚上到我的楼层站岗。",
         "并且为了更稳妥，让他的员工在第一天晚上到我的楼层站岗。"),
    ],
    "chunk059": [
        # ④ 同一指称（l'être）在同句内先「他」后「它」
        ("进入我生命的那个存在，他曾把我还给了我自己，因为他就是我，且大于我",
         "进入我生命的那个存在，它曾把我还给了我自己，因为它就是我，且大于我"),
        # ③ ce n'était qu'à l'instant ... que 强调句照搬，因果与时间错置
        ("而这一切不过是因为——她下葬一年多之后的此刻，由于这种常常妨碍事实的日历与感受的日历相吻合的时间错位——我才刚刚得知她已经去世。",
         "而这一切，只是在此刻——她下葬一年多之后，由于这种常常使事实的日历无法与感受的日历相吻合的时间错位——我才刚刚得知她已经去世。"),
        # ⑥ 生造词「虚在」（état virtuel）
        ("我只以虚在的状态在内心里承载着",
         "我只以潜在的状态在内心里承载着"),
        # ⑥ 语义反转：tout autant que ≠「且不说」
        ("而拿我来说，且不说盖尔芒特这个旧名字，那些更为严重的、关于我外祖母真实回忆的财富，同样不可支配。",
         "而拿我来说，无论盖尔芒特这个旧名字的财富，还是那些更其沉重的、关于我外祖母真实回忆的财富，都同样不可支配。"),
        # ⑤ 术语：intermittences du cœur 全书章节题作「心灵的间歇」
        ("因为与记忆的混乱相联系的是心的间歇性跳动。",
         "因为与记忆的混乱相联系的是心灵的间歇。"),
        # ① 主句与「就紧接在……之后」悬空后置，句序倒错
        ("因此再自然不过的是，不是在当前这一天之后，这个我对此一无所知，而是仿佛时间中存在着不同的、平行的、连续性绝无中断的序列——我立刻贴合到了外祖母向我俯下身来的那一分钟，就紧接在昔日那个第一夜之后。",
         "因此再自然不过的是：我贴合的并不是当前这一天之后——这个我对此一无所知——而是紧接在昔日那个第一夜之后。仿佛时间中存在着不同的、平行的、连续性绝无中断的序列，我径自贴合到了外祖母向我俯下身来的那一分钟。"),
        # ①「紧紧先于此刻」无此搭配
        ("以至于我似乎仍然能听到那些紧紧先于此刻的话语",
         "以至于我似乎仍然能听到那些紧贴在此刻之前的话语"),
        # ① 悬空主语「那个我如果当我是……」一句两主，谓宾断裂
        ("那个我如果当我是那些曾在我内心里相继出现的人中的某一个时，就要设想自己的话，我会遇到同样的困难，就如同现在要我去体验那些我已经，至少一度，不再是的某个人的欲望和愉悦会遇到同样的、而且徒劳的困难。",
         "而如果我正处在那些近来在我内心里相继出现的自我中的某一个，要设想出这个存在，我遇到的困难，会同如今要体会某个我已（至少一时）不再是的人的欲望与愉悦所要费的力气一样大，而且同样徒劳。"),
        # ① 「——，」标点断裂＋两个「它」指代不明（是·的·才 句序纠缠）
        ("因为我是在感受到她第一次活生生地、真实地存在——它胀满我的心，几乎要把它撑破——，在我终于重新找到她的时候，才知道我已经永远失去了她。",
         "因为我是在感受到她第一次活生生地、真实地存在，感受到这份存在胀满我的心、几乎要把它撑破，并在终于重新找到她的时候，才知道我已经永远失去了她。"),
        # ①③「一种虚无」被甩成悬空同位语；certitude de néant 的所属关系丢失
        ("感到它被某种确定性穿过，那确定性像一种反复的身体疼痛一样迫不及待地涌现，一种虚无，这虚无已经从那温柔中抹去了我的影像",
         "感到它被一种确定性贯穿，那确定性像反复发作的身体疼痛一样骤然涌出，是一种虚无的确定性；这虚无已经从那温柔中抹去了我的影像"),
    ],
    "chunk060": [
        # ① 一句里「相称」两次，宾语被压没
        ("这件晨衣恰与她为我所受的劳累相称，那劳累无疑有损健康，却也温存，相称得几乎成了它的象征",
         "这件晨衣恰与她为我所受的劳累相配，那劳累无疑有损健康，却也温存，这晨衣几乎成了这劳累的象征"),
    ],
    "chunk061": [
        # ③ en adressant 表方式，被搬成转折「而」
        ("也不假装外祖母只是不在、只是一时看不见，而对着她的照片",
         "也不假装外祖母只是不在、只是一时看不见，不对着她的照片"),
        # ① 「尊重……原貌，尊重它……原样」同义重复，句子塌陷
        ("还要尊重我的痛苦的原貌，尊重它那不由我做主、骤然袭来时的原样",
         "还要尊重我的痛苦的原貌，即我不由自主、骤然承受它时的原样"),
        # ② 四个「的」串成的长定语
        ("便在神秘地被照亮的、变得半透明的内脏的有机深处",
         "便在内脏那神秘照亮、变得半透明的有机深处"),
        # ⑥ exister pour elle ＝为她而活着
        ("仿佛我还在为她的存在而存在",
         "仿佛我还在为她而活着"),
        # ⑦① 顿号＋「而」误接分句
        ("既怕吵醒她，又怕她若是已经醒了，却听不见我、而她不敢动弹",
         "既怕吵醒她，又怕她若是已经醒了，听不见我，因而不敢动弹"),
    ],
}

HAN = lambda s: sum(1 for c in s if "\u4e00" <= c <= "\u9fff")


def main(dry=False):
    total = 0
    for chunk, edits in EDITS.items():
        path = os.path.join(BASE, chunk, "final.txt")
        with io.open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        nl = "\r\n" if "\r\n" in text else "\n"
        lines_before = text.count(nl)
        han_before = HAN(text)
        for old, new in edits:
            assert old in text, (chunk, "NOT FOUND", old[:30])
            assert text.count(old) == 1, (chunk, "NOT UNIQUE", text.count(old), old[:30])
            text = text.replace(old, new)
        lines_after = text.count(nl)
        assert lines_before == lines_after, (chunk, "LINE COUNT", lines_before, lines_after)
        assert "\n\n\n" not in text and "\r\n\r\n\r\n" not in text, (chunk, "BLANK RUN")
        # 引号成对
        for pair in ("“”", "‘’", "「」"):
            assert text.count(pair[0]) == text.count(pair[1]), (chunk, "QUOTE", pair)
        assert "「" not in text and "」" not in text, (chunk, "JP QUOTE")
        han_after = HAN(text)
        print("%s  edits=%d  lines=%d=%d  han=%d->%d  nl=%s" %
              (chunk, len(edits), lines_before, lines_after, han_before, han_after,
               "CRLF" if nl == "\r\n" else "LF"))
        total += len(edits)
        if not dry:
            bak = path + ".bak_20261125"
            assert not os.path.exists(bak), (chunk, "BAK EXISTS")
            with io.open(path, "rb") as f:
                raw = f.read()
            with io.open(bak, "wb") as f:
                f.write(raw)
            with io.open(path, "w", encoding="utf-8", newline="") as f:
                f.write(text)
    print("total edits:", total)


if __name__ == "__main__":
    import sys
    main(dry="--dry" in sys.argv)

ast.parse(io.open(__file__, encoding="utf-8").read())