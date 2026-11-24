# -*- coding: utf-8 -*-
"""neuegedichte（里尔克《Neue Gedichte》）c013/c01 逐片润色落盘脚本。

规则：定位唯一子串 → 替换 → 断言命中数 == 1；不整文件重写，段数/行数/换行符不变。
片：work_pub/neuegedichte/out/c013/c01/final.txt（79 段，均为诗行断处，行数不可动）
"""
import ast
import io
import re

P = 'work_pub/neuegedichte/out/c013/c01/final.txt'

EDITS = [
    # (类别, 旧句, 新句, 理由)
    ('⑥',
     '就会知道，他要慢慢数到七十',
     '就会知道，他不过是慢慢地数到七十',
     '德语 nur：只是为了慢慢数到七十才签字；原译吞掉了 nur（限制词）'),
    ('④⑥',
     '只还等着埃里希和乌尔丽克·多罗特娅，她们七岁和十三岁（一六一〇年）死于佛兰德',
     '只还等着埃里希和乌尔丽克·多罗特娅，他们一个七岁、一个十三岁（一六一〇年）死于佛兰德',
     'er/sie 的性别线索德语原文丢失（die 为复数）；埃里希是男孩，不能作「她们」；「七岁和十三岁」易读成两人同龄相加，须分开'),
    ('④',
     '紧挨他身后走着它沉重的丝绸',
     '紧挨他身后走着她的沉重丝绸',
     '德语 ihre Seide 指那面旗（die Fahne）；全诗把旗当作女人（「仿佛举着一个女人」「他不许离开她」），同一指称不能一会儿「它」一会儿「她」'),
    ('⑥',
     '对他有效；因为要这样逃',
     '于他作数；因为要这样逃',
     'gelten＝算数、作数，不是「有效」；「父辈的远方似乎不再于他作数」才是原意'),
    ('⑥',
     '他催他的马，那马大如他的心',
     '他催他的马，要它走得如他的心一样大',
     'groß wie sein Herz 修饰的是 gehn（要它走得气派如他的心），不是马的体量；原译读成了马的大小'),
    ('①③',
     '引向眼睛那无声的危险之上，一种秘密的往来',
     '在眼睛那无声的危险之上引过去——一种秘密的往来',
     'ob der lautlosen Gefahr der Augen hinführen：ob＝在……之上跨过；原译「引向……之上」把「向」错当介词，悬空成半句'),
    ('④',
     '于是海在它们里面升起、落下、变换',
     '于是海在眼睛里升起、落下、变换',
     'in ihnen：上句并提「眼睛」与「运河」，一个「它们」在这里指向不明'),
    ('④⑥',
     '一种秘密的往来把眼睛与运河连接起来，于是海在眼睛里',
     '一种秘密的往来把这两道桥接在运河上，于是海在眼睛里',
     'die ein heimlicher Verkehr an die Kanäle schließt：关系代词 die 指眉毛（桥），是「秘密的往来把桥接到运河上」，原译换成「眼睛」，且丢掉了桥的意象；若照原译，全诗桥—运河的转喻就断了'),
    ('①',
     '一旦看见过我，便羡慕我的狗',
     '谁一旦看见过我，就羡慕我的狗',
     'Wer mich einmal sah：主语被吞，成了缺主语的流水句'),
    ('①③',
     '只为不时向两侧鞠躬的人们显露自己，在斗篷的孤独中——：',
     '只为不时在斗篷的孤独里向两侧鞠躬的人们显露自己——：',
     'sich … zu zeigen in des Mantels Einsamkeit：介宾状语被甩到句末悬空，「在斗篷的孤独中」修饰「显露」'),
    ('①',
     '就这样，独自在栏杆之间升起，那些栏杆自开端以来就在鞠躬，那台阶：缓慢地，蒙上帝恩典，向着天空，又不向任何地方；',
     '就这样，那台阶独自在栏杆之间升起——那些栏杆自开端以来就在鞠躬——缓慢地，蒙上帝恩典，向着天空，又不向任何地方；',
     '主语「那台阶」被插句挤到句末，前半句悬空无主；德语框形可以拖，汉语不能断，用破折号把插入语隔开'),
    ('⑥',
     '甚至连那沉重的裙裾也不许任何人来拖。',
     '甚至连那沉重的裙裾，也不许谁去托起。',
     'tragen＝提、托（替她提裙）；「来拖」把动作读反，裙子不是被拖在地上的'),
    ('③⑥',
     '分给七匹拉车的马，那从未移动的东西便化为步伐；因为那高傲地留在大理石中央，与古老、抵抗和宇宙一同驻留的东西，',
     '那从未移动的东西被分派给七匹拉车的马，便化为步伐；因为那高傲地留在大理石中央、耽于古老、抵抗与万有的东西，',
     'Auf Pferde … verteilt 是被动分词短语前置，原译照搬成悬空的「分给……」；verweilen an＝耽于、流连于（an 不是「与……一同」），All 在此作「万有」'),
    ('⑥',
     '它如何金黄地向他滴落',
     '它如何金黄地从自身滴落',
     'wie es golden von ihm träuft：von ihm＝从它（佛）身上滴下；原译「向他滴落」把方向读反'),
    ('④',
     '因为那不是她们的饮器，也不是她们女人的耳坠。',
     '因为那并不是女人的饮器，也不是她们耳上的坠饰。',
     'das sind nicht ihre Trinkgeschirre und die Ohrgehänge ihrer Fraun：两个 ihre 指同一批女人，原译「她们的……她们女人的」叠出两个不同的「她们」，指代崩了'),
    ('⑤⑥',
     '从古老圆形的云石边缘溢出',
     '从古老圆形的大理石边缘里升起',
     'übersteigend 是「高过、升出」而非「溢出」；云石／大理石全册不一（大理石 3 次为 canon），按 canon 归一'),
    ('③',
     '向它展示天空在绿荫与幽暗之后，像一件未知的东西；',
     '向它展示绿荫与幽暗之后的天空，像一件未知的东西；',
     'ihm Himmel hinter Grün und Dunkel zeigend：介词短语后置直搬，汉语读来「天空在……之后」断裂'),
    ('①',
     '自己在美丽的碗中静静铺展，没有乡愁',
     '它自己在美丽的碗中静静铺展，没有乡愁',
     'sich selber … verbreitend：主语（水）跨行脱落，「自己在……」缺主语'),
    ('⑥',
     '而狮子背上白净地骑着一个男孩',
     '而狮子背上骑着一个白衣男孩',
     'weiß 与上段「一个小蓝衣女孩」（ein kleines blaues Mädchen）对举，指白衣，不是「白净」（面色白）'),
    ('①③',
     '而马匹上她们经过，也有女孩，明亮的，几乎已经长大，超过这马匹的腾跃；',
     '而骑在马上，她们过来了，也有女孩，明亮的，几乎已长过这马匹的腾跃；',
     'Und auf den Pferden kommen sie vorüber：德语状语前置＋倒装，原译「而马匹上她们经过」主谓错位；entwachsen＝长得超过了（不是「长大，超过」两截）'),
    ('①',
     '在近旁围观者的圈子里，她急促、明亮而炽热地，那圆舞开始颤动地铺展开来。',
     '在近旁围观者的圈子里，她的圆舞便急促、明亮而炽热地开始，颤动地铺展开来。',
     'hastig, hell und heiß … beginnt … ihr runder Tanz：状语与主语被拆成两句，前半句「她……地，」悬空；补出「她的圆舞」并让谓语落地'),
    ('①',
     '仿佛你要盲目攀登到的那里，才先是地表',
     '仿佛你要盲目攀登去的地方，才首先是地表',
     'als wäre dort, wohin du blindlings steigst, erst Erdenoberfläche：「……的那里，才先是」是德语关系副词串的直搬，汉语不成句'),
    ('①',
     '那些溪流从黑暗那寻觅的细流中',
     '那些溪流从黑暗中那寻觅着的细流里',
     'aus dem suchenden Gerinn der Dunkelheit：「黑暗那……」的指示词硬插在定语位置，汉语读不通'),
    ('⑥',
     '而随从与仪仗则慢慢在商行行列间',
     '而空虚的随从与仪仗则慢慢在商行行列间',
     'das Gefolge und Geleite der Leere：der Leere（空虚的）是全诗的题眼，原译整段漏掉'),
    ('①',
     '小房子们爬上山墙',
     '那些小房子爬上山墙',
     '汉语「们」不用于无生命物，且此处是拟人句，「小房子们」既破体例又破拟人'),
    ('①⑥',
     '那倒悬的镜影世界便越真实，真实得这些事物从来不曾有过。',
     '那倒悬的镜影世界便越真实——真实到这些事物从来不曾有过的地步。',
     'so wirklich wird, wie diese Dinge nie：wie＝达到……的程度；「真实得这些事物从来不曾有过」把比较读成所属，句子断了'),
]


