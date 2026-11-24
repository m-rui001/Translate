# -*- coding: utf-8 -*-
"""润色 v5 chunk075 / chunk076 / chunk081 / chunk107（2026-11-26）

只做「定位唯一子串 → 替换」，不重写整文件；保持 CRLF 与空行结构。
"""
import ast
import os
import re
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))

CHUNKS = {
    "075": [
        # ③ 被动式硬搬「被他请来」＋① 「心里受用」缺着落
        ("医生们被他请来，心里受用，便从他这位大工作家的美德",
         "医生们受他邀请，心里都很受用，便从他这位大工作家的美德"),
        # ⑥ 缺量词：「一位文坛宗师」
        ("尤其在一文坛宗师面前",
         "尤其在一位文坛宗师面前"),
        # ① 「阻止冷水澡害我们」句尾失据；法语是「不阻止它们害我们」
        ("却没有一位医生来阻止冷水澡害我们。",
         "却没有医生来制止它们害我们。"),
        # ① 「药效成功」说不通（avec succès, mais avec excès＝用得成功却过了度）
        ("转而试着用各种麻醉药，药效成功，但过了量。",
         "转而试着用各种麻醉药，试得成功，但过了量。"),
        # ③ 被动式硬搬「使他被嘱咐要休息」→ 主动
        ("一次相当轻的尿毒症发作，使他被嘱咐要休息。",
         "一次相当轻的尿毒症发作，医生嘱咐他要休息。"),
        # ① 「忽略了……严重」缺中心语
        ("这时他并没有忽略自己头晕的严重。",
         "这时他并没有忽视自己头晕的严重程度。"),
        # ⑥ imprudemment＝轻率、冒失，非「糊里糊涂」
        ("他感到自己糊里糊涂地以前者换了后者。",
         "他感到自己冒失地以前者换了后者。"),
    ],
    "076": [
        # ⑤ 专名归一：canon 作「贝戈特」（同册 43 见，他卷 93 见），本 chunk 3 处「贝尔戈特」为孤例
        ("因此，贝尔戈特并非永远死去了",
         "因此，贝戈特并非永远死去了"),
        ("我说过，那天我得知贝尔戈特死了。",
         "我说过，那天我得知贝戈特死了。"),
        ("因为那一天阿尔贝蒂娜根本没有碰见贝尔戈特",
         "因为那一天阿尔贝蒂娜根本没有碰见贝戈特"),
        # ①③ 关系从句后置被整句搬倒，主语悬空：「就像那块黄墙，一位……艺术家，画了出来」
        ("就像那个黄墙小片，一位永远无人知晓、几乎只能凭维米尔这个名字被辨认出来的艺术家，用那么多的学问和精细画了出来。",
         "就像那一小块黄墙，是一位永远无人知晓、几乎只能凭维米尔这个名字才辨认得出的艺术家，用那么多学问和精细画出来的。"),
        # ① 「而且这话还未必成立」指代悬空（et encore! ＝连「只对愚人不可见」也未必靠得住）
        ("而它们仅仅对愚人不可见——而且这话还未必成立。",
         "而它们仅仅对愚人不可见——而且连这一点也未必靠得住。"),
    ],
    "081": [
        # ① 「变成……的什么」悬空，quelqu'un qui ne peut plus répondre＝「再也不能回答问话的人」
        ("变成再也无法回答别人问话的什么，变成一个名字",
         "变成再也不能回答别人问话的人，变成一个名字"),
        # ① 句序倒装被照搬，末句「我当时重新感到了……」游离
        ("仿佛几行神秘的文字不合时宜地插了进来，我当时重新感到了它那种独特而触目的怪异。",
         "仿佛几行神秘的文字不合时宜地插了进来——我又一次感到了它那种独特而触目的怪异。"),
        # ①⑥ 「最最后」叠字失当；les tout à fait derniers temps＝最后那几年
        ("至少，只是到了最最后的时期才在这里",
         "至少，只是到了最后那几年才在这里"),
        # ④ 「离开他」的「他」可误认作布里肖，法语 lui＝车夫
        ("好有时间离开他。",
         "好有时间先离开车夫。"),
        # ⑥ devait venir me reprendre＝回头来接我，「接着我」词义走偏
        ("问我要不要他来接着我",
         "问我要不要他回头来接我"),
    ],
    # 107：全篇为拉丁文饮酒歌的中译，逐字核对后无硬伤，不作改动（见日志「未改判定」）
    "107": [],
}

REPORT = []


def han(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))


for key, edits in CHUNKS.items():
    d = os.path.join(BASE, "chunk" + key)
    path = os.path.join(d, "final.txt")
    bak = path + ".bak_20261125"
    text = open(path, encoding="utf-8", newline="").read()
    before_han = han(text)
    before_lines = text.count("\n")
    crlf = text.count("\r\n")

    if edits and not os.path.exists(bak):
        shutil.copy2(path, bak)

    for old, new in edits:
        assert old in text, (key, old)
        assert text.count(old) == 1, (key, "not unique", old)
        text = text.replace(old, new)

    if edits:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)

    after_han = han(text)
    after_lines = text.count("\n")
    assert before_lines == after_lines, (key, "line count changed")
    assert text.count("\r\n") == crlf, (key, "newline changed")
    assert "\n\n\n" not in text
    REPORT.append((key, len(edits), before_lines, after_lines,
                   before_han, after_han, crlf == after_lines))

print("chunk | 改动 | 行数前→后 | 汉字前→后 | 全CRLF")
for r in REPORT:
    print("%s | %d | %d→%d | %d→%d | %s" % r)

ast.parse(open(__file__, encoding="utf-8").read())