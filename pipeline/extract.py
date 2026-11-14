"""Extract clean, structured text from the 50th Anniversary PDF.

Output: work/src/<id>.json  with
  {id, book, chapter, title_en, title_zh, blocks:[{type: p|verse, text|lines}]}
Also work/src/<id>.txt  (LLM input form with markers).
"""
from __future__ import annotations

import json
import os
import re
import sys
import unicodedata

import pymupdf

PDF = "E:/Translate/The Lord of the Rings (50th Anniversary Edition) (J.R.R. Tolkien) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
OUT = "E:/Translate/work/src"

# chapter start pages (1-based, inclusive) -> parsed from heading scan
BOOKS = [
    ("book1", "卷一", [
        (45, "A Long-expected Party", "久盼的宴会"),
        (66, "The Shadow of the Past", "往昔阴影"),
        (89, "Three is Company", "三人成行"),
        (110, "A Short Cut to Mushrooms", "抄近路去采蘑菇"),
        (122, "A Conspiracy Unmasked", "阴谋揭穿"),
        (133, "The Old Forest", "老林子"),
        (147, "In the House of Tom Bombadil", "汤姆·邦巴迪尔的家"),
        (159, "Fog on the Barrow-downs", "古墓岗之雾"),
        (173, "At the Sign of the Prancing Pony", "跃马客栈"),
        (187, "Strider", "大步佬"),
        (200, "A Knife in the Dark", "黑暗中的利刃"),
        (221, "Flight to the Ford", "逃向渡口"),
    ]),
    ("book2", "卷二", [
        (243, "Many Meetings", "多次相会"),
        (263, "The Council of Elrond", "埃尔隆德的会议"),
        (296, "The Ring Goes South", "魔戒南行"),
        (319, "A Journey in the Dark", "黑暗之旅"),
        (345, "The Bridge of Khazad-dûm", "卡扎督姆桥"),
        (357, "Lothlórien", "罗斯洛立安"),
        (377, "The Mirror of Galadriel", "凯兰崔尔之镜"),
        (391, "Farewell to Lórien", "告别罗斯洛立安"),
        (404, "The Great River", "大河"),
        (419, "The Breaking of the Fellowship", "魔戒同盟瓦解"),
    ]),
    ("book3", "卷三", [
        (437, "The Departure of Boromir", "波罗莫的离开"),
        (445, "The Riders of Rohan", "洛汗骑兵"),
        (468, "The Uruk-hai", "强兽人"),
        (485, "Treebeard", "树胡"),
        (512, "The White Rider", "白骑士"),
        (530, "The King of the Golden Hall", "金殿之王"),
        (550, "Helm's Deep", "圣盔谷"),
        (567, "The Road to Isengard", "通往艾辛格之路"),
        (584, "Flotsam and Jetsam", "劫后余波"),
        (600, "The Voice of Saruman", "萨鲁曼之声"),
        (612, "The Palantír", "真知晶球"),
    ]),
    ("book4", "卷四", [
        (627, "The Taming of Sméagol", "驯服史麦戈"),
        (644, "The Passage of the Marshes", "死亡沼泽之路"),
        (660, "The Black Gate is Closed", "黑门关闭"),
        (672, "Of Herbs and Stewed Rabbit", "香草与炖兔肉"),
        (687, "The Window on the West", "西方之窗"),
        (707, "The Forbidden Pool", "禁地水池"),
        (718, "Journey to the Cross-roads", "前往十字路口"),
        (727, "The Stairs of Cirith Ungol", "西力斯昂哥的阶梯"),
        (741, "Shelob's Lair", "尸罗的巢穴"),
        (752, "The Choices of Master Samwise", "山姆怀斯先生的选择"),
    ]),
    ("book5", "卷五", [
        (771, "Minas Tirith", "米那斯提力斯"),
        (797, "The Passing of the Grey Company", "灰衣队伍的通过"),
        (815, "The Muster of Rohan", "洛汗集合"),
        (830, "The Siege of Gondor", "刚铎围攻战"),
        (854, "The Ride of the Rohirrim", "洛希尔人的冲锋"),
        (863, "The Battle of the Pelennor Fields", "帕兰诺平原之战"),
        (874, "The Pyre of Denethor", "迪耐瑟的火葬堆"),
        (882, "The Houses of Healing", "诊疗院"),
        (896, "The Last Debate", "最后的争论"),
        (907, "The Black Gate Opens", "黑门开了"),
    ]),
    ("book6", "卷六", [
        (921, "The Tower of Cirith Ungol", "西力斯昂哥之塔"),
        (940, "The Land of Shadow", "阴影之地"),
        (957, "Mount Doom", "末日火山"),
        (972, "The Field of Cormallen", "科玛伦平原"),
        (982, "The Steward and the King", "宰相与众王"),
        (998, "Many Partings", "多次告别"),
        (1013, "Homeward Bound", "归途"),
        (1022, "The Scouring of the Shire", "夏尔剿匪记"),
        (1045, "The Grey Havens", "灰港"),
    ]),
]

PROLOGUE = (25, 40, "prologue", "楔子", "Prologue", "楔子")


MARKS = {"´": "\u0301", "ˆ": "\u0302", "¨": "\u0308", "`": "\u0300"}
_MARK_CLASS = "´ˆ¨`"


def _accent_after(m):
    return unicodedata.normalize("NFC", m.group(1) + MARKS[m.group(2)])


