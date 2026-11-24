# -*- coding: utf-8 -*-
"""《追忆似水年华》第一卷 chunk036-040 通读润色 p2f（2026-11-25 轮）

只做「定位唯一子串 -> 替换 -> 断言命中数」的改法，不整文件重写。
行数/段数不变；已有 .bak_20261125 的不覆写。
"""
import io
import os
import shutil

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    'work_proust', 'out_ind', 'v1')

# (chunk, old, new, 类别, 理由)
EDITS = [
    # ---- chunk036 ----
    ('chunk036', '书脊上那些小册子和分册被绳子勒着，排在两扇门板上',
     '那些小册子和分册被绳子勒着，铺满两扇门板', '⑥',
     '«retenu par des ficelles dans la mosaïque des brochures et des livraisons qui revêtaient les deux vantaux de sa porte»：revêtaient 是「铺满」，书中物被绳子勒在那片铺满门板的书册当中；「书脊上……排在门板上」把位置和动作都读反了'),
    ('chunk036', '还落满了思想', '还撒满了思想', '⑥',
     '«plus semée de pensées qu’une porte de cathédrale»：semée 是「撒布着」；「落满」是落叶的落，与 semer 无关'),
    # ---- chunk037 ----
    ('chunk037', '就像两岸给泛滥激流的河床太窄', '就像两岸留给一道泛滥激流的河床太窄', '①',
     '«comme des berges qui offrent un lit trop étroit à un torrent déchaîné»：「给……的河床太窄」缺谓语，「给」字悬空'),
    # ---- chunk038 ----
    ('chunk038', '坐着观望，在门槛上镶出一道古怪而发暗的滚边',
     '坐着观望，把门槛镶成一道古怪而发暗的滚边', '①',
     '«festonnaient le seuil d’un liséré capricieux»：坐在门槛上的人是那道滚边本身，用「在门槛上镶出」读成他们往门槛上做装饰，主谓失配'),
    # ---- chunk040 ----
    ('chunk040', '；当是我自己在写它们的时候', '；而当我自己在写它们的时候', '⑥',
     '«quand c’était moi qui les composais»：「当是」不成词（当/但之误），与前句「只有当我读他的作品时」构成对照，缺转折连词读不通'),
]

def main():
    touched = {}
    for chunk, old, new, kind, why in EDITS:
        path = os.path.join(BASE, chunk, 'final.txt')
        text = io.open(path, encoding='utf-8', newline='').read()
        assert old in text and text.count(old) == 1, (chunk, old)
        bak = path + '.bak_20261125'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        raw = io.open(path, encoding='utf-8', newline='').read()
        assert len(raw.splitlines()) == len(raw.replace(old, new).splitlines()), chunk
        io.open(path, 'w', encoding='utf-8', newline='').write(raw.replace(old, new))
        touched.setdefault(chunk, []).append((kind, why))
    for chunk in sorted(touched):
        print(chunk, len(touched[chunk]))

if __name__ == '__main__':
    main()
    import ast
    ast.parse(io.open(__file__, encoding='utf-8').read())