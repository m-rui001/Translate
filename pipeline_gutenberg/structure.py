"""Separate the boilerplate and find chapter headings in a Gutenberg text.

Written as a module rather than as one regex because the twenty source files in
this project mark their chapters five different ways:

  * `Effi Briest`      ---  "Erstes Kapitel", "Sechsunddreißigstes Kapitel", ...
  * `La Regenta`       ---  "--I--", "--II--" between blank lines
  * `Der Nachsommer`   ---  a bare chapter *title* ("Die Häuslichkeit") that also
                           appears in the book's own "Inhalt:" list, and no number
                           anywhere at all
  * `Ayala's Angel`    ---  "CHAPTER I.", roman, spelled out
  * `Bunte Steine`     ---  a bare title ("Granit.") with no contents list at all

A pattern tuned to one of those turns the other four into single-chapter books,
which is how the first extraction run produced an "Effi Briest" of 585,997
characters in one chunk.

Three rules keep detection honest, each learned from a concrete failure:

  * German ordinals are compositional -- "Sechsunddreißigstes" is six-and-thirty
    -- so they cannot be enumerated. The ordinal test is a *suffix* test instead;
    enumerating them silently truncated every book longer than twenty chapters.
  * a heading must *start* with a heading word or be a bare number. Matching the
    word anywhere promoted prose like ``In Book Second, Chapter III`` into a
    title, deleting the sentence.
  * a heading may not end in sentence punctuation, and a repeated title must be
    title-cased. Without that, dialogue and scene separators (``* * *``,
    ``[Ilustración]``, ``»Gut, gut.«``) outscored the real chapters, because they
    repeat more often than chapter heads do.

When no shape recurs at least three times, the book is reported as unsplittable
instead of being handed back as one huge chapter.
"""
from __future__ import annotations

import re

START = re.compile(r"^\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*$", re.M)
END = re.compile(r"^\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG.*$", re.M)

ROMAN = r"(?=[IVXLC])[IVXLC]{1,8}"
ARABIC = r"\d{1,3}"
NUMONLY = re.compile(r"^(?:%s|%s)\.?$" % (ROMAN, ARABIC))

# `--I--` (La Regenta), `-I-` (Los pazos de Ulloa), `--12--` (Fortunata).
# Both dash widths occur in these sources, so the run is one *or* two dashes.
DASHED = re.compile(r"^-{1,2}\s*(?P<body>[A-Za-z0-9IVXLC][A-Za-z0-9IVX .'\u2019\-]{0,40}?)\s*-{1,2}$")

HEADWORD = (r"(?:Kapitel|Chapter|Capitulo|Capítulo|Capitolo|Hoofdstuk|Kapitlet|"
            r"Libro|Parte|Buch|Book|Tomo|Volume|Vorrede|Einleitung|"
            r"Prologo|Prólogo|Introduction)")
WORD_FIRST = re.compile(r"^%s\b" % HEADWORD, re.I)

# German/Swedish/Danish ordinals all end this way: "erste/erstes/ersten",
# "tredje", "fjerde", "Første". A token with this suffix before "Kapitel" is an
# ordinal, which is what makes 36 chapters detectable without a word list.
ORD_SUFFIX = re.compile(
    r"(?:te|ter|tes|ten|tem|ste|ster|stes|sten|stem|nde|ndes|nden|tti?|eima|"
    r"first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|"
    r"eleventh|twelfth)$", re.I)
# Romance ordinals are a closed set and short enough to list
ROM_ORD = re.compile(
    r"^(?:primera|primero|segunda|segundo|tercera|tercero|cuarta|cuarto|"
    r"quinta|quinto|sexta|sexto|séptima|séptimo|septima|septimo|octava|octavo|"
    r"novena|noveno|décima|décimo|decima|decimo|primeira|primeiro|terceira|"
    r"terceiro|quarta|quarto|quinta|quinto|sexta|sexto|sétima|sétimo|setima|"
    r"setimo|oitava|oitavo|nona|nono|prima|secondo|terza|terzo)\b", re.I)

