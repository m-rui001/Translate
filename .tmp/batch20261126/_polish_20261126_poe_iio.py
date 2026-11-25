# -*- coding: utf-8 -*-
"""爱伦·坡三篇逐段润色（2026-11-26）：imp / island / owl。

改法：读 JSON → 对 d[i] 做「定位唯一子串 → 替换 → assert」→ 按原 indent/换行落盘。
落盘前先做「原样回写 == 原字节」的格式自检，确保 indent / CRLF / 末尾换行未被改动。
"""
import ast
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

# key -> (indent, newline, 末尾是否带换行)
FMT = {
    'imp':    (1, '\n', True),
    'island': (1, '\r\n', False),
    'owl':    (0, '\n', False),
}

# (key, 段号, 旧串, 新串, 类别, 理由, 英文原文)
EDITS = [
    # ---------------- island（题词段末标点） ----------------
    ('island', 0,
     '塞尔维乌斯。。',
     '塞尔维乌斯。',
     '⑦', '题词段末缺句末标点；本批体例（同 purloined、eleonora 题词）署名后带句号',
     'Nullus enim locus sine genio est.--Servius.'),

    # ---------------- imp: The Imp of the Perverse ----------------
    ('imp', 7,
     '为了给你指派一点东西',
     '为了给你举出一点东西',
     '⑥', '「指派」只能用于任务或人员（指派工作／指派代表），不能「指派一点东西」；原文 assign to you something 是「举出／提出」',
     'that I may assign to you something that shall have at least the faint aspect of a cause for my wearing these fetters'),
    ('imp', 12,
     '我十分、太十分明白',
     '我十分明白，太明白了',
     '①', '「太十分」不成词，副词叠加造成语法断裂；原文 well, too well understood 是「明白，太明白了」的复沓',
     'for, alas! I well, too well understood that to think, in my situation, was to be lost'),
    ('imp', 12,
     '这时我感到了我命运的完成。',
     '这时我感到自己的大限已到。',
     '③', 'consummation of my fate 照字面搬成「命运的完成」，中文不成话；实指命运走到终点、死期已至',
     'I felt then the consummation of my fate.'),
    ('imp', 13,
     '却带着显著的加重和炽热的急促',
     '却带着明显的加重语气和炽热的急促',
     '①', '「加重」单用作名词悬空（加重什么？）；marked emphasis 是「加重语气」',
     'but with marked emphasis and passionate hurry'),

    # ---------------- island: The Island of the Fay ----------------
    ('island', 1,
     '仿佛存心讥讽它那轻快戏谑的精神',
     '仿佛存心讥讽它本身的精神',
     '⑥', '原文只说「仿佛在讥讽这个书名的 spirit（本意）」，译者擅自添了「轻快戏谑」这层形容，属增义',
     "which in all our translations, we have insisted upon calling 'Moral Tales,' as if in mockery of their spirit"),
    ('island', 1,
     '而它与其他才能所共有的，仅仅是它会产生一些可以在独处中充分享受的效果。',
     '它产生一些可以在独处中充分享受的效果，这一点也不过与其他才能相同。',
     '③', 'And it is only in common with other talents that it produces effects... 被搬成「与其他才能所共有的仅仅是……」，「仅仅是」把「也不过相同」误读成「只有这一点」，逻辑反了',
     'And it is only in common with other talents that it produces effects which may be fully enjoyed in solitude.'),
    ('island', 2,
     '星辰运行的那些个周期',
     '星辰运行所循的那些周期',
     '⑦', '「那些个」是口语填充词，与全篇庄重的论说体不合；改后仍保留原文的指示语气',
     'The cycles in which the stars move'),
    ('island', 2,
     '这并不构成反对体积为上帝所关注的一个理由',
     '这并不足以反驳体积乃是上帝所看重之物',
     '③', 'argument against X being Y 的介词串照搬成「反对……为……的理由」，中文读不通；改为动词句',
     'Nor is it any argument against bulk being an object with God, that space itself is infinite'),
    ('island', 2,
     '即神体旋转',
     '即神格旋转',
     '⑤', 'Godhead 是「神格／神性本体」，不是「神体」（后者易读作神像、神的身躯）；全篇基督教语境取通行译法',
     'all revolving around one far-distant centre which is the God-head'),
    ('island', 5,
     '那条小河在途中猛一转折，随即立刻看不见了',
     '那条小河在途中猛一转折，于是立刻看不见了',
     '⑦', '「随即」「立刻」同义叠用，属冗余；原文只是一个 immediately',
     'The little river which turned sharply in its course, and was thus immediately lost to sight'),
    ('island', 6,
     '静卧在流水的心口上',
     '静卧在流水的怀抱里',
     '⑥', 'bosom 在此是「怀抱、胸腹」，译作「心口」把位置读错（心口指胸口正中，且与「静卧」不搭）',
     'reposed upon the bosom of the stream'),
    ('island', 13,
     '少了那弹性的欢欣',
     '少了那轻快的欢欣',
     '③', 'elastic joy 直搬「弹性的欢欣」不成词；elastic 在此是「轻快、有弹跳感」的形容',
     'there was more of care and uncertainty and less of elastic joy'),

    # ---------------- owl: An Occurrence at Owl Creek Bridge ----------------
    ('owl', 3,
     '一片漂来荡去的浮木引住了他的注意',
     '一片漂来荡去的浮木吸引了他的注意',
     '⑥', '「引住」不是词（只有「引住目光」勉强可说），此处应作「吸引」',
     'A piece of dancing driftwood caught his attention'),
    ('owl', 8,
     '天生是个原始的分离派',
     '天生就是个分离派',
     '⑥', 'original secessionist 的 original 是「从一开始、骨子里的」，不是「原始的」（野蛮、未开化），词义误读',
     'he was naturally an original secessionist and ardently devoted to the Southern cause'),
    ('owl', 24,
     '预先给出、又强行带来一片静默',
     '预示凶兆、又强使兵士们安静下来',
     '⑥', 'presaging 是「预示（凶兆）」，不是「预先给出」；tranquility in the men 是兵士心里的镇定，不是场面上的「静默」',
     'with what an even, calm intonation, presaging, and enforcing tranquility in the men'),
    ('owl', 28,
     '这个被猎的人从肩上回头看着这一切',
     '这个被追猎的人从肩上回头看着这一切',
     '①', '「被猎的人」缺及物对象、读来悬空；the hunted man 是「被追猎的人」',
     'The hunted man saw all this over his shoulder'),
    ('owl', 34,
     '靠着太阳转圆来定方向',
     '靠着太阳的运转来定方向',
     '①', '「太阳转圆」是生造搭配；the rounding sun 指太阳的运行（绕行一周）',
     'laying his course by the rounding sun'),
]


