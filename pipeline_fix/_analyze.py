import zipfile, os, glob, re
from xml.etree import ElementTree as ET
from collections import defaultdict

NS = {'x':'http://www.idpf.org/2007/opf'}
XHTML = 'http://www.w3.org/1999/xhtml'

def epub_chapter_order(f):
    z = zipfile.ZipFile(f)
    opf = [n for n in z.namelist() if n.endswith('content.opf')][0]
    root = ET.fromstring(z.read(opf))
    items = {it.get('id'): it.get('href') for it in root.iter('{%s}item' % NS['x'])}
    spine = [s.get('idref') for s in root.iter('{%s}itemref' % NS['x'])]
    base = os.path.dirname(opf)
    res = []
    for sid in spine:
        href = items.get(sid)
        if href and re.search(r'cd+.xhtml$', href):
            full = os.path.normpath(os.path.join(base, href)).replace('\','/')
            m = re.search(r'(cd+).xhtml$', full)
            res.append((m.group(1), full, z))
    return res, z

def count_p(z, name):
    data = z.read(name).decode('utf-8')
    # crude count of <p ...> ... </p> occurrences in order, ignore self-closing
    # use regex on raw
    ps = re.findall(r'<p[^>]*>(.*?)</p>', data, re.S)
    return ps

# enumerate work books
work_books = {}
for wroot in glob.glob("E:/Translate/work_*"):
    if not os.path.isdir(wroot): continue
    for sub in os.listdir(wroot):
        sdir = os.path.join(wroot, sub)
        if not os.path.isdir(sdir): continue
        out_dir = os.path.join(sdir, "out")
        chunks_dir = os.path.join(sdir, "chunks")
        has_out = os.path.isdir(out_dir)
        has_chunks = os.path.isdir(chunks_dir)
        if not (has_out or has_chunks): continue
        key = wroot.split("/")[-1] + "/" + sub
        out_chaps = set()
        layout = None
        if has_out:
            for d in os.listdir(out_dir):
                m = re.match(r'c(d+)$', d)
                if m and os.path.isdir(os.path.join(out_dir, d)):
                    out_chaps.add(d)
            sample = sorted(out_chaps)[:1]
            if sample:
                sd = os.path.join(out_dir, sample[0])
                subs = [x for x in os.listdir(sd) if os.path.isdir(os.path.join(sd, x))]
                if any(re.match(r'cd+$', s) for s in subs):
                    layout = 'per-paragraph'
                else:
                    layout = 'per-chapter'
        work_books[key] = {'out_dir': out_dir if has_out else None, 'out_chaps': out_chaps, 'layout': layout}

# match
wb_sig = defaultdict(list)
for k, v in work_books.items():
    wb_sig[tuple(sorted(v['out_chaps']))].append(k)
epubs = glob.glob("E:/Translate/out/*.epub")
match = {}
used = set()
for f in epubs:
    z = zipfile.ZipFile(f)
    opf = [n for n in z.namelist() if n.endswith('content.opf')][0]
    root = ET.fromstring(z.read(opf))
    items = {it.get('id'): it.get('href') for it in root.iter('{%s}item' % NS['x'])}
    spine = [s.get('idref') for s in root.iter('{%s}itemref' % NS['x'])]
    chaps = set()
    for sid in spine:
        href = items.get(sid)
        if href:
            m = re.search(r'(cd+).xhtml$', href)
            if m: chaps.add(m.group(1))
    sig = tuple(sorted(chaps))
    free = [c for c in wb_sig.get(sig, []) if c not in used]
    if len(free)==1:
        match[f]=free[0]; used.add(free[0])

print("matched", len(match), "of", len(epubs))
# layout distribution
from collections import Counter
lay = Counter(work_books[k]['layout'] for k in match.values())
print("layout of matched:", lay)

# for per-paragraph books, check p count vs cXX count per chapter
mismatch_examples = []
for f, wb in match.items():
    info = work_books[wb]
    if info['layout'] != 'per-paragraph': continue
    chaps, z = epub_chapter_order(f)
    for cid, name, zz in chaps:
        ps = count_p(zz, name)
        out_c = os.path.join(info['out_dir'], cid)
        if not os.path.isdir(out_c): 
            mismatch_examples.append((wb, cid, len(ps), 'NO_OUT_DIR')); continue
        cxx = [x for x in os.listdir(out_c) if re.match(r'cd+$', x) and os.path.isdir(os.path.join(out_c,x))]
        if len(ps) != len(cxx):
            mismatch_examples.append((wb, cid, len(ps), len(cxx)))
print("per-paragraph chapter mismatches (epub_p != out_cxx):", len(mismatch_examples))
for e in mismatch_examples[:40]:
    print("  ", e)
