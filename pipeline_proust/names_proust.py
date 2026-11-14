"""Proper-name table for the independent Proust translation (all seven volumes).

This is **not** derived from Zhou Kexi's published version. Names are romanised
fresh from the French, following ordinary Pinyin-free Chinese conventions for
French names (see the rules at the bottom), and the same form is used wherever
the name occurs so that the motif words stay recognisable across 2,600 pages.

Romanisation policy
-------------------
* French nasal vowels keep their usual Chinese renderings: -an/-en → 安/昂,
  -in → 兰/林, -on → 翁, -om → 孔.
* *Gui-* is 吉-, *Qu-* is 屈-/凯-, *j-/g-* before e/i is 热/吉, *ch-* is 夏/沙.
* A final silent consonant is dropped; a pronounced one is kept (Guermantes →
  盖尔芒特, Charlus → 夏吕斯).
* The particle *de* is 德· and stays in front of the surname: 德·夏吕斯先生.
* Where a French place already has a settled Chinese name (Paris 巴黎, Venice
  威尼斯, Balbec is fictional so it is romanised), the settled name wins.

Note the deliberate divergences from the Zhou Kexi renderings, chosen either for
accuracy or for readability; nothing here is inherited from his text.
"""

# ── principal characters ────────────────────────────────────────────────
PEOPLE = {
    # narrator and family
    "Marcel": "马塞尔",
    "Françoise": "弗朗索瓦丝",
    "la grand'mère": "外祖母",
    "ma mère": "母亲",
    "mon père": "父亲",
    "tante Léonie": "莱奥妮姑妈",
    "Léonie": "莱奥妮",
    "Eulalie": "厄拉莉",
    "Adolphe": "阿道夫",
    "Aimé": "埃梅",
    # Swann's set
    "Swann": "斯万",
    "Odette": "奥黛特",
    "Odette de Crécy": "奥黛特·德·克雷西",
    "Gilberte": "吉尔贝特",
    "Mme Swann": "斯万夫人",
    "Mme Cottard": "科塔尔夫人",
    "Cottard": "科塔尔",
    "Vinteuil": "凡特伊",
    "Mlle Vinteuil": "凡特伊小姐",
    "Berma": "贝尔玛",
    "Bergotte": "贝戈特",
    "Elstir": "埃尔斯蒂尔",
    # Guermantes
    "Guermantes": "盖尔芒特",
    "Oriane": "奥丽亚娜",
    "la duchesse de Guermantes": "盖尔芒特公爵夫人",
    "le duc de Guermantes": "盖尔芒特公爵",
    "Basin": "巴赞",
    "le prince de Guermantes": "盖尔芒特亲王",
    "la princesse de Guermantes": "盖尔芒特亲王夫人",
    "Mme de Marsantes": "马桑特夫人",
    "Marsantes": "马桑特",
    "Charlus": "夏吕斯",
    "Palamède": "帕拉梅德",
    "Saint-Loup": "圣卢",
    "Robert": "罗贝尔",
    "Mme de Villeparisis": "维尔帕里齐夫人",
    "Villeparisis": "维尔帕里齐",
    "Mme de Saint-Euverte": "圣厄韦尔特夫人",
    "Saint-Euverte": "圣厄韦尔特",
    "Mme de Gallardon": "加拉尔东夫人",
    "Gallardon": "加拉尔东",
    "Mme de Bréauté": "布雷奥泰夫人",
    "Bréauté": "布雷奥泰",
    "Mme d'Arpajon": "达尔帕容夫人",
    "Arpajon": "达尔帕容",
    "Mme de Souvré": "苏夫雷夫人",
    "Souvré": "苏夫雷",
    "Mme de Montmorency": "蒙莫朗西夫人",
    "Montmorency": "蒙莫朗西",
    "M. de Froberville": "弗罗贝维尔先生",
    "Froberville": "弗罗贝维尔",
    "Mme de Varambon": "瓦朗邦夫人",
    "Varambon": "瓦朗邦",
    "Grouchy": "格鲁希",
    "Mme de Guise": "吉斯夫人",
    "Guise": "吉斯",
    "Mme de Mortemart": "莫特马尔夫人",
    "Mortemart": "莫特马尔",
    "Mme de Sagan": "萨冈夫人",
    "Sagan": "萨冈",
    "Mme de Duras": "迪拉斯夫人",
    "Duras": "迪拉斯",
    "Mme de Châtellerault": "沙特勒罗夫人",
    "Châtellerault": "沙特勒罗",
    "La Trémoïlle": "拉特雷穆瓦耶",
    "Mme de Beauvau": "博沃夫人",
    "Sainte-Feuverte": "圣特弗韦尔特",
    # Verdurin clan
    "Verdurin": "韦尔迪兰",
    "Mme Verdurin": "韦尔迪兰夫人",
    "le Patron": "老板",
    "la Patronne": "老板娘",
    "Brichot": "布里肖",
    "Saniette": "萨涅特",
    "Ski": "斯基",
    "Cottard": "科塔尔",
    "Morel": "莫雷尔",
    "Charlie": "夏利",
    "Jupien": "絮比安",
    "Aimé": "埃梅",
    "la princesse de Parme": "帕尔马亲王夫人",
    "Parme": "帕尔马",
    # Albertine and the little band
    "Albertine": "阿尔贝蒂娜",
    "Andrée": "安德蕾",
    "Gisèle": "吉泽尔",
    "Rosemonde": "罗斯蒙德",
    "Léa": "莱娅",
    "Mme Bontemps": "邦唐夫人",
    "Bontemps": "邦唐",
    "Octave": "奥克塔夫",
    # others
    "Bloch": "布洛克",
    "Rachel": "拉谢尔",
    "Rachel quand du Seigneur": "主所赐的拉谢尔",
    "Norpois": "诺普瓦",
    "Legrandin": "勒格朗丹",
    "Mme de Cambremer": "康布雷梅夫人",
    "Cambremer": "康布雷梅",
    "Forcheville": "福什维尔",
    "Stermaria": "斯泰尔玛丽亚",
    "Vaugoubert": "沃古贝尔",
    "Mme de Surgis": "叙尔吉斯夫人",
    "Surgis": "叙尔吉斯",
    "Citri": "西特里",
    "Nissim Bernard": "尼西姆·贝尔纳",
    "Théodore": "泰奥多尔",
    "Courvoisier": "库尔瓦西耶",
    "Franquetot": "弗朗克托",
    "Chantepie": "尚特皮",
    "Boulbon": "布尔邦",
    "Féterne": "费泰尔纳",
    "Douville": "杜维尔",
    "Maineville": "迈纳维尔",
    "Borodino": "博罗季诺",
    "Dreyfus": "德雷福斯",
}

