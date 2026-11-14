
"""Rebuild the six criticised books with the structure they actually have.

Everything here is mechanical. The text is taken as translated; this script only
decides what is a heading, what is a scene, what is verse, and where a part starts.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import build_epub as BE

OUT = os.path.join(ROOT, "out")
CJK = re.compile(r"[\u4e00-\u9fff]")
ROMAN = re.compile(r"^[-—–\s]*(?:第?[ivxlcdmIVXLCDM]+|第?[一二三四五六七八九十百]+|\d+)[-—–\s.]*$")
CN_NUM = "零一二三四五六七八九十"


def paras(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def chapter_text(root: str, cid: str) -> list[str]:
    files = sorted(glob.glob(os.path.join(root, cid, "c*", "final.txt")))
    return paras("\n\n".join(open(f, encoding="utf-8").read() for f in files))


def cids(root: str) -> list[str]:
    return sorted(os.path.basename(d) for d in glob.glob(os.path.join(root, "c*"))
                  if os.path.isdir(d))


def is_heading_like(p: str, title: str = "") -> bool:
    """A short paragraph that only repeats the chapter title or its number."""
    s = p.strip().rstrip("。.")
    if len(s) > 24:
        return False
    if title and (s == title or s.replace(" ", "") == title.replace(" ", "")):
        return True
    if ROMAN.match(s):
        return True
    return False


# ── per-book rules ─────────────────────────────────────────────────────────────

DUBLIN = ["姊妹们", "一次遭遇", "阿拉比", "伊芙琳", "赛车之后", "两个浪子",
          "寄宿公寓", "一朵小云", "无独有偶", "泥土", "一件悲痛的事",
          "常春藤日", "一位母亲", "恩典", "死者"]

MONDAY = ["闹鬼的宅子", "一个社团", "星期一或星期二", "一部未写的小说",
          "弦乐四重奏", "蓝与绿", "邱园", "墙上的斑点"]

IMMENSEE = ["老人", "两个孩子", "林中", "孩子站在路旁", "在家", "一封信",
            "茵梦湖", "母亲的心愿", "伊丽莎白", "老人"]

# Scene headings in the order the play has them. The body text uses slightly
# different wording from the translator's own table of contents, and one heading is
# glued to the stage direction that follows it, so matching is sequential: a paragraph
# only starts the *next* expected scene, never any scene.
FAUST_SCENES = [
    ("献词", "献词"),
    ("剧场序曲", "剧场序曲"),
    ("天上序幕", "天上序曲"),
    ("夜", "夜"),
    ("城门前", "城门外"),
    ("书斋", "书斋（一）"),
    ("书房", "书斋（二）"),
    ("莱比锡的奥尔巴赫地窖", "莱比锡奥耶尔巴赫地下酒室"),
    ("女巫的厨房", "魔女厨房"),
    ("街道（一）", "街道（一）"),
    ("傍晚", "傍晚"),
    ("散步", "散步"),
    ("邻居家", "邻妇之家"),
    ("街道（二）", "街道（二）"),
    ("园中", "园中"),
    ("园中小屋", "园中小亭"),
    ("林中洞府", "林中洞穴"),
    ("格蕾琴的闺房", "格蕾琴的闺房"),
    ("玛尔滕的园子", "玛尔特的花园"),
    ("井边", "井边"),
    ("茨温格宫", "城墙角"),
    ("夜。格蕾琴家门前的街道", "夜·格蕾琴门前"),
    ("教堂", "教堂"),
    ("沃尔普吉斯之夜", "瓦尔普吉斯之夜"),
    ("瓦尔普吉斯之夜之梦", "瓦尔普吉斯之夜梦"),
    ("阴霾的日子。田野", "阴郁的日子·旷野"),
    ("夜，旷野", "夜·旷野"),
    ("牢狱", "地牢"),
]


def build_dubliners() -> dict:
    root = os.path.join(ROOT, "work_pub", "dubliners", "out")
    ids = [c for c in cids(root) if chapter_text(root, c)]
    items = []
    for title, cid in zip(DUBLIN, ids):
        ps = chapter_text(root, cid)
        if ps and len(ps[0]) <= 24 and not ps[0].endswith("。"):
            ps = ps[1:]
        items.append({"title": title, "texts": ps, "types": ["p"] * len(ps)})
    cfg = {"title": "都柏林人", "sub": "Dubliners", "author": "詹姆斯·乔伊斯",
           "src": "Dubliners", "uid": "urn:pub-dubliners-zh",
           "note": "据一九一四年伦敦格兰特·理查兹初版译出"}
    return {"cfg": cfg, "items": items, "path": os.path.join(OUT, "都柏林人（坟头草译）.epub")}


def build_monday() -> dict:
    root = os.path.join(ROOT, "work_pub", "mondaytuesday", "out")
    ids = [c for c in cids(root) if chapter_text(root, c)]
    # c001 is the title page, c002 was dropped by the extractor; six stories remain
    # in order. The two missing ones are appended from the supplementary file.
    items = []
    have = list(zip(MONDAY[:2] + MONDAY[3:], ids))   # placeholder, rebuilt below
    have = []
    order = ["闹鬼的宅子", "一个社团", "一部未写的小说", "弦乐四重奏", "邱园", "墙上的斑点"]
    for title, cid in zip(order, ids):
        ps = chapter_text(root, cid)
        if ps and len(ps[0]) <= 24 and not ps[0].endswith("。"):
            ps = ps[1:]
        items.append({"title": title, "texts": ps, "types": ["p"] * len(ps)})
    extra = os.path.join(ROOT, "pipeline_fix", "monday_extra.json")
    if os.path.exists(extra):
        add = json.load(open(extra, encoding="utf-8"))
        for title in ("星期一或星期二", "蓝与绿"):
            if title in add:
                ps = [p for p in add[title] if p.strip()]
                types = ["center" if p in ("绿色", "蓝色") else "p" for p in ps]
                items.append({"title": title, "texts": ps, "types": types})
        items.sort(key=lambda it: MONDAY.index(it["title"]))
    cfg = {"title": "星期一或星期二", "sub": "Monday or Tuesday", "author": "弗吉尼亚·伍尔夫",
           "src": "Monday or Tuesday", "uid": "urn:pub-monday-zh",
           "note": "据一九二一年纽约哈考特布雷斯初版译出"}
    return {"cfg": cfg, "items": items, "path": os.path.join(OUT, "星期一或星期二（坟头草译）.epub")}


def build_voyage() -> dict:
    root = os.path.join(ROOT, "work_pub", "voyageout", "out")
    ids = [c for c in cids(root) if chapter_text(root, c)]
    items = []
    for i, cid in enumerate(ids, 1):
        ps = chapter_text(root, cid)
        if ps and re.match(r"^第[一二三四五六七八九十百]+章$", ps[0].strip()):
            ps = ps[1:]
        n = i
        title = f"第{cn(n)}章"
        items.append({"title": title, "texts": ps, "types": ["p"] * len(ps)})
    cfg = {"title": "远航", "sub": "The Voyage Out", "author": "弗吉尼亚·伍尔夫",
           "src": "The Voyage Out", "uid": "urn:pub-voyageout-zh",
           "note": "据一九一五年伦敦达克沃斯初版译出"}
    return {"cfg": cfg, "items": items, "path": os.path.join(OUT, "远航（坟头草译）.epub")}


def build_immensee() -> dict:
    root = os.path.join(ROOT, "work_gutenberg", "immensee", "out")
    ids = [c for c in cids(root) if chapter_text(root, c)]
    ids = [c for c in ids if c != "c001"]          # Gutenberg boilerplate
    items = []
    for i, (title, cid) in enumerate(zip(IMMENSEE, ids)):
        ps = chapter_text(root, cid)
        if ps and len(ps[0]) <= 24:
            ps = ps[1:]
        # The frame story opens and closes with 老人; the closing one is marked so the
        # contents list does not show the same heading twice.
        if title == "老人" and i > 0:
            title = "老人（尾声）"
        items.append({"title": title, "texts": ps, "types": ["p"] * len(ps)})
    cfg = {"title": "茵梦湖", "sub": "Immensee", "author": "特奥多尔·施托姆",
           "src": "Immensee", "uid": "urn:pub-immensee-zh",
           "note": "据一八五一年柏林初版译出"}
    return {"cfg": cfg, "items": items, "path": os.path.join(OUT, "茵梦湖（坟头草译）.epub")}


def build_faust() -> dict:
    root = os.path.join(ROOT, "work_pub", "faust", "out")
    ps = chapter_text(root, "c001")
    start = ps.index("献词", 28) if "献词" in ps[28:] else 28
    ps = ps[start:]

    items: list[dict] = []
    cur: list[str] = []
    types: list[str] = []
    cur_title = None
    expect = 0
    for p in ps:
        if expect < len(FAUST_SCENES):
            pat, title = FAUST_SCENES[expect]
            rest = None
            if p.strip() == pat:
                rest = ""
            elif p.startswith(pat + "。") or p.startswith(pat + "，"):
                rest = p[len(pat) + 1:].strip()
            if rest is not None:
                if cur_title is not None:
                    items.append({"title": cur_title, "texts": cur, "types": types})
                cur_title, cur, types = title, [], []
                expect += 1
                if rest:
                    cur.append(rest)
                    types.append("verse" if "\n" in rest else "p")
                continue
        if cur_title is None:
            continue
        cur.append(p)
        types.append("verse" if "\n" in p else "p")
    if cur_title is not None:
        items.append({"title": cur_title, "texts": cur, "types": types})
    cfg = {"title": "浮士德", "sub": "悲剧第一部", "author": "约翰·沃尔夫冈·冯·歌德",
           "src": "Faust: Der Tragödie erster Teil", "uid": "urn:pub-faust-zh",
           "note": "据一八〇八年第一部初版译出"}
    return {"cfg": cfg, "items": items, "path": os.path.join(OUT, "浮士德上册（坟头草译）.epub")}


PART_STARTS = {"c013": "第二部", "c020": "第三部", "c027": "第四部"}
PART_TAIL = re.compile(r"^(第[一二三四]部终?|…+|小说终)$")


def build_fortunata() -> dict:
    root = os.path.join(ROOT, "work_gutenberg", "fortunata", "out")
    ids = [c for c in cids(root) if chapter_text(root, c)]
    items, part = [], "第一部"
    for cid in ids:
        ps = chapter_text(root, cid)
        if len(ps) < 3:
            continue
        # para 0 is the chapter numeral, para 1 the chapter's own title
        if ROMAN.match(ps[0]):
            title = ps[1].strip().rstrip("。")
            body = ps[2:]
            if title in ("终", "结局"):
                title = "终章"
        else:
            title, body = ps[0].strip(), ps[1:]
        body = [p for p in body if not (len(p) <= 8 and ROMAN.match(p))]
        # part transitions are printed at the tail of the previous chapter
        cut = len(body)
        for i in range(len(body) - 1, max(-1, len(body) - 6), -1):
            if PART_TAIL.match(body[i].strip()):
                cut = i
        body = body[:cut]
        if cid in PART_STARTS:
            part = PART_STARTS[cid]
        items.append({"title": title, "texts": body, "types": ["p"] * len(body),
                      "part": part, "part_kicker": ""})
    cfg = {"title": "福尔图娜塔与哈辛塔", "sub": "两个已婚女人的故事",
           "author": "贝尼托·佩雷斯·加尔多斯",
           "src": "Fortunata y Jacinta", "uid": "urn:pub-fortunata-zh",
           "note": "据一八八六至八七年马德里初版译出"}
    return {"cfg": cfg, "items": items, "path": os.path.join(OUT, "福尔图娜塔与哈辛塔（坟头草译）.epub")}


def cn(n: int) -> str:
    if n <= 10:
        return CN_NUM[n]
    if n < 20:
        return "十" + CN_NUM[n - 10]
    return CN_NUM[n // 10] + "十" + (CN_NUM[n % 10] if n % 10 else "")


BUILDERS = {"dubliners": build_dubliners, "monday": build_monday, "voyage": build_voyage,
            "immensee": build_immensee, "faust": build_faust, "fortunata": build_fortunata}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    want = sys.argv[1:] or list(BUILDERS)
    for key in want:
        spec = BUILDERS[key]()
        items = spec["items"]
        print(f"== {key}: {len(items)} chapters")
        for it in items:
            print(f"   {it.get('part',''):4s} {it['title']:24s} {len(it['texts']):4d} paras"
                  f"  verse={sum(1 for t in it['types'] if t=='verse')}")
        if "--dry" in os.environ.get("FIX_MODE", ""):
            continue
        r = BE.build(spec["cfg"], items, spec["path"])
        print("   ->", r)


if __name__ == "__main__":
    main()
