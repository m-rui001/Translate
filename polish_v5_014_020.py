# -*- coding: utf-8 -*-
"""通读润色 v5 chunk014–chunk020：定位唯一子串 → 替换 → 断言命中数。"""
import ast, io, os, shutil, sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work_proust', 'out_ind', 'v5')

EDITS = {
    '014': [
        # ⑥ 硬伤：「这对男爵是莫大的恩典」说的是莫雷尔天天陪男爵喝茶，不是「我碰上他们」
        ('常常正是德·夏尔吕先生和莫雷尔去絮比安家喝茶的钟点，我在院子里碰上他们——这对男爵是莫大的恩典。',
         '常常正是德·夏尔吕先生和莫雷尔去絮比安家喝茶的钟点——这对男爵是莫大的恩典——我在院子里碰上他们。'),
    ],
    '015': [
        # ⑥ 异体字/错别字：全库「这份」为 canon
        ('德·夏尔吕先生骨子里对这分亲昵还挺受用。',
         '德·夏尔吕先生骨子里对这份亲昵还挺受用。'),
    ],
    '016': [
        # ⑤ 术语同册不一致：同一说法 canon 为「付茶钱」
        ('我个人的看法是，“请喝茶”这话准是莫雷尔自己先说的',
         '我个人的看法是，“付茶钱”这话准是莫雷尔自己先说的'),
        # ① 读不通：「有一天会到来」悬空无主
        ('也许有一天会到来，那时裁缝出入社交界',
         '也许会有那么一天，那时裁缝出入社交界'),
        # ① 读不通：「他比莫雷尔不那么蠢」比较结构破损
        ('他比莫雷尔不那么蠢，乐意打听那些体面太太的姓名',
         '他没莫雷尔那么蠢，乐意打听那些体面太太的姓名'),
        # ⑦ 顿号误用：动词短语与「的」字短语并列
        ('而且还把她那些接她上门、她也不因此摆架子的、很有身份的太太们',
         '而且还把她那些接她上门而她也不因此摆架子的、很有身份的太太们'),
    ],
    '017': [
        # ⑥ 量词错：「小两口」是双数，不能论「个」
        ('可是有一个“小两口”要引导', '可是有一对“小两口”要引导'),
        # ⑧ ①③ 「莫雷尔之妻又敬又畏、无所不能的保护人」定语层叠且首解错（读成妻子敬他畏他）
        ('觉得自己是莫雷尔之妻又敬又畏、无所不能的保护人',
         '觉得自己是莫雷尔之妻的既令人敬畏又无所不能的保护人'),
        # ① 「爱重」误作一词，读成「爱重（敬重）」；实为「爱又添了一层」
        ('夏尔吕先生对莫雷尔的爱重又添了一层美妙的鲜意',
         '夏尔吕先生对莫雷尔的爱又重新添了一层美妙的鲜意'),
        # ① 「好在他身上去爱」的「好在」易读成「幸亏」
        ('给了他另一样新鲜的、奇妙的东西，好在他身上去爱。',
         '给了他另一样新鲜的、奇妙的东西，可以在他身上去爱。'),
        # ① 比较句悬空：「然而不如……那么让他高兴」
        ('然而不如想到这小两口将要活在对他的依附里那么让他高兴。',
         '然而还比不上想到这小两口将要活在对他的依附里那么让他高兴。'),
    ],
    '018': [
        # ③ 被动式硬搬：人被「偿还」不合汉语
        ('布洛克这样就相当快地被偿还了。',
         '布洛克这样也就相当快地收回了钱。'),
        # ① 指代歧义：「莫雷尔仍没有回音」易读成莫雷尔不回信
        ('如果一下午过去而莫雷尔仍没有回音',
         '如果一下午过去而莫雷尔仍没有收到回音'),
        # ① 「该声明庆幸」搭配不成立
        ('而且很快又说他们该声明庆幸他不怨他们。',
         '而且很快又说他们该庆幸他不怨他们。'),
    ],
    '019': [
        # ⑦ 体例：疑问句段末标点
        ('“怎么，你们已经回来了。”我对她说。', '“怎么，你们已经回来了？”我对她说。'),
        # ①③ 「从……两个世界之一搬走」不合汉语，「所可」生硬，「将」宜作「把」
        ('她这样被从我们所可进入、并可轮流将同一对象安置其中的两个世界之一搬走',
         '她这样被从我们所能进入、并可轮流把同一对象安置其中的两个世界中的一个搬走'),
    ],
    '020': [
        # ① 悬空主语：句首「她——」无谓语，与后文「她就绕开我的房间」重复
        ('她——从前我谈起某个年轻姑娘时，她的眼睛是那样兴致勃勃',
         '从前——我谈起某个年轻姑娘时，她的眼睛是那样兴致勃勃'),
    ],
}


def run():
    total = 0
    for key, pairs in EDITS.items():
        path = os.path.join(BASE, 'chunk' + key, 'final.txt')
        bak = path + '.bak_20261125'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        with io.open(path, 'r', encoding='utf-8', newline='') as f:
            text = f.read()
        orig_lines = text.split('\r\n')
        before_lines = len(orig_lines)
        for old, new in pairs:
            assert old in text, (key, 'MISS', old)
            assert text.count(old) == 1, (key, 'MULTI', old, text.count(old))
            text = text.replace(old, new)
            total += 1
        new_lines = text.split('\r\n')
        after_lines = len(new_lines)
        assert before_lines == after_lines, (key, before_lines, after_lines)
        assert [not l for l in orig_lines] == [not l for l in new_lines], (key, 'blank layout changed')
        with io.open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        print('chunk%s ok: %d edits, lines %d' % (key, len(pairs), after_lines))
    print('total edits', total)


run()
ast.parse(io.open(__file__, 'r', encoding='utf-8').read())
print('self-check ast OK')