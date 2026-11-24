# -*- coding: utf-8 -*-
"""《魔戒》诗行类型对齐：把与 verse 同处一「短行块」的段落一并为 verse。

现象：诗被逐行拆成段落，types 只标了诗的第一行，其余行留作 p，排出来一首诗里
几行居中、几行像正文。规则：
  * 只有「短行（<=40 字）且不以引号起头」的段落参与成块；
  * 已标 verse 的段落不论长短都算块内成员（诗里也可能有引号行）；
  * 块内只要有一个 verse，整块标 verse。
"""
import ast
import glob
import json
import os
import shutil

LIMIT = 40


def main():
    files = 0
    flipped = 0
    for path in sorted(glob.glob('work_overhaul/lotr/final/book*c*.json')):
        if '.bak_' in path or '.polished' in path:
            continue
        d = json.load(open(path, encoding='utf-8'))
        texts = d.get('texts') or []
        types = list(d.get('types') or ['p'] * len(texts))
        if len(types) != len(texts):
            types = (types + ['p'] * len(texts))[:len(texts)]
        before = list(types)
        n = len(texts)

        def member(i):
            if types[i] == 'verse':
                return True
            return len(texts[i]) <= LIMIT and not texts[i].strip().startswith('“')

        i = 0
        while i < n:
            if not member(i):
                i += 1
                continue
            j = i
            while j < n and member(j):
                j += 1
            if any(types[k] == 'verse' for k in range(i, j)):
                for k in range(i, j):
                    if types[k] != 'verse':
                        types[k] = 'verse'
                        flipped += 1
            i = j

        if types != before:
            bak = path + '.bak_20261125'
            if not os.path.exists(bak):
                shutil.copy2(path, bak)
            d['types'] = types
            with open(path, 'w', encoding='utf-8') as fh:
                json.dump(d, fh, ensure_ascii=False, indent=1)
            files += 1
    print('files changed', files, 'paragraphs flipped', flipped)
    ast.parse(open(__file__, encoding='utf-8').read())


if __name__ == '__main__':
    main()
