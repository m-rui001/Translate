"""Chinese chapter summaries for the Proust volumes' table of contents.

The French edition prints a one-line *résumé* above each chapter, which in the
scanned text runs on into the chapter's opening sentence (the extractor could not
tell them apart). Rather than printing a page of French, each chapter gets a short
Chinese heading derived from that résumé, using the same proper names the body
text already uses (夏尔吕 / 韦尔迪兰 / 康布雷梅 / 沃古贝尔 …).

The summaries are deliberately terse — they exist to make the TOC navigable, not to
summarise the novel — and stay faithful to what the French résumé actually names.
Order matches `outline.markers()`: (volume, part, chapter) -> title.
"""
from __future__ import annotations

TITLES: dict[tuple[str, str, str], str] = {
    # 第三卷 盖尔芒特家那边
    ("v3", "", ""): "卷首",
    ("v3", "Première", ""): "第一部 外祖母的病与死",
    ("v3", "Deuxième", "premier"): "第二部 第一章 外祖母之死·贝戈特之死",
    ("v3", "", "deuxième"): "第二章 阿尔贝蒂娜来访·帕尔马亲王夫人面前的盖尔芒特精神",

    # 第四卷 索多姆和戈摩尔
    ("v4", "", ""): "卷首",
    ("v4", "Première", ""): "第一部 男同性恋者的初次登场",
    ("v4", "Deuxième", "premier"): "第二部 第一章 夏尔吕先生在社交界",
    ("v4", "", "deuxième"): "第二章 阿尔贝蒂娜的秘密",
    ("v4", "", "troisième"): "第三章 夏尔吕先生的忧伤·他虚构的决斗",
    ("v4", "", "quatrième"): "第四章 突然转向阿尔贝蒂娜",

    # 第六卷 女逃亡者
    ("v6", "", ""): "卷首",
    ("v6", "", "premier"): "第一章 悲伤与遗忘",
    ("v6", "", "II"): "第二章 福什维尔小姐",
    ("v6", "", "III"): "第三章 威尼斯之行",
    ("v6", "", "IV"): "第四章 圣卢的新面貌",

    # 第七卷 重现的时光
    ("v7", "", ""): "卷首",
    ("v7", "", "premier"): "第一章 当松维尔",
    ("v7", "", "II"): "第二章 战时的夏尔吕先生",
    ("v7", "", "III"): "第三章 盖尔芒特亲王夫人的下午茶会",
}


def title_for(vol: str, part: str, ch: str) -> str:
    return TITLES.get((vol, part or "", ch or ""), "")
