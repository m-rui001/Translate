# -*- coding: utf-8 -*-
"""《魔山》batch7：清掉 final.txt 的 UTF-8 BOM（assembly 用 encoding='utf-8' 读取，
BOM 会作为 U+FEFF 混进首段）。只去 BOM，不碰正文与换行符。"""
import io, os, glob, ast

files = sorted(glob.glob('E:/Translate/work_zauberberg/out/index_split_*/c*/final.txt'))
n = 0
for path in files:
    raw = open(path, 'rb').read()
    if raw.startswith(b'\xef\xbb\xbf'):
        body = raw[3:]
        # 备份（保持原样，含 BOM）
        bak = path + '.bak_20261125'
        if not os.path.exists(bak):
            open(bak, 'wb').write(raw)
        open(path, 'wb').write(body)
        n += 1
print('bom stripped', n, 'of', len(files))
ast.parse(open(__file__, encoding='utf-8').read())
print('OK')
