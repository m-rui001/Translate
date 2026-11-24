# -*- coding: utf-8 -*-
"""v6 chunk005-chunk008 逐段通读润色（2026-11-26 准则）。
只做「定位唯一子串 → 替换 → 断言命中数」，不整文件重写。
换行符按原文件保留（chunk006 为 LF，其余 CRLF）。
"""
import os
import re
import ast
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = '.bak_20261125'

EDITS = {
'chunk005': [
 # ① 悬空状语：「可在过去」断裂，tout de même dans le passé 无处安放
 ("即便到头来还是我胜了，可在过去，也就是在无可挽回的意义上，我仍然是失败者",
  "即便到头来还是我胜了，但在过去、在无可挽回的层面上，我依然是失败者"),
 # ① 介词悬空：「说的是对我的理智」不成句（Je dis pour ma raison, non pour moi）
 ("我说的是对我的理智，不是对我。",
  "我说的是我的理智，不是我自己。"),
 # ① 因果连词误植：法语无 car，la chose que… 是「那件事」的后置同位语，
 #    被读成「因为……我也从不敢想象」，把主句切断
 ("尽管那是我一生中到那时为止所尝过的最大的痛苦，因为即使在我最坏的猜想里，我也从来不曾大胆到把它想象出来。",
  "尽管那是我一生中到那时为止所尝过的最大的痛苦；而那件事，即便在我最坏的猜想里，我也从来不曾大胆到想象得出来。"),
],
'chunk006': [
 # ⑤ Rachel canon 作「拉谢尔」（v6 共 26 处；「蕾茜儿」3 处为孤形）
 ("虽然已经和蕾茜儿分了手",
  "虽然已经和拉谢尔分了手"),
 # ④ 指代不明 + ⑤ 专名：moi qui avais essayé d'ajouter à Rachel tout ce que
 #    Saint-Loup lui avait ajouté —— 「添到她身上」的「她」与原句同位，须点明
 ("把圣卢加到蕾茜儿身上的一切也添到她身上",
  "把圣卢自己加在拉谢尔身上的一切都添到她身上"),
 # ⑤ 同一段内 Rachel 两形并出（蕾茜儿 / 拉结），统一为 canon
 ("正如蕾茜儿在我眼里是什么样子",
  "正如拉谢尔在我眼里是什么样子"),
 # ⑤ 引文中的同名角色（《拉谢尔，当主恩……》，见 v3）一贯作「拉谢尔」，
 #    此处「拉结」使谐音双关失效
 ("“拉结，当主降临时”",
  "“拉谢尔，当主降临时”"),
 # ⑦ 赘余：「不过只瞥见过」二词叠用（n'avait qu'entrevue）
 ("认出阿尔贝蒂娜，他在车厢里也不过只瞥见过她一眼",
  "认出阿尔贝蒂娜，何况他在车厢里也只是瞥见过她一眼"),
 # ① 主谓关系倒置：「和巴尔贝克时期的阿尔贝蒂娜同现在活生生的她一样不同」不成句
 ("最近拍的那张照片上的她，已经和巴尔贝克时期的阿尔贝蒂娜同现在活生生的她一样不同",
  "最近那张照片上的她，跟巴尔贝克时期的阿尔贝蒂娜相比已变了那么多，其程度不亚于眼下活生生的她"),
 # ① 「还没有远去到这样的地步」生造搭配（ce qu'il avait éprouvé n'était pas encore si lointain）
 ("可他当时的经历还没有远去到这样的地步，以至于他对这类痛苦不再怀有一种特别的同情和怜悯",
  "可他那时的感受还没有淡远到这种地步，使他对这类痛苦不再怀有一种特别的同情和怜悯"),
 # ⑥ 成语误用：habituel 说的是「反应常见」，非「人惯做而视为平常」
 ("甚至可以说是习以为常",
  "甚至可以说是司空见惯"),
 # ⑥ 词义误读：l'importance individuelle 指此人作为个体的分量，非「对个人的重要性」
 ("体现在她对个人的重要性上",
  "体现在她这个人的分量上"),
 # ② 「的」字堆叠，中心语「蛹壳」被压没；顺带 pires＝最可怕，非「最剧烈」
 ("在那层叫情人看不见所爱之人最剧烈的变化的、痛苦与柔情的蛹壳之下，他所爱的人的脸，已有时间衰老、改变",
  "那层由痛苦与柔情结成的蛹壳叫情人看不见所爱之人身上最可怕的变化，而在它底下，那张脸已有时间衰老、改变"),
 # ④ 「它」两指：un résidu qu'elle m'empêchait d'apercevoir 的宾语是「残余」
 ("而正是这层积，反倒使我看不见它",
  "而正是这层积，反倒使我无法看见那残余"),
 # ⑦ 体例：原文括注（Qu'auraitce été si…）被抹平成正文，与全册括注体例不合
 ("假如罗贝尔看到的不是那个姑娘的照片，而是一个老情妇的照片，那又会怎样呢？",
  "（假如罗贝尔看到的不是那个姑娘的照片，而是一个老情妇的照片，那又会怎样呢？）"),
 # ⑦ 搭配错位：「好处」不能「胜过」一种做法
 ("可它有一个无可估量的好处，胜过了“本来该怎样做”",
  "可比起“本来应当采取的做法”，它有一个无可估量的好处"),
 # ⑥ 漏译时间框：Le temps était loin où j'avais commencé…
 ("还只是很笨拙地在视觉感受之外添上味觉、嗅觉和触觉，此后",
  "还只是很笨拙地在视觉感受之外添上味觉、嗅觉和触觉，那样的日子已经远了；此后"),
],
'chunk007': [
 # ① 「源于……纷至沓来」动宾失配（une sorte de beauté naît de la multiplicité des ennuis…）
 ("它源于袭扰着我们的诸多厌烦纷至沓来，交织如瓦格纳式的种种主导动机",
  "它源于袭扰我们的种种烦扰——它们纷至沓来，交织如瓦格纳式的主导动机"),
 # ① 「是……的时候」与「乃是」两套谓语叠置
 ("是在它们从那未来的深处给我们带来的乃是一种希望的时候",
  "是在它们从未来的深处给我们带来一种希望的时候"),
 # ① 生造短语「绝无败理」（la mission ne pouvant échouer）
 ("既然圣卢的使命绝无败理",
  "既然圣卢的使命绝无失败之理"),
 # ① 「笃定……及其必定成功」宾语错杂
 ("我终究如此笃定圣卢的干练及其必定成功",
  "我毕竟如此确信圣卢的干练和成功"),
 # ⑥ 词义误读：erreur judiciaire 是「误判」，非「龃龉」
 ("亦无司法的龃龉",
  "亦无误判"),
 # ③⑦ 法语括注（je ne songeai pas, en effet, que…）被搬成插入主句的「实际上，」，
 #    括号无闭合，主句 il me sembla que 被甩到下一句 —— 改还原为句末补注
 ("然而蓦地，出于一种我未曾察觉的混淆，实际上，我并未想到阿尔贝蒂娜既已成年，尽可以寓居于我家，甚至做我的情妇。我仿佛觉得拐骗未成年少女的罪名也能同样加诸阿尔贝蒂娜身上。",
  "然而蓦地，出于一种我未曾察觉的混淆，我仿佛觉得拐骗未成年少女的罪名也能同样加诸阿尔贝蒂娜身上——其实我并未想到，她既已成年，尽可以寓居我家，甚至做我的情妇。"),
 # ⑥ 词义误读：des petites filles mieux que celle-là 是「更好的」，非「更齐整的」
 ("比这齐整得多的小姑娘",
  "比这个好得多的小姑娘"),
],
'chunk008': [
 # ① 悬空修饰：「时刻，用来想象」把伴随动作说成目的（j'eus … à imaginer Venise）
 ("有过一些惬意平静的时刻，用来想象威尼斯和陌生的美丽女子",
  "在想象威尼斯和陌生的美丽女子时，也有过一些惬意的平静时刻"),
],
}

