import sys,re
sys.path.insert(0,'_pol')
from lp import path
import glob
out=open('_pol/chk.txt','w',encoding='utf-8')
for n in range(114,228):
    t=open(path(n),encoding='utf-8',newline='').read()
    msg=[]
    if t.count('“')!=t.count('”'): msg.append('quote %d/%d'%(t.count('“'),t.count('”')))
    if '"' in t or "'" in t: msg.append('ascii')
    if '⟦' in t or '⟧' in t: msg.append('marker')
    for w in ['自已','影晌','知识份子','其它','。。。。','。。','——，',' ，',' 。','..']:
        if w in t: msg.append('WORD:'+w+'x%d'%t.count(w))
    if msg: out.write('[%d] %s\n'%(n,'; '.join(msg)))
out.close()
