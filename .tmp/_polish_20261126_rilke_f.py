# -*- coding: utf-8 -*-
"""里尔克 Rainer Maria Rilke《Neue Gedichte》逐片润色落盘 c016/c00 c017/c00 c018/c00 c018/c01
（2026-11-26 逐片轮，第六组：Die Insel I–III / Hetärengräber / Orpheus.Eurydike.Hermes /
Alkestis / Geburt der Venus / Die Rosenschale / INHALT）

落盘方式：定位唯一子串 -> 替换 -> 断言全文命中数 == 1。
段数 / 行数 / 空行结构 / 换行符 / 诗行分行一律不变（本书诗句一节一段，不拆不并）。
"""
import ast
import os
import sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
STAMP = 'final.txt.bak_20261126'
SEP = '\n\n'  # 段落分隔符；CRLF 文件在 main() 里换探针

EDITS = {
    # ============ c016/c00：Die Insel（I） ============
    'c016/c00': [
        # ⑥ nicht…sondern 否定辖域读反：nicht auf sie Angewandtes, zu Großes, Rücksichtsloses
        #    ＝「不是加于他们身上的东西，而是过于庞大的、不顾情面的、被遣送来的」
        ('从童年起便是如此：并非加于他们身上的、过于庞大的、不顾情面的、被遣送来的东西，'
         '那东西把他们的孤寂越发夸大。',
         '从童年起便是如此：并非加于他们身上的东西，而是过于庞大的、不顾情面的、被遣送来的，'
         '它把他们的孤寂越发夸大。'),
    ],
    # ============ c017/c00：Die Insel（II） ============
    'c017/c00': [
        # ⑥ 量词错：jener Sturm 前指下段「那场风暴」，非「那个风暴」
        ('像孤儿一般被那个风暴梳得齐齐整整', '像孤儿一般被那场风暴梳得齐齐整整'),
        # ① 「些」与「何等」相撞：was auf den Kommoden Seltsames steht
        ('看见五斗橱上搁着些何等古怪的东西', '看见五斗橱上搁着何等古怪的东西'),
        # ① 同段两个「外面」，且 Außendeich 是「外堤」
        ('他是在一个陌生的港口听见的——外面，羊群中的一只渐渐变得极大，几乎咄咄逼人，'
         '立在外面的堤坝上。',
         '他是在一个陌生的港口听见的——而在外面，羊群中的一只渐渐变得极大，几乎咄咄逼人，'
         '立在外堤上。'),
    ],
    # ============ c018/c00：Die Insel（III）/ Hetärengräber / Orpheus / Alkestis ============
    'c018/c00': [
        # ⑥ 词不成词：Reiseschachspiel＝旅行棋（「旅棋」为生造）
        ('像一副象牙旅棋', '像一副象牙旅行棋'),
        # ⑥ 硬伤：Schalen gebrannten Tones 是烧陶的碗盏，「贝壳」误读（前文「黄珠」即串珠）
        ('——烘泥的贝壳', '——烧陶的钵碗'),
        # ④ sie＝Flußbetten（河床，阴性复数）；前句「他们」指孩童，此处若作「他们」即错认
        ('于是他们以浅而清的水注满这宽阔道路的整个宽度', '于是她们以浅而清的水注满这宽阔道路的整个宽度'),
        # ⑥ Brücken über Leeres 是「架在空无之上的桥」，「越过」把 über 读成动词性介词
        ('越过空无的桥', '横在空无之上的桥'),
        # ① 「雨天空」不成词（wie Regenhimmel über einer Landschaft）
        ('如雨天空悬在一片景物之上', '如雨天的天空悬在一片景物之上'),
        # ① 「垂在……垂落里」叠字且 aus dem Fall der Falten＝从衣褶的垂落中垂出
        ('双手沉沉垂在衣褶的垂落里', '双手沉沉垂出衣褶的垂落'),
        # ③ indes 并列（「而同时」），非时间从句「当……」
        ('当他的目光如犬先行，折返，回来', '而他的目光如犬先行，折返，回来'),
        # ⑥ 硬伤：Reischaube＝旅行风帽（Reisehaube），非「卷发」（Locken）
        ('那行路与远方消息之神，浅色眼睛上的卷发', '那行路与远方消息之神，明亮眼睛上方的旅行风帽'),
        # ① Gothicism：ihr Gestorbensein＝她「已死」这件事，原译「她的死充满她如丰盈」无法断句
        ('而她的死充满她如丰盈。', '而她已死这件事充满她，如一种丰盈。'),
        # ⑥ ihr Geschlecht war zu＝她的性别闭合着，「合着」读不出 zu
        ('她的性别合着，如一幼花向晚', '她的性别闭合着，如一朵幼花临晚'),
        # ② 三「的」压住中心语：des leichten Gottes unendlich leise leitende Berührung
        ('以致连那轻捷之神无限轻柔的引领的触碰', '以致连那轻捷之神无限轻柔的引领之触'),
        # ① auf dem Streifen eines Wiesenpfades＝一条草径的窄带上
        ('看那消息之神在草径的一条上', '看那消息之神在一条草径的窄带上'),
        # ① 「那身形，那身形」同格重复塞在句中（die schon zurückging dieses selben Weges）
        ('去随那身形，那身形已顺着同一条路退回', '去随那已顺着同一条路退回的身形'),
        # ② 「闷塞的、僵住的笑的坏味」三「的」＋「一阵落下的咿呀的沉淀」定语悬空
        ('只余一句落在浑浊喧响的底上，与一阵落下的咿呀的沉淀，已散发出闷塞的、僵住的笑的坏味。',
         '只余一句落在浑浊喧响的底上，和一阵沉淀下来的咿呀声，已散出闷塞变质的笑的坏味。'),
        # ④ 段首「她」紧接上段之「他」（阿德墨托斯），指代会错认；Die Alten＝一个老妇
        ('这时她走向他，一个老妇', '这时一个老妇走向他'),
        # ①④ Die Alten 是复数，且「那老人……不是赎价」主谓断裂
        ('那老人（立在那儿），你看，不是赎价，他们已用旧、坏了、几乎无值',
         '那两个老人（就立在那儿），你看，不能当赎价，他们已用旧、坏了、几乎无值'),
        # ① 「她的巷」不成词：ihre Gasse＝她的巷道
        ('其余一切不过是她的巷，', '其余一切不过是她的巷道，'),
        # ① 「而来的，是她」缺谓语落点（und das, was kam, war sie）
        ('他留在后头，而来的，是她', '他留在后头，而来到的，是她'),
    ],
    # ============ c018/c01：Alkestis 末 / Geburt der Venus / Die Rosenschale / INHALT ============
    'c018/c01': [
        # ⑦ 破折号后又加句号（德文作 "--."）：与本书他处段末「——」一致
        ('被如今做了我丈夫的那位掩埋之后，消融、化解——。', '被如今做了我丈夫的那位掩埋之后，消融、化解——'),
        # ⑤ 本册同一首诗内 die Gottheit 全作「神」，此处「上帝」为孤例；
        # ⑥ 兼修主谓错位：versteckt in einem kleinen Zeichen 是「神」藏身，不是「那丈夫」藏
        ('上帝几乎像走向一个死人，忽然间远远离开了她的丈夫，那丈夫，'
         '他把这地上百来个生命藏在一个小小的记号里，向他掷了过去。',
         '神几乎像走向一个死人，忽然间远远离开了她的丈夫，那神藏在一个小小的记号里，'
         '把这地上百来个生命向他掷了过去。'),
        # ⑦ 「之后，——」逗号与破折号并用
        ('充满呼喊、不安、骚动的一夜之后，——整个大海又一次裂开、呼喊。',
         '充满呼喊、不安、骚动的一夜之后——整个大海又一次裂开、呼喊。'),
        # ③ so wie… 从句直搬：比句在前、主句在后，须加「也」才收得住
        ('她的身体向清凉里、向未被触碰的晨风里展开。',
         '她的身体也向清凉里、向未被触碰的晨风里展开。'),
        # ② 「肩的活的天平」两「的」＋「活的天平」不成词（der Schultern rege Wage）
        ('现在，肩的活的天平已在笔直的身体上取得平衡', '现在，双肩灵活的天平已在笔直的身体上取得平衡'),
        # ① 缺介词：in dieses Leibes dunkle Frühe＝「在这身体幽暗的清晨里」
        ('然后，这身体幽暗的清晨里，像晨风一样，来了第一口气息。',
         '然后，在这身体幽暗的清晨里，像晨风一样，来了第一口气息。'),
        # ① die rasch dahinschritt… 是插说，原译读成并列谓语，主句（花与草茎立起来）被压没
        ('在她身后，她快步走过那年轻的海岸，整个上午，花与草茎都立起来，温暖、纷乱，像从拥抱中出来。',
         '在她身后——她正快步走过那年轻的海岸——整个上午，花与草茎都立起来，温暖、纷乱，'
         '像从拥抱中出来。'),
        # ⑥ sich aufheben＝涌起，「抬起」把海写成被人抬起的物
        ('大海又一次抬起，把一条海豚抛到那同一个地方', '大海又一次涌起，把一条海豚抛到那同一个地方'),
        # ⑥ Zornige＝愤怒的人们（名词化复数），非「愤怒的闪烁」
        ('你曾见过愤怒的闪烁', '你曾见过愤怒者闪忽'),
        # ② 「尘管的纷乱的一束」三「的」；das wirre Bündel der Staubgeläße
        ('尘管的纷乱的一束被激动、竖起', '那一束纷乱的尘管便激动、竖起'),
        # ① 「便会不被看见」两个否定词叠架，条件从句顺序颠倒
        ('那姿态的摆幅如此之小，若不是它们的光线向宇宙散开，便会不被看见。',
         '那姿态的摆幅如此之小，它们的光线若不向宇宙散开，便不会被看见。'),
        # ⑥ was sie abtun（斜体 was）＝「它们卸下的是什么」，原译作「怎样」
        ('而⟦i⟧它们怎样⟦/i⟧卸下，那轻与重', '而⟦i⟧它们卸下的是什么⟦/i⟧，那轻与重'),
        # ⑥ 否定反转：Was können sie nicht sein＝「它们能不是什么」
        ('它们不能是什么：那朵黄的', '它们能不是什么：那朵黄的'),
        # ⑦ 逗号与破折号并用
        ('盛满小小的明亮蝴蝶，——而那朵呢', '盛满小小的明亮蝴蝶——而那朵呢'),
        # ⑤ 目录归一到正文诗题：Hetärengräber 在本片正文作「娼妓之墓」（同诗内另有「娼妓的天堂」，
        #    娼妓 2 : 妓女 1），目录「妓女墓」为少数派
        ('%S%妓女墓%S%', '%S%娼妓之墓%S%'),
        # ⑤ 目录归一到正文诗题：ORPHEUS. EURYDIKE. HERMES 正文作「俄耳甫斯。欧律狄刻。赫尔墨斯」
        #    （平票 1:1，取正文诗题，且与原文句点一致；赫尔墨斯为通行汉译）
        ('%S%俄耳甫斯·欧律狄刻·赫耳墨斯%S%', '%S%俄耳甫斯。欧律狄刻。赫尔墨斯%S%'),
    ],
}


