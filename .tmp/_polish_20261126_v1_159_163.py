# -*- coding: utf-8 -*-
"""润色第一卷 chunk159 / 161 / 162 / 163（2026-11-26 轮，out_ind/v1）。

铁律：只做「定位唯一子串 → assert count == 1 → 替换」，绝不整文件重写；
先建 .bak_20261125（已存在则不覆盖）；保持原换行符与空行结构。
用法： python _polish_20261126_v1_159_163.py [--dry]
"""
import ast
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

EDITS = {
    '159': [
        # ①/③ changer, c'est-à-dire devenir une autre personne —— 插入语被挪到句末，读成另一层意思
        ('人不能一面改变，一面仍服从那个已经不复存在的自己的感情，也就是说，不能变成另一个人。',
         '人无法一面改变——也就是变成另一个人——一面仍旧服从自己已经不再是的那一个人的感情。'),
        # ③ comme au morne Parisien... —— 比喻提前、主句被割断
        ('但这嫉妒很轻，好比一个阴沉的巴黎人离开威尼斯回法国，最后一只蚊子还嗡嗡地证明意大利和夏天离得不算太远；'
         '这嫉妒向他证明，他也还没有完全走出那段他受尽折磨的时光——不过在那段时光里，他也领受过一种如此甜美的感受方式'
         '——也许路上的偶然还会让他从远处偷偷再瞥见几分那段时光的美；所以这嫉妒与其说是折磨，不如说给了他一种舒服的刺激。',
         '但这嫉妒很轻：它向他证明，他也还没有完全走出那段他受尽折磨的时光——不过在那段时光里，他也领受过一种如此甜美的感受方式'
         '——也许路上的偶然还会让他从远处偷偷再瞥见几分那段时光的美；所以这嫉妒与其说是折磨，不如说给了他一种舒服的刺激，'
         '就像一个阴沉的巴黎人离开威尼斯回法国时，最后一只蚊子还嗡嗡地证明，意大利和夏天离得并不太远。'),
        # ⑥ sinon ... du moins 读反（原译把「留住它」放在「看清」之后）
        ('可大多数时候，他想趁着还能做到，至少把那段刚刚走出的、如此特殊的生活看清楚一眼，不然就留住它；然而他发觉自己已经做不到了。',
         '可大多数时候，他努力想做的，即使不是留在那段他刚刚走出的、如此特殊的生活里，'
         '至少也是趁自己还能做到的时候把它看清楚一眼；然而他发觉自己已经做不到了。'),
        # ① 比喻句主语错位 + ⑥ ne pas laisser fuir sans ... 三重否定读成「不许它不告而别」
        ('于是他缩起身子，带着那种毫无好奇心、昏昏沉沉的状态，像个打盹的旅人把帽子往眼睛上一拉，在车厢里睡过去，'
         '听凭火车把他载得越来越快，载离那个他住了那么久、本来说好不许它不告而别的国度——他本该给它最后一个告别的。',
         '于是他缩起身子，像那个昏昏欲睡的旅人一样，带着毫无好奇心的麻木，把帽子往眼睛上一拉，在车厢里睡过去，'
         '听凭火车把他载得越来越快，载离那个他住了那么久的国度——他早已跟自己说定，不能任它就这么溜走，'
         '而不给它最后一个告别。'),
        # ① quand 从句被抹平成并列，比喻的落点错位
        ('甚至就像那个旅人只在到了法国才醒来一样，斯万偶然在身边找到了证据，证明福什维尔做过奥黛特的情人，他却发觉自己丝毫不觉得痛苦',
         '甚至就像那个旅人只到法国才醒来一样，当斯万偶然在身边找到证据、证明福什维尔做过奥黛特的情人时，'
         '他却发觉自己丝毫不觉得痛苦'),
        # ⑥ où elle le reverrait le soir ou un autre jour ＝ 当晚或改日在哪儿再见他
        ('也没有告诉他在哪儿、哪一天晚上再见面',
         '也没有告诉他当晚或改日在哪儿再见他'),
    ],
    '161': [
        # ②/③ telle ou telle partie du tableau changeant de la mer —— 三重「的」压没中心语
        ('把大海那幅变幻的图景的某一部分映照出来——这效果他事先并没有想到——',
         '把大海那幅变幻图景中的这一处或那一处映照出来——这效果他事先并没有想到——'),
        # ①/③ rien ne ressemblait moins à ... que —— 比较结构无基准
        ('可是，我从前在风暴的日子里常常梦想的那个巴尔贝克，与我此刻所见的真实的巴尔贝克，也再没有比这更不相同的了。',
         '可是，也没有什么东西比我在风暴的日子里常常梦想的那个巴尔贝克，更不像这个真实的巴尔贝克了。'),
        # ⑦ 「最相反对的东西」不成辞
        ('在我看来是与人类机械的产物最相反对的东西',
         '在我看来是与人类机械的产物最为对立的东西'),
        # ③ pour qui, pas plus que pour les baleines, il n'y eut de moyen âge —— 语序断裂
        ('那些粗野的渔人，之于他们，就像之于鲸鱼一样，并不存在什么中世纪',
         '那些粗野的渔人，对他们来说，正如对鲸鱼一样，从来就不存在什么中世纪'),
        # ③ 独立分词短语里的两个宾语被搬成破折号括注
        ('风——它吹进我心里，吹得它像吹我房间的壁炉一样瑟瑟颤动，吹来去巴尔贝克旅行的计划——'
         '在我心里把对哥特式建筑的渴望和对海上风暴的渴望混在了一起。',
         '风把去巴尔贝克旅行的计划吹进我心里，在我心中呼啸，把我的心吹得和我房间的壁炉一样瑟瑟颤动，'
         '也在我心里把对哥特式建筑的渴望和对海上风暴的渴望混在了一起。'),
    ],
    '162': [
        # ① quand le petit jour se lèverait... 主谓悬空，contre les écumes 被拆成独立句
        ('赶到巴尔贝克时，看微明的晨光升在海面上——那是一片狂暴的海，浪花飞溅，我要躲进那座波斯风格的教堂去。',
         '赶到巴尔贝克，正赶上微明的晨光从狂暴的海面上升起——我要迎着飞溅的浪沫，躲进那座波斯风格的教堂里去。'),
        # ⑥ piquait encore aigrement avec toutes les aiguilles du givre
        ('不是贡布雷那种还带着霜的尖刺、扎人的春天',
         '不是贡布雷那种还用满身霜针尖利地扎人的春天'),
        # ① 「这一页从另一章里撕下来的纸」定语后置悬空
        ('把这一页从另一章里撕下来的纸，不按它本来的位次、或早或晚地插进幸福那本掺了假历法的日历里。',
         '把从另一章里撕下的这一页纸，不按它本来的位次、或早或晚地插进幸福那本掺了假历法的日历里。'),
        # ① 「失落着另一季的一天」动词带「着」不成句
        ('因为常常在某一季里，会失落着另一季的一天',
         '因为常常在某一季里，会失落另一季的一天'),
        # ④/② le désir que m'avaient inspiré les lieux qu'ils désignaient —— 「它们」指代不明
        ('因为在这些名字内部，终于积攒起了那些地方所激起、由它们所指的欲望。',
         '因为在这些名字内部，终于攒起了那些地方在我心中激起的欲望，而那些地方正是这些名字所指的。'),
    ],
    '163': [
        # ① dont mon âme avait soif et qu'elle aurait profit à connaître
        ('我的心灵渴望着它，认识它是有好处的。',
         '我的心灵渴求着它，而认识它是会有所得的。'),
        # ①/② des noms ... des noms qui n'étaient que pour eux, des noms comme en ont les personnes
        ('它们因为有了名字，有了只属于它们的名字，像人一样有姓名的名字，就更加增添了几分个体性。',
         '它们被用名字来称呼之后，又平添了多少个体性啊——那是只属于它们的名字，像人一样各有其名的名字。'),
        # ① 「名字」被说成「城市之一」，主谓错配
        ('帕尔马这个名字，是我最想去的城市之一，自从我读了《帕尔马修道院》以后，它在我眼里就是紧凑的、光滑的、淡紫的、柔和的；',
         '帕尔马这个名字——我最想去的城市之一，自从我读了《帕尔马修道院》以后——在我眼里便是紧凑的、光滑的、淡紫的、柔和的；'),
        # ① 三个并列落不到谓语上：à l'aide de cette syllabe lourde ... où ne circule aucun air, et de tout ce que...
        ('因为我是只凭帕尔马这个名字里那个沉重的音节想象它的，那里没有空气流通，此外还加上我硬让它吸收来的司汤达式的柔美和紫罗兰的反光。',
         '因为我只是凭帕尔马这个名字里那个沉重的音节来想象它——那音节里不通一丝空气——'
         '再加上我硬要它吸收的司汤达式的柔美和紫罗兰的反光。'),
        # ⑤ Sainte-Marie-des-Fleurs 与 chunk162「圣母百花教堂」不一致，取通行汉译
        ('它的主教堂被称为花之圣母教堂',
         '它的主教堂被称为圣母百花教堂'),
        # ②/① 「一只轻盈的帽子翅膀那白色和粉色的飞扬」四个「的」压没中心语
        ('蓬塔旺，一只轻盈的帽子翅膀那白色和粉色的飞扬，倒映在一条发绿的运河水里，微微颤动；',
         '蓬塔旺，一顶轻盈软帽的帽翅扬起的一片白与粉，在发绿的运河水中颤颤地映着倒影；'),
        # ③ ce train ... dans lequel j'étais monté tant de fois en imagination —— 关系从句被搬成破折号插在句中
        ('至少也让我坐上一回那趟一点二十二分的火车，去见识诺曼底或布列塔尼的建筑和风景'
         '——那趟车我在想象中已经坐过许多次了，那我最想停留的，会是那些最美的城市',
         '至少也让我坐上一回那趟我在想象中已经坐过许多次的一点二十二分的火车，'
         '去见识诺曼底或布列塔尼的建筑和风景，那我最想停留的，会是那些最美的城市'),
        # ⑦ 「父母允许我——」后的破折号需与句末破折号成对
        ('去见识诺曼底或布列塔尼的建筑和风景，那我最想停留的，会是那些最美的城市',
         '去见识诺曼底或布列塔尼的建筑和风景——那我最想停留的，会是那些最美的城市'),
    ],
}


