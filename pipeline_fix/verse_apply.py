"""Write restored verse lineation into an EPUB, by file and paragraph index."""
import json, re, shutil, sys, zipfile
from html import escape

epub, data = sys.argv[1], sys.argv[2]
verse = json.load(open(data, encoding="utf-8"))
by_file = {}
for v in verse:
    by_file.setdefault(v["file"], {})[v["idx"]] = v["lines"]

with zipfile.ZipFile(epub) as z:
    order = list(z.namelist())
    raw = {n: z.read(n) for n in order}

total = 0
for name, edits in by_file.items():
    s = raw[name].decode("utf-8")
    c = [-1]

    def repl(m):
        c[0] += 1
        if c[0] not in edits:
            return m.group(0)
        return "<p class='verse'>" + "<br/>".join(escape(x, quote=False) for x in edits[c[0]]) + "</p>"

    s2 = re.sub(r"<p([^>]*)>(.*?)</p>", repl, s, flags=re.S)
    raw[name] = s2.encode("utf-8")
    total += len(edits)

tmp = epub + ".tmp"
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as o:
    for n in order:
        o.writestr(n, raw[n])
shutil.move(tmp, epub)
print("verse paragraphs written", total)
