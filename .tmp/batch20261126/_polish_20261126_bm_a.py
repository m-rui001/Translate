# -*- coding: utf-8 -*-
"""bm_a 逐段润色（2026-11-26）。只改元素值，不动数组长度与顺序。
落盘体例：indent=1, ensure_ascii=False, LF（照原文件）。
"""
import ast
import json
import shutil
import sys

PATH = 'bm_a_zh.json'
BAK = 'bm_a_zh.json.bak_20261126'

# (段号, 旧子串, 新子串, 类别, 理由, 原文)
EDITS = [
    (0,
     '爱德华·菲利里，对一个情感欲望皆属寻常的人来说，已尽可能地以超然的态度看待人生与人性。',
     '就一个情感欲望皆属寻常的人所能做到的限度而言，爱德华·菲利里以超然的态度看待人生与人性。',
     '③', '英语「so far as may be possible to a man of…」的状语硬搬到句首，中文须先说限度再说主语。',
     'Edward Fillery, so far as may be possible to a man of normal passions and emotions, took a detached view of life and human nature.'),
    (1,
     '这宽容显出一种不寻常的仁厚、一种格外的体谅——在一个那样年轻的人身上。',
     '在一个那样年轻的人身上，这宽容显出一种不寻常的仁厚、一种格外的体谅。',
     '③', '句末介词短语直搬成破折号补语，中文悬空；提前作状语。',
     'a tolerance which showed an unusual charity, an exceptional understanding, in one so young.'),
    (4,
     '低处的草坡上铺满百合、杜鹃与石楠',
     '低处的草坡上铺满百合、杜鹃与山踯躅',
     '⑥', 'rhododendron 误作「石楠」（石楠是 heather/Photinia）；与前一 azalea（杜鹃）并列，取「山踯躅」。',
     'their lower turfy slopes are carpeted with lilies, azaleas, rhododendrons'),
    (6,
     '但那原始血液的与生之权却没有淡去',
     '但那份出自原始血液的与生俱来的权利，却没有淡去',
     '①', '「与生之权」为生造压缩语，读不通。',
     'though not the birthright of his primitive blood.'),
    (7,
     '但爱德华身上有股质地，使溺爱无从为害。',
     '但爱德华身上有种底子，使溺爱无从为害。',
     '⑥', 'stuff 此处指「料子、底子」，作「质地」与下文重复且不通。',
     'But Edward had stuff in him that rendered spoiling harmless.'),
    (7,
     '他血里有些原始的质地，源流古老，偏向野性。',
     '他血里有一种原始的属性，源流古老，偏向野性。',
     '⑥', '同上段同一词，避免「质地」叠出。',
     'There lay some primal quality in his blood'),
    (27,
     '一丝隐约的不安，像压力一样，触到了他。',
     '一丝隐约的压力，仿佛不安，触到了他。',
     '⑥', '原文是「压力（似由不安而生）」，译文把喻体与本体颠倒了。',
     'A faint pressure, as of uneasiness, touched him.'),
    (36,
     '水，至少大量的水，是与他不和的。',
     '水，至少大量的水，是与他为敌的。',
     '⑥', 'inimical＝有害、为敌；「不和」误读为不和睦。',
     'Water, in large quantities at any rate, was inimical.'),
    (46,
     '孩子忽然问，语气紧得叫人注意：',
     '孩子忽然问，语气紧迫得叫人不得不注意：',
     '①', '「语气紧得叫人注意」不成句，强度也弱于原文。',
     'the boy asked suddenly with arresting intensity:'),
    (48,
     '在他看来，那些巍峨荒凉的山峦远在时空之外；而在那里，丰富而异教的想象，他深知，会奔向那些庞大威严的生灵，高于人类，或善或恶，近于那令人振奋的神祇观念，而且断然不是人。',
     '那些巍峨荒凉的山峦，于他已远隔时空；他深知，在那里，丰富而异教的想象会奔向那些庞大威严的生灵——高于人类，或善或恶，近于那令人振奋的神祇之观念，而且断然不是人。',
     '③', '插入语「他深知」被搬到句子中间拆断主干，是英语插入从句的直搬。',
     'Upon those immense and lonely mountains, distant in space and time for him, imagination, rich and pagan, ran, he well knew, to vast and mighty beings'),
    (60,
     '他在把紊乱恢复为匀衡方面极为成功。',
     '他在把紊乱恢复为均衡方面极为成功。',
     '⑥', '「匀衡」为错字，当作「均衡」。',
     'He was immensely successful in restoring proportion out of disorder.'),
    (64,
     '便让他当上了一所机构的主持——在那里',
     '便让他当上了一所机构的主管——在那里',
     '⑥', 'Head of an establishment 作「主持」词性不合，改「主管」。',
     'saw him Head of an establishment'),
    (65,
     '他那双安静而锐利的眼睛也使他显得威严，但那阴沉只到那微笑点亮他那略显粗犷的面孔时便消散了。',
     '他也因那双沉静而锐利的眼睛而显得威严；不过那阴沉只维持到微笑点亮他那略显粗犷的面孔为止。',
     '①', '「只到……时便消散」句式断裂，且一句两个「那」。',
     'imposing, too, with his quiet, piercing eyes, but sombre only until the smile lit up his somewhat rugged face.'),
    (67,
     '这些力至今少有人懂，它们像看起来那样不可信，又像实际上那样取用简易，其作用一样神秘，其限度一样无边。',
     '这些力至今少有人懂：它们似乎无边无际，却又看似难以置信；运用起来神秘莫测，取用起来却又极其简易。',
     '①', '「像看起来那样不可信」不成句；as…as 对举被机械照搬，须拆成两截。',
     'powers as yet but little understood, powers as limitless as they seemed incredible, as mysterious in their operation as they were simple in their accessibility.'),
    (69,
     '却又仿佛春天本人的美好曾在他的心上一落，在向北的途程中把它吻成了花。',
     '却又仿佛春天本人的美好曾落在他的心上，在她向北的途中把它吻成了花。',
     '①', '「曾在他的心上一落」为硬凑句式。',
     'yet perfumed as though the fairness of Spring herself had lit upon his heart and kissed it into blossom on her passage north.'),
    (69,
     '它躺在那儿，等着那份真诚的相信，好确信它的热情得到了回应。',
     '它躺在那儿，等着那份真诚的信念，好确信自己的热情得到了回应。',
     '①', 'belie(f) 作名词译「相信」，中文不通。',
     'It lay waiting for that sincere belief which would convince that its passion was returned.'),
    (70,
     '使它那宏大可怖的眼睛里的光黯淡下去，使他一开始质问，它便退走。',
     '使它那宏大可怖的眼睛里的光黯淡下去；他一开口追问，它便退走。',
     '⑥', '原文 the instant he began to question＝他一开口质问就退走，译文读成「使他开始质问」。',
     'causing it to withdraw the instant he began to question.'),
    (70,
     '然而他的爱、他的热情仍在那里，与相信一同躲着',
     '然而他的爱、他的热情仍在那里，与信念一同躲着',
     '①', 'belief 作「相信」不通，与上段统一作「信念」。',
     'His love, his passion, none the less, were there, hiding with belief'),
    (73,
     '他年近四十，在伦敦西北部创办了那所专收不寻常的、所谓无望病例的私人疗养院——那地方对所有人免费，他有时微笑着想，把它称作「精神诊所」；这时，他探索与研究的最终结果可以总括为一句话：',
     '他年近四十时，在伦敦西北部创办了那所专收不寻常的、所谓无望病例的私人疗养院——那地方对所有人免费，他有时微笑着想，称它作「精神诊所」。他的探索与研究的最终结果，可以总括为一句话：',
     '①', '「这时」所指悬空（原文本是 when 引导的时间状语嵌在主句主语里），拆句另起。',
     'The net result of his inquiries and research, when, at the age of nearly forty, he established his own Private Home…, may be summed up in the single sentence'),
    (80,
     '人的深处，超出了单纯的传心术和扩展的传心术之外，还包含',
     '人的深处，在单纯的传心术与扩展的传心术之外，还包含',
     '①', '「超出了……之外」重复赘余。',
     'The human depths included, beyond mere telepathy and extended telepathy,'),
    (88,
     '他所受那场震动的一个效果，只要说明他现在对这种头脑的了解比以前多得多，就清楚了。',
     '他受的那场震动，有一个效果只要说明一点便可见出：他现在对这种头脑的了解，比先前多得多。',
     '①', 'by merely stating that… 硬搬成「只要说明……就清楚了」，主语与谓语跨得太远。',
     'One effect of the shock he had undergone will be evident by merely stating that he now understood this type of mind a good deal better than before.'),
    (89,
     '可那期待已久的和平的好处，仍然挑逗人地、气人地遥不可及',
     '可那期待已久的和平的好处，仍然又撩人又气人地遥不可及',
     '①', '两个「……地」状语叠用不成话。',
     'the benefits of the long anticipated peace still kept provocatively, exasperatingly, out of reach'),
    (90,
     '人类仍因进步被有力地证伪而错位',
     '人类仍因进步之说被有力地驳倒而错乱',
     '⑥', 'dislocated 此处指人类心理的错乱，非物理「错位」；「进步被证伪」亦欠通。',
     'the Race was still dislocated by the convincing disproof of progress'),
    (91,
     '公开说来只是破坏性的。',
     '却公开自认只是破坏性的。',
     '①', 'avowedly destructive only 的副词硬翻成「公开说来」，不成句。',
     'was avowedly destructive only.'),
    (94,
     '我知道您已不再是利物浦那所机构的主持',
     '我知道您已不再是利物浦那所机构的主管',
     '⑥', '与第 64 段统一作「主管」。',
     'I know you are no longer head of the Establishment in Liverpool'),
    (98,
     '他对我们所知的人生，也许并不属于？',
     '他也许并不属于我们所知的那种人生？',
     '①', '介词短语前置造成句子失配。',
     'that to human life, as we know it, he does not, perhaps, belong?'),
    (103,
     '却是用铅笔签在一张未写字的空白纸的底端',
     '却是用铅笔签在一张空白纸的底端',
     '⑦', '「未写字的」「空白」同义重复。',
     'but signed in pencil and at the bottom of an unwritten blank sheet.'),
    (106,
     '那助手带着嫉妒般的谨慎与判断力',
     '那助手以近乎戒备的谨慎与判断力',
     '⑥', 'jealous care 是「看得极紧的守护」，非「嫉妒」。',
     'whose jealous care and judgment saved him so many foolish, futile, un-real cases'),
    (107,
     '笔记证实了他自己和助手的错误——也许是故意的？——无知。',
     '笔记证实了他的错误，也证实了他助手的无知——那无知也许是故意的？',
     '①', '英语双破折号插入语照搬，中文句子断成三截且不成话。',
     "The Notes established his mistakes and his assistant's--perhaps intentional?--ignorance."),
    (108,
     '他的名字仍像受人珍爱的香烟一样，缭绕在老城的塔楼之上。',
     '他的名字仍像一炷受人珍爱的熏香，缭绕在老城的塔楼之上。',
     '⑥', 'incense 是「熏香」，「香烟」今义为纸烟。',
     'still hovered like well-loved incense above the old-town towers.'),
    (109,
     '那异教缠念，拜风与火者，那奇怪的「N. H.」',
     '那异教缠念，拜火与风者，那奇怪的「N. H.」',
     '⑤', '与第 104 段「拜火与风者」不一致（worshipper of fire and wind），归一到出现较早者。',
     'the Mason letters, the pagan obsession, worshipper of wind and fire, the strange "N. H."'),
    (117,
     '对由众多工作者组成、以此和谐服务之理想为治的庞大体系，他有半截记忆。',
     '对一个由无数工作者构成、受这和谐服务之理想统辖的庞大体系，他保有半截记忆。',
     '①', '「以……为治」文言腔夹在口语笔记中，且定语堆叠，读不通。',
     'Half-memories of vast system of myriad workers, ruled by this ideal of harmonious service.'),
    (145,
     '那套私人套房已为它有趣的住客准备妥当',
     '那套私人套房已为那位有趣的住客准备妥当',
     '④', '「它」指套房，紧接又指住客，指代撞车。',
     'the private suite all ready for its interesting occupant'),
    (146,
     '「非人」也许确实有趣，但多半不如梅森所想的那样。',
     '「N. H.」也许确实有趣，但多半不如梅森所想的那样。',
     '⑤', '原文即引号内的 "N. H."，全篇他处一律作「N. H.」，此处不应转译。',
     '"N. H." might be distinctly interesting, but hardly all that Mason had thought him.'),
]