def cjk(s):
    return sum(1 for ch in s if '\u4e00' <= ch <= '\u9fff')


def main():
    report = []
    for key, pairs in EDITS.items():
        path = os.path.join(BASE, key.replace('/', os.sep), 'final.txt')
        bak = os.path.join(os.path.dirname(path), STAMP)
        if not os.path.exists(bak):
            print('!! missing backup for', key)
            return 1
        with open(path, encoding='utf-8', newline='') as f:
            text = f.read()
        global SEP
        SEP = '\r\n\r\n' if '\r\n' in text else '\n\n'
        before_cjk, before_crlf = cjk(text), text.count('\r\n')
        before_paras = len([p for p in text.replace('\r\n', '\n').split('\n\n')])
        before_lines = text.count('\n')
        n = 0
        for old, new in pairs:
            old, new = old.replace('%S%', SEP), new.replace('%S%', SEP)
            if old not in text and new in text and text.count(new) == 1:
                print('   (already applied, skip):', new[:24])
                continue
            assert old in text, ('MISS', key, old[:30])
            assert text.count(old) == 1, ('MULTI', key, text.count(old), old[:30])
            text = text.replace(old, new, 1)
            n += 1
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        after_paras = len([p for p in text.replace('\r\n', '\n').split('\n\n')])
        after_lines = text.count('\n')
        assert before_paras == after_paras, (key, 'paras', before_paras, after_paras)
        assert before_lines == after_lines, (key, 'lines', before_lines, after_lines)
        assert text.count('\r\n') == before_crlf, (key, 'eol')
        report.append((key, before_paras, after_paras, before_lines, after_lines,
                       before_cjk, cjk(text), n, before_crlf))
        print('%s: 段 %d→%d 行 %d→%d 汉字 %d→%d 改动 %d CRLF %d'
              % (key, before_paras, after_paras, before_lines, after_lines,
                 before_cjk, cjk(text), n, before_crlf))
    print('--- total edits:', sum(r[7] for r in report))
    return 0


if __name__ == '__main__':
    sys.exit(main())

ast.parse(open(__file__, encoding='utf-8').read())