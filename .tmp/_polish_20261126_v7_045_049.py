# -*- coding: utf-8 -*-
"""v7 chunk045/047/048/049 逐段润色落盘脚本（定位唯一子串 -> 替换）。
只改 ①读不通 ②的字堆叠 ③外语句法 ⑥硬伤 ⑦体例 五类，其余不动。
"""
import ast
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    '045': [
        # ⑥ « désappointèrent presque autant ... que l'agaçait ... » 两种情绪被并成一种
        ('这份动人的情意，几乎和那套略带几分程式化的乡巴佬腔调一样叫他恼火。',
         '这份动人的情意叫他失望，几乎不下于那套略带几分程式化的乡巴佬腔调叫他恼火。'),
        # ① « n'aboutissait qu'à révéler » 「什么也没落到」不成句
        ('因为它除了暴露出那么多愚蠢和天真，什么也没落到。',
         '因为它除了暴露出那么多愚蠢和天真，什么也没换来。'),
    ],
    '047': [
        # ① « J'espère pour lui, si, comme il est certain, il vit encore, qu'il était ... »
        #    条件从句被硬塞进主谓之间，读不通
        ('我希望他倘若如确凿无疑的情形那样还活着，得的不是一种长期的疾病，而只是一次短暂的中毒。',
         '我希望他得的并不是一种长期的疾病，而只是一次短暂的中毒——倘若他确实还活着，这是确凿无疑的。'),
    ],
    '048': [
        # ⑦ 顿号连接一个分句和一个名词短语（« même à supposer que l'abord soit simple,
        #    et inutiles les marivaudages ... »）
        ('即使假定接近是简单的、那些在沙龙里',
         '即使假定接近是简单的，那些在沙龙里'),
    ],
    '049': [
        # ② 「往往很轻的、他以为……所造成的生活更加艰苦的生活」三个「的」压住中心语
        ('比那种往往很轻的、他以为正是在同它斗争的疾病所造成的生活更加艰苦的生活',
         '比那种往往很轻、他以为正是在同它斗争的疾病所造成的生活更加艰苦的生活'),
        # ① « des êtres individuellement bons » 「个人本来善良的」
        ('一些个人本来善良的人，竟毫无顾忌地参与大规模的谋杀',
         '一些个体本身善良的人，竟毫无顾忌地参与大规模的谋杀'),
        # ⑥ « quand tant de jeunes gens du monde ne tirent d'elles aucun profit »
        #    quand = 对比（而），译文误作「正如」
        ('而这些教育和文化本来是可以使他成为一个如此出色的人物的，正如它们也使那么多上流社会的年轻人一无所获。',
         '而这些教育和文化本来可以使他成为一个如此出色的人物，可它们却让那么多上流社会的年轻人一无所获。'),
        # ① « séparer la moralité de tout un ordre d'actions » 「道德性同一整类行为」
        #    易被读成「同一」
        ('把道德性同一整类行为分割开来的习惯',
         '把道德性与一整类行为分割开来的习惯'),
        # ③ « selon les prédictions et les vœux de Mme Verdurin » 的 « selon » 被硬搬成「在……之下」
        ('即使死亡在韦尔迪兰夫人的预言和愿望之下，并未先由一次中毒来临，而这种中毒在他的年纪，反正只会加速死亡。',
         '即使按照韦尔迪兰夫人的预言与心愿，死亡之前并没有先来一次中毒——而这种中毒在他这个年纪，反正只会加速死亡。'),
        # ① « ... de la cathédrale de Reims ... qu'elle ne pourrait voir puisque ... »
        #    关系从句被搬成悬空的「她不可能去看的」
        ('——她不可能去看的，因为这些教堂都或多或少遭到了毁坏，她便羡慕',
         '——这些教堂她都不可能去看，因为它们都或多或少遭到了毁坏，她便羡慕'),
        # ⑥ « à quel rêve durable et inconscient il est lié » 误作「同一种……梦」
        ('谁能说它同一种持久而无意识的梦联系在一起',
         '谁能说清它同怎样一种持久而无意识的梦连在一起'),
    ],
}


def han(t):
    return sum(1 for ch in t if '\u4e00' <= ch <= '\u9fff')


def main():
    total = 0
    for ck, pairs in EDITS.items():
        p = os.path.join(BASE, 'chunk' + ck, 'final.txt')
        with open(p, encoding='utf-8', newline='') as f:
            text = f.read()
        before_han, before_lines = han(text), text.count('\r\n') + 1
        n = 0
        for old, new in pairs:
            assert old in text, (ck, old)
            assert text.count(old) == 1, (ck, 'not unique', old)
            text = text.replace(old, new)
            n += 1
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        after_han, after_lines = han(text), text.count('\r\n') + 1
        assert before_lines == after_lines, (ck, 'line count changed')
        print(f'chunk{ck}: 改动 {n} 条 | 行数 {before_lines}->{after_lines} | 汉字 {before_han}->{after_han}')
        total += n
    print('合计改动', total, '条')


main()
ast.parse(open(__file__, encoding='utf-8').read())