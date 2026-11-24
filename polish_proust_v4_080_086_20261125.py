# -*- coding: utf-8 -*-
"""通读润色：work_proust/out/v4/chunk080-086（7 个 final.txt）
准则：POLISH_BRIEF_2026-11-25.md 七类。只做“定位唯一子串 → 替换”，段数/行数不变。
"""
import ast
import os
import shutil

BASE = 'work_proust/out/v4'

EDITS = {
    '080': [
        # ①读不通：双重“鄙视”与“谁也不如……得厉害”两式相杂，主谓撑不住
        ('远算不得什么荣耀，她谁也不如鄙视这位波兰音乐家鄙视得厉害。',
         '远算不得什么荣耀，她比谁都要鄙视这位波兰音乐家。'),
    ],
    '081': [
        # ①缺主语：一串“出于……的需要”之后，“又加上了肖邦的作品”无人称
        ('或某句他也许根本没说过的话，又加上了肖邦的作品，',
         '或某句他也许根本没说过的话，人们又加上了肖邦的作品，'),
        # ③法语 sous la protection de laquelle il était entré juste à temps 硬搬，
        # 两个回指代词（它／其）撞在一处
        ('但被提到的那个名字这时就从它正好及时进入其庇护之下的招牌中获益了。',
         '但被提到的那个名字，这时正好及时进入了某块招牌的庇护之下，便从中获益了。'),
    ],
    '082': [
        # ⑥词义误读：nos parents 指“长辈”，非“父母”
        ('“我们的父母并不是我们这次拜访缩短的主要原因，”',
         '“我们的长辈并不是我们这次拜访缩短的主要原因，”'),
    ],
    '083': [
        # ⑦体例：引号——此句本是一段连续的对话，此处多出一个前引号
        ('倒挺好。“等您到了我这个年纪，',
         '倒挺好。等您到了我这个年纪，'),
        # ⑦体例：收引号误置于叙述句之后（cria-t-il à la cantonade 在引号外）
        ('‘孩子们，再见了！’他朝空阔处喊道，仿佛自己已经走远了五十步。”',
         '‘孩子们，再见了！’”他朝空阔处喊道，仿佛自己已经走远了五十步。'),
        # ⑥硬伤：tournée de confirmation 是“坚振巡视”，“确认”为 confirmation 的
        # 词典义直搬
        ('就像一个年迈的主教在确认巡视。',
         '就像一个年迈的主教在作坚振巡视。'),
    ],
    '084': [
        # ①“享受地”作状语不成话（J'éprouvai du plaisir à sentir…）
        ('我享受地感到，至少在这一刻，',
         '我愉快地感到，至少在这一刻，'),
        # ③法语比较结构直搬（dans certaines classes du peuple, plus de duplicité
        # que dans le monde），比较项错位
        ('是否比在上流社会里更多两面性，',
         '两面性是否比在上流社会里更多，'),
    ],
    '085': [
        # ①“我方面”不成词（N'était-elle de ma part que…）
        ('它难道只是我方面的一种无意识诡计',
         '它难道只是我这一方面的一种无意识诡计'),
    ],
    '086': [],
}

report = []
for d, edits in EDITS.items():
    path = os.path.join(BASE, 'chunk%s' % d, 'final.txt')
    with open(path, 'r', encoding='utf-8', newline='') as f:
        text = f.read()
    lines_before = text.count('\n')
    bak = path + '.bak_20261125'
    if not os.path.exists(bak) and edits:
        shutil.copy2(path, bak)
    n = 0
    for old, new in edits:
        if old not in text:
            # 上一轮已落盘（脚本中途断言失败重跑）：确认新文已在且唯一
            assert text.count(new) == 1, (d, 'neither old nor new', old)
            n += 1
            continue
        assert text.count(old) == 1, (d, old, text.count(old))
        text = text.replace(old, new)
        n += 1
    assert text.count('\n') == lines_before, (d, 'line count changed')
    # 体例自检
    assert text.count('“') == text.count('”'), (d, 'quote imbalance')
    assert '"' not in text, (d, 'ascii quote')
    assert '⟦' not in text and '⟧' not in text, (d, 'italic markers')
    if n:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
    report.append((d, n))

print('改为：')
for d, n in report:
    print('  chunk%s: %d 条' % (d, n))
print('合计 %d 条' % sum(n for _, n in report))

ast.parse(open(__file__, encoding='utf-8').read())