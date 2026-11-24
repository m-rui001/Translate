# -*- coding: utf-8 -*-
"""2026-11-25 润色轮：work_proust/out_ind/v5 chunk042-048
只改七类；专名不动；不拆段、不拆长句；定位唯一子串→替换→断言命中数==1。
"""
import ast
import os
import shutil

BASE = os.path.join("E:", os.sep, "Translate", "work_proust", "out_ind", "v5")

# (chunk, old, new, 类别)
EDITS = [
    # chunk042
    ("042",
     "也不觉得因为告诉她我要陪她去韦尔迪兰家，就采用了父亲那种突兀的方式有什么可指责",
     "也不觉得我因为告诉她我要陪她去韦尔迪兰家、便采用父亲那种突兀的方式有什么可指责",
     "①读不通"),
    ("042",
     "临走时在门口，作为插入语问他一个消息，而他连听都懒得听的样子，这就等于告诉兄弟",
     "临走时在门口，作为插入语问他一个消息，而他摆出一副连听都懒得听的样子，这就等于告诉兄弟",
     "①读不通"),
    # chunk044
    ("044",
     "而这气息不知一切恶，与其说取自一个人，宁可说取自一根挖空的芦苇",
     "而这气息对一切恶一无所知，与其说取自一个人，不如说取自一根挖空的芦苇",
     "③外语句法"),
    # chunk045
    ("045",
     "说不去韦尔迪兰家做客的那场晚会，第二天我一早就醒了",
     "说不去韦尔迪兰家做客的那场晚会之后的第二天，我一早就醒了",
     "①读不通"),
    # chunk046
    ("046",
     "而只有这些人才有好处对您撒谎，为了弄清，为了阻止。",
     "而只有这些人才有理由对您撒谎，为了弄清，为了阻止。",
     "①读不通"),
    ("046",
     "您心底里并不相信我爱的您，真怪。",
     "您心底里并不相信我是在爱您，真怪。",
     "①读不通"),
    ("046",
     "“哦！我清楚得很，您活不过我四十八小时，您会自杀的。”",
     "“哦！我清楚得很，您比我多活不了四十八小时，您会自杀的。”",
     "⑥硬伤"),
    # chunk047
    ("047",
     "有一种真相，比我们若真诚相待时所说出的更为深刻",
     "有一种真相，比我们若真诚相待时所说的话更为深刻",
     "①读不通"),
    ("047",
     "这样的睡眠（平均而言）要恢复精力四倍",
     "这样的睡眠（平均而言）恢复的精力是平时的四倍",
     "①读不通"),
    # chunk048
    ("048",
     "园丁培育出的花，有些是甜美的梦，有些则像噩梦。",
     "这些睡眠里，有些是甜美的梦，有些则像噩梦。",
     "④指代"),
    ("048",
     "只不过它们不是用大理石雕成的，恰恰相反，是虚而不实的。",
     "只不过它们不是用大理石雕成的，恰恰相反，是无形无体的。",
     "⑥硬伤"),
    ("048",
     "它是习惯的朋友，习惯每晚把它留住，比它本身更固定地留在它那惯常的处所",
     "它是习惯的朋友，习惯每晚把它留住，比它本身更固定地把它留在惯常的处所",
     "①读不通"),
    ("048",
     "总努力早早醒来，一点不落这些叫卖声。",
     "总努力早早醒来，一个不落地听全这些叫卖声。",
     "①读不通"),
]


def path_of(chunk):
    return os.path.join(BASE, "chunk%s" % chunk, "final.txt")


def main():
    stats = {}
    touched = set()
    for chunk, old, new, kind in EDITS:
        p = path_of(chunk)
        # 备份（已存在则不覆）
        bak = p + ".bak_20261125"
        if not os.path.exists(bak):
            shutil.copyfile(p, bak)
        with open(p, "r", encoding="utf-8", newline="") as f:
            text = f.read()
        if old not in text:
            # 断点续跑：已应用过则跳过
            assert text.count(new) == 1, "MISS %s: %s" % (chunk, old[:20])
            touched.add(chunk)
            stats[kind] = stats.get(kind, 0) + 1
            continue
        assert text.count(old) == 1, "DUP %s: %s" % (chunk, old[:20])
        text = text.replace(old, new)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        touched.add(chunk)
        stats[kind] = stats.get(kind, 0) + 1

    # 自检：行数、空段、ASCII 引号、⟦⟧
    for chunk in sorted(touched):
        p = path_of(chunk)
        bak = p + ".bak_20261125"
        with open(p, "r", encoding="utf-8", newline="") as f:
            t = f.read()
        with open(bak, "r", encoding="utf-8", newline="") as f:
            b = f.read()
        assert t.count("\r\n") == b.count("\r\n"), "EOL %s" % chunk
        la = t.split("\r\n")
        lb = b.split("\r\n")
        assert len(la) == len(lb), "LINES %s" % chunk
        assert [i for i, l in enumerate(la) if l.strip() == ""] == \
               [i for i, l in enumerate(lb) if l.strip() == ""], "EMPTY %s" % chunk
        for ch in ('"', "'"):
            assert ch not in t, "ASCII-QUOTE %s" % chunk
        assert "⟦" not in t and "⟧" not in t, "MARKUP %s" % chunk
        assert t.count("“") == t.count("”"), "QUOTE-PAIR %s" % chunk
        print("OK chunk%s  lines=%d  paras=%d" %
              (chunk, len(la), len([l for l in la if l.strip()])))

    total = sum(stats.values())
    print("total edits:", total, stats)


main()
ast.parse(open(__file__, encoding="utf-8").read())