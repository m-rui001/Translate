# -*- coding: utf-8 -*-
"""通读润色 chunk028-chunk034（Proust v5）：定位唯一子串 → 替换 → 断言命中数。"""
import os, shutil, json

BASE = 'work_proust/out_ind/v5'
BAK = '.bak_20261125'

EDITS = {
    'chunk028': [
        # ① 读不通／⑥ 虚词误用「哪怕」
        ('你下午哪怕写了点东西没有，我的小宝贝？',
         '你下午好歹写了点东西没有，我的小宝贝？'),
    ],
    'chunk029': [
        # ① 缺主语流水句
        ('在那些肉欲的表达之间，会认出另一些专属于我母亲和外祖母的表达',
         '在那些肉欲的表达之间，人会认出另一些专属于我母亲和外祖母的表达'),
        # ① 悬空同位语／赘余「得以可能」
        ('一种效果与原因之间的普遍联系，痛苦之产生得以可能的诸方式之一。',
         '一种效果与原因之间的普遍联系，痛苦得以产生的诸方式之一。'),
    ],
    'chunk030': [
        # ⑥ 错别字「自已」
        ('是我要向我自已证明', '是我要向我自己证明'),
        # ⑥ 词义误读：se donner congé 不是「放行」
        ('——他便对工作放行。', '——他便给自己放了假。'),
    ],
    'chunk031': [
        # ① 主谓失配（体质不会喘息）
        ('就像那些体质，风湿病只让人喘息片刻',
         '就像那些体质的人，风湿病只让他们喘息片刻'),
        # ① 破折插入后另起主句，缺连接
        ('——未来在我眼里变得可怕。', '——于是未来在我眼里变得可怕。'),
        # ⑥ 主谓错位：请布洛克给照片的是「我」
        ('只请给我看一张她的照片', '我只请他给我看一张她的照片'),
        # ① 主语悬空
        ('必要时安排我与她见面。', '必要时让他安排我与她见面。'),
    ],
    'chunk032': [
        # ⑥ 外文词拼写（源 v5 已误，v6 作 procrastination）
        ('procrasnation', 'procrastination'),
    ],
    'chunk033': [
        # ① 缺谓语
        ('甚至只需隐约预感。', '甚至只需隐约预感就够了。'),
        # ④ 指代错位：伴随神情的是目光，不是「它们所伴随」
        ('还带着它们所伴随的那种心不在焉、空空洞洞的神情',
         '还带着伴随着它们的那种心不在焉、空空洞洞的神情'),
        # ① 语序断裂「在按……判断可能的认识范围之外」
        ('因为这在按阿尔贝蒂娜的判断可能的认识范围之外。',
         '因为按阿尔贝蒂娜的判断，这超出了她所能认识的范围。'),
        # ① 缺谓语（au contraire de réserve）
        ('或者相反，那样克制，并且仿佛她没看见。',
         '或者相反，目光那样克制，仿佛她没看见。'),
    ],
    'chunk034': [
        # ① 主谓失配：眼睛不能「笼罩」光晕
        ('反而更笼罩着悲伤与气馁的光晕', '反而更蒙着悲伤与气馁的光晕'),
    ],
}

changed = []
for chunk, pairs in EDITS.items():
    path = os.path.join(BASE, chunk, 'final.txt')
    bak = path + BAK
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    with open(path, encoding='utf-8', newline='') as f:
        text = f.read()
    orig = text
    n_before = orig.count('\n')
    for old, new in pairs:
        assert old in text, (chunk, old)
        assert text.count(old) == 1, (chunk, old, text.count(old))
        text = text.replace(old, new)
    # 段落/行数不变
    assert text.count('\n') == n_before, chunk
    assert len(text.split('\n')) == len(orig.split('\n')), chunk
    # 无空段（结构：正文行与空行交替，空行数不变）
    assert [i for i, p in enumerate(text.split('\n')) if not p.strip()] == \
           [i for i, p in enumerate(orig.split('\n')) if not p.strip()], chunk
    # 无新增半角标点 / 引号成对
    for ch in '"\'':
        assert text.count(ch) == orig.count(ch), (chunk, ch)
    assert text.count('“') == text.count('”'), chunk
    assert '⟦' not in text
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    changed.append((chunk, len(pairs)))

print(json.dumps(changed, ensure_ascii=False))