SENTENCE_END = re.compile(r"[.?!…]\s*$")
# a title is title-cased: every word starts with a capital or a digit, and none
# of the junk separators appear
# A title line excludes markdown-ish marks and quotation. A trailing colon is also
# excluded: in a play, a speech prefix is a caps name followed by a colon (`JEDERMANN:`),
# which satisfies every other title test and, because it repeats hundreds of times, wins
# `repeat_titles` outright -- it split Hofmannsthal's one-act play into 196 "chapters".
# No chapter heading ends in a colon; a speaker label always does.
TITLE_OK = re.compile(r"^(?!.*(?:\*|\[|\]|»|«|\"|—))(?![^:]*:$).*$")
NONCAP_START = re.compile(r"[a-zà-öø-ÿ]")


def strip_licence(text: str) -> str:
    """Remove the Gutenberg wrapper from *every* volume in the file.

    Two separate jobs, and both matter:

      * the front matter before the first START marker is licence text, not the
        novel -- leaving it in makes "The Project Gutenberg eBook of Effi Briest"
        the book's first paragraph;
      * multi-volume works are concatenated at fetch time, so the file holds
        several START/END pairs. Stripping only the outermost pair leaves the
        middle volumes' licences inside the last chapter, where they get
        translated as prose.

    So each pair is cut out in turn, and the text before the first START is
    dropped as well. Everything between markers is kept verbatim.
    """
    first = START.search(text)
    if first:
        text = text[first.end():]
    while True:
        e = END.search(text)
        if not e:
            break
        nxt = START.search(text, e.end())
        if not nxt:
            text = text[:e.start()]
            break
        text = text[:e.start()] + "\n\n" + text[nxt.end():]
    return text

def _is_ordinal(tok: str) -> bool:
    t = tok.strip(".,")
    if not t:
        return False
    if NUMONLY.match(t) or ROM_ORD.match(t):
        return True
    return bool(ORD_SUFFIX.search(t)) and len(t) > 3


def _shape(line: str) -> str:
    """Classify a candidate heading line, or '' if it is not one."""
    s = line.strip()
    if not s or len(s) > 70:
        return ""
    m = DASHED.match(s)
    body = (m.group("body") if m else s).strip()

    if NUMONLY.match(body):
        return "num"

    words = body.split()
    if not words:
        return ""
    # "Kapitel XII", "CHAPTER I."
    if WORD_FIRST.match(body):
        if SENTENCE_END.search(body) and len(words) > 5:
            return ""
        return "word"
    # "Erstes Kapitel", "Sechsunddreißigstes Kapitel.", "Første Kapitel."
    if len(words) >= 2 and _is_ordinal(words[0]) and re.match(
            r"^(?:%s)" % HEADWORD, body[len(words[0]):].strip(), re.I):
        return "word"
    # a two-word ordinal heading with no noun: "Erstes Buch"
    if len(words) == 2 and _is_ordinal(words[0]) and _is_ordinal(words[1]):
        return "word"
    return ""


def _standalone(lines: list[str], i: int) -> bool:
    """True when line `i` is a heading on its own, not a stray matching line.

    Two shapes have to be accepted, and the second one is easy to lose:

        Book the First--Recalled to Life      <- heading, blank line follows
        \n
        CHAPTER I.                            <- heading, title on the next line
        The Period                            <- no blank line between them
        \n
    Dickens sets a chapter number and its title on consecutive lines with no blank
    between, so requiring a blank after the heading rejected all 45 `CHAPTER` lines
    in *A Tale of Two Cities*. The contents-anchored route then found zero body
    matches for a book whose contents list parses perfectly, and the extractor fell
    back to six `Book the ...` part headings -- 47 chapters became 6.

    The test for the second shape is deliberately narrow: the next line must be short
    enough to be a title and the line after it must be blank, so ordinary prose that
    happens to start with `Chapter` does not become a heading.
    """
    if i > 0 and lines[i - 1].strip():
        return False
    nxt = i + 1
    if nxt >= len(lines) or not lines[nxt].strip():
        return True
    # a two-line heading: short title line, then a blank
    t = lines[nxt].strip()
    if len(t) <= 60 and len(t.split()) <= 8:
        after = nxt + 1
        if after >= len(lines) or not lines[after].strip():
            return True
    return False


