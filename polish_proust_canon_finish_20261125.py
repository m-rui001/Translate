# -*- coding: utf-8 -*-
"""把普鲁斯特全书残余的少数派专名归一（按 canon 表多数派）。"""
import ast, glob, os, shutil

PAIRS = [
    ('拉斯佩利埃', '拉斯普利埃'),
    ('凡特伊', '凡德伊'),
    ('库尔瓦西埃', '库尔瓦西耶'),
    ('夏特罗', '沙泰勒罗'),
    ('沙特勒罗', '沙泰勒罗'),
    ('圣安德烈-德尚普', '圣安德烈-德尚普'),   # no-op guard
    ('圣安德烈-德尚', '圣安德烈-德尚普'),
    ('维尔邦', '瓦朗邦'),
    ('叙尔吉斯', '絮尔吉'),
    ('朗布雷萨克', '昂布勒萨克'),
    ('圣路', '圣卢'),
    ('阿尔帕容', '阿尔帕戎'),
    ('阿尔库尔', '达尔让库尔'),
    ('孔布雷', '贡布雷'),
    ('玛丽·安托瓦内特', '玛丽-安托瓦内特'),
]

def main():
    total = 0
    for path in sorted(glob.glob('work_proust/out/v*/*/final.txt')):
        raw = open(path, encoding='utf-8', newline='').read()
        if '拉斯佩利埃' not in raw and '凡特伊' not in raw and '库尔瓦西埃' not in raw \
           and '夏特罗' not in raw and '圣路' not in raw and '阿尔帕容' not in raw \
           and '孔布雷' not in raw and '叙尔吉斯' not in raw and '朗布雷萨克' not in raw \
           and '维尔邦' not in raw and '沙特勒罗' not in raw and '阿尔库尔' not in raw \
           and '玛丽·安托瓦内特' not in raw and '圣安德烈-德尚' not in raw:
            continue
        new = raw
        n = 0
        for old, rep in PAIRS:
            if old == rep:
                continue
            if old in new:
                n += new.count(old)
                new = new.replace(old, rep)
        if new == raw:
            continue
        bak = path + '.bak_20261125'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        assert new.count('\n') == raw.count('\n'), path
        open(path, 'w', encoding='utf-8', newline='').write(new)
        total += n
        print('%-60s %d' % (path, n))
    print('total replaced', total)
    ast.parse(open(__file__, encoding='utf-8').read())

if __name__ == '__main__':
    main()