def render(d, indent, nl, trailing):
    s = json.dumps(d, ensure_ascii=False, indent=indent)
    if nl != '\n':
        s = s.replace('\n', nl)
    if trailing:
        s += nl
    return s.encode('utf-8')


def han(t):
    return sum(1 for ch in t if '\u4e00' <= ch <= '\u9fff')


def check(key, d, zhpath):
    errs = []
    if any(not str(x).strip() for x in d):
        errs.append('有空段')
    for i, t in enumerate(d):
        if '"' in t:
            errs.append('[%d] ASCII 直引号' % i)
        if re.search(r'[。，、；：]{2,}', t):
            errs.append('[%d] 重复标点' % i)
        for m in re.finditer(r'[\u4e00-\u9fff] +[a-z]+ +[\u4e00-\u9fff]', t):
            errs.append('[%d] 残留英文: %s' % (i, m.group(0)))
        if '⟦' in t or '⟧' in t:
            errs.append('[%d] 斜体标记' % i)
    b = json.load(open(zhpath + '.bak_20261126', encoding='utf-8'))
    if len(b) != len(d):
        errs.append('段数变了 %d -> %d' % (len(b), len(d)))
    return errs


def main():
    by_key = {}
    for e in EDITS:
        by_key.setdefault(e[0], []).append(e)

    total = 0
    report = []
    for key in ['imp', 'island', 'owl']:
        zhpath = os.path.join(BASE, '%s_zh.json' % key)
        indent, nl, trailing = FMT[key]
        raw = open(zhpath, 'rb').read()
        d = json.loads(raw.decode('utf-8'))

        # 格式自检：原样回写必须与原字节完全一致
        assert render(d, indent, nl, trailing) == raw, '%s 回写格式与原文件不一致' % key

        n = 0
        for _, i, old, new, cat, why, en in by_key.get(key, []):
            # 幂等：重跑时旧串已不在（前次已落盘）则跳过
            if old not in d[i]:
                assert new in d[i], '%s[%d] 旧串新串均未命中: %s' % (key, i, old)
                continue
            assert old in d[i], '%s[%d] 未命中: %s' % (key, i, old)
            assert d[i].count(old) == 1, '%s[%d] 命中不唯一: %s' % (key, i, old)
            d[i] = d[i].replace(old, new)
            n += 1
        # n 允许小于 len(...)：重跑时前次改动已存在

        open(zhpath, 'wb').write(render(d, indent, nl, trailing))

        errs = check(key, d, zhpath)
        bak = json.load(open(zhpath + '.bak_20261126', encoding='utf-8'))
        report.append((key, len(d), len(bak), sum(han(x) for x in d), n, errs))
        total += n
        print('%s: 段数 %d（备份 %d）汉字 %d 改动 %d 条 自检 %s'
              % (key, len(d), len(bak), sum(han(x) for x in d), n,
                 'OK' if not errs else '; '.join(errs)))

    print('合计改动 %d 条（imp %d / island %d / owl %d）'
          % (total, len(by_key['imp']), len(by_key['island']), len(by_key['owl'])))
    return 0 if all(not r[5] for r in report) else 1


if __name__ == '__main__':
    sys.exit(main())

ast.parse(open(__file__, encoding='utf-8').read())