# -*- coding: utf-8 -*-
"""逐段润色 v3 chunk096-100（2026-11-26）。只做唯一子串定位替换，不整文件重写。"""
import ast
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

# (chunk, 类别, old, new, 说明)
UNIQUE = [
    # ---------------- chunk096 ----------------
    ("096", "①",
     "何况他还使出一种矫揉尖刻的才思",
     "何况他还动用一种矫揉尖刻的才思",
     "「使出…才思」动宾失配（user d'un esprit）"),
    ("096", "①",
     "布洛克的告别几乎没在侯爵夫人脸上绽开一个慵懒的微笑，也没能引出她一句话",
     "布洛克的告别几乎没能在侯爵夫人脸上展开一个慵懒的微笑，也没能引出她一句话",
     "「告别…绽开微笑」主语错配（déplissant à peine dans la figure de la marquise un languissant sourire）"),
    # ---------------- chunk097 ----------------
    ("097", "⑥",
     "那篇檄文玩意儿的作者",
     "那篇小册子玩意儿的作者",
     "factum 是小册子/论辩文字，非「檄文」"),
    ("097", "⑥",
     "“是的，他是比利时人，干的就是这一行，”他又说。",
     "“是的，论职业，他就是比利时人，”他又说。",
     "belge de son état 的「职业」即「比利时人」，非「干这一行」"),
    ("097", "④",
     "其中一个尽管对她的侄子颇有好意",
     "其中一位公主尽管对自己的侄子颇有好意",
     "L'une d'elle 紧接上文「比利时人」，指代易错认"),
    ("097", "⑥",
     "也以自己的圣徒般生活教化他们",
     "也以自己的圣徒般生活感化他们",
     "édifier 宗教义为感化/启迪，非「教化」"),
    ("097", "⑥",
     "穿着一件白色双绉长裙",
     "穿着一件白色苏拉绸长裙",
     "surah 是斜纹软绸（苏拉绸），非双绉"),
    # ---------------- chunk098 ----------------
    ("098", "⑥",
     "便求他别再提那个被判刑的人无辜",
     "便求他别再提那个被判刑的人是无辜的",
     "缺谓语助词，句子读断"),
    ("098", "①",
     "反而一直顶着斯万那毫不掩饰的愿望",
     "反而一直抵制斯万那个毫不掩饰的愿望",
     "「顶着…愿望」搭配不通（résisté au désir）"),
    ("098", "⑥",
     "可她今天非得来一趟",
     "可她今天只来这一趟",
     "pour une seule fois 的「只此一次」漏译"),
    ("098", "①",
     "其实德·马桑特夫人心想儿子不会有假",
     "其实德·马桑特夫人心想儿子请不到假",
     "「不会有假」易读成「不假」，permission 是准假"),
    ("098", "①",
     "公爵夫人对这庇护保留着既感激又含怨的记忆",
     "公爵夫人对这庇护保留着既感激又记仇的记忆",
     "rancunier 是记仇，非「含怨」"),
    # ---------------- chunk099 ----------------
    ("099", "①",
     "她任那蓝色目光的光辉洒落在我身上，迟疑了片刻，舒展手臂，把这手臂的枝条伸出去，身体向前倾去，随即又迅速向后挺直，像一株被压倒后又任其自由恢复原来姿势的灌木，她是在圣卢目光的火力下这样做的，圣卢正注视着她，远远地拼命使劲，想从姑母那里再多得到一点什么，他怕谈话冷落下来，便过来添些内容，替我回答道：",
     "她任那蓝色目光的光辉洒落在我身上，迟疑了片刻，舒展手臂，伸出那条枝条似的手臂，身体向前倾去，随即又迅速向后挺直，像一株被压倒后又任其自由恢复原来姿势的灌木。她是在圣卢的目光下这样做的：圣卢注视着她，远远地拼命使劲，想从姑母那里再多讨一点什么。他怕谈话冷落下来，便过来添些内容，替我回答道：",
     "三句法文并成一句流水句，中间插入「她是在…这样做的」把主语打断；另「把这手臂的枝条伸出去」重复"),
    ("099", "①",
     "它去参加舞会，坐着维多利亚马车兜风，过着一种神奇的生活。",
     "这个家族去参加舞会，坐着维多利亚马车兜风，过着一种神奇的生活。",
     "引语内「它」指「我的家族」，中文代词不可读"),
    # ---------------- chunk100 ----------------
    ("100", "①",
     "在我的记忆里找到了一个足够大的小位置",
     "在我的记忆里找到了一个小得足以容下它的位置",
     "「足够大的小位置」自相矛盾（trouver assez grande pour lui une petite place）"),
    ("100", "①",
     "于是这位亲王——当年在俄国两人同任大使时结识——便去拜访他",
     "于是这位亲王——当年两人在俄国同任大使时与他结识——便去拜访他",
     "破折号内悬空无谓语，读者不知谁与谁结识"),
]

# 专名归一：v3 全册 canon 为「德·马桑特夫人」（21 处），本两 chunk 用裸形「马桑特夫人」（11 处）
NAME_FIX = [("097", 8), ("099", 3)]


def load(chunk):
    p = os.path.join(BASE, "chunk" + chunk, "final.txt")
    with open(p, encoding="utf-8", newline="") as f:
        return p, f.read()


def save(p, text):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def count_paras(text):
    nl = "\r\n" if "\r\n" in text else "\n"
    return len([l for l in text.split(nl) if l.strip()])


def cjk(text):
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


report = []
for chunk in ["096", "097", "098", "099", "100"]:
    p, text = load(chunk)
    eol = "CRLF" if "\r\n" in text else "LF"
    before_paras, before_cjk = count_paras(text), cjk(text)
    n = 0

    # 1) 专名归一（批量，先做，避免与逐条替换互相干扰）
    for c, expect in NAME_FIX:
        if c != chunk:
            continue
        assert text.count("德·马桑特夫人") == 0, (chunk, "已有德·形式，勿批量")
        got = len(re.findall(r"(?<!德·)马桑特夫人", text))
        assert got == expect, (chunk, "马桑特夫人 计数", got, expect)
        text = re.sub(r"(?<!德·)马桑特夫人", "德·马桑特夫人", text)
        n += got
        report.append((chunk, "⑤", "马桑特夫人 ×%d" % got, "德·马桑特夫人", "专名归一（v3 canon）"))

    # 2) 唯一子串替换
    for c, cat, old, new, why in UNIQUE:
        if c != chunk:
            continue
        assert old in text and text.count(old) == 1, (chunk, cat, old[:20], text.count(old))
        text = text.replace(old, new)
        n += 1
        report.append((chunk, cat, old, new, why))

    after_paras, after_cjk = count_paras(text), cjk(text)
    assert before_paras == after_paras, (chunk, "段数变了")
    save(p, text)
    print("chunk%s 改动 %d 条 | 段数 %d→%d | 汉字 %d→%d | %s"
          % (chunk, n, before_paras, after_paras, before_cjk, after_cjk, eol))

print("\n---- 改动明细 ----")
for chunk, cat, old, new, why in report:
    print("[%s]%s %s\n   → %s\n   # %s" % (chunk, cat, old, new, why))

ast.parse(open(__file__, encoding="utf-8").read())
print("\nOK: %d 条" % len(report))