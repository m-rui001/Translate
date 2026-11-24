# -*- coding: utf-8 -*-
"""追忆似水年华（proust）全书专名／体例归一 · 第二遍（修正窗口内多命中的处理）
规则：不改行数、不改空行、不动 ⟦i⟧；定位唯一上下文窗口，逐处替换。
"""
import glob, os, shutil, ast

ROOT = 'E:/Translate/work_proust/out'
BAK = '.bak_20261125'

EDITS = [
    ('v3', '*', '圣艾弗特', '圣厄韦尔特', None),
    ('v7', '*', '圣艾弗特', '圣厄韦尔特', None),
    ('v7', '*', '圣欧韦特', '圣厄韦尔特', None),
    ('v3', '*', '玛桑特', '马桑特', None),
    ('v7', '*', '玛桑特', '马桑特', None),
    ('v7', '*', '福瓦', '富瓦', None),
    ('v3', '*', '阿尔帕荣', '阿尔帕戎', None),
    ('v4', '*', '阿尔帕荣', '阿尔帕戎', None),
    ('v7', '*', '阿尔帕荣', '阿尔帕戎', None),
    ('v6', '*', '埃波切维尔', '埃波舍维尔', None),
    ('v3', '*', '昂布雷萨克', '昂布勒萨克', None),
    ('v3', '*', '加拉东', '加朗东', None),
    ('v4', '*', '加拉东', '加朗东', None),
    ('v4', '*', '加尔朗', '加朗东', None),
    ('v3', '*', '夏特勒罗', '沙泰勒罗', None),
    ('v7', '*', '库尔瓦济耶', '库尔瓦西耶', None),
    ('v3', '*', '拉格拉维埃尔', '拉格拉维埃', None),
    ('v7', '*', '德·阿让库尔', '达尔让库尔', None),
    ('v3', '*', '东西埃尔', '当西埃尔', None),
    ('v4', 'chunk102', "‘-ism'", "‘-ism’", 1),
    ('v4', 'chunk040', '自己也躲着所有人。））', '自己也躲着所有人。）', 1),
    ('v4', 'chunk120', '我是在《寻……寻……', '我是在《寻……寻……》', 1),
    ('v7', 'chunk038', '踏着鹅步。说回我在巴尔贝克', '踏着鹅步。’说回我在巴尔贝克', 1),
]

changed_files = []
report = []


def uniq_positions(text, old):
    """返回 (位置列表)，要求每一处的上下文窗口在全文唯一。"""
    out = []
    start = 0
    while True:
        i = text.find(old, start)
        if i < 0:
            return out
        w = 12
        while True:
            lo, hi = max(0, i - w), min(len(text), i + len(old) + w)
            win = text[lo:hi]
            if text.count(win) == 1:
                break
            w += 6
            assert w < 400, '窗口无法唯一化: %r' % old
        out.append(lo + (i - lo))
        start = i + len(old)


def structure(text):
    lines = text.split('\n')
    return len(lines), sum(1 for l in lines if not l.strip())


for vol, chunk, old, new, expect in EDITS:
    files = sorted(glob.glob(f'{ROOT}/{vol}/{chunk}/final.txt'))
    assert files, (vol, chunk)
    for f in files:
        raw = open(f, encoding='utf-8', newline='').read()
        if old not in raw:
            continue
        crlf = '\r\n' in raw
        text = raw.replace('\r\n', '\n') if crlf else raw
        before = structure(text)
        if f not in changed_files:
            bak = f + BAK
            if not os.path.exists(bak):
                shutil.copy2(f, bak)
            changed_files.append(f)
        # 计算全部命中位置（基于原文本），自后向前替换，避免位移
        idxs = []
        start = 0
        while True:
            i = text.find(old, start)
            if i < 0:
                break
            idxs.append(i)
            start = i + len(old)
        n = len(idxs)
        if expect is not None:
            assert n == expect, f'{f}: {old} 命中 {n} 次，期望 {expect}'
        # 逐处校验唯一窗口
        for i in idxs:
            w = 12
            while True:
                lo, hi = max(0, i - w), min(len(text), i + len(old) + w)
                win = text[lo:hi]
                if text.count(win) == 1:
                    break
                w += 6
                assert w < 400
        for i in reversed(idxs):
            text = text[:i] + new + text[i + len(old):]
        after = structure(text)
        assert before == after, f'{f}: 行数/空行变了 {before} -> {after}'
        out = text.replace('\n', '\r\n') if crlf else text
        open(f, 'w', encoding='utf-8', newline='').write(out)
        report.append((vol, os.path.basename(os.path.dirname(f)), old, new, n))

for r in report:
    print('%s/%s  %s -> %s  x%d' % r)
print('files changed:', len(changed_files), ' edits:', sum(r[4] for r in report))
ast.parse(open(__file__, encoding='utf-8').read())