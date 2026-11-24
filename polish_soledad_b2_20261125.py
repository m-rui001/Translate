# -*- coding: utf-8 -*-
"""《百年孤独》通读润色 第2批（capitulo004-006）。"""
import ast
import glob
import shutil

ROOT = 'E:/Translate/work_soledad/out'
BAK = '.bak_20261125'

EDITS = [
    # ---------------- capitulo005 ----------------
    ('capitulo005',
     '一双半腿长的绑腿遮住脚踝上五年脚镣留下的疤',
     '一副从脚踝缠到膝盖的绑腿，遮住五年脚镣留下的疤',
     '①「一双半腿长的绑腿」语序拧，「半腿长」不知何指'),
    ('capitulo005',
     '三爪剥去她的贴身衣物',
     '三下扯去她的贴身衣物',
     '⑥tres zarpazos 误作「三爪」，中文无此量词'),
    ('capitulo005',
     '觉得皮埃特罗·克雷斯皮在这个原型雄性面前',
     '觉得皮埃特罗·克雷斯皮在这个十足的雄性标本面前',
     '③protómacho 直译为「原型雄性」，中文读者摸不着头脑'),
    ('capitulo005',
     '怎么也无法与曾祖母的学院式形象对上号',
     '怎么也无法与一位曾祖母庄重的画像对上号',
     '⑥imagen académica 误读为「学院式形象」'),
    ('capitulo005',
     '金银器工作台前五感俱警的奥雷里亚诺',
     '金银器工作台前全身戒备的奥雷里亚诺',
     '⑥「五感俱警」生造，中文不成词'),
    ('capitulo005',
     '还有一句谁也不信服的医学箴言：一钉拔一钉。',
     '还有一句谁也不信服的医学箴言：以钉拔钉，以毒攻毒。',
     '③Un clavo saca otro clavo 是成语，字面直搬成「一钉拔一钉」不通'),
    ('capitulo005',
     '乌尔苏拉百般折磨，阿玛兰妲愤然痛哭',
     '乌尔苏拉把她逼问得苦不堪言，阿玛兰妲愤然痛哭',
     '⑥Atormentada por Úrsula 原是被动，译文倒成「乌尔苏拉百般折磨」'),
    ('capitulo005',
     '早已失去了对死罪的恶意',
     '早已不把死罪当作一回事',
     '⑥habían perdido la malicia del pecado mortal，「恶意」误读'),
    ('capitulo005',
     '是个因神职不获感恩而变得冷硬的老人',
     '是个因教务无人感恩而变得冷硬的老人',
     '①「神职不获感恩」名词短语塞进状语，读不通'),
    ('capitulo005',
     '奥雷里亚诺却对这阴谋避之不及',
     '奥雷里亚诺却对这阴谋不寒而栗',
     '⑥「避之不及」是躲不开之意，与文意（畏避）相反'),
    ('capitulo005',
     '选举的临近，是那根让他重新找到颠覆线团的线头。',
     '选举的临近，才成了让他重新抓住密谋线头的那根线索。',
     '①「找到颠覆线团的线头」线头线团缠作一团，句意过滤不出'),
    ('capitulo005',
     '把他卷进这阵去看医生的风里的，纯粹是一时好奇',
     '把他卷进这桩看医生的把戏里的，纯粹是一时好奇',
     '①「卷进这阵……风里」搭配不成立'),
    ('capitulo005',
     '皮埃特罗·克雷斯皮礼拜五收到一封信，宣告他母亲即将离世',
     '皮埃特罗·克雷斯皮礼拜五收到一封信，信中说他的母亲即将离世',
     '①「一封信，宣告……」信无口，主语失当'),

    # ---------------- capitulo006 ----------------
    ('capitulo006',
     '他每天读多达四份报纸，好把脑子里闪过的念头统统下达指令。',
     '他每天读多达四份报纸，好把脑子里闪过的每个念头都下达成一道指令。',
     '①「把念头下达指令」动宾杂糅'),
    ('capitulo006',
     '乌尔苏拉终于能告诉他一个像是真的的消息。',
     '乌尔苏拉终于能告诉他一个像是真切的消息。',
     '②「像是真的的消息」两个「的」相撞，且易读成「真的消息」'),
    ('capitulo006',
     '一小时接一小时地弹齐特琴。一天夜里他唱了起来。马孔多在恍惚中醒来，被一把不属于尘世的齐特琴',
     '一小时接一小时地弹齐特拉琴。一天夜里他唱了起来。马孔多在恍惚中醒来，被一把不属于尘世的齐特拉琴',
     '⑤cítara 全册两译（齐特拉琴／齐特琴），归一'),
    ('capitulo006',
     '而在阿尔卡蒂奥执政的十一个月里，此人不仅卷走了捐税',
     '而在他执政的十一个月里，此人不仅卷走了捐税',
     '④上句主语为何塞·阿尔卡蒂奥，「此人」指代不清'),
    ('capitulo006',
     '行刑队长是即决的行家',
     '行刑队长是擅长即决处决的行家',
     '③「即决的行家」压缩过度，中文不成句'),
    ('capitulo006',
     '而同居未婚的桑塔索菲亚·德拉彼达又怀了身孕',
     '而尚未婚配、与他同居的桑塔索菲亚·德拉彼达又怀了身孕',
     '①「同居未婚的」定语生硬'),
]

# 全册专名统一（按出现次数多者为 canon）
GLOBAL = [
    ('神甫', '神父', '⑤同一职衔全册两译（神父×61／神甫×16），归一'),
    ('安帕罗', '安帕萝', '⑤Amparo 全册两译（安帕萝×8／安帕罗×4），归一'),
]

CHAPTERS = [f'capitulo{i:03d}' for i in range(1, 21)]


def main():
    by_chapter = {}
    for ch, old, new, why in EDITS:
        by_chapter.setdefault(ch, []).append((old, new, why))

    total = 0
    for ch in CHAPTERS:
        files = sorted(glob.glob(f'{ROOT}/{ch}/c*/final.txt'))
        texts = {}
        for f in files:
            with open(f, encoding='utf-8', newline='') as fh:
                texts[f] = fh.read()
        before = {f: t for f, t in texts.items()}
        n = 0
        for old, new, why in by_chapter.get(ch, []):
            hits = [f for f, t in texts.items() if old in t]
            cnt = sum(t.count(old) for t in texts.values())
            assert len(hits) == 1 and cnt == 1, f'{ch} 定位失败: {why} | {old!r} hits={hits} n={cnt}'
            f = hits[0]
            texts[f] = texts[f].replace(old, new, 1)
            n += 1
        for old, new, why in GLOBAL:
            for f in texts:
                c = texts[f].count(old)
                if c:
                    texts[f] = texts[f].replace(old, new)
                    n += c
        if n:
            for f, t in texts.items():
                if t == before[f]:
                    continue
                shutil.copyfile(f, f + BAK)
                with open(f, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(t)
            print(f'{ch}: {n} 处')
            total += n
    print('total', total)


main()
ast.parse(open(__file__, encoding='utf-8').read())