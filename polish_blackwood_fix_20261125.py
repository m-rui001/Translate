# -*- coding: utf-8 -*-
"""布莱克伍德册润色 补遗：eh_promise / eh_gift 长定语拆句"""
import json, ast, shutil, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work_batch_20261124')

EDITS = {
 'eh_promise': [
  ("本属于一个离他那小小的、精选的书本与冥想的世界很远的天地",
   "本属于另一个天地——离他那书本与冥想的小小精选世界远得很"),
 ],
 'eh_gift': [
  ("纽约那时正好被敲诈犯、假钞贩子和别的受警察庇护的丑类的地下门路钻得千疮百孔",
   "纽约那时正好被敲诈犯、假钞贩子和其他受警察庇护的丑类的秘密门路掏得千疮百孔"),
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