# -*- coding: utf-8 -*-
"""bm_i / bm_j 逐段通读润色（2026-11-26）。

规则：只改七类；只允许「定位唯一子串 → 替换 → 断言命中」；数组长度与顺序不变；
json.dump(ensure_ascii=False, indent=1) + 末尾换行，与原文件逐字节同格式（LF）。
"""
import ast
import io
import json
import os
import re
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = '.bak_20261126'

# ---------------------------------------------------------------- 改动清单
# (段号, 类别, 旧串, 新串, 理由, 英文原文)
I_EDITS = [
    (2, '③',
     '接受它的特权或许会托付给我们；',
     '这份接受它的特权，或许会托付给我们；',
     'may be entrusted the privilege 的被动硬搬，宾语提前成了无主语流水句',
     'may be entrusted the privilege of accepting it'),
    (38, '①',
     '他心里的心和智也比先前更静',
     '他胸中的心与智也比先前更静',
     '「他心里的心」自相缠绕，主语压不出中心语',
     'even stiller than before, too, lay heart and mind within him'),
    (41, '⑥',
     '热与空气的能量，这各地一切生命赖以存在的要素，是他的侍女',
     '热与空气的能量，是任何地方一切生命赖以存在的要素，是他的侍女',
     'everywhere 误读作「这各地」，句子成了半截',
     'The energies of heat and air, essentials of all life everywhere'),
    (44, '①',
     '单个个人起初也许无法抵抗而不遭灾难',
     '单个人起初也许抵挡不住而不遭灾难',
     'might not be able to resist without disaster 被读成「无法抵抗而不遭灾难」，语义拧住',
     'What a single individual might not be able to resist at first without disaster'),
    (47, '①',
     '他世上想不出一句话可说。',
     '他想不出这世上有什么话可说。',
     'nothing in the world to say 直搬，中文语序断裂',
     'He could think of nothing in the world to say'),
    (55, '④',
     '为它的福祉工作了不可计数的年代',
     '为人类的福祉工作了不可计数的年代',
     '同段「它／他」已混指两个对象，此处 it 指 humanity，须点明',
     'that humanity for whose welfare it--or was it he?--had worked'),
    (81, '①',
     '不管怎样，他的『看见』察觉到那些接近的身影四面八方、上下左右、一下子全都看见，',
     '不管怎样，他的『看见』把那些接近的身影四面八方、上下左右、一下子全都收进眼底，',
     '「察觉到……全都看见」两个谓语打架，一句里两个「看见」',
     "His \"sight\" perceived the approaching figures all round, all over, all at once"),
    (84, '①',
     '是某种不倦服务的伟大慈悲，那不倦是不死的',
     '是某种不知疲倦、永不消亡的服务的伟大慈悲',
     '「那不倦是不死的」悬空判断，主谓接不上',
     'the great compassion of some untiring service that was deathless'),
    (90, '②',
     '撕扯着那限制、搅乱它们的推理表层意识的盖子。',
     '撕开那只盖子——那是推理的表层意识，限制着它们、搅乱着它们。',
     '「限制、搅乱它们的推理表层意识的」四个「的」把中心语「盖子」压没，拆成破折句',
     'tearing away the lid of the reasoning surface-consciousness that confined, confused them'),
    (102, '①',
     '他只在另一张人的脸上见过一次',
     '他只在另一个人的脸上见过一次',
     '「另一张人的脸」不成词',
     'he had seen once only in another human countenance'),
    (108, '⑦',
     '「——这里面有某种意义。我是说结果，」',
     '「这里面有某种意义。我是说结果，」',
     '说话人标签后的第二段引文不该以破折号起头（原破折号属迟疑，已由「他迟疑了一下」承担）',
     '"there\'s meaning in it of some kind. Results, I mean,"'),
    (113, '⑦',
     '花的图案、轮廓、形相，螺旋，圆圈……',
     '花的图案、轮廓、形相、螺旋、圆圈……',
     '并列项标点不统一（顿号／逗号混用）',
     'patterns, outlines, forms of flowers, spirals, circles'),
    (116, '①',
     '他那种对真理与知识的热忱，在那颗受震惊却诚实的心里表达得如此明白，以致菲利里',
     '那颗受震惊却诚实的心，把他对真理与知识的热忱表露得如此明白，以致菲利里',
     '「热忱在……心里表达得明白」主谓失配（心不会「表达」）',
     'So plainly was his passion for truth and knowledge legible in the expression of the shocked but honest mind'),
    (119, '①',
     '菲利里把握着的那只手又紧了一紧。',
     '菲利里把他握着的那只手又紧了一紧。',
     '「把握着的那只手」歧义（把握＝确信），且缺施动',
     'Fillery tightened his grip a second on the hand he held'),
    (122, '⑦',
     '「N. H.」声音的波浪似乎接住了他们的嗓音，把它放大。',
     '「N. H.」。声音的波浪似乎接住了他们的嗓音，把它放大。',
     '引文收束后另起一句，缺句末标点',
     '"N. H." The wave of sound seemed to take their voices and increase them'),
]

