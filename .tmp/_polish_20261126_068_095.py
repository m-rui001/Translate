# -*- coding: utf-8 -*-
"""逐段润色落盘脚本 —— 第四卷 chunk068/070/072/075/095（2026-11-26）

铁律：只做「定位唯一子串 → 替换 → assert 命中数 == 1」，绝不整文件重写；
读写用 encoding='utf-8', newline=''，保持原换行符（CRLF）与空行结构。
段数与法文 JSON 数组长度一一对应，改后复查。
"""
import ast
import json
import os
import shutil

ROOT = r"E:/Translate/work_proust"
VOL = "v4"
CHUNKS = ["068", "070", "072", "075", "095"]
BAK_SUFFIX = ".bak_20261125"

# (chunk, 类别, 旧句片段, 新句片段)
EDITS = [
    # ---- chunk068 ----
    ("068", "①", "但也应当懂得不无动于衷，尽管她的话老生常谈",
                  "但也应当懂得不能无动于衷，尽管她的话老生常谈"),
    ("068", "⑥", "无法在她眼里唤起一点亲爱的目光",
                  "无法在她眼里唤起一点慈爱的目光"),
    ("068", "①", "把我照得那样优雅，那样无忧无虑",
                  "把她照得那样优雅，那样无忧无虑"),
    ("068", "⑤", "可是，您知道，您们是老主顾，我们一心想叫您们满意",
                  "可是，您知道，你们是老主顾，我们一心想叫你们满意"),
    ("068", "⑥", "是那疾病掴在外祖母这张被粗暴扇过的脸上的一个耳光",
                  "是那疾病掴向外祖母这张被粗暴扇过的脸的一个耳光"),
    # ---- chunk070 ----
    ("070", "③", "我每天被按在床上躺很久休息",
                  "人们每天让我在床上躺很久休息"),
    ("070", "①", "与那永恒海洋流动、不可企及、神话般的近邻之间的对立",
                  "与那流动、不可企及、神话般的永恒海洋近邻之间的对立"),
    ("070", "④", "至少也是第一眼的幻觉——它在想象中唤起的暗示",
                  "至少也是第一眼的幻觉——那种在想象中唤起的联想"),
    ("070", "①", "因为色彩空间界限分明地交替",
                  "因为界线分明的一块块色域彼此交替"),
    # ---- chunk072 ----
    ("072", "①", "然而有一样东西，激怒人的本领之大",
                  "然而有一样东西，其激怒人的本领之大"),
    ("072", "①", "以便那些晚上哪一天我需要她时好找",
                  "以便那些晚上我需要她时好找"),
    # ---- chunk075 ----
    ("075", "③", "那潜藏的爱情也搅着我，人总把它带在身上",
                  "那潜藏的爱情也揪着我，人总把它带在身上"),
    # ---- chunk095 ----
    ("095", "⑥", "他不久前甩了《阿塔莉》合唱队里的那个孩子",
                  "他不久前背着《阿塔莉》合唱队里的那个孩子"),
    ("095", "①", "要我后天去吃饭，为什么，很快就能见分晓",
                  "要我后天去吃饭，至于为什么，很快就能见分晓"),
    ("095", "⑥", "又想法子让人家改菜单了",
                  "又想法子让人家改了点菜"),
    ("095", "①", "它先走一步，是去换竖直方向的",
                  "它先走一步，走的是竖直方向"),
]


def hanzi(s):
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def paths(chunk):
    d = os.path.join(ROOT, "out", VOL, "chunk" + chunk)
    return d, os.path.join(d, "final.txt")


def main():
    report = []
    for chunk in CHUNKS:
        d, fin = paths(chunk)
        bak = fin + BAK_SUFFIX
        if not os.path.exists(bak):
            shutil.copy2(fin, bak)
            bak_state = "新建"
        else:
            bak_state = "已存在(未覆盖)"

        src_json = os.path.join(ROOT, "chunks", VOL, "chunk%s.json" % chunk)
        n_src = len(json.load(open(src_json, encoding="utf-8")))

        with open(fin, encoding="utf-8", newline="") as f:
            text = f.read()
        nl = "\r\n" if "\r\n" in text else "\n"
        before_lines = text.count(nl)
        before_han = hanzi(text)
        before_paras = len([p for p in text.split(nl + nl)])

        mine = [e for e in EDITS if e[0] == chunk]
        for _, cat, old, new in mine:
            assert text.count(old) == 1, (chunk, old)
            text = text.replace(old, new)

        after_lines = text.count(nl)
        after_han = hanzi(text)
        after_paras = len([p for p in text.split(nl + nl)])
        assert after_paras == before_paras == n_src, (chunk, before_paras, after_paras, n_src)
        assert after_lines == before_lines
        assert old_deco(text), chunk

        with open(fin, "w", encoding="utf-8", newline="") as f:
            f.write(text)

        report.append(dict(chunk=chunk, lines=(before_lines, after_lines),
                           han=(before_han, after_han), paras=after_paras,
                           n=len(mine), nl="CRLF" if nl == "\r\n" else "LF",
                           bak=bak_state))
    print("%-6s %-12s %-14s %-6s %-5s %-4s %s" % ("chunk", "行数改前后", "汉字改前后", "段数", "改动数", "换行", "备份"))
    for r in report:
        print("%-6s %-12s %-14s %-6d %-5d %-4s %s" % (
            r["chunk"], "%d/%d" % r["lines"], "%d/%d" % r["han"], r["paras"], r["n"], r["nl"], r["bak"]))
    print("总改动 %d 条" % sum(r["n"] for r in report))


def old_deco(text):
    """落盘前自检：引号成对、无半角省略号、无 ASCII 引号"""
    assert text.count("“") == text.count("”"), "引号不成对"
    assert '"' not in text.replace("‘", "").replace("’", ""), "残留 ASCII 双引号"
    assert "..." not in text, "半角省略号"
    return True


main()
ast.parse(open(__file__, encoding="utf-8").read())
print("ast.parse OK")