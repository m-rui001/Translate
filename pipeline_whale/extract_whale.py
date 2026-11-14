"""Extract Moby-Dick (Penguin Classics EPUB) into structured per-chapter JSON.

Output: work_whale/src/<id>.json
  {id, num, title_en, title_zh, blocks:[{type: p|verse|speaker|head, text|lines}]}

Design notes
------------
The EPUB is a calibre conversion of the Penguin Enriched eBook Classic. Chapter
files carry a `<p class=calibre8>CHAPTER n</p>` label, an italic title line
(`calibre11`), prose paragraphs (`calibre21/40/24/30/6/22`), attribution lines
(`calibre31`, verse sources) and `<blockquote>` verse / drama lines whose nesting
depth encodes stanza structure.

Italics carry real meaning in this book (emphasis, foreign words, stage
directions), so they are preserved as ⟦i⟧…⟦/i⟧ markers and lyrics are kept as
verse blocks with their line breaks. Footnote superscripts are dropped.
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
import zipfile

from lxml import html as LH

EPUB = "E:/Translate/Moby-Dick.epub"
OUT = "E:/Translate/work_whale/src"

# Front matter + 135 chapters + epilogue, in spine order.
START, END = "ebook_017.html", "ebook_154.html"

TITLE_ZH = {
    "Etymology": "词源",
    "Extracts": "摘录",
}
# chapter number -> 中文标题（自拟，尽量贴通行译名）
CHAPTER_ZH = {
    1: "幻影重重", 2: "旅行袋", 3: "大鲸客店", 4: "被单", 5: "早餐", 6: "街道",
    7: "小教堂", 8: "讲坛", 9: "讲道", 10: "知心朋友", 11: "睡衣", 12: "身世",
    13: "独轮车", 14: "南塔开特", 15: "杂烩", 16: "船", 17: "斋月", 18: "他的记号",
    19: "预言家", 20: "忙乱", 21: "上船", 22: "快乐圣诞", 23: "背风岸",
    24: "辩护人", 25: "附言", 26: "骑士与随从", 27: "骑士与随从（续）",
    28: "亚哈", 29: "亚哈登场，斯塔布随后", 30: "烟斗", 31: "助产婆玛布",
    32: "鲸类学", 33: "斯培克辛德", 34: "船长室的餐桌", 35: "桅顶瞭望",
    36: "后甲板", 37: "日落", 38: "黄昏", 39: "初夜班", 40: "午夜，水手舱",
    41: "莫比·迪克", 42: "大鲸的白色", 43: "听！", 44: "海图", 45: "宣誓书",
    46: "揣想", 47: "编席", 48: "第一次下艇", 49: "鬣狗", 50: "亚哈的小艇与费达拉",
    51: "精灵喷水", 52: "“裴廓德”号遇上“信天翁”号", 53: "海上相逢",
    54: "“城头”号的故事", 55: "荒唐的大鲸画像", 56: "略为准确的鲸画像",
    57: "鲸画、鲸牙和木刻", 58: "小鱼", 59: "鱿鱼", 60: "鲸索",
    61: "斯塔布杀死一条鲸", 62: "投鱼叉", 63: "叉架", 64: "斯塔布的晚餐",
    65: "鲸作为菜肴", 66: "鲨鱼大屠杀", 67: "割油", 68: "毯子", 69: "葬礼",
    70: "斯芬克司", 71: "“裴廓德”号遇上“耶罗波安”号", 72: "猴索",
    73: "斯塔布与弗拉斯克杀死一条露脊鲸", 74: "抹香鲸的脑袋", 75: "露脊鲸的脑袋",
    76: "攻城槌", 77: "海德堡大酒桶", 78: "水罐与水桶", 79: "大草原",
    80: "脑袋", 81: "“裴廓德”号遇上“处女”号", 82: "捕鲸的荣耀与光荣",
    83: "约拿的历史地位", 84: "投杆", 85: "喷泉", 86: "尾巴", 87: "大舰队",
    88: "鲸群与群主", 89: "有主鲸与无主鲸", 90: "正面与反面", 91: "“裴廓德”号遇上“玫瑰苞”号",
    92: "龙涎香", 93: "漂流者", 94: "捏手", 95: "法衣", 96: "炼油间",
    97: "灯", 98: "收纳与清洗", 99: "杜伯隆金币", 100: "“裴廓德”号遇上伦敦的“撒母耳·恩德比”号",
    101: "玻璃酒瓶", 102: "阿萨西兹的凉亭", 103: "鲸骨的尺寸", 104: "化石鲸",
    105: "鲸会变小吗", 106: "亚哈的腿", 107: "木匠", 108: "甲板上·亚哈与木匠",
    109: "舱室内·亚哈与斯达巴克", 110: "魁魁格的棺材", 111: "太平洋",
    112: "铁匠", 113: "熔炉", 114: "镀金者", 115: "“裴廓德”号遇上“单身汉”号",
    116: "垂死的鲸", 117: "守望鲸", 118: "象限仪", 119: "蜡烛", 120: "甲板上",
    121: "午夜，前甲板", 122: "午夜，桅顶", 123: "滑膛枪", 124: "罗盘针",
    125: "测程仪与绳子", 126: "救生圈", 127: "甲板上·亚哈与木匠", 128: "“裴廓德”号遇上“拉结”号",
    129: "舱室内·亚哈与皮普", 130: "帽子", 131: "“裴廓德”号遇上“欢欣”号",
    132: "交响曲", 133: "追击·第一天", 134: "追击·第二天", 135: "追击·第三天",
}

PROSE_CLASSES = {"calibre21", "calibre40", "calibre24", "calibre30", "calibre6",
                 "calibre22", "calibre5", "calibre2", "calibre46", "calibre20",
                 "calibre25", "calibre49"}
ATTR_CLASSES = {"calibre31"}          # verse / quotation attributions
HEAD_CLASSES = {"calibre8", "calibre11"}  # CHAPTER n, chapter title
SKIP_CLASSES = {"calibre39", "calibre4"}


def outer(el) -> str:
    return LH.tostring(el, encoding="unicode")


def text_with_italics(el) -> str:
    """Plain text, with <em>/<i> runs marked as ⟦i⟧…⟦/i⟧ and notes dropped."""
    parts: list[str] = []

    def walk(node, in_i: bool = False):
        tag = node.tag if isinstance(node.tag, str) else ""
        if tag == "sup":                      # footnote marker
            return
        if tag in ("em", "i") or (tag == "span" and "italic" in (node.get("class") or "")):
            if not in_i:
                parts.append("⟦i⟧")
            if node.text:
                parts.append(node.text)
            for ch in node:
                walk(ch, True)
            if not in_i:
                parts.append("⟦/i⟧")
            if node.tail:
                parts.append(node.tail)
            return
        if tag == "br":
            parts.append("\n")
            return
        if node.text:
            parts.append(node.text)
        for ch in node:
            walk(ch, in_i)
        if node.tail:
            parts.append(node.tail)

    walk(el)
    txt = "".join(parts)
    txt = txt.replace("\u00a0", " ").replace("\u200b", "")
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r" *\n *", "\n", txt)
    txt = txt.strip()
    # collapse empty italic runs and nested markers
    txt = re.sub(r"⟦i⟧\s*⟦/i⟧", "", txt)
    txt = txt.replace("⟦/i⟧⟦i⟧", "")
    return txt


def body_children(doc):
    body = doc.find(".//body")
    # unwrap single wrapper divs
    while len(body) == 1 and body[0].tag == "div" and not (body[0].get("class") or "").startswith("calibre1"):
        body = body[0]
    if len(body) >= 1 and body[0].tag == "div":
        return list(body[0])
    return list(body)


def parse_chapter(raw: bytes):
    doc = LH.fromstring(raw)
    blocks: list[dict] = []
    verse: list[str] = []

    def flush_verse():
        nonlocal verse
        if verse:
            blocks.append({"type": "verse", "lines": verse})
            verse = []

    for el in body_children(doc):
        tag = el.tag if isinstance(el.tag, str) else ""
        cls = el.get("class") or ""
        if tag == "a":
            continue
        if tag == "blockquote":
            t = text_with_italics(el)
            if t:
                verse.append(t)
            continue
        flush_verse()
        if tag == "p":
            t = text_with_italics(el)
            if not t:
                continue
            if cls in HEAD_CLASSES:
                blocks.append({"type": "head", "text": t})
            elif cls in ATTR_CLASSES:
                blocks.append({"type": "attr", "text": t})
            else:
                kind = "p"
                blocks.append({"type": kind, "text": t})
        elif tag in ("div", "h1", "h2", "h3"):
            t = text_with_italics(el)
            if t:
                blocks.append({"type": "head", "text": t})
    flush_verse()
    return blocks


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(OUT, exist_ok=True)
    z = zipfile.ZipFile(EPUB)
    nav = z.read("nav.xhtml").decode()
    ents = re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', nav, re.S)
    order = []
    for h, t in ents:
        h = h.split("#")[0]
        t = html.unescape(re.sub(r"<[^>]+>", "", t)).strip()
        if not re.match(r"ebook_\d+\.html$", h):
            continue
        order.append((h, t))
    files = [x for x in order]
    ids = [h for h, _ in files]
    i0, i1 = ids.index(START), ids.index(END)
    sel = files[i0:i1 + 1]

    total_words = 0
    for h, label in sel:
        blocks = parse_chapter(z.read(h))
        num = None
        head = ""
        for b in blocks:
            if b["type"] == "head" and b["text"].upper().startswith("CHAPTER"):
                m = re.search(r"(\d+)", b["text"])
                if m:
                    num = int(m.group(1))
                break
        title_en = ""
        seen_chap = False
        for b in blocks:
            if b["type"] == "head":
                if b["text"].upper().startswith("CHAPTER"):
                    seen_chap = True
                    continue
                if seen_chap:
                    title_en = b["text"]
                    break
                if not head:
                    head = b["text"]
        clean_title = re.sub(r"⟦/?i⟧", "", title_en or head).strip()
        if title_en:
            title_en = clean_title
        elif head:
            head = clean_title
        if num is None:
            # front matter / epilogue
            cid = "front_ety" if "Etymology" in label else (
                "front_ext" if "Extracts" in label else (
                    "epilogue" if "EPILOGUE" in label.upper() else
                    re.sub(r"\W+", "_", label.lower())))
            title_en = head or label
        else:
            cid = f"ch{num:03d}"
        title_zh = CHAPTER_ZH.get(num) or TITLE_ZH.get(label) or (
            "尾声" if cid == "epilogue" else label)
        # drop the two heading blocks from the body (kept in metadata)
        if num is not None:
            body = [b for b in blocks if b["type"] != "head"]
        else:
            body = [b for b in blocks if not (b["type"] == "head"
                                              and b["text"].strip().upper() in ("EPILOGUE",))]
        words = sum(len(re.sub(r"⟦/?i⟧", "", b.get("text", " ".join(b.get("lines", [])))).split())
                    for b in body)
        total_words += words
        rec = {"id": cid, "num": num, "label": label, "title_en": title_en,
               "title_zh": title_zh, "words": words, "blocks": body}
        with open(os.path.join(OUT, cid + ".json"), "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=1)
        print(f"{cid:10s} {str(num):>4s} {words:6d}w  {title_en[:44]:44s} {title_zh}")
    print("chapters:", len(sel), "words:", total_words)


if __name__ == "__main__":
    main()
