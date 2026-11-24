# -*- coding: utf-8 -*-
"""v3 chunk035 / 036 / 038 / 039 / 041 逐段润色（2026-11-26 轮）

准则：E:/Translate/POLISH_BRIEF_2026-11-25.md（只改七类，不重译、不改情节、不动段数）
canon：E:/Translate/scratch/rev2026/proust_canon_1125.md
源文：work_proust/chunks/v3/chunkNNN.json（法文段落数组）

落盘方式：定位唯一子串 -> 替换 -> assert text.count(old) == 1，绝不整文件重写。
换行符：newline='' 读写，CRLF/LF 原样保留。
用法：先 cp final.txt final.txt.bak_20261125（已存在则跳过，不覆盖），再运行本脚本。
"""
import ast
import io
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = "final.txt.bak_20261125"

# (chunk, 类别, old, new, 法文依据)
EDITS = [
    # ---------------- chunk035 ----------------
    ("035", "①",
     "还把活龙虾投进店主所谓的“永恒之火”",
     "活龙虾被投进店主所谓的“永恒之火”",
     # où des homards encore vivants étaient jetés dans ce que l'hôtelier appelait le « feu éternel »
     # 前两个分句「转着…鸡，烤着猪」是存现句，第三个却用「把」字句，主语（谁把龙虾投进去）
     # 在句中从未出现 —— 缺主语的流水句。改为受事在前，与前两句并列，即立。
     ),

    ("035", "③",
     "许多已经接近尾声的饭菜在我到达时却未被动用地堆着",
     "许多已经接近尾声的饭菜在我到达时却堆在那里，无人动用",
     # « beaucoup de repas touchant à leur fin, quand j'arrivais » ils s'entassaient inutilisés
     # inutilisés 是形容词作伴随状语的直搬，被译成「未被动用地」——汉语没有这种「被+动用地」
     # 的叠合，读来像衍字。改成两个谓语分句，语义不变。
     ),

    ("035", "③",
     "那汉子有时似乎被支撑在一只水晶鸭的翅膀上",
     "那汉子有时似乎就立在一只水晶鸭的翅膀上",
     # un énorme bonhomme quelquefois supporté sur les ailes d'un canard en cristal
     # 独立分词 supporté sur 被搬成「被支撑在…上」：汉语「被支撑在」既生硬又把施动者悬空；
     # 这里说的是那座冰雕人像立在鸭翅上，改用「立在」即可。
     ),

    ("035", "①",
     "“好”充当一道开胃菜，好让人等一会儿，好找到话：",
     "“好”充当一道开胃菜，让人先等一会儿，好找到话：",
     # « Bonne » sert de hors-d'œuvre et permet d'attendre un instant qu'on ait trouvé
     # 句首那个「好」是被引号括起的名词（=「好」这个字），紧接两个副词「好…好…」，
     # 三个「好」连排成一串，读者先卡一次。删去第一个副词「好」，「让人先等一会儿」即通。
     ),

    ("035", "④",
     "指的是一个你认识、而你又不太知道跟一个并非你密友的人该说她什么的人。",
     "指的是这么一个人：你认识她，却不太清楚跟一个并非你密友的人该怎么说她。",
     # désignant une personne qu'on connaît et dont on ne sait trop que dire avec quelqu'un
     # qui n'est pas de votre intimité
     # 两个「一个」在同一从句里指两个人（被指的人 / 并非密友的人），末尾「…的人」与前一个
     # 「一个…的人」套在一起，中心语被压没；②「的」字堆叠与④指代不明同时成立。拆成冒号顺句。
     ),

    # ---------------- chunk036 ----------------
    ("036", "③",
     "德·盖尔芒特夫人知道我和他——一个聪明人等等——有来往的动机向我提问题",
     "德·盖尔芒特夫人知道——他是个聪明人，等等——我和他有来往的动机，向我提问题",
     # de me poser sur mes motifs de désirer que Mme de Guermantes me sût lié avec lui,
     # intelligent, etc., des questions
     # 同位语 intelligent, etc. 被照搬成破折号，正插在「知道我和他」与「有来往」之间，
     # 把宾语从句拦腰截断（同 2026-11-25 判例「括注破折号插在主谓之间」）。破折号前移到
     # 「知道」之后，宾语「我和他有来往」恢复完整；句末补逗号断开「向我提问题」。
     ),

    ("036", "①",
     "我实际上在意它，还只是为了试探您，都无关紧要",
     "我是否真的在意它，还是只为了试探您，都无关紧要",
     # que j'y tienne en réalité ou seulement pour vous éprouver, peu importe
     # 「还是」缺了与之配对的「是否」，「我实际上在意它，还只是为了试探您」是两个并列陈述
     # 而非两个待选情形，后面接「都无关紧要」便无着落。补「是否真的…还是…」，选择题成立。
     ),

    # ---------------- chunk038 ----------------
    ("038", "⑤⑥",
     "一位犹太太太，她的本堂神甫谴责",
     "一位犹太太太，她的本堂神父谴责",
     # une dame juive ... que son curé blâme les massacres de juifs
     # 两处：①「太太太」为衍字（太太→太太）；②presbytère/curé 系统内 canon 作「本堂神父」
     # （全库「本堂神父」28 次 vs「本堂神甫」15 次，且 POLISH_BRIEF 二·5 明文规定
     # 天主教 curé 作「本堂神父」；「神甫」仅保留给巴尔扎克书名《图尔的本堂神甫》）。
     ),

    ("038", "⑦",
     "齐格弗里德—圣卢",
     "齐格弗里德-圣卢",
     # le jeune Siegfried-Saint-Loup
     # 复合专名用半角连字符（canon「体例」条：玛丽-安托瓦内特、圣安德烈-德尚普…），
     # 此处误用破折号，全库仅此 1 例。
     ),

    # ---------------- chunk039 ----------------
    ("039", "①",
     "这既是出于对圣卢那些朋友的礼貌，圣卢那些德雷福斯派的信仰表白令他们难受，也是因为",
     "这既是出于对圣卢那些朋友的礼貌，因为圣卢那些德雷福斯派的信仰表白令他们难受，也是因为",
     # Autant par politesse pour ses amis à qui les professions de foi dreyfusardes de
     # Saint-Loup étaient pénibles que parce que le reste m'intéressait davantage
     # 关系从句 à qui… 被搬成并列陈述句塞进「既是…也是…」的框架中间，没有连接词，
     # 「圣卢那些德雷福斯派的信仰表白令他们难受」自成一句、前后不接。补一个「因为」即挂回。
     ),

    # ---------------- chunk041 ----------------
    ("041", "①",
     "并没有上当",
     "并没有让我上当",
     # que peut-être je n'étais pas dupe dans ma vie de Doncières
     # 主语是「我在当西埃尔过的这种生活」——「生活」不能「上当」，主谓失配。补「让我」，
     # 让「生活」回到状语位置，施受关系落实。
     ),

    ("041", "④",
     "那个想从敌人的计划中读出他意图的对手",
     "那个想从你的计划中读出你意图的敌方",
     # la divination chez l'adversaire qui veut lire dans ses plans
     # 「对手」与「敌人」本是同一人，译文却让「对手」去读「敌人」的计划，一段里两个称谓
     # 指同一人而又互相充当对方的宾语，读者必错认。按法文（敌方读的是统帅的计划）归一为「敌方」。
     ),
]

