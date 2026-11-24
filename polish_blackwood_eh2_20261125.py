# -*- coding: utf-8 -*-
"""布莱克伍德《空屋》册润色 第2批：eh_promise / eh_skeleton / eh_secretary_a / eh_secretary_b"""
import json, ast, shutil, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work_batch_20261124')

EDITS = {
 'eh_promise': [
  ("马里奥特住在三楼，所在的F——街一带清静，几乎一点声响也打不破那寂静",
   "马里奥特住在三楼，那条F——街一带很清静，几乎没有一点声响能打破这寂静"),
 ],
 'eh_skeleton': [
  ("前者于我是不可能，可后者我又极其厌恶，退缩不前；进退两难之中",
   "前者于我绝不可能，后者我又极其厌恶、退缩不前；进退两难之中"),
 ],
 'eh_secretary_a': [
  ("敞着的通风口从前坏过谈话",
   "敞着的通风口从前害得人漏过话"),
  ("他知道他们积起家财之神速，只被他们随后立刻消失于太虚之神速超过",
   "他知道他们聚财有多快，而比这更快的，是他们随即一下消失得无影无踪"),
  ("*       *       *       *       *",
   "＊　＊　＊　＊　＊"),
  ("园里长满野草和长草",
   "园里长满乱草和深草"),
  ("他并不知道秘书对信的内容一无所知，可脸上没露出半点神情",
   "他并不知道秘书对信的内容一无所知；而他脸上也没露出半点神情"),
  ("可这老希伯来仆人在旁伺候实在叫人厌恶，一匙一匙便吃得颇慢",
   "可有这老希伯来仆人在旁伺候实在叫人厌恶，于是一匙一匙吃得颇慢"),
  ("可他苦得很。我怀疑那饥饿还能逼我再干一次",
   "可他一身苦味。我怀疑那饥饿还能逼我再干一次"),
 ],
 'eh_secretary_b': [
  ("门外一声倒抽气，门板轻轻一晃",
   "门外有人倒抽了一口气，门板轻轻一晃"),
  ("捅出一片旺堂堂的火光",
   "捅出一片旺腾腾的火光"),
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
    for old, new in pairs:
        assert old in text, (key, old)
        assert text.count(old) == 1, (key, old, text.count(old))
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