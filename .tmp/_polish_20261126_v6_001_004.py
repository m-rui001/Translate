# -*- coding: utf-8 -*-
"""v6 chunk001-chunk004 逐段通读润色（2026-11-26 准则）。
只做「定位唯一子串 → 替换 → 断言命中数」，不整文件重写。"""
import io
import os
import shutil
import ast

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = '.bak_20261125'

EDITS = {
'chunk001': [
 # ⑥ 漏译情态：j'ai toujours eu si peur devant vous（一向那么怕您）
 ("因为我太怯懦，在您面前一向如此，即使逼着自己",
  "因为我太怯懦，我在您面前一向那么害怕，以至于即使逼着自己"),
],
'chunk002': [
 # ⑥ 成语误用：si heureux（很幸福），与「天伦」（亲子之伦）无关
 ("我们俩将双双厮守在此，享尽天伦",
  "我们俩将双双厮守在此，过得十分幸福"),
 # ⑥ 成语误用：ce qui est le plus important pour notre cœur（最重要之物）
 ("对我们的心灵或精神休戚相关之物",
  "对我们的心灵或精神至关重要之物"),
 # ⑥ 成语误用／错字：pensée panique（惊心动魄）
 ("我所感受到的惊魂动魄",
  "我所感受到的惊心动魄"),
 # ⑥ 词义误读：le bruit de la fenêtre（窗户的响声），非「窗枢」
 ("我听见窗枢声响的那个深宵",
  "我听见窗户作响的那个深宵"),
 # ⑥ 成语误用：l'intervalle est le plus grand（间隔最大），「达于化境」言技艺
 ("其间的悬殊遂达于化境",
  "其间的悬殊遂达于极点"),
 # ⑥ 词义误读：encore une fois（再说一遍）被读成「再次重申」
 ("再次重申，撇开所有言之凿凿的缘由不提",
  "再说一遍，撇开上述种种缘由不谈"),
 # ⑥ 词义误读：celle qui était là（先前就在这儿的那个女人），「膝下」指子女
 ("况且离去的女人亦已非复昔日膝下的那个女人",
  "况且，走了的女人已不再是先前在此的那个女人"),
 # ① 主谓失配：sa vie… voit s'ajouter à elle les vies（生活里添进了别的生活）
 ("她在我们身畔的生活，我们原本洞若观火，如今却猝然裹挟进了她势必涉足其间的万千生灵，而她之所以背弃我们",
  "她与我们共处的生活，我们原本洞若观火，如今却骤然添上了她势必与之交融的那些生活；而她之所以背弃我们"),
 # ⑥ 词义误读：rétroagit（反过来作用），「反躬」是自省
 ("反躬作用于昔日依偎在我们身畔",
  "反过来作用于昔日依偎在我们身畔"),
 # ① 主谓失配：et qui fait que les hommes… l'ont été presque toujours de la même manière
 ("这使得屡遭弃置的男人因其秉性与恒常可测的划一反应，遭弃的行径往往如出一辙",
  "这使那些屡遭弃置的男人因其秉性与恒常可测的划一反应，遭弃的方式往往如出一辙"),
 # ① 缺成分：l'horreur qu'elle avait de vivre ainsi en esclave
 ("我早已洞悉了她对沦为这般囚徒生活的厌烦与惊惧",
  "我早已洞悉她对过这种囚徒生活的厌烦与惊惧"),
 # ① 冗赘：「迎面扑来」与「飞来」重复，原文只 le malheur imprévu
 ("眼前这迎面扑来的飞来横祸",
  "眼前这突如其来的横祸"),
 # ① 独立绝对结构被搬成「在…之下」的条件状语，悬空
 ("甚而假使阿尔贝蒂娜向我挑明去意，而在我威逼利诱、苦苦哀求之下，我又是否真能将她挽留！",
  "甚而，假使阿尔贝蒂娜向我挑明去意，而我又威逼利诱、苦苦哀求，是否就真能将她挽留！"),
 # ⑦ 冗余：「唯一途径」+「唯有」
 ("远走高飞的唯一途径便唯有潜逃",
  "远走高飞的唯一途径便是潜逃"),
 # ⑥ 词义误读：Fugitive parce que reine（正因为是女王才逃亡），「沦为」加了贬义
 ("贵为女王故而沦为逃亡者，势必如此。",
  "正因为是女王，才只能逃亡，事情就是这样。"),
 # ⑥ 词义误读：un nom différent（姓氏不同），原文并无「相仿」
 ("而是致予府上一位姓氏相仿、为人误读之人",
  "而是致予府上一位姓氏不同、被人错认之人"),
],
'chunk003': [
 # ⑥ 成语／熟语误读：porter le diable en terre（满面晦气、哭丧着脸）
 ("她就像要把魔鬼送进坟墓",
  "她就像送殡似的一脸晦气"),
 # ①「的字堆叠 + 关系从句直搬」，中心语被压没
 ("得知了这些事，我们便明白，那个女人，如今她在我们眼里已经远不如散步时轻易遇见的所有女人那么可意，我们曾怪她让我们为了她而牺牲那些女人，反倒成了我们千倍愿意选择的人。",
  "得知了这些事，我们便明白，那个如今在我们眼里已远不如散步时随便遇见的任何女人那么可意的女人，那个我们曾怪她让我们为她牺牲了那些女人的女人，反倒成了我们千倍愿意选择的人。"),
 # ③ 法语括注被照搬成破折号插在「在…之间」当中，把介宾隔断
 ("因为此时问题已不再是在一种愉悦——它由于习惯，也许还由于对象平庸，几乎变得等于零——和其他愉悦之间作选择，那些愉悦诱人而又迷人，问题是在那些愉悦和某种比它们强烈得多的东西之间作选择，那就是对痛苦的怜悯。",
  "因为此时问题已不再是在一种愉悦和其他愉悦之间作选择，那第一种愉悦由于习惯，也许还由于对象的平庸，几乎已变得等于零；那些愉悦诱人而又迷人，问题是在它们和某种比它们强烈得多的东西之间作选择，那就是对痛苦的怜悯。"),
],
'chunk004': [
 # ⑥ 词义误读：se plaçait de façon à ne pas apercevoir（站到看不见…的位置），非「避开看不见的椅子」
 ("我在房间里每挪一步都小心翼翼，避开看不见的阿尔贝蒂娜那把椅子，避开那架自动钢琴——她曾把金色拖鞋踩在它的踏板上——避开她用过的任何一件东西；",
  "我在房间里每挪一步都小心翼翼，总摆好位置，不让自己看见阿尔贝蒂娜那把椅子，不让自己看见那架自动钢琴——她曾把金色拖鞋踩在它的踏板上——也不让自己看见她用过的任何一件东西；"),
 # ①「而非」与「非…不可」纠缠，读作「而不是通知它」
 ("总有一个还不知道阿尔贝蒂娜已经走了，而非通知它不可",
  "总有一个还不知道阿尔贝蒂娜已经走了，还得去通知它"),
 # ①「轮到」+「到头来」叠床架屋
 ("非得让它们每一个轮到头来第一次听见这句话",
  "非得让它们每一个轮着第一次听见这句话"),
 # ① 比较从句缺主句谓语，悬空
 ("就像在葬礼上，一个认识死者的告老仆人的到来。",
  "正像在葬礼上，一个认识死者的告老仆人到来时那样。"),
 # ① 缺中心语：le nom de celle qu'homme il avait aimée（所爱的那女人的名字）
 ("只是它还是人时所爱过的那个名字",
  "只是它还是人时所爱的那个女子的名字"),
 # ⑦ 体例：破折号前多一个顿号
 ("把那同我的痛苦连在一起、——这类观念反正总有一个——单独抽出来",
  "把那同我的痛苦连在一起的观念——这类观念反正总有一个——单独抽出来"),
 # ⑥ 词义误读：de caresser ce qui en était le dehors，第二个「占有」应作「抚弄」
  ("占有它、抚弄它的幸福，占有这个未知的外壳",
  "占有它、抚弄它的幸福，抚摸这个未知的外壳"),
 # ① 主句缺谓语（c'est … combien …）
 ("证明这一点最有力的，比起幸福之中感到的厌倦来还有力：",
  "证明这一点最有力的，是这么一种情形，它比起幸福之中感到的厌倦来还有力："),
],
}

