"""English → Chinese glossary for Moby-Dick.

Naming policy: use the established Chinese renderings (吴钧陶/罗山川/成时 等通行译名),
which we verified against the published 中央编译 reference text where possible
(裴廓德, 亚哈, 以实玛利, 魁魁格, 斯塔布, 斯达巴克, 弗拉斯克, 塔希蒂格, 达格, 皮普,
费达拉, 比尔达, 皮勒, 梅普尔, 耶罗波恩 …). Where the reference is idiosyncratic we
still keep the wider convention when it is clearly more familiar to readers.

Only entries whose English form actually occurs in the chunk are injected.
"""
from __future__ import annotations

import re

G = {
    # ── 人物：裴廓德号
    "Ahab": "亚哈", "Ishmael": "以实玛利", "Queequeg": "魁魁格",
    "Starbuck": "斯达巴克", "Stubb": "斯塔布", "Flask": "弗拉斯克",
    "Tashtego": "塔希蒂格", "Daggoo": "达格", "Pip": "皮普",
    "Fedallah": "费达拉", "Parsee": "祆教徒", "Stubb’s": "斯塔布的",
    "Ahab’s": "亚哈的", "Queequeg’s": "魁魁格的", "Starbuck’s": "斯达巴克的",
    "Bulkington": "布尔金顿", "Mapple": "梅普尔", "Father Mapple": "梅普尔神甫",
    "Peleg": "皮勒", "Captain Peleg": "皮勒船长", "Bildad": "比尔达",
    "Captain Bildad": "比尔达船长", "Hussey": "胡赛", "Mrs. Hussey": "胡赛太太",
    "Radney": "拉德尼", "Steelkilt": "斯蒂尔基尔特", "Perth": "珀斯",
    "Gabriel": "加百列", "Elijah": "伊莱贾", "Yojo": "约约",
    "Lakeman": "莱克曼", "Bunger": "邦格", "Macey": "马西",
    "Archy": "阿基", "Cabaco": "卡巴科", "Fleece": "弗利斯",
    "Sleet": "斯利特", "Derick": "德里克", "Dough-Boy": "面团仔",
    "Manxman": "马恩岛人", "Guernsey-man": "格恩西人", "Tranquo": "特兰科",
    "Tranque": "特兰克", "Scoresby": "斯科斯比", "Cuvier": "居维叶",
    "Beale": "比尔", "Colnett": "科尔内特", "Langsdorff": "朗斯多夫",
    "Samuel Enderby": "撒母耳·恩德比", "Captain Cook": "库克船长", "Owen": "欧文",
    "Harris": "哈里斯", "Browne": "布朗", "Mayhew": "梅休",
    "Charley Coffin": "查理·咖芬", "Peter Coffin": "彼得·咖芬",
    # NOTE: 裸 Cook 是船上的厨子（ch064 弗利斯），不是库克船长。
    # 术语表只收 "Captain Cook"，否则会污染普通名词——ch001 与 ch064 都栽在这上头。
    # ── 人物：圣经与古典
    "Jonah": "约拿", "Leviathan": "利维坦", "Job": "约伯", "Noah": "挪亚",
    "Solomon": "所罗门", "Jeroboam": "耶罗波安", "Belshazzar": "伯沙撒",
    "Lazarus": "拉撒路", "Adam": "亚当", "Hosea": "何西阿",
    "Hercules": "赫拉克勒斯", "Perseus": "珀耳修斯", "Andromeda": "安德洛墨达",
    "Prometheus": "普罗米修斯", "Ixion": "伊克西翁", "Cato": "伽图",
    "Vishnoo": "毗湿奴", "Jove": "朱庇特", "Jupiter": "朱庇特",
    "Pliny": "普林尼", "Plutarch": "普卢塔克", "Hackluyt": "哈克鲁特",
    # ── 船
    "Pequod": "裴廓德号", "Pequod’s": "裴廓德号的", "the Pequod": "裴廓德号",
    "Jeroboam": "耶罗波恩号", "Albatross": "信天翁号",
    "Town-Ho": "城头号", "Bachelor": "单身汉号", "Virgin": "处女号",
    "Rose-bud": "玫瑰苞号", "Samuel Enderby": "撒母耳·恩德比号",
    "Rachel": "拉结号", "Delight": "欢欣号", "Jeroboam’s": "耶罗波恩号的",
    "Rachel’s": "拉结号的", "Town-Ho’s": "城头号的",
    # ── 地名
    "Nantucket": "南塔开特", "Nantucketer": "南塔开特人",
    "Nantucketers": "南塔开特人", "New Bedford": "新贝德福",
    "Bedford": "贝德福", "Manhattoes": "曼哈托人", "Manhattan": "曼哈顿",
    "Sag Harbor": "沙格港", "Vineyard": "玛莎葡萄园岛",
    "Cape Horn": "合恩角", "Cape of Good Hope": "好望角",
    "Cape Cod": "科德角", "Atlantic": "大西洋", "Pacific": "太平洋",
    "Indian Ocean": "印度洋", "Arctic": "北极", "Greenland": "格陵兰",
    "Spitzbergen": "斯匹次卑尔根", "Iceland": "冰岛", "Java": "爪哇",
    "Sumatra": "苏门答腊", "Sunda": "巽他", "Manilla": "马尼拉",
    "Japan": "日本", "China": "中国", "Tahiti": "塔希提",
    "Joppa": "约帕", "Tarshish": "他施", "Nineveh": "尼尼微",
    "Lima": "利马", "Andes": "安第斯山", "Thames": "泰晤士河",
    "London": "伦敦", "England": "英国", "America": "美国",
    "Holland": "荷兰", "Zealand": "西兰岛", "Cologne": "科隆",
    "Heidelburgh": "海德堡", "Jungfrau": "少女峰", "Propontis": "普罗蓬提斯海",
    "Mediterranean": "地中海", "Cadiz": "加的斯", "Alabama": "阿拉巴马",
    "Virginia": "弗吉尼亚", "York": "约克", "Tower": "伦敦塔",
    "Spouter-Inn": "大鲸客店", "Try Pots": "炼油锅客店",
    "Euroclydon": "友拉革罗", "Arsacides": "阿萨西兹",
    # ── 鲸与捕鲸术语
    "Moby Dick": "莫比—迪克", "White Whale": "白鲸", "Sperm Whale": "抹香鲸",
    "sperm whale": "抹香鲸", "Spermaceti": "鲸脑油", "spermaceti": "鲸脑油",
    "Right Whale": "露脊鲸", "right whale": "露脊鲸",
    "Greenland Whale": "格陵兰鲸", "Greenland whale": "格陵兰鲸",
    "Hump Back": "座头鲸", "humpback": "座头鲸", "Fin-Back": "长须鲸",
    "Razor Back": "剃刀鲸", "Sulphur Bottom": "硫磺底鲸",
    "Killer": "逆戟鲸", "Narwhale": "独角鲸", "grampus": "虎鲸",
    "Porpoise": "海豚", "porpoise": "海豚", "Squid": "鱿鱼", "squid": "鱿鱼",
    "Albatross": "信天翁", "albatross": "信天翁", "Brit": "小鲸虫",
    "Ambergris": "龙涎香", "ambergris": "龙涎香",
    "Doubloon": "杜伯隆金币", "doubloon": "杜伯隆金币",
    "Try-Works": "炼油间", "try-works": "炼油间",
    "try-pot": "炼油锅", "try-pots": "炼油锅",
    "blubber": "鲸脂", "blubber-room": "鲸脂间", "cutting-in": "割油",
    "Case": "鲸头桶", "Heidelburgh Tun": "海德堡大酒桶",
    "cassock": "法衣", "monkey-rope": "猴索", "monkey-rope’s": "猴索的",
    "crotch": "叉架", "waif": "信号旗", "waif-pole": "信号旗杆",
    "irons": "铁钩", "toggle-irons": "活钩铁", "spade": "铲刀",
    "lance": "长矛", "harpoon": "鱼叉", "dart": "标枪",
    "harpooneer": "标枪手", "harpooneers": "标枪手",
    "specksynder": "斯培克辛德", "Specksynder": "斯培克辛德",
    "lay": "分成", "the lay": "分成", "greasy luck": "满舱的运气",
    "there she blows": "喷水啦",
    "Fast-Fish and Loose-Fish": "有主鲸与无主鲸",
    "fast-fish": "有主鲸", "loose-fish": "无主鲸",
    "gam": "海上相逢", "Gam": "海上相逢", "the gam": "海上相逢",
    "weather-watch": "上风瞭望", "mast-head": "桅顶", "crow’s-nest": "桅顶瞭望台",
    "scuttle-butt": "饮水桶", "cuddy": "厨房", "forecastle": "水手舱",
    "quarter-deck": "后甲板", "poop": "艉楼", "taffrail": "艉栏",
    "bowsprit": "船首斜桁", "jib": "前帆", "foretop": "前桅顶",
    "main-top": "主桅顶", "mizzen": "后桅", "yard-arm": "桁端",
    "keel": "龙骨", "hold": "货舱", "hatches": "舱口",
    "line": "鲸索", "the line": "鲸索", "warp": "拖索",
    "bow oar": "头桨", "stroke oar": "尾桨", "steersman": "舵手",
    "boat-header": "艇头", "boat steerer": "艇尾桨手",
    "Cetology": "鲸类学", "cetology": "鲸类学", "cetacean": "鲸类",
    "Leviathanic": "利维坦式的", "Leviathans": "利维坦",
    "Folio": "对开卷", "Octavo": "八开卷", "Duodecimo": "十二开卷",
    "Ramadan": "斋月", "ramadan": "斋月", "Quaker": "教友派",
    "Quakeress": "教友派女人", "Quakers": "教友派",
    "Pagan": "异教徒", "Christian": "基督徒", "Christians": "基督徒",
    "Presbyterian": "长老会", "Pythagorean": "毕达哥拉斯式的",
    # ── 反复出现的母题用词（统一用词，形成母题）
    "whiteness": "白色", "monomania": "偏执狂", "monomaniac": "偏执狂",
    "fiend": "魔鬼", "cannibal": "食人生番", "savage": "野性",
    "malice": "恶意", "vengeance": "复仇", "fate": "命运",
    "the whale": "大鲸", "whale": "鲸", "whales": "鲸",
}

