"""Chinese chapter titles for the sixteen public-domain titles in `work_pub`.

The table of contents must read as Chinese. Three kinds of source title turn up here and
each needs a different treatment:

  * **numbered** (`ERSTES KAPITEL`, `CHAPTER ONE`, `I`) -- the number is the only content,
    so it becomes 第一章 and similar. These are counted, not translated, because the
    ordinal is the title.
  * **real titles** -- Kafka's thirteen prose pieces, Woolf's seven stories, Rilke's
    cycles. These are translated here by hand, once, so that every volume in the set uses
    the same Chinese wording. A model asked twice would produce 揭穿一个骗子 and 揭穿骗子
    for the same story.
  * **absent** -- single-chapter books (Mrs Dalloway, The Voyage Out's undivided source,
    the two plays). The chapter has no title of its own, so the book's title serves, and
    `book_title_as_chapter` marks that case rather than inventing a section name.

Names follow the Chinese Kafka and Rilke conventions already used in this workspace
(`pipeline_gutenberg/titles_src.py`); nothing here may contradict the text itself, so the
short-story titles are the standard published ones.
"""
from __future__ import annotations

import re

# --- Kafka: Betrachtung (1913), nineteen pieces ------------------------------------
BETRACHTUNG = {
    "Kinder auf der Landstraße": "乡间公路上的孩子们",
    "Entlarvung eines Bauernfängers": "揭穿一个骗子",
    "Der plötzliche Spaziergang": "突如其来的散步",
    "Entschlüsse": "决心",
    "Der Ausflug ins Gebirge": "山中远足",
    "Das Unglück des Junggesellen": "单身汉的不幸",
    "Der Kaufmann": "商人",
    "Zerstreutes Hinausschaun": "心不在焉地向外望",
    "Der Nachhauseweg": "回家之路",
    "Die Vorüberlaufenden": "从旁跑过的人",
    "Der Fahrgast": "乘客",
    "Kleider": "衣服",
    "Die Abweisung": "拒绝",
    "Zum Nachdenken für Herrenreiter": "为骑手先生们思量",
    "Das Gassenfenster": "临街的窗",
    "Wunsch, Indianer zu werden": "想成为印第安人",
    "Die Bäume": "树",
    "Unglücklichsein": "不幸",
}

# --- Kafka: Ein Landarzt (1919), fourteen pieces -----------------------------------
LANDARZT = {
    "Der neue Advokat.": "新律师",
    "Ein Landarzt.": "乡村医生",
    "Auf der Galerie.": "在顶层楼座上",
    "Ein altes Blatt.": "一份旧账",
    "Vor dem Gesetz.": "在法的门前",
    "Schakale und Araber.": "豺狗与阿拉伯人",
    "Ein Besuch im Bergwerk.": "一次矿井之行",
    "Das nächste Dorf.": "邻村",
    "Eine kaiserliche Botschaft.": "一道圣旨",
    "Die Sorge des Hausvaters.": "家长的忧虑",
    "Elf Söhne.": "十一个儿子",
    "Ein Brudermord.": "一场兄弟残杀",
    "Ein Traum.": "一场梦",
    "Ein Bericht für eine Akademie.": "为科学院作的一份报告",
}

# --- Woolf: Monday or Tuesday (1921), seven stories --------------------------------
MONDAY = {
    "A HAUNTED HOUSE": "闹鬼的宅子",
    "A SOCIETY": "一个社团",
    "MONDAY OR TUESDAY": "星期一或星期二",
    "AN UNWRITTEN NOVEL": "一部未写的小说",
    "THE STRING QUARTET": "弦乐四重奏",
    "BLUE & GREEN": "蓝与绿",
    "KEW GARDENS": "邱园",
    "THE MARK ON THE WALL": "墙上的斑点",
}

# --- Rilke: Das Stunden-Buch, three books ------------------------------------------
STUNDENBUCH = {
    "Erstes Buch": "第一书",
    "Zweites Buch": "第二书",
    "Drittes Buch": "第三书",
    # the volume's own contents list repeats the three books with their full titles and
    # dates; those became chapters too, so they get the same three names plus the subtitle
    "_Erstes Buch:_ Das Buch vom mönchischen Leben (1899)":
        "第一书：修士生活之书",
    "_Zweites Buch:_ Das Buch von der Pilgerschaft (1901)":
        "第二书：朝圣之书",
    "_Drittes Buch:_ Das Buch von der Armut und vom Tode (1903)":
        "第三书：贫穷与死亡之书",
}

# --- Rilke: Die Aufzeichnungen des Malte Laurids Brigge ---------------------------
MALTE = {
    "Rainer Maria Rilke": "马尔特手记",
    "Bibliothèque Nationale.": "国家图书馆",
    "Ein Briefentwurf.": "一封书信草稿",
}

