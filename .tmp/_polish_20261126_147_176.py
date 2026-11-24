# -*- coding: utf-8 -*-
"""v3 chunk147 / 159 / 161 / 163 / 176 逐段润色落盘（定位唯一子串 → 替换）。"""
import ast
import os
import re
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

EDITS = {
    'chunk147': [
        # ③ 法语括注被搬成破折号、插在「是那样一些爱抚」之后把话掐断 → 括注独立成插入语
        ('是那样一些爱抚——你恼恨不能让那个女人亲自把它们完成，恰恰是这些爱抚，其余的一概排除在外。',
         '是那样一些爱抚——你恼恨不能让那个女人亲自把它们完成——恰恰是这些爱抚，其余的一概排除在外。'),
        # ④ 同一句里「你细细端量」后突然换成「我们的目光」，主语跳人称 → 统一为「你」
        ('我们的目光毫无过渡地从修整过的园林移向默东和瓦莱里安山那些天然的高处',
         '你的目光毫无过渡地从修整过的园林移向默东和瓦莱里安山那些天然的高处'),
        # ⑦/① 「是天色的颜色」叠字成病 → couleur du temps 即「天色」
        ('然而这水在它神圣的童年里始终是天色的颜色，并且时时刻刻忘掉云和花的影像。',
         '然而这水在它神圣的童年里始终是天色，并且时时刻刻忘掉云和花的影像。'),
    ],
    'chunk159': [
        # ⑥ plus catastrophique que le Déluge ET le Götter Dämmerung：一层比较、两项并列，
        #    原译拆成两个「比……还」，把并列读成了递进
        ('那会比大洪水还要灾难深重，比《众神的黄昏》还要厉害——只不过持续的时间要短一些。',
         '那会比大洪水与《众神的黄昏》加在一起还要灾难深重——只不过持续的时间要短一些。'),
    ],
    'chunk161': [
        # ⑥ ni chez lui ni chez la duchesse 是「既不在他家也不在公爵夫人家」，非「在此之前」
        ('她们在我去他家、去公爵夫人家之前，在我最初在她们的姑母家见到她们时，并不曾在我眼前显现，正如',
         '她们在他家、在公爵夫人家都不曾在我眼前显现，尽管我最初是在她们的姑母家见到她们的；正如'),
        # ⑤ 拉贝尔玛（本卷仅此 2 处）归一到 canon「贝尔玛」（v3 共 40 处）
        # ⑥ gens du monde 是「上流社会的人」，不是「世人」；chez celle-ci 指贝尔玛，非「后者」
        ('正如我头一天不曾看出把拉贝尔玛与她的同台演员们隔开的那些差别，虽说在后者身上那些特点要明显得多，因为世人身上的特点总要随着物件',
         '正如我头一天不曾看出把贝尔玛与她的同台演员们隔开的那些差别，虽说在贝尔玛身上这些特点要比在上流社会的人身上明显得多，因为世人身上的特点总要随着物件'),
        # ① 「离我们之远，就像……一头动物」比较句缺「一样」，句子断在半空
        ('仿佛以为这位史诗诗人和这位统帅离我们之远，就像在动物园里看到的一头动物。',
         '仿佛以为这位史诗诗人和这位统帅离我们之远，就像在动物园里看到的一头动物一样。'),
        # ① 「会只显得讨人喜欢」语序错乱 → 「只会显得」
        ('这些片段倘若署上一个同时代人的名字单独发表，会只显得讨人喜欢',
         '这些片段倘若署上一个同时代人的名字单独发表，只会显得讨人喜欢'),
    ],
    'chunk163': [
        # ⑥ bercé doucement 是「轻轻摇着我（哄我入睡）」，不是「在耳边回荡」
        ('客人的门铃声不断响着，轻轻地在耳边回荡。',
         '客人的门铃声不断响着，轻轻地摇晃着我。'),
        # ③ 法语括注（moins rapidement il est vrai）被搬成破折号插在「终于……把我……唤醒」中间
        ('终于——虽说没有那么快——把我从遐想中唤醒，就像',
         '终于把我从遐想中唤醒——虽说这唤醒来得并不太快——就像'),
        # ⑥ sinon pour eux, du moins pour moi 是「即使对他们不算，至少对我」→ 递进，原译读反成转折
        ('不认识他的宾客显然无足轻重，至少对他们如此，而对我则不然；',
         '不认识他的宾客显然无足轻重，对他们固然如此，对我就更是如此；'),
    ],
    'chunk176': [
        # ⑥ Jardin d'Acclimatation 是（巴黎）驯化园，非植物园；chunk164 已作「驯化园」
        ('使这个风雅的中心酷似植物园里的“棕榈园”',
         '使这个风雅的中心酷似驯化园的“棕榈园”'),
        # ① ce Swann quelconque 的 quelconque 是「平平常常、没什么特别」，非「随便什么」
        ('也不大愿意向这个随便什么斯万主动示好',
         '也不大愿意向这个平平常常的斯万主动示好'),
    ],
}

TOTAL = 0
for chunk in sorted(EDITS):
    d = os.path.join(BASE, chunk)
    path = os.path.join(d, 'final.txt')
    bak = os.path.join(d, BAK)
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    with open(path, encoding='utf-8', newline='') as f:
        text = f.read()
    before_lines = len(text.replace('\r\n', '\n').split('\n'))
    before_cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    n = 0
    for old, new in EDITS[chunk]:
        assert old in text, (chunk, old[:30])
        assert text.count(old) == 1, (chunk, old[:30], text.count(old))
        text = text.replace(old, new)
        n += 1
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    after_lines = len(text.replace('\r\n', '\n').split('\n'))
    after_cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    assert before_lines == after_lines, (chunk, before_lines, after_lines)
    crlf = text.count('\r\n')
    print(f'{chunk}: 改动 {n} 条; 行 {before_lines}->{after_lines}; '
          f'汉字 {before_cjk}->{after_cjk}; crlf={crlf}')
    TOTAL += n
print('total edits:', TOTAL)

ast.parse(open(__file__, encoding='utf-8').read())