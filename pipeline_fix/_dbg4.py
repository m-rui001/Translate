import zipfile, os, glob, re
from xml.etree import ElementTree as ET
NS = '{http://www.idpf.org/2007/opf}'

def chap_info(f):
    z = zipfile.ZipFile(f)
    opf = [n for n in z.namelist() if n.endswith('content.opf')][0]
    root = ET.fromstring(z.read(opf))
    items = {it.get('id'): it.get('href') for it in root.iter(NS+'item')}
    spine = [s.get('idref') for s in root.iter(NS+'itemref')]
    base = os.path.dirname(opf)
    ids = []
    for sid in spine:
        href = items.get(sid)
        if href:
            m = re.search(r'c([0-9]+)[.]xhtml$', href)
            if m: ids.append(m.group(1))
    return ids, z, opf, items, spine, base

for name in ['双城记（坟头草译）.epub','追忆似水年华（坟头草译）.epub','魔戒（坟头草译）.epub','鼠疫（坟头草译）.epub']:
    f = glob.glob('E:/Translate/out/'+name)[0]
    ids, z, opf, items, spine, base = chap_info(f)
    print('===', name, 'nchaps=', len(ids), 'first=', ids[:6], 'last=', ids[-3:])
    if len(ids)==0:
        # show all spine hrefs
        print('   all spine hrefs:', [items.get(s) for s in spine][:20])
    # show first chapter body start
    if ids:
        cid = 'c'+ids[0]
        href = None
        for sid in spine:
            h = items.get(sid)
            if h and h.endswith(cid+'.xhtml'):
                href = os.path.normpath(os.path.join(base,h)).replace(os.sep,'/'); break
        if href:
            data = z.read(href).decode('utf-8')
            # first <p> text
            m = re.search(r'<p[^>]*>(.*?)</p>', data, re.S)
            t = re.sub(r'<[^>]+>','',m.group(1)) if m else ''
            print('   c%s first <p>:', cid, t[:80])

# camus chunks first lines
print('=== camus chunk first lines ===')
import glob as G
od = 'E:/Translate/work_camus/out'
for c in sorted(G.glob(os.path.join(od,'c*'))):
    fp = os.path.join(c,'final.txt')
    if os.path.isfile(fp):
        t = open(fp, encoding='utf-8').read()
        first = t.strip().split(chr(10))[0][:30]
        print('   ', os.path.basename(c), repr(first))
