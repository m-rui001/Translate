# -*- coding: utf-8 -*-
"""把《追忆似水年华》第一、二、五卷（out_ind）的专名归一到全书 canon。

canon 取值：全书多数 + 通行汉译（与 v3/v4/v6/v7 一致者优先）。
  夏吕斯   -> 夏尔吕        (main 900 : ind 408，且通行作「夏尔吕」)
  凡特伊   -> 凡德伊        (通行汉译作「凡德伊」，v3–v7 已用)
  安德蕾   -> 安德烈        (main 180 : ind 247；取与 main 一致以便全书同形)
  圣路     -> 圣卢
  斯旺     -> 斯万
  叙尔吉斯 -> 絮尔吉
  沙特勒罗 -> 沙泰勒罗
  孔布雷   -> 贡布雷
"""
import ast
import glob
import os
import shutil

PAIRS = [
    ('夏吕斯', '夏尔吕'),
    ('凡特伊', '凡德伊'),
    ('安德蕾', '安德烈'),
    ('圣路', '圣卢'),
    ('斯旺', '斯万'),
    ('叙尔吉斯', '絮尔吉'),
    ('沙特勒罗', '沙泰勒罗'),
    ('孔布雷', '贡布雷'),
]


def main():
    total = 0
    files = 0
    for path in sorted(glob.glob('work_proust/out_ind/v*/chunk*/final.txt')):
        raw = open(path, encoding='utf-8', newline='').read()
        new = raw
        n = 0
        for old, rep in PAIRS:
            if old in new:
                # 保护已经正确的新形（避免替换链式自伤）
                n += new.count(old)
                new = new.replace(old, rep)
        if new == raw:
            continue
        bak = path + '.bak_20261125'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        assert new.count('\n') == raw.count('\n'), path
        open(path, 'w', encoding='utf-8', newline='').write(new)
        files += 1
        total += n
    print('files', files, 'replacements', total)
    ast.parse(open(__file__, encoding='utf-8').read())


if __name__ == '__main__':
    main()
