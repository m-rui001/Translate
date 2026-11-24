# -*- coding: utf-8 -*-
"""《追忆似水年华》第二卷 chunk032-036 通读润色 p2（2026-11-25 轮）

只做「定位唯一子串 -> 替换 -> 断言命中数」的改法，不整文件重写。
行数/段数不变；已有 .bak_20261125 的不覆写。专名一律不动。
"""
import ast
import io
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    'work_proust', 'out_ind', 'v2')

# (chunk, old, new, 类别, 理由)
EDITS = [
    # ---- chunk032 ----
    ('chunk032', '铭文下方是一个字母，那是一种很大的字迹',
     '铭文下方是一个字母，笔迹很大', '⑥',
     '「一个字母」与「一种字迹」量类失配（«une lettre, d’une grosse écriture»）；「那是一种很大的字迹」主语暗换成字迹，读来断裂'),
    # ---- chunk033 ----
    ('chunk033', '也许可以认为，我对此部分地要归功于一件小事',
     '也许可以说，我对此要部分地归功于一件小事', '①',
     '「认为……要归功于」主谓失配：归功的主语是我，不是「认为」的宾语从句；换成「可以说」，让「我」回到主句'),
    ('chunk033', '我觉得，它们那既天然又超自然的草的纤细，加上那艺术卷须的力量',
     '我觉得，它们那草的纤细——既天然又超自然——加上那艺术卷须的力量', '②',
     '「既天然又超自然的草的纤细」三个「的」串成定语，中心语「纤细」被两个修饰层压住；把判断语提出作插入语'),
    # ---- chunk034 ----
    # 同批第二处（并列结构下半句，随本批单独落盘）：'有时则圈在' -> '时而又圈在'
    ('chunk034', '再有一回，“吉尔贝特”的名字有时斜着写在角落里',
     '再有一回，“吉尔贝特”的名字时而斜着写在角落里', '⑦',
     '「再有一回」与「有时……有时……」两套并列标记并用，读者分不清这是同一封信的两种写法还是两封信；统一为「时而……时而又……」'),
    # ---- chunk035 ----
    ('chunk035', '给你做科隆班家一样好的吐司',
     '给你做跟科隆班家一样好的吐司', '①',
     '「做科隆班家一样好的吐司」缺比较介词，「科隆班家」悬空'),
    ('chunk035', '嵌着鲜红果子隔格',
     '嵌着一格格鲜红果子', '⑥',
     '«cloisonné de fruits écarlates»：cloisonné 是「隔成一格一格的」；「果子隔格」不成词，是错字'),
    # ---- chunk036 ----
    ('chunk036', '如果说，我已经带着敬畏与欢喜的颤栗',
     '虽说我已经带着敬畏与欢喜的颤栗', '①',
     '「如果说」后面本该有「那么」呼应，此处接的是「然而」，让步关系被写成了假设关系'),
    ('chunk036', '照那句漂亮的俗话说的——',
     '正如那句漂亮的俗话所说——', '③',
     '«comme dit le joli proverbe»直搬成「照……说的」，「照」字后缺主句，成了悬空修饰语'),
    ('chunk036', '我是奉了那个穿短裤的男仆传达的夫人之命——夫人想跟我说一句话——',
     '我是奉了夫人之命——话是那个穿短裤的男仆传的，夫人想跟我说一句话——', '②',
     '「那个穿短裤的男仆传达的夫人之命」三个「的」套在一起，谁传谁的话要读两遍才理得清'),
]


def line_count(path):
    with io.open(path, 'r', encoding='utf-8', newline='') as f:
        return len(f.read().split('\r\n'))


def main():
    cache = {}
    for chunk, old, new, cat, why in EDITS:
        path = os.path.join(BASE, chunk, 'final.txt')
        if path not in cache:
            with io.open(path, 'r', encoding='utf-8', newline='') as f:
                cache[path] = f.read()
        text = cache[path]
        assert old in text, (chunk, old)
        assert text.count(old) == 1, (chunk, old, text.count(old))
        cache[path] = text.replace(old, new)
        print('%s %s OK  %s' % (chunk, cat, why[:30]))

    for path, text in cache.items():
        bak = path + '.bak_20261125'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        before = line_count(path)
        with io.open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        after = line_count(path)
        assert before == after, (path, before, after)
        print('WROTE %s lines %d -> %d' % (os.path.basename(os.path.dirname(path)), before, after))


main()
ast.parse(io.open(__file__, encoding='utf-8').read())