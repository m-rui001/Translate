# -*- coding: utf-8 -*-
"""malte c004 六片（c25 c26 c29 c30 c31 c32）逐片润色落盘脚本。

铁律：只「定位唯一子串 → 替换 → 断言命中数 == 1」，不整文件重写；
每片改完立即落盘；段数/行数/空行结构/换行符不变。
用法：python work_pub/malte/_polish_20261126_malte_c.py [c25 c26 ...]
"""
import ast
import os
import sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'c004')

# (类别, old, new, 理由)
EDITS = {
    'c25': [
        ('①', '民众见了这时，心里喜欢',
         '民众见了这般情景，心里喜欢',
         '「见了这时」不成话，缺中心语；de «des Anblicks» = 见了这等景象'),
        ('③④', '只为容让上帝在他身上越过他行事，在他那迟来的不耐中。',
         '只为容让上帝凭着他那迟来的不耐，从他身上越过去行事。',
         'de «Gott über ihn weg handelte in seiner späten Ungeduld» 的框形状语被搬到句末，「他那」承接不清；'
         '把 «in seiner späten Ungeduld» 归给上帝并前置'),
        ('①', '这一桩，人们早已当作他荣耀的开端印在他心里。',
         '这一桩，人们早已当作他荣耀的开端，刻进他心里。',
         'de «Dies hatte man ihm eingeprägt als den Anfang seines Ruhms»：「当作…印在」两动词挤在一个宾语上，断句'),
        ('⑥', '到那圣母受难兄弟会去看那些秘仪',
         '到那受难兄弟会去看那些秘仪',
         'de «Passionsbrüderschaft» = 基督受难兄弟会，译稿多出「圣母」二字'),
        ('①', '比国王这安定了的形象更完美的了',
         '比国王这副安定的形象更完美的了',
         '「这安定了的形象」定语与助词相撞，改用「这副」+ 形容词作定语'),
        ('①③', '就像他站在卢浮宫一扇高窗之下，肩背的弧线垂落其下。',
         '就像他站在卢浮宫一扇高窗里，肩背的弧线沉沉垂下。',
         'de «in einem der hohen Fenster … stand unter dem Sturz ihrer Schultern»：是「站在窗中」，'
         '「垂落其下」的「其」无先行语，悬空'),
        ('⑥', '被辽阔的表情所合拢',
         '被那辽阔的神情所封住',
         'de «zugehalten vom Ausdruck der Weiten»：«zuhalten» 是「堵住、封住」，非「合拢」'),
        ('⑥', '它们起初合拢，正如一个吃奶婴儿的颅骨',
         '它们要到后来才合拢，正如吃奶婴儿的颅骨',
         'de «die sich erst schlossen»：«erst» = 直到后来才，译稿读成「起初」，时态反转'),
        ('①', '他在桌子边上那边设起罗马',
         '他在桌子那一头的边上设起罗马',
         '「边上那边」叠床架屋；de «drüben am Rande des Tisches» = 桌子那头的边缘'),
        ('⑥', '记忆便复述起那座高高的赫尔墨斯宫殿',
         '记忆便复述起那座高耸封闭的宫殿',
         'de «den hohen hermetischen Palast»：«hermetisch» = 封闭幽闭的，非神名「赫尔墨斯」'),
    ],
    'c26': [
        ('③⑥', '他还被那些穿透蜡像的长针刺伤了自己。',
         '他还在那些穿透蜡像的长针上划伤了自己。',
         'de «er ritzte sich an den langen Nadeln»：主动反身 + «ritzen»=划伤，「被…刺伤了自己」被动反身混用'),
        ('①', '接连数日，他不发出一举一动，',
         '接连数日，他没有一点举动，',
         'de «ging keine Aktion von ihm aus»；「不发出…举动」动宾失配'),
        ('⑥', '他年纪很大，我甚至觉得，他必定因其身高而引人注目。',
         '他个子很高，我甚至觉得，他必定因这身高而引人注目。',
         'de «Er war sehr groß … durch seine Größe»：通篇说身量，译成「年纪很大」与下半句「身高」自相矛盾'),
    ],
    'c29': [
        ('①', '合上眼覆在一行重读过的字句上',
         '合上眼睛，俯就一行重读过的字句',
         'de «er schließt die Augen über einer wiedergelesenen Zeile»；「合上眼覆在…上」动宾纠缠'),
        ('⑦', '以其——可以说是——足数的显形',
         '以其堪称全数的显形',
         '插说用双破折号嵌在定语中，读来断气；de «gewissermaßen vollzähligen Versichtbarungen» 收为「堪称全数」'),
        ('①', '想着并且看出时，注意到窗台上有一盘水果',
         '想着，并且看明白时，注意到窗台上有一盘水果',
         'de «denkt und einsieht»；「想着…想着并…」重出且「看出时」悬空，断开'),
        ('①', '为她，他在一个夜里正在逝去的时辰中懂得了爱的要求。',
         '为她，他在一个正在逝去的夜间时辰里懂得了爱的要求。',
         'de «in einer nächtlichen Stunde, die vorübergeht»：关系从句塞在「时辰」前，读作「夜里正在逝去」；'
         '提「夜间」作定语、从句作前置定语'),
        ('①⑦', '为她而想，那位爱人何等有理：倘若她知道',
         '为她而想，并且想：那位爱人何等有理——倘若她知道',
         'de «wie sehr im Recht jene Liebende war» 是 «denken» 的宾语从句，译稿用逗号硬接，主谓断裂；'
         '句内又连用两层冒号，后一层改破折号'),
        ('①', '还有一次，阿贝洛内，在最后那些年里，我感觉到你，并且看透了你，出乎意料，在我久不曾想到你之后。',
         '阿贝洛内，还有一次：在最后那些年里，我感觉到你，并且看透了你——出乎意料，在我久不曾想到你之后。',
         '呼语与三个后置状语串成流水句，主语悬到最后；加冒号、破折号分层'),
        ('①', '每当一位熟稔的邻客把他们短短地、遮掩地转向门口',
         '每当一位熟稔的邻客把他们短促而隐蔽地转向门口',
         'de «kurz und verkappt»：两个副词并列带「地」，改成联合定语'),
        ('①', '不再是新婚夫妇——他们整趟旅行中只彼此说着怨怼的话——也沉入沉默的相安',
         '那些不再是新婚夫妇的人——整趟旅行中只彼此说着怨怼的话——也沉入沉默的相安',
         'de «Nicht mehr neue Eheleute … versinken»：主语是「那些人」，译稿省略中心语致「不再是…也沉入」失主'),
        ('②', '那男人身上袭来他理想的舒适的疲倦',
         '那男人身上袭来一份舒适的疲倦，那是他那些理想带来的',
         'de «die angenehme Müdigkeit seiner Ideale»；三「的」连缀把中心语压没，拆成主句+补充'),
        ('③', '那暗示性的国家，以它贫穷的盐与玻璃',
         '那富于暗示的国家，以它贫穷的盐与玻璃',
         'de «Der suggestive Staat» 直搬形容词；汉语「暗示性的国家」义晦，改「富于暗示的」'),
        ('⑦', '那能量越来越精细地神经化——：这威尼斯。',
         '那能量越来越精细地神经化——这威尼斯。',
         'de «vernervten--:» 的破折号与冒号并置被照搬；汉语「——：」不合体例'),
    ],
    'c30': [
        ('⑥', '我满以为这年轻姑娘会推说自己不会唱、推说在座的人未必有兴致听丹麦歌，以此为辞。',
         '我满以为这年轻姑娘会推说，在座的人未必有兴致听丹麦歌，以此为辞。',
         'de 只说 «sich damit entschuldigen würde, daß niemand … Interesse haben könne»，'
         '「推说自己不会唱」是译稿添加'),
        ('②', '那些劝说者脸上久笑而松弛的皮肉上，已经浮起一层干涩的委屈',
         '那些劝说者被长久的笑弄得松弛的脸上，已经浮起一层干涩的委屈',
         '「脸上…皮肉上」双层定位叠用；de «über die vom langen Lächeln abgespannten Gesichter»'),
        ('⑥', '她的衣裙拂着我',
         '她的衣裙的光照着我',
         'de «Ihr Kleid schien mich an»：«anscheinen» = 照向、映向，非「拂」'),
        ('①④', '我慢慢跟着那一群人走，她随他们去了。',
         '我慢慢跟着那一群人走，她正随那群人走远。',
         'de «mit der sie sich entfernte» 是关系从句；「她随他们去了」易读成「去世」，且与主语「我」错位'),
        ('⑦', '她唱：她唱道：',
         '她唱：',
         'de «Sie sang:» 只一句，译稿重出「她唱：她唱道：」'),
        ('①', '都能俯身倾心，温顺地——被爱着。',
         '都能俯身倾心，温顺顺从，却仍被爱着。',
         'de «nachgiebig, doch geliebt»：破折号把「被爱着」孤立成悬空成分，«doch» 的转折也丢了'),
        ('⑥', '他却偏偏在前厅那紧绷的空中，再一次现出形来',
         '他却偏偏在那紧绷的天堂前庭里，再一次现出形来',
         'de «im spannenden Vorhimmel»：«Vorhimmel» = 天堂的前庭，译作「前厅」丢「天」'),
        ('①', '因为你不断从手里放掉一切证据，证明那最陌生者如何到来。',
         '因为你不断撒手丢掉的，正是那些表明最陌生之物如何到来的证据。',
         'de «alle Beweise dafür, wie das Fremdeste, aus den Händen läßt»：「证据，证明…」后置定语断裂'),
        ('⑦', '或者是一缕不留残余的芬芳。',
         '或者是一缕不留残余的芬芳。”',
         '诗分两节各为一引，第一节到末行未收引号，全片 6/5 不配；补收引号'),
    ],
    'c31': [
        ('①', '那些狗，一整天里期待在它们身上越长越大',
         '那些狗，身上的期待长了整整一天',
         'de «in denen die Erwartung den ganzen Tag angewachsen war»：「期待在它们身上越长越大」主语宾语倒错'),
        ('①', '他们倒好，他们躲在暗处，单单落在他一个人身上，随着灯光，落下来的是全部羞耻——长着一张脸。',
         '他们倒好，他们待在暗处；而随着灯光，单单落在他一人身上的，是全部的羞耻——长着一张脸。',
         'de «auf ihn allein fällt, mit dem Licht, alle Schande»：译稿先出「落在他身上」再出「落下来的是」，主谓重出'),
        ('①', '他会放弃去成为那可能伤害他家里那些只剩一颗衰弱的心的人的东西吗？',
         '他会放弃成为那个可能伤害他家里那些只剩一颗衰弱的心的人的东西吗？',
         '「放弃去成为那…的东西」结构绕；de «Wird er es aufgeben, das zu werden, was … schaden könnte»'),
        ('⑤⑥', '可是一个肯让步的情人，还远不是一个爱着的人。',
         '可是一个肯让步的被爱者，还远不是一个爱着的人。',
         'de «eine Geliebte, die nachgiebt, ist noch lang keine Liebende»：全段「爱者／被爱者」对立，'
         '此处译作「情人」破坏术语系统'),
        ('⑦', '和他那巨硕夜晚的整个浩渺空间。',
         '和他那巨硕夜晚的整个浩渺空间？',
         'de «Welche Kunst ist weit genug, …?» 是问句，译稿段末用句号'),
        ('①', '那就是这样一个时期，它以他感到自己变得普通、无名，像一个迟疑的康复者开始。',
         '那就是这样一个时期，它这样开始：他感到自己变得普通、无名，像一个迟疑的康复者。',
         'de «die damit begann, daß er sich … fühlte»：「以他感到…开始」把从句塞进介词宾语，读不通'),
        ('②', '在阿利斯康那片住惯了灵魂的阴影里',
         '在阿利斯康那片灵魂惯居的阴影里',
         'de «im seelengewohnten Schatten»；「住惯了灵魂的阴影」定语重出，改「灵魂惯居的」'),
        ('①', '可他那颗心不成其为别的什么的力量又涨起来，再一次临到他身上。',
         '可他心中那不断增长的、不得不如此的力量又涨起来，再一次临到他身上。',
         'de «das anwachsende Nichtanderskönnen seines Herzens»：「不成其为别的什么的力量」不成话'),
        ('②', '他整个在长久独处中变得有预感而不可动摇的本性向他保证',
         '他在长久独处中变得满是预感、不可动摇的整个本性向他保证',
         'de «Sein ganzes, im langen Alleinsein ahnend und unbeirrbar gewordenes Wesen»：'
         '「整个在…中变得…的本性」定语链把中心语压没'),
        ('①', '他觉得自己要朝空间里向他扑去',
         '他觉得自己要朝空间中的他扑过去',
         'de «sich auf ihn zuzuwerfen in den Raum»；「朝…向他」两个方向介词叠用'),
        ('③', '却被人指给他看：至今他自以为做出的一切爱',
         '却有人指给他看：至今他自以为做出的一切爱',
         'de «wurde ihm gezeigt» 的被动直搬；汉语「被人指给他看」主客纠缠'),
    ],
    'c32': [
        ('⑥', '她们照自己的方式解释他的激烈，一面按自己的方式加以曲解。',
         '她们照自己的方式解释他的激烈，因为她们原谅了他。',
         'de «indem sie verziehen»：«verziehen» = 原谅（«verzeihen» 同源），译稿读作「曲解」'),
    ],
}


