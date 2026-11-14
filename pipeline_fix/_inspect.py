import os, re, glob as G
from collections import defaultdict

def classify(out_dir):
    top = [d for d in os.listdir(out_dir) if os.path.isdir(os.path.join(out_dir,d))]
    has_c = any(re.match(r'c[0-9]+$', d) for d in top)
    has_sec = any(re.match(r'sec', d) for d in top)
    has_idx = any('index_split' in d for d in top)
    has_chunk = any(re.match(r'chunk', d) for d in top)
    sample = None
    for d in sorted(top):
        if re.match(r'(c[0-9]+|sec[0-9]+|index_split_[0-9]+)$', d):
            sample = d; break
    subkind = None
    if sample:
        sd = os.path.join(out_dir, sample)
        subs = os.listdir(sd)
        if any(re.match(r'c[0-9]+$', s) and os.path.isdir(os.path.join(sd,s)) for s in subs):
            subkind = 'cXX-subfolders'
        elif any(re.match(r'chunk[0-9]+$', s) and os.path.isdir(os.path.join(sd,s)) for s in subs):
            subkind = 'chunk-subfolders'
        elif any(s.endswith('.txt') for s in subs):
            subkind = 'txt-files'
    sk = subkind or 'NONE'
    return (has_c,has_sec,has_idx,has_chunk,sk)

res = defaultdict(list)
for wroot in sorted(G.glob('E:/Translate/work_*')):
    if not os.path.isdir(wroot): continue
    for sub in sorted(os.listdir(wroot)):
        sdir = os.path.join(wroot, sub)
        if not os.path.isdir(sdir): continue
        out_dir = os.path.join(sdir, 'out')
        if not os.path.isdir(out_dir): continue
        c = classify(out_dir)
        key = os.path.basename(wroot)+'/'+sub
        res[c].append(key)

for k, v in sorted(res.items(), key=lambda kv: str(kv[0])):
    print('PATTERN', k, '->', len(v))
    print('   ', v)
