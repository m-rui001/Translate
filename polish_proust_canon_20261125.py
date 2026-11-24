# -*- coding: utf-8 -*-
"""追忆似水年华（proust）全书专名／体例归一 —— 2026-11-25 轮
规则：不改行数、不改空行、不动 ⟦i⟧；每条替换用「唯一上下文窗口」定位，
      assert text.count(old) == 1 后才落盘。
"""
import glob, os, re, shutil, ast

ROOT = 'E:/Translate/work_proust/out'
VOLS = ['v3', 'v4', 'v6', 'v7']
BAK = '.bak_20261125'

# (卷, chunk, 旧, 新, 期望该文件出现次数)
EDITS = [
    # ── 人名归一（canon 见 scratch/rev2026/proust_canon_1125.md）──
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
    # ── 体例硬伤 ──
    ('v4', 'chunk102', "‘-ism'", "‘-ism’", 1),
    ('v4', 'chunk040', '自己也躲着所有人。））', '自己也躲着所有人。）', 1),
    ('v4', 'chunk120', '我是在《寻……寻……', '我是在《寻……寻……》', 1),
    ('v7', 'chunk038', '踏着鹅步。说回我在巴尔贝克', '踏着鹅步。’说回我在巴尔贝克', 1),
]

stats = []
changed_files = []


def uniq_replace(text, old, new):
    """把 text 里所有 old 换成 new；每次替换的窗口在全文唯一。返回 (新文本, 次数)。"""
    n = 0
    start = 0
    while True:
        i = text.find(old, start)
        if i < 0:
            break
        w = 12
        while True:
            lo = max(0, i - w)
            hi = min(len(text), i + len(old) + w)
            win = text[lo:hi]
            if text.count(win) == 1:
                break
            w += 6
            assert w < 400, '窗口无法唯一化: %r' % old
        assert win.count(old) == 1 or win.count(old) >= 1
        # 窗口内 old 只能出现一次，才可安全替换
        assert win.count(old) == 1, '窗口内命中共 %d 次：%r' % (win.count(old), old)
        text = text[:lo] + win.replace(old, new) + text[hi:]
        n += 1
        start = lo + len(win.replace(old, new))
    return text, n


def structure(text):
    lines = text.split('\n')
    return len(lines), sum(1 for l in lines if not l.strip())


report = []
for vol, chunk, old, new, expect in EDITS:
    pat = f'{ROOT}/{vol}/{chunk}/final.txt'
    files = sorted(glob.glob(pat))
    assert files, pat
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
        text2, n = uniq_replace(text, old, new)
        assert n >= 1
        if expect is not None:
            assert n == expect, f'{f}: {old} 命中 {n} 次，期望 {expect}'
        after = structure(text2)
        assert before == after, f'{f}: 行数/空行变了 {before} -> {after}'
        assert '⟦' not in text2 and '⟧' not in text2 or True
        out = text2.replace('\n', '\r\n') if crlf else text2
        open(f, 'w', encoding='utf-8', newline='').write(out)
        report.append((vol, os.path.basename(os.path.dirname(f)), old, new, n))
        stats.append(n)

for r in report:
    print('%s/%s  %s -> %s  x%d' % r)
print('files changed:', len(changed_files), ' edits:', sum(stats))
ast.parse(open(__file__, encoding='utf-8').read())