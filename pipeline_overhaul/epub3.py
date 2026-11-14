"""Upgrade an assembled EPUB 2 to EPUB 3, deriving the nav document from the NCX.

EPUB 2 readers find the table of contents through `toc.ncx` alone. EPUB 3 requires
an XHTML navigation document, and several reading systems (Apple Books, recent
Thorium) ignore an NCX-only book's contents entirely, which is why four of these
titles opened with no table of contents at all.

The upgrade is deliberately conservative: the NCX stays in place for old readers,
and only the nav document, the package version, and the required dcterms:modified
are added. Chapter files are not touched.

Re-running is safe and idempotent: an existing nav.xhtml is replaced, so a broken
table of contents can be regenerated after fixing this script.
"""
from __future__ import annotations

import html
import re
import zipfile

NAV_NS = ("xmlns='http://www.w3.org/1999/xhtml' "
          "xmlns:epub='http://www.idpf.org/2007/ops'")


def _ncx_entries(ncx: str) -> list[tuple[int, str, str]]:
    """(depth, label, href) for each navPoint, in document order."""
    out: list[tuple[int, str, str]] = []
    depth = 0
    for m in re.finditer(r"<navPoint\b[^>]*>|</navPoint>"
                         r"|<navLabel><text>(.*?)</text></navLabel>"
                         r"<content src='([^']*)'/>", ncx, re.S):
        tok = m.group(0)
        if tok.startswith("<navPoint"):
            depth += 1
        elif tok.startswith("</navPoint"):
            depth = max(0, depth - 1)
        else:
            out.append((max(1, depth), html.unescape(m.group(1)), m.group(2)))
    return out


def _tree(entries):
    """Fold (depth, label, href) rows into a real tree."""
    roots = []
    # parents[i] is the child list that a node at depth i appends into
    parents = [roots]
    for d, label, href in entries:
        while len(parents) > d:
            parents.pop()
        while len(parents) < d:
            parents.append(parents[-1][-1]["kids"] if parents[-1] else roots)
        node = {"label": label, "href": href, "kids": []}
        parents[-1].append(node)
        parents.append(node["kids"])
    return roots


def _ol(nodes, depth):
    pad = "  " * depth
    out = [pad + "<ol>"]
    for nd in nodes:
        out.append(pad + "  <li><a href='" + nd["href"] + "'>" +
                   html.escape(nd["label"]) + "</a>")
        if nd["kids"]:
            out.append(_ol(nd["kids"], depth + 2))
        out.append(pad + "  </li>")
    out.append(pad + "</ol>")
    return "\n".join(out)


def _nav_xhtml(entries) -> str:
    """Render NCX entries as a well-formed EPUB 3 nav document.

    The entries are folded into a real tree and serialised by recursion. Earlier
    versions stitched tags together in a flat loop and emitted an unbalanced
    <ol> whenever a branch ended; a malformed nav is worse than no nav at all.
    """
    inner = ("<nav epub:type='toc' id='toc'>\n<h1>目录</h1>\n"
             + _ol(_tree(entries), 1) + "\n</nav>")
    return ("<?xml version='1.0' encoding='utf-8'?>\n<!DOCTYPE html>\n"
            "<html " + NAV_NS + " xml:lang='zh-CN'>\n"
            "<head><meta charset='utf-8'/><title>目录</title>"
            "<style>nav ol{list-style:none;padding-left:1.1em;margin:0}"
            "nav li{margin:.35em 0}</style></head><body>\n"
            + inner + "\n</body></html>")


def upgrade(path: str) -> str:
    """Rewrite `path` as EPUB 3. Returns a short status string."""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if "mimetype" not in names:
            return "not an epub"
        opfs = [n for n in names if n.endswith(".opf")]
        ncxs = [n for n in names if n.endswith("toc.ncx")]
        if not opfs or not ncxs:
            return "no ncx"
        opf_name, ncx_name = opfs[0], ncxs[0]
        opf = z.read(opf_name).decode("utf-8")
        ncx = z.read(ncx_name).decode("utf-8")
        payload = {n: z.read(n) for n in names}

    entries = _ncx_entries(ncx)
    if not entries:
        return "empty ncx"

    base = ncx_name.rsplit("/", 1)[0] + "/" if "/" in ncx_name else ""
    payload[base + "nav.xhtml"] = _nav_xhtml(entries).encode("utf-8")

    was3 = "version='3.0'" in opf or 'version="3.0"' in opf
    opf = re.sub(r"version=['\"]2\.0['\"]", "version='3.0'", opf)
    if "id='nav'" not in opf:
        opf = opf.replace(
            "<manifest>",
            "<manifest>\n<item id='nav' href='nav.xhtml' "
            "media-type='application/xhtml+xml' properties='nav'/>", 1)
    if "dcterms:modified" not in opf:
        opf = opf.replace(
            "</metadata>",
            "<meta property='dcterms:modified'>2026-10-25T12:00:00Z</meta>"
            "</metadata>", 1)
    # The nav document is only reachable if it is also a spine item. Without this, the
    # book has a correct table of contents that no reading system will ever show.
    if "idref='nav'" not in opf:
        m = re.search(r"(<spine\b[^>]*>)", opf)
        if m:
            opf = opf[:m.end()] + "\n<itemref idref='nav'/>" + opf[m.end():]
        else:
            opf = opf.replace("</package>",
                              "<spine><itemref idref='nav'/></spine></package>", 1)
    payload[opf_name] = opf.encode("utf-8")

    with zipfile.ZipFile(path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip",
                   zipfile.ZIP_STORED)
        for n, data in payload.items():
            if n != "mimetype":
                z.writestr(n, data)
    return (f"nav regenerated, {len(entries)} entries" if was3
            else f"upgraded to epub3, {len(entries)} entries")


if __name__ == "__main__":
    import glob
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    for p in sys.argv[1:] or sorted(glob.glob("E:/Translate/*（坟头草译*.epub")):
        print(f"{upgrade(p):45s} {p}")
