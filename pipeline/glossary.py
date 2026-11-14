"""Canonical English -> Chinese glossary for the Middle-earth corpus.

Names follow the established Chinese Tolkien nomenclature (世纪文景／译林 通行译名),
chosen for coherence and readability. The pipeline injects only the entries that
actually occur in the chunk being translated, plus a small core set.
"""
from __future__ import annotations

import re

G = {
    # ── 霍比特人
    "Baggins": "巴金斯", "Frodo": "佛罗多", "Bilbo": "比尔博",
    "Samwise": "山姆怀斯", "Sam": "山姆", "Gamgee": "甘姆吉",
    "Meriadoc": "梅里雅达克", "Merry": "梅里", "Brandybuck": "烈酒鹿",
    "Peregrin": "佩里格林", "Pippin": "皮平", "Took": "图克",
    "Sackville-Baggins": "萨克维尔−巴金斯", "Lobelia": "罗贝拉", "Otho": "奥索",
    "Lotho": "洛索", "Old Took": "老图克", "Gaffer": "老爹",
    "Hamfast": "汉姆法斯特", "Drogo": "德罗戈", "Primula": "普丽缪拉",
    "Fredegar": "弗雷德加", "Fatty": "胖子", "Folco": "福尔科",
    "Farmer Maggot": "马戈特农夫", "Maggot": "马戈特",
    "Ted Sandyman": "泰德·山迪曼", "Sandyman": "山迪曼",
    "Daddy Twofoot": "双足老爹", "Old Noakes": "老诺克斯",
    "Farmer Cotton": "科顿农夫", "Rosie": "罗西", "Cotton": "科顿",
    "Halfast": "哈法斯特", "Daddy": "老爹", "Gorbadoc": "戈巴多克",
    "Buckland": "烈酒鹿地", "Bree": "布理", "Hobbiton": "霍比屯",
    "Bywater": "傍水镇", "the Shire": "夏尔", "Bag End": "袋底洞",
    "Brandywine": "烈酒河", "Crickhollow": "溪谷地",
    "Michel Delving": "米丘窟", "Tuckborough": "图克堡",
    "Hobbiton Hill": "霍比屯小丘", "The Water": "河水",
    # ── 魔戒同盟
    "Gandalf": "甘道夫", "Aragorn": "阿拉贡", "Strider": "大步佬",
    "Boromir": "波罗莫", "Legolas": "勒苟拉斯", "Gimli": "金雳",
    "Elrond": "埃尔隆德", "Galadriel": "凯兰崔尔", "Celeborn": "凯勒鹏",
    "Haldir": "哈尔迪尔", "Arwen": "阿尔温", "Glorfindel": "葛罗芬戴尔",
    "Erestor": "埃瑞斯托", "Galdor": "加尔多", "Lindir": "林迪尔",
    "Bill": "比尔", "Shadowfax": "捷影", "Asfaloth": "阿斯法洛斯",
    "Nazgûl": "戒灵", "Ringwraith": "戒灵", "Black Riders": "黑骑士",
    "Witch-king": "巫王", "Sauron": "索伦", "Saruman": "萨鲁曼",
    "Gollum": "咕鲁", "Sméagol": "史麦戈", "Gríma": "格里马",
    "Wormtongue": "巧言", "Shelob": "尸罗", "Sharkey": "沙基",
    "Mouth of Sauron": "索伦之口", "Uglúk": "乌格鲁克",
    "Grishnákh": "格里什纳赫", "Shagrat": "夏格拉", "Gorbag": "哥巴格",
    "Lugbúrz": "卢格伯兹", "Lurtz": "路兹", "Snaga": "斯纳加",
    # ── 洛汗与刚铎
    "Théoden": "希优顿", "Éowyn": "伊欧玟", "Éomer": "伊欧墨",
    "Théodred": "希优德雷德", "Háma": "哈玛", "Gamling": "加姆林",
    "Grímbold": "格里姆博德", "Erkenbrand": "鄂肯布兰德",
    "Denethor": "迪耐瑟", "Faramir": "法拉墨", "Imrahil": "印拉希尔",
    "Beregond": "贝尔贡", "Bergil": "贝吉尔", "Ioreth": "伊欧瑞斯",
    "Ghân-buri-Ghân": "甘−布里−甘", "Woses": "野人", "Damrod": "丹姆罗德",
    "Mablung": "马伯龙", "Anborn": "安本", "Hirgon": "希尔贡",
    "Ingold": "印格德", "Gandalf's horse": "捷影",
    "Dernhelm": "德恩海尔姆", "Elfhelm": "艾尔夫海尔姆",
    "Dunharrow": "登哈洛", "Edoras": "伊多拉斯", "Helm's Deep": "圣盔谷",
    "Hornburg": "号角堡", "Meduseld": "梅杜西金殿",
    "Rohan": "洛汗", "Gondor": "刚铎", "Minas Tirith": "米那斯提力斯",
    "Minas Morgul": "米那斯魔窟", "Osgiliath": "奥斯吉力亚斯",
    "Pelennor": "帕兰诺", "Rammas Echor": "拉马斯埃霍尔",
    "Lossarnach": "罗萨那奇", "Lebennin": "雷本宁", "Lamedon": "拉梅顿",
    "Anórien": "阿诺瑞安", "Ithilien": "伊西立安",
    "Henneth Annûn": "汉奈斯安努恩", "Cirith Ungol": "西力斯昂哥",
    "Cirith Gorgor": "西力斯葛哥", "Morannon": "摩拉南", "Udûn": "乌顿",
    "Narchost": "纳科斯", "Carchost": "卡尔科斯", "Cormallen": "科玛伦",
    "Mering Stream": "分水溪", "Erech": "伊瑞赫", "Dimholt": "暗林",
    "Paths of the Dead": "亡者之路", "Druadan": "德鲁阿丹",
    "Rath Dínen": "拉斯狄能", "Fen Hollen": "芬霍楞",
    "Houses of the Dead": "亡者之屋", "Steward": "宰相",
    "Citadel": "圣域", "White Tower": "白塔", "Tower of Ecthelion": "埃克西里昂之塔",
    "Key of Orthanc": "欧散克之钥",
    # ── 精灵、矮人与上古
    "Elendil": "伊兰迪尔", "Isildur": "埃西铎", "Anárion": "阿纳瑞安",
    "Gil-galad": "吉尔加拉德", "Celebrimbor": "凯勒布理鹏",
    "Fëanor": "费诺", "Lúthien": "露西安", "Beren": "贝伦",
    "Tinúviel": "缇努维尔", "Eärendil": "埃雅仁迪尔", "Elwing": "爱尔温",
    "Thingol": "庭葛", "Melian": "美丽安", "Morgoth": "魔苟斯",
    "Túrin": "图林", "Húrin": "胡林", "Tuor": "图尔",
    "Númenor": "努曼诺尔", "Dúnedain": "登丹人", "Dúnadan": "登丹人",
    "Westernesse": "西方之地", "Last Alliance": "最后联盟",
    "Durin": "都灵", "Balin": "巴林", "Thorin": "索林", "Dáin": "戴因",
    "Glóin": "葛罗音", "Bard": "巴德", "Brand": "布兰德",
    "Thranduil": "瑟兰督伊", "Elbereth": "埃尔贝瑞丝",
    "Treebeard": "树胡", "Quickbeam": "快木", "Ent": "树人", "Huorn": "胡恩",
    "Bregalad": "布雷加拉德", "Fimbrethil": "芬布瑞希尔",
    "Tom Bombadil": "汤姆·邦巴迪尔", "Goldberry": "金莓",
    "Barrow-wight": "古冢尸妖", "Old Man Willow": "老柳头",
    "Butterbur": "奶油伯", "Barliman": "巴力曼", "Nob": "诺布", "Bob": "巴伯",
    "Bill Ferny": "比尔·蕨叶", "Ferny": "蕨叶", "Harry": "哈利",
    # ── 地名
    "Rivendell": "瑞文戴尔", "Lothlórien": "罗斯洛立安", "Lórien": "罗斯洛立安",
    "Moria": "摩瑞亚", "Khazad-dûm": "卡扎督姆", "Isengard": "艾辛格",
    "Orthanc": "欧散克塔", "Fangorn": "法贡森林", "Rauros": "拉洛斯",
    "Emyn Muil": "艾明莫尔", "Dead Marshes": "死亡沼泽", "Noman-lands": "无人之地",
    "Mordor": "魔多", "Mount Doom": "末日火山", "Orodruin": "末日山",
    "Barad-dûr": "巴拉多", "Weathertop": "风云顶", "Amon Sûl": "阿蒙苏尔",
    "Barrow-downs": "古冢岗", "Old Forest": "老林子", "Grey Havens": "灰港",
    "Eregion": "伊瑞詹", "Hollin": "冬青郡", "Caradhras": "红角峰",
    "Dimrill Dale": "暗溪谷", "Celebrant": "银流河", "Anduin": "安都因",
    "Argonath": "亚苟那斯", "Nen Hithoel": "宁希索尔",
    "Tol Brandir": "托尔布兰迪尔", "the Great River": "大河",
    "Mirkwood": "幽暗密林", "Dunland": "登兰德", "Erebor": "孤山",
    "Dale": "河谷城", "Esgaroth": "长湖镇", "Iron Hills": "铁丘陵",
    "Gap of Rohan": "洛汗豁口", "White Mountains": "白色山脉",
    "Misty Mountains": "迷雾山脉", "Amon Hen": "阿蒙汉",
    "Amon Lhaw": "阿蒙罗", "Torech Ungol": "托瑞克昂哥",
    "Minas Anor": "米那斯阿诺尔", "Minas Ithil": "米那斯伊西尔",
    "Bay of Belfalas": "贝尔法拉斯湾", "Ethir Anduin": "安都因河口",
    "Tarlang's Neck": "塔朗隘口", "Pelargir": "佩拉格", "Dol Amroth": "多阿姆洛斯",
    # ── 山川地名（书五书六密集出现，误译会直接伤忠实度）
    "Mindolluin": "明多立安", "Ered Nimrais": "白峰山脉", "White Mountains": "白色山脉",
    "Snowbourn": "雪河", "Snowy River": "雪河", "Entwash": "恩特河",
    "Dwimorberg": "幽影山", "Dimholt": "暗林", "Doorstone": "门石",
    "Eretriel": "埃瑞崔尔", "Harrowdown": "哈罗丘", "Deephallow": "深潭",
    "Belfalas": "贝尔法拉斯", "Dor-en-Ernil": "亲王之地", "Calenardhon": "卡勒纳宏",
    "Halifirien": "哈利菲仁", "Amon Anwar": "希望之丘", "Firienwood": "哈利菲仁林",
    "Langstrand": "长滩", "Lamedon": "拉梅顿", "Ringló": "林罗河",
    "Mering": "分水", "Withywindle": "柳条河", "Shirebourn": "夏尔河",
    "Gladden": "花楸河", "Limlight": "银雾河", "Entwade": "恩特滩",
    "Riddlemount": "谜语山", "Barrowfield": "古冢地", "Hornburg": "号角堡",
    "Deeping Coomb": "深谷", "Deeping": "深谷", "Saruman's ring": "萨鲁曼之戒",
    # ── 名物
    "One Ring": "至尊戒", "the Ring": "魔戒", "Red Book": "西界红皮书",
    "palantír": "真知晶球", "elanor": "星辰花", "niphredil": "宁芙瑞迪尔",
    "mallorn": "梅隆树", "mithril": "秘银", "lembas": "兰巴斯",
    "cram": "克拉姆", "miruvor": "米鲁伏尔", "Silmarils": "精灵宝钻",
    "Andúril": "安都瑞尔", "Narsil": "纳西尔", "Sting": "刺针",
    "Glamdring": "敌击剑", "Orcrist": "兽咬剑",
    "Phial of Galadriel": "凯兰崔尔之瓶", "mûmakil": "猛玛象",
    "oliphaunt": "大象", "mathom": "珍玩", "Silmaril": "精灵宝钻",
    "Orc": "半兽人", "Uruk-hai": "强兽人", "Goblin": "哥布林",
    "Warg": "座狼", "Oliphaunt": "大象", "Black Breath": "黑息",
    "Wraith-world": "幽界", "the Shadow": "魔影",
}

CORE = ["Frodo", "Bilbo", "Sam", "Merry", "Pippin", "Gandalf", "Aragorn",
        "the Ring", "the Shire", "Hobbiton", "Bag End", "Sauron"]

_PUNCT = ".,;:!?\"'()[]–—-’‘“”´¨ "


def _present(key: str, text: str) -> bool:
    stem = key
    # crude but effective: match the key (or its first word if multiword) anywhere
    if re.search(r"\b" + re.escape(stem) + r"\b", text):
        return True
    parts = [p for p in re.split(r"[\s\-]", stem) if len(p) > 3]
    return any(re.search(r"\b" + re.escape(p), text) for p in parts)


def relevant(text: str, limit: int = 120) -> dict[str, str]:
    """Glossary entries occurring in this source chunk, plus the core set."""
    out = {}
    for k in CORE:
        if k in G:
            out[k] = G[k]
    for k, v in G.items():
        if k in out:
            continue
        if _present(k, text):
            out[k] = v
        if len(out) >= limit:
            break
    return out


def render(entries: dict[str, str]) -> str:
    if not entries:
        return ""
    lines = [f"{k} = {v}" for k, v in sorted(entries.items())]
    return "【专名对照表（必须严格照用）】\n" + "\n".join(lines)
