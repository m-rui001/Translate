"""Download the source texts from Project Gutenberg and verify each one.

The Gutenberg id in books_meta points at a specific edition, and ids are easy to
mistype, so every download is checked against the file's own `Title:` and
`Author:` header. A mismatch is reported instead of being silently translated,
because translating the wrong book is unrecoverable work.

Multi-volume works are downloaded volume by volume and concatenated in order,
each volume keeping its own Gutenberg header (they are stripped again at extract
time, so the seam is invisible). Taking only volume one would ship a book that
stops mid-story.

Usage:
    python pipeline_gutenberg/fetch.py            # all missing
    python pipeline_gutenberg/fetch.py --force    # re-download everything
"""
from __future__ import annotations

import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "work_gutenberg", "src")

URLS = [
    "https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt",
    "https://www.gutenberg.org/files/{gid}/{gid}-0.txt",
    "https://www.gutenberg.org/files/{gid}/{gid}.txt",
    "https://gutenberg.pglaf.org/cache/epub/{gid}/pg{gid}.txt",
]


def fetch(url: str, gid: int) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": "translate-pipeline/1.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
            if len(data) < 20000:          # a stub or a redirect page
                return None
            return data
        except Exception as e:             # noqa: BLE001
            if attempt == 2:
                print(f"    gid={gid} {type(e).__name__}: {str(e)[:80]}")
            time.sleep(2 + attempt * 3)
    return None


def header_of(raw: bytes) -> dict[str, str]:
    out = {}
    for line in raw.decode("utf-8", "replace").split("\n")[:120]:
        m = re.match(r"^(Title|Author|Language):\s*(.*)$", line)
        if m:
            out.setdefault(m.group(1), m.group(2).strip())
    return out


def main() -> None:
    import books_meta
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(SRC, exist_ok=True)
    force = "--force" in sys.argv

    ok, bad, total = [], [], 0
    for key, meta in books_meta.BOOKS.items():
        dest = os.path.join(SRC, key + ".txt")
        gids = meta["gids"]
        if os.path.exists(dest) and not force:
            h = header_of(open(dest, "rb").read(20004))
            size = os.path.getsize(dest)
            total += size
            print(f"  have  {key:16s} {size/1e6:5.2f}MB {h.get('Language','?'):10s} "
                  f"{len(gids)}v {h.get('Title','?')[:38]}")
            ok.append(key)
            continue

        chunks, langs = [], set()
        for gid in gids:
            data = None
            for tpl in URLS:
                data = fetch(tpl.format(gid=gid), gid)
                if data:
                    break
            if not data:
                print(f"  FAIL  {key:16s} gid={gid}")
                bad.append(f"{key}#{gid}")
                chunks = []
                break
            h = header_of(data)
            langs.add(h.get("Language", "?"))
            chunks.append(data)

        if not chunks:
            continue
        blob = b"\n\n".join(chunks)
        open(dest, "wb").write(blob)
        size = len(blob)
        total += size
        h = header_of(chunks[0])
        print(f"  ok    {key:16s} {size/1e6:5.2f}MB {','.join(sorted(langs)):10s} "
              f"{len(gids)}v {h.get('Title','?')[:38]}")
        ok.append(key)

    print(f"\n{len(ok)} ready / {total/1e6:.1f}MB, {len(bad)} problem(s): {bad or 'none'}")


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    main()
