# -*- coding: utf-8 -*-
"""定位唯一子串 -> 替换 -> 断言命中数的落盘工具（Proust 第二卷 out_ind 润色用）。"""
import os
import shutil

ROOT = 'work_proust/out_ind/v2'


def path(c):
    return os.path.join(ROOT, 'chunk%03d' % c, 'final.txt')


class Batch:
    def __init__(self, name):
        self.name = name
        self.files = {}
        self.n = 0
        self.log = []

    def _load(self, c):
        if c not in self.files:
            p = path(c)
            bak = p + '.bak_20261125'
            if not os.path.exists(bak):
                shutil.copy2(p, bak)
            self.files[c] = open(p, encoding='utf-8', newline='').read()
        return self.files[c]

    def rep(self, c, old, new, expect=1, tag=''):
        t = self._load(c)
        assert old in t, (c, 'MISS', old[:40])
        got = t.count(old)
        assert got == expect, (c, 'COUNT', got, expect, old[:40])
        self.files[c] = t.replace(old, new)
        self.n += got
        self.log.append((c, got, tag, old[:36], new[:36]))

    def flush(self):
        for c, t in sorted(self.files.items()):
            p = path(c)
            raw = open(p, encoding='utf-8', newline='').read()
            assert raw.count('\n') == t.count('\n'), (c, 'line count changed')
            assert '\r\n' in raw or '\r\n' not in t
            open(p, 'w', encoding='utf-8', newline='').write(t)
        return self.n


def check(c):
    """自检：段数、空段、引号、ASCII 引号、⟦⟧。"""
    t = open(path(c), encoding='utf-8', newline='').read()
    lines = t.split('\r\n')
    if lines and lines[-1] == '':
        lines = lines[:-1]
    bad = []
    if any(x.strip() == '' and x != '' for x in lines):
        bad.append('empty-line')
    if t.count('“') != t.count('”'):
        bad.append('quote%d/%d' % (t.count('“'), t.count('”')))
    if '"' in t or "'" in t:
        bad.append('ascii-quote')
    if '⟦' in t or '⟧' in t:
        bad.append('marker')
    return bad