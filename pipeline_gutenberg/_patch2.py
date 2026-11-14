"""Rewrite `short_title_lines` with cluster-based spacing.

The first version took the median gap over *all* short standalone lines and
rejected anything below 200 lines. That fails on two real books: `Bunte Steine`
spaces chapters 1200-2500 lines apart (fine) but `Immensee` is a novella whose
chapters sit only 50-100 lines apart. Worse, both print a contents block whose
entries are one line apart, which drags the median to ~1 and rejects the book
even though its chapters are perfectly regular.

Clustering first fixes both: entries of a contents block collapse into a single
occurrence, and a chapter opening never has another candidate within a few lines
of it. What still distinguishes chapters from dialogue is that chapters recur at
a spacing of tens of lines, while dialogue clusters every few lines.
"""
import io
import re

p = "E:/Translate/pipeline_gutenberg/structure.py"
s = io.open(p, encoding="utf-8").read()

start = s.index("def short_title_lines(")
end = s.index("def chapter_starts(")

new = '''def short_title_lines(lines: list[str], min_count: int = 3) -> list[int]:
    """Chapters by bare title lines at regular spacing, with no numbering at all.

    `Bunte Steine` heads its six pieces with "Granit.", "Kalkstein." and so on,
    prints no contents list, and repeats nothing -- so neither numbering nor
    repetition can find them. What distinguishes them is shape and spacing: a
    short, title-cased, sentence-less line alone between blank lines, opening
    text rather than a quotation.

    Candidates are clustered before being judged. A contents block repeats its
    entries one per line, so those collapse into a single cluster; a real chapter
    opening is isolated. The test that then rejects dialogue is the *cluster*
    spacing: chapter openings recur tens or hundreds of lines apart, dialogue
    every few lines. Using the median over raw candidates instead would let a
    contents block drag the median to 1 and lose the book.
    """
    cands: list[int] = []
    for i, l in enumerate(lines):
        s = l.strip()
        if not _title_like(s) or NUMONLY.match(s) or _shape(s):
            continue
        if not _standalone(lines, i):
            continue
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if nxt.startswith(("\\u00bb", "\\u00ab", '"', "\\u2014")):
            continue
        cands.append(i)
    if len(cands) < min_count:
        return []

    clusters = [cands[0]]
    for i in cands[1:]:
        if i - clusters[-1] > 6:
            clusters.append(i)
    if len(clusters) < min_count:
        return []

    gaps = sorted(clusters[j + 1] - clusters[j] for j in range(len(clusters) - 1))
    if gaps[len(gaps) // 2] < 30:
        return []

    # keep the largest subset of clusters that stay far apart from one another
    floor = max(30, gaps[len(gaps) // 2] // 3)
    out = [clusters[0]]
    for i in clusters[1:]:
        if i - out[-1] >= floor:
            out.append(i)
    return out if len(out) >= min_count else []


'''

io.open(p, "w", encoding="utf-8").write(s[:start] + new + s[end:])
print("patched short_title_lines")
