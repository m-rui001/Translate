# -*- coding: utf-8 -*-
"""润色 work_pub/neuegedichte/out/c013/c00（里尔克《Neue Gedichte》第二部开头一片）。

规则：定位唯一子串 → 替换 → 断言命中数 == 1；不整文件重写，段数/行数/空行/换行符不动。
"""
import ast
import io
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'c013', 'c00', 'final.txt')

# (类别, 旧子串, 新子串)
EDITS = [
    # ⑦ 组序号按全书体例（c002/c003/… 均作「一」「二」「三」）
    ('⑦', '第二部', '二'),

    # ⑥ als wär es keines：keines 指「一只杯子」，不是领属
    ('⑥', '仿佛那并不是他的：', '仿佛它已不是一只杯子：'),

    # ④ seine Kostbarkeiten 指原拥有者，非橱柜
    ('④', '那里头放着它的珍宝', '那里头放着他的珍宝'),

    # ① sie fühlt sich wie Verführung：她觉得自己成了诱惑，原译悬空
    ('①', '她几乎觉得像是一种引诱，当那只', '她几乎觉得自己成了一种诱惑，当那只'),

    # ⑥ trug bis obenhin＝满满担到罐口，非「承受到头」
    ('⑥', '一直承受到头', '一直担得满满的'),

    # ③ 分词短语 verwandelnd und auf andres vorbereitend 修饰 Schleier，原译读成谓语
    ('③', '直到嬉戏正当中，一变而为别样的准备，那第一层白色的面纱，轻轻地滑下来',
     '直到嬉戏正当中，那第一层白色的面纱，变换着、预备着另一样东西，轻轻地滑下来'),

    # ③ zu keinem Dinge hin aus ihrem Gefühle führend＝从感觉里引向任何事物
    ('③', '从自己的感觉里引不出来', '不从自己的感觉引向任何东西'),

    # ⑥ wie es der Zufall brachte＝听凭偶然，非「像偶然领着似的」
    ('⑥', '像偶然领着似的穿过许多房间', '听凭偶然，穿过许多房间'),

    # ① durch jenen Spalt, durch den du hingingst：穿过的是缝隙，不是「地方」
    ('①', '就穿过你从那缝隙走出去的地方，破进了这舞台', '就穿过你走出去的那道缝隙，破进了这舞台'),

    # ⑥ verneuen＝更新、变新鲜；原文「重新新起来」叠字不成词；量词「个」→「把」
    ('⑥', '仿佛在一个花伞里重新新起来', '仿佛在一把花伞里又重新鲜亮起来'),

    # ① man weiß nicht was, ein Etwas, fortgenommen：原译两截悬空
    ('①', '园里所有的绿都少了点什么，一种什么，被拿走了',
     '园里所有的绿里，不知是什么，有一点什么被取走了'),

    # ⑤ Frau Nonnas＝诺娜夫人（c018/c01 目录作「诺娜夫人收藏」为 canon），非修女
    ('⑤', '诺娜修女旧藏', '诺娜夫人旧藏'),

    # ① 两个「地」字状语叠在谓语前，主谓被压断
    ('①', '而镜台上奇怪地陌生地立着那顶黑筒帽，带着骷髅。',
     '而镜台上，那顶带着骷髅的黑筒帽，奇怪而陌生地立着。'),

    # ②「修身的／贵族制服的／装饰性的／绦带」三个「的」压掉中心语
    ('②', '那修身的贵族制服的全副装饰性的绦带', '那修身贵族制服的全副装饰性绦带'),

    # ⑦ 段末「——。」不成标点，改为省略号（trüb--. 为诗中拖曳）
    ('⑦', '且从它自身的深处幽暗地——。', '且从它自身的深处幽暗……'),
]


def main():
    with io.open(P, encoding='utf-8', newline='') as f:
        text = f.read()
    orig = text
    for cls, old, new in EDITS:
        assert text.count(old) == 1, (cls, old, text.count(old))
        text = text.replace(old, new)

    with io.open(P, 'w', encoding='utf-8', newline='') as f:
        f.write(text)

    stat = lambda s: (
        len(s.split('\n')),
        len([x for x in s.split('\n') if x.strip()]),
        s.count('\r\n'),
        sum(1 for ch in s if '\u4e00' <= ch <= '\u9fff'),
    )
    a, b = stat(orig), stat(text)
    print('改动条数:', len(EDITS))
    print('行数 {0[0]} -> {1[0]} | 段数 {0[1]} -> {1[1]} | CRLF {0[2]} -> {1[2]} | 汉字 {0[3]} -> {1[3]}'.format(a, b))
    assert a[0] == b[0] and a[1] == b[1] and a[2] == b[2], '结构被改动！'


main()
ast.parse(io.open(__file__, encoding='utf-8').read())
print('ast.parse OK')