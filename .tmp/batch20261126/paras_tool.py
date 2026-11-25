# -*- coding: utf-8 -*-
"""work_batch_20261124 短篇逐段润色工具。

一对文件：
    源：`_<key>_paras.json`（英文原段落，含篇名 [0]）
    译：`<key>_zh.json`（中文段落，**不含篇名**，故 zh[i] ↔ src[i+1]）
用法：
    python paras_tool.py list                 # 全部篇目：段数/汉字/是否已润
    python paras_tool.py list --todo          # 只列没润过的
    python paras_tool.py show <key>           # 逐段对照
    python paras_tool.py backup <key>         # 建 <key>_zh.json.bak_20261126
"""
import glob
import json
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
STAMP = '_zh.json.bak_20261126'


def pairs():
    out = []
    for zh in sorted(glob.glob(os.path.join(BASE, '*_zh.json'))):
        key = os.path.basename(zh)[:-len('_zh.json')]
        src = os.path.join(BASE, '_%s_paras.json' % key)
        if not os.path.exists(src):
            continue
        out.append((key, src, zh))
    return out


def cjk(s):
    return sum(1 for ch in str(s) if '\u4e00' <= ch <= '\u9fff')


def list_pairs(only_todo=False):
    tot_c = tot_p = 0
    n_todo = 0
    for key, src, zh in pairs():
        d = json.load(open(zh, encoding='utf-8'))
        s = json.load(open(src, encoding='utf-8'))
        done = os.path.exists(os.path.join(BASE, key + STAMP))
        h = sum(cjk(x) for x in d)
        tot_c += h
        tot_p += len(d)
        n_todo += 0 if done else 1
        if only_todo and done:
            continue
        flag = 'done' if done else 'TODO'
        warn = '' if len(d) in (len(s), len(s) - 1) else '  <-- 段数差 %+d' % (len(d) - len(s))
        print('%s\t%s\tzh=%d src=%d  han=%d%s' % (flag, key, len(d), len(s), h, warn))
    print('-- pairs=%d todo=%d  han=%d paras=%d' % (len(pairs()), n_todo, tot_c, tot_p))


def show(key):
    src = os.path.join(BASE, '_%s_paras.json' % key)
    zh = os.path.join(BASE, '%s_zh.json' % key)
    s = json.load(open(src, encoding='utf-8'))
    d = json.load(open(zh, encoding='utf-8'))
    off = len(s) - len(d)
    print('%s: src=%d zh=%d offset=%d' % (key, len(s), len(d), off))
    for i in range(len(d)):
        j = i + off
        print('\n--- [%d] 源 ---\n%s\n--- [%d] 译 ---\n%s'
              % (j, s[j] if j < len(s) else '(无)', i, d[i]))
    return 0


def backup(key):
    zh = os.path.join(BASE, '%s_zh.json' % key)
    b = zh + '.bak_20261126'
    if os.path.exists(b):
        print('backup exists, not overwritten:', b)
    else:
        shutil.copy2(zh, b)
        print('backup made:', b)
    return 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    if argv[1] == 'list':
        list_pairs('--todo' in argv)
        return 0
    if argv[1] == 'show':
        return show(argv[2])
    if argv[1] == 'backup':
        return backup(argv[2])
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))