# --- Kafka: Das Urteil ------------------------------------------------------------
URTEIL = {
    "DAS URTEIL": "判决",
    #  is the dedication that heads the story itself, not a section title. Kafka
    # printed it alone on the line above the first sentence, so extraction made it the
    # chapter heading and the story's own name -- which sat on the imprint page -- was
    # lost. The dedication is the chapter's opening line in the text, so the heading here
    # must be the title.
    "FÜR F.": "判决",
}

# --- Rilke: Neue Gedichte, cycles --------------------------------------------------
NEUEGEDICHTE = {
    "I": "一", "II": "二", "III": "三", "IV": "四", "V": "五",
}

# --- Kafka: Der Prozess, ten chapters ----------------------------------------------
# Each chapter prints its number (KAPITEL) and then its name in capitals. The names are
# Kafka's own, so they are translated rather than numbered; `build_pub` lifts the rest of
# them out of the translated body, but the first and the fifth only reach it here.
PROZESS = {
    "ERSTES KAPITEL": "逮捕 · 与格鲁巴赫太太的谈话 · 比珥斯特纳小姐",
    "ZWEITES KAPITEL": "第一次调查",
    "DRITTES KAPITEL": "空无一人的审讯庭 · 大学生 · 办公室",
    "VIERTES KAPITEL": "比珥斯特纳小姐的女友",
    "FÜNFTES KAPITEL": "打手",
    "SECHSTES KAPITEL": "舅舅·莱妮",
    "SIEBENTES KAPITEL": "律师·工厂主·画家",
    "ACHTES KAPITEL": "布洛克律师 · 律师的解约",
    "NEUNTES KAPITEL": "教堂",
    "ZEHNTES KAPITEL": "结局",
}

# --- Woolf: Jacob's Room, fifteen chapters -----------------------------------------
EN_ORDINAL = {
    1: "第一章", 2: "第二章", 3: "第三章", 4: "第四章", 5: "第五章",
    6: "第六章", 7: "第七章", 8: "第八章", 9: "第九章", 10: "第十章",
    11: "第十一章", 12: "第十二章", 13: "第十三章", 14: "第十四章",
    15: "第十五章", 16: "第十六章", 17: "第十七章", 18: "第十八章",
    19: "第十九章", 20: "第二十章", 21: "第二十一章", 22: "第二十二章",
    23: "第二十三章", 24: "第二十四章", 25: "第二十五章", 26: "第二十六章",
    27: "第二十七章", 28: "第二十八章", 29: "第二十九章", 30: "第三十章",
}

# --- Dubliners (1914), fifteen stories ---------------------------------------------
DUBLINERS = {
    "THE SISTERS": "姊妹们",
    "AN ENCOUNTER": "一次遭遇",
    "ARABY": "阿拉比",
    "EVELINE": "伊芙琳",
    "AFTER THE RACE": "赛车之后",
    "TWO GALLANTS": "两个浪子",
    "THE BOARDING HOUSE": "寄宿公寓",
    "A LITTLE CLOUD": "一朵小云",
    "COUNTERPARTS": "无独有偶",
    "CLAY": "泥土",
    "A PAINFUL CASE": "一件悲痛的事",
    "IVY DAY IN THE COMMITTEE ROOM": "常春藤日",
    "A MOTHER": "一位母亲",
    "GRACE": "恩典",
    "THE DEAD": "死者",
}

# --- Hesse: Siddhartha (1922) ------------------------------------------------------
SIDDHARTHA = {
    "ERSTER TEIL": "第一部",
    "ZWEITER TEIL": "第二部",
    "DER SOHN DES BRAHMANEN": "婆罗门之子",
    "BEI DEN SAMANAS": "沙门",
    "GOTAMA": "乔达摩",
    "ERWACHEN": "觉醒",
    "KAMALA": "迦摩罗",
    "BEI DEN KINDERMENSCHEN": "尘世",
    "SANSARA": "轮回",
    "AM FLUSSE": "河边",
    "DER FÄHRMANN": "船夫",
    "DER SOHN": "儿子",
    "GOVINDA": "戈文达",
}

# --- Maupassant: Le Horla (1887 collection) ----------------------------------------
HORLA = {
    "LE HORLA": "奥尔拉",
    "TROIS PAGES DU LIVRE D'UN CHASSEUR": "猎人手记的三页",
    "LE TROU": "洞",
    "SAUVÉE": "获救",
    "CLOCHETTE": "小铃铛",
    "LE MARQUIS DE FUMEROL": "菲默罗尔侯爵",
    "MÉLANI.": "梅拉妮",
    "LE SIGNE": "记号",
    "LE DIABLE": "魔鬼",
    "LES ROIS": "国王们",
    "AU BOIS": "林中",
    "UNE FAMILLE": "一家人",
    "JOSEPH": "约瑟夫",
    "L'AUBERGE": "客栈",
    "LE VAGABOND": "流浪汉",
    "FIN": "终",
}

