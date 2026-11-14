"""Fetch the missing Proust volumes (I, II, V) as plain French text.

The book currently starts at volume three, which is visible to any reader as a
hole: `pipeline_proust/extract_proust.py` was written for "the volumes Zhou Kexi
did not finish", so I, II and V were never downloaded. This pulls them from
Project Gutenberg (all French; English translations are refused) and writes the
same `src/vN.txt` shape the rest of the pipeline expects.

Gutenberg ships *À l'ombre des jeunes filles en fleurs* split across three
ebooks, so volume two is concatenated in part order.
"""
from __future__ import annotations

import io
import os
import re
import sys
import time
import urllib.request

SRC = "E:/Translate/work_proust/src"

VOL = {
    "v1": [2650],                    # Du côté de chez Swann
    "v2": [2998, 2999, 3000],        # À l'ombre des jeunes filles en fleurs
    "v5": [60720],                   # La Prisonnière (Sodome et Gomorrhe III)
}

WANT = {"v1": "Du côté de chez Swann",
        "v2": "A l'ombre des jeunes filles",
        "v5": "La Prisonnière"}

UA = {"User-Agent": "Mozilla/5.0 (compatible; personal translation project)"}


def get(gid: int) -> str:
    url = f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
            return raw.decode("utf-8")
        except Exception as e:                                   # noqa: BLE001
            print(f"  {gid} attempt {attempt + 1}: {e}")
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"cannot fetch {gid}")


def strip_licence(text: str) -> str:
    """Drop the Gutenberg header and footer, keep only the novel."""
    start = 0
    m = re.search(r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", text, re.I)
    if m:
        start = m.end()
    end = len(text)
    m = re.search(r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", text, re.I)
    if m:
        end = m.start()
    return text[start:end].strip()


def meta(text: str) -> dict:
    head = "\n".join(text.split("\n")[:120])
    out = {}
    for key in ("Title", "Author", "Language"):
        m = re.search(rf"^{key}:\s*(.+)$", head, re.M)
        if m:
            out[key] = m.group(1).strip()
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(SRC, exist_ok=True)
    for vol, gids in VOL.items():
        parts, metas = [], []
        for gid in gids:
            print(f"{vol}: fetching {gid} …")
            raw = get(gid)
            m = meta(raw)
            metas.append(m)
            if m.get("Language", "").lower() != "french":
                raise SystemExit(f"{gid}: language is {m.get('Language')!r}, not French "
                                 f"— refusing to translate a translation")
            if WANT[vol].lower()[:18] not in m.get("Title", "").lower():
                raise SystemExit(f"{gid}: title {m.get('Title')!r} does not look like "
                                 f"{WANT[vol]!r} — refusing")
            body = strip_licence(raw)
            if len(body) < 20_000:
                raise SystemExit(f"{gid}: only {len(body)} chars after stripping licence")
            parts.append(body)
            print(f"   {m.get('Title')} / {len(body):,} chars")

        text = "\n\n\n".join(parts)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        out = os.path.join(SRC, vol + ".txt")
        io.open(out, "w", encoding="utf-8").write(text)
        print(f"{vol}: wrote {out} — {len(text):,} chars, "
              f"title={metas[0].get('Title')!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
