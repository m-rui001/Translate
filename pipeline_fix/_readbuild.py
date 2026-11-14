t = open('E:/Translate/pipeline_build/build_all.py', encoding='utf-8').read()
lines = t.splitlines()
# print key regions
for lo, hi in [(150,200),(330,470)]:
    print('==== lines', lo, hi, '====')
    for i in range(lo-1, min(hi, len(lines))):
        print(f'{i+1}: {lines[i]}')
