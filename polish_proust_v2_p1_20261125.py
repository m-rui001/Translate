# -*- coding: utf-8 -*-
"""《追忆似水年华》第二卷 chunk027-031 通读润色 p1（2026-11-25 轮）

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
    # ---- chunk027 ----
    ('chunk027', '这一切使我们面对所爱之人时的注意力颤抖得太厉害',
     '这一切使我们面对所爱之人时，注意力颤抖得太厉害', '②',
     '「我们面对所爱之人时的注意力」三个「的」把中心语「注意力」压没了，切断状语读起来才顺'),
    ('chunk027', '斯万以为我像的那种不择手段的年轻人，我把他想象成这样：',
     '斯万以为我像的那种不择手段的年轻人，我是这样想象的：', '③',
     '法语关系从句先行、再用「我把他……」回指，是句法直搬；中文改成话题+「我是这样想象的」才立得住'),
    ('chunk027', '让我想要、让我向她要求——为了第二天，每天在这方面把我的柔情变成一种新的柔情。',
     '让我想要、让我向她要求，每天在这方面把我的柔情变成一种新的柔情，为的是第二天。', '①',
     '「为了第二天」插在句首，与后面的「每天……」争主语，整句读不出因果；移到句末作目的'),
    # ---- chunk028 ----
    ('chunk028', '这封信的真诚，我竟觉得他当时不肯被说服真是太不明智了',
     '这封信如此真诚，我竟觉得他当时不肯被说服，真是太不明智了', '①',
     '「这封信的真诚，我竟觉得……太不明智」前后两个话题相撞，主谓失配；补「如此」并断开'),
    ('chunk028', '几乎没让我更喘多少气',
     '几乎没有让我喘得更厉害', '①',
     '«sans qu’en fût à peine augmenté l’essoufflement»：「没……多少」双否叠用，读者要绕两步才算得清；改正面陈述'),
    # ---- chunk029 ----
    ('chunk029', '而例如意味着刚挨了骂',
     '而比如说意味着刚挨了骂', '③',
     '«mais par exemple qu’on a été grondé»：par exemple 在此是「说不定／比如说」，直搬成「例如」不成话'),
    ('chunk029', '那是一场已经开始的疾病焦躁的应答',
     '那是一场已经开始的疾病发出的狂热应答', '⑥',
     '«réponse fébrile d’une maladie commencée»：fébrile 是「狂热的、亢奋的」，不是「焦躁」；且两个「的」套叠读不通'),
    # ---- chunk030 ----
    ('chunk030', '我半点也不可怜，她尽可以放心我是幸福的',
     '我半点也不值得可怜，她尽可以放心我是幸福的', '⑥',
     '«je n’étais pas à plaindre»：「我半点也不可怜」在中文里歧义（像是「我不慈悲」），补「值得」才落实原意'),
    # ---- chunk031 ----
    ('chunk031', '因为那种病要求一种饮食，这种饮食反过来对结核病人又会是有害的',
     '因为那种病要求的饮食反过来对结核病人又会是有害的', '②',
     '同一句里「一种饮食……这种饮食」两遍指同一物，删掉回指，句子的推进才不受阻'),
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
        print('%s %s OK  %s' % (chunk, cat, why[:28]))

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