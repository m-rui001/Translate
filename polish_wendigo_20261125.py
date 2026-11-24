# -*- coding: utf-8 -*-
"""《温迪戈》(wendigo_a / wendigo_b) 通读润色 2026-11-25。

原则：只改「读不通 / 的字堆叠 / 外语句法 / 指代 / 专名 / 硬伤 / 体例」七类；
不重译、不加形容词、不把暗示写成明说。定位唯一子串 → 替换 → 断言命中数 == 1。
底本：work_batch_20261124/blackwood_wendigo.txt（Gutenberg 15469）。
不 commit、不 push、不改 MEMORY.md、不动 out/*.epub。
"""
import ast
import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent / 'work_batch_20261124'

EDITS = {
    # ── 上册 ─────────────────────────────────────────────────────────────
    'wendigo_a': [
        # ⑤ 职衔归一：全册「大夫」29 处 vs「医生」12 处（下册通篇作「大夫」，汉克口中的
        #    Doc 也译「大夫」），以多者为 canon。此处改 11 处，保留「管医生叫『大夫』」
        #    一句里的类名用法。
        ('卡瑟卡特医生也在其中', '卡瑟卡特大夫也在其中'),
        ('卡瑟卡特医生的敬意', '卡瑟卡特大夫的敬意'),
        ('随卡瑟卡特医生和汉克', '随卡瑟卡特大夫和汉克'),
        ('卡瑟卡特医生和外甥经过', '卡瑟卡特大夫和侄子经过'),
        ('舅舅合住的帐篷里说。卡瑟卡特医生当时', '叔叔合住的帐篷里说。卡瑟卡特大夫当时'),
        ('卡瑟卡特医生又一次注意到', '卡瑟卡特大夫又一次注意到'),
        ('汉克转向医生。', '汉克转向大夫。'),
        ('卡瑟卡特医生看出再谈下去已不可能，便学外甥的样子',
         '卡瑟卡特大夫看出再谈下去已不可能，便学侄子的样子'),
        ('医生注意到这些细节', '大夫注意到这些细节'),
        ('卡瑟卡特医生随后也躺下了', '卡瑟卡特大夫随后也躺下了'),
        ('比如引到汉克和医生身上', '比如引到汉克和大夫身上'),
        # ⑤ 亲属称谓归一：下册通篇「叔叔/侄子」（18 处），上册「舅舅/外甥」（6 处）
        ('还有他的外甥、年轻的辛普森', '还有他的侄子、年轻的辛普森'),
        ('等外甥听不见了', '等侄子听不见了'),
        ('他忽然记起舅舅讲过', '他忽然记起叔叔讲过'),
        # ⑥ 硬伤：Hank knew him and swore by him（信得过他），非「拿他起誓」
        ('汉克了解他，也拿他起誓', '汉克了解他，也极信服他'),
        # ① 读不通：sleepiness fought in his mind with a faint curiosity
        ('倦意与睡意在心头同一种隐约的好奇交战', '倦意与睡意在他心头同那一点隐约的好奇交战'),
        # ⑥ 硬伤：betrayed itself by no outer sign → 「外形」应为「形迹」
        ('却不露半点外形', '却不露半点形迹'),
        # ⑥ 硬伤：though as yet, of course, untraveled（当然还没出过远门）
        ('虽然自然还没见过世面', '只是当然还没出过远门'),
        # ② 三连「的」压住中心语
        ('这些遥远孤绝的森林的凄怆壮丽，颇叫他生出自身的渺小之感而被压倒',
         '这些遥远孤绝的森林自有一种凄怆的壮丽，叫他生出自身的渺小之感，几乎被压倒'),
        # ② 三连「的」：「……的哀婉的、近乎忧郁的船歌」
        ('唱了一支伐木人和捕兽人借以减轻劳苦的哀婉的、近乎忧郁的船歌',
         '唱起一支船歌，哀婉近乎忧郁——伐木人和捕兽人就是唱着它减轻劳苦的'),
        # ⑥ 硬伤：into the sea of darkness（海一般的黑暗），非「黑暗的海」
        ('越过他的肩膀朝黑暗的海张望', '越过他的肩膀朝那一片海似的黑暗里张望'),
        # ⑥ 硬伤：Punk at halfway house 是「半路上的营地」，林莽里没有「馆子」
        ('老帕克在半路馆子里', '老帕克守在半路上的营地'),
        # ⑥ 硬伤：partly… partly… partly 译成三个「一半」，加不出整份
        ('他把缘由一半归给', '他把缘由一部分归给'),
        ('一半归给孤寂的魔咒，再一半归给过度疲劳', '一部分归给孤寂的魔咒，再一部分归给过度疲劳'),
        # ⑦ 体例：同一句呼号（My feet of fire! My burning feet of fire!）上下册须一致
        ('我的火的脚！我烧着的火的脚！哦！哦！这样的高度，这样火的速度',
         '我的火脚！我燃烧的火脚！哦！哦！这样的高度，这样火一样的速度'),
        # ③ 外语句法：with something less than his usual frankness
        ('坦率得不及往常', '不如往常坦率'),
    ],
    # ── 下册 ─────────────────────────────────────────────────────────────
    'wendigo_b': [
        # ⑤ 称谓归一：迪法尤口称 Boss Simpson，上册作「头儿」，此处「老板」归一
        ('「我在这儿呢，辛普森老板', '「我在这儿呢，辛普森头儿'),
        # ⑦ 体例：同一呼号三处措辞不一（「烧着的火脚」），与上册统一为「燃烧的火脚」
        ('哦，我的火脚！我烧着的火脚……！」那悲苦的声音',
         '哦，我的火脚！我燃烧的火脚……！」那悲苦的声音'),
        ('哦，哦！我的火脚！我烧着的火脚！」', '哦，哦！我的火脚！我燃烧的火脚！」'),
        ('哦，哦！我的火脚！我烧着的火脚……！」随后消散了',
         '哦，哦！我的火脚！我燃烧的火脚……！」随后消散了'),
        ('看见我那双火烧的、烧着的脚了', '看见我那双火脚、那双燃烧的脚了'),
        # ⑥ 硬伤：bladder faces（膀胱吹的假脸）误作「鳔胶脸谱」；Ludgate Hill 通译勒德门山
        ('柳德门山上货郎们吹起来的那些鳔胶脸谱', '勒德门山上货郎们吹起来的那种膀胱假脸'),
        # ⑦ 体例：下册 5 处分节行用了双倍间隔（＊　　＊　　…），与上册及全库 canon
        #    「＊　＊　＊　＊　＊」（64 处）不一致，整行归一（三段式：old, new, 期望命中数）
        ('＊\u3000\u3000＊\u3000\u3000＊\u3000\u3000＊\u3000\u3000＊',
         '＊\u3000＊\u3000＊\u3000＊\u3000＊', 5),
    ],
}


