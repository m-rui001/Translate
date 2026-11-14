p = 'E:/Translate/pipeline_fix/sync_epub_to_work.py'
lines = open(p, encoding='utf-8').read().split(chr(10))
for i in range(328, 340):
    if i < len(lines):
        print(i+1, repr(lines[i]))
