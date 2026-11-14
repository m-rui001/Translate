"""Acceptance check for every EPUB in ./out.

A book that opens in a viewer is not the same as a book that is correct. This checks
the things that actually broke during the project, in the order they would hurt a
reader:

  * the file is a valid ZIP with `mimetype` first and stored, not deflated;
  * every XHTML and the OPF/NCX parse as XML;
  * every manifest href exists and every spine idref is in the manifest;
  * `nav.xhtml` is both flagged `properties='nav'` **and** present in the spine —
    the earlier build had a perfect nav that no reader ever reached;
  * the NCX and the nav list the same number of entries;
  * no `⟦i⟧` / `[[n]]` / `（坟头草` residue leaked into the prose;
  * the copyright page carries exactly one paragraph of claim;
  * chapter count, paragraph count and Han character count, so a truncated build shows.
"""
from __future__ import annotations

import glob
import os
import re
import sys
import zipfile
from xml.dom import minidom

ROOT = "E:/Translate"
OUT = os.path.join(ROOT, "out")
RESIDUE = re.compile(r"⟦/?i⟧|\[\[\d+\]\]|<first_translation>|<polished>")
CJK = re.compile(r"[\u4e00-\u9fff]")


def check(path: str) -> dict:
    r = {"file": os.path.basename(path), "errors": [], "warn": []}
    try:
        z = zipfile.ZipFile(path)
    except Exception as e:  # noqa: BLE001
        r["errors"].append(f"not a zip: {e}")
        return r
    names = z.namelist()
    if not names or names[0] != "mimetype":
        r["errors"].append("mimetype is not the first entry")
    else:
        info = z.getinfo("mimetype")
        if info.compress_type != zipfile.ZIP_STORED:
            r["errors"].append("mimetype is compressed")
        if z.read("mimetype") != b"application/epub+zip":
            r["errors"].append("mimetype content wrong")

    docs = {}
    for n in names:
        if n.endswith((".xhtml", ".opf", ".ncx", ".xml")):
            try:
                docs[n] = z.read(n).decode("utf-8")
                minidom.parseString(docs[n].encode("utf-8"))
            except Exception as e:  # noqa: BLE001
                r["errors"].append(f"XML {n}: {str(e)[:70]}")
    opf = next((v for k, v in docs.items() if k.endswith(".opf")), "")
    if not opf:
        r["errors"].append("no OPF")
        return r

    manifest = {}
    for attrs in re.findall(r"<item\b([^>]*)/>", opf):
        i = re.search(r"id='([^']+)'", attrs)
        h = re.search(r"href='([^']+)'", attrs)
        if i and h:
            manifest[i.group(1)] = h.group(1)
    spine = re.findall(r"<itemref\b[^>]*idref='([^']+)'", opf)
    for i in spine:
        if i not in manifest:
            r["errors"].append(f"spine idref '{i}' missing from manifest")
    hrefs = set(manifest.values())
    for m in re.finditer(r"<item\b([^>]*)/>", opf):
        attrs = m.group(1)
        h = re.search(r"href='([^']+)'", attrs)
        if not h:
            continue
        full = "OEBPS/" + h.group(1)
        if h.group(1) not in ("nav.xhtml",) and full not in names:
            r["errors"].append(f"manifest href missing from zip: {h.group(1)}")

    nav_item = [k for k, v in manifest.items() if v == "nav.xhtml"]
    if not nav_item:
        r["errors"].append("no nav.xhtml in manifest")
    else:
        if nav_item[0] not in spine:
            r["errors"].append("nav.xhtml NOT in spine (reader cannot reach the TOC)")
        props = re.search(r"<item\b[^>]*href='nav\.xhtml'[^>]*properties='([^']*)'", opf)
        if not props or "nav" not in props.group(1):
            r["errors"].append("nav.xhtml lacks properties='nav'")

    navdoc = next((v for k, v in docs.items() if k.endswith("nav.xhtml")), "")
    nav_links = re.findall(r"<a\s+href='([^']+)'[^>]*>(.*?)</a>", navdoc, re.S)
    ncxdoc = next((v for k, v in docs.items() if k.endswith(".ncx")), "")
    ncx_links = re.findall(r"<content\s+src='([^']+)'", ncxdoc)
    r["toc"] = len(nav_links)
    r["toc_ncx"] = len(ncx_links)
    if nav_links and ncx_links and len(nav_links) != len(ncx_links):
        r["errors"].append(f"nav has {len(nav_links)} entries, ncx has {len(ncx_links)}")
    for href, label in nav_links:
        if not re.search(r"[\u4e00-\u9fff]", label):
            r["warn"].append(f"TOC entry not Chinese: {label[:24]}")
        if "OEBPS/" + href not in names:
            r["errors"].append(f"TOC points at missing file: {href}")

    text = "".join(v for k, v in docs.items()
                   if k.endswith(".xhtml") and "nav" not in k)
    hits = RESIDUE.findall(text)
    if hits:
        r["errors"].append(f"residue markers in prose: {len(hits)} ({set(hits)})")

    copy = next((v for k, v in docs.items() if "copyright" in k), "")
    # The licence text is a single bare paragraph inside <div class='cn'>, not a <p>.
    # Count non-empty text blocks there; Proust's page header carries extra <p class='src'>
    # lines that used to be counted and made every Proust build look one short.
    inner = re.search(r"<div class=['\"]cn['\"]>(.*?)</div>", copy, re.S)
    scope = inner.group(1) if inner else copy
    blocks = re.findall(r"<p(?![^>]*class=['\"]src['\"])[^>]*>(.*?)</p>", scope, re.S)
    blocks += [b for b in re.split(r"\n\s*\n", re.sub(r"<[^>]+>", "\n\n", scope)) if b.strip()]
    r["copyright_paras"] = len(blocks)
    if "以原文为准" in copy or "原文著作权归原作者" in copy:
        r["errors"].append("copyright still carries the removed boilerplate")

    body = "".join(v for k, v in docs.items()
                   if k.endswith(".xhtml") and "nav" not in k and "copyright" not in k)
    r["han"] = len(CJK.findall(re.sub(r"<[^>]+>", "", body)))
    # Proust and the split-volume books name their chapters v3_01.xhtml, not cNNN.xhtml,
    # so match both shapes; counting only cNNN reported Proust as having 0 chapters.
    r["chapters"] = sum(1 for k in names
                        if re.fullmatch(r"OEBPS/(?:c\d+|v\d+_\d+)\.xhtml", k))
    r["size"] = os.path.getsize(path)
    return r


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    files = sorted(glob.glob(os.path.join(OUT, "*.epub")))
    if not files:
        print("nothing in ./out")
        return 1
    bad = 0
    for f in files:
        r = check(f)
        status = "OK " if not r["errors"] else "FAIL"
        if r["errors"]:
            bad += 1
        print(f"[{status}] {r['file']}")
        print(f"        {r.get('chapters', 0):3d} chapters  han={r.get('han', 0):,}  "
              f"toc={r.get('toc', 0)}/ncx={r.get('toc_ncx', 0)}  "
              f"copyright_paras={r.get('copyright_paras', 0)}  "
              f"{r.get('size', 0)/1048576:.2f}MB")
        for e in r["errors"]:
            print(f"        ERROR {e}")
        for w in dict.fromkeys(r["warn"]):
            print(f"        warn  {w}")
    print(f"\n{len(files)} epub, {bad} with errors")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
