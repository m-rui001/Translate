# -*- coding: utf-8 -*-
"""里尔克 Rainer Maria Rilke《Neue Gedichte》逐片润色落盘 c009/c00 c010/c00 c011/c00
（2026-11-26 逐片轮，第三组）

落盘方式：定位唯一子串 -> 替换 -> 断言全文命中数 == 1。
段数 / 行数 / 空行结构 / 换行符 / 诗行分行一律不变（本书诗句一节一段，不拆不并）。
"""
import ast
import sys

BASE = 'out'
EDITS = {
    # ============ c009/c00：门洞 III（大教堂雕像）／玫瑰窗／柱头／中世纪的上帝／停尸房 ============
    'c009/c00': [
        # ⑤ 段序号 canon：全册 I/II/III 作「一」「二」「三」（c006 已作「三」）；此处原为「题」，属坏字
        ('题\n', '三\n'),
        # ⑥ die Herzen（复数）＝众像的心，原译「那颗心」落成单数
        ('就这样，它们立着，那颗心已被止住', '就这样，它们立着，它们的心已被止住'),
        # ① 「爪步」不成词，Tatzen＝爪掌
        ('它们爪步的迟钝踩踏', '它们爪掌迟钝的踩踏'),
        # ① 「一个漩涡的圆圈」同义叠架，von eines Wirbels Kreis＝被漩涡的圈子
        ('那目光仿佛被一个漩涡的圆圈攫住', '那目光仿佛被漩涡的圈子攫住'),
        # ① 「再不知道自己什么」句法断裂，nichts mehr von sich weiß＝再也不认得自己
        ('随即沉没，再不知道自己什么，', '随即沉没，再也不认得自己，'),
        # ③⑦ 「升起来……随之而起」重复同一个动词（aufsteigend…erhebt），且「——；」标点相撞
        ('如同从一场梦的产儿中，从纷乱的折磨里升起来，次日随之而起——；拱顶的那些肋条，也这样从那纷乱的柱头里生出，',
         '如同次日从一场梦的产儿中、从纷乱的折磨里升起——拱顶的那些肋条，也这样从那纷乱的柱头里生出，'),
        # ① 「留下，……的，是扑翅的造物」主谓失配：lassen drin 的宾语就是那造物
        ('而在其中留下，拥挤着、谜一般缠绕着的，是扑翅的造物：',
         '而在其中留下拥挤着、谜一般缠绕的扑翅造物：'),
        # ③ 「头颅之猝然」文言语序直搬，das Plötzliche der Köpfe＝头颅的猝然一动
        ('它们的迟疑，它们的头颅之猝然，', '它们的迟疑，它们头颅的猝然一动，'),
        # ① 「省在自己心里」不成话，erspart＝攒下、省下
        ('而他们已把他省在自己心里', '而他们早已把他攒在自己心里'),
        # ③ 德语框形（über seine Zahlen zeigend kreisen）照搬，状语串被压散
        ('而他只该指着自己那无穷的数目盘旋，又像一座钟，',
         '而他只该在自己那些无穷的数字上方盘旋指点，又像一座钟，'),
        # ① 缺量词，「那惊骇的城里」读来悬空（die Leute der entsetzten Stadt）
        ('那惊骇的城里的百姓怕他的声音', '那座惊骇的城里的百姓怕他的声音'),
        # ① 缺主语：zu versöhnen weiß 的主语是 die Handlung（那情节），不是尸身
        ('仿佛真要事后补编出一桩情节，好与彼此、与这寒冷相调和，相连接；',
         '仿佛真的要事后补编出一桩情节，好让这情节把它们彼此、把它们与这寒冷调和起来，连接起来；'),
        # ⑥ 虚拟式 hätte … finden sollen＝本该找到，「该」吞掉了 soll
        ('该在他们口袋里找出个什么名字来呢？', '本该在他们口袋里找出个什么名字来呢？'),
        # ① 「厌倦，被人擦洗过了」逗号断主谓；er wurde nur ganz rein 是「只是被擦净」
        ('他们嘴边的厌倦，被人擦洗过了；\n\n擦不掉；只是擦得干干净净。',
         '他们嘴边的厌倦被人擦洗过了；\n\n擦不掉；只是被擦得干干净净。'),
    ],
    # ============ c010/c00：囚徒（DER GEFANGENE 正文） ============
    'c010/c00': [
        # ① 「那东西」承前无着（上片止于诗题），es＝落下的水汽，改「有什么」存其不确定
        ('那东西从岩上湿漉漉地落到旧石上。', '有什么从岩上湿漉漉地落到旧石上。'),
        # ⑥ Tropften sie doch＝但愿它们（水滴）滴得更快，原译误作单数
        ('但愿它滴得更快些', '但愿它们滴得更快些'),
    ],
    # ============ c011/c00：安魂曲（II）／豹／瞪羚／独角兽／圣塞巴斯蒂安／捐赠者／天使／罗马石棺／天鹅／童年／诗人／花边 ============
    'c011/c00': [
        # ⑤ 段序号 canon：全册作「一」「二」「三」，此处「第二部」为孤例（详见日志）
        ('第二部\r\n', '二\r\n'),
        # ⑦ 引号只套了中间两个，同串其余不加引号，体例不一
        ('叫作“然后”，叫作“往后”，叫作明年', '叫作然后，叫作往后，叫作明年'),
        # ⑥ Eiter＝脓，无「血」；voller Eiter 是「满含脓水」
        ('满是脓血', '满含脓水'),
        # ① 「会发了疯」时体不合
        ('而过去的一切会发了疯', '而过去的一切会发疯'),
        # ①③ 「上帝所是的一切」把 was Gott war 逐字搬来；wäre nur＝只会充当
        ('而上帝所是的一切，只会做你的看守', '而曾经是上帝的那一切，只会充当你的看守'),
        # ⑤⑥ Stäbe 同片两译（栏杆／栅栏），归一为出现较多的「栅栏」；Vorübergehn＝不断掠过
        ('他的目光被往复经过的栏杆磨得那样疲倦', '他的目光被不断掠过的栅栏磨得那样疲倦'),
        # ⑤ 诗题 canon 见本册目录「瞪羚（羚羊）」；dorcas 是拉丁种名，不作音译「多卡斯」
        ('羚羊多卡斯\r\n', '羚羊\r\n'),
        # ⑥ Einklang（和声、谐和）被吞，只剩「两个精选的词」
        ('两个精选的词怎能企及那', '两个精选词语的和声怎能企及那'),
        # ① 「把头留住倾听」／「在水里中断了自己」两处生硬（sich unterbricht＝中途停住）
        ('还把头颅留住倾听：如同林中沐浴时，沐浴者在水里中断了自己，',
         '还把头颅停住，倾听：如同林中沐浴时，沐浴者骤然停住，'),
        # ⑥ Der Beine elfenbeinernes Gestell＝腿的象牙骨架，原译「四腿如象牙」义转为比喻
        ('四腿如象牙的架子', '四条腿的象牙骨架'),
        # ④ 「它」指圣塞巴斯蒂安，与前文「他」并置，读者会错认
        ('仿佛从它的腰肋间弹出', '仿佛从他的腰肋间弹出'),
        ('可它暗暗地微笑，未受损伤', '可他暗暗地微笑，未受损伤'),
        # ⑤ 诗题 canon 见本册目录「捐赠者」（Stifter＝捐建祭坛者，非「创始人」）
        ('创始人\r\n', '捐赠者\r\n'),
        # ① 「紧紧绷在心里的，像把马握在手中」定语悬空，谓语被切断
        ('紧紧绷在心里的，像把马握在手中', '紧紧绷在心里，像把马握在手中'),
        # ①③ durch sein Herz geht … das ewig Kommende 句末分词照搬，主谓被拆散
        ('因为穿过他的心的，是那永远到来的、在旋转的，巨大而直立地升起。',
         '因为穿过他的心的，是那永远到来之物，它旋转着，巨大而笔直地升起。'),
        # ⑥ ihm 是与格（在他眼前、为他而设），不是「在他心中」
        ('深深的天空在他心中立满形象', '深深的天空在他眼前立满形象'),
        # ① 「打碎出来」不成词，brächen dich aus deiner Form heraus＝把你从形体里砸出来
        ('把你从你的形体里打碎出来', '把你从你的形体里砸出来'),
        # ③ hingestellt und verteilt 的被动直搬，「被分配」于人不通
        ('（正如我们被摆放和被分配的那样）', '（正如我们被摆放、被分置的那样）'),
        # ③ 冠词式「那装饰的石棺」；verziert＝饰满雕纹
        ('像从前在那装饰的石棺里', '像从前在那具饰满雕纹的石棺里'),
        # ① 「不再把握……那个根基」缺补语，读成「死亡把握根基」
        ('那不再把握我们每日站立其上的那个根基', '那不再把握住我们每日站立其上的那个根基'),
        # ① 「越来越王者」以名词充状语，三连排比在此断裂
        ('越来越成熟、越来越王者、越来越从容地乐于前行',
         '越来越成熟、越来越具王者气象、越来越从容地乐于前行'),
        # ① 「是它们的所有」缺中心语（das Ihre＝它们的所有物）
        ('是它们的所有，直到边缘都充满了形象', '是它们的所有物，直到边缘都充满了形象'),
        # ⑥ keine Stelle, auf der ich lebe＝没有一处我赖以生活的地方（Stelle 非「位置」）
        ('没有我赖以生活的位置', '没有一处我赖以生活的地方'),
        # ⑥⑤ 诗题 DIE SPITZE＝花边（下文「这一小片密实的花边」），非「尖端」；本册目录亦作「花边」
        ('尖端\r\n', '花边\r\n'),
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
    }


def run(piece):
    p = '%s/%s/final.txt' % (BASE, piece)
    before = read(p)
    text = before
    n = 0
    for old, new in EDITS[piece]:
        assert old in text, '%s: NOT FOUND %r' % (piece, old[:40])
        assert text.count(old) == 1, '%s: NOT UNIQUE %r' % (piece, old[:40])
        text = text.replace(old, new)
        n += 1
    a0 = stat(before)
    a1 = stat(text)
    assert a0['paras'] == a1['paras'], '%s paras %d->%d' % (piece, a0['paras'], a1['paras'])
    assert a0['lines'] == a1['lines'], '%s lines %d->%d' % (piece, a0['lines'], a1['lines'])
    assert a0['crlf'] == a1['crlf'], '%s crlf changed' % piece
    assert text.count('"') == 0 and text.count("'") == 0, '%s ASCII quote' % piece
    assert text.count('“') == text.count('”'), '%s quotes unpaired' % piece
    assert '⟦' not in text.replace('⟦i⟧', '').replace('⟦/i⟧', ''), '%s stray ⟦' % piece
    write(p, text)
    print('%s: edits=%d paras=%d==%d lines=%d==%d cjk=%d->%d crlf=%d' % (
        piece, n, a0['paras'], a1['paras'], a0['lines'], a1['lines'],
        a0['cjk'], a1['cjk'], a1['crlf']))
    return n


def main():
    total = 0
    for piece in ('c009/c00', 'c010/c00', 'c011/c00'):
        total += run(piece)
    print('total edits:', total)
    return 0


if __name__ == '__main__':
    ast.parse(open(__file__, encoding='utf-8').read())
    sys.exit(main())