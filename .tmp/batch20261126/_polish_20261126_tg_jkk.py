# -*- coding: utf-8 -*-
"""逐段润色 tg_jest / tg_kai / tg_king（2026-11-26 批）。

铁律：只改 d[i] 的元素值，数组长度与顺序不变；定位唯一子串 → 断言命中 → 替换。
"""
import ast
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

# 每篇：(段号, 旧串, 新串, 类别标记)
EDITS = {
    "tg_jest": [
        (0,
         "放进对别家君王所不贪的疆土的贪欲",
         "放进对疆土的贪欲，比别家君王更甚",
         "⑥ 否定反转：beyond the lust of other kings 是“超出别家君王所欲求”，"
         "旧译“所不贪”把意思读反；顺带解掉三层“的”"),
        (1,
         "他们的怒气渐渐消散，把眼睛转开了",
         "他们的怒气渐渐消散，诸神把眼睛转开了",
         "④ 指代：They averted Their eyes 的主语是诸神，旧译紧接“怒气”，"
         "易读成魂灵转眼"),
    ],
    "tg_kai": [
        (3,
         "于是各级魔法师都聚到伊劳恩来，直到第七级，那些曾在「独居的哈纳扎」朝上施过咒的；",
         "于是各级魔法师——直到第七级——都聚到伊劳恩来，他们都是曾在「独居的哈纳扎」朝上施过咒的；",
         "① 读不通：even to the seventh 是插说，旧译“直到第七级”悬空，"
         "后半句“那些……的”也无着落"),
        (19,
         "派出骑手去告诫平原上的居民",
         "派出骑手去告知平原上的居民",
         "⑥ 词义：warn 此处只是预先通报，非“告诫”（训诫）"),
        (21,
         "哈纳扎王和他跟随西拉恩的两支军队前行",
         "哈纳扎王和他那两支跟随西拉恩的军队一路前行",
         "① 读不通：his two armies who followed Syrahn 的关系从句被倒装后"
         "成了“他跟随西拉恩的军队”，主谓反了"),
        (21,
         "张起紫底金边的帐篷",
         "张起紫色镶金边的帐篷",
         "⑥ 词义：with golden border 是镶金边，不是“紫底”"),
        (23,
         "「那边看我的礼物。",
         "「看那边，那是我的礼物。",
         "① 读不通：Yonder behold my gifts 的 yonder 是指示，旧译“那边看”缺动词感"),
        (31,
         "还我一粒粘在那个时辰上的尘土，就在你洞中那一堆里的。",
         "还我一粒粘在那个时辰上的尘土——那尘土就在你洞中那一堆里。",
         "① 读不通：in the heap that lies within thy cave 的定语倒挂成了句末悬空成分"),
        (39,
         "琴弦上像沾着尘土似的，粘着几个从被遗忘的时辰里来的秒，和过去的日子里的一些小事。",
         "琴弦上像沾了尘土，粘着几个零碎的秒——那是从被遗忘的时辰里来的——还有些过去日子里的小事。",
         "① 读不通＋② 的字堆叠：some seconds out of the forgotten hours 直搬成"
         "“从……里来的秒”，四个“的”串死"),
        (40,
         "琴师见哈纳扎看他并不恼怒，",
         "琴师见哈纳扎并不恼怒地看着他，",
         "① 读不通：looked not angrily upon him 旧译语序颠倒，读成“看他并不恼怒”"),
        (47,
         "你就去守着我的大明天；",
         "你就去守着我的伟大的明天；",
         "① 读不通：great to-morrow 作“大明天”与“明朝”同形，易误读"),
        (49,
         "「我愿守着你的大明天；",
         "「我愿守着你的伟大的明天；",
         "① 同上，与前段口径统一"),
    ],
    "tg_king": [
        (1,
         "又把云披在身上，摆出最神异的姿态",
         "又把云披在身上，摆出他们最神圣的气度",
         "⑥ 词义：Their divinest air 是“最神圣的气度”，“神异／姿态”皆偏"),
        (6,
         "于是传令官被派往鲁纳扎各城",
         "于是国王派传令官前往鲁纳扎各城",
         "③ 被动式硬搬：heralds were sent abroad 旧译“被派往”，主语虚悬"),
    ],
}


def detect_style(path):
    with open(path, "rb") as f:
        raw = f.read()
    crlf = b"\r\n" in raw
    head = raw.split(b"\n", 1)[0]
    # indent = 第二行行首空格数
    lines = raw.split(b"\r\n" if crlf else b"\n")
    ind = 0
    if len(lines) > 1:
        ind = len(lines[1]) - len(lines[1].lstrip(b" "))
    return crlf, ind


def main():
    total = 0
    for key, edits in EDITS.items():
        path = os.path.join(BASE, key + "_zh.json")
        bak = path + ".bak_20261126"
        crlf, ind = detect_style(path)
        with open(path, encoding="utf-8", newline="") as f:
            d = json.load(f)
        dbak = json.load(open(bak, encoding="utf-8"))
        n0 = len(d)
        applied = 0
        for idx, old, new, why in edits:
            t = d[idx]
            assert old in t, (key, idx, old[:30])
            assert t.count(old) == 1, (key, idx, "non-unique", old[:30])
            d[idx] = t.replace(old, new)
            applied += 1
        # 落盘
        with open(path, "w", encoding="utf-8", newline="") as f:
            json.dump(d, f, ensure_ascii=False, indent=ind)
            if crlf:
                pass  # json.dump 用 \n，下面统一转换
        if crlf:
            with open(path, encoding="utf-8", newline="") as f:
                txt = f.read()
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(txt.replace("\r\n", "\n").replace("\n", "\r\n"))
        # 自检
        with open(path, encoding="utf-8", newline="") as f:
            chk = json.load(f)
        assert len(chk) == n0 == len(dbak), (key, "长度校验失败")
        for i, p in enumerate(chk):
            assert p.strip(), (key, i, "空段")
            assert '"' not in p, (key, i, "ASCII 直引号")
            for bad in ("。。", "，，", "；；", "、、", "——　"):
                assert bad not in p, (key, i, bad)
        han = sum(1 for p in chk for c in p if "\u4e00" <= c <= "\u9fff")
        print("%-8s 段数=%d(改前=%d) 改动=%d 汉字=%d 换行=%s indent=%d"
              % (key, len(chk), len(dbak), applied, han,
                 "CRLF" if crlf else "LF", ind))
        total += applied
    print("合计改动 %d 条" % total)


main()
ast.parse(open(__file__, encoding="utf-8").read())