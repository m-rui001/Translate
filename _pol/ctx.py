import re,sys
t=open('work_proust/src/v2.txt',encoding='utf-8').read()
key=sys.argv[1]; before=int(sys.argv[2]) if len(sys.argv)>2 else 200; after=int(sys.argv[3]) if len(sys.argv)>3 else 2500
i=t.find(key)
open('_pol/fr.txt','w',encoding='utf-8').write('NOT FOUND' if i<0 else t[max(0,i-before):i+after])
