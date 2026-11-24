# -*- coding: utf-8 -*-
"""布莱克伍德《日与夜的故事》册润色 第1批：dn_a / dn_b / dn_c / dn_d"""
import json, ast, shutil, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work_batch_20261124')

EDITS = {
 'dn_a': [
  ("小小白花园门", "白色小花园门", 9),
  ("这份对诺言从未枯萎的死死守住",
   "这份对诺言始终未曾枯萎的坚守"),
  ("一想到黎明里的山谷，他在最气派的宅子里，脚也会觉得孤单",
   "一想到黎明里的山谷，哪怕待在最气派的宅子里，他的脚也会觉得孤单"),
  ("因为月光自由地从枝间洒下，就像那其实它本来就是的淡淡阳光",
   "因为月光自由地从枝间洒下，像一片淡淡的阳光——它本来就是"),
 ],
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
    shutil.copyfile(path, path + '.bak_20261125')
    with open(path, encoding='utf-8', newline='') as f:
        data = json.load(f)
    n_before = len(data)
    text = '\n'.join(data)
    applied = 0
    for item in pairs:
        old, new = item[0], item[1]
        want = item[2] if len(item) > 2 else 1
        assert old in text, (key, old)
        assert text.count(old) == want, (key, old, text.count(old))
        assert new not in text, (key, new)
        text = text.replace(old, new)
        applied += 1
    paras = text.split('\n')
    assert len(paras) == n_before, (key, len(paras), n_before)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        json.dump(paras, f, ensure_ascii=False, indent=0)
        f.write('\n')
    report.append((key, n_before, applied))

for r in report:
    print('%s 段数=%d 改动=%d' % r)

ast.parse(open(__file__, encoding='utf-8').read())
print('OK')