# -*- coding: utf-8 -*-
"""逐段润色 v7 chunk091/092/094/095：定位唯一子串 → 替换 → 校验；不整文件重写；逐 chunk 落盘。"""
import os, shutil, ast

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

EDITS = {
    '091': [
        # ⑥ 词义（cheveux dorés tout plats＝金黄的、平贴的头发；「齐平」为误读）
        ('那头齐平的金发底下', '那头平贴的金发底下'),
        # ⑥ 词义（la transformation des idées morales qu'il éveillait dans le public
        #      ＝他如今在公众心里唤起的道德观念的变化，非「公众对他的看法」）
        ('这种改变之深，正如公众如今对他的道德看法所发生的变化',
         '这种改变之深，不亚于他如今在公众心中唤起的道德观念所经历的变化'),
    ],
    '092': [
        # ⑥ 词义（« à la ville »＝戏台之下、私生活中，此处非「她家」）
        ('一旦被邀到她家，也就是“城里”吃午饭，整个聊天过程中',
         '一旦被请去“在城里”和她一起吃午饭，整个聊天过程中'),
        # ① 「热络着」不成动词，法语 inutilement chaude 是形容声音的状语
        ('那声音一如从前，白白地热络着，动人',
         '那声音一如从前，徒然地热络、动人'),
        # ⑤ 地名（au Bois＝布洛涅林苑；单作「林苑」不成地名）
        ('从前为了在林苑里看她一眼', '从前为了在布洛涅林苑里看她一眼'),
        # ① 「不像（当年）那些困难」比较项悬空，主谓失配
        ('我一点没犯难，不像当年第一次去盖尔芒特亲王家里赴晚宴时碰到的那些困难，'
         '那时我觉得那些困难理所当然，如今把一位客人介绍给他，在我看来竟如此简单',
         '我一点没犯难：当年第一次去盖尔芒特亲王家里赴晚宴时碰到的那些困难，'
         '如今连影子也没有了；那时我觉得那些困难理所当然，'
         '如今把一位客人介绍给他，在我看来竟如此简单'),
    ],
    '094': [
        # ④ 指代（关系从句 qui＝l'Affaire Dreyfus，非「他成了狂热分子」这件事）
        ('又成了狂热分子或傻瓜，这件事在他们眼中改变了人的价值',
         '又成了狂热分子或傻瓜——德雷福斯事件在他们眼中改变了人的价值'),
        # ③ 括注被照搬成破折号、插在主谓之间，把「我曾在这种本性中……找到」切断
        ('这个圈子，我曾在其特殊本性中——这种本性由某些亲和力界定，'
         '这些亲和力把欧洲所有伟大的亲王家族姓氏吸引到它这里，'
         '而那种排斥力则使一切非贵族成分远离它——为盖尔芒特这个姓氏找到一处物质上的庇护所，'
         '而这个姓氏正是由它赋予最后的现实性；这个圈子本身，'
         '在其我曾以为稳固的亲密构造中，也经历了深刻的改变。',
         '这个圈子有一种特殊的本性：某些亲和力把欧洲所有伟大的亲王家族姓氏吸引到它这里，'
         '另一种排斥力则使一切非贵族成分远离它。我曾在这种本性里为盖尔芒特这个姓氏'
         '找到一处物质上的庇护所，而这个姓氏的最后一点现实性，正是它赋予的。'
         '然而这个圈子本身，在其我曾以为稳固的亲密构造中，也经历了深刻的改变。'),
        # ③ 被动式硬搬（appelés par leur prénom）
        ('他们在这里受到接待、被以名字相称时那种亲密无间的熟稔',
         '他们在这里受到接待、被人直呼其名时那种亲密无间的熟稔'),
    ],
    '095': [
        # ① 「但恰恰是因为……」无主句，因果从句悬空（Mais précisément c'est que…）
        ('但恰恰是因为当时的社交界，正如如今已经改变的面容',
         '但原因恰恰在于，当时的社交界，正如如今已经改变的面容'),
        # ③ 关系从句（qui, niant l'élégance de Swann…）被搬成重复整句
        ('会对这种说法报以微笑，这种说法否认了斯万的优雅，在我看来简直荒唐',
         '会对这种说法报以微笑，它否认了斯万的优雅，在我看来简直荒唐'),
        # ① 悬空修饰语（honorée, glorieuse 修饰的是一生的阶段，非「伟人」）
        ('为自己人生一个新的阶段，以一位受人尊崇、声名显赫的伟人身份露了面。',
         '为自己人生中一个受人尊崇、光彩夺目的新阶段，作了一次伟人式的登场。'),
    ],
}


def read(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()


def cjk(txt):
    return sum(1 for ch in txt if '\u4e00' <= ch <= '\u9fff')


def main():
    total = 0
    for num, edits in EDITS.items():
        d = os.path.join(BASE, 'chunk' + num)
        f = os.path.join(d, 'final.txt')
        b = os.path.join(d, BAK)
        if not os.path.exists(b):
            shutil.copy2(f, b)
            print(f'chunk{num}: 备份已建 {BAK}')
        else:
            print(f'chunk{num}: 备份已存在，未覆盖')

        text = read(f)
        before_cjk, before_lines = cjk(text), text.count('\n')
        applied = 0
        for old, new in edits:
            assert old in text, f'chunk{num} 未命中: {old[:30]}'
            assert text.count(old) == 1, f'chunk{num} 命中不唯一: {old[:30]}'
            text = text.replace(old, new, 1)
            applied += 1
        # 落盘前自查：段落结构、引号
        assert text.count('\n') == before_lines
        assert text.count('“') == text.count('”')
        assert '"' not in text
        with open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)
        total += applied
        print(f'chunk{num}: 改动 {applied} 条 | 行数 {before_lines}->{text.count(chr(10))} '
              f'| 汉字 {before_cjk}->{cjk(text)} | 段数 {len([x for x in text.split(chr(10)) if x.strip()])}')
    print('合计改动', total, '条')


main()
ast.parse(open(__file__, encoding='utf-8').read())