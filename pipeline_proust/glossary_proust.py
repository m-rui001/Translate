"""Proust glossary: Zhou Kexi's confirmed renderings + standard forms for names
that only appear in the volumes he did not finish."""
from __future__ import annotations

import json
import os
import re

_Z = os.path.join(os.path.dirname(__file__), "..", "work_proust", "glossary_zhou.json")

# Confirmed in Zhou's published text (see mine_zhou_glossary.py)
_ZHOU = {
    "Swann": "斯万", "Odette": "奥黛特", "Gilberte": "吉尔贝特",
    "Charlus": "夏尔吕", "Saint-Loup": "圣卢", "Albertine": "阿尔贝蒂娜",
    "Morel": "莫雷尔", "Bloch": "布洛克", "Bergotte": "贝戈特",
    "Verdurin": "韦尔迪兰", "Jupien": "絮比安", "Basin": "巴赞",
    "Elstir": "埃尔斯蒂尔", "Combray": "贡布雷", "Balbec": "巴尔贝克",
    "Guermantes": "盖尔芒特", "Verdurins": "韦尔迪兰夫妇",
    "madeleine": "玛德莱娜", "petite phrase": "小乐句",
    "sonate": "奏鸣曲", "sonata": "奏鸣曲",
    "hawthorn": "山楂花", "lilas": "丁香", "goéland": "海鸥",
    "Bois de Boulogne": "布洛涅树林", "Vinteuil": "凡德伊",
}

# Not in his finished volumes: standard established renderings
_REST = {
    "Norpois": "诺普瓦", "Mme de Villeparisis": "维尔帕里西斯夫人",
    "Villeparisis": "维尔帕里西斯", "Cottard": "科塔尔",
    "Venteville": "旺德夫尔", "Oriane": "奥里亚娜",
    "Mme Bontemps": "邦唐夫人", "Bontemps": "邦唐",
    "Princesse de Parme": "帕尔马亲王夫人", "Parme": "帕尔马",
    "Mme de Stermaria": "斯泰尔玛丽亚夫人", "Stermaria": "斯泰尔玛丽亚",
    "Forcheville": "福什维尔", "Norpois": "诺普瓦",
    "Tansonville": "当松维尔", "Doncières": "当西埃尔",
    "Verrières": "韦里耶尔", "Illiers": "伊利耶",
    "Étretat": "埃特尔塔", "Trouville": "特鲁维尔",
    "Rivebelle": "里夫贝尔", "La Raspelière": "拉斯普利埃",
    "Montjouvain": "蒙茹万", "Méséglise": "梅塞格利斯",
    "Simonet": "西蒙内", "Andrée": "安德烈",
    "Léa": "莱娅", "Mme Verdurin": "韦尔迪兰夫人",
    "Princesse de Guermantes": "盖尔芒特亲王夫人",
    "Duchesse de Guermantes": "盖尔芒特公爵夫人",
    "Duc de Guermantes": "盖尔芒特公爵",
    "M. de Guermantes": "德·盖尔芒特先生",
    "M. de Charlus": "德·夏尔吕先生",
    "M. de Saint-Loup": "德·圣卢先生",
    "Mme de Saint-Loup": "德·圣卢夫人",
    "Mme Swann": "斯万夫人", "O Mme Swann": "噢，斯万夫人",
    "la Bergotte": "贝戈特", "la Verdurin": "韦尔迪兰夫人",
    "la Prince de Guermantes": "盖尔芒特亲王",
    "Bloch": "布洛克", "Le Catelet": "勒卡特莱",
    "Princesse d'Iéna": "耶纳亲王夫人",
    "Cambremer": "康布雷梅", "Mme de Cambremer": "康布雷梅夫人",
    "l'Hôtel de Guermantes": "盖尔芒特府",
    "l'Église": "教堂", "la Madeleine": "玛德莱娜教堂",
    "le Jardin des Plantes": "巴黎植物园",
    "Champs-Élysées": "香榭丽舍", "Rue de la Paix": "和平街",
    "le Bois": "树林", "Combray": "贡布雷",
    "les Guermantes": "盖尔芒特这一族", "côté de Guermantes": "盖尔芒特家那边",
    "côté de Méséglise": "梅塞格利斯那边", "les deux côtés": "两条散步的路",
    "plaisir": "愉悦", "ennui": "厌烦", "habitude": "习惯",
    "mémoire involontaire": "非自主记忆", "le temps perdu": "逝去的时光",
    "le Temps retrouvé": "重现的时光", "Albertine": "阿尔贝蒂娜",
    "les jeunes filles": "那群少女", "la mer": "大海",
    "une auberge": "客栈", "la sonate": "奏鸣曲",
}

G = {**_ZHOU, **_REST}
CORE = ["Swann", "Albertine", "Charlus", "Saint-Loup", "Combray", "Balbec",
        "Guermantes", "Vinteuil", "Bergotte", "Verdurin"]


def relevant(text: str, limit: int = 130) -> dict[str, str]:
    """Glossary entries that occur in this source chunk, plus the core set."""
    out = {k: G[k] for k in CORE if k in G}
    for k, v in G.items():
        if k in out:
            continue
        if re.search(r"\b" + re.escape(k) + r"\b", text, re.I):
            out[k] = v
        if len(out) >= limit:
            break
    return out


def render(entries: dict[str, str]) -> str:
    if not entries:
        return ""
    lines = [f"{k} = {v}" for k, v in sorted(entries.items())]
    return "【专名对照表（与周克希先生既有译文保持一致，必须严格照用）】\n" + "\n".join(lines)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print("glossary entries:", len(G))
    zhou = {}
    if os.path.exists(_Z):
        zhou = json.load(open(_Z, encoding="utf-8"))
    print("confirmed in Zhou's text:", len(zhou))
