#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""prozess 逐片润色（2026-11-26，片组 d）
c009/c00 c009/c04 c009/c07 c010/c00 c010/c04 c011/c00
只做「定位唯一子串 → 替换 → 断言命中数==1」，不整文件重写。
"""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def path(chapter, piece):
    return os.path.join(ROOT, 'out', chapter, piece, 'final.txt')


# 每片：(chapter, piece, [(old, new, 类别, 理由), ...])
EDITS = [
    ('c009', 'c00', [
        ('这一信念压倒了疑虑。',
         '这后一个念头终究占了上风。',
         '①',
         '同句之内「疑虑」出现两次，后一处实际指「确信势必行」的念头，直说压倒疑虑等于自己压自己；überwog＝占了上风。'),
        ('从他的脸色神情上',
         '从他的脸色和举止上',
         '⑥',
         '原文 aus seinem Gesicht und seinem Benehmen 是两项，Benehmen（举止）被并进「神情」漏掉。'),
    ]),
    ('c009', 'c04', [
        ('他们高踞于小律师之上，其悬殊远过小律师之于那被人瞧不起的讼棍，简直无从比较。',
         '他们高踞于小律师之上，位阶悬殊之远，非小律师之于那被人瞧不起的讼棍可比。',
         '①',
         '「其悬殊……简直无从比较」修饰语悬空，收尾四字无着落；原文是「高出之多，远非……可比」的两级比较。'),
        ('不有一阵子成天惦记着他们。',
         '不曾有一阵子成天惦记着他们。',
         '①',
         '「不有一阵子」不成词，der nicht … eine Zeit lang träumen würde 是否定关系从句。'),
        ('可这不是谁能求来的',
         '可这不是凭自己意愿能求来的',
         '⑥',
         '原文 durch eigenen Willen kann man das nicht erreichen，「凭自己意愿」是句眼，漏了就把「求」变成单纯的门路问题。'),
    ]),
    ('c009', 'c07', [
        ('她冲K.点了点头，K.却直勾勾地盯着她，她笑了笑。',
         '她含笑朝K.点了点头，K.却直勾勾地盯着她。',
         '⑥',
         'Sie nickte K., der sie starr ansah, lächelnd zu：lächelnd 是点头的方式，译成事后的「笑了笑」把同时性读成了先后。'),
        ('这一问简直像在布洛克胸口推了一把，又在背上推了一把——他早已往前挪了一大截——他踉跄着，深深地弯下腰站住',
         '布洛克早已往前挪了一大截，这一问简直像在他胸口推了一把，又在背上推了一把，他踉跄着，深深地弯下腰站住',
         '①',
         'der schon eine große Strecke weitergerückt war 是插入定语，原文夹在两次「推」之间；汉语照搬会把连动切碎，提到句首才不断气。'),
        ('可我但凡力量够得着，礼数、本分和法庭惯例所要求的一切都仔细研究过。',
         '可我只要这点微薄力气够得着，礼数、本分和法庭惯例所要求的一切都下过细功夫研究。',
         '⑥',
         'soweit meine schwachen Kräfte reichen 的「微薄」是布洛克自贬的分寸所在，漏掉则成了逞强；句末 auch 的「仔细」也宜落在动词上。'),
        ('这番话若译成言语，那就是粗野的辱骂。',
         '这一举一动若译成言语，那就是粗野的辱骂。',
         '⑥',
         'Hätte man dieses Benehmen in Worte übersetzt：Benehmen 指他方才瞪眼摇头的举止，他一句话也没说，作「这番话」是误读。'),
        ('他这场官司的日子还数得过来呢',
         '他这场官司的时辰还数得过来呢',
         '⑥',
         'Man kann noch die Stunden seines Prozesses zählen：以「时辰可数」极言案期将尽，作「日子」把夸张的狠劲磨平了。'),
    ]),
    ('c010', 'c00', [
        ('等这趟差事回来，他头痛欲裂',
         '等他出完这趟公差回来，头痛欲裂',
         '①',
         '「等这趟差事回来」缺主语，读者不知谁回来；原文 Als er von dieser Reise … zurückkehrte 主语明确。'),
        ('如今干活时，他总觉得四面八方都是威胁，那些差错再也没法避免了。',
         '如今干活时，他总觉得四面八方都是威胁，而这些差错他已经再也避不开了。',
         '①',
         '原文 von denen … und die er nicht mehr vermeiden konnte 是同一个关系从句管住「差错」，译成并列短句后两句失联。'),
    ]),
    ('c010', 'c04', [
        ('辨认出一道光，从法的大门里不可熄灭地透出来。',
         '辨认出一道光，从法的大门里透出来，永不熄灭。',
         '③',
         'der unverlöschlich aus der Türe bricht 的副词 unverlöschlich 照搬成「不可熄灭地」，汉语无此状语；拆作后置谓语才立得住。'),
        ('又用他的请求把守门人弄得很累',
         '又一遍遍地请求，把守门人弄得很累',
         '①',
         'durch seine Bitten 直搬成「用他的请求」不成话，动词句化才通。'),
        ('为了让他的听觉在消逝中还能听见，便冲他吼道',
         '为了还能传到他那正在消逝的听觉里，便冲他吼道',
         '①',
         'um sein vergehendes Gehör noch zu erreichen：消逝的是听觉本身，不是「在消逝中听见」，主语错位。'),
        ('因为这道入口只为你一个人设的。',
         '因为这道入口只为你一个人而设。',
         '⑦',
         '「只为你一个人设的」与「而设」相较漏字，句末助词与介词搭配不齐。'),
    ]),
    ('c011', 'c00', [
        ('又用一种训练有素的、演练纯熟的、不可抗拒的手法抓住了K.的手。',
         '又用一种训练有素、演练纯熟、不可抗拒的握法抓住了K.的手。',
         '⑥②',
         'Griff 是「握法」不是「手法」；三个「的」定语串联也把中心语压没了。'),
        ('这是一种几乎只有死物才能结成的统一。',
         '这是一种几乎只有死物才能结成的统一体。',
         '①',
         'Einheit 在此是可数的实体（浑然一体），作「统一」缺中心语。'),
        ('刮净他们下巴上的皱纹。',
         '抠净他们下巴上的褶子。',
         '⑥',
         'die Falten am Kinn ausgekratzt：auskratzen 是抠净褶缝里的脏，皱纹是刮不掉的。'),
        ('”他嚷道，与其说是问，不如说是喊。',
         '”与其说他是在问，不如说是在嚷。',
         '①',
         'rief er mehr als er fragte：原文对比的是「问」与「嚷」，译文「嚷道……不如说是喊」同语反复。'),
        ('只觉得自己这番抵抗毫无价值，这一点当即就叫他明白了。',
         '他当即明白的，只是自己这番抵抗毫无价值。',
         '①',
         'bloß die Wertlosigkeit seines Widerstandes kam ihm gleich zum Bewußtsein：主语是「毫无价值」这件事，「叫他明白」把施受关系倒置了。'),
        ('只为不忘记她对他所意味的那番告诫。',
         '只为不忘记她给他带来的那番告诫。',
         '②',
         '「她对他所意味的那番告诫」三个「的」式定语叠加，中心语被压没。'),
        ('在底下，如今看不见了，有铺着碎石的小径和舒适的长椅',
         '在它们下面，如今看不见了，是铺着碎石的小径和舒适的长椅',
         '①',
         'Unter ihnen 的 ihnen 指岛上的树丛灌木，单说「在底下」读者会以为是桥下。'),
        ('四下里都是月光，带着它那天然的、宁静的气度，那是任何别的光都没有的。',
         '四下里都铺着月光，带着它那份自然与安详，那是任何别的光都得不到的。',
         '⑥',
         'mit seiner Natürlichkeit und Ruhe：是「自然」与「安详」两种性质，不是「天然的宁静气度」。'),
    ]),
]


def apply(chapter, piece, edits):
    p = path(chapter, piece)
    with open(p, encoding='utf-8', newline='') as f:
        text = f.read()
    orig = text
    n_before_par = count_paras(text)
    lines_before = text.count('\n')
    newline = '\r\n' if '\r\n' in text else '\n'
    done = []
    for old, new, cat, why in edits:
        assert old in text, f'{chapter}/{piece}: NOT FOUND: {old[:40]}'
        assert text.count(old) == 1, f'{chapter}/{piece}: NOT UNIQUE({text.count(old)}): {old[:40]}'
        text = text.replace(old, new)
        done.append((cat, old, new, why))
    # 校验：段数、行数、换行符不变
    assert count_paras(text) == n_before_par, f'{chapter}/{piece}: 段数变了'
    assert text.count('\n') == lines_before, f'{chapter}/{piece}: 行数变了'
    assert ('\r\n' in text) == (newline == '\r\n'), f'{chapter}/{piece}: 换行符变了'
    assert '⟦' not in text.replace('⟦i⟧', '').replace('⟦/i⟧', ''), 'marker broken'
    assert text.count('⟦i⟧') == orig.count('⟦i⟧') and text.count('⟦/i⟧') == orig.count('⟦/i⟧')
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    return done, n_before_par, count_paras(text), text


def count_paras(text):
    return len([b for b in text.replace('\r\n', '\n').split('\n\n') if b.strip()])


def hanzi(text):
    return sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')


def main():
    only = set(sys.argv[1:])
    total = 0
    report = []
    for chapter, piece, edits in EDITS:
        if only and f'{chapter}/{piece}' not in only:
            continue
        done, na, nb, text = apply(chapter, piece, edits)
        total += len(done)
        report.append((chapter, piece, na, nb, text.count('\n'), hanzi(text), len(done)))
    print('%-6s %-5s %s %s %s %s %s' % ('piece', 'paras', 'paras_after', 'lines', 'hanzi', 'edits', 'nl'))
    for chapter, piece, na, nb, nl, hz, n in report:
        print('%-4s/%-4s %5d %8d %10d %7d %7d' % (chapter, piece, na, nb, nl, hz, n))
    print('total edits:', total)
    for chapter, piece, edits in EDITS:
        if only and f'{chapter}/{piece}' not in only:
            continue
        for cat, old, new, why in edits:
            print(f'[{chapter}/{piece}][{cat}] {old} -> {new}')


if __name__ == '__main__':
    main()

ast.parse(open(__file__, encoding='utf-8').read())