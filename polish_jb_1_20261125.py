# -*- coding: utf-8 -*-
"""《吉姆博》润色 第 1 批：jb_a / jb_b / jb_c"""
import json, io, ast

LOG = []


def load(p):
    with io.open(p, encoding='utf-8', newline='') as f:
        return json.load(f)


def save(p, data):
    with io.open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1).replace('\n', '\r\n') + '\r\n')


def sub(data, old, new, tag, note=''):
    n = sum(x.count(old) for x in data)
    assert n == 1, (tag, n, old[:40])
    for i, x in enumerate(data):
        if old in x:
            data[i] = x.replace(old, new)
            LOG.append((tag, i, note))
            return


def sub_all(data, old, new, expect, tag, note=''):
    n = sum(x.count(old) for x in data)
    assert n == expect, (tag, n, old[:40])
    for i, x in enumerate(data):
        if old in x:
            data[i] = x.replace(old, new)
            LOG.append((tag, i, note))


# ---------------- jb_a ----------------
p = 'jb_a_zh.json'
d = load(p)
n0 = len(d)

sub(d, '*       *       *       *       *', '＊　＊　＊　＊　＊', '⑦', '分节星号行体例统一（全书余处用「＊　＊」全角）')
sub(d, '吉姆博的女家庭教师本该更懂事的', '吉姆博的女教师本该更懂事的',
    '⑤', '职衔归一：governess 全册 123 处作「女教师」，此为少数派')
sub(d, '我们得赶紧给他请个女家庭教师什么的', '我们得赶紧给他请个女教师什么的', '⑤', '职衔归一')
sub(d, '「我们马上请一位明白事理的育儿女教师，」', '「我们马上请一位明白事理的女教师，」', '⑤', '职衔归一；「育儿女教师」非汉语词')
sub_all(d, '守猎人', '猎场看守人', 2, '⑥', '「守猎人」非汉语词，gamekeeper 通译「猎场看守人」')
sub(d, '吉姆博是跌在头上的。', '吉姆博是头朝下摔下来的。', '①⑥', '原文 fallen on his head，「跌在头上」不成话')
sub(d, '而他手里那根官职的权杖——一把脏兮兮的小铲子——给了他极大的威严',
    '而他手里那根代表职权的权杖——一把脏兮兮的小铲子——给了他极大的威严',
    '⑥', 'his wand of office，「官职的权杖」误读为官职所有物')
assert len(d) == n0
save(p, d)
print('jb_a', len(d))

# ---------------- jb_b ----------------
p = 'jb_b_zh.json'
d = load(p)
n0 = len(d)

sub(d, '满怀着一种可怕的的好奇心', '满怀着一种可怕的好奇心', '⑥', '叠字「的的」')
sub(d, '可她不肯告诉他他想知道的，最后他也就不问了',
    '可她不肯说出他想知道的事，最后他也就不问了', '①④', '「他他」两句挤在一处，且指代混')
sub_all(d, '家庭教师', '女教师', 4, '⑤', '职衔归一：governess 作「女教师」（全册 123 处）')
sub(d, '「你的编号是 102。」', '「你的编号是102。」', '⑦', '数字与汉字间不留空格')
sub(d, '为什么他叫 102 号', '为什么他叫102号', '⑦', '同上')
sub_all(d, '「102 是你在那些', '「102是你在那些', 1, '⑦', '同上')
sub(d, '他们一共 101 个', '他们一共101个', '⑦', '同上')
assert len(d) == n0
save(p, d)
print('jb_b', len(d))

# ---------------- jb_c ----------------
p = 'jb_c_zh.json'
d = load(p)
n0 = len(d)

sub(d, '它近得那股风掀起了他额前的头发', '它近得那股扑翅的风都掀起了他额前的头发',
    '①', '「它近得……掀起了」缺关联，主谓断裂')
sub(d, '「昨晚上他大半个时候都在外头——打猎——」', '「昨晚上他大半个晚上都在外头——打猎——」',
    '⑥', '「时候」误用，应是时段')
sub(d, '他发现最好的练习时候是夜里', '他发现最好的练习时间是夜里', '⑥', '同上')
assert len(d) == n0
save(p, d)
print('jb_c', len(d))

for t, i, n in LOG:
    print(t, i, n)
ast.parse(open(__file__, encoding='utf-8').read())
print('AST ok')