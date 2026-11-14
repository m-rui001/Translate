"""Write the restored verse lineation into the Faust EPUB."""
import json, os, re, shutil, zipfile
from html import escape

EPUB = "out/浮士德上册（坟头草译）.epub"
verse = json.load(open("scratch/faust_verse.json", encoding="utf-8"))
by_file = {}
for v in verse:
    by_file.setdefault(v["file"], {})[v["idx"]] = v["lines"]

with zipfile.ZipFile(EPUB) as z:
    order = [n for n in z.namelist()]
    raw = {n: z.read(n) for n in order}

total = 0
for name, edits in by_file.items():
    s = raw[name].decode("utf-8")
    c = [-1]

    def repl(m):
        c[0] += 1
        if c[0] not in edits:
            return m.group(0)
        body = "<br/>".join(escape(x, quote=False) for x in edits[c[0]])
        return "<p class='verse'>" + body + "</p>"

    s2 = re.sub(r"<p([^>]*)>(.*?)</p>", repl, s, flags=re.S)
    assert s2 != s or not edits
    raw[name] = s2.encode("utf-8")
    total += len(edits)

tmp = EPUB + ".tmp"
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as o:
    for n in order:
        o.writestr(n, raw[n])
shutil.move(tmp, EPUB)
print("verse paragraphs written", total)
