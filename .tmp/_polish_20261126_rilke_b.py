# -*- coding: utf-8 -*-
"""里尔克 Rainer Maria Rilke《Neue Gedichte》逐片润色落盘 c005/c00 c006/c00 c007/c00 c008/c00
（2026-11-26 逐片轮，第二组）

落盘方式：定位唯一子串 -> 替换 -> 断言全文命中数 == 1。
段数 / 行数 / 空行结构 / 换行符 / 诗行分行一律不变（本书诗句一节一段，不拆不并）。
"""
import ast
import os
import shutil
import sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
STAMP = 'final.txt.bak_20261126'

EDITS = {
    # ============ c005/c00：亚比煞（III） ============
    'c005/c00': [
        # ⑥ abgenommner Baum＝果实被采尽的树（不是被斫倒的树）；下文「为你结果实的枝条」正是证据
        ('它像一棵被斫下的树：你曾借那些枝条结果，如今透过它们望进去，'
         '深处宛如未来将至的日子——我几乎认不出它了。',
         '它像一棵果实被采尽的树：那些曾为你结果实的枝条，如今透过它们，'
         '有一片深处望过来，仿佛来自将来的日子——我几乎认不出它了。'),
    ],
    # ============ c006/c00：约书亚的邦议会 / 浪子的出走 / 橄榄园 / 哀悼基督 … ============
    'c006/c00': [
        # ① 「它河口的过量」中心语悬空，Übermaß 作名词须落到「满溢」
        ('凭着它河口的过量冲决堤坝', '借着河口的满溢冲决堤坝'),
        # ① 「升上了一个喉咙」方位失当（in einem Mund＝升进一个喉咙）
        ('一齐升上了一个喉咙', '一齐升进一个喉咙'),
        # ⑥ 「以至」表程度延伸；此处是 so…daß 的结果，当作「以致」
        ('以至他们翻滚在地', '以致他们翻滚在地'),
        # ⑥ schlachtend＝正在屠杀的（主动），原译「屠杀的」可读成被杀的一代
        ('为了那屠杀的一代', '为了那正在屠杀的一代'),
        # ① 「坚固我们作这艰难的选择」缺连接词，stärke uns zu…是「坚固我们，好去作…」
        ('坚固我们作这艰难的选择', '坚固我们，好去作这艰难的选择'),
        # ① 「并且预感到地」不成词（von nah und ahnend＝从近处、怀着预感地）
        ('从近处并且预感到地看出', '从近处、怀着预感地看出'),
        # ⑥ unpersönlich＝非个人地、无人格地，不是「非人地」（那是 unmenschlich）
        ('那苦难是如何非人地', '那苦难是如何非个人地'),
        # ⑥ Ölgelände＝橄榄园地（Öl＝橄榄油），不是「油色的光」
        ('消融在油色的光里', '消融在橄榄园里'),
        # ① 「那发热双手的满是尘土之中」的字体叠架，中心语被压没（Staubigsein 的三重尘土仍保留）
        ('埋进那发热双手的满是尘土之中', '埋进那发热双手的尘土里'),
        # ③ wenn… 从句被甩到句末，问句主干与条件从句隔断
        ('而你为何要我一定说你在，当我再也找不到你本人。',
         '而当我再也找不到你本人时，你为何一定要我说你在？'),
        # ① 「那些迷失者，一切离弃他们」逗号流水，主谓挂不上（läßt alles los＝一切都撇下他们）
        ('那些迷失者，一切离弃他们', '那些自我迷失的人，一切离弃他们'),
        # ③ nicht…von… 机械对举，缺谓语落点（不是被我撕的，是被我的咬噬）
        ('爱人，不是我，是我的咬噬', '爱人，不是被我撕的，是被我的咬噬'),
        # ① 「因为这：」悬空，denn dieses 指下文那一串东西
        ('因为这：这些深处', '因为这一切：这些深处'),
        # ① 「如今仍要向他」缺谓语落点（zu ihm will＝要向他而去）
        ('如今仍要向他，仍围绕他求爱', '如今仍要向他而去，仍围绕他求爱'),
        # ⑥ eine Ferne＝一片远方；「一片远」不成词
        ('寂静：一片远……', '寂静：一片遥远……'),
        # ① 「他，忘却……的，而经历着……的」同位语套住全句，谓语丢失
        ('他，忘却我们所经历的，而经历着那排斥我们的。',
         '他忘却我们所经历的，而经历着那排斥我们的。'),
        # ① 悬空修饰语：「像一个否定者」贴着「主教座堂」，实指风暴（um…stürzt＝绕着猛扑）
        ('在风暴中，风暴扑向那雄伟的主教座堂，像一个否定者，想着，想着，人忽然觉得',
         '在风暴中，风暴像一个否定者绕着那雄伟的主教座堂猛扑，想着，想着，人忽然觉得'),
        # ③ 框形结构照搬：谓语「立」被推到两个状语之后，关系从句被搬成三个并列短语
        ('日晷上，一日的整个数字同时并列，同样真实，立在深深的平衡里，仿佛',
         '日晷上，一日的整个数字同时并列、同样真实地立在深深的平衡里，仿佛'),
        # ① 「知道我们的存在什么」缺介词（von unserm Sein＝对我们的存在）
        ('你这石造的，知道我们的存在什么？', '你这石造的，对我们的存在知道些什么？'),
        # ⑥ 「小贩拿来当围裙的一切」读成小贩拿它当围裙；实为孩子们把小贩摊上的一切当围裙穿
        ('以及小贩拿来当围裙的一切穿在身上', '以及小贩摊上的一切当围裙穿在身上'),
        # ① 「在某个更之中」把 mehr 硬当名词塞进介词短语，句子不成立
        ('而我们会在某个⟦i⟧更⟦/i⟧之中么？', '而我们会在某个人身上成为⟦i⟧更多⟦/i⟧么？'),
        # ③ seitdem… 从句后置直搬，主句「苍白而拒绝」与说明它的从句被隔断
        ('他立起的脸苍白而拒绝，倚在陡峭的枕间，自从世界以及世界对这世界的知，'
         '从他的感官上被撕下，落回那不关情的一年。',
         '自从世界以及世界对这世界的知，从他的感官上被撕下、落回那不关情的一年，'
         '他立起的脸便在陡峭的枕间苍白而拒绝。'),
    ],
    # ============ c007/c00：柱头（II） ============
    'c007/c00': [
        # ⑤ 组序号体例：全书作「一／二／三」，唯此处作「壹」
        ('壹\r\n\r\n它们就停在那里', '一\r\n\r\n它们就停在那里'),
        # ① 「与玄武岩的形体之别，只在……」主谓失配，unterschieden 是「借……而与……有别」
        ('它们停在那里，与玄武岩的形体之别，只在一圈光晕、一顶主教冠，间或在一抹微笑',
         '它们停在那里，与玄武岩中的形体只靠一圈光晕、一顶主教冠，间或一抹微笑，而有所区别'),
    ],
    # ============ c008/c00：门洞（II） ============
    'c008/c00': [
        # ③/⑥ handelnd auftritt 是「以行动者的身份登场」，原译「动了起来」丢了 auftreten；
        #       auf seiner Tiefe 是「在它深处……之上」，不是「从……里」
        ('这大门的幽暗便也如此，从它深处那座悲剧剧场里动了起来',
         '这大门的幽暗便也如此，在它深处那座悲剧剧场里登场，行动起来'),
    ],
}


