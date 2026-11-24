# -*- coding: utf-8 -*-
"""布莱克伍德《空屋》册润色 第3批：eh_smith / eh_steal / eh_wood"""
import json, ast, shutil, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work_batch_20261124')

EDITS = {
 'eh_smith': [
  ("我死活抓不住、也叫不出名目来，只觉那是个极惹眼的性格，其种种古怪之处究竟是什么",
   "我说不出他哪里不对，也安不上名目来，只觉这是个性格极惹眼的人，可他种种古怪之处究竟是什么，我抓不住"),
  ("另一个笨重，还有点拙",
   "另一个笨重，还有几分笨拙"),
  ("我独自坐着这些念头，坐了有一阵",
   "我独自坐着想这些念头，坐了有一阵"),
 ],
 'eh_steal': [
  ("就在那时，大天白日的，我竟傻乎乎地觉得",
   "就在那时，大白天里，我竟傻乎乎地觉得"),
  ("我竟不能把二三两件事凑到一起",
   "我竟不能把二加二凑成四"),
 ],
 'eh_wood': [
  ("剥去那些显然随着年月围着一个古怪而如画的形象的记忆积起来的迷信",
   "剥去那些随着年月积在记忆里、围着这个古怪而如画的人物生长起来的迷信"),
  ("我还记得自己庆幸地意识到我们坐处这片清凉的树荫——我们坐在这里，望着外面那炎热的世界。",
   "我还记得自己庆幸地意识到我们坐在这片清凉的树荫里——望着外面那炎热的世界。"),
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