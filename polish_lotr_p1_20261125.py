"""《魔戒》润色 第 1 批：全册专名归一。

只做「定位唯一子串 → 替换 → 断言命中数」。按段落替换，段落内命中数精确断言，
章内合计命中数再断言一次。改前备份 .bak_20261125。

canon 取法（POLISH_BRIEF 二·5）：出现次数最多者，少数派一律归一；
个别 canon 存疑处取通行汉译，理由逐条写在 TERMS 的注释里。
"""
from __future__ import annotations

import ast
import json
import os
import shutil
import sys

FINAL = "work_overhaul/lotr/final"

# (旧形, 新形, 全册应替换总数)
TERMS: list[tuple[str, str, int]] = [
    # 加拉德瑞尔是另一译本系统的写法，本书正文 66 处作凯兰崔尔
    ("加拉德瑞尔", "凯兰崔尔", 18),
    # Elessar：13 处作埃莱萨，2 处作伊力萨
    ("伊力萨", "埃莱萨", 2),
    # smial：9 处作斯密奥，序里 2 处作斯密尔
    ("斯密尔", "斯密奥", 2),
    # Bucklebury：9 处作雄鹿堡，2 处作雄鹿镇（雄鹿地是 Buckland，另一地名，不动）
    ("雄鹿镇", "雄鹿堡", 2),
    # Michel Delving：10 处作米丘窟，1 处作大洞镇
    ("大洞镇", "米丘窟", 1),
    # Inglorion：两处两种写法，统一为通行汉译英格洛瑞安
    ("英格洛里安", "英格洛瑞安", 1),
    ("英格罗瑞安", "英格洛瑞安", 1),
    # Lothlórien：113 处罗斯洛立安，1 处洛丝罗立安
    ("洛丝罗立安", "罗斯洛立安", 1),
    # hobbit：781 处霍比特人，1 处哈比人
    ("哈比人", "霍比特人", 1),
    # orc：565 处半兽人，4 处奥克
    ("奥克", "半兽人", 4),
    # Entwash：18 处恩特河，另有恩特沛河 2、恩特洗河 1
    ("恩特沛河", "恩特河", 2),
    ("恩特洗河", "恩特河", 1),
    # Mirkwood：39 处幽暗密林，序里 1 处黑森林（原文正说「得了个新名字」）
    ("黑森林", "幽暗密林", 1),
    # troll：41 处食人妖，5 处巨魔
    ("巨魔", "食人妖", 5),
    # palantír：20 处真知晶球，8 处真知晶石
    ("真知晶石", "真知晶球", 8),
    # Cracks of Doom：6 处末日裂隙，1 处末日罅隙
    ("末日罅隙", "末日裂隙", 1),
    # the Ruling Ring：8 处统御魔戒，1 处至尊魔戒
    ("至尊魔戒", "统御魔戒", 1),
    # Pelennor：20 处帕兰诺，4 处佩兰诺
    ("佩兰诺", "帕兰诺", 4),
    # Ered Nimrais：2 处埃瑞德宁莱斯，1 处埃雷德尼姆莱斯
    ("埃雷德尼姆莱斯", "埃瑞德宁莱斯", 1),
    # Osgiliath：29 处奥斯吉力亚斯，3 处奥斯吉利亚斯
    ("奥斯吉利亚斯", "奥斯吉力亚斯", 3),
    # Peregrin：48 处佩里格林，4 处佩瑞格林
    ("佩瑞格林", "佩里格林", 4),
    # Bergil：16 处贝吉尔，3 处伯吉尔
    ("伯吉尔", "贝吉尔", 3),
    # Ithilien：13 处伊希利恩，3 处伊西利恩
    ("伊西利恩", "伊希利恩", 3),
    # Silverlode：15 处银流河，2 处银脉河，另有 1 处「银色溪流」同指
    ("银脉河", "银流河", 2),
    ("银色溪流", "银流河", 1),
    # Cirith Ungol：13 处西力斯昂哥，5 处奇立斯乌苟
    ("奇立斯乌苟", "西力斯昂哥", 5),
    # Eorl：24 处埃奥尔，3 处伊奥尔
    ("伊奥尔", "埃奥尔", 3),
    # Tharbad：2 处塔巴德，1 处沙巴德
    ("沙巴德", "塔巴德", 1),
]


def load(p: str) -> dict:
    with open(p, encoding="utf-8", newline="") as f:
        return json.load(f)


def dump(p: str, d: dict) -> None:
    with open(p, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main(apply: bool) -> None:
    files = sorted(f for f in os.listdir(FINAL)
                   if f.endswith(".json") and not f.endswith(".polished.json"))
    docs = {f: load(os.path.join(FINAL, f)) for f in files}
    hits: dict[tuple[str, str], list[tuple[str, int, int]]] = {}
    for f, d in docs.items():
        texts = d["texts"]
        for old, new, _ in TERMS:
            if old == new or old in new:
                raise SystemExit(f"bad pair {old}->{new}")
            got = 0
            for i, t in enumerate(texts):
                c = t.count(old)
                if c:
                    hits.setdefault((old, new), []).append((f, i, c))
                    got += c
    total_ok = True
    for old, new, expect in TERMS:
        got = sum(c for _, _, c in hits.get((old, new), []))
        flag = "OK " if got == expect else "MISMATCH"
        if got != expect:
            total_ok = False
        print(f"{flag} {old}->{new}: {got} (expect {expect}) "
              f"in {len(hits.get((old, new), []))} paras")
    if not total_ok:
        raise SystemExit("count mismatch, abort")
    if not apply:
        for (old, new), lst in hits.items():
            for f, i, c in lst:
                print(f"  {f}[{i}] x{c}  {old}->{new}")
        return
    changed = 0
    for (old, new), lst in hits.items():
        for f, i, c in lst:
            texts = docs[f]["texts"]
            assert texts[i].count(old) == c, (f, i, old)
            old_text = texts[i]
            texts[i] = texts[i].replace(old, new)
            assert old not in texts[i]
            assert len(texts[i]) <= len(old_text) + c * (len(new) - len(old)) + 0
            changed += 1
    for f, d in docs.items():
        bak = os.path.join(FINAL, f + ".bak_20261125")
        if not os.path.exists(bak):
            shutil.copy2(os.path.join(FINAL, f), bak)
        dump(os.path.join(FINAL, f), d)
    print("paragraph replacements:", changed)


if __name__ == "__main__":
    main("--apply" in sys.argv)
    ast.parse(open(__file__, encoding="utf-8").read())