J_EDITS = [
    (0, '⑥',
     '那张纸白的脸上，有一种神秘而敬畏的神情',
     '那张惨白的脸上，有一种神秘而敬畏的神情',
     'sheet-white 逐字硬译作「纸白」，汉语不成词',
     'the expression of something mysterious and awed in the sheet-white face'),
    (3, '①',
     '他的神情里有某种怒视',
     '他神情里透着一股怒意',
     '「有某种怒视」动宾失配（怒视是动作，不是可「有」之物）',
     'Somewhere in his expression was a glare'),
    (33, '②',
     '若不是有那些完美正常的健康的明证，那简直可能是一种昏迷状态',
     '若不是有那些迹象表明他的健康完美正常，那简直可能是一种昏迷状态',
     '三个「的」串成的长定语，中心语「明证」被压没',
     'but for the obvious evidences of perfect normal health, it might have been a state of coma'),
    (61, '①',
     '只是还不必就在眼前——',
     '只是眼下还不行——',
     'not just yet 直搬成「不必就在眼前」，意思走偏且不通',
     'though not, however, just yet'),
    (65, '③',
     '他所寻求、所被影响的，就是你——作为你。',
     '他所寻求、并为之所动的，就是你——作为你。',
     '「所被影响的」被动式硬搬，与「所寻求」并列不齐',
     'we cannot be sure that it was you--as you--he sought and is affected by'),
    (79, '⑦',
     '我们半凭本能地服从某种未知状态——」他迟疑了一下，「——某种未知存在的法则。」',
     '我们半凭本能地服从某种未知的——」他迟疑了一下，「某种未知存在状态的法则。」',
     '说话人标签后的引文起首破折号重复；且第一段丢了「法则」，与原文断句不合',
     'We obey half instinctively the unknown laws of"--he hesitated a moment--"of some unknown state of being."'),
    (80, '⑥',
     '它像一阵大风浇在我身上',
     '它像一阵大风倾泻在我身上',
     '「浇」只用于液体，接「大风」是量词／动词误配',
     'It pours over me like a great wind, a wind with heat in it'),
    (88, '①',
     '那一幕，和一个她从未见过的青年——那必定带来痛苦的记忆；如果那是一见钟情，记忆就更痛苦。',
     '那一幕——和一个她从未见过的青年——必定带来痛苦的回忆；如果那是一见钟情，回忆就更痛苦。',
     '原文 must bring 的谓语被逗号切成断句，中文读来前后不接',
     'That scene with a young man she had never seen before must bring painful memories'),
    (88, '①',
     '而到目前为止，她一直完全不表态，而且令人钦佩。',
     '而到目前为止，她一直完全不表态，而且做得令人钦佩。',
     '「而且令人钦佩」悬空，缺被修饰的谓语',
     'and so far she had been entirely and admirably non-committal'),
    (89, '③',
     '她那种母性的、母亲般的本能是被需要的，而她必须服从它的提示',
     '她那种母性的本能是有人需要的，而她必须服从它的提示',
     'mothering, maternal 的英文同位重复照搬成「母性的、母亲般的」，中文同义反复',
     'that her mothering, maternal instinct was needed and that she must obey its prompting'),
]


