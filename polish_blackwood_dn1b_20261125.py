# -*- coding: utf-8 -*-
"""布莱克伍德《日与夜的故事》册润色 第1批(b)：dn_b / dn_c / dn_d —— 按段定位替换"""
import json, ast, shutil, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work_batch_20261124')

EDITS = {
 'dn_b': [
  ("那支枪金属的表", "那只炮铜色的表"),
  ("她觉得自己站在她之外的东西的边缘上",
   "她觉得自己站在自身以外某样东西的边上"),
  ("既是万有、既在无处不有", "既是万有，又无所不在"),
  ("我们必须设法把这人的、热烈的、建设性的才华引进某条人的渠道",
   "我们必须设法把这人热烈而富于建设性的才华，引进某条人的渠道"),
  ("「给我的灵魂添翼……去认识你那可畏的迅疾！」",
   "「给我的灵魂添上羽翼……去认识你那可畏的迅疾！」"),
 ],
 'dn_c': [
  ("一股寒气顺着我脊梁下去，除非我想忘，否则不必忘",
   "一股寒气顺着我脊梁下去——这事我永远忘不了，除非我情愿忘掉"),
  ("——我想，更宏伟是那个词", "——我想，那个词是「更宏伟」"),
  ("正是我们对他们那宏大召唤——那么狂野、那么甜美、那么美——的拒绝，造成了「恶」",
   "我们对他们那宏大召唤的拒绝——那召唤那么狂野、那么甜美、那么美——正是「恶」的由来"),
 ],
 'dn_d': [
  ("一同在水恒里", "一同在永恒里"),
  ("那通向随手别一枚面纱、通向系紧一条马镫带、通向与同伴的那几句闲话的、令人目眩的时间的伸展",
   "那令人目眩的时间的伸展——它通向随手别一枚面纱，通向系紧一条马镫带，通向与同伴的那几句闲话"),
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
        assert sum(p.count(old) for p in data) == 1, (key, old)
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