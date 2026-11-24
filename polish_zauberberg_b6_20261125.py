# -*- coding: utf-8 -*-
"""《魔山》batch6：西文撇号统一为 ’（全册其余处已用 ’），清掉 ASCII 单引号。"""
import io, os, ast

files = {
    'E:/Translate/work_zauberberg/out/index_split_001/c03/final.txt': [
        ("Possible que j'ai eu tant d'esprit？", "Possible que j’ai eu tant d’esprit？"),
    ],
    'E:/Translate/work_zauberberg/out/index_split_013/c04/final.txt': [
        ("Fort possible qu'il aille mourir", "Fort possible qu’il aille mourir"),
    ],
}
for path, pairs in files.items():
    with io.open(path, 'r', encoding='utf-8-sig', newline='') as f:
        text = f.read()
    bak = path + '.bak_20261125'
    if not os.path.exists(bak):
        with io.open(bak, 'w', encoding='utf-8-sig', newline='') as f:
            f.write(text)
    for old, new in pairs:
        assert text.count(old) == 1, (path, old, text.count(old))
        text = text.replace(old, new)
    with io.open(path, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(text)
    print('patched', os.path.basename(os.path.dirname(path)))
ast.parse(open(__file__, encoding='utf-8').read())
print('OK')
