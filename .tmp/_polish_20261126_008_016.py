# -*- coding: utf-8 -*-
"""v3 chunk008 / chunk013 / chunk016 逐段润色落盘脚本（2026-11-26 轮）

准则：E:/Translate/POLISH_BRIEF_2026-11-25.md（只改七类，不重译、不改情节、不增删段）
方式：定位唯一子串 → 替换 → assert count == 1；绝不整文件重写；
      读写 newline='' 保 CRLF；行数/段数/空行结构前后比对。
"""
import ast
import os
import shutil
import sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)))
BAK_SUFFIX = '.bak_20261125'

# (类别, 旧句, 新句)
EDITS = {
    '008': [
        ('①',
         '说出与我熟知的那些话相似的话',
         '说出与我熟悉的那类话相仿的言辞'),
        ('①',
         '他们围坐在摆好餐具的桌布旁',
         '他们围坐在铺好桌布、摆好餐具的餐桌旁'),
        ('⑥',
         '他们便依次呈现出一次骑士比武和一片国有森林的面貌',
         '他们便依次呈现出骑士比武和国有森林的面貌'),
    ],
    '013': [
        ('④',
         '而那位半神自己明白，她和那位半神用这几句话概括着怎样崇高的思想',
         '而那位半神自己明白，他们两人用这几句话概括着怎样崇高的思想'),
        ('⑥',
         '她顺着这场游戏，也以同样神秘的促狭回答',
         '他顺着这场游戏，也以同样神秘的促狭回答'),
    ],
    '016': [
        ('①',
         '这就是人们约定俗成地授予这些称号的东西',
         '这就是人们约定俗成地冠以这些称号的东西'),
        ('⑤',
         '火星、维纳斯、土星',
         '玛尔斯、维纳斯、萨图恩'),
        ('⑥',
         '我本该从这错觉中醒悟过来',
         '我终究从这错觉中醒悟了过来'),
        ('③',
         '而是我把它们与我预先形成的观念联系起来，与我对自己说“我终于听到贝尔玛了”'
         '所感到的愉悦联系起来。',
         '而是我把它们与我预先形成的观念、与我对自己说“我终于听到贝尔玛了”'
         '所感到的愉悦联系起来的产物。'),
    ],
}


def structure(text):
    """(总字符数, 行数, 空行数, 段落数) —— 用于前后比对。"""
    lines = text.split('\r\n')
    return (
        len(text),
        text.count('\r\n'),
        sum(1 for ln in lines if ln == ''),
        sum(1 for ln in lines if ln != ''),
    )


def han(text):
    return sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')


def main(dry=False):
    total = 0
    tally = {k: 0 for k in '①②③④⑤⑥⑦'}
    for chunk in ('008', '013', '016'):
        path = os.path.join(BASE, 'chunk' + chunk, 'final.txt')
        with open(path, encoding='utf-8', newline='') as fh:
            text = fh.read()

        before = structure(text)
        han_before = han(text)

        done = 0
        for cat, old, new in EDITS[chunk]:
            assert old != new
            if text.count(old) == 1:
                text = text.replace(old, new)
                tally[cat] += 1
                total += 1
                done += 1
            elif text.count(old) == 0 and text.count(new) == 1:
                done += 1  # 本脚本已跑过，此条已落盘（幂等）
                tally.setdefault('已应用', 0)
                tally['已应用'] = tally.get('已应用', 0) + 1
            else:
                raise AssertionError((chunk, cat, old, text.count(old)))

        after = structure(text)
        assert before[1] == after[1], ('行数变了', chunk, before, after)
        assert before[2] == after[2], ('空行数变了', chunk, before, after)
        assert before[3] == after[3], ('段落数变了', chunk, before, after)
        assert '\r\n' in text and '\n' not in text.replace('\r\n', '')
        assert '⟦' not in text and '⟧' not in text

        print('chunk%s 本跑改动 %d 条 / 清单 %d 条 | 行数 %d=%d 段数 %d=%d 空行 %d=%d | '
              '汉字 %d→%d | 换行 CRLF'
              % (chunk, done, len(EDITS[chunk]), before[1], after[1],
                 before[3], after[3], before[2], after[2],
                 han_before, han(text)))

        if dry:
            continue

        bak = path + BAK_SUFFIX
        if os.path.exists(bak):
            print('  backup 已存在，未覆盖：%s' % os.path.basename(bak))
        else:
            shutil.copyfile(path, bak)
            print('  backup 新建：%s' % os.path.basename(bak))

        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)

    print('合计 %d 条 —— ' % total
          + ' '.join('%s%d' % (k, v) for k, v in tally.items() if v))
    return total


if __name__ == '__main__':
    main(dry='--dry' in sys.argv)
    ast.parse(open(__file__, encoding='utf-8').read())
    print('ast.parse 自查通过')