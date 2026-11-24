# -*- coding: utf-8 -*-
"""v3 chunk018-020 逐段润色（2026-11-26 轮）

准则：E:/Translate/POLISH_BRIEF_2026-11-25.md
canon：E:/Translate/scratch/rev2026/proust_canon_1125.md

落盘方式：只做「定位唯一子串 → 替换」，每处 assert text.count(old) == 1；
不整文件重写（读入全文 → 逐处 str.replace 唯一命中 → 原样写回，newline='' 保持 CRLF/LF）。
"""
import ast
import os

BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    "018": [
        # ③ 外语句法直搬 / ④ 指代：`ce que je demandais à leur opinion de me rendre, c'était…`
        (
            "我怀着发烧病人般的焦渴与乡愁，向她们对《费德尔》的意见所要求的，正是让它替我找回那种魅力",
            "我怀着发烧病人般的焦渴与乡愁，要求她们对《费德尔》的意见还给我的，正是那种魅力",
        ),
    ],
    "019": [
        # ⑥ 硬伤（误读）：`les avait fait entrer à son insu en conflagration` 的 les = mes regards
        (
            "她不过是转动眼睛想看看表妹在跟谁打招呼，却不知不觉让那双眼睛烧了起来；",
            "她不过是转动眼睛想看看表妹在跟谁打招呼，不知不觉间就把我的目光点燃了；",
        ),
        # ① 读不通：`à la première éclaircie`「放晴」的主语是天，不是「阳光」
        (
            "若是下过雨，第一缕阳光一放晴，我就下楼走几步",
            "若是下过雨，天一放晴，我就下楼走几步",
        ),
    ],
    "020": [
        # ⑥ 硬伤（漏译限定语）：`sa coiffure haute de cheveux blonds et légers` 的 légers
        (
            "她个子高挑，一头金发梳得很高",
            "她个子高挑，一头轻盈的金发梳得很高",
        ),
        # ① 读不通：同位语悬空（`dont le plumage épais…`）
        (
            "正如某些秃鹫，厚密、平滑、黄褐而柔软的羽毛，看上去像是一层皮毛。",
            "正如某些秃鹫，羽毛厚密、平滑、黄褐而柔软，看上去像是一层皮毛。",
        ),
    ],
}

CJK = lambda s: sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def audit(tag, text):
    body = text.replace("\r\n", "\n")
    paras = [p for p in body.split("\n\n") if p.strip()]
    lines = body.count("\n") + 1
    nl = "CRLF" if "\r\n" in text else "LF"
    print(
        "[%s] 行数=%d 段数=%d 汉字=%d 换行=%s 引号“%d/”%d ASCII\"=%d ⟦=%d"
        % (
            tag,
            lines,
            len(paras),
            CJK(text),
            nl,
            text.count("\u201c"),
            text.count("\u201d"),
            text.count('"'),
            text.count("\u27e6"),
        )
    )
    return lines, len(paras), CJK(text), nl


report = {}
for chunk, edits in EDITS.items():
    path = os.path.join(BASE, "chunk%s" % chunk, "final.txt")
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    before = audit(chunk + " 改前", text)
    n = 0
    for old, new in edits:
        assert old in text, "未命中：%s" % old
        assert text.count(old) == 1, "非唯一：%s" % old
        text = text.replace(old, new)
        n += 1
    after = audit(chunk + " 改后", text)
    assert before[0] == after[0], "行数变化 %s" % chunk
    assert before[1] == after[1], "段数变化 %s" % chunk
    assert before[3] == after[3], "换行符变化 %s" % chunk
    assert text.count("\u201c") == text.count("\u201d"), "引号不成对 %s" % chunk
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    report[chunk] = {"edits": n, "before": before, "after": after}
    print("  → 改动 %d 条\n" % n)

print("各 chunk 改动条数：", {k: v["edits"] for k, v in report.items()})
print("合计 %d 条" % sum(v["edits"] for v in report.values()))

ast.parse(open(__file__, encoding="utf-8").read())
print("ast.parse 自查通过")