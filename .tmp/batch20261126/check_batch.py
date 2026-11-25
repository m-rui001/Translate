# -*- coding: utf-8 -*-
"""短篇批次机械体检：对每对 <key>_zh.json / 备份，检查
JSON 可解析、数组长度不变、无空段、无 ASCII 直引号、引号成对、
无重复标点、无拉丁残留、段末标点（诗行豁免）。
用法：python check_batch.py [key ...]   不给 key 则查全部有 bak 的篇目。
"""
import glob
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
STAMPS = ['_zh.json.bak_20261126', '_zh.json.bak_20261125']

DBL = re.compile(r'[，。；：、]{2}|[！？]{3,}')
LEAK = re.compile(r'[\u4e00-\u9fff] [a-z]{3,12} [\u4e00-\u9fff]')
END_OK = tuple('。！？…：”——）」』］】')
SEP = re.compile(r'^[\s＊*·…\u3000]+$')
NUM = re.compile(r'^[一二三四五六七八九十百]+$|^[IVXLC]+\.?$')


def check(key):
    z = os.path.join(BASE, key + '_zh.json')
    bak = None
    for st in STAMPS:
        if os.path.exists(z + st):
            bak = z + st
            break
    out = []
    if not os.path.exists(z):
        return ['%s: MISSING zh' % key], 0, 0
    try:
        d = json.load(open(z, encoding='utf-8'))
    except Exception as e:  # noqa: BLE001
        return ['%s: JSON BROKEN %s' % (key, e)], 0, 0
    n = len(d)
    han = sum(1 for p in d for ch in str(p) if '\u4e00' <= ch <= '\u9fff')
    if bak:
        b = json.load(open(bak, encoding='utf-8'))
        if len(b) != n:
            out.append('%s: LEN %d -> %d' % (key, len(b), n))
    for i, p in enumerate(d):
        p = str(p)
        if not p.strip():
            out.append('%s[%d]: EMPTY' % (key, i))
            continue
        if '"' in p:
            out.append('%s[%d]: ASCII-QUOTE' % (key, i))
        o, c = p.count('「'), p.count('」')
        if o != c:
            out.append('%s[%d]: QUOTE %d/%d' % (key, i, o, c))
        m = DBL.search(p)
        if m:
            out.append('%s[%d]: DBL-PUNCT %r' % (key, i, m.group(0)))
        m = LEAK.search(p)
        if m:
            out.append('%s[%d]: LATIN-LEAK %r' % (key, i, m.group(0)))
        if SEP.match(p) or NUM.match(p.strip()):
            continue
        if p.rstrip()[-1] not in END_OK and '\n' not in p.rstrip()[-1:]:
            out.append('%s[%d]: NO-END-PUNCT %r' % (key, i, p.rstrip()[-6:]))
    return out, n, han


def main(argv):
    keys = argv[1:]
    if not keys:
        keys = sorted(os.path.basename(p)[:-len('_zh.json')]
                      for p in glob.glob(os.path.join(BASE, '*_zh.json')))
    tot_n = tot_h = 0
    probs = 0
    for k in keys:
        msgs, n, han = check(k)
        tot_n += n
        tot_h += han
        if msgs:
            probs += 1
            print('[!!] %s' % k)
            for m in msgs[:12]:
                print('     ', m)
    print('checked %d, with problems %d, paras %d, han %d'
          % (len(keys), probs, tot_n, tot_h))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))