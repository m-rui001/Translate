import re,sys
t=open('work_proust/src/v2.txt',encoding='utf-8',errors='replace').read()
out=open('_pol/fr.txt','w',encoding='utf-8')
for k in sys.argv[1:]:
    found=False
    for m in re.finditer(k,t):
        found=True
        out.write('### %s :: %s\n\n'%(k,t[max(0,m.start()-400):m.end()+400].replace('\n',' ')))
    if not found: out.write('### %s :: NOT FOUND\n\n'%k)
out.close()
