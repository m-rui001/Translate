import os, re
roots = ['E:/Translate/pipeline', 'E:/Translate/pipeline_build', 'E:/Translate/pipeline_pub', 'E:/Translate/pipeline_polish', 'E:/Translate/pipeline_new', 'E:/Translate/pipeline_overhaul']
hits = []
for root in roots:
    if not os.path.isdir(root): continue
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if f.endswith('.py'):
                p = os.path.join(dp, f)
                try:
                    t = open(p, encoding='utf-8', errors='ignore').read()
                except: continue
                if 'final.txt' in t and ('<p' in t or 'xhtml' in t or 'write' in t.lower()):
                    # find lines mentioning final.txt and p
                    for i, line in enumerate(t.splitlines(), 1):
                        if 'final.txt' in line or ('<p' in line and 'final' in t):
                            hits.append((p, i, line.strip()[:140]))
print('PY files with final.txt + p:', len(hits))
for h in hits[:60]:
    print(h)
