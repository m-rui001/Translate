p = 'E:/Translate/pipeline_fix/sync_epub_to_work.py'
s = open(p, encoding='utf-8').read()
b = chr(92)
old = '[([0-9]+)]'
new = b + '[([0-9]+)' + b + ']'
print('present:', old in s)
s = s.replace(old, new)
open(p, 'w', encoding='utf-8').write(s)
# sanity: count remaining unintended bracket-only footnote pattern
print('fixed present:', ('[([0-9]+)]' in s))