def apply(piece):
    path = os.path.join(BASE, piece, 'final.txt')
    with open(path, encoding='utf-8', newline='') as f:
        text = f.read()
    before_lines = text.replace('\r\n', '\n').count('\n')
    before_paras = len([x for x in text.replace('\r\n', '\n').split('\n') if x.strip()])
    n = 0
    for cat, old, new, _why in EDITS[piece]:
        if new in text:
            continue  # 已落盘（脚本可重入；new 均为本批次唯一长串）
        assert old in text, f'{piece}: 未命中 {old[:24]}'
        assert text.count(old) == 1, f'{piece}: 命中 {text.count(old)} 次 {old[:24]}'
        text = text.replace(old, new, 1)
        n += 1
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    after_lines = text.replace('\r\n', '\n').count('\n')
    after_paras = len([x for x in text.replace('\r\n', '\n').split('\n') if x.strip()])
    cjk = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')
    assert before_lines == after_lines, f'{piece}: 行数变了'
    assert before_paras == after_paras, f'{piece}: 段数变了'
    print(f'{piece}: 改动 {n} 条 | 段 {before_paras}->{after_paras} | 行 {before_lines}->{after_lines} | 汉字 {cjk}')
    return n


def main(argv):
    pieces = argv[1:] or list(EDITS)
    total = 0
    for p in pieces:
        total += apply(p)
    print('---', f'共 {total} 条')


if __name__ == '__main__':
    main(sys.argv)
    ast.parse(open(__file__, encoding='utf-8').read())