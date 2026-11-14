
"""Recover the Chinese rendering of every source proper noun, then find variants.

Why not cluster Chinese look-alikes: every six-character window of a Chinese sentence
looks like a name, so a character-level scan produces hundreds of fragments ("克西米
利亚诺" cut out of "马克西米利亚诺") for one real variant. The source knows what the
names are; the translation knows how they were written. Aligning the two by chapter
gives one candidate per name, and the variants are whatever else the translator wrote
for the same name in the same chapters.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

CJK = r"\u4e00-\u9fff"
NAME = re.compile(r"[A-ZÄÖÜ][a-zäöüßâêîôûçáéíóúñ]{2,}")

STOP = set("""The And But She He It They We You I His Her Their Our Your My This That These Those
When Then What Which Who Whom Why How Where There Here Now So If As At In On Of Or For With
Not All One Two Three Four Five Six Seven Eight Nine Ten No Yes Oh Ah Well Come Look Said
Chapter Part Book Volume Page Mr Mrs Miss Sir Lady Lord God Heaven
Der Die Das Den Dem Des Ein Eine Einer Eines Und Aber Ich Du Er Sie Es Wir Ihr Nicht Auch
Noch Nur Schon Wenn Als Wie Was Wer Wo Warum Dann Da Hier Dort Jetzt So Ja Nein Oh Ach Nun
Denn Doch Viel Mehr Sehr Alle Eines Kein Keine Habe Hat Hatte Wird Wurde Kann Muss Soll
Le La Les Un Une Des Du De Et Mais Il Elle Ils Elles Je Tu Nous Vous Ce Cette Ces Son Sa
Ses Mon Ma Mes Qui Que Quoi Quand Comme Pour Par Avec Sans Sur Dans Plus Tres Tout Tous
Toute Alors Donc Oui Non Ah Oh Eh Bien Voila Voici Monsieur Madame Mademoiselle
El Los Las Un Una Unos Unas Y Pero Que Como Cuando Para Por Con Sin Su Sus Del Al Es Son
Era Fue Ser Estar Hay Muy Todo Todos Toda Todas No Si Ya Oh Ah Bien Senor Senora Don Dona
Il Lo Gli I Le Un Uno Una Che Chi Cui Come Quando Per Con Suo Sua Non Si Ma Anche Piu
O A E Di Da In Del Della Dei Delle""".split())

# Syllables used in transliterated names. A candidate made mostly of these is a name;
# a candidate made of ordinary characters is a phrase that happens to co-occur.
SYL = set("阿尔巴布莱布鲁蒂德迪杜多厄恩法菲弗福盖戈格哈海赫霍基吉加杰卡凯科克库拉莱雷里利卢鲁路罗洛马玛梅蒙米摩莫姆穆纳奈内尼涅诺帕皮普奇齐乔萨塞桑瑟森沙舍什施舒斯苏索塔泰坦汤特提图托瓦威维沃乌西希夏谢辛休雅亚耶伊尤于约泽扎詹兹")


def src_text(book_dir: str, cid: str) -> str:
    p = os.path.join(book_dir, "src", cid + ".json")
    if not os.path.exists(p):
        return ""
    d = json.load(open(p, encoding="utf-8"))
    return "\n".join((b.get("text") or "") for b in d.get("blocks") or [])


def zh_text(out_dir: str, cid: str) -> str:
    fs = sorted(glob.glob(os.path.join(out_dir, cid, "c*", "final.txt")))
    return "\n".join(open(f, encoding="utf-8").read() for f in fs)


def units(root: str) -> list[tuple[str, str]]:
    """(source, Chinese) pairs, one per translated chunk.

    Chapter granularity is useless for Faust: the whole play is one chapter. The
    chunk is the unit the translator actually worked in, so a name that occurs in
    three chunks gives three independent chances to see how it was written.
    """
    out = []
    for p in sorted(glob.glob(os.path.join(root, "chunks", "c*.json"))):
        cid = os.path.basename(p)[:-5]
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:                                        # noqa: BLE001
            continue
        for i, blocks in enumerate(d.get("chunks") or []):
            src = "\n".join((b.get("text") or "") for b in blocks if isinstance(b, dict))
            fp = os.path.join(root, "out", cid, f"c{i:02d}", "final.txt")
            if not src.strip() or not os.path.exists(fp):
                continue
            zh = open(fp, encoding="utf-8").read()
            if zh.strip():
                out.append((src, zh))
    return out


def analyse(root: str) -> dict:
    pairs = units(root)
    cnt = Counter()
    where = defaultdict(list)
    for i, (src, _zh) in enumerate(pairs):
        for m in NAME.finditer(src):
            w = m.group(0)
            if w in STOP:
                continue
            cnt[w] += 1
            where[w].append(i)
    names = {}
    # Where each Chinese candidate occurs, so a candidate can be scored on precision
    # and not only on recall: 菲斯 occurs in every chunk of Faust because it sits
    # inside 梅菲斯特, and only precision tells the two apart.
    gwhere: dict[str, set[int]] = defaultdict(set)
    for i, (_src, zh) in enumerate(pairs):
        for m in re.finditer(rf"[{CJK}]{{2,8}}", zh):
            run = m.group(0)
            for j in range(len(run)):
                for L in (2, 3, 4, 5, 6, 7, 8):
                    if j + L <= len(run):
                        gwhere[run[j:j + L]].add(i)
    for name, n in cnt.items():
        idx = set(where[name])
        if n < 3 or len(idx) < 3:
            continue
        best = []
        for g, seen in gwhere.items():
            if len(g) < 3:
                continue
            hit = len(seen & idx)
            if hit < 0.7 * len(idx):
                continue
            prec = hit / len(seen)
            if prec < 0.75:
                continue
            if sum(1 for ch in g if ch in SYL) < max(2, len(g) - 2):
                continue
            best.append((prec * hit, prec, len(g), g))
        if not best:
            continue
        best.sort(reverse=True)
        # drop fragments of the winner (克西米利亚诺 out of 马克西米利亚诺)
        top = best[0][3]
        alts = [g for _s, _p, _L, g in best[1:]
                if g not in top and top not in g][:4]
        names[name] = {"count": n, "chunks": len(idx), "zh": top,
                       "precision": round(best[0][1], 2), "alt": alts}
    return names


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for root in sys.argv[1:]:
        print("==", root)
        res = analyse(root)
        for k, v in sorted(res.items(), key=lambda kv: -kv[1]["count"])[:25]:
            print(f"   {k:24s} {v['count']:4d} ch={v['chunks']:3d} -> {v['zh']}  alt={v['alt'][:3]}")
