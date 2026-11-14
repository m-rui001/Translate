p = 'E:/Translate/pipeline_fix/sync_epub_to_work.py'
s = open(p, encoding='utf-8').read()
old1 = 'summary = "' + chr(10) + '".join(lines)'
new1 = 'summary = chr(10).join(lines)'
s = s.replace(old1, new1)
old2 = 'print("' + chr(10) + 'Report written to pipeline_fix/sync_report.txt")'
new2 = 'print(chr(10) + "Report written to pipeline_fix/sync_report.txt")'
s = s.replace(old2, new2)
open(p, 'w', encoding='utf-8').write(s)
print('patched1', old1 in s, 'patched2', old2 in s)
