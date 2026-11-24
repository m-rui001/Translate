# -*- coding: utf-8 -*-
"""prozess c002/c01, c002/c02, c002/c05, c004/c02 逐段润色（2026-11-26）
只做「定位唯一子串 → 替换」，段数/段序/空行结构不动。
"""
import ast
import io

BASE = 'work_pub/prozess/out'

EDITS = {
    'c002/c01': [
        # ⑤ 术语：本片「身份证件」4 处 vs「身份证明」1 处，归一到 canon
        ('可偏偏他急着要找的那些身份证明',
         '可偏偏他急着要找的那些身份证件'),
        # ① 悬空/缺主语：Man sah sie nur einen Augenblick, denn …
        ('只看得见她一眨眼的工夫，因为她一认出是K.，显然就窘了',
         '只看得见她一眨眼的工夫：她认出是K.，显然就窘了'),
        # ① 定语套定语，句子读断：sein Frühstück verzehrten（wie K. jetzt erkannte）
        ('正吃着K.这才看清的他的早饭。',
         '正吃着他的早饭——他这会儿才看清。'),
        # ⑥ 词义误读：sich in Ihre Lage nicht fügen können＝不肯安于处境，非「认不得」
        ('“您就认不得自己的处境，看样子还存心要白白地招惹我们',
         '“您就是不肯安于自己的处境，看样子还存心要白白地招惹我们'),
        # ③ 德语定语串（bedeutungsvollen, aber unverständlichen Blick）照搬成状语串
        ('而是意味深长地、——大概如此——叫人看不懂地，久久望着K.。',
         '而是用一道长长的目光望着K.，这目光大概是意味深长的，却又叫人看不懂。'),
        # ① 搭配不成话：Zwiegespräch der Blicke＝用目光交谈
        ('K.不由自主地跟弗朗茨对起眼来',
         'K.不由自主地跟弗朗茨用目光交谈起来'),
        # ① 「只…地」不成句，补判断词
        ('可看守只不客气地说：',
         '可看守却只是不客气地说：'),
        # ① 插入语悬空（es zu sein 落在半句上）：补出指代内容
        ('——他们自己都承认是——用这种废话',
         '——这一点他们自己也承认——用这种废话'),
        # ① 比况从句悬空（unvergleichlich klarer als die längsten Reden mit diesen）
        ('我只要跟我地位相当的人说上几句话，一切就会比跟这些人谈上老半天清楚得没法比。',
         '我只要跟一个和我地位相当的人说上几句话，一切就会清楚得没法比，跟这些人谈上老半天也及不上。'),
        # ⑤ 专物一致：Wandschrank 本册作「壁橱」，此处「小柜子」易与床头柜混
        ('他怎样走到一个小柜子跟前',
         '他怎样走到一个小壁橱跟前'),
        # ⑥ 同义重复「以防万一，免得万一」
        ('——这后一杯只是以防万一，免得万一用得着。',
         '——这后一杯只是出于谨慎，以防那未必会有的万一。'),
    ],
    'c002/c02': [
        # ⑥⑦ 敬称体例：Der Aufseher ruft Sie，同一场面看守一律称「您」；且说话人不明
        ('“监察官在叫你。”那人说道。',
         '“监察官在叫您。”有人说道。'),
        # ① 「带兵气十足」不成话（militärisches Schreien）
        ('这短促、断续、带兵气十足的吆喝',
         '这短促、断续、十足军人气的吆喝'),
        # ⑥ 敬称一致（Was fällt Euch ein?）
        ('“你这是想干什么？”他们喊道',
         '“您这是想干什么？”他们喊道'),
        # ⑥ 敬称一致，并补出 durchprügeln 的使劲义
        ('他会叫人抽你一顿，连我们一块儿挨。',
         '他会叫人把您抽一顿，连我们一块儿挨。'),
        # ① knapp vor Willem 译成「紧走在…前头」不成立
        ('他穿戴完毕，就得紧走在威廉前头，穿过空荡荡的邻室',
         '他穿戴完毕，就得贴着威廉走在前面，穿过空荡荡的邻室'),
        # ① 主谓插入打断（Dieses Zimmer wurde, wie K. genau wußte, …@）
        ('这间屋子，K.清楚知道，近来住着一位布尔斯特纳小姐',
         'K.清楚知道，这间屋子近来住着一位布尔斯特纳小姐'),
        # ① ihre Gesellschaft vergrößert＝又添了人，「壮大」误用于人数
        ('不过他们那一伙壮大了',
         '不过他们那一伙又添了人'),
        # ① 双重弱化词叠用「并不怎么十分」
        ('“不错，我是吃惊，可也并不怎么十分吃惊。”',
         '“不错，我是吃惊，可也并不特别吃惊。”'),
        # ① 同上，回声句一并归一（Nicht sehr überrascht?）
        ('“不怎么十分吃惊？”监察官问',
         '“不特别吃惊？”监察官问'),
        # ⑥ 词义误读：nicht üblich＝没有这个规矩，非「不常有」
        ('“这不常有的。”监察官回答。',
         '“这儿不兴这个。”监察官回答。'),
        # ⑥ 「为此」误作因果连词（dafür scheinen mir … zu umfangreich）
        ('为此我觉得所布置的这一切毕竟太铺张了',
         '因为我觉得所布置的这一切毕竟太铺张了'),
        # ① 缺谓语「有」：es müßten alle Mitglieder … beteiligt sein
        ('那就得公寓里全体人员都参与其事',
         '那就得有公寓里全体人员参与其事'),
        # ⑥ 数误读：Sind Sie Beamte? 为复数
        ('您是官员吗？谁也没穿制服',
         '您几位是官员吗？谁也没穿制服'),
        # ① 「反倒」无对照；es stört 直陈即可
        ('这反倒破坏了您本来给人留下的不算坏的印象',
         '这会搅坏您本来给人留下的不算坏的印象'),
        # ① 主谓失配：能让人看出来的是「举动」，不是「您说的话」
        ('其实只要说上三言两语，您的举动也就能让人看出来了',
         '其实只要说上三言两语，剩下的别人从您的举动里也看得出来'),
        # ⑥ 词义误读：nichts für Sie übermäßig Günstiges＝并无特别的好处
        ('此外，这些话对您也并无过分的好处。',
         '此外，这些话对您也并没有什么特别的好处。'),
    ],
    'c002/c05': [
        # ① 「但凡看得见的」主语悬空（Soviel man sehen konnte）
        ('但凡看得见的，确实都各归其位',
         '凡能看见的地方，一切确实都各归其位'),
        # ⑤ 同词异译：Pension 本册 canon「公寓」（4 处）vs「宅子」（2 处）
        ('谁家招房客不想把宅子保持得清清白白呢',
         '谁家招房客不想把公寓保持得清清白白呢'),
        ('您要真想把这宅子保持得清清白白',
         '您要真想把这公寓保持得清清白白'),
        # ⑥ 语义反转：die Tür ein wenig geöffnet＝门开了一条缝，非「掩上」
        ('只把通前厅的门稍稍掩上',
         '只把通前厅的门开了一条缝'),
    ],
    'c004/c02': [
        # ⑥ 名物误：Vollbart＝满脸大胡子，与「一撮」「络腮」自相矛盾
        ('正靠一撮稀疏发红的络腮胡子给自己添几分威严',
         '正靠一脸稀疏发红的大胡子给自己添几分威严'),
        # ① 同义重复＋主语错位（der erste Student der unbekannten Rechtswissenschaft）
        ('这毕竟是他头一回碰上的一个法律界生人，算起来还是他与人打交道时遇上的头一个，一个说不定将来也会爬上高位去的家伙。',
         '这毕竟是他头一回跟这门陌生法学的学生当面打交道，一个说不定将来也会爬上高位去的家伙。'),
        # ① 破折号插入后主语掉线（「说道」的主语是学生）
        ('所以学生开口的时候，他并不觉得不受用——那学生显然是被K.的踱步搅扰了，那脚步有一阵已经变成了跺脚——说道：“您要是不耐烦',
         '因此学生一开口，他倒觉得正合心意——那学生显然是被K.的踱步搅扰了，那脚步有一阵已经变成了跺脚——学生说：“您要是不耐烦'),
        # ⑥ 硬伤：「架走」为错字/误词（Entführung＝绑走、劫走）
        ('想表示这场架走跟她不相干',
         '想表示这场绑架跟她无关'),
    ],
}

TOTAL = 0
for piece, pairs in EDITS.items():
    path = f'{BASE}/{piece}/final.txt'
    with open(path, encoding='utf-8', newline='') as f:
        text = f.read()
    before_paras = len([x for x in text.split('\n\n') if x.strip()])
    before_lines = text.count('\n')
    before_han = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    n = 0
    for old, new in pairs:
        assert old in text, (piece, old)
        assert text.count(old) == 1, (piece, old)
        text = text.replace(old, new, 1)
        n += 1
    after_paras = len([x for x in text.split('\n\n') if x.strip()])
    after_lines = text.count('\n')
    after_han = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    assert before_paras == after_paras, (piece, before_paras, after_paras)
    assert before_lines == after_lines, (piece, before_lines, after_lines)
    assert '\r' not in text
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    TOTAL += n
    print(f'{piece}: 改动 {n} 条 | 段数 {before_paras}->{after_paras} | '
          f'行数 {before_lines}->{after_lines} | 汉字 {before_han}->{after_han} | 换行符 LF')

print('总改动', TOTAL, '条')
ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse OK')