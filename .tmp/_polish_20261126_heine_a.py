# -*- coding: utf-8 -*-
"""《新诗集》(neuegedichte) 润色落盘 c001/c00 c002/c00 c003/c00 c004/c00（2026-11-26 逐片轮）

注：本书源文为里尔克 Rainer Maria Rilke《Neue Gedichte》(Insel 1920)，
并非海涅；脚本名沿用分配表所给 `_polish_20261126_heine_a.py`，内容按实际书目处理。

落盘方式：定位唯一子串 -> 替换 -> 断言全文命中数 == 1；段数/行数/空行/换行符不变。
本书诗句在 final.txt 里已按「一节一段」落行，不拆不并。
"""
import ast
import os
import shutil
import sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
STAMP = 'final.txt.bak_20261126'

EDITS = {
    # ============ c001/c00：题献 / 早年的阿波罗 / 少女的哀诉 / 情歌 / 埃拉娜组诗 ============
    'c001/c00': [
        # ① 「in Freundschaft」＝以友谊（献给），原译「谨志友谊」无动词落点，中文不成句
        ('卡尔与伊丽莎白·冯·德·海特谨志友谊',
         '以友谊献给卡尔与伊丽莎白·冯·德·海特'),
        # ① 「没有什么能阻挡…光辉几乎致命地击中我们」缺「使…不…」的挂靠，句子断裂
        ('他的头颅里也这般，没有什么能阻挡一切诗篇的光辉几乎致命地击中我们；',
         '，他的头颅里也这般：没有什么能拦住一切诗篇的光辉，使它不几乎致命地击中我们；'),
        # ③ 「meines」＝我自身的一切，原译「我的什么」是逐字直搬
        ('我的什么，不再安慰我、理解我，一如童年时么？',
         '我自身的一切，不再像童年时那样安慰我、理解我了么？'),
        # ③ 德语框形／从句后置照搬：「wenn…」的时间从句被甩到句末，主语与谓语隔了整段
        ('忽然我像被放逐了，而这孤独于我变成一种过大之物，当我站在我胸脯的丘陵上，'
         '我的感情呼喊着要翅膀，或者要一个终结。',
         '忽然我像被放逐了；当我站在自己胸脯的丘陵上，我的感情呼喊着要翅膀，'
         '或者要一个终结，这孤独于我变成一种过大之物。'),
        # ① 「一切触动我们、你与我的」同位语夹在定语中，读不通
        ('然而一切触动我们、你与我的，都把我们合在一起',
         '然而凡触动我们两个的，都把我们合在一起'),
        # ③ 「wenn…」从句后置直搬，问句主干被推到从句之后
        ('那么你究竟有什么要对我说，你又与我灵魂何干，当你的眼睛在近前的未说者面前垂下去？男人，',
         '当你的眼睛在近前的未说者面前垂下，你究竟有什么要对我说，你又与我的灵魂何干？男人，'),
        # ① 「das Sagen dieser Dinge」是「讲述这些事情」，原译「说这些事情曾把我们席卷」主谓挤作一团
        ('看哪，说这些事情曾把我们席卷而去，直至声名之中。',
         '看哪，讲述这些事情，曾把我们席卷而去，直到声名之中。'),
        # ① 同位语三层套叠（那少女气，我，知者，与…知者），中心语被压没
        ('那少女气，我，知者，与那些同我一样的知者，受神看护，未受触碰地带着它',
         '那少女气，我们——我，知者，以及与我同为知者的她们——受神的看护，未受触碰地带着它'),
        # ① 呼语「求婚者，垂着面容」悬在句尾，与「你没有挑选」错位
        ('是啊，也因这胸脯，你没有像挑选果实花环那样挑选它们，求婚者，垂着面容。',
         '是啊，也因这胸脯，垂着面容的求婚者，你没有把它们像挑选果实花环那样挑走。'),
        # ⑥ 「der Verwöhnende der Fraun」＝惯宠女人的那一位，「娇养妇女」搭配不伦
        ('那娇养妇女者', '那娇宠女人的'),
        # ③ 「seitdem ich dich erkenn」从句后置，主句被劈成两半
        ('啊，我的身体从每一条血脉里怎样更芬芳地开花，自从我认识了你；',
         '啊，自从我认识了你，我的身体怎样从每一条血脉里更芬芳地开花；'),
        # ① 「它于我们不骇人地陌生么」两个状语叠架，读不通
        ('它于我们不骇人地陌生么？', '它不是可怕地令我们感到陌生么？'),
        # ① 「外面那缓慢开始的、被称作白昼的」中心语缺失
        ('外面那缓慢开始的、被称作白昼的，于我们难道比它更可理解么？',
         '外面那缓慢开始、被称作白昼的东西，难道比它更可理解么？'),
        # ③ 「sich zücken」是抽身、拔出，原译「被抽出」硬搬被动
        ('它却能从你身上、从我身上被抽出', '它却能从你身上、从我身上抽身而去'),
    ],
    # ============ c002/c00：亚比煞（I） ============
    'c002/c00': [
        # ① 「缚在枯萎者的周围」方位介宾不成立（um ihn gebunden＝环缚在他身上）
        ('她那稚弱的双臂被仆人们缚在枯萎者的周围',
         '她那稚弱的双臂被仆人缚在那枯萎者的身上'),
    ],
    # ============ c003/c00：亚比煞（II） ============
    'c003/c00': [
        # ⑤ 组序号体例：全书 8 处作「一/二/三」，唯此处作「第二」
        ('第二\r\n\r\n那君王坐着', '二\r\n\r\n那君王坐着'),
        # ⑥ 脱字：「leerer Tag」＝白白过去的一天，「白过去」不成词
        ('思量着白过去的一天里做下的事', '思量着白白过去的一天里做下的事'),
    ],
    # ============ c004/c00：大卫在扫罗面前歌唱 ============
    'c004/c00': [
        # ① 「还有那些…人，啊，那些躯体」两个宾语叠在一起；「造物之力」亦非 Schaffen（创造）本义
        ('还有那些因你的造物之力而衰颓的人，啊，那些躯体曾是何等美。',
         '而那些被你的创造耗弱了的人——啊，所有躯体曾是何等美。'),
    ],
}