def _accent_before(m):
    return unicodedata.normalize("NFC", m.group(2) + MARKS[m.group(1)])


def clean_line(s: str) -> str:
    """Per-line hygiene; diacritics are fixed later, once lines are joined."""
    s = s.replace("\ufb01", "fi").replace("\ufb02", "fl").replace("\ufb00", "ff")
    s = s.replace("\ufb03", "ffi").replace("\ufb04", "ffl")
    s = s.replace("\u2018", "‘").replace("\u2019", "’")
    s = re.sub(r"[ \t]+", " ", s)
    return s


def fix_accents(text: str) -> str:
    """This PDF draws diacritics as separate glyph runs: The´oden, Lo´ rien, Ea¨rn, ´Eomer,
    and puts the accent over the *next* letter after a dotless i: Grıḿa = Gríma."""
    # dotless i carrying the accent on the following letter
    text = re.sub(
        "ı([A-Za-z])([\u0301\u0300\u0302\u0308])",
        lambda m: unicodedata.normalize("NFC", "i" + m.group(2)) + m.group(1),
        unicodedata.normalize("NFD", text),
    )
    text = text.replace("ı", "i")
    text = re.sub("([A-Za-z])([" + _MARK_CLASS + "])[ ]?", _accent_after, text)
    text = re.sub("([" + _MARK_CLASS + "])([A-Za-z])", _accent_before, text)
    for ch in _MARK_CLASS:
        text = text.replace(ch, "")
    return unicodedata.normalize("NFC", text)


def page_lines(page, base_x=48.0, top=50.0):
    """Yield (x0, y0, y1, text, italic) for body lines of a page."""
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            spans = [s for s in l["spans"] if s["text"].strip()]
            if not spans:
                continue
            text = clean_line("".join(s["text"] for s in l["spans"]))
            x0, y0, x1, y1 = l["bbox"]
            if y0 < top:  # running head / page number
                continue
            if re.fullmatch(r"\s*\d+\s*", text):  # folio
                continue
            if any(s["size"] > 11.5 for s in spans):  # heading
                continue
            italic = all("Ital" in s["font"] for s in spans)
            out.append((x0, y0, y1, text, italic))
    return out


def build_blocks(lines):
    """Assemble lines into paragraphs / verse blocks with de-hyphenation."""
    blocks = []
    cur = None
    verse = None
    last_y1 = None

    def flush():
        nonlocal cur, verse
        if verse is not None:
            if verse:
                blocks.append({"type": "verse", "lines": verse})
            verse = None
        if cur is not None:
            if cur:
                blocks.append({"type": "p", "text": cur})
            cur = None

    for x0, y0, y1, text, italic in lines:
        is_verse = italic and x0 > 62
        if is_verse:
            if verse is None:
                flush()
                verse = []
            verse.append(text.strip())
            last_y1 = y1
            continue
        if verse is not None:
            # stanza gap inside verse? if same indent continues, keep verse
            flush()
        new_para = cur is None or x0 > 56
        if new_para:
            flush()
            cur = text.strip()
        else:
            # continuation line: join, handling hyphenation
            if cur.endswith("\u00ad"):
                cur = cur[:-1] + text.strip()
            elif cur.endswith("-"):
                nxt = text.lstrip()
                if nxt and nxt[0].islower():
                    cur = cur[:-1] + nxt
                else:
                    cur = cur + nxt
            else:
                cur = cur.rstrip() + " " + text.strip()
        last_y1 = y1
    flush()
    return blocks


def extract_range(doc, start, end):
    lines = []
    for pg in range(start - 1, end):
        lines.extend(page_lines(doc[pg]))
    blocks = build_blocks(lines)
    for b in blocks:
        if b["type"] == "p":
            b["text"] = fix_accents(b["text"])
        else:
            b["lines"] = [fix_accents(l) for l in b["lines"]]
    return blocks


def main():
    doc = pymupdf.open(PDF)
    os.makedirs(OUT, exist_ok=True)
    items = []
    # prologue
    s, e, cid, zh, en, title = PROLOGUE
    items.append(
        dict(id=cid, book="prologue", book_zh="楔子", no=0, title_en=en, title_zh=zh,
             blocks=extract_range(doc, s, e))
    )
    for book, book_zh, chs in BOOKS:
        for idx, (start, en, zh) in enumerate(chs):
            end = chs[idx + 1][0] - 1 if idx + 1 < len(chs) else None
            if end is None:
                end = {"book1": 240, "book2": 432, "book3": 624, "book4": 768,
                       "book5": 918, "book6": 1056}[book]
            items.append(
                dict(id=f"{book}c{idx+1:02d}", book=book, book_zh=book_zh, no=idx + 1,
                     title_en=en, title_zh=zh, blocks=extract_range(doc, start, end))
            )

    total_words = 0
    for it in items:
        jp = os.path.join(OUT, it["id"] + ".json")
        with open(jp, "w", encoding="utf-8") as f:
            json.dump(it, f, ensure_ascii=False, indent=1)
        paras = [b for b in it["blocks"] if b["type"] == "p"]
        verses = [b for b in it["blocks"] if b["type"] == "verse"]
        words = sum(len(p["text"].split()) for p in paras)
        words += sum(len(" ".join(v["lines"]).split()) for v in verses)
        total_words += words
        print(f"{it['id']:12s} words={words:6d} paras={len(paras):4d} verse={len(verses):3d} {it['title_en']}")
    print("TOTAL words:", total_words)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
