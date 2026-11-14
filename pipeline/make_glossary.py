"""Build/verify the name & term glossary against the existing Chinese edition.

For every entry we hold several candidate renderings and pick the one that the
published translation actually uses most often (so our new translation keeps the
established Tolkien nomenclature Chinese readers know).
"""
from __future__ import annotations

import glob
import json
import os
import re

REF = "E:/Translate/work/ref_zh"
OUT = "E:/Translate/work/glossary.json"

# english -> [candidates in order of preference]
CANDIDATES = {
    # --- hobbits
    "Frodo": ["弗罗多", "佛罗多"],
    "Bilbo": ["比尔博"],
    "Samwise": ["山姆怀斯"],
    "Sam": ["山姆"],
    "Meriadoc": ["梅里雅达克"],
    "Merry": ["梅里"],
    "Peregrin": ["佩里格林"],
    "Pippin": ["皮平"],
    "Baggins": ["巴金斯"],
    "Gamgee": ["甘姆吉", "甘吉"],
    "Brandybuck": ["烈酒鹿", "白兰地鹿"],
    "Took": ["图克"],
    "Sackville-Baggins": ["萨克维尔-巴金斯", "萨克维尔–巴金斯"],
    "Lobelia": ["罗贝拉", "洛比莉亚"],
    "Otho": ["奥索"],
    "Old Took": ["老图克"],
    "Gaffer": ["老头儿", "老爹", "甘姆吉老头"],
    "Hamfast": ["汉姆法斯特"],
    "Drogo": ["德罗哥", "卓果"],
    "Primula": ["普丽缪拉", "普利米拉"],
    "Folco": ["佛科"],
    "Fredegar": ["弗雷德加"],
    "Fatty": ["小胖", "胖墩"],
    "Farmer Maggot": ["马戈特农夫"],
    "Ted Sandyman": ["泰德·山迪曼"],
    "Lotho": ["洛索"],
    "Robin": ["罗宾"],
    "Hob": ["霍伯"],
    "Daddy Twofoot": ["双足老爹"],
    "Old Noakes": ["老诺克斯"],
    # --- the Company
    "Gandalf": ["甘道夫"],
    "Aragorn": ["阿拉贡"],
    "Boromir": ["波罗莫", "博罗米尔"],
    "Legolas": ["勒苟拉斯", "莱戈拉斯"],
    "Gimli": ["金雳", "吉姆利"],
    "Strider": ["大步佬", "神行客"],
    "Elrond": ["埃尔隆德", "爱隆"],
    "Galadriel": ["凯兰崔尔", "凯兰崔尔女王"],
    "Celeborn": ["凯勒鹏", "凯勒鹏王"],
    "Haldir": ["哈尔迪尔"],
    "Arwen": ["阿尔温", "亚玟"],
    "Glorfindel": ["葛罗芬戴尔"],
    "Erestor": ["埃瑞斯托"],
    "Galdor": ["加尔多"],
    "Bill the Pony": ["小马比尔", "比尔"],
    # --- villains
    "Sauron": ["索伦"],
    "Saruman": ["萨鲁曼"],
    "Gollum": ["咕鲁", "古鲁姆"],
    "Sméagol": ["史麦戈"],
    "Wormtongue": ["巧言"],
    "Gríma": ["格里马"],
    "Witch-king": ["巫王"],
    "Nazgûl": ["戒灵"],
    "Ringwraith": ["黑骑士", "戒灵"],
    "Black Riders": ["黑骑士"],
    "Sharkey": ["沙基", "萨基"],
    "Mouth of Sauron": ["索伦之口"],
    "Shelob": ["尸罗"],
    "Uglúk": ["乌格鲁克", "乌骨陆"],
    "Grishnákh": ["格里什纳赫"],
    "Shagrat": ["夏格拉"],
    "Gorbag": ["哥巴葛"],
    "Lugbúrz": ["卢格伯兹"],
    "Lurtz": ["路兹"],
    # --- Rohan & Gondor
    "Théoden": ["希优顿", "塞奥顿"],
    "Éowyn": ["伊欧玟", "伊奥温"],
    "Éomer": ["伊欧墨", "伊奥梅尔"],
    "Théodred": ["希优德", "塞奥德雷德"],
    "Háma": ["哈玛"],
    "Gamling": ["加姆林"],
    "Grímbold": ["格里姆博德"],
    "Erkenbrand": ["鄂肯布兰德"],
    "Denethor": ["迪耐瑟", "德内梭尔"],
    "Faramir": ["法拉墨", "法拉米尔"],
    "Boromir's father": ["波罗莫的父亲"],
    "Imrahil": ["印拉希尔"],
    "Beregond": ["贝尔贡"],
    "Bergil": ["贝吉尔"],
    "Ioreth": ["伊欧瑞斯"],
    "Ghân-buri-Ghân": ["甘布理甘", "甘-布里-甘"],
    "Woses": ["野人"],
    "Ghân": ["甘"],
    "Damrod": ["丹姆罗德"],
    "Mablung": ["马伯龙"],
    "Anborn": ["安本"],
    "Henneth Annûn": ["汉奈斯安努恩"],
    # --- elves / dwarves / elder days
    "Elendil": ["伊兰迪尔"],
    "Isildur": ["埃西铎", "伊西尔都"],
    "Anárion": ["阿纳瑞安", "阿那瑞安"],
    "Gil-galad": ["吉尔加拉德"],
    "Celebrimbor": ["凯勒布理鹏", "凯勒布林博"],
    "Fëanor": ["费诺", "费艾诺"],
    "Lúthien": ["露西安", "卢西恩"],
    "Beren": ["贝伦"],
    "Tinúviel": ["缇努维尔"],
    "Eärendil": ["埃兰迪尔"],
    "Elwing": ["爱尔温"],
    "Thingol": ["庭葛", "辛葛"],
    "Melian": ["美丽安"],
    "Morgoth": ["魔苟斯", "米尔寇"],
    "Túrin": ["图林"],
    "Húrin": ["胡林"],
    "Númenor": ["努曼诺尔", "努门诺尔"],
    "Dúnedain": ["登丹人"],
    "Dúnadan": ["登丹人"],
    "Durin": ["都灵", "杜林"],
    "Balin": ["巴林"],
    "Thorin": ["索林"],
    "Dáin": ["戴因"],
    "Glóin": ["葛罗音"],
    "Bard": ["巴德"],
    "Brand": ["布兰德"],
    "Thranduil": ["瑟兰督伊"],
    "Treebeard": ["树胡"],
    "Quickbeam": ["快木", "快枝"],
    "Ent": ["树人"],
    "Huorn": ["胡恩"],
    "Tom Bombadil": ["汤姆·邦巴迪尔", "汤姆·庞巴迪"],
    "Goldberry": ["金莓"],
    "Barrow-wight": ["古冢尸妖"],
    "Old Man Willow": ["老柳头"],
    # --- places
    "the Shire": ["夏尔"],
    "Hobbiton": ["霍比屯"],
    "Bag End": ["袋底洞"],
    "Bywater": ["傍水镇", "水边镇"],
    "Buckland": ["烈酒鹿地", "雄鹿地"],
    "Brandywine": ["烈酒河", "白兰地河"],
    "Bree": ["布理"],
    "Rivendell": ["瑞文戴尔"],
    "Lothlórien": ["罗斯洛立安"],
    "Lórien": ["罗斯洛立安", "罗瑞安"],
    "Moria": ["摩瑞亚"],
    "Khazad-dûm": ["卡扎督姆"],
    "Isengard": ["艾辛格"],
    "Rohan": ["洛汗"],
    "Gondor": ["刚铎"],
    "Minas Tirith": ["米那斯提力斯"],
    "Minas Morgul": ["米那斯魔窟"],
    "Osgiliath": ["奥斯吉力亚斯"],
    "Edoras": ["伊多拉斯"],
    "Helm's Deep": ["圣盔谷"],
    "Fangorn": ["法贡森林"],
    "Rauros": ["拉洛斯"],
    "Emyn Muil": ["艾明莫尔"],
    "Dead Marshes": ["死亡沼泽"],
    "Cirith Ungol": ["西力斯昂哥"],
    "Mordor": ["魔多"],
    "Mount Doom": ["末日火山"],
    "Barad-dûr": ["巴拉多"],
    "Orodruin": ["末日山"],
    "Ithilien": ["伊西立安"],
    "Pelennor": ["帕兰诺"],
    "Weathertop": ["风云顶"],
    "Amon Sûl": ["阿蒙苏尔"],
    "Barrow-downs": ["古冢岗"],
    "Old Forest": ["老林子"],
    "Crickhollow": ["溪谷地"],
    "Michel Delving": ["米丘窟"],
    "Grey Havens": ["灰港"],
    "Eregion": ["伊瑞詹"],
    "Caradhras": ["红角峰"],
    "Hollin": ["冬青郡"],
    "Dimrill Dale": ["暗溪谷"],
    "Celebrant": ["银流河"],
    "Anduin": ["安都因"],
    "Argonath": ["亚苟那斯"],
    "Nen Hithoel": ["宁希索尔"],
    "Tol Brandir": ["托尔布兰迪尔"],
    "Rohan's capital": ["洛汗首都"],
    "Dunharrow": ["登哈洛"],
    "Druadan": ["德鲁丹"],
    "the Pelennor Fields": ["帕兰诺平原"],
    "Rammas Echor": ["拉马斯埃霍尔"],
    "Cirith Gorgor": ["西力斯葛哥"],
    "Udûn": ["乌顿"],
    "Narchost": ["纳科斯"],
    "Carchost": ["卡尔科斯"],
    "Morannon": ["摩拉南"],
    "Cormallen": ["科玛伦"],
    "Isen": ["艾辛"],
    "Mering Stream": ["分水河"],
    "Anórien": ["阿诺瑞安"],
    "Lossarnach": ["罗萨那奇"],
    "Lebennin": ["雷本宁"],
    "Lamedon": ["拉梅顿"],
    "Ethring": ["埃斯林"],
    "Erech": ["伊瑞赫"],
    "Paths of the Dead": ["亡者之路"],
    "Dimholt": ["暗林"],
    # --- things
    "One Ring": ["至尊戒"],
    "the Ring": ["魔戒"],
    "Red Book": ["西界红皮书"],
    "palantír": ["真知晶球"],
    "elanor": ["星辰花"],
    "niphredil": ["宁芙瑞迪尔"],
    "mallorn": ["梅隆树"],
    "mithril": ["秘银"],
    "lembas": ["兰巴斯"],
    "cram": ["克拉姆"],
    "miruvor": ["米鲁伏尔"],
    "Silmarils": ["精灵宝钻"],
    "Andúril": ["安都瑞尔"],
    "Narsil": ["纳西尔"],
    "Sting": ["刺针"],
    "Glamdring": ["敌击剑"],
    "Orcrist": ["兽咬剑"],
    "Phial of Galadriel": ["凯兰崔尔的水晶瓶", "凯兰崔尔之瓶"],
    "mûmakil": ["猛玛象", "姆玛克"],
    "oliphaunt": ["大象", "奥力芬特"],
    "Nazgûl-blade": ["戒灵之刃"],
    "Wraith-world": ["幽界"],
    "mathom": ["珍玩"],
    "Hobbiton's mill": ["霍比屯磨坊"],
}


def load_ref_text() -> str:
    parts = []
    for f in glob.glob(os.path.join(REF, "*.json")):
        if f.endswith("index.json"):
            continue
        d = json.load(open(f, encoding="utf-8"))
        parts.extend(b["text"] for b in d["blocks"])
    return "\n".join(parts)


def main():
    ref = load_ref_text()
    resolved, unresolved = {}, []
    for en, cands in CANDIDATES.items():
        counts = [(ref.count(c), c) for c in cands]
        counts.sort(reverse=True)
        if counts[0][0] > 0:
            resolved[en] = {"zh": counts[0][1], "count": counts[0][0], "alt": [c for n, c in counts[1:]]}
        else:
            unresolved.append((en, cands))
    print(f"resolved {len(resolved)} / {len(CANDIDATES)}")
    print("\nUNRESOLVED (not found in reference edition):")
    for en, cands in unresolved:
        print("  ", en, cands)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(resolved, f, ensure_ascii=False, indent=1)
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
