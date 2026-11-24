# -*- coding: utf-8 -*-
"""v7 chunk025 / chunk026 / chunk028 / chunk029 逐段润色落盘脚本（2026-11-26）。

改法：定位唯一子串 → 替换 → 断言命中数 == 1；绝不整文件重写。
读写均 newline='' ，保持 CRLF。每改完一个 chunk 立即落盘。
"""
import ast
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

EDITS = {
    'chunk025': [
        # ③ 括注式独立分词被搬成破折号，插在「装出……觉得」之间，把宾语从句隔断
        ('他总装出——他那法兰西人的血在血管里沸腾，像贡布雷的葡萄汁——觉得战争期间待在办公室里算不了什么',
         '他那法兰西人的血在血管里沸腾，像贡布雷的葡萄汁；他总装出觉得战争期间待在办公室里算不了什么'),
        # ⑥ « Mais si, vous servez dans ce bureau, et plus qu\'au front. » 「比在前线服役得更多」，非「更有用」
        ('“哪儿的话，您在这个处服役，比在前线还更有用。',
         '“哪儿的话，您在这个处服役，而且比在前线服役得还多。'),
        # ⑥ « les deuils … inutiles même à les empêcher d\'aller dans le monde » ＝丧事都拦不住他们，非「不必靠丧事」
        ('如今男人更稀少，丧事更频繁，甚至不必靠丧事来阻止他们出入社交界，战争本身就足够了。',
         '如今男人更稀少，丧事更频繁，而丧事甚至已经拦不住他们出入社交界，战争本身就足够了。'),
        # ③ 括注被搬成破折号，插在「正如……钟爱……」与主句「他眼看着……」之间，主语漂移
        ('那种稍显笨重的美——他曾在绘画和挂毯中追逐它、抚摩它——，他眼看着',
         '那种稍显笨重的美（他曾在绘画和挂毯中追逐它、抚摩它），他眼看着'),
        # ③ « à l\'état de souvenir aimé » 被动态直搬（「被爱着的记忆」）
        ('而他的绘画，作为一种被爱着的记忆，可以说就寄寓在其中',
         '而他的绘画，作为一份被珍爱的记忆，可以说就寄寓在其中'),
    ],
    'chunk026': [
        # ⑥ juste en apparence ＝表面上正当，非「正确」
        ('任何一句表面上正确的话欺骗我的本能',
         '任何一句表面上正当的话欺骗我的本能'),
        # ① 一句话里「以这样的尺度」出现两次，第二个悬空，草履虫与「它们」指代纠缠
        ('而且他将以这样的尺度来看它们：需要一万多只才能填满边长一毫米的立方体的草履虫，'
         '正是以这样的尺度看一个高个男子的身体。',
         '而且他将以那种尺度来看它们：填满边长一毫米的立方体需要一万多只草履虫，'
         '而它们看一个高个男子的身体，用的正是这种尺度。'),
        # ② 四个「的」串成的长定语（……的海洋的汹涌）把中心语压没
        ('如同一片有着数百万波浪、试图冲破一道存在了数世纪的悬崖线的海洋的汹涌，',
         '如同一片汹涌的海洋，带着数百万波浪，试图冲破一道存在了数世纪的悬崖线，'),
        # ③ 原文「德国人被……阻挡住了，诚然」的括注被搬成引号后的分句，引号内外错位、句子断气
        ('几乎没想到德国人虽说被一道不断更新的血腥屏障“阻挡住了”，而这道屏障距巴黎只有一小时汽车路程。',
         '几乎没想到德国人虽说被一道不断更新的血腥屏障“阻挡住了”——诚然，那道屏障距巴黎只有一小时汽车路程。'),
        # ⑥ lieue 是全库 canon 的「里格」（chunk129「几里格高」），非市里「里」
        ('几天之内跃过数百万里，', '几天之内跃过数百万里格，'),
        # ① « détourner son autre main des trempettes » 直搬成「从蘸食中移开」，动宾不通
        ('而不必让她另一只手从蘸食中移开',
         '而不必让她另一只手从蘸的动作中腾出来'),
    ],
    'chunk028': [
        # ③ 一句里两个「既然」各领一个条件，第二个把「du moment que」的让步搬成对等原因
        ('然而，既然他不过是个旁观者，一切就都该把他推向亲德，既然他并不是真正的法国人，却生活在法国。',
         '然而，既然他不过是个旁观者，一切就都该把他推向亲德——何况他并不是真正的法国人，却生活在法国。'),
        # ⑥ « assurés dans un nouveau pronostic » ＝笃定地作出新的预测，非「确信一个新的预言」
        ('一年之后又同样确信一个新的预言', '一年之后又同样笃定地作出新的预测'),
        # ① 三层套嵌（莫奈的诋毁者／对他们说……的人／的「这不是一回事」），主谓宾读不出来
        ('在艺术上也许不会明白，莫奈的诋毁者们用来反驳那些对他们说“当年对德拉克洛瓦也说过同样的话”'
         '的人的“这不是一回事”，正回应着同一种思想倾向。',
         '在艺术上也许不会明白：当有人对莫奈的诋毁者说“当年对德拉克洛瓦也说过同样的话”时，'
         '他们回敬的那句“这不是一回事”，正出自同一种思想习惯。'),
        # ① 「……撰写的，……撰写」同一句里两个「撰写」，后一个悬空无主语
        ('找到了一种“重新服役”的方式，由布里肖们、诺普瓦们、勒格朗丹们撰写。',
         '找到了一种“重新服役”的方式：布里肖之流、诺普瓦之流、勒格朗丹之流。'),
        # ⑤ « un vaincu » 全册作「战败者」；「侮辱被战胜者的人」两层被动，读者会读成「侮辱那些被战胜的人」
        ('让这些侮辱被战胜者的人蒙羞、喘不过气',
         '让这些侮辱战败者的人蒙羞、喘不过气'),
        # ⑥ « brebis galeuse » 成语作「害群之马」；且马的量词是「匹」
        ('会导致那只害群之羊的母亲死亡', '会导致那匹害群之马的母亲死亡'),
        # ① 两个「也就是」串成流水句，第二处把 cis-à-dire 的说明叠成并列
        ('那就是像他只在肉欲时刻才做的那样行动，也就是说，违背他那富有同情的本性，'
         '也就是违背那为诱人的恶而燃烧、并压碎有德性的丑的本性。',
         '那就像他只在肉欲时刻才会做的那样行事——也就是说，逆着他那富有同情心的本性，'
         '逆着那为诱人的恶而燃烧、并压碎有德性的丑的本性。'),
        # ⑥ 括注读反：「公众对这一切一无所知，而夏尔吕完全知道」→ 公众不知道的正是夏尔吕所深知的内情
        ('如果不是公众对这一切一无所知，而德·夏尔吕先生却完全知道，这一印象本还会强烈得多。',
         '倘若公众不是对德·夏尔吕先生了如指掌的那些内情全然无知，这一印象本还会强烈得多。'),
    ],
    'chunk029': [
        # ⑥ « la berloque » 是解除警报的汽笛／号声（CNRTL：appel de sirène signalant la fin d\'une alerte），非「放晚了的炮声」
        ('而他们身旁那阵放晚了的炮声，像一个看不见的顽童，每隔一会儿便为这个好消息添上一笔，把欢叫抛向空中。',
         '而他们身旁那声解除警报的汽笛，像一个看不见的顽童，每隔一会儿便为这个好消息添上一句，把欢叫抛向空中。'),
    ],
}


