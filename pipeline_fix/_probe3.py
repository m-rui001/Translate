import zipfile, os, glob, re
from xml.etree import ElementTree as ET

WORK = "E:/Translate/work_"
OUT = "E:/Translate/out"

work_books = {}
for wroot in glob.glob(os.path.join(WORK, "*")):
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
                m = re.match(r'c(\d+)$', d)
                if m and os.path.isdir(os.path.join(out_dir, d)):
                    out_chaps.add(d)
            sample = sorted(out_chaps)[:1]
            if sample:
                sd = os.path.join(out_dir, sample[0])
                subs = [x for x in os.listdir(sd) if os.path.isdir(os.path.join(sd, x))]
                if any(re.match(r'c\d+$', s) for s in subs):
                    layout = 'per-paragraph'
                else:
                    layout = 'per-chapter'
        chunk_chaps = set()
        if has_chunks:
            for cf in os.listdir(chunks_dir):
                m = re.match(r'c(\d+)\.json$', cf)
                if m:
                    chunk_chaps.add('c'+m.group(1))
        work_books[key] = {'out_chaps': out_chaps, 'chunk_chaps': chunk_chaps, 'layout': layout}

print("num work books:", len(work_books))

def epub_chapters(f):
    z = zipfile.ZipFile(f)
    opf = [n for n in z.namelist() if n.endswith('content.opf')][0]
    root = ET.fromstring(z.read(opf))
    items = {it.get('id'): it.get('href') for it in root.iter('{http://www.idpf.org/2007/opf}item')}
    spine = [s.get('idref') for s in root.iter('{http://www.idpf.org/2007/opf}itemref')]
    base = os.path.dirname(opf)
    chaps = []
    for sid in spine:
        href = items.get(sid)
        if href and re.search(r'c\d+\.xhtml$', href):
            full = os.path.normpath(os.path.join(base, href)).replace('\\','/')
            m = re.search(r'(c\d+)\.xhtml$', full)
            chaps.append(m.group(1))
    return chaps

epubs = glob.glob(os.path.join(OUT, "*.epub"))
epub_map = {}
for f in epubs:
    try:
        epub_map[f] = epub_chapters(f)
    except Exception as e:
        print("ERR epub", f, e)

print("num epubs:", len(epub_map))

from collections import defaultdict
wb_sig = defaultdict(list)
for k, v in work_books.items():
    wb_sig[tuple(sorted(v['out_chaps']))].append(k)

match = {}
unmatched = []
used = set()
for f, ch in epub_map.items():
    sig = tuple(sorted(ch))
    free = [c for c in wb_sig.get(sig, []) if c not in used]
    if len(free) == 1:
        match[f] = free[0]; used.add(free[0])
    else:
        unmatched.append((f, len(wb_sig.get(sig,[])), wb_sig.get(sig,[])))

print("matched:", len(match))
print("unmatched epubs:", len(unmatched))
for f, n, c in unmatched[:30]:
    print("  UNMATCHED", os.path.basename(f), "nCands=", n, c)
print("=== work books not used ===")
for k in work_books:
    if k not in used:
        print("  unused:", k, "nOut=", len(work_books[k]['out_chaps']), "nChunk=", len(work_books[k]['chunk_chaps']))