def main():
    with io.open(P, 'r', encoding='utf-8', newline='') as f:
        text = f.read()
    orig = text

    paras_before = text.count('\r\n\r\n') + 1
    lines_before = text.count('\r\n')
    crlf_before = text.count('\r\n')
    lf_before = text.count('\n')
    cjk_before = len(re.findall(r'[\u4e00-\u9fff]', text))

    for tag, old, new, _why in EDITS:
        n = text.count(old)
        assert n == 1, 'not unique (%d): %s' % (n, old[:40])
        text = text.replace(old, new)

    # 红线校验
    assert text.count('\r\n\r\n') + 1 == paras_before, '段数变了'
    assert text.count('\r\n') == crlf_before, '行数变了'
    assert text.count('\n') == lf_before, '换行符结构变了'
    assert '\r\n\r\n\r\n' not in text, '出现空段'

    with io.open(P, 'w', encoding='utf-8', newline='') as f:
        f.write(text)

    cjk_after = len(re.findall(r'[\u4e00-\u9fff]', text))
    print('改动条数:', len(EDITS))
    print('段数: %d -> %d' % (paras_before, text.count('\r\n\r\n') + 1))
    print('行数(CRLF): %d -> %d' % (lines_before, text.count('\r\n')))
    print('汉字: %d -> %d' % (cjk_before, cjk_after))
    print('字节: %d -> %d' % (len(orig.encode('utf-8')), len(text.encode('utf-8'))))
    print('换行符: CRLF only =', text.count('\n') == text.count('\r\n'))
    for bad in ['"', "'"]:
        assert bad not in text, '有半角引号'
    assert '⟦i⟧' in text and '⟦/i⟧' in text, '斜体锚点丢了'
    print('斜体锚点:', text.count('⟦i⟧'), text.count('⟦/i⟧'))


main()
ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse OK')