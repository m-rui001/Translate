import io, re

p = "E:/Translate/pipeline_gutenberg/structure.py"
s = io.open(p, encoding="utf-8").read()

old = s[s.index('DASHED = re.compile('):]
old = old[:old.index('\n')]
new = ('# `--I--` (La Regenta), `-I-` (Los pazos de Ulloa), `--12--` (Fortunata).\n'
       '# Both dash widths occur in these sources, so the run is one *or* two dashes.\n'
       'DASHED = re.compile(r"^-{1,2}\\s*(?P<body>[A-Za-z0-9IVXLC][A-Za-z0-9IVX .\'\\u2019\\-]{0,40}?)\\s*-{1,2}$")')
s = s.replace(old, new)

# a heading may also be a bare title-cased word run found at regular spacing
addition = '''

def short_title_lines(lines: list[str], min_count: int = 3) -> list[int]:
    """Chapters by bare title lines at regular spacing, with no numbering at all.

    `Bunte Steine` heads its six pieces with "Granit.", "Kalkstein." and so on,
    prints no contents list, and repeats nothing -- so neither numbering nor
    repetition can find them. What distinguishes them is shape and spacing: a
    short, title-cased, sentence-less line alone between blank lines, separated
    from its neighbours by thousands of lines rather than dozens.

    The spacing test is what makes this safe. Dialogue lines are short and alone
    too, but they cluster; real chapter openings in these books are hundreds of
    lines apart. Requiring the median gap to exceed 200 lines rejects dialogue
    while accepting chapter heads.
    """
    cands: list[int] = []
    for i, l in enumerate(lines):
        s = l.strip()
        if not _title_like(s) or NUMONLY.match(s) or _shape(s):
            continue
        if not _standalone(lines, i):
            continue
        # a title line is a heading, so it is followed by text, not by a quote
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if nxt.startswith(("\\u00bb", "\\u00ab", '"', "-", "\\u2014")):
            continue
        cands.append(i)
    if len(cands) < min_count:
        return []
    gaps = [cands[j + 1] - cands[j] for j in range(len(cands) - 1)]
    gaps.sort()
    if gaps[len(gaps) // 2] < 200:
        return []
    out = [cands[0]]
    for i in cands[1:]:
        if i - out[-1] > 200:
            out.append(i)
    return out if len(out) >= min_count else []
'''

s = s.replace('\n\ndef chapter_starts(', addition + '\n\ndef chapter_starts(')
s = s.replace(
    '    for name, fn in (("toc", toc_titles), ("repeat", repeat_titles)):',
    '    for name, fn in (("toc", toc_titles), ("repeat", repeat_titles),\n'
    '                     ("titles", short_title_lines)):')

io.open(p, "w", encoding="utf-8").write(s)
print("patched")