HAN = re.compile(r'[\u4e00-\u9fff]')


def paragraphs(text):
    return [l for l in text.replace('\r\n', '\n').split('\n') if l.strip()]


def main():
    report = []
    for chunk, edits in EDITS.items():
        d = os.path.join(BASE, chunk)
        path = os.path.join(d, 'final.txt')
        bak = path + BAK
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        with open(path, encoding='utf-8', newline='') as f:
            text = f.read()
        nl = '\r\n' if '\r\n' in text else '\n'
        n_par_before = len(paragraphs(text))
        n_han_before = len(HAN.findall(text))
        n_applied = 0
        for old, new in edits:
            assert old in text, '缺失: %s' % old[:30]
            assert text.count(old) == 1, '非唯一: %s' % old[:30]
            text = text.replace(old, new)
            n_applied += 1
        assert len(paragraphs(text)) == n_par_before
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        with open(path, encoding='utf-8', newline='') as f:
            check = f.read()
        assert check == text
        assert ('\r\n' in check) == (nl == '\r\n')
        report.append((chunk, n_applied, n_par_before, len(paragraphs(check)),
                       n_han_before, len(HAN.findall(check)), nl))
    print('chunk | 改动 | 段数(前/后) | 汉字(前/后) | 换行')
    for r in report:
        print('%s | %d | %d/%d | %d/%d | %s' %
              (r[0], r[1], r[2], r[3], r[4], r[5], 'CRLF' if r[6] == '\r\n' else 'LF'))
    print('总改动: %d' % sum(r[1] for r in report))


main()
ast.parse(open(__file__, encoding='utf-8').read())