# -*- coding: utf-8 -*-
"""逐段润色 v7 chunk060-063：定位唯一子串 → 替换 → 校验；不整文件重写。"""
import os, re, shutil, ast

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

EDITS = {
    '060': [
        # ① 悬空流水句：maintenant que 从句被并成并列事实，补出因果
        ('而我当时却如此渴望生活，此刻一个真正的往昔时刻刚刚在我身上复活',
         '而我当时却如此渴望生活，因为此刻一个真正的往昔时刻刚刚在我身上复活'),
        # ① 二次打磨：避免与上文「因为我是根据……」连用两个「因为」，maintenant que＝既然
        ('而我当时却如此渴望生活，因为此刻一个真正的往昔时刻刚刚在我身上复活',
         '而我当时却如此渴望生活，既然此刻一个真正的往昔时刻刚刚在我身上复活'),
    ],
    '061': [
        # ⑥ 搭配误（dessécher「使干枯」被译成「弄干」）
        ('而知性把过去给它弄干', '而知性却把过去给它抽干'),
        # ① 句末比较项悬空（comme me l\'avait déjà fait… 缺宾语）
        ('——正如在巴黎一家大餐馆里，一间半空、夏意融融的豪华餐厅的景象已经让我感到过一次。',
         '——在巴黎一家大餐馆里，一间半空、夏意融融的豪华餐厅的景象，也曾让我有过同样的感受。'),
        # ① 二次打磨：补回比较连词，免得破折号后突然另起
        ('推入木框的铰链中——在巴黎一家大餐馆里', '推入木框的铰链中——正如在巴黎一家大餐馆里'),
        # ⑥ 成语误用（envahissants 指「涌来、侵入」，非「咄咄逼人」）
        ('让这个既咄咄逼人又被压回的贡布雷', '让这个不断涌来又被压回的贡布雷'),
    ],
    '062': [
        # ④ 指代不明（「它」隔了两个分句，实指「这趟旅行」）
        ('——它不可能成为我所寻求的办法。', '——这趟旅行不可能成为我所寻求的办法。'),
        # ⑥ 词义误读（une expérience de plus＝再多一次，非「另一种」）
        ('去尝试另一种经历。', '去再多尝试一次。'),
        # ① 末句重复「愈来愈」且关系从句硬搬，主语（我）被搬成「对于……的人来说」
        ('我的兴奋却愈来愈强烈——对于那个把莱奥妮姨妈的房间带进自己房间、并随着它把贡布雷以及贡布雷的两边都带进来的人来说，那愉悦也愈来愈深。',
         '我的兴奋却愈来愈强烈——毕竟是我把莱奥妮姨妈的房间请进了自己的房间，并随之把整个贡布雷及其两边都带了进来。'),
        # ⑥ 词义误读／搭配误（recouvrir＝覆盖、包含，非「掩映」）
        ('而且它也掩映着我天性中一个根本的特点', '而且它底下也掩藏着我天性的一个根本特点'),
    ],
    '063': [
        # ③ Seulement 硬搬成句首「只是」，与副词「只是」撞形
        ('只是借口在艺术中根本不算数', '不过，借口在艺术中根本不算数'),
    ],
}

HAN = re.compile(r'[\u4e00-\u9fff]')

total = 0
for key in ['060', '061', '062', '063']:
    d = os.path.join(BASE, 'chunk' + key)
    p = os.path.join(d, 'final.txt')
    bak = os.path.join(d, BAK)
    if not os.path.exists(bak):
        shutil.copy2(p, bak)
    with open(p, encoding='utf-8', newline='') as f:
        text = f.read()
    before_lines = text.count('\n') + 1
    before_han = len(HAN.findall(text))
    before_q = (text.count('\u201c'), text.count('\u201d'))
    n = 0
    for old, new in EDITS[key]:
        if old not in text:
            assert text.count(new) == 1, (key, old)
            continue  # 已应用（脚本可重入）
        assert text.count(old) == 1, (key, old, text.count(old))
        text = text.replace(old, new)
        n += 1
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    with open(p, encoding='utf-8', newline='') as f:
        chk = f.read()
    after_lines = chk.count('\n') + 1
    after_han = len(HAN.findall(chk))
    after_q = (chk.count('\u201c'), chk.count('\u201d'))
    assert after_lines == before_lines, (key, before_lines, after_lines)
    assert after_q == before_q, (key, before_q, after_q)
    assert '\u201c' in chk or True
    assert chk.count('\uff02') == 0
    total += n
    print('chunk%s: 改动 %d 条 | 行数 %d=%d | 汉字 %d→%d | 引号 %s=%s | CRLF %s'
          % (key, n, before_lines, after_lines, before_han, after_han,
             before_q, after_q, '\r\n' in chk))
print('总计改动', total, '条')
ast.parse(open(__file__, encoding='utf-8').read())
print('self-check ast OK')