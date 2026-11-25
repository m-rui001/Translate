# -*- coding: utf-8 -*-
"""cent_h 逐段润色脚本（2026-11-26）。只改元素值，不动数组长度与顺序。"""
import json, ast, os, shutil, re

KEY = 'cent_h'
HERE = os.path.dirname(os.path.abspath(__file__))
ZH = os.path.join(HERE, KEY + '_zh.json')
BAK = ZH + '.bak_20261126'

# 先备份（已存在则不覆盖）
if not os.path.exists(BAK):
    shutil.copy2(ZH, BAK)
    print('backup ->', BAK)
else:
    print('backup exists, skip')

with open(BAK, encoding='utf-8', newline='') as f:
    ref = json.load(f)
with open(ZH, encoding='utf-8', newline='') as f:
    d = json.load(f)

assert len(d) == len(ref) == 148, (len(d), len(ref))

EDITS = [
    # (idx, old, new, 类别)
    (7, '她的意识曾镶触了他自己意识的边缘', '她的意识曾触到他意识的边缘', '①'),
    (7, '在那素朴之可爱的刹那', '在那素朴之美的刹那', '⑥'),
    (12, '令人目盲的美的局部瞬间', '令人目盲之美的局部瞬间', '②'),
    (15, '世人所认识的可爱，是背后那大地灵魂的一番启示', '世人所认识的美，是背后那大地灵魂的一番启示', '⑥'),
    (15, '都是她之可爱的通道', '都是她之美的通道', '⑥'),
    (12, '奇妙、可爱与激情', '奇妙、美与激情', '⑥'),
    (17, '那伟大大地生命的流', '那伟大的大地生命的流', '①'),
    (19, '一种眩目而至高的可爱', '一种眩目而至上的美', '⑥'),
    (20, '那时他镶触到一个更伟大存在的领域的边缘', '那时他触及了一个更伟大存在的领域的边缘', '①'),
    (23, '他最后这样说，那是叙述将近结束时我大着胆子在这里那里提了个问题。',
         '他最后这样说——那时叙述将近结束，我大着胆子东一句西一句地问。', '①'),
    (29, '站在一个认得的小村附近', '站在他认得的一个小村附近', '①'),
    (47, '肉体奢华与浅薄机巧的、看来琐屑的活动', '肉体奢华与浅薄机巧之种种看来琐屑的活动', '②'),
    (47, '更甚于此——一种深沉而痛切的失落之感', '更进一层，是一种深沉而痛切的失落之感', '⑥'),
    (70, '可它外在的可爱上蒙着灰', '可它外在的美上蒙着灰', '⑥'),
    (73, '几乎像某段凄惨的牢狱生活的细节，痛苦、困顿与争斗，是把它们全绑在一起的调子。',
         '几乎像是某段凄惨牢狱生活的细节；痛苦、困顿与争斗，就是把它们全绑在一起的调子。', '①'),
    (81, '「死亡的打击，」回答轻轻地说出。', '「死亡的打击，」那回答轻轻地说了出来。', '③'),
    (98, '因为它把他那激情整个儿地宣告完整了', '因为它把他那份激情整个儿地说尽了', '①'),
    (103, '「——又有几个愿意跟从——更少的人敢。」', '「……又有几个愿意跟从——敢的人就更少了。」', '⑦'),
    (109, '正装上一小批额外货物——核桃木原木；那工程师这样说。', '正额外装上一小批核桃木原木；那工程师这样说。', '①'),
    (112, '听说在山那一类里，那是个了不起的东西。', '听说论山，那可是一样了不起的东西。', '③'),
    (126, '可归根到底，这难道不是比文明借以产生另外那些类型的、那套相对晚近才发展出来的理性方式，具有更大的精神意义与价值？',
          '可归根到底，文明靠一套相对晚近才发展出来的理性方式产生了另外那些类型；比起这套方式，它难道不具有更大的精神意义与价值？', '②'),
    (126, '比起这套方式，它难道不具有更大的精神意义与价值？', '比起这套方式，这种天性难道不具有更大的精神意义与价值？', '④'),
    (134, '她的意识又一次擦伤、镶触了他自己意识的边缘。', '她的意识又一次触及并擦伤了他意识的边缘。', '①'),
    (137, '那与大地同行时自由的、奔流般的通道的欢乐', '那与大地同行时自由奔涌的通道之乐', '②'),
    (137, '小小空置的肉身躯壳作过调查', '空置的小小肉身作过查验', '⑥'),
    (139, '在那人的抚慰的宁静面前慢慢退去', '在对方那抚慰的宁静面前慢慢退去', '①'),
    (144, '向这另一个人敞开了心，让他灵魂的闸门大大敞开', '向这另一个人敞开了心，任凭灵魂的闸门大大敞开', '①'),
]

n = 0
for idx, old, new, cat in EDITS:
    assert old in d[idx], (idx, old)
    assert d[idx].count(old) == 1, (idx, old)
    d[idx] = d[idx].replace(old, new)
    n += 1
    print('[%s] d[%d] ok' % (cat, idx))

# ---- 落盘（保持 indent=1；CRLF/LF 照原样）----
CRLF = chr(13) + chr(10)
is_crlf = (CRLF.encode()).decode() and b'\r\n' in open(BAK, 'rb').read()
with open(ZH, 'w', encoding='utf-8', newline=CRLF if is_crlf else '') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)

# ---- 自检 ----
with open(ZH, encoding='utf-8', newline='') as f:
    chk = json.load(f)
raw = open(ZH, 'rb').read()
assert len(chk) == len(ref) == 148
assert all(t.strip() for t in chk), 'empty paragraph'
assert '"' not in ''.join(chk), 'ASCII double quote'
assert '\u27e6' not in ''.join(chk), 'injected marker'
for i, t in enumerate(chk):
    for bad in ('。。', '，，', '、、', '！！', '？？'):
        assert bad not in t, (i, bad)
    assert not re.search(r'[\u4e00-\u9fff] +[A-Za-z]|[A-Za-z]+ +[\u4e00-\u9fff]', t), (i, t[:40])
han = sum(1 for t in chk for c in t if '\u4e00' <= c <= '\u9fff')
print('改动条数 =', n)
print('数组长度 =', len(chk), '(备份', len(ref), ')')
print('汉字 =', han)
print('换行符 =', 'CRLF' if b'\r\n' in raw else 'LF')
print('涉及段 =', [i for i in range(len(chk)) if chk[i] != ref[i]])

ast.parse(open(__file__, encoding='utf-8').read())
print('self-parse OK')