# -*- coding: utf-8 -*-
"""《浮士德》第一部 润色落盘 p6（c06 书斋·魔约 / c08 书斋·学生场景前半）"""
import io, os, shutil, ast

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work_pub', 'faust', 'out', 'c001')

EDITS = {
    'c06': [
        # 「was steht dem Herrn zu Diensten?」原译倒装成「有什么要小的效劳」，读不通
        ('吵什么？有什么要小的效劳？', '吵什么？有什么要小的效劳的？'),
        # 舞台指示作「游学书生装」，同一词 Scholastikus 此处作「游方学者」，术语不统一；
        # 「Der Kasus」是拉丁语法「格」的双关，原译「案子」失义
        ('一个游方学者？这案子倒叫我好笑。', '一个游学书生？这个“格”倒叫我好笑。'),
    ],
    'c08': [
        # Des Italieners feurig Blut：三字硬拼「火热血」不成词
        ('意大利人的火热血，北方人的耐久', '意大利人的热血，北方人的耐久'),
        # 「Herr Nachbar Wanst」是一个人（大肚子街坊），原译拆成「胃口先生」＋「街坊」两个人
        ('这种事留给胃口先生、咱们的街坊去吧！', '这种事留给咱们那位大肚子街坊去吧！'),
        # 「Vergeht mir Hören, Sehn und Denken」直搬，中文句意断裂
        ('在那些厅里，那些凳子上，我听得、看得、想得都没了。',
         '在这些厅堂里、这些长凳上，我的听、看、想一样样都消磨尽净。'),
        # 「Weh dir, daß du ein Enkel bist!」＝可叹你是孙辈（生来继承这堆旧法）；
        # 「你是个孙子」在中文里是骂人话，误读
        ('倒霉的是你，因为你是个孙子！', '倒霉的是你，谁叫你是孙辈！'),
    ],
}

report = []
for ch, edits in EDITS.items():
    path = os.path.join(BASE, ch, 'final.txt')
    text = io.open(path, encoding='utf-8', newline='').read()
    bak = path + '.bak_20261125b'
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    n0 = text.count('\n'); b0 = sum(1 for L in text.split('\n') if not L.strip())
    for old, new in edits:
        assert old in text, (ch, old)
        assert text.count(old) == 1, (ch, old, text.count(old))
        text = text.replace(old, new)
    assert text.count('\n') == n0, ch
    assert sum(1 for L in text.split('\n') if not L.strip()) == b0, ch
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    report.append((ch, len(edits)))

print('OK', report)
ast.parse(io.open(__file__, encoding='utf-8').read())