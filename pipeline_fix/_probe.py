import zipfile, os, glob

out_dir = "E:/Translate/out"
epubs = glob.glob(os.path.join(out_dir, "*.epub"))
print("num epubs", len(epubs))
f = epubs[0]
print("sample epub:", f)
try:
    z = zipfile.ZipFile(f)
    names = z.namelist()
    print("entries", len(names))
    for n in names:
        if n.endswith('.opf') or n.endswith('c001.xhtml') or n.endswith('c002.xhtml'):
            print("  ", n)
except Exception as e:
    print("ERR", repr(e))
