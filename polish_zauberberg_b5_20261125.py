# -*- coding: utf-8 -*-
"""《魔山》batch5：补出原文自带的西文夹注（dos banderas = 两面旗帜），免中文读者失据。"""
import io, os, ast

path = 'E:/Translate/work_zauberberg/out/index_split_014/c12/final.txt'
with io.open(path, 'r', encoding='utf-8-sig', newline='') as f:
    text = f.read()
bak = path + '.bak_20261125'
if not os.path.exists(bak):
    with io.open(bak, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(text)
old = '在 dos banderas 之下汇成一场混乱的厮杀'
new = '在“dos banderas”——“两面旗帜”——之下汇成一场混乱的厮杀'
assert text.count(old) == 1
text = text.replace(old, new)
with io.open(path, 'w', encoding='utf-8-sig', newline='') as f:
    f.write(text)
print('patched 1')
ast.parse(open(__file__, encoding='utf-8').read())
print('OK')