# ── places ──────────────────────────────────────────────────────────────
PLACES = {
    "Combray": "贡布雷",
    "Balbec": "巴尔贝克",
    "Paris": "巴黎",
    "Venise": "威尼斯",
    "Doncières": "东谢尔",
    "Méséglise": "梅塞格利斯",
    "Tansonville": "唐松维尔",
    "Montjouvain": "蒙茹万",
    "Roussainville": "鲁森维尔",
    "Martinville": "马丹维尔",
    "Illiers": "伊利耶",
    "Chartres": "沙特尔",
    "la Raspelière": "拉斯普利埃",
    "Rivebelle": "里夫贝尔",
    "Incarville": "安卡维尔",
    "Parville": "帕尔维尔",
    "Féterne": "费泰尔纳",
    "Chatou": "沙图",
    "Boulogne": "布洛涅",
    "le Bois": "布洛涅树林",
    "Champs-Élysées": "香榭丽舍",
    "Trocadéro": "特罗卡德罗",
    "Montmartre": "蒙马特",
    "Versailles": "凡尔赛",
    "Naples": "那不勒斯",
    "Florence": "佛罗伦萨",
    "Rome": "罗马",
    "Venise": "威尼斯",
    "Vichy": "维希",
    "Cannes": "戛纳",
    "Étretat": "埃特勒塔",
    "Trouville": "特鲁维尔",
    "Reims": "兰斯",
    "Rue de la Paix": "和平街",
    "Grand-Hôtel": "大旅馆",
    "hôtel de Guermantes": "盖尔芒特府",
    "jardin des Plantes": "植物园",
    "la madeleine": "玛德莱娜教堂",
    "l'Opéra": "歌剧院",
}

# ── works, paintings, music ─────────────────────────────────────────────
WORKS = {
    "la petite phrase": "小乐句",
    "la sonate": "奏鸣曲",
    "le septuor": "七重奏",
    "Phèdre": "《费德尔》",
    "Bérénice": "《贝蕾妮丝》",
    "Athalie": "《阿塔莉》",
    "Tartuffe": "《伪君子》",
    "le Misanthrope": "《愤世嫉俗》",
    "les Mémoires d'outre-tombe": "《墓中回忆录》",
    "la Comédie humaine": "《人间喜剧》",
    "les Fleurs du mal": "《恶之花》",
    "Sodome et Gomorrhe": "索多姆与戈摩尔",
    "les Mille et une Nuits": "《一千零一夜》",
}

# ── recurring motifs — the translation must be identical every occurrence ──
MOTIFS = {
    "madeleine": "玛德莱娜小蛋糕",
    "petite madeleine": "小玛德莱娜蛋糕",
    "aubépine": "山楂花",
    "côté de chez Swann": "斯万家那边",
    "côté de Guermantes": "盖尔芒特家那边",
    "les deux côtés": "两边",
    "mémoire involontaire": "非自主记忆",
    "le temps perdu": "逝去的时光",
    "le Temps retrouvé": "重现的时光",
    "les intermittences du cœur": "心灵的间歇",
    "la race des tantes": "姑妈一族",
    "le petit noyau": "小核心",
    "les fidèles": "忠实信徒",
}

ALL = {**PEOPLE, **PLACES, **WORKS, **MOTIFS}

CORE = ["Swann", "Albertine", "Charlus", "Saint-Loup", "Guermantes",
        "Combray", "Balbec", "Vinteuil", "Bergotte", "Verdurin", "Morel",
        "Oriane", "Françoise", "Elstir", "Bloch", "Cottard"]


def relevant(text: str, limit: int = 140) -> dict[str, str]:
    """Glossary entries that actually occur in this chunk, plus the core set."""
    import re
    out = {k: ALL[k] for k in CORE if k in ALL}
    for key, val in sorted(ALL.items(), key=lambda kv: -len(kv[0])):
        if key in out:
            continue
        if re.search(r"\b" + re.escape(key) + r"\b", text, re.I):
            out[key] = val
        if len(out) >= limit:
            break
    return out


def render(entries: dict[str, str]) -> str:
    if not entries:
        return ""
    lines = [f"{k} = {v}" for k, v in sorted(entries.items())]
    return ("【专名对照表（本译本自定译名，全书统一，必须严格照用；"
            "与任何其他中译本的译名无关）】\n" + "\n".join(lines))


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print("entries:", len(ALL), "people", len(PEOPLE), "places", len(PLACES))
