# -*- coding: utf-8 -*-
"""《浮士德》第一部 润色落盘 c001/c10 + c001/c18（2026-11-26 逐片轮）
落盘方式：定位唯一子串 -> 替换 -> 断言全文命中数 == 1；段数/行数/空行结构不变。
诗行逐行保留，不并合、不拆行。
"""
import ast
import os
import shutil
import sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'c001')
STAMP = 'final.txt.bak_20261126'

EDITS = {
    # ================= c10：奥尔巴赫地窖收尾 / 女巫的厨房 =================
    'c10': [
        # ⑥ 「die Pfropfen gleich zu machen」是马上把塞子做出来，原译「把塞子封上」把做塞读成封孔
        ('弄点蜡来，把塞子封上！', '弄点蜡来，马上把塞子做好！'),
        # ⑥ 「mag keinen Franzen leiden」= 受不了法国佬，原译加「也许」把断言弱化成猜测
        ('一个真正的德国人也许受不了法国佬', '一个真正的德国人受不了法国佬'),
        # ⑥ 场上饮酒的是弗罗施、布兰德、西贝尔、阿尔特迈尔四人，「两人」数错
        ('（两人频频举杯。）', '（众人频频举杯。）'),
        # ⑥ 「Laß Er uns das zum zweiten Male bleiben」= 让他别再来第二次，原译「再试一回」否定反转
        ('弗罗施：让他再试一回！', '弗罗施：让他别再给我们来这一套！'),
        # ⑥ vogelfrei 是「不受法律保护、人人得而诛之」，非「野鸟」
        ('这家伙是只野鸟！', '这家伙人人得而诛之！'),
        # ⑥ 旁观的是全体伙计（前文「他们拔出刀」），「二人」数错
        ('（二人愕然伫立，面面相觑。）', '（众人愕然伫立，面面相觑。）'),
        # ⑦ 括注缺右括号，与全册体例不合（原文本身在此断句，括号仍需闭合）
        ('（他与浮士德一同消失，众伙计四散分开。',
         '（他与浮士德一同消失，众伙计四散分开。）'),
        # ① 「能把…从我身上弄掉」两个「我」叠架，且「弄掉三十年」搭配不伦
        ('能把我这三十年从我身上弄掉？', '能把我这三十年从身上除掉？'),
        # ⑥ 「Beim Schmause, / Aus dem Haus / Zum Schornstein hinaus!」＝赴宴去了，出了屋子，
        #    从烟囱里钻出去；原译读成「出了『烟囱之家』」把烟囱当成客栈名。
        #    注：该段在上游被复制成两行（第 156/157 行），红线不许改行数，故两行同步改。
        ('动物：赴宴去，出了“烟囱之家”！\n赴宴去，出了“烟囱之家”！',
         '动物：赴宴去了，出了屋子，从烟囱里钻出去！\n赴宴去了，出了屋子，从烟囱里钻出去！'),
        # ⑥ schwärmen 指在外游荡，非「胡思乱想」
        ('她这样胡思乱想，通常要持续多久？', '她这样在外游荡，通常要多久？'),
        # ⑥ breite Bettelsuppen 是稀薄的乞丐汤，「用来施舍」为增义
        ('我们在煮稀汤，用来施舍。', '我们在煮稀汤，乞丐喝的那种。'),
        # ⑤ 同片同一只 Kater，前文作「公猿」，此处误作「公猫」（c11 另有「公猫」，跨片归一另记）
        ('公猫（凑上前来，向梅菲斯特献媚）', '公猿（凑上前来，向梅菲斯特献媚）'),
        # ① 「快活得像吃人一样」状语残缺，补足为「像吃了人肉一样」
        ('我们快活得像吃人一样，好比五百头猪！', '我们快活得像吃了人肉一样，好比五百头猪！'),
    ],
    # ================= c18：瓦尔普吉斯之夜 =================
    'c18': [
        # ④ 「不然它会把…」紧接「岩石」，「它」实指狂风（sie = Windsbraut），指代错人
        ('不然它会把你掀下这深渊的墓穴', '不然那狂风会把你掀下这深渊的墓穴'),
        # ⑤ 同一 Baubo 后文作「保姆婆婆」，此处「老妪保姆」语义重复（老妪＝保姆）
        ('一个声音：老妪保姆独自来了，骑一头母猪。', '一个声音：老保姆独自来了，骑一头母猪。'),
        # ⑥ 「Ein tüchtig Schwein und Mutter drauf」是壮猪驮着母亲（Baubo），原译「母猪驮着」反了主客
        ('一头壮猪，母猪驮着，整群女巫随后跟上。', '一头壮猪，这位婆婆骑在上头，整群女巫随后跟上。'),
        # ⑥ HALBHEXE 是「半截女巫」（只露出半身者），非「半队女巫」；「半队」属 HALBER CHOR
        ('半队女巫（低处）：我一路小跑', '半截女巫（低处）：我一路小跑'),
        # ⑥ 「in einem Satz」= 一跃（Satz＝跳），非「一句话」
        ('咱们一句话的工夫就逃出这人群', '咱们一跳就逃出这人群'),
        # ① 「Ich lobt euch, wenn…」是虚拟假设句，原译「我倒赞你们」缺谓语落点、读不通
        ('我倒赞你们待在正中间，被旋舞围着，被青春的喧腾围着；各人守在自己家里，尽够了。',
         '我若看见你们好好待在正中间，被旋舞围着，被青春的喧腾围着，倒要夸你们；'
         '各人守在自己家里，倒也尽够了。'),
        # ① 「证明过…难道没有吗」把陈述＋反问叠成一句，读来断裂
        ('早就向你们证明过，鬼魂从不会规规矩矩地站在脚上，难道没有吗？',
         '不是早就有人向你们证明过，鬼魂从不会规规矩矩地站在脚上吗？'),
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
        assert old in text, f'NOT FOUND [{piece}]: {old[:40]}'
        assert text.count(old) == 1, f'NOT UNIQUE [{piece}]: {old[:40]} ({text.count(old)})'
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
    for piece in ('c10', 'c18'):
        total += run(piece)
    print('total edits:', total)
    return 0


if __name__ == '__main__':
    ast.parse(read(__file__))
    sys.exit(main())