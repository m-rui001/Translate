# -*- coding: utf-8 -*-
"""逐段润色：第二卷 out_ind/v2 chunk132 / chunk134 / chunk135 / chunk136
作业准则：POLISH_BRIEF_2026-11-25.md + SUBTASK_README_2026-11-26.md
只做「定位唯一子串 → 替换 → 断言命中数」，不整文件重写，段数/空行/换行符不变。
"""
import ast
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'  # 与 verify_polish.py 一致；已存在则不覆盖

EDITS = {
    '132': [
        # ⑥ 生造词：「柔活」非规范词，souple → 柔韧
        ('那份优雅是柔活的', '那份优雅是柔韧的',
         '⑥', "d'une élégance souple"),
        # ① 主谓失配：「皮……把红透了出来」
        ('两颊的皮太细，把一层鲜明的红透了出来',
         '两颊的皮太细，一层鲜明的红直透出来',
         '①', 'la peau trop fine de ses joues laissait transparaître une vive rougeur'),
    ],
    '134': [
        # ④ 「他圣卢本人」与他前一个「他」（布洛克的朋友）同形，改为直呼其名
        ('他圣卢本人对此毫不在意', '圣卢本人对此毫不在意',
         '④', "à laquelle, lui, Saint-Loup, n'attachait aucune importance"),
        # ① 「可见……显然」语义重复
        ('可见布洛克显然以为', '布洛克显然以为',
         '①', 'Bloch croyait donc évidemment'),
        # ② 长定语「布洛克有朝一日……涌上脸的红晕」压在「它」上，拆句
        ('而布洛克有朝一日发现自己的错误时大概会涌上脸的红晕，他预先就感到它通过反照升到了自己脸上。',
         '而布洛克有朝一日发现自己的错误时，脸上大概会涌起红晕——这红晕他预先就感到，借着反照，升到了自己脸上。',
         '②', 'la rougeur qui colorerait sans doute un jour le visage de Bloch... il la sentit par anticipation et réversibilité monter au sien'),
        # ① 句末括注被搬成半截悬空句，读不通
        ('而有时，他被推向的那种“另想办法”，就是自杀——被推向它，是毫无任何重要性的。',
         '而那种“另想办法”有时就是自杀——被逼到那一步，也照样“没有任何一丁点重要性”。',
         '①', "l'autre arrangement vers lequel il est sans aucune espèce d'importance d'être rejeté étant quelquefois le suicide"),
        # ⑤ 职衔语序：Lord John Ruskin → 约翰·罗斯金勋爵
        ('约翰勋爵·罗斯金的《威尼斯之石》', '约翰·罗斯金勋爵的《威尼斯之石》',
         '⑤', 'de Lord John Ruskin'),
    ],
    '135': [
        # ① 插入语 mais tu es demeuré naïf 是陈述，不是反问
        ('不过你还挺天真的吧？你眼下', '不过你还是一派天真。你眼下',
         '①', 'mais tu es demeuré naïf'),
        # ④ 同一句内「他」「她」混指同一人（原文为 elle），统一为「她」
        ('可他会把你亲口托他带的最重要的信忘在口袋里',
         '可她把你亲口托她带的最重要的信忘在口袋里',
         '④', 'elle vous a demandé elle-même de lui confier'),
        # ① 「他见你的乐趣对他如此珍贵」主语关系绕
        ('他见你的乐趣对他如此珍贵，以至于宁可让你累死',
         '他见到你所感到的乐趣，对他如此珍贵，以至于宁可让你累死',
         '①', "le plaisir qu'il a à vous voir lui est si cher qu'il vous ferait crever de fatigue"),
        # ① 主谓失配：「注意力……注意到它」
        ('再说，我们的注意力总是被吸引到自己身上的特征，似乎也就比别的东西更容易在别人身上注意到它。',
         '再说，我们的注意力总是被吸引到自己身上的特征，于是这特征似乎也比别的东西更容易在别人身上被注意到。',
         '①', 'notre attention toujours attirée sur ce qui nous caractérise le remarque plus que toute autre chose chez les autres'),
        # ③ 「每个人关于我们所讲的话」是 ce que chacun nous en disait 的硬搬
        ('当我们不是凭着每个人关于我们所讲的话而对自己形成的形象',
         '当我们不是凭着别人对我们的说法所形成的自我形象',
         '③', "l'image qu'on s'était faite de soi-même grâce à ce que chacun nous en disait"),
    ],
    '136': [
        # ⑤ snobisme 在本段下文作「势利眼」，同句内「附庸风雅」不统一
        ('布洛克跟我谈起我势必会经历的那场附庸风雅的风潮',
         '布洛克跟我谈起我势必会经历的那场势利的风潮',
         '⑤', 'la crise de snobisme que je devais traverser'),
        # ⑥ 词义：pour que cela lui fût redit 是「让人转告他」，非「让他传到耳朵里」
        ('还是故意说的，就是为了让他传到耳朵里',
         '还是故意说的，就是为了让人转告他',
         '⑥', 'exprès, pour que cela lui fût redit'),
        # ⑥ 擦了一滴眼泪 → essuya une larme 是「擦去」
        ('还擦了一滴眼泪', '还擦去了一滴眼泪',
         '⑥', 'et essuya une larme'),
    ],
}

total = 0
for chunk, edits in EDITS.items():
    path = os.path.join(BASE, 'chunk' + chunk, 'final.txt')
    bak = os.path.join(os.path.dirname(path), BAK)
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    with open(path, encoding='utf-8', newline='') as f:
        text = f.read()
    before = (text.count('\n'), sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff'))
    applied = 0
    for old, new, cat, fr in edits:
        if old not in text:
            # 已落盘过（脚本可重跑）：改为校验新句在位
            assert text.count(new) == 1, (chunk, new)
            continue
        assert text.count(old) == 1, (chunk, old, text.count(old))
        text = text.replace(old, new)
        applied += 1
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    with open(path, encoding='utf-8', newline='') as f:
        text2 = f.read()
    after = (text2.count('\n'), sum(1 for ch in text2 if '\u4e00' <= ch <= '\u9fff'))
    assert before[0] == after[0], (chunk, before, after)
    total += applied
    print('chunk%s 改动 %d 条（本次新落盘，脚本可重跑）行数 %d→%d 汉字 %d→%d 换行符 CRLF=%d' % (
        chunk, applied, before[0] + 1, after[0] + 1, before[1], after[1],
        text2.count('\r\n')))

print('合计改动 %d 条' % total)
ast.parse(open(__file__, encoding='utf-8').read())