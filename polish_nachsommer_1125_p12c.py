# -*- coding: utf-8 -*-
"""《晚夏》后半通读润色 —— p12c：c017/c04 第 5–11 段引号归层
该分片第 1、3、4 段及 c017 其余各片一律用「“ ”」引对话，唯第 5–11 段改用「‘ ’」，
同章两套层级并存。此处归回「“ ”」（段内无嵌套引语，逐段断言命中数）。
"""
import os, shutil, ast

PATH = r'E:/Translate/work_gutenberg/nachsommer/out/c017/c04/final.txt'

EDITS = [
    ('他说：‘再说一遍，欢迎你到我家来。', '他说：“再说一遍，欢迎你到我家来。'),
    ('别的事上也都如此。’', '别的事上也都如此。”'),
    ('‘你这样的厚意，叫我十分惶恐，’我答道，‘我如今才看出来',
     '“你这样的厚意，叫我十分惶恐，”我答道，“我如今才看出来'),
    ('哪怕只胜任一分半分。’', '哪怕只胜任一分半分。”'),
    ('‘要胜任，也许并不难，’他回答说。', '“要胜任，也许并不难，”他回答说。'),
    ('‘可要是偏偏不胜任呢？’我问。', '“可要是偏偏不胜任呢？”我问。'),
    ('‘那我们便直说，把话向你说明白，好叫事情有个办法，’他答道。',
     '“那我们便直说，把话向你说明白，好叫事情有个办法，”他答道。'),
    ('‘这话叫我心里轻省多了，’我答道，‘因为这样一来',
     '“这话叫我心里轻省多了，”我答道，“因为这样一来'),
    ('第二户人家，我也忘不了。’', '第二户人家，我也忘不了。”'),
    ('‘也许我们这一户也会叫你忘不了，’他说，‘现在且叫人领你看看房子',
     '“也许我们这一户也会叫你忘不了，”他说，“现在且叫人领你看看房子'),
    ('也不必敲我的门。’', '也不必敲我的门。”'),
]

with open(PATH, encoding='utf-8', newline='') as fh:
    text = fh.read()
lines0 = text.split('\n')
n0, b0 = len(lines0), sum(1 for x in lines0 if x.strip() == '')
bak = PATH + '.bak_20261125'
if not os.path.exists(bak):
    shutil.copy2(PATH, bak)

q_before = (text.count('“'), text.count('”'), text.count('‘'), text.count('’'))
for old, new in EDITS:
    assert text.count(old) == 1, ('not unique', old, text.count(old))
    text = text.replace(old, new)

lines1 = text.split('\n')
assert len(lines1) == n0 and sum(1 for x in lines1 if x.strip() == '') == b0
q_after = (text.count('“'), text.count('”'), text.count('‘'), text.count('’'))
print('quotes before', q_before, 'after', q_after)
assert q_after[0] == q_after[1] and q_after[2] == q_after[3]

with open(PATH, 'w', encoding='utf-8', newline='') as fh:
    fh.write(text)
print('p12c done, edits:', len(EDITS))
ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse OK')