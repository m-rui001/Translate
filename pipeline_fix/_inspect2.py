import os, re, glob as G
from collections import defaultdict

def find_work_books():
    books = {}
    for wroot in sorted(G.glob('E:/Translate/work_*')):
        if not os.path.isdir(wroot): continue
        subs = [s for s in os.listdir(wroot) if os.path.isdir(os.path.join(wroot,s))]
        placed = False
        for sub in subs:
            od = os.path.join(wroot, sub, 'out')
            if os.path.isdir(od):
                books[os.path.basename(wroot)+'/'+sub] = od
                placed = True
        if not placed:
            od = os.path.join(wroot, 'out')
            if os.path.isdir(od):
                books[os.path.basename(wroot)] = od
    return books

def describe(out_dir):
    top = sorted([d for d in os.listdir(out_dir) if os.path.isdir(os.path.join(out_dir,d))])
    # classify top naming
    kinds = defaultdict(int)
    for d in top:
        if re.match(r'c[0-9]+$', d): kinds['cNN']+=1
        elif re.match(r'sec[0-9]+$', d): kinds['secNN']+=1
        elif 'index_split' in d: kinds['index_split']+=1
        else: kinds['other:'+d[:10]]+=1
    # sample first chapter unit, see block structure
    sample = top[0] if top else None
    blockkind = None
    nblocks = 0
    if sample:
        sd = os.path.join(out_dir, sample)
        subs = os.listdir(sd)
        blocks = [s for s in subs if os.path.isdir(os.path.join(sd,s))]
        txts = [s for s in subs if s.endswith('.txt')]
        if blocks:
            # are blocks cNN / chunkNN / other
            if any(re.match(r'c[0-9]+$', b) for b in blocks): blockkind='cXX'
            elif any(re.match(r'chunk[0-9]+$', b) for b in blocks): blockkind='chunkNN'
            else: blockkind='otherblock'
            nblocks = len(blocks)
        elif txts:
            blockkind='txt-direct'
    return {'ntop':len(top),'kinds':dict(kinds),'sample':sample,'blockkind':blockkind,'nblocks_sample':nblocks}

books = find_work_books()
print('TOTAL WORK BOOKS:', len(books))
from collections import Counter
cnt = Counter()
for k,od in books.items():
    d = describe(od)
    sig = (tuple(sorted(d['kinds'].keys())), d['blockkind'])
    cnt[sig]+=1
for s,c in cnt.items():
    print('  ', s, '->', c)
print('--- details ---')
for k,od in books.items():
    d = describe(od)
    print(f'  {k:45s} top={d["ntop"]:3d} kinds={d["kinds"]} block={d["blockkind"]} nblk={d["nblocks_sample"]} sample={d["sample"]}')
