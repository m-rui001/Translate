# -*- coding: utf-8 -*-
"""逐段润色落盘：v4 chunk032 / 034 / 035 / 037 / 038（2026-11-26 轮）

铁律：只做「定位唯一子串 → 替换」，每处 assert text.count(old) == 1；
不整文件重写；读写 newline='' 保持原换行符；段数/行数/空行结构不变。
用法：  python _polish_20261126_032_038.py [--dry]
"""
import ast
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'
DRY = '--dry' in sys.argv

# ---------------------------------------------------------------- 改动清单
# (chunk, 类别, old, new, 理由)
EDITS = [
    # ---------------- chunk032 ----------------
    ('chunk032', '③',
     '本比她更有理由抱这种虚无主义，并不只是社交上的，但诚然，某些优点往往更多地帮助人忍受旁人的缺点',
     '本比她更有理由抱这种虚无主义（这种虚无主义并不只是社交上的），但诚然，某些优点往往更多地帮助人忍受旁人的缺点',
     '法语括注 (qui n\'était pas que mondain) 被搬成后置散句，「并不只是社交上的」悬在句末无所属；改回括注。'),
    ('chunk032', '①',
     '至少也是一种才情，一种善于，像译者那样，运用各种句法形式的灵巧才情。',
     '至少也是一种才情，一种灵巧的才情，善于像译者那样运用各种句法形式。',
     '「一种善于，像译者那样，运用……」把「善于……运用」这个动宾拆成两截，句中出不来；改动词句。'),
    ('chunk032', '①④',
     '另一个使西特里侯爵夫人眼见奥丽娅娜跟某某宾客打招呼而郁积的怒火大为减色的原因，是盖尔芒特公爵夫人虽然病势远没有她重，却也显出了那种正在摧毁她的病症的征象。',
     '还有一个原因，也使西特里侯爵夫人眼见奥丽娅娜向某位宾客问好时郁积的怒火减去几分：盖尔芒特公爵夫人的病势虽远没有西特里侯爵夫人那么深，却也已经显出那种正在摧毁她的病症的征象。',
     '「使……怒火大为减色」搭配不成立（ôter quelque valeur à la rage ＝使怒火减几分分量），长定语把中心语「原因」压没；'
     '句末「她」上承「公爵夫人」而实指侯爵夫人，指代打架，改回姓名。'),

    # ---------------- chunk034 ----------------
    ('chunk034', '①',
     '比起我遇见他的那个下午——“总之，不过几小时之前”——在盖尔芒特公爵的书房里，他变得多么厉害啊。',
     '比起我在盖尔芒特公爵的书房里遇见他的那个下午——“总之，不过几小时之前”——他变得多么厉害啊。',
     '「在……书房里」本修饰「遇见」，被括注挤到后面，悬在「他变得」之前成了孤立的处所状语。'),
    ('chunk034', '①',
     '他真的跟亲王闹了一场，就是那场风波把他搅乱了吗？不必这样设想。',
     '他真的跟亲王闹了一场，是那场闹翻把他搅乱了吗？不必这样设想。',
     '原文是两个并列问句（…et qui l\'avait bouleversé ?），「就是那场风波……吗」把第二问读成了第一问的补充说明。'),
    ('chunk034', '③',
     '因为莫莱夫人，眼下正是她得宠，刚走，他完全不知所措了。',
     '因为莫莱夫人（眼下得宠的正是她）刚走，他就完全不知所措了。',
     '原文括注 (car c\'est elle qui tient la corde en ce moment) 被搬成插在主谓之间的逗号散句，把「刚走」与主句隔断。'),
    ('chunk034', '①',
     '那个负责训人的舅舅几乎必然有着和被派去训斥的侄子差不多的缺点。',
     '那个负责训人的舅舅，缺点几乎必然和人家派他去训斥的侄子差不多。',
     '「被派去训斥的侄子」缺施事，读作「侄子被派去训斥」；qu\'on l\'a chargé de gronder 的施事须补出。'),
    ('chunk034', '⑤',
     '所以是你让我姑妈有幸得到我光临她的晚会',
     '所以是你让我舅妈有幸得到我光临她的晚会',
     '圣卢口中「ma tante」（指公爵夫人/亲王妃一系）在 v4 两处作「舅妈」、此处独作「姑妈」，按多数归一；'
     '且公爵夫人是罗贝尔的舅母，非姑母。'),

    # ---------------- chunk035 ----------------
    ('chunk035', '①⑥',
     '这位男爵素来以奥丽娅娜的保护人自居，而且是家族中唯一“由于公爵的遗产、又出于对公爵夫人的嫉妒，往往对公爵的要求过于迁就”的人，唯独他对弟弟的情妇们毫不留情地拒之千里。',
     '这位男爵素来以奥丽娅娜的保护人自居；家族中人“由于公爵的遗产、又出于对公爵夫人的嫉妒，往往对公爵的要求过于迁就”，唯独他对弟弟的情妇们毫不留情地拒之千里。',
     '原文「seul de la famille [trop souvent complaisante…] tenait à distance」：迁就公爵的是「家族」，'
     '唯独男爵拒情妇于千里。原译把「家族中唯一……的人」和被引号括起的「迁就」都挂到男爵身上，正与句意相反。'),
    ('chunk035', '③',
     '因此，絮尔吉夫人要是明白她所惧怕的男爵那副态度的种种缘由，倒也罢了，可她丝毫没料到他如今接待她时态度竟完全相反，其中缘由她又哪里猜得到。',
     '因此，絮尔吉夫人对她所惧怕的男爵那副态度，本来是不难明白其中缘由的；可他如今接待她的态度恰恰相反，个中缘由她却丝毫摸不着头脑。',
     '法语过去虚拟式条件句 (eût-elle fort bien compris…, mais ne soupçonna nullement) 被搬成「要是……倒也罢了」的让步句式，'
     '语义（她本不难明白前者、却完全猜不到后者）被读成一句赌气话。'),
    ('chunk035', '⑤',
     '确确实实就是在那儿以二十法郎接客的。',
     '确确实实就是在那儿以一路易的价钱接客的。',
     '原文 pour un louis；v4 金币单位他处作「金路易」（chunk112「二十五金路易」），此处独作「二十法郎」，按全书用词归一。'),

    # ---------------- chunk037 ----------------
    ('chunk037', '⑥',
     '当他们跟“出身”的人、尤其是跟那些他们想要巴结也巴结得上的、“出身”不如他们的人在一起时',
     '当他们跟“出身”好的人、尤其是跟那些他们想要巴结也巴结得上的、“出身”不如他们的人在一起时',
     '« gens “nés” » 指「出身好的人」；漏一「好」字，「跟“出身”的人」不成语，且与下文「“出身」不如他们」相抵。'),
    ('chunk037', '⑥',
     '不屑于德·夏尔吕先生让她产生的那些恶感',
     '不屑于她在德·夏尔吕先生身上引起的那些恶感',
     '« les mauvais sentiments qu\'elle inspirait à M. de Charlus » ＝她引起男爵的恶感；原译主客颠倒，成了男爵令她生厌。'),

    # ---------------- chunk038 ----------------
    ('chunk038', '③',
     '不管怎样，我宁愿找个舒服点的地方解决，也不愿在那位夫人家里，如果我没记错，我初入社交界那会儿她正在庆祝百岁寿辰呢，就是说，不在她家。',
     '不管怎样，我宁愿找个比那位夫人家更舒服的地方解决——如果我没记错，我刚出入社交界那会儿她已经在庆祝百岁寿辰了——就是说，不在她家。',
     '« plus confortable que chez une personne qui, si j\'ai bonne mémoire, … » 的关系从句被搬成主语后的逗号散句，'
     '「也不愿在那位夫人家里」后面接不住，句尾「就是说，不在她家」更成了悬空补语。'),
    ('chunk038', '⑥',
     '那粪坑会膨胀成一辆骇人的吸粪车。',
     '那粪坑会膨胀成一只骇人的大粪桶。',
     '« tonneau de vidange » 是泔水（粪）桶，量词用「只」；原译错成「吸粪车」。'),
    ('chunk038', '①⑥',
     '这含糊其辞摆得又傻气又小家子气，活像个裁缝，德·夏尔吕先生也不怕冒犯絮尔吉夫人',
     '这份含糊其辞，傻气得像个风雅票友，小家子气得像个女裁缝，德·夏尔吕先生也不怕冒犯絮尔吉夫人',
     '« si bêtement dilettante et si mesquinement couturière » 是两个副词性比喻修饰「含糊其辞」本身；'
     '原译「摆得……活像个裁缝」把 couturière 读成对说话人的比喻，且「摆得」无主语。'),
    ('chunk038', '④③',
     '这位只不屑地报以一阵响亮的讥笑，勉强赏了句“晚安”，这句话，仿佛他要等侯爵夫人先打招呼才察觉到她在场，又是一重侮辱。',
     '男爵只不屑地报以一阵响亮的讥笑，勉强赏了句“晚安”——仿佛他要等侯爵夫人先打个招呼才察觉到她在场——这又是一重侮辱。',
     '上句主语是圣厄韦尔特夫人，「这位」易误指；「这句话，仿佛……，又是一重侮辱」把从句夹在两个逗号之间，主句读断，改用破折号。'),
    ('chunk038', '⑤',
     '“哦！对不起，夏尔吕先生，我希望没撞疼您，”',
     '“哦！对不起，德·夏尔吕先生，我希望没撞疼您，”',
     '呼语 monsieur de Charlus；v4 称谓一律作「德·夏尔吕先生」（88 处），此处脱「德」。'),
]

