# -*- coding: utf-8 -*-
"""《追忆似水年华》第一卷 chunk000-014 通读润色 p1（2026-11-25 轮）

只做「定位唯一子串 -> 替换 -> 断言命中数」的改法，不整文件重写。
- 称谓/专名归一见每条注释
- 已有 .bak_20261125 的不覆写
"""
import os
import sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    'work_proust', 'out_ind', 'v1')

# (chunk, old, new, expected_count, 类别, 理由)
EDITS = [
    # ---- chunk001 ----
    ('chunk001', '我是在乡下，在祖父家里', '我是在乡下，在外祖父家里', 1, '⑤',
     '同一间卧房同段后文即作「在外祖父母家」，grand-père 全书 canon 为「外祖父」'),
    # ---- chunk002 ----
    ('chunk002', '在贡布雷外姑婆家', '在贡布雷外姑祖母家', 1, '⑤',
     'grand\'tante 全书两派：姑祖母(8 个 chunk)／姑婆(7 个 chunk)，归并为「姑祖母」'),
    # ---- chunk004 ----
    ('chunk004', '姑婆', '姑祖母', 5, '⑤', '同上，grand\'tante 归并'),
    # ---- chunk006 ----
    ('chunk006', '可我的姑祖母和祖父母全然不曾察觉', '可我的姑祖母和外祖父母全然不曾察觉', 1, '⑤',
     '同一句里既有「姑祖母」又有「祖父母」，全书 canon 为外祖父母'),
    # ---- chunk007 ----
    ('chunk007', '姑婆', '姑祖母', 6, '⑤', '同上，grand\'tante 归并'),
    ('chunk007', '阿利巴巴', '阿里巴巴', 2, '⑤', 'Ali Baba 通行汉译作「阿里巴巴」；chunk024 已作「阿里巴巴」'),
    # ---- chunk009 ----
    ('chunk009', '外祖姨', '姑祖母', 5, '⑤', '同段 French 作 ma grand\'tante，与全书其他译法归一'),
    ('chunk009', '在科罗展览上展出的画', '在柯罗展览上展出的画', 1, '⑤',
     'Corot 全书 3 处，通行汉译为「柯罗」'),
    ('chunk009', '他们对一切与上流社会生活或近或远沾边的东西', '她们对一切与上流社会生活或近或远沾边的东西',
     1, '④', '上文主语是外祖母的「两个老姑娘」姐妹（les deux sœurs），此处却换成了男性「他们」'),
    # ---- chunk010 ----
    ('chunk010', '姑婆', '姑祖母', 2, '⑤', '同上，grand\'tante 归并'),
    # ---- chunk014 ----
    ('chunk014', '外祖父转身对着两个姨婆补了一句', '外祖父转身对着两位姑妈补了一句', 1, '⑤',
     '同一段下文即作「弗洛拉姑妈」「塞莉娜姑妈」，指同一对姐妹，称谓须一'),
    ('chunk014', '我很久以前就收到过他一封讲这件事的信，我赶紧没有照着办',
     '我很久以前就收到过他一封讲这件事的信，我赶紧搁下了，没有照办', 1, '①',
     '「赶紧没有照着办」不合汉语（empressé de ne pas me conformer 的硬搬），否定副词不能直接受「赶紧」修饰'),
]


def main():
    changed = {}
    for chunk, old, new, expected, kind, why in EDITS:
        path = os.path.join(BASE, chunk, 'final.txt')
        with open(path, encoding='utf-8', newline='') as f:
            text = f.read()
        assert old in text, (chunk, old[:30])
        assert text.count(old) == expected, (chunk, old[:30], text.count(old))
        assert new not in text or new == old
        # 备份（已有 .bak_20261125 不覆写）
        bak = path + '.bak_20261125'
        if not os.path.exists(bak):
            with open(bak, 'w', encoding='utf-8', newline='') as f:
                f.write(text)
        # 段落数守恒
        n_before = len([l for l in text.split('\n') if l.strip()])
        text = text.replace(old, new)
        n_after = len([l for l in text.split('\n') if l.strip()])
        assert n_before == n_after, chunk
        assert '"' not in text and "'" not in text, chunk
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        changed.setdefault(chunk, []).append((kind, old[:20], new[:20], expected, why))
        print(f'[ok] {chunk} {kind} x{expected}: {old[:24]} -> {new[:24]}')

    total = sum(expected for _, _, _, expected, _, _ in EDITS)
    print(f'\n共 {len(EDITS)} 条编辑，实际替换 {total} 处，涉及 {len(changed)} 个 chunk')
    return changed


if __name__ == '__main__':
    main()


ast_ok = True
import ast  # noqa: E402
ast.parse(open(__file__, encoding='utf-8').read())