def cjk(t):
    return sum(1 for ch in t if '\u4e00' <= ch <= '\u9fff')


def apply_one(chunk):
    d = os.path.join(ROOT, chunk)
    f = os.path.join(d, 'final.txt')
    bak = os.path.join(d, BAK)
    if not os.path.exists(bak):
        shutil.copy2(f, bak)
        print('%s: 新建备份 %s' % (chunk, BAK))
    else:
        print('%s: 备份已存在，未覆盖' % chunk)
    with open(bak, encoding='utf-8', newline='') as fh:
        text = fh.read()
    with open(f, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)
    before_lines = len(text.replace('\r\n', '\n').split('\n'))
    before_paras = len([x for x in text.replace('\r\n', '\n').split('\n') if x.strip()])
    before_cjk = cjk(text)
    n = 0
    for old, new in EDITS[chunk]:
        assert old in text, (chunk, 'MISS', old[:30])
        assert text.count(old) == 1, (chunk, 'NOT UNIQUE', old[:30], text.count(old))
        text = text.replace(old, new)
        n += 1
    with open(f, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)
    after_lines = len(text.replace('\r\n', '\n').split('\n'))
    after_paras = len([x for x in text.replace('\r\n', '\n').split('\n') if x.strip()])
    after_cjk = cjk(text)
    print('%s: 改动 %d 条 | 行数 %d->%d | 段数 %d->%d | 汉字 %d->%d | %s'
          % (chunk, n, before_lines, after_lines, before_paras, after_paras,
             before_cjk, after_cjk, 'CRLF' if '\r\n' in text else 'LF'))
    assert before_lines == after_lines and before_paras == after_paras
    return n


if __name__ == '__main__':
    total = 0
    for c in ['chunk025', 'chunk026', 'chunk028', 'chunk029']:
        total += apply_one(c)
    print('--- 合计改动 %d 条' % total)
    ast.parse(open(__file__, encoding='utf-8').read())
    print('AST self-check OK')