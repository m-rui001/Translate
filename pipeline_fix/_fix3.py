p = 'E:/Translate/pipeline_fix/sync_epub_to_work.py'
s = open(p, encoding='utf-8').read()

# fix 1: footnote regex backslashes
cur = 're.search(r"[([0-9]+)]", sup_inner)'
new = 're.search(chr(92) + "[([0-9]+)" + chr(92) + "]", sup_inner)'
print('footnote cur present:', cur in s)
s = s.replace(cur, new)

# fix 2: chapter_key_num must map v<digits> to vol key
old_ckn = '''def chapter_key_num(name):
    m = re.search(r"([0-9]+)", name)
    return ("num", int(m.group(1))) if m else ("name", name)'''
new_ckn = '''def chapter_key_num(name):
    m = re.search(r"v([0-9]+)", name)
    if m:
        return ("vol", int(m.group(1)))
    m = re.search(r"([0-9]+)", name)
    return ("num", int(m.group(1))) if m else ("name", name)'''
print('ckn present:', old_ckn in s)
s = s.replace(old_ckn, new_ckn)

# remove stray unused b=chr(92) inside extract_paragraphs (harmless but tidy)
s = s.replace('    b = chr(92)
', '')

open(p, 'w', encoding='utf-8').write(s)
print('patched')
