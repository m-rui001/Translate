# -*- coding: utf-8 -*-
"""布莱克伍德《日与夜的故事》册润色 第2批：dn_d / dn_e / dn_f / dn_g"""
import json, ast, shutil, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work_batch_20261124')

EDITS = {
 'dn_d': [
  ("命令似地望进他眼里", "命令似的望进他眼里"),
  ("着迷似地瞪着", "着迷似的瞪着"),
 ],
 'dn_e': [
  ("蒂姆像挨了一击似地往后跳", "蒂姆像挨了一击似的往后跳"),
 ],
 'dn_f': [
  ("断断续续打了些狗睡", "断断续续打了几个盹"),
  ("「信念」已经同时要弄了两大传统", "「信念」已经同时耍弄了两大传统"),
 ],
 'dn_g': [
  ("他像漩涡里的水一样漏斗似地翻转", "他像漩涡里的水一样漏斗似的翻转"),
  ("那被称为物质穿透物质的现像发生了", "那被称为物质穿透物质的现象发生了"),
  ("往绿屋去", "往绿色书房去"),
 ],
}

report = []
for key, pairs in EDITS.items():
    path = os.path.join(BASE, key + '_zh.json')
    if not os.path.exists(path + '.bak_20261125'):
        shutil.copyfile(path, path + '.bak_20261125')
    with open(path, encoding='utf-8', newline='') as f:
        data = json.load(f)
    n_before = len(data)
    applied = 0
    for old, new in pairs:
        hits = [i for i, p in enumerate(data) if old in p]
        assert len(hits) == 1, (key, old, hits)
        i = hits[0]
        assert new not in data[i], (key, new)
        data[i] = data[i].replace(old, new)
        applied += 1
    assert len(data) == n_before
    with open(path, 'w', encoding='utf-8', newline='') as f:
        json.dump(data, f, ensure_ascii=False, indent=0)
        f.write('\n')
    report.append((key, n_before, applied))

for r in report:
    print('%s 段数=%d 改动=%d' % r)

ast.parse(open(__file__, encoding='utf-8').read())
print('OK')