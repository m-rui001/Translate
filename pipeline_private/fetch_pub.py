"""Fetch the sixteen new public-domain German and English texts from Project Gutenberg.

The existing `pipeline_gutenberg` workspace is already full of twenty finished books, so
these get a separate tree (`work_pub/src`). Mixing them in would make the book count
ambiguous and risk an assembler picking up half-finished directories.

Every download is verified against the `Title:` and `Author:` lines in the file's own
Gutenberg header. Ids are transcribed from an API response, and a single wrong digit
yields a real, well-formed, entirely different book; without this check that failure
mode stays invisible until someone reads the translation and finds it is not Kafka.

German originals are chosen over English translations deliberately. Translating an
English Kafka into Chinese would be translating a translation, which loses the syntax
that makes the prose worth doing at all.
"""
from __future__ import annotations

import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline_private.books import PUBLIC          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "work_pub", "src")

UA = "Mozilla/5.0 (compatible; translate-pipeline/1.0)"
URLS = [
    "https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt",
    "https://www.gutenberg.org/files/{gid}/{gid}-0.txt",
    "https://www.gutenberg.org/files/{gid}/{gid}.txt",
]


def fetch(gid: int) -> bytes | None:
    for url in URLS:
        req = urllib.request.Request(url.format(gid=gid), headers={"User-Agent": UA})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    data = r.read()
                if len(data) > 5000:
                    return data
                break
            except Exception as e:                    # noqa: BLE001
                if attempt == 2:
                    print(f"      {type(e).__name__}: {str(e)[:70]}")
                time.sleep(2 + attempt * 2)
    return None


def header_of(raw: bytes) -> dict:
    out = {}
    text = raw.decode("utf-8", "replace")
    for line in text.split("\n")[:150]:
        m = re.match(r"^(Title|Author|Language|Translator):\s*(.*)$", line)
        if m:
            out.setdefault(m.group(1), m.group(2).strip())
    return out


def surname(name: str) -> str:
    """The family name of an author, whichever order the table spells it in.

    Gutenberg headers write `Kafka, Franz`, and the first version of this function
    assumed the book table did too, so it returned everything before the comma. The
    table actually uses ordinary order -- `Franz Kafka`, `Johann Wolfgang von Goethe` --
    which made the check compare a whole name against a header that splits it, and every
    new book failed with MISMATCH. The existing sixteen passed only because they were
    already cached and the check is skipped for those.

    Taking the last token handles both spellings: `Franz Kafka` -> `kafka`,
    `Kafka, Franz` -> `franz` is still wrong, so a comma is stripped first and then the
    last word is taken, which gives `kafka` either way. Particles survive as expected:
    `Guy de Maupassant` -> `maupassant`, `Hugo von Hofmannsthal` -> `hofmannsthal`.
    """
    n = name.split(",")[0].strip().lower()
    return n.split()[-1] if n else n


def main() -> int:
    os.makedirs(SRC, exist_ok=True)
    ok = skipped = failed = 0
    for b in PUBLIC:
        gid = b.get("gid")
        dst = os.path.join(SRC, b["key"] + ".txt")
        if os.path.exists(dst) and os.path.getsize(dst) > 5000:
            print(f"{b['key']:16s} cached")
            skipped += 1
            continue
        if not gid:
            print(f"{b['key']:16s} no gid, skipped")
            skipped += 1
            continue
        print(f"{b['key']:16s} gid={gid} fetching…", end=" ", flush=True)
        raw = fetch(gid)
        if raw is None:
            print("FAILED")
            failed += 1
            continue
        h = header_of(raw)
        title = h.get("Title", "")
        author = h.get("Author", "")
        want_sur = surname(b["author_src"])
        # guard: the file must name the right author, else the id is wrong
        if want_sur not in author.lower() and want_sur not in title.lower():
            print(f"MISMATCH (author={author!r} title={title[:40]!r})")
            failed += 1
            continue
        with open(dst, "wb") as f:
            f.write(raw)
        print(f"{len(raw):,}B  {title[:44]}")
        ok += 1
        time.sleep(1.0)
    print(f"\nfetched={ok} cached={skipped} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
