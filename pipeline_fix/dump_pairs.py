
import glob, json, os, sys
sys.path.insert(0, "pipeline_fix")
import names_scan as N

out = {}
for p in sorted(glob.glob("out/*.epub")):
    t = N.book_text(p)
    c = N.collect(t)
    ps = N.pairs(c)
    if not ps:
        continue
    book = os.path.basename(p)[:-5]
    out[book] = []
    for r in ps[:60]:
        out[book].append({**r,
                          "ctx_major": N.context(t, r["major"], 24),
                          "ctx_minor": N.context(t, r["minor"], 24)})
json.dump(out, open("scratch/audit/name_pairs.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(len(out), sum(len(v) for v in out.values()))
