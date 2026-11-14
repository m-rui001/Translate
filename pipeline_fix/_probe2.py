import zipfile, os, glob, re
from xml.etree import ElementTree as ET

out_dir = "E:/Translate/out"
epubs = glob.glob(os.path.join(out_dir, "*.epub"))
f = epubs[0]
z = zipfile.ZipFile(f)
names = z.namelist()

opf_name = [n for n in names if n.endswith('content.opf')][0]
print("OPF:", opf_name)
root = ET.fromstring(z.read(opf_name))
items = {}
for it in root.iter('{http://www.idpf.org/2007/opf}item'):
    items[it.get('id')] = it.get('href')
spine = [s.get('idref') for s in root.iter('{http://www.idpf.org/2007/opf}itemref')]
print("manifest items:", len(items), "spine:", len(spine))
base = os.path.dirname(opf_name)
order = []
for sid in spine:
    href = items.get(sid)
    if href and href.endswith('.xhtml'):
        full = os.path.normpath(os.path.join(base, href)).replace('\\','/')
        order.append(full)
print("total xhtml:", len(order))
print("first 12:", order[:12])
c1 = [o for o in order if o.endswith('c001.xhtml')]
if c1:
    data = z.read(c1[0]).decode('utf-8')
    print("=== c001.xhtml (first 2500 chars) ===")
    print(data[:2500])
