# -*- coding: utf-8 -*-
"""v1 chunk176-180 逐段润色：定位唯一子串 -> 替换 -> 断言命中数。"""
import ast
import os
import re
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    176: [
        ("颤动着的有价值的寄生物群落",
         "颤动着的珍贵寄生物群落"),
        ("林中忽然闪出一个快步走过的散步女子，裹着贴身的皮裘",
         "林中忽然闪出一个快步走过的散步女子，裹着柔滑的皮裘"),
        ("那轻易的优雅、卖俏的轮廓和薄薄的质地",
         "那种轻巧的优雅、卖俏的轮廓和薄薄的质地"),
    ],
    177: [
        ("匆匆穿过阿卡西亚道",
         "匆匆穿过金合欢路"),
        ("帽上缀着一根凤头鹦鹉的羽饰",
         "帽上缀着一根虹雉的羽饰"),
        ("可是，我把豪华放在最高位，而非简朴：那是在我逼着弗朗索瓦丝",
         "可是，我把豪华而非简朴放在最高位：那是在我逼着弗朗索瓦丝"),
        ("对我而言这形象意味着王者的威仪、君临的驾到，其程度是后来任何一位真正的女王都再没能给我这种印象的，"
         "因为我对她们权势的观念没那么模糊、更多来自经验",
         "对我而言，这形象意味着王者的威仪、君临的驾临；后来任何一位真正的女王都没再给我这样的印象，"
         "因为我对她们权势的观念没那么模糊，更多来自经验"),
        ("果然，到某一刻，正是步行道那头，她朝我们走来，我看见斯万夫人让她那件",
         "果然，到某一刻，我望见斯万夫人正沿着步行道朝我们走来，让她那件"),
    ],
    178: [
        ("有些日子我在金合欢道上没见到她，却碰巧在玛格丽特王后道上遇见她",
         "有些日子我在金合欢路上没见到她，却碰巧在玛格丽特王后路上遇见她"),
        ("或者想显得想图清静的女人",
         "或者想显得自己想图清静的女人"),
    ],
    179: [
        ("我朝金合欢道走去",
         "我朝金合欢路走去"),
        ("我想把一些女人的小帽子按在我身体的眼睛之下",
         "我想用身体的眼睛去看清一些女人的小帽子"),
        ("一般的瘦马——那种瘦削；",
         "一般的瘦马的瘦削；"),
    ],
    180: [
        ("在金合欢大道——那桃金娘的小径——上",
         "在金合欢路——那桃金娘的小径——上"),
        ("那里的女人被裹在连衣料都算不上的裙子里，举步维艰",
         "那里的女人穿着甚至算不上衣料的裙子，把自己捆得迈不开步"),
        ("我甚至能让他们明白吗——冬日清晨，我步行遇见斯万夫人时心里的那份激动：她穿着水獭皮大衣",
         "我甚至能让他们明白，冬日清晨我步行遇见斯万夫人时心里那份激动吗？她穿着水獭皮大衣"),
        ("我唯一的安慰，是在如今再无优雅可言的今天，回想我从前认识的那些女人。",
         "如今已无优雅可言，我唯一的安慰便是回想我从前认识的那些女人。"),
        ("而这欲望的种种要素，就是这个本身已变得无法企及的欲望的要素，正如它从前徒然追逐过的快乐一样。",
         "而这个欲望，这个本身已变得无法企及的欲望，正如它从前徒然追逐过的快乐一样。"),
        ("也帮我更清楚地懂得了一个矛盾：想从现实中去寻找记忆中的画面，是多么矛盾——",
         "也帮我更清楚地懂得了这样一个矛盾：想从现实中去寻找记忆中的画面——"),
    ],
}


def hanzi(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def main():
    for chunk in sorted(EDITS):
        d = os.path.join(ROOT, "chunk%d" % chunk)
        f = os.path.join(d, "final.txt")
        bak = f + ".bak_20261125"
        if not os.path.exists(bak):
            shutil.copyfile(f, bak)
            made = "新备份"
        else:
            made = "备份已存在，未覆盖"

        with open(f, encoding="utf-8", newline="") as fh:
            text = fh.read()
        nl = "\r\n" if "\r\n" in text else "\n"
        lines_before = text.count("\n") + (0 if text.endswith("\n") else 1)
        han_before = hanzi(text)

        n = 0
        for old, new in EDITS[chunk]:
            if text.count(old) == 0:
                assert text.count(new) == 1, "已应用但不可辨: %r" % new[:30]
                n += 1
                continue
            assert text.count(old) == 1, "命中 %d 次: %r" % (text.count(old), old[:30])
            text = text.replace(old, new)
            n += 1

        with open(f, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)

        lines_after = text.count("\n") + (0 if text.endswith("\n") else 1)
        han_after = hanzi(text)
        assert lines_before == lines_after, "行数变了 %d -> %d" % (lines_before, lines_after)
        paras = [x for x in text.replace("\r\n", "\n").split("\n") if x.strip()]
        print("chunk%d 改动 %d 条 行 %d->%d 汉字 %d->%d 段数 %d 换行 %s (%s)"
              % (chunk, n, lines_before, lines_after, han_before, han_after,
                 len(paras), "CRLF" if nl == "\r\n" else "LF", made))


main()
ast.parse(open(__file__, encoding="utf-8").read())
print("ast.parse OK")