def _num_key(s: str) -> str:
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

    def _restarts(idx: list[int]) -> bool:
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

    num_levels: list[tuple[float, str, list[int]]] = []
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


def _title_like(s: str) -> bool:
    """A chapter title, as opposed to dialogue or a scene break."""
    if not s or len(s) > 60 or len(s.split()) > 8:
        return False
    if not TITLE_OK.match(s):
        return False
    if SENTENCE_END.search(s) and not s.endswith("."):
        return False
    words = [w for w in s.split() if w]
    if not words:
        return False
    # every word must begin with an uppercase letter or a digit
    return not any(NONCAP_START.match(w[0]) for w in words)


def repeat_titles(lines: list[str], min_count: int = 3) -> list[int]:
    """Chapters found by a title printed twice: once listed, once used.

    `Der Nachsommer`, `Bunte Steine` and `Immensee` have no numbering visible in
    the text body: their parts are headed by plain titles, and the same strings
    are listed once up front. So every chapter title appears at least twice.
    Counting standalone occurrences and keeping each occurrence after the first
    reconstructs the printed structure without inventing numbering.

    Candidates are restricted to title-cased lines, because dialogue and scene
    separators repeat far more often than chapter heads and would otherwise win.
    """
    where: dict[str, list[int]] = {}
    for i, l in enumerate(lines):
        s = l.strip()
        if not _title_like(s) or NUMONLY.match(s) or _shape(s):
            continue
        if not _standalone(lines, i):
            continue
        where.setdefault(s, []).append(i)

    starts: list[int] = []
    for title, idxs in where.items():
        if len(idxs) < 2:
            continue
        starts.extend(idxs[1:])
    starts.sort()
    if len(starts) < min_count:
        return []
    # a contents list repeats each title back-to-back; real openings are far apart
    out = [starts[0]]
    for i in starts[1:]:
        if i - out[-1] > 8:
            out.append(i)
    return out


def toc_titles(lines: list[str], min_count: int = 3) -> list[int]:
    """Chapters by an explicit contents block whose entries later reappear.

    `Der Nachsommer` prints "Inhalt:" then its seventeen part titles; each one
    recurs later as the heading of its part. The contents block is the index.
    """
    start = -1
    for i, l in enumerate(lines[:400]):
        if re.match(r"^\s*(?:Inhalt|Contents|Índice|Indice|ÍNDICE|Sumário|"
                    r"Îndice|Sommario)\s*:?\s*$", l, re.I):
            start = i
            break
    if start < 0:
        return []

    entries: list[str] = []
    for l in lines[start + 1:start + 80]:
        s = l.strip()
        if not s:
            if entries:
                break
            continue
        if not _title_like(s) or len(s.split()) > 6:
            break
        entries.append(s)
    if len(entries) < min_count:
        return []

    entries_set = set(entries)
    idx: list[int] = []
    for i, l in enumerate(lines):
        if i <= start:
            continue
        if l.strip() in entries_set and _standalone(lines, i):
            idx.append(i)
    # the block itself may re-list them; keep only the late occurrences
    if len(idx) > len(entries):
        idx = idx[len(idx) - len(entries):]
    return idx if len(idx) >= min_count else []


