import re,glob,collections
files=sorted(glob.glob('work_proust/out_ind/v2/chunk*/final.txt'))
chunks=[f for f in files if 114<=int(re.search(r'chunk(\d+)',f).group(1))<=227]
txt=''.join(open(f,encoding='utf-8').read() for f in chunks)
cnt=collections.Counter(re.findall(r'[\u4e00-\u9fff·]{2,10}',txt))
pairs=[('维尔帕里西','德·维尔帕里西'),('圣日耳曼区','圣日耳曼郊区'),('圣卢','圣路'),('埃梅','艾梅'),('布洛克','勃洛克'),('弗朗索瓦丝','弗朗索瓦斯'),('德·夏尔吕','夏尔吕'),('巴尔贝克','巴尔倍克'),('贡布雷','孔布雷'),('斯万','斯旺'),('维尔迪兰','韦尔迪兰'),('维尔帕里西夫人','维尔帕里西侯爵夫人')]
for a,b in pairs:
    print(a,txt.count(a),'|',b,txt.count(b))
out=open('_pol/names_top.txt','w',encoding='utf-8')
for w,c in cnt.most_common(200):
    out.write('%s %d\n'%(w,c))
out.close()