# --- Musil: Die Verwirrungen des Zöglings Törleß (1906) ----------------------------
# The novel has no chapter titles; the extractor took each chapter's first sentence
# as one. Numbering is the honest heading, and the sentence stays in the body.
TOERLESS_FIRST_SENTENCE = {"Zögern.", "Keine Antwort.", "Allgemeines Gebrülle."}

# Title pages that the extractor treated as chapters: the book's own name in Latin,
# and the author's name on the half-title. Nothing to translate, nothing to print.
FRONT_TITLE_PAGES = {"DUBLINERS", "SIDDHARTHA", "GUY DE MAUPASSANT"}

TABLES = {
    "betrachtung": BETRACHTUNG,
    "dubliners": DUBLINERS,
    "siddhartha": SIDDHARTHA,
    "horla": HORLA,
    "landarzt": LANDARZT,
    "mondaytuesday": MONDAY,
    "stundenbuch": STUNDENBUCH,
    "prozess": PROZESS,
    "malte": MALTE,
    "urteil": URTEIL,
}


# Books whose single chapter carries no title of its own: the book title is the heading.
book_title_as_chapter = {"mrsdalloway", "strafkolonie", "hungerkuenstler",
                         "jedermann", "torundtod"}

# Chapter counts, so a missing entry is reported rather than silently numbered.
EXPECTED = {
    "betrachtung": 19, "landarzt": 15, "prozess": 11, "jacobsroom": 15,
    "mondaytuesday": 7, "voyageout": 28, "neuegedichte": 18, "stundenbuch": 7,
    "malte": 4, "verwandlung": 4, "urteil": 3,
}

_WORD_ORD = {
    "ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5, "SIX": 6, "SEVEN": 7,
    "EIGHT": 8, "NINE": 9, "TEN": 10, "ELEVEN": 11, "TWELVE": 12, "THIRTEEN": 13,
    "FOURTEEN": 14, "FIFTEEN": 15, "SIXTEEN": 16, "SEVENTEEN": 17,
    "EIGHTEEN": 18, "NINETEEN": 19, "TWENTY": 20,
}
_DE_ORD = {
    "ERSTES": 1, "ZWEITES": 2, "DRITTES": 3, "VIERTES": 4, "FÜNFTES": 5,
    "SECHSTES": 6, "SIEBENTES": 7, "ACHTES": 8, "NEUNTES": 9, "ZEHNTES": 10,
    "ELFTES": 11, "ZWÖLFTES": 12, "DREIZEHNTES": 13, "VIERZEHNTES": 14,
    "FÜNFZEHNTES": 15, "SECHZEHNTES": 16, "SIEBZEHNTES": 17, "ACHTZEHNTES": 18,
    "NEUNZEHNTES": 19, "ZWANZIGSTES": 20,
}
_ROMAN = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8,
    "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15,
    "XVI": 16, "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20, "XXI": 21,
    "XXII": 22, "XXIII": 23, "XXIV": 24, "XXV": 25, "XXVI": 26, "XXVII": 27,
    "XXVIII": 28, "XXIX": 29, "XXX": 30,
}


def ordinal(n: int) -> str:
    return EN_ORDINAL.get(n, f"第{n}章")


_FR_ORD = {
    "PREMIER": 1, "PREMIÈRE": 1, "DEUXIÈME": 2, "TROISIÈME": 3, "QUATRIÈME": 4,
    "CINQUIÈME": 5, "SIXIÈME": 6, "SEPTIÈME": 7, "HUITIÈME": 8, "NEUVIÈME": 9,
    "DIXIÈME": 10, "ONZIÈME": 11, "DOUZIÈME": 12, "TREIZIÈME": 13, "QUATORZIÈME": 14,
    "QUINZIÈME": 15, "SEIZIÈME": 16, "DIX-SEPTIÈME": 17, "DIX-HUITIÈME": 18,
    "DIX-NEUVIÈME": 19, "VINGTIÈME": 20,
}


def roman_to_int(s: str) -> int | None:
    """Any well-formed Roman numeral, not just the ones in a hand-written table.

    The table stopped at XXX, so Tess (LIX) and Bleak House (LXVII) fell through to
    the Latin fallback and printed "CHAPTER LIX" in a Chinese contents list.
    """
    s = s.strip().upper()
    if not s or not re.fullmatch(r"[IVXLCDM]+", s):
        return None
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total, prev = 0, 0
    for ch in reversed(s):
        v = vals[ch]
        total += -v if v < prev else v
        prev = max(prev, v)
    return total or None


