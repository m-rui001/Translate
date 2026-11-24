# -*- coding: utf-8 -*-
"""布莱克伍德《空屋》册润色 第1批：eh_empty / eh_eaves / eh_gift / eh_island"""
import json, ast, shutil, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work_batch_20261124')

EDITS = {
 'eh_empty': [
  ("就连地下那一圈脏栏杆的高低也一样",
   "就连地下室周围那圈脏栏杆的高低也一样"),
  ("而且发电报叫他来是有一桩极特别的目的",
   "而且电报叫他来是为了一桩极特别的目的"),
  ("亮着灯的窗子很少，几乎没有一囱烟或火星。",
   "亮着灯的窗子很少，几乎没有哪个烟囱冒出烟或火星。"),
  ("一间比一间冷，一间比一间不招人待",
   "一间比一间冷，一间比一间更不招人待见"),
  ("那种难免的感觉是：房间空着时照常进行的活动",
   "萦绕不去的那个感觉是：房间空着时照常进行的活动"),
  ("据说就是当年那暴怒的马夫追上他受害者、最后抓住她的那间屋子",
   "据说就是当年那个暴怒的马夫追上他的受害者、最后抓住她的那间屋子"),
  ("接着是半分钟的死的寂静",
   "接着是半分钟死一般的寂静"),
  ("而当他感到他凝注的目光、她转过来看他时",
   "而当他觉出她凝注的目光、见她转过脸来看他时"),
 ],
 'eh_eaves': [
  ("而且他「先生，能给贵报干出好活儿来，当记者」",
   "而且他能「给贵报干出好活儿来，先生，当个记者」"),
  ("吉姆关心自己的睡眠，已胜过关心偷听邻居私隐在道义上是否妥当",
   "吉姆此时惦记自己的睡眠，已胜过顾虑偷听邻家私隐在道义上是否妥当"),
 ],
 'eh_gift': [
  ("他把这归因于一些他爱说怪不得自己的情形",
   "他把这归因于一些情形——他总爱说那些怪不得自己"),
  ("那间屋只在他交房租这层意义上算是他的",
   "那间屋只在他付房租这层意义上才算是他的"),
  ("而那些印出来、付了稿酬的字句，极少有见天日的机会",
   "而那些稿子即使印出来、付了稿酬，也极少有见天日的机会"),
  ("任人敲诈而告不得",
   "任人敲诈却有冤难告"),
 ],
 'eh_island': [
  ("就只可合理地认为是与我有关",
   "就只能合情合理地认为与我有关"),
  ("是这一切可怖的恐怖",
   "是这一切骇人的恐怖"),
  ("我这辈子划桨从没有接下来那几分钟划得那么快",
   "我这辈子划桨，从没有像接下来那几分钟那样快过"),
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