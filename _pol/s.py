import sys
sys.path.insert(0,'_pol')
from lp import path
t=open(path(int(sys.argv[1])),encoding='utf-8').read()
k=sys.argv[2]
i=t.find(k)
open('_pol/s.txt','w',encoding='utf-8').write('NOTFOUND' if i<0 else repr(t[max(0,i-120):i+200]))
