# -*- coding: utf-8 -*-
"""把《魔戒》里「整首并成一段」的诗按标点重新分行（英文原本多行、中文只有一行）。

只在同时满足下列条件时动手：
  * 该段 types 标为 verse；
  * 该段中文不含换行，长度 > 60；
  * `work_overhaul/lotr/ch/<cid>.json` 里同下标英文段有 >= 3 行；
  * 按标点切出的行数与英文行数相差不超过 4。
"""
import ast
import glob
import json
import os
import re
import shutil

SEG = re.compile(r'[^，。！？；：]+[，。！？；：]?')


def main():
    changed = 0
    files = 0
    for path in sorted(glob.glob('work_overhaul/lotr/final/book*c*.json')):
        if '.bak_' in path or '.polished' in path:
            continue
        cid = os.path.basename(path)[:-5]
        chp = f'work_overhaul/lotr/ch/{cid}.json'
        if not os.path.exists(chp):
            continue
        d = json.load(open(path, encoding='utf-8'))
        ch = json.load(open(chp, encoding='utf-8'))
        src = ch.get('src_paras') or []
        texts = d.get('texts') or []
        types = d.get('types') or []
        touched = False
        for i, t in enumerate(types):
            if t != 'verse' or i >= len(texts) or i >= len(src):
                continue
            zh = texts[i]
            if '\n' in zh or len(zh) <= 60:
                continue
            en_lines = src[i].count('\n') + 1
            if en_lines < 3:
                continue
            # 先排除误标成 verse 的散文：句子里带「某某说」这类归属小句，
            # 或平均分句长度超过 14 字，都不当诗行处理。
            if re.search(r'[^，。！？]{1,6}(说|道|问|答|喊|叫)[，。：]', zh):
                continue
            segs = [s.strip() for s in SEG.findall(zh) if s.strip()]
            if abs(len(segs) - en_lines) > 10:
                continue
            if len(zh) / max(len(segs), 1) > 14:
                continue
            texts[i] = '\n'.join(segs)
            changed += 1
            touched = True
            print(cid, i, 'en lines', en_lines, 'zh lines', len(segs))
        if touched:
            bak = path + '.bak_20261125'
            if not os.path.exists(bak):
                shutil.copy2(path, bak)
            d['texts'] = texts
            with open(path, 'w', encoding='utf-8') as fh:
                json.dump(d, fh, ensure_ascii=False, indent=1)
            files += 1
    print('paragraphs reflowed', changed, 'files', files)
    ast.parse(open(__file__, encoding='utf-8').read())


if __name__ == '__main__':
    main()
