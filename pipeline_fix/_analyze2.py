import zipfile, os, glob, re, html
from collections import defaultdict, Counter
from xml.etree import ElementTree as ET

NS = '{http://www.idpf.org/2007/opf}'
OUT = 'E:/Translate/out'

work_books = {}
for wroot in glob.glob('E:/Translate/work_*'):
    if not os.path.isdir(wroot): continue
    for sub in os.listdir(wroot):
        sdir = os.path.join(wroot, sub)
        if not os.path.isdir(sdir): continue
        out_dir = os.path.join(sdir, 'out')
        chunks_dir = os.path.join(sdir, 'chunks')
        has_out = os.path.isdir(out_dir)
        has_chunks = os.path.isdir(chunks_dir)
        if not (has_out or has_chunks): continue
        key = os.path.basename(wroot) + '/' + sub
        out_chaps = set()
        layout = None
        if has_out:
            for d in os.listdir(out_dir):
                m = re.match(r'c([0-9]+)$', d)
                if m and os.path.isdir(os.path.join(out_dir, d)):
                    out_chaps.add(d)
            sample = sorted(out_chaps)[:1]
            if sample:
                sd = os.path.join(out_dir, sample[0])
                subs = [x for x in os.listdir(sd) if os.path.isdir(os.path.join(sd, x))]
                if any(re.match(r'c([0-9]+)$', s) for s in subs):
                    layout = 'per-paragraph'
                else:
                    layout = 'per-chapter'
        work_books[key] = {'out_dir': out_dir if has_out else None, 'out_chaps': out_chaps, 'layout': layout, 'has_out': has_out}

wb_sig = defaultdict(list)
for k, v in work_books.items():
    wb_sig[tuple(sorted(v['out_chaps']))].append(k)

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
                res.append('c'+m.group(1))
    return res

epubs = glob.glob(os.path.join(OUT, '*.epub'))
match = {}
used = set()
for f in epubs:
    chaps = epub_chaps(f)
    sig = tuple(sorted(chaps))
    free = [c for c in wb_sig.get(sig, []) if c not in used]
    if len(free) == 1:
        match[f] = free[0]; used.add(free[0])

print('WORK BOOKS:', len(work_books))
print('EPUBS:', len(epubs))
print('MATCHED:', len(match))
print('UNMATCHED EPUBS:', len(epubs) - len(match))
for f in epubs:
    if f not in match:
        print('  NO-MAP', os.path.basename(f))
unused = [k for k in work_books if k not in used]
print('UNUSED WORK BOOKS:', len(unused))
for k in unused:
    v = work_books[k]
    print('  unused', k, 'nOut', len(v['out_chaps']))

lay = Counter(work_books[match[f]]['layout'] for f in match)
print('LAYOUT OF MATCHED:', dict(lay))

def extract_p(z, name):
    data = z.read(name).decode('utf-8')
    blocks = re.findall(r'<p([^>]*)>(.*?)</p>', data, re.S)
    out = []
    for attrs, inner in blocks:
        t = re.sub(r'<br[^>]*>', chr(10), inner)
        t = re.sub(r'<[^>]+>', '', t)
        t = html.unescape(t)
        out.append(t)
    return out

mism = []
for f, wb in match.items():
    info = work_books[wb]
    if info['layout'] != 'per-paragraph': continue
    chaps = epub_chaps(f)
    for cid in chaps:
        # find xhtml name
        z = zipfile.ZipFile(f)
        opf = [n for n in z.namelist() if n.endswith('content.opf')][0]
        root = ET.fromstring(z.read(opf))
        items = {it.get('id'): it.get('href') for it in root.iter(NS+'item')}
        spine = [s.get('idref') for s in root.iter(NS+'itemref')]
        base = os.path.dirname(opf)
        xname = None
        for sid in spine:
            href = items.get(sid)
            if href and re.search(r'c'+cid[1:]+r'[.]xhtml$', href):
                xname = os.path.normpath(os.path.join(base, href)).replace(os.sep, '/')
                break
        if not xname: continue
        ps = extract_p(z, xname)
        out_c = os.path.join(info['out_dir'], cid)
        if not os.path.isdir(out_c):
            mism.append((wb, cid, len(ps), 'NO_DIR')); continue
        cxx = [x for x in os.listdir(out_c) if re.match(r'c([0-9]+)$', x) and os.path.isdir(os.path.join(out_c, x))]
        if len(ps) != len(cxx):
            mism.append((wb, cid, len(ps), len(cxx)))
print('PER-PARAGRAPH CHAPTER MISMATCHES (epub_p != out_cxx):', len(mism))
for e in mism[:120]:
    print('  ', e)
