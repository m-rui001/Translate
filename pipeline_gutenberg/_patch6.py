"""Two final structure repairs.

1. `Bunte Steine`'s contents block opens with a column header ("Seite") before the
   first entry. The parser treated that header as an unparsable entry and gave up,
   so the book kept falling back to spacing and lost "Granit.". Skipping the
   header line makes the printed contents list usable, which is exact: it names
   the six pieces plus "Einleitung" and "Nachwort".

2. `Fortunata y Jacinta` restarts its numbering inside each part, so single-dash
   capitals mark sections, not parts. A restart is direct evidence that a
   numbered level is *not* top level; when one is detected, the coarser `word`
   level (the four "Parte ..." headings) must win.
"""
import io

p = "E:/Translate/pipeline_gutenberg/structure.py"
s = io.open(p, encoding="utf-8").read()

# 1. skip a column header inside the contents block
old = '''    heads: list[str] = []
    for l in lines[start + 1:start + 80]:
        t = l.strip()
        if not t:
            if heads:
                break
            continue'''
new = '''    heads: list[str] = []
    for l in lines[start + 1:start + 80]:
        t = l.strip()
        if not t:
            if heads:
                break
            continue
        # a contents list may open with a column header ("Seite", "Page")
        if re.match(r"^(?:Seite|Page|P\\u00e1gina|Pagina|Sida)\\s*$", t, re.I):
            continue'''
s = s.replace(old, new, 1)

# 2. a restarted numbering must not win over the coarser word level
old2 = '''    if best_num and best_word:
        if len(best_word[2]) >= 2 * len(best_num[2]) and len(best_word[2]) >= 8:
            return best_word[1], best_word[2]
        return best_num[1], best_num[2]'''
new2 = '''    if best_num and best_word:
        if len(best_word[2]) >= 2 * len(best_num[2]) and len(best_word[2]) >= 8:
            return best_word[1], best_word[2]
        if _restarts(best_num[2]) and len(best_word[2]) >= 3:
            # the numbering cycles, so it labels sections inside a part
            return best_word[1], best_word[2]
        return best_num[1], best_num[2]'''
s = s.replace(old2, new2, 1)

# 3. make the contents route authoritative when it succeeds
old3 = '''    anchored = contents_anchored(lines)
    if len(anchored) >= 3:
        return "contents", anchored'''
new3 = '''    anchored = contents_anchored(lines)
    if len(anchored) >= 3:
        return "contents", anchored'''
s = s.replace(old3, new3, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("patched")