# ── 补充：清点全书大写词后补入的专名与名物
EXTRA = {
    # 人物与绰号
    "Quohog": "夸霍格", "Yarman": "雅曼", "Tash": "塔希", "Canaller": "运河船工",
    "Canallers": "运河船工", "King-Post": "王柱", "Burtons": "伯顿滑车组",
    "Linn": "林奈", "Linnæus": "林奈", "Sebastian": "塞巴斯蒂安", "Pedro": "佩德罗",
    "Frederick": "腓特烈", "Louis": "路易", "George": "乔治", "Thomas": "托马斯",
    "Henry": "亨利", "John": "约翰", "Samuel": "撒母耳", "Peter": "彼得",
    "Mary": "玛丽", "Aunt Charity": "慈善姑母", "Monsieur": "先生",
    "Capting": "船老大", "Bishop": "主教", "Mrs": "太太",
    # 民族与国族（名词形态；形容词形态请按中文习惯活用）
    "Englishman": "英格兰人", "Englishmen": "英格兰人", "Frenchman": "法国人",
    "Dutchman": "荷兰人", "Spaniard": "西班牙人", "American": "美国人",
    "Americans": "美国人", "Indian": "印第安人", "Indians": "印第安人",
    "Hindoo": "印度人", "Malay": "马来人", "Malays": "马来人",
    "Patagonian": "巴塔哥尼亚人", "Persian": "波斯人", "Turk": "土耳其人",
    "Turks": "土耳其人", "Tartar": "鞑靼人", "Roman": "罗马人",
    "Greek": "希腊人", "Egyptian": "埃及人", "Egyptians": "埃及人",
    "Chilian": "智利人", "Peruvian": "秘鲁人", "Manxman": "马恩岛人",
    "Nantucketer": "南塔开特人", "Christendom": "基督教世界",
    "Islanders": "岛民", "Oriental": "东方人", "Gothic": "哥特式",
    "Latin": "拉丁文", "Venetian": "威尼斯人", "Russian": "俄国人",
    "Turkish": "土耳其的", "Chinese": "中国的", "Japanese": "日本的",
    "Spanish": "西班牙的", "French": "法国的", "German": "德国的",
    "Dutch": "荷兰的", "English": "英国的", "American": "美国的",
    # 地名补
    "Africa": "非洲", "Asia": "亚洲", "Europe": "欧洲", "Spain": "西班牙",
    "France": "法国", "India": "印度", "Peru": "秘鲁", "Chili": "智利",
    "Rome": "罗马", "Greece": "希腊", "Egypt": "埃及", "Turkey": "土耳其",
    "Rockaway Beach": "洛克威海滩", "Saco": "萨科", "Corlears Hook": "柯勒亚斯岬",
    "Coenties Slip": "昆蒂斯船坞", "Whitehall": "白厅", "Broadway": "百老汇",
    "Buffalo": "布法罗", "Erie": "伊利", "Ohio": "俄亥俄",
    "Mississippi": "密西西比", "Missouri": "密苏里", "Amazon": "亚马孙",
    "Nile": "尼罗河", "Euphrates": "幼发拉底河", "Ganges": "恒河",
    "Gibraltar": "直布罗陀", "Archipelago": "群岛海域",
    "Bermudas": "百慕大", "Caribbean": "加勒比", "Azores": "亚速尔",
    "Ceylon": "锡兰", "Borneo": "婆罗洲", "Celebes": "西里伯斯",
    "Moluccas": "摩鹿加", "Philippines": "菲律宾", "Sandwich Islands": "三明治群岛",
    "Otaheite": "塔希提", "Tahiti": "塔希提", "Patagonia": "巴塔哥尼亚",
    "Lancashire": "兰开夏", "Yorkshire": "约克郡", "Nantucket Sound": "南塔开特湾",
    "Martha’s Vineyard": "玛莎葡萄园岛", "Delaware": "特拉华",
    "Maryland": "马里兰", "Carolina": "卡罗来纳", "Vermont": "佛蒙特",
    "New Hampshire": "新罕布什尔", "Connecticut": "康涅狄格",
    "Hudson": "哈得孙河", "Manhattan Island": "曼哈顿岛",
    # 名物、器具、航海
    "windlass": "绞盘", "capstan": "绞盘", "lubber": "旱鸭子",
    "deck-watch": "甲板班", "anchor-watch": "锚班", "look-out": "瞭望手",
    "cutting-stage": "割油台", "blubber-hook": "捞脂钩", "blubber-spade": "脂铲",
    "mincing-knife": "碎脂刀", "boarding-knife": "登船刀", "drawing-knife": "剥脂刀",
    "cutting-tackle": "割油索具", "windlass-pawl": "绞盘掣子",
    "scuttle": "舷窗", "companion-way": "升降口", "cabin": "船长室",
    "forecastle": "水手舱", "steerage": "统舱", "main-hatch": "主舱口",
    "bowsprit": "船首斜桁", "cross-trees": "桅顶横桁", "top-gallant": "顶桅",
    "royal-mast": "天桅", "sky-sail": "云帆", "studding-sail": "翼帆",
    "trysail": "斜桁纵帆", "mainsail": "主帆", "topsail": "中桅帆",
    "binnacle": "罗经柜", "quadrant": "象限仪", "log-line": "测程绳",
    "compass": "罗盘", "sextant": "六分仪", "chronometer": "经线仪",
    "waist": "腰舱", "bulwarks": "舷墙", "gunwale": "舷缘", "thwart": "坐板",
    "tholes": "桨架钉", "stretchers": "踏脚板", "gunwales": "舷缘",
    "drugg": "海锚", "toggle": "活钩", "toggle-iron": "活钩铁",
    "tackle": "滑车组", "tiller": "舵柄", "helm": "舵轮",
    # 鲸类与名物补
    "Sulphur-Bottom": "硫磺底鲸", "Junk": "鲸头瘤", "junk": "鲸头瘤",
    "Case": "鲸头桶", "case": "鲸头桶", "Pocket": "鲸头囊",
    "scarf": "鲸脂接缝", "blanket-piece": "大脂片", "sheet": "脂版",
    "white-horse": "白浪马", "horse-tails": "马尾浪",
    "Cuttings": "割油残渣", "cuttings": "割油残渣",
    "Ambergris": "龙涎香", "sperm": "鲸脑", "oil": "鲸油",
    "whalebone": "鲸须", "baleen": "鲸须", "blubber": "鲸脂",
    "Spermaceti": "鲸脑油", "spermaceti": "鲸脑油",
    "Battering Ram": "攻城槌", "Sphinx": "斯芬克司",
    "Esau": "以扫", "Ishmael": "以实玛利", "Hagar": "夏甲",
    "Aunt": "姑母", "Bridegroom": "新郎", "Sabbath": "安息日",
    "Christmas": "圣诞节", "Ramadan": "斋月",
}
G.update(EXTRA)

# 常用译法：短词只在整词匹配时替换，避免误伤（如 Fast-Fish）
CORE = ["Ahab", "Ishmael", "Queequeg", "Starbuck", "Stubb", "Flask",
        "Pequod", "Moby Dick", "Nantucket", "Tashtego", "Daggoo", "Pip",
        "Fedallah", "Mapple", "Peleg", "Bildad"]


def relevant(source: str, limit: int = 90) -> list[tuple[str, str]]:
    """Entries occurring in this source, longest English form first."""
    hits = []
    for en, zh in G.items():
        pat = r"(?<![A-Za-z])" + re.escape(en) + r"(?![A-Za-z])"
        if re.search(pat, source):
            hits.append((en, zh))
    hits.sort(key=lambda x: (-len(x[0]), x[0]))
    core = [(en, G[en]) for en in CORE if (en, G[en]) not in hits]
    return (hits + core)[:limit]


def render(entries: list[tuple[str, str]]) -> str:
    if not entries:
        return "【术语表】本章无必须统一的专名。"
    lines = [f"{en} → {zh}" for en, zh in entries]
    return "【术语表·必须照此译，全书一致】\n" + "\n".join(lines)
