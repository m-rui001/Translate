
"""Apply the adjudicated name corrections to the EPUB files in place.

Only text nodes are touched, and every replacement is counted and reported, so the
pass can be audited afterwards. The map below is the curated result of the scanner
plus the model's verdicts: pairs that turned out to be two different people (Hirst /
Hewet, Charlus / Charlème) and pairs that were ordinary phrases (我的朋友 / 我的好朋友)
were dropped by hand.
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
import zipfile

# book title (without the 坟头草译 suffix) -> [(wrong, right)]
FIX: dict[str, list[tuple[str, str]]] = {
    "三个火枪手": [("达塔尼昂", "达达尼昂"), ("阿多斯", "阿托斯"), ("米拉狄", "米拉迪"),
                   ("普朗谢", "普朗歇")],
    "傲慢与偏见": [("班内特", "班纳特")],
    "双城记": [("马奈特", "马内特"), ("克兰彻", "克朗彻")],
    "基督山伯爵": [("唐太斯", "唐泰斯"), ("唐戴斯", "唐泰斯"), ("唐代斯", "唐泰斯")],
    "布登勃洛克一家": [("佩尔马内德", "佩尔曼内德")],
    "戴安娜的交叉": [("达西埃", "达西尔")],
    "热尔米妮·拉瑟尔特": [("瓦尔朗德伊", "瓦朗德伊")],
    "爱玛": [("哈里特", "哈丽特")],
    "瓜拉尼人": [("印第安佬", "印第安人")],
    "福尔图娜塔与哈辛塔": [("福图纳塔", "福尔图娜塔"), ("吉耶尔米娜", "吉列尔米娜")],
    "红与黑": [("拉摩尔", "拉莫尔"), ("拉穆尔", "拉莫尔")],
    "艾菲·布里斯特": [("英斯泰顿", "英斯泰滕")],
    "荒凉山庄": [("贾恩狄斯", "贾恩戴斯"), ("贾恩迪斯", "贾恩戴斯"),
                 ("贾恩代斯", "贾恩戴斯"), ("贾迪斯", "贾恩戴斯"),
                 ("特维德洛普", "特维德罗普"), ("克罗克", "克鲁克"),
                 ("斯莫尔威德", "斯莫尔维德"), ("艾斯特", "艾丝特")],
    "远大前程": [("贾格思", "贾格斯"), ("赫伯尔特", "赫伯特"), ("伍普塞尔", "伍普斯尔")],
    "远航": [("达洛威", "达洛维")],
    "野人旅馆": [("多萝特", "多蕾特")],
    "金人": [("蒂玛尔", "蒂马尔"), ("特蕾丝", "特蕾泽")],
    "阿亚拉的天使": [("特拉弗克", "特拉菲克"), ("斯托布斯", "斯塔布斯"),
                     ("斯特布斯", "斯塔布斯")],
    "马亚一家": [("达马佐", "达马索")],
    "马克斯·哈弗拉尔": [("弗尔布鲁格", "弗布鲁格")],
    "高老头": [("纽辛根", "纽沁根"), ("博赛昂", "博塞昂")],
    # The five books the review looked at, where the variants were counted by hand.
    "都柏林人": [("艾沃斯", "艾弗丝")],
    "浮士德上册": [("靡菲斯特", "梅菲斯特"), ("靡菲斯托菲勒斯", "梅菲斯托菲勒斯"),
                   ("格雷琴", "格蕾琴"), ("玛格丽特", "玛加蕾特"),
                   ("玛格蕾特", "玛加蕾特"), ("瓦朗坦", "瓦伦丁")],
    "星期一或星期二": [("卡斯塔利亚", "卡斯塔莉亚"), ("缙绅录", "年鉴")],
}

TEXT = re.compile(r"(<(?:p|h1|h2|h3|title)[^>]*>)(.*?)(</(?:p|h1|h2|h3|title)>)", re.S)


def apply_text(s: str, pairs: list[tuple[str, str]]) -> tuple[str, dict]:
    counts = {}
    for wrong, right in pairs:
        n = s.count(wrong)
        if n:
            s = s.replace(wrong, right)
            counts[wrong] = n
    return s, counts


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    total = 0
    for path in sorted(os.listdir("out")):
        if not path.endswith(".epub"):
            continue
        book = path.replace("（坟头草译）.epub", "")
        pairs = FIX.get(book)
        if not pairs:
            continue
        src = os.path.join("out", path)
        zin = zipfile.ZipFile(src)
        items = [(i, zin.read(i.filename)) for i in zin.infolist()]
        zin.close()
        counts, changed = {}, False
        out_items = []
        for info, data in items:
            if info.filename.endswith(".xhtml"):
                s = data.decode("utf-8")
                def repl(m):
                    t = html.unescape(m.group(2))
                    t2, c = apply_text(t, pairs)
                    for k, v in c.items():
                        counts[k] = counts.get(k, 0) + v
                    return m.group(1) + html.escape(t2, quote=False) + m.group(3)
                s2 = TEXT.sub(repl, s)
                if s2 != s:
                    changed = True
                    data = s2.encode("utf-8")
            out_items.append((info, data))
        if not changed:
            continue
        tmp = src + ".tmp"
        with zipfile.ZipFile(tmp, "w") as z:
            for info, data in out_items:
                z.writestr(info, data)
        os.replace(tmp, src)
        total += sum(counts.values())
        print(f"{book:20s} " + "  ".join(f"{k}->{v}:{n}" for k, v, n in
                                         ((k, dict(pairs)[k], n) for k, n in counts.items())))


if __name__ == "__main__":
    main()
