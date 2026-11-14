import zipfile, os, glob, re
from xml.etree import ElementTree as ET
from collections import defaultdict
NS = '{http://www.idpf.org/2007/opf}'

work_books = {}
for wroot in glob.glob('E:/Translate/work_*'):
    if not os.path.isdir(wroot): continue
    for sub in os.listdir(wroot):
        sdir = os.path.join(wroot, sub)
        if not os.path.isdir(sdir): continue
        out_dir = os.path.join(sdir, 'out')
        if not os.path.isdir(out_dir): continue
        key = os.path.basename(wroot) + '/' + sub
        out_chaps = set()
        for d in os.listdir(out_dir):
            m = re.match(r'c([0-9]+)$', d)
            if m and os.path.isdir(os.path.join(out_dir, d)):
                out_chaps.add(d)
        work_books[key] = out_chaps

wb_sig = defaultdict(list)
for k, v in work_books.items():
    wb_sig[tuple(sorted(v))].append(k)
# show collisions
coll = {s:cs for s,cs in wb_sig.items() if len(cs)>1}
print('num signatures with >1 work book:', len(coll))
for s,cs in coll.items():
    print('  sigsize', len(s), 'books', cs)

def epub_chaps(f):
    z = zipfile.ZipFile(f)
    opf = [n for n in z.namelist() if n.endswith('content.opf')][0]
    root = ET.fromstring(z.read(opf))
    items = {it.get('id'): it.get('href') for it in root.iter(NS+'item')}
    spine = [s.get('idref') for s in root.iter(NS+'itemref')]
    res = []
    for sid in spine:
        href = items.get(sid)
        if href:
            m = re.search(r'c([0-9]+)[.]xhtml$', href)
            if m: res.append('c'+m.group(1))
    return res

f = glob.glob('E:/Translate/out/三个火枪手（坟头草译）.epub')[0]
ec = epub_chaps(f)
sig = tuple(sorted(ec))
print('MUSKETEERS epub sig size', len(sig), 'first', sig[:3], 'last', sig[-2:])
print('in wb_sig?', sig in wb_sig)
print('candidates:', wb_sig.get(sig, 'NONE'))
# also check out_chaps for musketeers
print('musketeers out chaps size', len(work_books.get('work_pub/musketeers', set())))
