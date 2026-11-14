"""Look up Project Gutenberg ids for the new catalogue, one query per author.

Ids are needed before anything can be fetched, and guessing them produces either the
wrong book or a 404 halfway through a run. gutendex is queried per author and the results
are filtered by language, because Gutenberg's English-language translations of a German
author are not the text we want -- translating an English Kafka into Chinese would be
translating a translation, which is exactly the defect the project exists to avoid.

The output is written to a JSON file rather than printed and re-typed, so the ids that
end up in the book table are the ones the API actually returned.
"""
import json
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

QUERIES = [
    ("kafka", "Kafka", "de"),
    ("rilke", "Rilke", "de"),
    ("woolf", "Woolf", "en"),
    ("hofmannsthal", "Hofmannsthal", "de"),
    ("celan", "Celan", "de"),
    ("bachmann", "Bachmann", "de"),
    ("buzzati", "Buzzati", "it"),
    # in-copyright authors: only to confirm Gutenberg has nothing (they should not)
    ("lispector", "Lispector", "pt"),
    ("calvino", "Calvino", "it"),
    ("rulfo", "Rulfo", "es"),
    ("beckett", "Beckett", "fr"),
    ("duras", "Duras", "fr"),
    ("hrabal", "Hrabal", "cs"),
    ("sebald", "Sebald", "de"),
]


def get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as f:
        return json.loads(f.read().decode("utf-8"))


found = {}
for key, name, lang in QUERIES:
    url = ("https://gutendex.com/books?search=" + urllib.parse.quote(name)
           + "&languages=" + lang)
    print(f"\n=== {key} ({name}, {lang}) ===", flush=True)
    try:
        d = get(url)
    except Exception as e:
        print("  ERR", e, flush=True)
        continue
    rows = []
    for r in d.get("results", [])[:15]:
        a = r["authors"][0] if r["authors"] else {}
        rows.append(dict(id=r["id"], title=r["title"],
                         author=a.get("name"), died=a.get("death_year"),
                         langs=r["languages"],
                         downloads=r.get("download_count", 0)))
    found[key] = rows
    if not rows:
        print("  (nothing)", flush=True)
    for r in rows:
        print(f"  {r['id']:6d} {r['title'][:46]:48s} {str(r['author'])[:24]:26s} "
              f"{r['langs']} d={r['died']} dl={r['downloads']}", flush=True)
    time.sleep(0.6)

json.dump(found, open("pipeline_private/_gids.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nwrote pipeline_private/_gids.json")
