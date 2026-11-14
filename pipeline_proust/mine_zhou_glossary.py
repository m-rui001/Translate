"""Mine Zhou Kexi's own name renderings from his translated volumes.

We build a candidate list of Proust proper nouns (from the French source) and
check which Chinese rendering his published text actually uses. Anything we
cannot confirm stays at his most likely form, but confirmed hits keep the new
volumes consistent with his existing ones.
"""
from __future__ import annotations

import glob
import json
import re
import sys
import zipfile

EPUB = "E:/Translate/追寻逝去的时光.epub"
OUT = "E:/Translate/work_proust/glossary_zhou.json"

# french -> [candidate renderings in order of likelihood]
CAND = {
    # people
    "Marcel": ["马塞尔"], "Swann": ["斯万"], "Odette": ["奥黛特"],
    "Gilberte": ["吉尔贝特"], "Charles": ["夏尔"], "Charlus": ["夏尔吕", "夏吕斯"],
    "Saint-Loup": ["圣卢"], "Robert": ["罗贝尔"], "Albertine": ["阿尔贝蒂娜"],
    "Morel": ["莫雷尔"], "Bloch": ["布洛什", "布洛克", "布洛赫"],
    "Bergotte": ["贝戈特"], "Verdurin": ["韦尔迪兰", "维尔迪兰"],
    "Princesse de Guermantes": ["盖尔芒特亲王夫人"],
    "Duchesse de Guermantes": ["盖尔芒特公爵夫人"],
    "Duc de Guermantes": ["盖尔芒特公爵"],
    "Mme de Villeparisis": ["维尔帕里西斯夫人", "维尔帕里西"],
    "Norpois": ["诺普瓦"], "Balançoire": ["秋千"], "Forcheville": ["福什维尔"],
    "Princesse de Parme": ["帕尔玛亲王夫人"],
    "Mme de Stermaria": ["斯台尔玛丽亚夫人"],
    "Elstir": ["埃尔斯蒂尔"], "Cottard": ["科塔尔"], "Jupien:": ["朱皮安"],
    "Jupien": ["朱皮安"], "Venteville": ["旺德夫尔"],
    "Léa": ["莱娅"], "Oriane": ["奥里亚娜"], "Basin": ["巴赞"],
    "Mme Bontemps": ["邦唐夫人"], "Simonet": ["西蒙内"],
    "Andrée": ["安德烈"], "Rachilde": ["拉希尔德"],
    "Le Catelet": ["勒卡特莱"], "Tête": ["特隆贝尔"],
    "Mme de Sévigné": ["塞维涅夫人"], "Babenko": ["巴宾科"],
    "Griamphi": ["格里扬菲"], "Mme de Sévigné": ["塞维涅夫人"],
    "Proust": ["普鲁斯特"], "Larbaud": ["拉尔博"],
    # places
    "Combray": ["贡布雷"], "Balbec": ["巴尔贝克"], "Tansonville": ["当松维尔", "唐松维尔"],
    "Doncières": ["当西埃尔"], "Paris": ["巴黎"], "Guermantes": ["盖尔芒特"],
    "Verrières": ["韦里耶尔"], "Illiers": ["伊利耶"], "Illiers-Combray": ["伊利耶-贡布雷"],
    "Étretat": ["埃特尔塔"], "Trouville": ["特鲁维尔", "特鲁维尔海滨"],
    "Cannes": ["戛纳"], "Aix": ["艾克斯"], "Venise": ["威尼斯"],
    "Londres": ["伦敦"], "Bergame": ["贝加莫"], "Houdemer": ["乌德梅尔"],
    "Rivebelle": ["里夫贝尔"], "La Raspelière": ["拉斯普利埃", "拉斯贝尔耶尔"],
    "Montjouvain": ["蒙茹万"], "Gourdon": ["古尔东"],
    "Méséglise": ["梅塞格利斯"], "Way side": ["田野"],
    "Champs-Élysées": ["香榭丽舍"], "Rue": ["街"],
    # concepts / key terms
    "mémoire involontaire": ["非自主记忆", "无意记忆"],
    "habit": ["习惯"], "temps perdu": ["逝去的时光"],
    "petite phrase": ["小乐句"], "sonate": ["奏鸣曲"],
    "madeleine": ["玛德莱娜", "马德莱娜"],
    "hawthorn": ["山楂"], "lilas": ["丁香"],
    "verger": ["果园"], "goéland": ["海鸥"],
    "plésiade": ["七星诗社"],
}


def load_zhou_text() -> str:
    z = zipfile.ZipFile(EPUB)
    parts = []
    for n in sorted(z.namelist()):
        if re.match(r"text/part\d+\.html", n):
            raw = z.read(n).decode("utf-8", errors="ignore")
            body = re.sub(r"<[^>]+>", " ", raw)
            parts.append(body)
    return re.sub(r"\s+", " ", " ".join(parts))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ref = load_zhou_text()
    out, unresolved = {}, []
    for fr, cands in CAND.items():
        counts = [(ref.count(c), c) for c in cands]
        counts.sort(reverse=True)
        if counts[0][0] > 0:
            out[fr] = {"zh": counts[0][1], "n": counts[0][0]}
        else:
            unresolved.append((fr, cands))
    print(f"confirmed {len(out)} / {len(CAND)}")
    print("\n未确认（周克希文本中未找到，需人工核对或沿用候选）:")
    for fr, c in unresolved:
        print("  ", fr, c)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
