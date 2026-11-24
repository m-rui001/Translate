# -*- coding: utf-8 -*-
"""逐段润色 chunk091-chunk095（第三卷），2026-11-26 轮。
只做「定位唯一子串 → 替换 → 断言命中数」的改法；段数/行数/空行结构/换行符不变。
"""
import ast
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

EDITS = {
    'chunk091': [
        # ⑥ hard: la Patrie française 是保皇派民族主义同盟（Ligue de la Patrie française），不是报纸
        ('拿《法兰西祖国报》来烦我们',
         '拿‘法兰西祖国’来烦我们'),
        # ⑥ sieur Dreyfus 含轻蔑，非敬称「先生」
        ('偏偏又是德雷福斯先生的同乡',
         '偏偏又是那个德雷福斯的老乡'),
        # ④ 前句刚由档案保管员发言，此「他」实指公爵
        ('一听到布洛克的名字，他就瞧见布洛克',
         '一听到布洛克的名字，公爵就瞧见布洛克'),
        # ① 括注缺谓语，读来断裂
        ('（我只在联合俱乐部和赛马俱乐部）',
         '（我只是联合俱乐部和赛马俱乐部的成员）'),
        # ① comme de l'an quarante（满不在乎）直搬成「跟哪年哪月的事一样」，读者无从索解
        ('我才不当回事呢，跟哪年哪月的事一样',
         '我才不当回事呢，就跟四零年的旧皇历一样'),
    ],
    'chunk092': [
        # ⑦ 括注插在引语中间却先闭合了引号，引语被切成残句
        ('说道：‘以我军人的名誉担保——’说到这里，德·诺普瓦先生的声音微微颤动，带着一丝爱国主义的颤音——‘这就是我的信念’',
         '说道：‘以我军人的名誉担保，’——说到这里，德·诺普瓦先生的声音微微颤动，带着一丝爱国主义的颤音——‘这就是我的信念’'),
        # ⑦ 破折号孤用（前有成对括注），主句复起处应归位为逗号
        ('我说的是真话’——风向便转了',
         '我说的是真话’，风向便转了'),
    ],
    'chunk093': [
        # ① 「有些题目，在上面」悬空，题旨与状语黏连
        ('况且，有些题目，在上面掀起一场骚动是极不谨慎的',
         '况且，在有些题目上掀起一场骚动是极不谨慎的'),
        # ① 「也轮不到需要」不成句
        ('也轮不到需要一位靠军事政变起家的将军。',
         '也感觉不到需要一位搞军事政变的将军。'),
        # ① 「我就说这最后一句」语序倒错；⑤「争吵」对 algarade偏重，改「吵闹」
        ('关于奥尔良的亨利亲王那场争吵，我就说这最后一句：我很难相信它会合他父亲的心意。',
         '关于奥尔良的亨利亲王那场吵闹，我最后再说一句：我很怀疑这会合他父亲的心意。'),
        # ⑥ circonstances secondaires 是「次要情况」，「情状」为生造文言
        ('只愿意谈次要的情状',
         '只愿意谈次要的情况'),
    ],
    'chunk094': [
        # ①④ 上段末言保加利亚亲王不会拥抱埃斯特哈兹，此处 il 指亲王，「是个普通士兵」易读成「他宁可是士兵」
        ('“他倒宁愿是个普通士兵，”',
         '“他倒宁愿那是个普通士兵，”'),
        # ④ 同句两个「她」分指萨冈夫人与维尔帕里西夫人
        ('心想德·萨冈夫人既然亲自登门邀请过这位夫人，接待她的朋友自然也会乐意',
         '心想德·萨冈夫人既然亲自登门邀请过维尔帕里西夫人，接待这位夫人的朋友自然也会乐意'),
        # ⑥ faux chic, snob à côté 的「à côté」（差一截、不上台面）被吞掉
        ('是不是相当假时髦、相当装腔作势？',
         '是不是有点假时髦、有点不上台面的势利？'),
    ],
    'chunk095': [
        # ⑥ faire entendre les mots de vérité 是「让人听见」，非「听到」
        ('要听到真理和正义这两个词，就必须横渡英吉利海峡',
         '要让‘真理’和‘正义’这两个词有人听，就必须横渡英吉利海峡'),
        # ① 「我认为不幸地在……那里所缺乏的东西」三层定语压在中心语上
        ('如果你们还有一点我认为不幸地在你们某些领袖和朋友那里所缺乏的东西，也就是一点政治头脑',
         '如果你们身上还有一点——可惜我觉得你们某些领袖和朋友偏偏缺少的——政治头脑'),
    ],
}

REPORT = []

for chunk, edits in EDITS.items():
    d = os.path.join(BASE, chunk)
    path = os.path.join(d, 'final.txt')
    bak = os.path.join(d, BAK)
    if not os.path.exists(bak):
        shutil.copy2(path, bak)

    with open(path, encoding='utf-8', newline='') as f:
        text = f.read()

    before_lines = text.count('\r\n')
    before_han = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')
    before_paras = len(text.rstrip('\r\n').split('\r\n\r\n'))
    crlf = '\r\n' in text

    n = 0
    for old, new in edits:
        assert old in text, (chunk, old[:30])
        assert text.count(old) == 1, (chunk, 'not unique', old[:30])
        text = text.replace(old, new)
        n += 1

    assert text.count('\r\n') == before_lines, (chunk, 'line count changed')
    assert len(text.rstrip('\r\n').split('\r\n\r\n')) == before_paras, (chunk, 'para count changed')
    assert ('\r\n' in text) == crlf

    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)

    after_han = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')
    REPORT.append((chunk, before_paras, n, before_lines, text.count('\r\n'),
                   before_han, after_han, 'CRLF' if crlf else 'LF'))

print('chunk | 段数 | 改动 | 换行改前后 | 汉字改前后 | 换行符')
for r in REPORT:
    print('%s | %d | %d | %d→%d | %d→%d | %s' % r)
print('总改动', sum(r[2] for r in REPORT), '条')

ast.parse(open(__file__, encoding='utf-8').read())
print('AST OK')