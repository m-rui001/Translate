import sys
sys.path.insert(0,'_pol')
from lp import path
out=open('_pol/q.txt','w',encoding='utf-8')
for n in [int(x) for x in sys.argv[1:]]:
    t=open(path(n),encoding='utf-8',newline='').read().replace('\r\n','\n')
    out.write('===== %d =====\n'%n)
    for i,ch in enumerate(t):
        if ch in '“”':
            out.write('%s ...%s...\n'%(ch, t[max(0,i-45):i+45].replace('\n','\n')))
out.close()
