
"""Find proper-noun variants in a translated book by looking where names actually sit.

Chinese does not mark names, so a character-level scan of the whole text finds
fragments of sentences instead of people. Names do have positions, though: after 堂/
小/老, before 先生/太太/小姐/博士/神甫, and before a speech verb (说/道/问/答/喊).
Harvesting only those positions cuts the candidate set by two orders of magnitude and
leaves the pairs a reader would actually notice.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
import zipfile
from collections import Counter, defaultdict
from html import unescape

CJK = r"\u4e00-\u9fff"
TITLE = r"(?:堂|小|老|大)"
ROLE = r"(?:先生|太太|小姐|夫人|博士|神甫|教授|伯爵|公爵|侯爵|骑士|医生|律师|法官|上尉|中尉|少校|将军|主教|教士|修女|老板|掌柜|大娘|大妈|姑娘|少爷|老爷)"
SPEECH = r"(?:说|道|问|答|喊|叫|嚷|笑|叹|低声|高声|自语|插嘴|回答|追问|嘟囔)"
NAME_RE = re.compile(rf"(?:{TITLE})?([{CJK}]{{2,6}}?)(?={ROLE}|{SPEECH}|[，。！？：；、”])")
DOT_RE = re.compile(rf"[{CJK}]{{2,8}}(?:·[{CJK}]{{1,10}})+")


def book_text(path: str) -> str:
    z = zipfile.ZipFile(path)
    out = []
    for n in z.namelist():
        if n.endswith(".xhtml") and not any(k in n for k in ("nav", "title", "copyright")):
            s = z.read(n).decode("utf-8")
            for m in re.finditer(r"<p[^>]*>(.*?)</p>", s, re.S):
                out.append(unescape(re.sub(r"<[^>]+>", "", m.group(1))))
    return "\n".join(out)


def collect(text: str) -> Counter:
    c = Counter()
    for m in DOT_RE.finditer(text):
        c[m.group(0)] += 1
    for m in NAME_RE.finditer(text):
        w = m.group(1)
        if len(w) >= 3:
            c[w] += 1
    return c


def lev(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def lcs(a: str, b: str) -> int:
    prev = [0] * (len(b) + 1)
    for ca in a:
        cur = [0]
        for j, cb in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if ca == cb else max(prev[j], cur[j - 1]))
        prev = cur
    return prev[-1]


def pairs(cnt: Counter, min_major: int = 4) -> list[dict]:
    """Variant pairs, compared only inside narrow buckets.

    Comparing every candidate with every other one is quadratic, and a long novel
    produces sixty thousand candidates; that never finishes. Two names that are the
    same person written two ways share most of their characters and nearly all of
    their length, so bucketing by length and by first character loses nothing and
    turns the job into a few million comparisons.
    """
    buckets: dict[tuple[int, str], list[str]] = defaultdict(list)
    for w in cnt:
        if 3 <= len(w) <= 10:
            buckets[(len(w), w[0])].append(w)
    out = []
    for (L, first), words in buckets.items():
        if len(words) > 4000:
            words = sorted(words, key=lambda w: -cnt[w])[:4000]
        for a in words:
            if cnt[a] < min_major:
                continue
            cands = []
            for L2 in (L - 1, L, L + 1):
                for f2 in (first,) if L2 == L else (first,):
                    cands += buckets.get((L2, f2), [])
            for b in cands:
                if a == b or cnt[b] < 2 or cnt[a] < 8 * cnt[b]:
                    continue
                # 福尔图娜塔啊 is the name plus the next character, not another
                # spelling of it; only an interior difference counts as a variant.
                if b.startswith(a) or a.startswith(b) or b.endswith(a) or a.endswith(b):
                    continue
                if lev(a, b) > 2:
                    continue
                if lcs(a, b) < max(len(a), len(b)) - 1:
                    continue
                out.append({"major": a, "minor": b,
                            "n_major": cnt[a], "n_minor": cnt[b]})
    out.sort(key=lambda r: -r["n_major"])
    seen, uniq = set(), []
    for r in out:
        k = (r["major"], r["minor"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)
    return uniq


def context(text: str, word: str, width: int = 30) -> str:
    i = text.find(word)
    if i < 0:
        return ""
    return text[max(0, i - width):i + len(word) + width].replace("\n", " ")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for p in sys.argv[1:]:
        t = book_text(p)
        cnt = collect(t)
        print("==", os.path.basename(p), "candidates", len(cnt))
        for r in pairs(cnt)[:30]:
            print(f"   {r['major']}({r['n_major']}) ~ {r['minor']}({r['n_minor']})"
                  f"  | {context(t, r['minor'], 18)}")
