"""Split the "num" heading family into its real sub-kinds.

`Fortunata y Jacinta` is hierarchical: single-dash roman capitals (`-I-`) mark
its ten parts, double-dash lower-case (`--i--`) mark the sections inside each
part. `Sotileza` is flat, `I` through `XXIX`. Treating all of those as one
"num" family merges two levels of a hierarchy into one list and produces 31
"chapters" where the book has 10 parts, which is not how the book is divided.

So the family is keyed by (dash width, upper/lower case) and the *coarsest* level
that still recurs is used: the level whose median spacing is largest. A part is
by definition longer than the sections inside it.
"""
import io

p = "E:/Translate/pipeline_gutenberg/structure.py"
s = io.open(p, encoding="utf-8").read()

old_start = s.index("def find_headings(")
old_end = s.index("def _title_like(")

new = '''def _num_key(s: str) -> str:
    """Sub-kind of a bare-number heading: dash width plus case."""
    m = DASHED.match(s.strip())
    body = (m.group("body") if m else s).strip().strip(".")
    if not body:
        return ""
    if body.isdigit():
        return "arabic"
    if body.islower():
        return "roman_lower"
    if body.isupper():
        return "roman_upper"
    return "roman_mixed"


def find_headings(lines: list[str], min_count: int = 3) -> tuple[str, list[int]]:
    """Return (kind, line indexes) for the best recurring heading shape.

    When the file uses bare numbers, the coarsest level wins: `-I-` beats
    `--i--` because the latter numbers the sections *inside* the former. Picking
    the level with the largest median gap reconstructs the printed hierarchy
    instead of flattening it.
    """
    numbered: dict[str, list[int]] = {}
    worded: list[int] = []

    for i, l in enumerate(lines):
        k = _shape(l)
        if not k or not _standalone(lines, i):
            continue
        if k == "num":
            numbered.setdefault(_num_key(l), []).append(i)
        else:
            worded.append(i)

    best: list[tuple[float, str, list[int]]] = []
    for key, idx in numbered.items():
        if len(idx) < min_count:
            continue
        gaps = sorted(idx[j + 1] - idx[j] for j in range(len(idx) - 1))
        med = gaps[len(gaps) // 2] if gaps else 0
        best.append((med, "num:" + key, idx))
    if len(worded) >= min_count:
        gaps = sorted(worded[j + 1] - worded[j] for j in range(len(worded) - 1))
        med = gaps[len(gaps) // 2] if gaps else 0
        best.append((med, "word", worded))

    if not best:
        return "", []
    # coarsest level first; tie-break on count so a flat book still wins
    best.sort(key=lambda t: (t[0], len(t[2])), reverse=True)
    med, kind, idx = best[0]
    return kind, idx


'''

io.open(p, "w", encoding="utf-8").write(s[:old_start] + new + s[old_end:])
print("patched find_headings")
