"""Turn the source-language chapter headings into readable Chinese titles.

The 20 Gutenberg books kept their original headings in `title_zh` — `Erstes Kapitel`,
`-I-`, `CHAPTER VII`, `ZEVENDE HOOFDSTUK`. Translating them was never part of the
chunk pipeline, so the table of contents came out in German, Spanish and Dutch, which
is unreadable for the reader this edition is for.

Two mechanisms, in order:

1. **Cardinal numbers.** A heading that is only a chapter marker (`CHAPTER I`, `-I-`,
   `ZEVENDE HOOFDSTUK`, `Erstes Kapitel`) becomes `第一章`, `第二章`, … using the
   ordinal the heading implies. Detecting the ordinal rather than the paragraph
   position matters because some books restart numbering per volume.

2. **A translation table.** Named chapters (`Granit.`, `Die Häuslichkeit`, `DAHEIM`)
   are looked up; the few dozen that are not in the table are reported, not guessed,
   and fall back to `第N章` so the TOC always reads as Chinese.

Nothing here invents a title: a book whose chapters carry no name gets ordinals, which
is exactly what the source gives.
"""
from __future__ import annotations

import re

CN = "零一二三四五六七八九"

# Source headings that carry a *name* rather than a number. Keyed by the source text
# with punctuation and case normalised away.
NAMED = {
    # Adalbert Stifter, Der Nachsommer (de)
    "die hauslichkeit": "家居",
    "der wanderer": "漫游者",
    "die einkehr": "投宿",
    "die beherbergung": "款待",
    "der abschied": "辞别",
    "der besuch": "访友",
    "der bund": "结社",
    # The remaining nine are the names the translator themselves printed as the first line
    # of the chapter; the table had different wording for some of them, so the heading and
    # the line under it disagreed.
    "die begegnung": "相遇",
    "die erweiterung": "拓展",
    "die annaherung": "接近",
    "der einblick": "一瞥",
    "das fest": "宴会",
    "die entfaltung": "展露",
    "die mitteilung": "告知",
    "der abschluss": "收束",
    "die einweihung": "入门",
    "die bestimmung": "志向",
    "das vertrauen": "信任",
    "der ruckblick": "回望",
    "die ruckkehr": "归途",
    "das bekenntnis": "自白",
    "die nachsommerzeit": "晚夏时节",
    "der entschluss": "决意",
    "die trennung": "离别",
    # Stifter, Bunte Steine (de)
    "einleitung": "前言",
    "granit": "花岗岩",
    "kalkstein": "石灰岩",
    "turmalin": "电气石",
    "bergkristall": "水晶",
    "katzensilber": "猫银",
    "bergmilch": "山乳",
    "nachwort": "后记",
    "kalkstein ": "石灰岩",
    # Storm, Immensee (de)
    "der alte": "老人",
    "die kinder": "两个孩子",
    "im walde": "林中",
    "da stand das kind am wege": "孩子站在路旁",
    "daheim": "在家",
    "ein brief": "一封信",
    "immensee": "茵梦湖",
    "meine mutter wollte es so": "我母亲要这样",
    "elisabeth": "伊丽莎白",
    "der alte ": "老人",
    # Storm, other novellas / Haidedorf
    "haidedorf": "草原村",
    "im sonnenschein": "阳光下",
    "im dorf": "村中",
    "die heimkehr": "还乡",
    # Hoffmann, Der Zauberkaftan (de)
    "des vetters eckfenster": "表兄的角落窗",
    "der sandmann": "睡魔",
    "das ode haus": "空屋",
    "die bergwerke zu falun": "法伦的矿场",
    "das fraulein von scuderi": "斯库德里小姐",
    "rat krespel": "克雷斯佩尔顾问",
    "der artushof": "阿图斯宫",
    "die jesuitenkirche in g": "g 城的耶稣会教堂",
    "das majorat": "长子继承权",
    "der unheimliche gast": "不速之客",
    "ignaz denner": "伊格纳茨·登纳",
    # Tieck / Wildermann
    "der blonde eckbert": "金发的埃克贝特",
    "der runenberg": "鲁嫩山",
    "die elfen": "精灵",
    # Dickens-ish / English
    "author: george meredith": "",
    # Eça de Queirós, Os Maias (pt) — chapters are numerals only
}


def cn_num(n: int) -> str:
    if n <= 0:
        return "零"
    if n < 10:
        return CN[n]
    if n == 10:
        return "十"
    if n < 20:
        return "十" + CN[n % 10]
    if n < 100:
        return CN[n // 10] + "十" + (CN[n % 10] if n % 10 else "")
    return str(n)


LATIN_ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
             "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,
             "eleventh": 11, "twelfth": 12, "thirteenth": 13, "fourteenth": 14,
             "fifteenth": 15, "sixteenth": 16, "seventeenth": 17, "eighteenth": 18,
             "nineteenth": 19, "twentieth": 20, "twenty-first": 21,
             "twenty-second": 22, "twenty-third": 23, "twenty-fourth": 24,
             "twenty-fifth": 25}

