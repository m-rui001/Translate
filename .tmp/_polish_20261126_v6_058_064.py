# -*- coding: utf-8 -*-
"""v6 chunk058/061/063/064 逐段润色落盘脚本（2026-11-26）。

只做「定位唯一子串 → 替换 → 断言命中数」的改法；不整文件重写。
读写用 encoding='utf-8', newline='' 以保持 CRLF。
"""
import ast
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    "058": [
        # ③ 法语括注被搬成破折号，插在「跟瓦兹农……也很相熟」中间，把宾语割断
        ("跟瓦兹农——也就是盖尔芒特亲王的城堡——也很相熟",
         "跟瓦兹农也很相熟——那是盖尔芒特亲王的城堡"),
        # ④ 一句里「她」「他」分指吉尔贝特与父亲，改出「父亲」
        ("借这些典型特征为她把他“定位”出来",
         "借这些典型特征替她把父亲“定位”出来"),
        # ④ 「他的画」「她的一个表姐妹」两个代词分指埃尔斯蒂尔与公爵夫人
        ("自己曾把那么多他的画送给她的一个表姐妹",
         "自己曾把那么多他的画送给自己的一个表姐妹"),
    ],
    "061": [
        # ①③ 「影响在吉尔贝特身上，对……起的作用」主谓错位（法语 se fût exercée pour Gilberte sur …）
        ("而且我想，尽管距离近得多，当松维尔那种迷人的影响在吉尔贝特身上，对萨泽拉夫人或古皮尔夫人起的作用，恐怕还不如对阿格里让特先生大。",
         "而且我想，尽管萨泽拉夫人和古皮尔夫人住得近得多，当松维尔那种迷人影响在吉尔贝特身上起的作用，恐怕对她们还是不如对阿格里让特先生大。"),
        # ⑥ 引语断句误读：des métaphores comme dans la prose démodée de Chateaubriand
        ("里面有“夸张，有隐喻，像夏多布里昂过时的散文”",
         "里面有“夸张，有像夏多布里昂过时散文那样的隐喻”"),
        # ① 「声音悲伤地回答」状语倒装不成句
        ("但我声音悲伤地回答", "但我用悲伤的声音回答"),
        # ① 「然而，尽管如此」双重转折冗余（mais pourtant）
        ("然而，尽管如此，这是第一次", "但尽管如此，这是第一次"),
        # ① 「像压缩机抬起一样」主语缺位，读者不知所云（comme un compresseur se soulève）
        ("像压缩机抬起一样", "像压缩机的压板抬起来一样"),
        # ⑥ Pour me consoler de son silence 误读为「排遣他的沉默」
        ("为了排遣他的沉默", "为了宽解自己因他沉默而生的不快"),
        # ③ par un choc en retour 直搬成「作为反冲」
        ("后来也应当向我承认，不过是作为反冲。",
         "后来也应当向我承认，只不过是被反弹回来的。"),
    ],
    "063": [
        # ③ 「承受没有阿尔贝蒂娜而生活」= supporter de vivre sans Albertine 直搬
        ("那个能够轻松承受没有阿尔贝蒂娜而生活的新存在",
         "那个能够轻松承受没有阿尔贝蒂娜的生活的新存在"),
        # ① 「随着遗忘带给我几乎完全的痛苦消除」句子断裂（apportait avec l'oubli une suppression …）
        ("随着遗忘带给我几乎完全的痛苦消除、一种安适的可能性",
         "给我带来了遗忘，带来了痛苦的几乎完全消除，也带来了一种安适的可能"),
        # ① 破折号括注把主句「并在……的惊叹中」割成悬空
        ("我们惊讶于再也找不到它，并在自己已变成另一个人的惊叹中——对这个另一个人来说，其前身的痛苦不过是别人的痛苦，是我们可以怀着怜悯谈论、因为我们并不感受到的痛苦。",
         "我们惊讶于再也找不到它，并惊叹自己已经变成另一个人——对这个人来说，前身的痛苦不过是别人的痛苦，是我们可以怀着怜悯谈论、因为自己并不感受到的痛苦。"),
        # ① 「噩梦在夜里是可怕的，这也并非不可能」语序拗折
        ("同样，我们的噩梦在夜里是可怕的，这也并非不可能。",
         "同样，我们夜里的噩梦也许真是可怕的。"),
        # ②③ 「爱起初曾有的、如今又重新具有的集体性」的字压住中心语
        ("这是由于我对小团体里那群少女的爱起初曾有的、如今又重新具有的集体性——",
         "因为我对小团体里那群少女的爱，起初带有一种集体性，如今这种集体性又回来了——"),
        # ⑦ 「巴黎她的表姐家」多余「的」
        ("只在巴黎她的表姐家待几个星期", "只在巴黎她表姐家待几个星期"),
        # ①③ 「关于你的事」悬空（qui m'a beaucoup parlé de toi）＋「不过相反」直搬 en revanche
        ("我很烦恼，不过相反，在门口，我离开时遇见了盖尔芒特公爵夫人，她非常客气，关于你的事。",
         "我很烦恼；不过我离开时，在门口遇见了盖尔芒特公爵夫人，她非常客气，跟我说了许多你的事。"),
        # ④ 一句里两个「她」分指公爵夫人与阿尔贝蒂娜
        ("她告诉我说，你对她说，她的死对你是多么大的悲伤。",
         "她告诉我说，你对她说，阿尔贝蒂娜的死对你是多么大的悲伤。"),
    ],
    "064": [
        # ④⑦ 「在他们身边」与前句「同她们一起吃饭」指人换形，且 auprès d'eux 指她贪恋的那些人
        ("也就随之无法在他们身边尝到一种完整的愉悦。",
         "也就随之无法从那些人身上尝到一种完整的愉悦。"),
    ],
}


def han_count(s):
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def main():
    total = 0
    for chunk, edits in EDITS.items():
        d = os.path.join(BASE, "chunk" + chunk)
        path = os.path.join(d, "final.txt")
        bak = path + ".bak_20261125"
        with open(path, "r", encoding="utf-8", newline="") as f:
            text = f.read()
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        before = text
        n_before_lines = before.count("\n")
        n_before_han = han_count(before)
        n = 0
        for old, new in edits:
            assert old in before, "missing: " + old[:30]
            assert before.count(old) == 1, "not unique: " + old[:30]
            assert new not in before, "already applied?: " + new[:30]
            before = before.replace(old, new)
            n += 1
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(before)
        n_after_lines = before.count("\n")
        n_after_han = han_count(before)
        assert n_before_lines == n_after_lines, "line count changed"
        print("chunk%s: 改动 %d 条 | 行数 %d→%d | 汉字 %d→%d | CRLF=%s"
              % (chunk, n, n_before_lines, n_after_lines,
                 n_before_han, n_after_han,
                 "\r\n" in open(path, "rb").read().decode("utf-8")))
        total += n
    print("合计改动 %d 条" % total)


main()
ast.parse(open(__file__, encoding="utf-8").read())