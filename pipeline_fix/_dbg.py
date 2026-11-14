
import os, sys, zipfile, glob
from xml.etree import ElementTree as ET
sys.path.insert(0,"E:/Translate/pipeline_fix")
import sync_epub_to_work as S
NS=S.NS
def epub_chaps(f):
    z=zipfile.ZipFile(f); opf=[n for n in z.namelist() if n.endswith("content.opf")][0]
    root=ET.fromstring(z.read(opf))
    items={it.get("id"):it.get("href") for it in root.iter(NS+"item")}
    spine=[s.get("idref") for s in root.iter(NS+"itemref")]
    out=[]
    for s in spine:
        href=items.get(s,"")
        if href.endswith(".xhtml"):
            bn=os.path.basename(href)
            if bn in ("nav.xhtml","title.xhtml","copyright.xhtml"): continue
            out.append(bn)
    return out
f=os.path.join(S.OUT_EPUB_DIR,"浮士德上册（坟头草译）.epub")
print("EPUB chapters (%d):"%len(epub_chaps(f)), epub_chaps(f)[:15])
# faust work units
import json
info=S.precompute_work()["work_pub/faust"]
print("faust units (%d):"%len(info["units"]))
names=[]
for u in info["units"][:15]:
    rel=os.path.relpath(os.path.dirname(u[0]), info["out_dir"]); names.append(rel.split(os.sep)[0])
print(names)
print("faust src/chunks.json exists:", os.path.isfile(os.path.join(info["out_dir"],"..","src","chunks.json")))
# check faust out top-level
print("faust out top:", sorted(os.listdir(info["out_dir"]))[:20])