CHUNKS = ['chunk032', 'chunk034', 'chunk035', 'chunk037', 'chunk038']


def cjk(t):
    return sum(1 for ch in t if '\u4e00' <= ch <= '\u9fff')


def main():
    by_chunk = {c: [] for c in CHUNKS}
    for e in EDITS:
        by_chunk[e[0]].append(e)

    total = 0
    for c in CHUNKS:
        d = os.path.join(BASE, c)
        f = os.path.join(d, 'final.txt')
        b = os.path.join(d, BAK)
        with open(f, encoding='utf-8', newline='') as fh:
            text = fh.read()
        orig = text
        nl = 'CRLF' if '\r\n' in text else 'LF'
        n_old = len([x for x in text.split('\n') if x.strip()])
        hz_old = cjk(text)

        if not os.path.exists(b):
            if not DRY:
                shutil.copyfile(f, b)
                print(f'{c}: backup created -> {BAK}')
        else:
            print(f'{c}: backup exists, NOT overwritten')

        n = 0
        for _, cat, old, new, why in by_chunk[c]:
            assert old in text, f'{c} MISS: {old[:30]}'
            assert text.count(old) == 1, f'{c} NOT UNIQUE ({text.count(old)}): {old[:30]}'
            text = text.replace(old, new)
            n += 1
            print(f'  [{c}] {cat} ok: {why[:34]}…')

        n_new = len([x for x in text.split('\n') if x.strip()])
        assert n_new == n_old, f'{c} 段数变了 {n_old}->{n_new}'
        assert text.count('\n') == orig.count('\n'), f'{c} 行数变了'
        assert ('\r\n' in text) == ('\r\n' in orig)
        assert text.count('“') == text.count('”'), f'{c} 引号不成对'
        assert text.count('“') == orig.count('“'), f'{c} 引号数变了'
        assert text.count('"') == 0, f'{c} ASCII 引号'
        assert text.count('⟦') == orig.count('⟦')

        if not DRY:
            with open(f, 'w', encoding='utf-8', newline='') as fh:
                fh.write(text)
        print(f'{c}: {n} edits | 行 {len(orig.split(chr(10)))}={len(text.split(chr(10)))} '
              f'| 段 {n_old}={n_new} | 汉字 {hz_old}->{cjk(text)} | {nl}')
        total += n
    print(f'TOTAL {total} edits in {len(CHUNKS)} chunks' + (' [DRY]' if DRY else ''))


ast.parse(open(__file__, encoding='utf-8').read())
main()