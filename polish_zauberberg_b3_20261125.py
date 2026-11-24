# -*- coding: utf-8 -*-
"""《魔山》batch3：Sorgenkind des Lebens 与“俄国桌”用名归一、称谓归一、指代澄清。"""
import io, os, glob, ast

BASE = 'E:/Translate/work_zauberberg/out'


def patch(rel, pairs):
    path = os.path.join(BASE, rel)
    with io.open(path, 'r', encoding='utf-8-sig', newline='') as f:
        text = f.read()
    bak = path + '.bak_20261125'
    if not os.path.exists(bak):
        with io.open(bak, 'w', encoding='utf-8-sig', newline='') as f:
            f.write(text)
    for old, new, cnt in pairs:
        assert old in text, (rel, old)
        assert text.count(old) == cnt, (rel, old, text.count(old))
        text = text.replace(old, new)
    with io.open(path, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(text)
    print('patched', rel, len(pairs))


patch('index_split_008/c07/final.txt', [('“好俄罗斯人桌”', '“好的俄国桌”', 1)])
patch('index_split_019/c03/final.txt', [('“好俄罗斯人桌”', '“好的俄国桌”', 1)])

patch('index_split_016/c02/final.txt', [
    ('“好俄罗斯人桌”', '“好的俄国桌”', 1),
    ('称其为“生活的愁孩子”', '称其为“生命的忧患儿”', 1),
    ('由宫廷顾问贝伦斯大夫以多舌的辞令', '由宫廷顾问贝伦斯以多舌的辞令', 1),
])

patch('index_split_017/c14/final.txt', [
    ("觉得我是个‘人生的忧患儿童’", "觉得我是个‘生命的忧患儿’", 1),
    ("把我当作‘人生的忧患儿童’", "把我当作‘生命的忧患儿’", 1),
])

# 指代：Settembrini 说“他和他表兄”两人都属受威胁的天性，原句“他表兄和他”易错认
patch('index_split_013/c02/final.txt', [
    ('说得不错，他表兄和他，多多少少都算是受了威胁的天性',
     '说得不错，他和表兄，多多少少都算是受了威胁的天性', 1),
])

ast.parse(open(__file__, encoding='utf-8').read())
print('OK')