def short_title_lines(lines: list[str], min_count: int = 3) -> list[int]:
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
        # A heading is flush with the left margin. Every false positive of this route
        # was an indented title-page line -- `Torless` prints the author name
        # "ROBERT MUSIL" centred on the title page, and the all-caps route already
        # excludes indented lines for the same reason, so this route must too. Without
        # it, the author line became a chapter start and the rest of the book (229k
        # characters) collapsed into a single following chapter.
        if l[:1].isspace():
            continue
        if not _standalone(lines, i):
            continue
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if nxt.startswith(("\u00bb", "\u00ab", '"', "\u2014")):
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


def contents_anchored(lines: list[str], min_count: int = 3) -> list[int]:
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
        if _re.match(r"^\s*(?:Inhalt|Contents|\u00cdndice|Indice|\u00cdNDICE|"
                     r"Sum\u00e1rio|\u00ceandice|Sommario)\s*[.:]?\s*$", l, _re.I):
            start = i
            break
    if start < 0:
        return []

    heads: list[str] = []
    end_of_contents = start
    for j, l in enumerate(lines[start + 1:start + 80], start + 1):
        t = l.strip()
        # entries are separated by blank lines, so gaps are not the end of the
        # block; only an unparsable line is
        if not t:
            continue
        # a contents list may open with a column header ("Seite", "Page")
        if re.match(r"^(?:Seite|Page|P\u00e1gina|Pagina|Sida)\s*$", t, re.I):
            continue
        # "Granit                        1" -> leading words
        # page numbers appear as arabic ("38") or roman ("V") depending on the
        # volume's front matter; both must parse or the list stops at entry one
        m = (_re.match(r"^(.+?)\s{2,}(?:\d{1,4}|[IVXLC]{1,7})\s*$", t)
             or _re.match(r"^(.+?)\s+(?:\d{1,4}|[IVXLC]{1,7})\s*$", t))
        if not m:
            # Dickens prints a contents list with no page numbers at all:
            #
            #     CHAPTER I      The Period
            #     CHAPTER II     The Mail
            #
            # The discriminator is still the one described above -- the contents entry
            # carries its title on the same line, separated by a run of spaces, while a
            # body opening leaves the title for the next line. So a heading marker plus
            # a number plus a gap plus a title is an entry; a bare "CHAPTER I." is not.
            m = _re.match(
                r"^(?:%s)\s+(?:PREMIER|PREMI\u00c8RE|[IVXLCDM]+|\d{1,3})\b"
                r"\s{2,}\S.*$" % "CHAPITRE|Chapitre|CHAPTER|Chapter|"
                                  "CAPITULO|Capitulo|CAPITOL|Capitolo|"
                                  "Kapitel|Buch|Book|Tomo|Volume|Parte|Libro",
                t, _re.I)
        if not m:
            # "Book the First--Recalled to Life": the part name and its title are
            # joined by a dash pair rather than spaced, so the whole line is the head
            # and the body heading repeats it verbatim.
            m = _re.match(
                r"^(?:%s)\s+\S.*?--\S.*$" % "CHAPITRE|Chapitre|CHAPTER|Chapter|"
                                            "CAPITULO|Capitulo|Kapitel|Buch|Book|"
                                            "Tomo|Volume|Parte|Libro",
                t, _re.I) if "--" in t else None
        if not m:
            break
        # the first pattern captures the head as group 1; the two Dickens patterns
        # are non-capturing, so the head is the whole match
        heads.append(m.group(1).strip() if m.lastindex else m.group(0).strip())
        end_of_contents = j
    if len(heads) < min_count:
        return []

    idx: list[int] = []
    # Search only *after* the contents block. Starting at `start` made every match
    # land on the contents entry itself: "Book the First--Recalled to Life" is
    # standalone at line 13 and again at line 73, and the first one found was the
    # contents line, so a 47-chapter novel came back as three contents entries.
    #
    # A contents entry carries its title on the same line but the body heading does
    # not -- "CHAPTER I      The Period" becomes just "CHAPTER I." in the body. So
    # the head is trimmed at the first run of two or more spaces, and the untrimmed
    # form is tried too because "Book the First--Recalled to Life" repeats verbatim.
    #
    # The cursor advances past every match, because a book that numbers its parts
    # independently repeats its chapter labels. *A Tale of Two Cities* has three
    # books each running CHAPTER I..XI/XXIII/XVI, so the bare form "CHAPTER I" maps
    # all three contents entries onto the first body heading and 47 chapters collapse
    # to 26. Since heads are listed in document order and so are the body headings,
    # a monotonic cursor pairs them correctly; a head that fails to match simply
    # leaves the cursor where it was.
    cursor = end_of_contents + 1
    for hi, h in enumerate(heads):
        marker = _re.split(r"\s{2,}", h, 1)[0]
        forms = [h] if marker == h else [marker, h]
        for form in forms:
            pat = _re.compile(r"^" + _re.escape(form) + r"\b", _re.I)
            for i in range(cursor, len(lines)):
                t = lines[i].strip()
                if not t.startswith(form[:6]):
                    continue
                if not pat.match(t):
                    continue
                if not _standalone(lines, i):
                    continue
                # heading is the bare word, possibly with a full stop -- not a sentence
                if len(t) <= len(form) + 2:
                    idx.append(i)
                    cursor = i + 1
                    break
            else:
                continue
            break
    return idx if len(idx) >= min_count else []