report = []
for name, edits in EDITS.items():
    d = os.path.join(BASE, name)
    path = os.path.join(d, 'final.txt')
    bak = path + BAK
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        created = 'bak 新建'
    else:
        created = 'bak 已存在（未覆盖）'
    text = io.open(path, encoding='utf-8', newline='').read()
    before_nl = text.count('\n')
    before_han = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')
    for old, new in edits:
        assert old in text, (name, 'missing', old)
        assert text.count(old) == 1, (name, 'not unique', old)
        text = text.replace(old, new)
    after_nl = text.count('\n')
    after_han = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')
    assert after_nl == before_nl, (name, 'line count changed', before_nl, after_nl)
    io.open(path, 'w', encoding='utf-8', newline='').write(text)
    # 落盘后自检
    t = io.open(path, encoding='utf-8', newline='').read()
    assert '\r\n' in t
    assert '"' not in t
    assert t.count('“') == t.count('”'), (name, 'quotes unbalanced')
    assert t.count('，、') == 0 and '、—' not in t, (name, 'stray dunhao')
    assert t.count('⟦') == 0
    report.append((name, len(edits), created, before_nl, after_nl, before_han, after_han))

for r in report:
    print('%-9s edits=%d %s nl %d -> %d han %d -> %d' % r)

ast.parse(open(__file__, encoding='utf-8').read())
print('OK')