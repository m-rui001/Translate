"""Fix level selection: numbered levels only compete with numbered levels.

The previous version let a *numbered* level and the *worded* headings compete on
median spacing alone. That broke two books, because a `word` match can be a
chapter-word that only appears at part level:

  * `La Regenta`  -- `--I--`..`--XXX--` (30 chapters) lost to the words
    "Prólogo"/"TOMO II" (3 hits, huge gaps), collapsing 30 chapters into 3;
  * `O Guarany`   -- its 29 chapters lost to "TOMO PRIMEIRO"/"SEGUNDA PARTE".

Meanwhile the coarsest-level rule *is* wanted inside the numbered family, where
`Fortunata`'s `-I-` parts must beat its `--i--` sections. So the two families are
compared on count first (a real chapter structure has many entries), and only
spacing decides ties within a family.
"""
import io

p = "E:/Translate/pipeline_gutenberg/structure.py"
s = io.open(p, encoding="utf-8").read()

old_start = s.index("    best: list[tuple[float, str, list[int]]] = []")
old_end = s.index("def _title_like(")

new = '''    num_levels: list[tuple[float, str, list[int]]] = []
    for key, idx in numbered.items():
        if len(idx) < min_count:
            continue
        gaps = sorted(idx[j + 1] - idx[j] for j in range(len(idx) - 1))
        med = gaps[len(gaps) // 2] if gaps else 0
        num_levels.append((med, "num:" + key, idx))

    # Within the numbered family the coarsest level wins: `-I-` beats `--i--`
    # because the latter numbers sections *inside* the former.
    best_num = max(num_levels, key=lambda t: (t[0], len(t[2])), default=None)

    best_word = None
    if len(worded) >= min_count:
        gaps = sorted(worded[j + 1] - worded[j] for j in range(len(worded) - 1))
        med = gaps[len(gaps) // 2] if gaps else 0
        best_word = (med, "word", worded)

    # The two families are not commensurable: a chapter word can legitimately
    # appear only at part level ("TOMO PRIMEIRO"), and a numbered level can be
    # only the sections inside a part. Density decides, because a chapter
    # structure has many entries and a part structure has few.
    if best_num and best_word:
        if len(best_word[2]) >= 2 * len(best_num[2]) and len(best_word[2]) >= 8:
            return best_word[1], best_word[2]
        return best_num[1], best_num[2]
    if best_num:
        return best_num[1], best_num[2]
    if best_word:
        return best_word[1], best_word[2]
    return "", []


'''

io.open(p, "w", encoding="utf-8").write(s[:old_start] + new + s[old_end:])
print("patched level selection")
