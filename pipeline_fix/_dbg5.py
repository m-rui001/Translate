import os, re, html, glob, zipfile
from collections import Counter
from xml.etree import ElementTree as ET
ROOT='E:/Translate'; NS='{http://www.idpf.org/2007/opf}'
NL=chr(10); BLANK=NL+NL
ITAL_O='⟦i⟧'; ITAL_C='⟦/i⟧'

def natsorted(names):
    return sorted(names, key=lambda s:[int(t) if t.isdigit() else t for t in re.split(r'([0-9]+)', s)])

def paras_of_file(p):
    try: t=open(p,encoding='utf-8').read()
    except: return []
    return [x.strip() for x in re.split(BLANK,t) if x.strip()]

def find_work_books():
    b={}
    for w in sorted(glob.glob(os.path.join(ROOT,'work_*'))):
        if not os.path.isdir(w): continue
        placed=False
        for sub in sorted(os.listdir(w)):
            od=os.path.join(w,sub,'out')
            if os.path.isdir(od): b[os.path.basename(w)+'/'+sub]=od; placed=True
        if not placed:
            od=os.path.join(w,'out')
            if os.path.isdir(od): b[os.path.basename(w)]=od
    return b

def build_units(od):
    units=[]; is_idx=False
    top=[d for d in os.listdir(od) if os.path.isdir(os.path.join(od,d))]
    for u in natsorted(top):
        ud=os.path.join(od,u)
        if 'index_split' in u: is_idx=True
        sub=[s for s in os.listdir(ud) if os.path.isdir(os.path.join(ud,s))]
        if sub:
            bl=[]
            for b in natsorted(sub):
                fp=os.path.join(ud,b,'final.txt')
                if os.path.isfile(fp): bl.append(fp)
            if bl: units.append(bl)
        else:
            fp=os.path.join(ud,'final.txt')
            if os.path.isfile(fp): units.append([fp])
    if is_idx:
        grouped=[]; cur=None
        HEAD=re.compile(r'^[一二三四五六七八九十百零0-9]{1,4}[章回节部卷]$')
        for bl in units:
            ft=''
            for bf in bl:
                ps=paras_of_file(bf)
                if ps: ft=ps[0]; break
            ih=bool(ft) and len(ft)<=24 and NL not in ft and not ft.startswith(ITAL_O)
            if ih or cur is None: cur=[]; grouped.append(cur)
            cur.extend(bl)
        units=[g for g in grouped if g]
    return units

def precompute():
    info={}
    for k,od in find_work_books().items():
        units=build_units(od)
        full=''.join(''.join(paras_of_file(bf)) for bl in units for bf in bl)
        info[k]={'units':units,'counter':Counter(full)}
    return info

def epub_chapters(f):
    z=zipfile.ZipFile(f)
    opf=[n for n in z.namelist() if n.endswith('content.opf')][0]
    root=ET.fromstring(z.read(opf))
    items={it.get('id'):it.get('href') for it in root.iter(NS+'item')}
    spine=[s.get('idref') for s in root.iter(NS+'itemref')]
    base=os.path.dirname(opf)
    res=[]
    for sid in spine:
        href=items.get(sid)
        if href and href.endswith('.xhtml'):
            bn=os.path.basename(href)
            if bn in ('nav.xhtml','title.xhtml','copyright.xhtml'): continue
            full=os.path.normpath(os.path.join(base,href)).replace(os.sep,'/')
            res.append((bn,full))
    return res,z

def extract(z,name):
    data=z.read(name).decode('utf-8')
    out=[]
    for attrs,inner in re.findall(r'<p([^>]*)>(.*?)</p>',data,re.S):
        t=inner
        t=re.sub(r'<sup[^>]*>(.*?)</sup>', lambda m:(re.search(r'[([0-9]+)]',m.group(1)) and ('[['+re.search(r'[([0-9]+)]',m.group(1)).group(1)+']]')) or '', t, flags=re.S)
        t=re.sub(r'<br[^>]*>',NL,t)
        t=re.sub(r'<em[^>]*>(.*?)</em>', lambda m: ITAL_O+m.group(1)+ITAL_C, t, flags=re.S)
        t=re.sub(r'<[^>]+>','',t)
        t=html.unescape(t)
        out.append(t)
    return out

wi=precompute()
for name in ['双城记（坟头草译）.epub','追忆似水年华（坟头草译）.epub','鼠疫（坟头草译）.epub']:
    f=glob.glob(os.path.join(ROOT,'out',name))[0]
    ch,z=epub_chapters(f)
    full=''.join(BLANK.join(p) for bn,x in ch for p in extract(z,x))
    ce=Counter(full)
    sev=sum(ce.values())
    scores=[]
    for k,info in wi.items():
        co=info['counter']
        inter=sum(min(ce[c],co.get(c,0)) for c in ce)
        ov=inter/sev if sev else 0
        scores.append((ov,k))
    scores.sort(reverse=True)
    print(name,'nEpubChap=',len(ch))
    for ov,k in scores[:5]:
        print('   %.3f %s'%(ov,k))
