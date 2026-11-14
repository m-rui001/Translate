"""Two level-selection repairs that the generic rules could not make.

Both were found by listing the chosen indexes and reading the headings.

1. `Fortunata y Jacinta` restarts its numbering inside each part: `-I-`..`-X-`
   under "Parte primera", then `-I-` again for "Parte segunda". So single-dash
   capitals are the *sections*, and the real parts are the four "Parte N"
   headings that the `word` detector had found. The fix is to notice a restart:
   when a numbered sequence returns to its first value, the numbering is not
   top-level.

2. `Bunte Steine` lost "Granit." because it sits only seven lines after the
   author's signature, inside the minimum-gap floor, and gained three non-chapter
   entries ("Nachwort.", the translator's name) because they are also short
   title-cased standalone lines. The fix is to trust the book's own contents
   list when one exists and its entries actually occur in the body, and to fall
   back to spacing only when no usable contents list is printed.

Both are content tests, not tuning: neither invents structure the file does not
state.
"""
import io

p = "E:/Translate/pipeline_gutenberg/structure.py"
s = io.open(p, encoding="utf-8").read()


# ── 1. detect restarted numbering ────────────────────────────────────────────
anchor = '''    num_levels: list[tuple[float, str, list[int]]] = []'''
addition = '''    def _restarts(idx: list[int]) -> bool:
        """True when the numbering returns to its first value -- i.e. it is not
        top level. `Fortunata` numbers -I-..-X- inside each of its four parts."""
        vals = []
        for i in idx:
            b = _shape(lines[i]) and lines[i].strip()
            m = DASHED.match(b)
            v = (m.group("body") if m else b).strip().strip(".")
            vals.append(v.upper())
        for j in range(1, len(vals)):
            if vals[j] == vals[0] and j > 2:
                return True
        return False

'''
s = s.replace(anchor, addition + anchor, 1)


# ── 2. prefer contents-list anchoring over spacing ───────────────────────────
old = '''def chapter_starts(lines: list[str]) -> tuple[str, list[int]]:
    """Best available chapter delineation for this file."""
    kind, idx = find_headings(lines)'''
new = '''def contents_anchored(lines: list[str], min_count: int = 3) -> list[int]:
    """Chapter openings found by matching a printed contents list to the body.

    `Bunte Steine` prints "Inhalt." with each piece and its page number, then
    heads each piece with the same word ("Granit.", "Kalkstein.", ...). Those
    occurrences *are* the chapter starts, exactly, with no spacing guesswork.

    Matching is on the leading word of each contents entry, because the entry
    carries a page number ("Granit   1") while the heading does not ("Granit.").
    """
    import re as _re
    start = -1
    for i, l in enumerate(lines[:600]):
        if _re.match(r"^\\s*(?:Inhalt|Contents|\\u00cdndice|Indice|\\u00cdNDICE|"
                     r"Sum\\u00e1rio|\\u00ceandice|Sommario)\\s*[.:]?\\s*$", l, _re.I):
            start = i
            break
    if start < 0:
        return []

    heads: list[str] = []
    for l in lines[start + 1:start + 80]:
        t = l.strip()
        if not t:
            if heads:
                break
            continue
        # "Granit                        1" -> leading words
        m = _re.match(r"^(.+?)\\s{2,}\\d{1,4}\\s*$", t) or _re.match(r"^(.+?)\\s+\\d{1,4}\\s*$", t)
        if not m:
            break
        heads.append(m.group(1).strip())
    if len(heads) < min_count:
        return []

    idx: list[int] = []
    for hi, h in enumerate(heads):
        pat = _re.compile(r"^" + _re.escape(h) + r"\\b", _re.I)
        for i in range(start, len(lines)):
            t = lines[i].strip()
            if not t.startswith(h[:6]):
                continue
            if not pat.match(t):
                continue
            if not _standalone(lines, i):
                continue
            # heading is the bare word, possibly with a full stop -- not a sentence
            if len(t) <= len(h) + 2:
                idx.append(i)
                break
    return idx if len(idx) >= min_count else []


def chapter_starts(lines: list[str]) -> tuple[str, list[int]]:
    """Best available chapter delineation for this file."""
    anchored = contents_anchored(lines)
    if len(anchored) >= 3:
        return "contents", anchored
    kind, idx = find_headings(lines)'''

s = s.replace(old, new, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("patched restarts + contents anchoring")
