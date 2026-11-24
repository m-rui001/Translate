# -*- coding: utf-8 -*-
"""《追忆似水年华》第二卷 chunk037-040 通读润色 p3（2026-11-25 轮）

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
    # ---- chunk037 ----
    ('chunk037', '她是一个小姑娘的舅舅，那姑娘来上我的课',
     '他是一个小姑娘的舅舅，那姑娘来上我的课', '④',
     '«C’est l’oncle d’une petite qui venait à mon cours»：说的是邦唐先生；「她……的舅舅」性别自相矛盾，一段里又紧接「我不认识她」，不改成「他」读者会错认'),
    # ---- chunk038 ----
    ('chunk038', '她比某位夫人可没那么叫人烦',
     '她可没有某位夫人那么叫人烦', '①',
     '«Elle est moins ennuyeuse que Mme X»：「比……没那么」两套比较句式叠在一处，语序拧着；改一处比较就够了'),
    # ---- chunk039 ----
    ('chunk039', '她了解她传播的本事',
     '她了解科塔尔夫人传播消息的本事', '④',
     '同一句里两个「她」分指斯万夫人和科塔尔夫人，读者要猜；此处换成名字'),
    # ---- chunk040 ----
    ('chunk040', '生活在那种圈子里的人自以为永远不可能邀请一个“机会主义者”、更不用说一个可恶的激进派这件事，会像煤油灯和公共马车一样天长地久。',
     '生活在那种圈子里的人，自以为永远不可能邀请一个“机会主义者”，更不用说一个可恶的激进派，并且觉得这规矩会像煤油灯和公共马车一样天长地久。', '①',
     '「……这件事，会像……一样天长地久」把几十字的长主语挂在「会」上，主谓之间隔着三重从句，读到最后已经忘了主语是什么'),
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