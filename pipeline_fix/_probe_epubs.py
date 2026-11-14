
import os, zipfile
from xml.etree import ElementTree as ET
NS="{http://www.idpf.org/2007/opf}"
OUT="E:/Translate/out"
for title in ["双城记（坟头草译）.epub","追忆似水年华（坟头草译）.epub","鼠疫（坟头草译）.epub"]:
    f=os.path.join(OUT,title)
    z=zipfile.ZipFile(f)
    opf=[n for n in z.namelist() if n.endswith("content.opf")][0]
    root=ET.fromstring(z.read(opf))
    items={it.get("id"):it.get("href") for it in root.iter(NS+"item")}
    spine=[s.get("idref") for s in root.iter(NS+"itemref")]
    chaps=[os.path.basename(items[s]) for s in spine if items.get(s,"").endswith(".xhtml")]
    print("==== "+title)
    print("chapter count:",len(chaps))
    print("first 8:",chaps[:8])
    print("last 4:",chaps[-4:])
    z.close()
