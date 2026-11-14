
import os, zipfile
n = 0
for fn in sorted(os.listdir("out")):
    if not fn.endswith(".epub"):
        continue
    p = os.path.join("out", fn)
    z = zipfile.ZipFile(p)
    items = [(i, z.read(i.filename)) for i in z.infolist()]
    z.close()
    changed = False
    out = []
    for info, data in items:
        if info.filename.endswith(".xhtml"):
            s = data.decode("utf-8")
            s2 = s.replace("<p class='tr'>坟头草译</p>", "<p class='tr'>坟头草\u3000译</p>")
            if s2 != s:
                changed = True
                data = s2.encode("utf-8")
        out.append((info, data))
    if changed:
        tmp = p + ".tmp"
        with zipfile.ZipFile(tmp, "w") as z2:
            for info, data in out:
                z2.writestr(info, data)
        os.replace(tmp, p)
        n += 1
print("restored", n)
