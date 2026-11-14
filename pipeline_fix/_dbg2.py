import zipfile, os, glob, re, html
from xml.etree import ElementTree as ET
NS = '{http://www.idpf.org/2007/opf}'

def epub_chaps(f):
    z = zipfile.ZipFile(f)
    opf = [n for n in z.namelist() if n.endswith('content.opf')][0]
    root = ET.fromstring(z.read(opf))
    items = {it.get('id'): it.get('href') for it in root.iter(NS+'item')}
    spine = [s.get('idref') for s in root.iter(NS+'itemref')]
    base = os.path.dirname(opf)
    res = []
    for sid in spine:
        href = items.get(sid)
        if href:
            m = re.search(r'c([0-9]+)[.]xhtml$', href)
            if m:
                res.append(('c'+m.group(1), os.path.normpath(os.path.join(base, href)).replace(os.sep,'/')))
    return res, z, opf, items, spine, base

f = glob.glob('E:/Translate/out/傲慢与偏见（坟头草译）.epub')[0]
chaps, z, opf, items, spine, base = epub_chaps(f)
print('EPUB chapter count:', len(chaps))
# find c001
c001 = [c for c in chaps if c[0]=='c001'][0]
data = z.read(c001[1]).decode('utf-8')
print('c001 xhtml length:', len(data))
print('count <p occurrences:', len(re.findall(r'<p', data)))
print('count </p>:', len(re.findall(r'</p>', data)))
print('regex <p>...</p> blocks:', len(re.findall(r'<p([^>]*)>(.*?)</p>', data, re.S)))
print('--- first 600 chars of c001 body ---')
print(data[2000:2600])

# out side
out_c = 'E:/Translate/work_pub/pride/out/c001'
print('--- out/c001 cXX dirs:', sorted(os.listdir(out_c)))
for cx in sorted(os.listdir(out_c)):
    p = os.path.join(out_c, cx, 'final.txt')
    if os.path.isfile(p):
        t = open(p, encoding='utf-8').read()
        print(cx, 'len', len(t), 'newlines', t.count(chr(10)), 'hanzi', sum(1 for ch in t if 0x4E00<=ord(ch)<=0x9FFF))
        print('   first120:', repr(t[:120]))