def allcaps_titles(lines: list[str], min_count: int = 3) -> list[int]:
    """Chapters by ALL-CAPS title lines, read straight off the page.

    `Immensee` is the one book the spacing route misses: its ten chapter titles
    are printed all-caps with no numbering at all. It also lists them first, so
    the same ten strings appear twice -- and the first and last chapters share
    the title "DER ALTE", which defeats both "every occurrence after the first"
    (drops the final chapter) and "one entry per repeated string" (merges the
    first and last).

    So this route does not count repeats at all. It takes the all-caps standalone
    lines in document order; the contents run and the chapter openings are the
    same strings in the same order, and the closing chapter's repeated title is
    simply the tenth entry rather than a duplicate to be removed.
    """
    caps = [i for i, l in enumerate(lines)
            if l.strip() and len(l.strip()) > 2
            and l.strip() == l.strip().upper()
            and l.strip("_*=-— ") != ""
            and len(l.strip().split()) <= 8
            # A heading is flush with the left margin. Every false positive on this
            # shelf was indented: `Dubliners` sets three newspaper clippings inside
            # "A Painful Case" at five spaces (`     A PAINFUL CASE`,
            # `     ROYAL EXCHANGE WARD`), `Buddenbrooks` runs the author line in from
            # the edge, and `Tess` indents its epigraph. No real chapter heading does.
            and not l[:1].isspace()
            and _standalone(lines, i)]
    if len(caps) < min_count:
        return []
    # Drop a candidate that merely continues the one before it. "LES ROIS" and
    # "AU BOIS" are a single story title wrapped over two lines, and the printed
    # contents wraps it the same way, so both looked like headings -- which split
    # Maupassant's story in two and put `AU BOIS` in the table of contents as if it
    # were a story of its own. A second candidate within four lines of the first is
    # a continuation, not a new chapter.
    caps = [i for n, i in enumerate(caps)
            if n == 0 or i - caps[n - 1] > 4]
    titles = [lines[i].strip() for i in caps]
    # This route is trusted on *variety*, not on repetition. An earlier check bailed when
    # any title recurred (`len(set) < len - 1`), which contradicted the design above and
    # cost a whole book: `Le Horla` lists thirteen story titles, then repeats five of
    # them in a closing contents run, plus four all-caps noise lines (the author name,
    # a year, the wrapped tail of "LES ROIS AU BOIS", an illustration caption). Thirty-four
    # candidates with six duplicates tripped the bail and the book fell through to
    # `repeat`, which split it on dialogue lines -- seven "chapters" titled `--Oui.`.
    #
    # What distinguishes a real chapter run from a stray all-caps line is that the
    # titles are mostly distinct. A page of noise has no such variety.
    uniq = len(set(titles))
    if uniq < min_count:
        return []
    if uniq * 2 < len(titles):
        return []
    return caps


