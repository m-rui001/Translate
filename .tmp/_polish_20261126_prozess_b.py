# -*- coding: utf-8 -*-
"""prozess c007/c01–c05 逐片润色落盘脚本（2026-11-26，batch b）。

铁律：只做「定位唯一子串 → 替换 → 断言命中数」，不整文件重写；
读写用 newline='' 保住原换行符；段数/行数不变。
"""
import ast
import os

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'out', 'c007')


def load(piece):
    p = os.path.join(OUT, piece, 'final.txt')
    with open(p, encoding='utf-8', newline='') as fh:
        return p, fh.read()


def save(p, text, old_text):
    # 结构自检：行数、空行数、段数一律不变
    def stat(t):
        lines = t.replace('\r\n', '\n').split('\n')
        return len(lines), sum(1 for x in lines if not x.strip()), t.count('\r\n')
    assert stat(text) == stat(old_text), 'structure changed!'
    with open(p, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


def sub(text, old, new, n=1, tag=''):
    cnt = text.count(old)
    assert cnt == n, f'{tag}: expect {n} hit, got {cnt} for {old!r}'
    return text.replace(old, new)


def c01(t):
    log = []
    # ① notwendigerweise 误作「不由自主」：这里是「必然」，不是「不由己」
    o = '会不由自主地自动用到你身上'
    n = '必然会自动用到你身上'
    t = sub(t, o, n, tag='c01-1'); log.append((o, n, '⑥词义误读（notwendigerweise＝必然，非「不由自主」）'))
    # ⑤ Erna 全册 canon 为「埃尔娜」
    t = sub(t, '爱尔娜', '埃尔娜', tag='c01-2'); log.append(('爱尔娜', '埃尔娜', '⑤专名归一（全书「埃尔娜」2 见，此片「爱尔娜」孤例）'))
    # ① 两个分句硬连，「我看你留在这里＋事情会被耽误」主语与谓语打架
    o = '只是因为我看你留在这里，事情会被你的无所谓耽误，觉得不如让我替你去办'
    n = '只是因为我觉得，你若留在这里，事情会被你的无所谓耽误，不如我替你去办'
    t = sub(t, o, n, tag='c01-3'); log.append((o, n, '①读不通（补出「我觉得」后，条件从句与主句各归其位）'))
    # ① 「我也有点觉得突然」视角错位（mir kam es unerwartet＝对我来说是意外的）
    o = '你的案子我也有点觉得突然'
    n = '你的案子对我来说也有点突然'
    t = sub(t, o, n, tag='c01-4'); log.append((o, n, '①读不通（用「对我来说」承住 mir，去掉「觉得」的错位主语）'))
    # ① 「把K.拉到身后塞进车里」动作链断裂（hinter sich in den Wagen＝拉着跟在身后进车）
    o = '一边把K.拉到身后塞进车里'
    n = '一边拉着K.跟在自己身后钻进车里'
    t = sub(t, o, n, tag='c01-5'); log.append((o, n, '①读不通（「拉到身后」与「塞进车里」接不上，改为随行入车）'))
    return t, log


def c02(t):
    log = []
    # ⑥/① als Menschen＝对他这个人；「是把他当人看」既添义又添一个「他」
    o = '“可我个人尤其对他，是把他当人看，对他抱着极大的信任。”'
    n = '“可我个人对他这个人，尤其抱着极大的信任。”'
    t = sub(t, o, n, tag='c02-1'); log.append((o, n, '⑥词义误读（als Menschen 修饰 zu ihm，非「把他当人看」）'))
    # ⑥ freundlicher 指房间给人的感觉＝亲切，不是「和气」（用于人的态度）
    o = '那时我觉得这里还和气些'
    n = '那时我觉得这里还亲切些'
    t = sub(t, o, n, tag='c02-2'); log.append((o, n, '⑥词义误读（damals schien es mir freundlicher 说的是屋子）'))
    return t, log


def c03(t):
    log = []
    # ⑤ Onkel 全书 canon「舅舅」（75 见），此片一律「叔叔」（16 见）
    c = t.count('叔叔')
    t = sub(t, '叔叔', '舅舅', n=c, tag='c03-onkel'); log.append(('叔叔 ×%d' % c, '舅舅', '⑤称谓归一（全书「舅舅」75 见为 canon）'))
    # ⑤ 侄子：舅舅的甥辈＝外甥（全书「舅舅」确立母系，c005/c00 亦用「外甥」）
    c = t.count('侄子')
    t = sub(t, '侄子', '外甥', n=c, tag='c03-neffe'); log.append(('侄子 ×%d' % c, '外甥', '⑤亲属称谓（Onkel 已定「舅舅」，Neffe 相应作「外甥」）'))
    # ⑤ Kanzleidirektor：全书 canon「文书主任」（c04 9 见），此片「书记长」（4 见）
    c = t.count('书记长')
    t = sub(t, '书记长', '文书主任', n=c, tag='c03-kanzlei'); log.append(('书记长 ×%d' % c, '文书主任', '⑤职衔归一（Kanzleidirektor 全书 canon 为「文书主任」）'))
    # ⑤ Prokurist：全书 canon「襄理」（17 见），此片「代理经理」（2 见）
    c = t.count('代理经理')
    t = sub(t, '代理经理', '襄理', n=c, tag='c03-prokurist'); log.append(('代理经理 ×%d' % c, '襄理', '⑤职衔归一（Prokurist 全书 canon 为「襄理」）'))
    # ① 「还在喉咙里打转」缺主语，悬空
    o = '他在怒气初涌、还在喉咙里打转的时候，说得还相当含糊。'
    n = '他在怒气初涌、话音还在喉咙里打滚的时候，说得还相当含糊。'
    t = sub(t, o, n, tag='c03-1'); log.append((o, n, '①读不通（im ersten Gurgeln＝话音在喉咙里打滚，补出主语）'))
    # ⑥ was ich verlange＝我所要求的；「有求于人的事」添了原文没有的「求人」
    o = '我要是有求于人的事办不到，我也不会开口。'
    n = '我要求的事若办不到，我也不会提。'
    t = sub(t, o, n, tag='c03-2'); log.append((o, n, '⑥词义误读（was ich verlange＝我要求的事，非「有求于人」）'))
    # ① 「仿佛这是长久分别」缺量词与中心语，句尾单薄
    o = '把手递给他，仿佛这是长久分别。'
    n = '把手递给他，仿佛这是一场长久的告别。'
    t = sub(t, o, n, tag='c03-3'); log.append((o, n, '①读不通（einen Abschied＝一场告别，补量词）'))
    # ① 「和解地走近」状语生造（versöhnt＝气已消）
    o = '舅舅已经和解地走近了些'
    n = '舅舅已经消了气，走近了些'
    t = sub(t, o, n, tag='c03-4'); log.append((o, n, '①读不通（versöhnt 是状态，不是方式状语）'))
    # ① 「仿佛……瘫痪，他现在看上去多么有精神」前后失接（so kräftigt）
    o = '仿佛“探望病人”这一念头此前一直使律师瘫痪，他现在看上去多么有精神'
    n = '仿佛“探望病人”这一念头此前一直使律师瘫痪，他现在看上去却多么有精神'
    t = sub(t, o, n, tag='c03-5'); log.append((o, n, '①读不通（补「却」承住 so kräftigt 的转折）'))
    # ③ wenn 从句后置直搬
    o = '我当然会感到荣幸，如果我的力量足以应付这项极其艰巨的任务'
    n = '如果我的力量足以应付这项极其艰巨的任务，那我当然会感到荣幸'
    t = sub(t, o, n, tag='c03-6'); log.append((o, n, '③外语句法（德语 wenn 从句后置，汉语须前置）'))
    # ① nichts unversucht lassen 的双重否定绕成一团
    o = '无论如何我不愿有任何尝试不做'
    n = '无论如何，我都不愿放过任何尝试'
    t = sub(t, o, n, tag='c03-7'); log.append((o, n, '①读不通（双重否定绕口，正说「不放过任何尝试」）'))
    return t, log


def c04(t):
    log = []
    # ⑤ Onkel 归一「舅舅」（此片「叔父」4 见）
    c = t.count('叔父')
    t = sub(t, '叔父', '舅舅', n=c, tag='c04-onkel'); log.append(('叔父 ×%d' % c, '舅舅', '⑤称谓归一（全书「舅舅」为 canon）'))
    # ⑤ Pflegerin 归一「女看护」
    t = sub(t, '女护理', '女看护', n=1, tag='c04-pflegerin'); log.append(('女护理', '女看护', '⑤称谓归一（Pflegerin 全书 canon 为「女看护」）'))
    # ① 「来客中的舅舅」——席上只一位舅舅
    o = '他微微向来客中的舅舅点点头'
    n = '他微微向舅舅点点头'
    t = sub(t, o, n, tag='c04-1'); log.append((o, n, '①读不通（「来客中的」是误加的限定）'))
    # ⑥ schütter＝稀疏，不是「颤巍巍」
    o = '那些胡子颤巍巍的老先生们'
    n = '那些胡子稀疏的老先生们'
    t = sub(t, o, n, tag='c04-2'); log.append((o, n, '⑥词义误读（mit den schüttern Bärten＝胡子稀疏）'))
    return t, log


def c05(t):
    log = []
    # ⑤ Pflegerin 归一「女看护」
    c = t.count('护士')
    t = sub(t, '护士', '女看护', n=c, tag='c05-pflegerin'); log.append(('护士 ×%d' % c, '女看护', '⑤称谓归一（Pflegerin 全书 canon 为「女看护」，此片孤用「护士」）'))
    # ① 「小女看护」连读拗口，改「小看护」
    o = '最后是这个小女看护'
    n = '最后是这个小看护'
    t = sub(t, o, n, tag='c05-1'); log.append((o, n, '①读不通（两个「女」字连读拗口）'))
    # ④/⑥ 那声「哦」是莱妮自己发出来的（diesen kleinen Ausruf），不是K.的话
    o = '因K.这句话和这一声“哦”，倒添了几分居高临下的神气'
    n = '因K.这句话和自己这一声“哦”，倒添了几分居高临下的神气'
    t = sub(t, o, n, tag='c05-2'); log.append((o, n, '④指代（diesen Ausruf 是莱妮自己的惊叹，非K.所言）'))
    # ⑥ niemals＝绝不，不是「未必」
    o = '可他从来也未必像画上这副样子'
    n = '可他绝不可能像画上这副样子'
    t = sub(t, o, n, tag='c05-3'); log.append((o, n, '⑥词义误读（niemals auch nur ähnlich＝绝不可能有几分像）'))
    # ⑦ 反意问句前缺逗号
    o = '“那么我要是不招认，您就帮不了我对吗？”'
    n = '“那么我要是不招认，您就帮不了我，对吗？”'
    t = sub(t, o, n, tag='c05-4'); log.append((o, n, '⑦体例（反意问「对吗」前须有逗号）'))
    return t, log


def main():
    total = 0
    for piece, fn in (('c01', c01), ('c02', c02), ('c03', c03), ('c04', c04), ('c05', c05)):
        p, old = load(piece)
        new, log = fn(old)
        assert new != old
        save(p, new, old)
        cjk = sum(1 for ch in new if '\u4e00' <= ch <= '\u9fff')
        paras = sum(1 for x in new.replace('\r\n', '\n').split('\n') if x.strip())
        print(f'{piece}: 改动 {len(log)} 条, 段数 {paras}, 汉字 {cjk}, crlf {new.count(chr(13)+chr(10))}')
        for o, n, why in log:
            print(f'  - {why}\n    旧: {o}\n    新: {n}')
        total += len(log)
    print('总计改动', total, '条')


main()
ast.parse(open(__file__, encoding='utf-8').read())
print('ast.parse self-check OK')