def main():
    total = 0
    for key, pairs in EDITS.items():
        p = BASE / (key + '_zh.json')
        bak = p.with_name(p.name + '.bak_20261125')
        if not bak.exists():
            shutil.copy2(p, bak)
        text = p.read_text(encoding='utf-8', newline='')
        before = json.loads(text)
        n_par = len(before)
        want_sum = 0
        for item in pairs:
            old, new = item[0], item[1]
            want = item[2] if len(item) > 2 else 1
            hit = text.count(old)
            assert hit == want, 'hit mismatch: %s -> %r (%d != %d)' % (
                key, old[:24], hit, want)
            text = text.replace(old, new)
            want_sum += want
        data = json.loads(text)
        assert len(data) == n_par, (key, n_par, len(data))
        assert all(isinstance(s, str) and s.strip() for s in data), key
        changed = [i for i, (a, b) in enumerate(zip(before, data)) if a != b]
        assert 0 < len(changed) <= want_sum, (key, len(changed), want_sum)
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        total += len(pairs)
        print('%s: %d 处替换（涉及 %d 段）, 段数 %d（改前==改后）'
              % (key, want_sum, len(changed), n_par))
        total += want_sum - len(pairs)
    print('合计 %d 处替换' % total)


main()
ast.parse(open(__file__, encoding='utf-8').read())