def main():
    try:
        shutil.copyfile(PATH, BAK) if not __import__('os').path.exists(BAK) else None
    except Exception as e:  # noqa
        print('backup skip:', e)

    with open(PATH, encoding='utf-8', newline='') as f:
        d = json.load(f)

    with open(BAK, encoding='utf-8', newline='') as f:
        d0 = json.load(f)
    assert len(d) == len(d0) == 147, (len(d), len(d0))

    n = 0
    skipped = 0
    for idx, old, new, cat, why, src in EDITS:
        if new in d[idx] and old not in d[idx]:
            skipped += 1          # 已改过（重跑安全）
            continue
        assert old in d[idx], (idx, old)
        assert d[idx].count(old) == 1, (idx, old)
        d[idx] = d[idx].replace(old, new)
        n += 1

    # 自检（落盘前）
    for i, t in enumerate(d):
        assert t.strip(), ('empty', i)
        assert '\r' not in t, ('CR', i)
        for bad in ('"', "'"):
            assert bad not in t, ('ascii quote', i, bad)
        for bad in ('。。', '，，', '、、', '；；', '！！', '？？', '：：'):
            assert bad not in t, ('dup punct', i, bad)
    # 引号配对
    for i, t in enumerate(d):
        assert t.count('「') == t.count('」'), ('quote', i)
        assert t.count('『') == t.count('』'), ('nested quote', i)
    # 段末标点
    ok_end = '。！？…：—」』）'
    for i, t in enumerate(d):
        assert t.rstrip()[-1] in ok_end, ('end punct', i, t.rstrip()[-6:])
    # 拉丁残留（汉字 + 空格 + 小写英文 + 空格 + 汉字）
    import re
    pat = re.compile(r'[\u4e00-\u9fff] [a-z]{2,} [\u4e00-\u9fff]')
    for i, t in enumerate(d):
        assert not pat.search(t), ('latin residue', i)

    with open(PATH, 'w', encoding='utf-8', newline='') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write('\n')

    # 落盘后复核
    with open(PATH, encoding='utf-8', newline='') as f:
        d2 = json.load(f)
    assert len(d2) == 147
    assert d2 == d
    han = sum(1 for t in d2 for ch in t if '\u4e00' <= ch <= '\u9fff')

    print('本次落盘改动条数:', n, '（已改跳过:', skipped, '）')
    print('数组长度: %d（备份 %d）OK' % (len(d2), len(d0)))
    print('汉字数:', han)
    print('JSON 可解析: OK；无空段: OK；无 ASCII 引号: OK；无重复标点: OK；无拉丁残留: OK；引号成对: OK')


if __name__ == '__main__':
    main()
    ast.parse(open(__file__, encoding='utf-8').read())
    print('ast self-check: OK')