# -*- coding: utf-8 -*-
"""普鲁斯特全书逐段体检：扫描 7 卷所有 final.txt。
报出：ASCII 引号、半角标点、汉字间空格、重复标点、落单引号段、
      工具标记残留、拉丁字母夹在汉字之间。"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
VOLS = [('v3', 'out/v3'), ('v4', 'out/v4'), ('v6', 'out/v6'), ('v7', 'out/v7'),
        ('v1', 'out_ind/v1'), ('v2', 'out_ind/v2'), ('v5', 'out_ind/v5')]

PATS = [
    ('ascii_quote', re.compile(r'"')),
    ('halfwidth', re.compile(r'[,.?!;:]')),
    ('cjk_space', re.compile(r'[\u4e00-\u9fff] [\u4e00-\u9fff]')),
    ('dbl_punct', re.compile(r'[，。；：、]{2}|[！？]{2,}(?![”])')),
    ('tool_mark', re.compile(r'```|oldText|newText|⟦/?i⟧{2}')),
    ('latin_leak', re.compile(r'[\u4e00-\u9fff] [a-z]{3,12} [\u4e00-\u9fff]')),
]


def main():
    report = {k: [] for k, _ in PATS}
    qodd = []
    files = 0
    paras = 0
    cjk = 0
    for vol, rel in VOLS:
        d = os.path.join(ROOT, rel)
        for c in sorted(os.listdir(d)):
            if not c.startswith('chunk'):
                continue
            f = os.path.join(d, c, 'final.txt')
            if not os.path.exists(f):
                continue
            files += 1
            with open(f, encoding='utf-8', newline='') as fh:
                txt = fh.read()
            for line in txt.replace('\r\n', '\n').split('\n'):
                if not line.strip():
                    continue
                paras += 1
                cjk += sum(1 for ch in line if '\u4e00' <= ch <= '\u9fff')
                for k, p in PATS:
                    m = p.search(line)
                    if m:
                        report[k].append((vol, c, m.group(0), line[:40]))
                o, cl = line.count('“'), line.count('”')
                if o != cl:
                    qodd.append((vol, c, o, cl, line[:40]))
    print(f'files {files}  paras {paras}  han {cjk:,}')
    for k, _ in PATS:
        v = report[k]
        print(f'{k}: {len(v)}')
        for item in v[:8]:
            print('   ', item)
    print(f'quote-odd paragraphs: {len(qodd)}')
    for item in qodd[:20]:
        print('   ', item)
    return 0


if __name__ == '__main__':
    sys.exit(main())