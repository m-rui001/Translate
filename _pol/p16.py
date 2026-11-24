# -*- coding: utf-8 -*-
"""p16: chunk114–133 润色。"""
import sys
sys.path.insert(0, '_pol')
from lp import Batch, check

b = Batch('p16')

# ch114 ③外语句法：de ne laisser tomber mes regards sur notre table que les jours où y était servi quelque vaste poisson
b.rep(114, '而且只在桌上被端上一条大鱼的日子', '而且只在大鱼端上桌的日子', tag='读不通')

# ch115 ⑥搭配：éprouvent et manifestent une vive satisfaction
b.rep(115, '就会生出、也会表现出极大的快活', '就会感到、也会表现出极大的快活', tag='硬伤')
# ch115 ⑥搭配：répondait à nos remerciements
b.rep(115, '她答谢我们的道谢时', '她回应我们的道谢时', tag='读不通')
# ch115 ②的字堆叠 / ⑥词义：le bonheur d'une union conclue à sa table（婚约≠union）
b.rep(115, '不声不响地守望在自家餐桌上缔结的婚约的美满',
      '不声不响地守望自家餐桌上缔结的那桩姻缘，看它美满', tag='的字堆叠')

# ch117 ⑥词义：admirateur 作「崇拜者」，非「赞赏者」
b.rep(117, '因为他是提香一个学生的赞赏者', '因为他是提香一个学生的崇拜者', tag='硬伤')

# ch118 ⑦体例：引语缺收引号；③外语句法 comme Mme Blandais m'agace
b.rep(118, '多让我恼火，”律师公会会长对庭长说', '叫我有多恼火，”律师公会会长对庭长说', tag='外语句法')
b.rep(118, '我就不跟他们一道出门了。', '我就不跟他们一道出门了。”', tag='体例')

# ch120 ⑦体例：破折号后多余的逗号；⑤专名（faubourg Saint-Germain 全册作「圣日耳曼区」）
b.rep(120, '不住旅馆的人也有权从那里经过——，那个', '不住旅馆的人也有权从那里经过——那个', tag='体例')
b.rep(120, '古老圣日耳曼郊区的贵族们', '古老圣日耳曼区的贵族们', tag='专名')

# ch122 ③外语句法：elle ne possédait sur moi aucune des notions qui constituent une personne
b.rep(122, '而既然关于我，她并不具有构成一个人的任何观念',
      '而既然在她眼里，关于我连构成一个人的起码观念都不存在', tag='外语句法')

# ch127 ①读不通：两个「因」叠床架屋
b.rep(127, '因他一向对我殷勤，我因这种失礼而难过，而他似乎正为此难受。',
      '他一向对我殷勤，我为他受这份失礼而难过，而他似乎也正为此难受。', tag='读不通')

# ch128 ⑤专名：全册 98 处作「维尔帕里西夫人」，chunk128 独有 5 处带「德·」
b.rep(128, '德·维尔帕里西夫人', '维尔帕里西夫人', expect=5, tag='专名')

# ch130 ①读不通：状语插在主语与谓语之间
b.rep(130, '维尔帕里西夫人本人也虽说是间接地为我早已确信的他那本性的几个主要特点添了一份证实。',
      '而且这一回，维尔帕里西夫人虽说是间接地，也为我早已确信的他那本性的几个主要特点添了一份证实。',
      tag='读不通')

# ch133 ⑥错别字：自已
b.rep(133, '朝向我自已', '朝向我自己', tag='硬伤')

n = b.flush()
print('p16 改动', n, '条')
for row in b.log:
    print(row[0], row[1], row[2], '|', row[3])
bad = {c: check(c) for c in range(114, 134) if check(c)}
print('自检问题:', bad if bad else 'none')