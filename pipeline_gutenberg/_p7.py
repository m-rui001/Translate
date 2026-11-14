import io

p = "E:/Translate/pipeline_gutenberg/structure.py"
s = io.open(p, encoding="utf-8").read()

start = s.index("def strip_licence(")
end = s.index("\n\ndef _is_ordinal")

new = '''def strip_licence(text: str) -> str:
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
        text = text[:e.start()] + "\\n\\n" + text[nxt.end():]
    return text'''

io.open(p, "w", encoding="utf-8").write(s[:start] + new + s[end:])
print("patched strip_licence")