def load(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()


def save(p, t):
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(t)


def cjk(t):
    return sum(1 for ch in t if '\u4e00' <= ch <= '\u9fff')


def main(dry):
    total = 0
    for chunk, edits in EDITS.items():
        d = os.path.join(BASE, 'chunk' + chunk)
        fp = os.path.join(d, 'final.txt')
        bp = os.path.join(d, BAK)
        text = load(fp)
        orig = text
        n_before_lines = len(text.replace('\r\n', '\n').split('\n'))
        n_before_cjk = cjk(text)
        if not dry and not os.path.exists(bp):
            shutil.copy2(fp, bp)
        for i, (old, new) in enumerate(edits, 1):
            assert old in text, f'{chunk} edit#{i} MISSING: {old[:30]}'
            assert text.count(old) == 1, f'{chunk} edit#{i} NOT UNIQUE: {old[:30]}'
            assert old != new
            text = text.replace(old, new)
        n_after_lines = len(text.replace('\r\n', '\n').split('\n'))
        assert n_before_lines == n_after_lines, f'{chunk} line count changed'
        assert text.count('\r\n') == orig.count('\r\n'), f'{chunk} CRLF changed'
        # 引号成对、无 ASCII 引号、⟦ 计数不变
        assert text.count('“') == text.count('”'), f'{chunk} quotes unbalanced'
        assert '"' not in text, f'{chunk} ASCII quote'
        assert text.count('⟦') == orig.count('⟦') and text.count('⟧') == orig.count('⟧')
        if not dry:
            save(fp, text)
        total += len(edits)
        print(f'chunk{chunk}: {len(edits)} edits | lines {n_before_lines} -> {n_after_lines} | '
              f'cjk {n_before_cjk} -> {cjk(text)} | {"DRY" if dry else "written"}')
    print(f'--- total edits: {total}')


if __name__ == '__main__':
    ast.parse(open(__file__, encoding='utf-8').read())
    main('--dry' in sys.argv)