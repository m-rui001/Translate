# -*- coding: utf-8 -*-
"""全书体检后的收尾修补（2026-11-26）。
每处均为唯一子串定位 → 断言命中数 → 替换；段数/行数/空行/换行符不变。"""
import ast
import os

BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = [
    # ── 引号失衡（三处真问题）────────────────────────────────
    # v4/chunk042 p0：内层引语『盖尔芒特亲王夫人。』之后多一个收引号，
    # 使得公爵那段长话在「纠正错误。」处又收一次（深度归负）。删。
    ('out/v4/chunk042/final.txt',
     '‘盖尔芒特亲王夫人。’”正当我担心',
     '‘盖尔芒特亲王夫人。’正当我担心'),
    # v5/chunk111 p18：韦尔迪兰夫人被打断后接着说「他害人……我会不舒服的，」
    # 但续话没有重新起引号，段末那个收引号无处可收。补前引号。
    ('out_ind/v5/chunk111/final.txt',
     '太过分了；他害人，害得很厉害',
     '太过分了；“他害人，害得很厉害'),
    # v2/chunk217 p0：叙述者括注插在阿尔贝蒂娜话中间，括注后她只是接着说，
    # 原译却多起了一个前引号（深度 1→2）。删。
    ('out_ind/v2/chunk217/final.txt',
     '可视的形象）。“再说，她何止',
     '可视的形象）。再说，她何止'),

    # ── 分节行统一为「＊　＊　＊」（全角星＋全角空）───────────
    ('out_ind/v1/chunk018/final.txt', '……', '＊　＊　＊'),
    ('out_ind/v1/chunk056/final.txt', '……', '＊　＊　＊'),
    ('out_ind/v1/chunk081/final.txt', '……', '＊　＊　＊'),
    ('out_ind/v2/chunk092/final.txt', '...', '＊　＊　＊'),
    ('out_ind/v2/chunk155/final.txt', '* * * * *', '＊　＊　＊'),
    ('out_ind/v5/chunk030/final.txt', '＊ ＊ ＊', '＊　＊　＊'),
    ('out_ind/v5/chunk073/final.txt', '＊ ＊ ＊', '＊　＊　＊'),

    # ── 篇内标题的空格改全角 ───────────────────────────────
    ('out_ind/v1/chunk082/final.txt', '第二部 斯万之恋', '第二部　斯万之恋'),
]


def stats(txt):
    norm = txt.replace('\r\n', '\n')
    lines = norm.split('\n')
    return (len(lines), sum(1 for x in lines if x.strip()), txt.count('\r\n'))


def main():
    for rel, old, new in EDITS:
        p = os.path.join(BASE, rel)
        with open(p, encoding='utf-8', newline='') as f:
            txt = f.read()
        if new in txt and txt.count(old) == 0:
            print(f'skip (already applied) {rel}: {old!r}')
            continue
        assert txt.count(old) == 1, (rel, old, txt.count(old))
        before = stats(txt)
        txt2 = txt.replace(old, new)
        after = stats(txt2)
        assert before == after, (rel, before, after)
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(txt2)
        print(f'ok {rel}: {old!r} -> {new!r}  lines={after[0]} paras={after[1]} crlf={after[2]}')

    ast.parse(open(__file__, encoding='utf-8').read())


if __name__ == '__main__':
    main()