def parse_number(title: str) -> int | None:
    """The number a title *is*, or None when the title carries content."""
    t = title.strip().strip(".").strip()
    if not t:
        return None
    t = re.sub(r"[\].]+$", "", t).strip()
    m = re.fullmatch(r"(?:CHAPTER|CHAPITRE|KAPITEL)\s+([A-ZÄÖÜa-zäöü-]+)", t, re.I)
    if m:
        w = m.group(1).upper()
        if w in _WORD_ORD:
            return _WORD_ORD[w]
        if w in _FR_ORD:
            return _FR_ORD[w]
        if w in _DE_ORD:
            return _DE_ORD[w]
        if w in _ROMAN:
            return _ROMAN[w]
        r = roman_to_int(w)
        if r:
            return r
    m = re.fullmatch(r"([A-Z]+)", t)
    if m:
        w = m.group(1)
        if w in _WORD_ORD:
            return _WORD_ORD[w]
        if w in _ROMAN:
            return _ROMAN[w]
        r = roman_to_int(w)
        if r:
            return r
    m = re.fullmatch(r"([A-ZÄÖÜ]+)\s+KAPITEL", t, re.I)
    if m:
        w = m.group(1).upper()
        for cand in (w, w + "ES", w + "E"):
            if cand in _DE_ORD:
                return _DE_ORD[cand]
        return None
    if t.isdigit():
        return int(t)
    return None


def title_zh(book: str, title_src: str, ordinal_pos: int, book_title: str,
             skip_numbering: bool = False, single_chapter: bool = False,
             body_pos: int = 0) -> str:
    """Chinese heading for one chapter.

    `ordinal_pos` is the chapter's position in the book, used only as a last resort and
    never as a stand-in for a real title -- the difference between 第一章 and 揭穿一个骗子
    is the difference between a usable contents list and a useless one.

    `skip_numbering` is set for the leading title-page chapter. Its title is empty and it
    is not translated, but it still occupies position one, which made `jacobsroom` list
    "第一章 / 第一章 / 第二章": the imprint and the first real chapter both claimed to be
    the first. Front matter gets 卷首语 instead, and the body keeps its own numbering.
    """
    table = TABLES.get(book, {})
    t = title_src.strip()
    # Gutenberg and the French texts mark italics with underscores and quote titles
    # with guillemets; neither belongs in the lookup key or in the heading.
    t_key = t.replace("_", "").strip("«»\"")
    if t_key.upper() in FRONT_TITLE_PAGES and not single_chapter:
        return "卷首"
    if book == "toerless" and t in TOERLESS_FIRST_SENTENCE:
        return ordinal(body_pos or ordinal_pos)

    if t in table:
        return table[t]
    if t_key in table:
        return table[t_key]

    n = parse_number(t)
    if n is not None:
        # a bare number in Neue Gedichte is a poem inside a cycle, numbered from one each
        # time; the ordinal table would print 第一章 eight times, so fall back to the
        # Chinese numeral and let the builder disambiguate by position if it must
        if book == "neuegedichte":
            # The cycles are numbered from one again inside each group, so the raw
            # numeral repeats -- the contents list read 一 / 二 / 一 / 二 / 三 / 一.
            # The group names (FRÜHER APOLLO, MÄDCHENKLAGE ...) sit in the body, not in
            # the extracted title, so the honest heading is the poem's place in the book.
            return f"第{body_pos}首"
        return ordinal(n)

    if skip_numbering:
        # A single-chapter book has no front matter: its one chapter *is* the book, so the
        # book title is the heading. "卷首" is right only when there is a body after it.
        return book_title if single_chapter else "卷首"

    if book in book_title_as_chapter and not t:
        return book_title

    if not t:
        return ordinal(ordinal_pos)

    # Source title present but untranslated: keep it rather than print a wrong ordinal.
    # Reported by `verify()` so it can be fixed by hand instead of shipping Latin text.
    return t


def verify(index: dict) -> list[str]:
    """Problems worth fixing before assembly."""
    book = index["book"]
    problems = []
    chapters = index["chapters"]
    exp = EXPECTED.get(book)
    if exp is not None and len(chapters) != exp:
        problems.append(f"{book}: {len(chapters)} chapters, expected {exp}")
    for c in chapters:
        zh = c.get("title_zh", "")
        if not zh:
            problems.append(f"{book}/{c['id']}: empty title")
        elif re.search(r"[A-Za-zÄÖÜäöü]{2,}", zh):
            # two or more consecutive Latin letters means an untranslated word. A single
            # initial inside a Chinese title is legitimate: `献给F.` is how Kafka's
            # dedication to Felice Bauer is printed in Chinese, and the letter must stay.
            problems.append(f"{book}/{c['id']}: still Latin: {zh!r}")
    return problems
