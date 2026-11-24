# -*- coding: utf-8 -*-
"""work_pub 分册「小片」读写工具。

一块（piece）＝ `out/<chapter>/<piece>/final.txt`，对应 `chunks/<chapter>.json`
里 `chunks[k]` 那一组源段（k 为该目录的序号）。中文一段一行、段间空行。

用法：
    python piece_tool.py list   <book>                  # 列出还没润过的片
    python piece_tool.py show   <book> <chapter> <piece>  # 打印德/英原文与中文对照
    python piece_tool.py backup <book> <chapter> <piece>  # 建 final.txt.bak_20261126
"""
import glob
import json
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
STAMP = 'final.txt.bak_20261126'


def _paths(book):
    return os.path.join(BASE, book, 'chunks'), os.path.join(BASE, book, 'out')


def list_pieces(book):
    _, out = _paths(book)
    rows = []
    for ch in sorted(glob.glob(os.path.join(out, 'c*'))):
        if not os.path.isdir(ch):
            continue
        for p in sorted(glob.glob(os.path.join(ch, 'c*'))):
            f = os.path.join(p, 'final.txt')
            if not os.path.exists(f):
                continue
            done = bool(glob.glob(os.path.join(p, 'final.txt.bak_*')))
            rows.append((os.path.basename(ch), os.path.basename(p), done, f))
    return rows


def show(book, chapter, piece):
    chunk_dir, out = _paths(book)
    src = json.load(open(os.path.join(chunk_dir, chapter + '.json'), encoding='utf-8'))
    blocks = src['chunks']
    idx = int(piece.lstrip('c'))
    block = blocks[idx]
    f = os.path.join(out, chapter, piece, 'final.txt')
    with open(f, encoding='utf-8', newline='') as fh:
        zh = [x for x in fh.read().replace('\r\n', '\n').split('\n') if x.strip()]
    src_ps = [x['text'] for x in block if x.get('type') == 'p']
    print(f'{book}/{chapter}/{piece}: src_p={len(src_ps)} zh_p={len(zh)}')
    n = max(len(src_ps), len(zh))
    for i in range(n):
        s = src_ps[i] if i < len(src_ps) else '(无)'
        z = zh[i] if i < len(zh) else '(无)'
        print(f'\n--- [{i}] 源 ---\n{s}\n--- [{i}] 译 ---\n{z}')
    return 0


def backup(book, chapter, piece):
    _, out = _paths(book)
    d = os.path.join(out, chapter, piece)
    f = os.path.join(d, 'final.txt')
    b = os.path.join(d, STAMP)
    if os.path.exists(b):
        print('backup exists, not overwritten:', b)
    else:
        shutil.copy2(f, b)
        print('backup made:', b)
    return 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == 'list':
        rows = list_pieces(argv[2])
        todo = [r for r in rows if not r[2]]
        for ch, p, done, _ in rows:
            print(f'{ch}/{p} {"done" if done else "TODO"}')
        print(f'-- {len(rows) - len(todo)}/{len(rows)} done, {len(todo)} left')
        return 0
    if cmd == 'show':
        return show(argv[2], argv[3], argv[4])
    if cmd == 'backup':
        return backup(argv[2], argv[3], argv[4])
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))