def read(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()


def write(p, t):
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(t)


def cjk(t):
    return sum(1 for ch in t if '\u4e00' <= ch <= '\u9fff')


def stat(t):
    return {
        'paras': len([x for x in t.split('\n') if x.strip()]),
        'lines': len(t.split('\n')),
        'cjk': cjk(t),
        'crlf': t.count('\r\n'),
        'ascii_quote': t.count('"') + t.count("'"),
    }


def run(piece):
    d = os.path.join(BASE, piece)
    f = os.path.join(d, 'final.txt')
    b = os.path.join(d, STAMP)
    if not os.path.exists(b):
        shutil.copy2(f, b)
        print('backup made:', b)
    else:
        print('backup exists, not overwritten:', b)
    text = read(f)
    before = stat(text)
    n = 0
    for old, new in EDITS[piece]:
        assert old in text, 'NOT FOUND [%s]: %s' % (piece, old[:36])
        assert text.count(old) == 1, 'NOT UNIQUE [%s]: %s (%d)' % (piece, old[:36], text.count(old))
        text = text.replace(old, new)
        n += 1
    after = stat(text)
    assert before['paras'] == after['paras'], '%s paras %d->%d' % (piece, before['paras'], after['paras'])
    assert before['lines'] == after['lines'], '%s lines %d->%d' % (piece, before['lines'], after['lines'])
    assert before['crlf'] == after['crlf'], '%s crlf changed' % piece
    assert after['ascii_quote'] == 0, '%s has ASCII quotes' % piece
    assert '⟦' not in text.replace('⟦i⟧', '').replace('⟦/i⟧', ''), '%s stray ⟦' % piece
    write(f, text)
    print('%s: edits=%d paras=%d==%d lines=%d==%d cjk=%d->%d crlf=%d' % (
        piece, n, before['paras'], after['paras'], before['lines'], after['lines'],
        before['cjk'], after['cjk'], after['crlf']))
    return n


def main():
    total = 0
    for piece in ('c005/c00', 'c006/c00', 'c007/c00', 'c008/c00'):
        total += run(piece)
    print('total edits:', total)
    return 0


if __name__ == '__main__':
    ast.parse(read(__file__))
    sys.exit(main())