def load(key):
    with open(os.path.join(BASE, key + '_zh.json'), encoding='utf-8', newline='') as f:
        return json.load(f)


def save(key, d):
    buf = io.StringIO()
    json.dump(d, buf, ensure_ascii=False, indent=1)
    with open(os.path.join(BASE, key + '_zh.json'), 'w', encoding='utf-8', newline='') as f:
        f.write(buf.getvalue() + '\n')


def apply_edits(key, edits):
    d = load(key)
    n0 = len(d)
    log = []
    for idx, cat, old, new, why, src in edits:
        assert 0 <= idx < len(d), (key, idx)
        assert old != new, (key, idx, 'no-op edit')
        assert old in d[idx], (key, idx, old)
        assert d[idx].count(old) == 1, (key, idx, 'not unique in para', old)
        d[idx] = d[idx].replace(old, new)
        assert new in d[idx]
        log.append((idx, cat, old, new, why, src))
    assert len(d) == n0
    save(key, d)
    print('%s: %d 段，改动 %d 条 -> 已落盘' % (key, len(d), len(log)))
    return log


def check(key):
    path = os.path.join(BASE, key + '_zh.json')
    bak = path + BAK
    d = json.load(open(path, encoding='utf-8'))
    b = json.load(open(bak, encoding='utf-8'))
    raw = open(path, 'rb').read()
    han = sum(1 for x in d for c in x if '\u4e00' <= c <= '\u9fff')
    problems = []
    if len(d) != len(b):
        problems.append('段数与备份不一致')
    if any(not str(x).strip() for x in d):
        problems.append('有空段')
    if '"' in ''.join(d):
        problems.append('残留 ASCII 直引号')
    if re.search(r'[。，；：、？！]{2,}', ''.join(d)) and '……' not in ''.join(d):
        problems.append('重复标点')
    for i, x in enumerate(d):
        for m in re.finditer(r'[\u4e00-\u9fff]\s+[a-z][A-Za-z]*\s+[\u4e00-\u9fff]', x):
            problems.append('[%d] 残留英文 %r' % (i, m.group(0)))
        if re.search(r'[。，][。，]', x):
            problems.append('[%d] 重复标点' % i)
        if not re.search(r'[。！？…—」』：；]$|[\u4e00-\u9fff）]$', x.strip()):
            problems.append('[%d] 段末标点可疑' % i)
    crlf = b'\r\n' in raw
    print('--- 自检 %s: 段数=%d 汉字=%d 换行=%s' % (key, len(d), han, 'CRLF' if crlf else 'LF'))
    print('    JSON 可解析 ✓ 长度=备份(%d) ✓ 无空段 ✓ ASCII引号=无 ✓' % len(b)
          if not problems else '    问题: ' + '; '.join(problems))
    return han, len(d), problems


def main():
    for key, edits in (('bm_i', I_EDITS), ('bm_j', J_EDITS)):
        path = os.path.join(BASE, key + '_zh.json')
        if not os.path.exists(path + BAK):
            shutil.copy2(path, path + BAK)
            print('backup made:', path + BAK)
        else:
            print('backup exists, kept:', path + BAK)
        log = apply_edits(key, edits)
        cats = {}
        for idx, cat, old, new, why, src in log:
            cats[cat] = cats.get(cat, 0) + 1
        print('    类别:', ' '.join('%s×%d' % (k, cats[k]) for k in sorted(cats)))
        check(key)
    return 0


if __name__ == '__main__':
    sys.exit(main())

ast.parse(open(__file__, encoding='utf-8').read())