# -*- coding: utf-8 -*-
"""《追忆似水年华》第一卷 chunk021-025 通读润色 p2c（2026-11-25 轮）

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
    # ---- chunk021 ----
    ('chunk021', '我祖父的表妹', '我外祖父的表妹', '⑤',
     '原文 la cousine de mon grand-père；本卷 grand-père 一律作「外祖父」（66 处对 6 处），此处漏改'),
    ('chunk021', '她说话从来都只相当低声', '她说话总是压得相当低', '①',
     'Elle ne parlait jamais qu’assez bas 直搬，「只相当低声」不成句'),
    ('chunk021', '整整一种隐秘的、看不见的、过剩的、有德性的生活释放出来的，由室内的空气悬浮着',
     '整整一种隐秘的、看不见的、过剩的、有德性的生活所释放出来、由室内的空气悬浮着的气味', '②',
     '「那是德行、智慧、习惯，整整一种……生活释放出来的，由……悬浮着」缺中心语，四个「的」定语悬空；补出「的气味」'),
    # ---- chunk022 ----
    ('chunk022', '进姑婆家之前', '进姑祖母家之前', '⑤',
     'grand’tante 本卷 canon 为「姑祖母」（34 处），「姑婆」仅 4 处，归一'),
    # ---- chunk023 ----
    ('chunk023', '也只好少叫她一会儿，知道母亲多看重这个用人伺候得好',
     '也只好少用她一点，知道母亲多看重这个用人伺候得有多好', '①',
     'se priver un peu d’elle 是「少用她一点」，非「少叫她一会儿」；「看重这个用人伺候得好」缺程度词，读不通'),
    ('chunk023', '弗朗索瓦丝照看父母所需一切齐备之后', '弗朗索瓦丝照看父母所需的一切都齐备之后', '①',
     'après avoir veillé à ce que mes parents eussent tout ce qu’il leur fallait：原译缺「都」，句子断裂'),
    ('chunk023', '它们要是从本堂神甫先生家来的，那也没什么奇怪。',
     '它们就是从本堂神甫先生家来的，那也不奇怪。', '⑥',
     'Il n’y aurait rien d’étonnant qu’elles viennent de chez M. le Curé 是虚拟式推测，非条件句；「要是……的」把肯定推测改成假设'),
    # ---- chunk024 ----
    ('chunk024', '不记得有哪一次，每当圣灵街', '不记得有哪一次，每逢圣灵街', '①',
     '「不记得有哪一次，每当……」两个引导词撞在一起，改「每逢」使从句就位'),
    # ---- chunk025 ----
    ('chunk025', '其余几个却被拉得过分开', '其余几个却被刻意拉开', '①',
     'd’autres écartés avec recherche：「拉得过分开」不成话'),
    ('chunk025', '在那些难得的时刻之一', '在那种难得的时刻', '③',
     'à l’un de ces rares moments 直搬「之一」，与「在……时刻」不搭'),
    ('chunk025', '它便安慰我，因大地尚光秃黑黢，让这一片耀眼的、金灿灿的玻璃勿忘我花铺展开来，仿佛置身于一个历史性的、属于圣卢易后继者时代的春天。',
     '它便安慰我，让这一片耀眼的、金灿灿的玻璃勿忘我花铺展开来，仿佛开在一个历史性的、属于圣卢易后继者时代的春天里。', '①',
     '前半句已说「地还光着、黑着」，此处「因大地尚光秃黑黢」重复且「因」字悬空；句末「仿佛置身于……春天」主语缺失'),
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