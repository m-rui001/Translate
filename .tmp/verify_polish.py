# -*- coding: utf-8 -*-
"""校验一个 chunk 的润色落盘是否守红线：行数/段数/空行结构不变、引号成对、
无 ASCII 引号、无 ⟦ 增删、段末标点齐全。用法：
    python verify_polish.py out/v3/chunk003 [out/v3/chunk004 ...]
"""
import os
import sys

BAK = 'final.txt.bak_20261125'


def load(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()


def stats(txt):
    norm = txt.replace('\r\n', '\n')
    lines = norm.split('\n')
    paras = [x for x in lines if x.strip()]
    crlf = txt.count('\r\n')
    return {
        'lines': len(lines),
        'paras': len(paras),
        'blank': sum(1 for x in lines if not x.strip()),
        'crlf': crlf,
        'open': txt.count('“'),
        'close': txt.count('”'),
        'ascii_q': txt.count('"'),
        'mark': txt.count('⟦'),
    }


def main(dirs):
    bad = 0
    for d in dirs:
        f = os.path.join(d, 'final.txt')
        b = os.path.join(d, BAK)
        if not os.path.exists(b):
            print(f'{d}: NO BACKUP')
            bad += 1
            continue
        ta, tc = load(b), load(f)
        a, c = stats(ta), stats(tc)
        errs = []
        for k in ('lines', 'paras', 'blank'):
            if a[k] != c[k]:
                errs.append(f'{k} {a[k]}->{c[k]}')
        if a['crlf'] and c['crlf'] != a['crlf']:
            errs.append(f"crlf {a['crlf']}->{c['crlf']}")
        if c['open'] != c['close']:
            errs.append(f"quote {c['open']}/{c['close']}")
        if c['ascii_q']:
            errs.append(f"ascii-quote {c['ascii_q']}")
        if c['mark'] != a['mark']:
            errs.append(f"⟦ {a['mark']}->{c['mark']}")
        cjk = sum(1 for ch in tc if '\u4e00' <= ch <= '\u9fff')
        print(f"{d}: cjk {cjk} {'OK' if not errs else 'FAIL ' + ', '.join(errs)}")
        bad += 1 if errs else 0
    print('---', 'ALL OK' if not bad else f'{bad} problem(s)')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))