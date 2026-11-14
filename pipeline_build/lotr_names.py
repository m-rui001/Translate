"""魔戒 termbase, hand-checked against the 31 good chapters.

Automatic extraction from co-occurrence produced garbage ("Gandalf" -> "真可惜",
"Treebeard" -> "早上好") because dialogue tags sit in the same paragraph as the name.
The reliable source is the frequency list of the book's own Chinese: every entry below
is a form that occurs many times in the existing translations, so it is a phrase a human
already settled on.

Format: english -> chinese. Only proper nouns, places, and Tolkien's invented measures.
The retranslation prompt renders this as a flat list; `check_names.py` then verifies that
a newly translated chapter uses the same forms.
"""
from __future__ import annotations

# People
PEOPLE = {
    "Frodo": "佛罗多",
    "Sam": "山姆",
    "Samwise": "山姆怀斯",
    "Gamgee": "甘姆吉",
    "Pippin": "皮平",
    "Peregrin": "佩里格林",
    "Merry": "梅里",
    "Meriadoc": "梅里雅达克",
    "Gandalf": "甘道夫",
    "Mithrandir": "米斯兰迪尔",
    "Aragorn": "阿拉贡",
    "Strider": "大步佬",
    "Boromir": "波罗莫",
    "Legolas": "勒苟拉斯",
    "Gimli": "金雳",
    "Gloin": "葛罗音",
    "Bilbo": "比尔博",
    "Baggins": "巴金斯",
    "Gollum": "咕鲁",
    "Smeagol": "史麦戈",
    "Elrond": "埃尔隆德",
    "Celeborn": "凯勒鹏",
    "Galadriel": "凯兰崔尔",
    "Treebeard": "树胡",
    "Saruman": "萨鲁曼",
    "Theoden": "希优顿",
    "Eomer": "伊欧墨",
    "Eowyn": "伊欧玟",
    "Faramir": "法拉墨",
    "Denethor": "迪耐瑟",
    "Beregond": "贝瑞刚德",
    "Gildor": "吉尔多",
    "Inglorion": "英格洛瑞安",
    "Tom Bombadil": "汤姆·邦巴迪尔",
    "Bombadil": "邦巴迪尔",
    "Maggot": "马戈特",
    "Haldir": "哈尔迪尔",
    "Shagrat": "沙格拉特",
    "Ingold": "英戈尔德",
    "Bergil": "贝吉尔",
    "Elbereth": "埃尔贝瑞丝",
    "Shadowfax": "捷影",
    "Isildur": "伊西铎",
    "Elendil": "伊兰迪尔",
    "Anarion": "安那瑞安",
    "Sauron": "索伦",
    "Lobelia": "罗贝拉",
    "Lotho": "洛索",
    "Butterbur": "黄油菊",
    "Farmer Maggot": "马戈特农夫",
}

# Places
PLACES = {
    "Shire": "夏尔",
    "Hobbiton": "霍比屯",
    "Bag End": "袋底洞",
    "Bree": "布理",
    "Rivendell": "瑞文戴尔",
    "Lothlorien": "罗瑞安",
    "Lorien": "罗瑞安",
    "Moria": "摩瑞亚",
    "Khazad-dum": "凯萨督姆",
    "Isengard": "艾辛格",
    "Rohan": "洛汗",
    "Gondor": "刚铎",
    "Rohirrim": "洛希尔人",
    "Minas Tirith": "米那斯提力斯",
    "Minas Morgul": "米那斯魔窟",
    "Mordor": "魔多",
    "Mount Doom": "末日火山",
    "Cracks of Doom": "末日罅隙",
    "Orodruin": "欧洛都因",
    "Barad-dur": "巴拉多",
    "Fangorn": "法贡",
    "Edoras": "伊多拉斯",
    "Helm's Deep": "圣盔谷",
    "Osgiliath": "奥斯吉利亚斯",
    "Ithilien": "伊希利恩",
    "Anorien": "阿诺瑞恩",
    "Pelennor": "佩兰诺",
    "Anduin": "安都因",
    "Emyn Arnen": "埃敏阿尔嫩",
    "Cair Andros": "凯尔安卓斯",
    "Rammas Echor": "拉马斯埃霍尔",
    "Harlond": "哈隆德",
    "Lossarnach": "罗斯那赫",
    "Lebennin": "雷本宁",
    "Cirith Ungol": "西力斯昂哥",
    "Shelob": "尸罗",
    "Bucklebury": "雄鹿堡",
    "Bucklebury Ferry": "雄鹿堡渡口",
    "Crickhollow": "溪谷地",
    "Brandywine": "烈酒河",
    "Old Forest": "老林",
    "Barrow-downs": "古墓岗",
    "Weathertop": "风云顶",
    "Trollshaws": "食人妖森林",
    "Eregion": "伊瑞詹",
    "Hollin": "冬青郡",
    "Caradhras": "卡罗德拉斯",
    "Dimrill Dale": "暗溪谷",
    "Silverlode": "银流河",
    "Nimrodel": "宁若戴尔",
    "Cerin Amroth": "凯林阿姆洛斯",
    "Emyn Muil": "埃敏穆伊",
    "Dead Marshes": "死亡沼泽",
    "Black Gate": "黑门",
    "Morannon": "魔兰农",
    "Udun": "乌顿",
    "Nurn": "努恩",
    "Ephel Duath": "艾菲尔多阿斯",
    "Bay of Belfalas": "贝尔法拉斯湾",
    "Umbar": "昂巴",
    "Harad": "哈拉德",
    "Khand": "侃德",
    "Rhun": "卢恩",
    "Erebor": "孤山",
    "Dale": "河谷镇",
    "Mirkwood": "幽暗密林",
    "Beorn": "贝奥恩",
    "Redhorn": "红角峰",
    # the white tower of the Citadel, named for the Steward Ecthelion. The old draft called
    # it 埃克西里昂之塔 and a re-translation flattened it to 白塔, losing the dedication
    "Ecthelion": "埃克西里昂",
    "Tower of Ecthelion": "埃克西里昂之塔",
    "Citadel": "高庭",
    "White Tree": "白树",
    "Argonath": "亚苟那斯",
    "Pillars of the Kings": "王者之柱",
    "Rath Dinen": "拉斯迪能",
}

