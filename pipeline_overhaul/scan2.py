import json, glob


def find_dup(t):
    for i in range(len(t) - 2):
        if t[i] == t[i + 1] == t[i + 2] and "一" <= t[i] <= "鿿":
            return t[i:i + 3]
    for i in range(len(t) - 3):
        if t[i:i + 2] == t[i + 2:i + 4] and "一" <= t[i] <= "鿿":
            return t[i:i + 4]
    return None


for book in ["whale"]:
    n = 0
    for f in sorted(glob.glob("work_overhaul/%s/final/*.json" % book)):
        d = json.load(open(f, encoding="utf-8"))
        for i, t in enumerate(d["texts"]):
            s = find_dup(t)
            if s:
                n += 1
                if n <= 30:
                    print(d["id"], i, repr(s), t[max(0, t.index(s) - 12):t.index(s) + 16])
    print(book, "total", n)
