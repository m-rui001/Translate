t = open('E:/Translate/pipeline_build/build_all.py', encoding='utf-8').read()
lines = t.splitlines()
print('==== 1..120 ====')
for i in range(0,120):
    print(f'{i+1}: {lines[i]}')
