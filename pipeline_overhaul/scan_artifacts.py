import json, glob, re

CJK = "一-鿿"


def has_dup(t):
    # three identical adjacent CJK chars
    for i in range(len(t) - 2):
        if t[i] == t[i + 1] == t[i + 2] and "一" <= t[i] <= "鿿":
            return True
    # an adjacent repeated 2-char run (e.g. "层一层")
    for i in range(len(t) - 3):
        if t[i:i + 2] == t[i + 2:i + 4] and "一" <= t[i] <= "鿿":
            return True
    return False


def scan(book):
    bad = []
    for f in sorted(glob.glob("work_overhaul/%s/final/*.json" % book)):
        d = json.load(open(f, encoding="utf-8"))
        for i, t in enumerate(d["texts"]):
            if has_dup(t):
                bad.append((d["id"], i, t[:60]))
    print(book, "artifacts", len(bad))
    for b in bad[:12]:
        print("  ", b)


for b in ["whale", "soledad"]:
    scan(b)
