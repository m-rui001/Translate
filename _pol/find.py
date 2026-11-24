import re,glob,sys
pat=sys.argv[1]
out=open('_pol/out.txt','w',encoding='utf-8')
for f in sorted(glob.glob('work_proust/out_ind/v2/chunk*/final.txt')):
    n=int(re.search(r'chunk(\d+)',f).group(1))
    if not(114<=n<=227): continue
    t=open(f,encoding='utf-8').read().replace('\r\n','\n')
    for m in re.finditer(pat,t):
        out.write('[%d] ...%s...\n'%(n,t[max(0,m.start()-40):m.end()+40]))
out.close()