BACKUP_ONLY = {"035", "036", "038", "039", "041"}
CHUNKS = sorted({c for c, *_ in EDITS} | BACKUP_ONLY)
report = []


def load(chunk):
    path = os.path.join(BASE, "chunk%s" % chunk, "final.txt")
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        return path, f.read()


def stats(text):
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)
    han = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return nl, len(lines), sum(1 for l in lines if l.strip()), han


dry = "--dry" in __import__("sys").argv

for chunk in CHUNKS:
    path, text = load(chunk)
    bak = os.path.join(os.path.dirname(path), BAK)
    nl0, ln0, ne0, han0 = stats(text)
    n = 0
    for c, cat, old, new, *_why in EDITS:
        if c != chunk:
            continue
        assert old in text, "NOT FOUND [%s] %s" % (chunk, old[:30])
        assert text.count(old) == 1, "NOT UNIQUE [%s] %s (%d)" % (
            chunk, old[:30], text.count(old))
        text = text.replace(old, new, 1)
        n += 1
    nl1, ln1, ne1, han1 = stats(text)
    assert nl0 == nl1, "newline changed"
    assert ln0 == ln1, "line count changed %d->%d" % (ln0, ln1)
    assert ne0 == ne1, "non-empty line count changed"
    assert text.count("\u27e6") == 0
    assert '"' not in text and "'" not in text
    assert text.count("\u201c") == text.count("\u201d"), "quote unpaired [%s]" % chunk
    if not dry:
        if os.path.exists(bak):
            pass  # 已存在：不覆盖（红线）
        else:
            shutil.copyfile(path, bak)
        if n:
            with io.open(path, "w", encoding="utf-8", newline="") as f:
                f.write(text)
    report.append((chunk, n, ln0, ln1, ne0, han0, han1,
                   "CRLF" if nl0 == "\r\n" else "LF"))

print("chunk | edits | lines(before=after) | paras | hanzi | newline")
for r in report:
    print("%s | %d | %d=%d | %d | %d->%d | %s" % r)

cats = {}
for c, cat, *_w in EDITS:
    for ch in cat:
        cats[ch] = cats.get(ch, 0) + 1
print("categories:", " ".join("%s=%d" % (k, cats[k]) for k in sorted(cats)))

# 自查：脚本本身可解析
ast.parse(io.open(__file__, encoding="utf-8").read())
print("self-check ast.parse OK; total edits =", sum(r[1] for r in report))