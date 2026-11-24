import re,sys
t=open('work_proust/src/v2.txt',encoding='utf-8').read()
out=open('_pol/fr.txt','w',encoding='utf-8')
for k in sys.argv[1:]:
    idx=[m.start() for m in re.finditer(re.escape(k),t)]
    out.write('### %s (%d)\n'%(k,len(idx)))
    for i in idx[:2]:
        out.write(t[max(0,i-500):i+500].replace('\n',' ')+'\n\n')
out.close()
