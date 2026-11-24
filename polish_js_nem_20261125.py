# -*- coding: utf-8 -*-
"""《约翰·塞伦斯医生奇案》第三案《火的报复》（The Nemesis of Fire）通读润色。

特别处理：js_nem_a 全片 184 段被整章套在「」里（内层用『』甚至「「」」），
与全书体例（叙述段不加引号、对白用「」、嵌套用『』）冲突。此处逐段剥掉
最外层一对引号，并把原内层『』降一级为「」，三级嵌套（『…『…』…』）保留『』。
转换后逐段断言引号配平。
"""
import json, ast, io

BASE = 'work_batch_20261124/'


def unquote_outer(p):
    assert p.startswith('「') and p.endswith('」'), p[:30]
    s = p[1:-1]
    out, depth = [], 0
    for ch in s:
        if ch == '『':
            if depth == 0:
                out.append('「'); depth = 1
            else:
                out.append('『'); depth = 2
        elif ch == '』':
            if depth == 2:
                out.append('』'); depth = 1
            elif depth == 1:
                out.append('」'); depth = 0
            else:
                out.append('』')
        else:
            out.append(ch)
    assert depth == 0, p[:40]
    r = ''.join(out)
    assert r.count('「') == r.count('」'), p[:40]
    return r


EDITS = [
    # ① 读不通：「这宅子里的热得」多一个「的」
    ('js_nem_a', 35, '只是这宅子里的热得让我觉得反常。', '只是这宅子热得让我觉得反常。'),
    # ⑥ 硬伤：错字「月人」（两个男人）
    ('js_nem_a', 58, '见两个月人正站在炉火前等我。', '见两个男人正站在炉火前等我。'),
    # ⑦ 体例：连用「、，」
    ('js_nem_a', 67, '即将聆听或许离奇、，却也神秘之事的这层事实',
     '即将聆听或许离奇却也神秘之事的这层事实'),
    # ① 读不通：「我是二十年前我长兄」主谓挤叠
    ('js_nem_a', 79, '「我是二十年前我长兄去世时继承了这地方，」',
     '「我是在二十年前长兄去世时继承了这地方，」'),
    # ⑥ 硬伤：长兄（elder brother）全书误作「弟弟」六处
    ('js_nem_b', 27, '讲过他弟弟和猎场看守二十年前是怎么死的。', '讲过他哥哥和猎场看守二十年前是怎么死的。'),
    ('js_nem_b', 107, '「您是说我弟弟——！」', '「您是说我哥哥——！」'),
    ('js_nem_c', 89, '「一条地道，我弟弟造的！」', '「一条地道，我哥哥造的！」'),
    ('js_nem_c', 90, '「你的弟弟，毫无疑问，也曾和你一样备受折磨；', '「你的哥哥，毫无疑问，也曾和你一样备受折磨；'),
    ('js_nem_c', 93, '「你弟弟从它安息了几个世纪的地方取出来', '「你哥哥从它安息了几个世纪的地方取出来'),
    ('js_nem_d', 10, '「把木乃伊带到这儿来的那位旅行家弟弟，想必也曾被它纠缠，」',
     '「把木乃伊带到这儿来的那位旅行家哥哥，想必也曾被它纠缠，」'),
    # ⑤ 术语统一：护壳（shell of protection）
    ('js_nem_b', 33, '你被一个保护你的壳罩围着。把自己想成待在一个护罩之内，',
     '你被一层护壳围着。把自己想成待在一层护壳之内，'),
    ('js_nem_b', 33, '这样一个由你的思想、意志和想象筑成的壳完完全全罩着你',
     '这样一个由你的思想、意志和想象筑成的护壳完完全全罩着你'),
    ('js_nem_c', 9, '想象一个保护壳环绕着你', '想象一层护壳环绕着你'),
    # ⑤ 术语统一：elemental = 元素灵／火之元素灵（原「火精」「精怪」「元素之灵」并存）
    ('js_nem_b', 130, '本性即属元素之灵', '本性即属元素灵'),
    ('js_nem_c', 49, '「是为它们的主人开路的火精，」', '「是为它们的主人开路的火之元素灵，」'),
    ('js_nem_c', 67, '当初正是它派遣了那火精去执行使命的', '当初正是它派遣了那火之元素灵去执行使命的'),
    ('js_nem_c', 86, '「一个火精，在底比斯的时代', '「一个火之元素灵，在底比斯的时代'),
    ('js_nem_c', 95, '他们懂得如何把一种精怪之力系附在木乃伊上', '他们懂得如何把一种元素灵之力系附在木乃伊上'),
    ('js_nem_c', 95, '就这一例而言，那是一个火精。', '就这一例而言，那是一个火之元素灵。'),
    ('js_nem_d', 12, '它始终在其使者——那精怪——背后操纵着', '它始终在其使者——那元素灵——背后操纵着'),
    # ① 读不通：「在我看来自五官」
    ('js_nem_c', 43, '但在我看来自五官——眼、鼻、嘴——依旧未变',
     '但在我看来，五官——眼、鼻、嘴——依旧未变'),
    # ⑦ 体例：跨段引语段末引号缺失
    ('js_nem_b', 105, '大体就像这个世纪的实干家们驾驭蒸汽和电力一样。',
     '大体就像这个世纪的实干家们驾驭蒸汽和电力一样。」'),
    ('js_nem_d', 7, '以防亵渎，尤其防止毁坏。', '以防亵渎，尤其防止毁坏。」'),
]

cache = {}
def load(k):
    if k not in cache:
        cache[k] = json.load(io.open(BASE + k + '_zh.json', encoding='utf-8', newline=''))
    return cache[k]

d = load('js_nem_a')
cache['js_nem_a'] = [unquote_outer(p) for p in d]

for k, i, old, new in EDITS:
    d = load(k)
    p = d[i]
    assert old in p, (k, i, old)
    assert p.count(old) == 1, (k, i, 'not unique')
    d[i] = p.replace(old, new)

for k, d in cache.items():
    with io.open(BASE + k + '_zh.json', 'w', encoding='utf-8', newline='') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(k, len(d))

ast.parse(open(__file__, encoding='utf-8').read())