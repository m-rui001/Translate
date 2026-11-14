"""Catalogue of the public-domain titles being translated.

Selection rule: the author must have died more than fifty years ago AND the work
must have no established Chinese translation, or only an old/abridged one. Books
whose Chinese versions are plentiful and good (Hugo, Dostoevsky, Tolstoy,
Stendhal, Flaubert, Maupassant) are deliberately excluded -- another translation
of those adds nothing, and the good ones are not improved on.

Two further rules turned out to matter, both learned by checking the downloads:

  * **Prefer the original language.** Where Gutenberg only offers an English
    translation of e.g. Goncharov or Jókai, translating from that translation
    would launder a translator's choices into our Chinese. Those titles are kept
    only when a source-language file exists; otherwise they are dropped.
  * **Fetch every volume.** Several of these are multi-volume on Gutenberg
    (O Guarany 2, Pelle 4, Diana 4). Taking volume one alone produces a book that
    stops mid-story, which is exactly the fault this project exists to avoid.

`died` is recorded so the fifty-year rule is auditable rather than asserted.
`gids` is the ordered list of Gutenberg ids making up the whole work.
"""

BOOKS = {
    # ── German ───────────────────────────────────────────────────────────────
    "nachsommer": {
        "title_zh": "晚夏", "title_src": "Der Nachsommer",
        "author_zh": "阿达尔贝特·施蒂弗特", "author_src": "Adalbert Stifter",
        "lang": "de", "gids": [8126], "died": 1868,
        "note": "德语长篇，歌德之后最沉静的成长小说；中译仅有节译",
    },
    "effi": {
        "title_zh": "艾菲·布里斯特", "title_src": "Effi Briest",
        "author_zh": "特奥多尔·冯塔纳", "author_src": "Theodor Fontane",
        "lang": "de", "gids": [5323], "died": 1898,
        "note": "德语现实主义的巅峰，通奸题材却写得极冷",
    },
    "immensee": {
        "title_zh": "茵梦湖", "title_src": "Immensee",
        "author_zh": "特奥多尔·施托姆", "author_src": "Theodor Storm",
        "lang": "de", "gids": [6651], "died": 1888,
        "note": "德语中篇名作，郭沫若旧译已过时",
    },
    "zauberkaftan": {
        "title_zh": "魔法袍", "title_src": "Der Zauberkaftan",
        "author_zh": "卡尔曼·米克沙特", "author_src": "Kálmán Mikszáth",
        "lang": "de", "gids": [23740], "died": 1910,
        "note": "匈牙利作家作品的德语本，讽刺小说，中文几无译介",
    },
    "haidedorf": {
        "title_zh": "草原村", "title_src": "Das Haidedorf",
        "author_zh": "阿达尔贝特·施蒂弗特", "author_src": "Adalbert Stifter",
        "lang": "de", "gids": [7068], "died": 1868,
        "note": "施蒂弗特中篇，与《晚夏》同一世界，中译无",
    },
    "buntesteine": {
        "title_zh": "彩石集", "title_src": "Bunte Steine",
        "author_zh": "阿达尔贝特·施蒂弗特", "author_src": "Adalbert Stifter",
        "lang": "de", "gids": [29553], "died": 1868,
        "note": "施蒂弗特最著名的中篇集，含《石灰石》《水晶》诸篇",
    },
    "wilderMann": {
        "title_zh": "野人旅馆", "title_src": "Zum wilden Mann",
        "author_zh": "威廉·拉贝", "author_src": "Wilhelm Raabe",
        "lang": "de", "gids": [22123], "died": 1910,
        "note": "德语现实主义大家，中文几乎无人译介",
    },

    # ── Romance ──────────────────────────────────────────────────────────────
    "fortunata": {
        "title_zh": "福尔图娜塔与哈辛塔", "title_src": "Fortunata y Jacinta",
        "author_zh": "贝尼托·佩雷斯·加尔多斯", "author_src": "Benito Pérez Galdós",
        "lang": "es", "gids": [17013], "died": 1920,
        "note": "西班牙十九世纪最长的杰作，中译不全",
    },
    "regenta": {
        "title_zh": "庭长夫人", "title_src": "La Regenta",
        "author_zh": "莱奥波尔多·阿拉斯", "author_src": "Leopoldo Alas «Clarín»",
        "lang": "es", "gids": [17073], "died": 1901,
        "note": "西班牙版《包法利夫人》，篇幅两倍于原著题材",
    },
    "sotileza": {
        "title_zh": "索蒂莱萨", "title_src": "Sotileza",
        "author_zh": "何塞·马里亚·德·佩雷达", "author_src": "José María de Pereda",
        "lang": "es", "gids": [49388], "died": 1906,
        "note": "桑坦德渔民生活，地域小说，中文无译本",
    },
    "ulloa": {
        "title_zh": "乌略亚庄园", "title_src": "Los pazos de Ulloa",
        "author_zh": "埃米莉亚·帕尔多·巴桑", "author_src": "Emilia Pardo Bazán",
        "lang": "es", "gids": [18005], "died": 1921,
        "note": "西班牙自然主义代表作，中译仅有零散短篇",
    },
    "germinie": {
        "title_zh": "热尔米妮·拉瑟尔特", "title_src": "Germinie Lacerteux",
        "author_zh": "埃德蒙·德·龚古尔", "author_src": "Edmond de Goncourt",
        "lang": "fr", "gids": [17285], "died": 1896,
        "note": "法国自然主义开山之作，女仆悲剧，中译罕见",
    },
    "guarany": {
        "title_zh": "瓜拉尼人", "title_src": "O Guarany",
        "author_zh": "若泽·德·阿伦卡尔", "author_src": "José de Alencar",
        "lang": "pt", "gids": [67724, 67725], "died": 1877,
        "note": "巴西民族文学的奠基作，中文几乎空白；两卷全译",
    },
    "maias": {
        "title_zh": "马亚一家", "title_src": "Os Maias",
        "author_zh": "埃萨·德·凯罗斯", "author_src": "Eça de Queirós",
        "lang": "pt", "gids": [40409], "died": 1900,
        "note": "葡萄牙现实主义顶峰，中文译本久佚",
    },

    # ── Nordic / Dutch ───────────────────────────────────────────────────────
    "lykkepers": {
        "title_zh": "幸运的佩尔", "title_src": "Lykke-Per",
        "author_zh": "亨里克·彭托皮丹", "author_src": "Henrik Pontoppidan",
        "lang": "da", "gids": [51384], "died": 1943,
        "note": "丹麦诺奖得主代表作，中文无全译；仅有第一部原文，缺卷不补",
    },
    "maxhavelaar": {
        "title_zh": "马克斯·哈弗拉尔", "title_src": "Max Havelaar",
        "author_zh": "穆尔塔图里", "author_src": "Multatuli",
        "lang": "nl", "gids": [11024], "died": 1887,
        "note": "荷属东印度殖民批判经典，中文译本罕见",
    },

    # ── Italian ──────────────────────────────────────────────────────────────
    "dopoidivorzio": {
        "title_zh": "离婚之后", "title_src": "Dopo il divorzio",
        "author_zh": "格拉齐亚·黛莱达", "author_src": "Grazia Deledda",
        "lang": "it", "gids": [43226], "died": 1936,
        "note": "意大利诺奖得主早期长篇，中文仅有短篇集",
    },

    # ── Polish / Hungarian ───────────────────────────────────────────────────
    "timar": {
        "title_zh": "金人", "title_src": "Az arany ember",
        "author_zh": "莫尔·约卡伊", "author_src": "Mór Jókai",
        "lang": "hu", "gids": [31409], "died": 1904,
        "note": "匈牙利浪漫主义长篇，中文几乎空白",
    },

    # ── English ──────────────────────────────────────────────────────────────
    "ayala": {
        "title_zh": "阿亚拉的天使", "title_src": "Ayala's Angel",
        "author_zh": "安东尼·特罗洛普", "author_src": "Anthony Trollope",
        "lang": "en", "gids": [33500], "died": 1882,
        "note": "特罗洛普后期长篇，中译仅数种且不全",
    },
    "diana": {
        "title_zh": "戴安娜的交叉", "title_src": "Diana of the Crossways",
        "author_zh": "乔治·梅瑞狄斯", "author_src": "George Meredith",
        "lang": "en", "gids": [4465, 4466, 4467, 4468], "died": 1909,
        "note": "英国心理小说先驱，中文无全译；四卷全译",
    },
}


def by_lang() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for k, v in BOOKS.items():
        out.setdefault(v["lang"], []).append(k)
    return out


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    for lang, ids in sorted(by_lang().items()):
        print(f"  {lang}: {len(ids)} -> {', '.join(sorted(ids))}")
    bad = [k for k, v in BOOKS.items() if 2026 - v["died"] <= 50]
    vols = sum(len(v["gids"]) for v in BOOKS.values())
    print(f"{len(BOOKS)} titles, {vols} volumes")
    print("copyright-unsafe:", bad or "none")