# Things, and Tolkien's measures
THINGS = {
    "Ring": "魔戒",
    "the Ring": "魔戒",
    "One Ring": "至尊魔戒",
    "Red Book": "西界红皮书",
    "Red Book of Westmarch": "西界红皮书",
    "palantir": "真知晶石",
    "palantiri": "真知晶石",
    "mithril": "秘银",
    "silmaril": "精灵宝钻",
    "Anduril": "安都瑞尔",
    "Narsil": "纳西尔",
    "Sting": "刺针",
    "Glamdring": "敌击剑",
    "Phial of Galadriel": "凯兰崔尔的水晶瓶",
    "lembas": "兰巴斯",
    "miruvor": "米卢活",
    "athe-las": "王叶草",
    "Athelas": "王叶草",
    "kingsfoil": "王叶草",
    "Westron": "通用语",
    "Sindarin": "辛达林语",
    "Quenya": "昆雅语",
    "Ent": "树人",
    "Ents": "树人",
    "Nazgul": "戒灵",
    "Black Riders": "黑骑手",
    "Ringwraiths": "戒灵",
    "Wargs": "恶狼",
    "Orcs": "半兽人",
    "Uruk-hai": "强兽人",
    "Hobbits": "霍比特人",
    "halfling": "半身人",
    "Elves": "精灵",
    "Dwarves": "矮人",
    "Elessar": "伊力萨王",
    "Evenstar": "暮星",
    "leagues": "里格",
    "league": "里格",
    # the White Tower is "fifty fathoms from its base to the pinnacle" in the source, so
    # 英寻 is correct here -- the old draft's 五十赛因特 was a mistranslation, not a house
    # convention, and 赛因特/ranga is a different (unused) Tolkien measure
    "fathom": "英寻",
    "fathoms": "英寻",
    "lar": "拉尔",
    "tharni": "萨尼",
}

ALL = {}
ALL.update(PEOPLE)
ALL.update(PLACES)
ALL.update(THINGS)

# forms the old draft used that a re-translation must not replace with a paraphrase
MUST_USE = [
    "埃克西里昂之塔", "洛希尔人", "亚苟那斯", "捷影", "伊兰迪尔",
    "沃伦迪尔", "米那斯提力斯", "拉马斯埃霍尔", "阿诺瑞恩", "埃敏阿尔嫩", "伊希利恩",
    "奥斯吉利亚斯", "佩兰诺", "安都因", "白树", "真知晶石", "刚铎", "洛汗",
]


def render(limit: int = 90) -> str:
    """A compact glossary for the prompt, most important names first."""
    items = sorted(ALL.items(), key=lambda kv: (-len(kv[0].split()), kv[0]))
    head = "；".join(f"{en}={zh}" for en, zh in items[:limit])
    must = "、".join(MUST_USE)
    return (f"必用译名（不得改写、不得意译）：{head}\n"
            f"以下译名在本章务必原样出现：{must}")


if __name__ == "__main__":
    print(render())