def read(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()


def write(p, t):
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(t)


def cjk(t):
    return sum(1 for ch in t if '\u4e00' <= ch <= '\u9fff')


def run(piece):
    d = os.path.join(BASE, piece)
    f = os.path.join(d, 'final.txt')
    b = os.path.join(d, STAMP)
    if not os.path.exists(b):
        shutil.copy2(f, b)
        print('backup made:', b)
    else:
        print('backup exists, not overwritten:', b)
    text = read(f)
    before = {
        'paras': len([x for x in text.split('\n') if x.strip()]),
        'lines': len(text.split('\n')),
        'cjk': cjk(text),
        'crlf': text.count('\r\n'),
    }
    n = 0
    for old, new in EDITS[piece]:
        assert old in text, f'NOT FOUND [{piece}]: {old[:36]}'
        assert text.count(old) == 1, f'NOT UNIQUE [{piece}]: {old[:36]} ({text.count(old)})'
        text = text.replace(old, new)
        n += 1
    after = {
        'paras': len([x for x in text.split('\n') if x.strip()]),
        'lines': len(text.split('\n')),
        'cjk': cjk(text),
        'crlf': text.count('\r\n'),
    }
    assert before['paras'] == after['paras'], f'{piece} paras {before["paras"]}->{after["paras"]}'
    assert before['lines'] == after['lines'], f'{piece} lines {before["lines"]}->{after["lines"]}'
    assert before['crlf'] == after['crlf'], f'{piece} crlf changed'
    write(f, text)
    print(f'{piece}: edits={n} paras={before["paras"]}=={after["paras"]} '
          f'lines={before["lines"]}=={after["lines"]} '
          f'cjk={before["cjk"]}->{after["cjk"]} crlf={after["crlf"]}')
    return n


def main():
    total = 0
    for piece in ('c001/c00', 'c002/c00', 'c003/c00', 'c004/c00'):
        total += run(piece)
    print('total edits:', total)
    return 0


if __name__ == '__main__':
    ast.parse(read(__file__))
    sys.exit(main())