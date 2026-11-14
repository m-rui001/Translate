
import os, re, zipfile, glob, json
from collections import Counter
from xml.etree import ElementTree as ET
ROOT="E:/Translate"
NS="{http://www.idpf.org/2007/opf}"

def hanzi_only(t):
    return "".join(ch for ch in t if 0x4E00<=ord(ch)<=0x9FFF)

def bg(text):
    h=hanzi_only(text)
    return Counter(h[i:i+2] for i in range(len(h)-1))

def epub_text(f):
    z=zipfile.ZipFile(f)
    opf=[n for n in z.namelist() if n.endswith("content.opf")][0]
    root=ET.fromstring(z.read(opf))
    items={it.get("id"):it.get("href") for it in root.iter(NS+"item")}
    spine=[s.get("idref") for s in root.iter(NS+"itemref")]
    out=[]
    for s in spine:
        href=items.get(s,"")
        if href.endswith(".xhtml"):
            bn=os.path.basename(href)
            if bn in ("nav.xhtml","title.xhtml","copyright.xhtml"): continue
            data=z.read(os.path.normpath(os.path.join(os.path.dirname(opf),href)).replace(os.sep,"/")).decode("utf-8","ignore")
            if "titlepage" in data or "copyright" in data or "<nav" in data: continue
            for m in re.findall(r"<p[^>]*>(.*?)</p>",data,re.S):
                t=re.sub(r"<[^>]+>","",m)
                out.append(t)
    return "".join(out)

# build work book text map
def work_texts():
    res={}
    for wroot in sorted(glob.glob(os.path.join(ROOT,"work_*"))):
        if not os.path.isdir(wroot): continue
        placed=False
        for sub in sorted(os.listdir(wroot)):
            od=os.path.join(wroot,sub,"out")
            if os.path.isdir(od):
                res[os.path.basename(wroot)+"/"+sub]=od; placed=True
        if not placed:
            od=os.path.join(wroot,"out")
            if os.path.isdir(od): res[os.path.basename(wroot)]=od
    return res

wt=work_texts()
wbg={k:bg(" ".join(open(os.path.join(v,f),encoding="utf-8").read() for f in __import__("os").walk(v) if False)) for k,v in wt.items()}
# simpler: read all final.txt under each out
def read_all(outd):
    parts=[]
    for dp,_,fs in os.walk(outd):
        for fn in fs:
            if fn=="final.txt":
                try: parts.append(open(os.path.join(dp,fn),encoding="utf-8").read())
                except: pass
    return "".join(parts)
wbg={k:bg(read_all(v)) for k,v in wt.items()}

tests=["傲慢与偏见（坟头草译）.epub","双城记（坟头草译）.epub","三个火枪手（坟头草译）.epub","鼠疫（坟头草译）.epub","追忆似水年华（坟头草译）.epub","魔戒（坟头草译）.epub","布登勃洛克一家（坟头草译）.epub"]
for t in tests:
    f=os.path.join(ROOT,"out",t)
    eb=bg(epub_text(f))
    sc=[]
    for k,c in wbg.items():
        inter=sum((eb&c).values()); uni=sum((eb|c).values())
        sc.append((inter/uni if uni else 0,k))
    sc.sort(reverse=True)
    print(t)
    for s,k in sc[:5]: print("   %.3f  %s"%(s,k))