def chapter_starts(lines: list[str]) -> tuple[str, list[int]]:
    """Best available chapter delineation for this file.

    Every detector is normalised here: ascending, de-duplicated, and with an index of 0
    dropped. `contents_anchored` returns hits in *scan order*, and scanning a table of
    contents then the body can revisit a line number ("Monday or Tuesday" was observed
    returning `[69, 144, 64, ...]`). An out-of-order pair makes `build_blocks` slice an
    empty `lines[at:end]`, and `body[0]` then raises IndexError on a real book. Sorting
    at the single exit point means no detector can reintroduce the bug.
    """
    kind, idx = _chapter_starts_raw(lines)
    seen = sorted({i for i in idx if i > 0})
    return kind, seen


def chapter_alone(lines: list[str], min_count: int = 3) -> list[int]:
    """Chapters marked by a bare chapter word with no title on the same line.

    Two French books defeated every other route for the same reason: their table of
    contents and their body use the *same* word, so a detector that keys on the word
    alone fires on the contents and then finds the body headings indistinguishable.

        CHAPITRE II L'ANTICHAMBRE DE M. DE TRÉVILLE      <- contents (indented, titled)
        CHAPITRE II.                                     <- body (flush, bare)
        Chapitre I Monsieur Myriel                       <- contents (titled)
        Chapitre III                                     <- body (bare)

    The discriminator is what follows the number. A contents entry carries the chapter's
    title on the same line; a body opening does not -- the title sits on the next line, or
    is absent altogether. So this route takes only the bare form, which by construction
    cannot match a contents line. `PREMIER` is included because Dumas numbers his first
    chapter with the word rather than a roman numeral.
    """
    pat = re.compile(
        r"^\s*(?:CHAPITRE|Chapitre|CHAPTER|Chapter|CAPITULO|Capitulo)\s+"
        r"(?:PREMIER|PREMIÈRE|Premier|Première|[IVXLCDM]+|[0-9]{1,3})"
        r"\.?\s*$", re.I)
    hits = [i for i, l in enumerate(lines) if pat.match(l)]
    return hits if len(hits) >= min_count else []


def _chapter_starts_raw(lines: list[str]) -> tuple[str, list[int]]:
    anchored = contents_anchored(lines)
    if len(anchored) >= 3:
        return "contents", anchored
    kind, idx = find_headings(lines)
    if len(idx) >= 3:
        return kind, idx
    for name, fn in (("bare", chapter_alone), ("toc", toc_titles),
                     ("allcaps", allcaps_titles), ("repeat", repeat_titles),
                     ("titles", short_title_lines)):
        got = fn(lines)
        if len(got) >= 3:
            return name, got
    return "", []


def diagnose(lines: list[str]) -> str:
    kind, idx = chapter_starts(lines)
    if not idx:
        return "NO STRUCTURE"
    spans = [idx[i + 1] - idx[i] for i in range(len(idx) - 1)]
    med = sorted(spans)[len(spans) // 2] if spans else 0
    return (f"{kind:6s} n={len(idx):3d} gap={med:5d} "
            f"first={lines[idx[0]].strip()[:32]!r} last={lines[idx[-1]].strip()[:32]!r}")


if __name__ == "__main__":
    import os
    import sys
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.stdout.reconfigure(encoding="utf-8")
    for name in sorted(os.listdir(os.path.join(root, "work_gutenberg", "src"))):
        if not name.endswith(".txt"):
            continue
        raw = open(os.path.join(root, "work_gutenberg", "src", name),
                   encoding="utf-8", errors="replace").read()
        lines = strip_licence(raw).split("\n")
        print(f"{name[:-4]:16s} {diagnose(lines)}")