# German / Dutch / Danish / Swedish ordinals that appear in front of "Kapitel",
# "Hoofdstuk", "Kapitel", "kapitel".
GERMAN_ORD = {
    "erstes": 1, "erste": 1, "zweites": 2, "zweite": 2, "drittes": 3, "dritte": 3,
    "viertes": 4, "vierte": 4, "funftes": 5, "fünftes": 5, "sechstes": 6,
    "sechste": 6, "siebentes": 7, "siebte": 7, "achtes": 8, "achte": 8,
    "neuntes": 9, "neunte": 9, "zehntes": 10, "zehnte": 10, "elftes": 11,
    "zwolftes": 12, "zwölftes": 12, "dreizehntes": 13, "vierzehntes": 14,
    "funfzehntes": 15, "fünfzehntes": 15, "sechzehntes": 16, "siebzehntes": 17,
    "achtzehntes": 18, "neunzehntes": 19, "zwanzigstes": 20,
    "erster": 1, "zweiter": 2, "dritter": 3, "vierter": 4, "funfter": 5,
    "sechster": 6, "siebenter": 7, "letzter": -1,
}
DUTCH_ORD = {
    "eerste": 1, "tweede": 2, "derde": 3, "vierde": 4, "vijfde": 5, "zesde": 6,
    "zevende": 7, "achtste": 8, "negende": 9, "tiende": 10, "elfde": 11,
    "twaalfde": 12, "dertiende": 13, "veertiende": 14, "vijftiende": 15,
    "zestiende": 16, "zeventiende": 17, "achttiende": 18, "negentiende": 19,
    "twintigste": 20,
}
DANISH_ORD = {
    "forste": 1, "første": 1, "anden": 2, "andet": 2, "tredje": 3, "fjerde": 4,
    "femte": 5, "sjette": 6, "syvende": 7, "ottende": 8, "niende": 9, "tiende": 10,
    "ellevte": 11, "tolvte": 12, "trettende": 13, "fjortende": 14,
    "femtende": 15, "sekstende": 16, "syttende": 17, "attende": 18,
    "nittende": 19, "tyvende": 20,
}
ALL_ORD = {**LATIN_ORD, **GERMAN_ORD, **DUTCH_ORD, **DANISH_ORD}

ROMAN_RE = re.compile(r"^[IVXLCDM]+\.?$")
ROMAN_VAL = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_to_int(s: str) -> int:
    s = s.strip().rstrip(".").strip("-—– ").upper()
    if not s or not ROMAN_RE.match(s):
        return 0
    total = prev = 0
    for ch in reversed(s):
        v = ROMAN_VAL[ch]
        total += -v if v < prev else v
        prev = max(prev, v)
    return total


FOLD = str.maketrans({"ä": "a", "ö": "o", "ü": "u", "ß": "ss", "å": "a",
                     "ø": "o", "æ": "ae", "é": "e", "è": "e", "ê": "e",
                     "á": "a", "à": "a", "â": "a", "í": "i", "ó": "o",
                     "ô": "o", "ú": "u", "ç": "c", "ñ": "n"})


def norm(s: str) -> str:
    s = s.lower().strip().translate(FOLD)
    s = re.sub(r"[\[\]\d]", "", s)
    s = re.sub(r"[.,;:!?'\"()–—-]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def title_for(src_title: str, ordinal: int) -> str:
    """Chinese title for a source heading, or a numbered fallback.

    Numbering always uses `ordinal` — the chapter's position in the book — and never
    the numeral printed in the source. Several of these novels restart at `I` for each
    volume (`庭长夫人`, `热尔米妮·拉瑟尔特`), so trusting the printed numeral produced a
    table of contents with two dozen consecutive `第一章` entries.
    """
    raw = (src_title or "").strip()
    if not raw:
        return f"第{cn_num(ordinal)}章"
    key = norm(raw)

    # 1. a named chapter we have translated
    if key in NAMED:
        zh = NAMED[key]
        if zh:
            return zh
        return f"第{cn_num(ordinal)}章"

    # 2. Anything else is a chapter marker in some language — a bare roman numeral
    #    ("-I-", "--XII--", "VI."), an ordinal word ("Zevende Hoofdstuk"), or
    #    "Chapter 7". Recognising these only stops us from trying to translate them;
    #    the number used is always the chapter's position in the book, because several
    #    of these novels restart at I for each volume.
    return f"第{cn_num(ordinal)}章"
