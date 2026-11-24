# -*- coding: utf-8 -*-
"""校验 out_ind/v1 指定 chunk 区间的落盘结果：段数不变（对比 .bak_20261125）、
无空段、引号成对、无 ASCII 引号、无 ⟦⟧、无残留英文、CRLF 结构不变。"""
import io, os, re, sys

BASE = "E:/Translate/work_proust/out_ind/v1"


def paras(path):
    t = io.open(path, "r", encoding="utf-8", newline="").read()
    return t, [p for p in t.replace("\r\n", "\n").split("\n") if p.strip()]


def main(a, b):
    bad = []
    tot_p = 0
    for i in range(a, b + 1):
        path = os.path.join(BASE, "chunk%03d" % i, "final.txt")
        bak = path + ".bak_20261125"
        t, ps = paras(path)
        tot_p += len(ps)
        if os.path.exists(bak):
            tb, pb = paras(bak)
            if len(pb) != len(ps):
                bad.append((i, "paras %d->%d" % (len(pb), len(ps))))
            if tb.count("\r\n") != t.count("\r\n"):
                bad.append((i, "crlf count changed"))
        if any(not p.strip() for p in ps):
            bad.append((i, "empty para"))
        for p in ps:
            if p.count("“") != p.count("”"):
                bad.append((i, "quote mismatch", p[:20]))
            if '"' in p or "'" in p:
                bad.append((i, "ascii quote", p[:20]))
            if "⟦" in p or "⟧" in p:
                bad.append((i, "italic marker", p[:20]))
            if re.search(r"\b[a-zA-Z]{3,}\b", p):
                bad.append((i, "latin residue", p[:20]))
            if not re.search(r"[。！？…”』」]$", p):
                bad.append((i, "para end", p[-20:]))
    print("paras total", tot_p)
    for x in bad:
        print("BAD", x)
    print("OK" if not bad else "ISSUES %d" % len(bad))


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))