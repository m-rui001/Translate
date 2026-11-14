"""Deterministic manuscript hygiene for the finished 《魔戒》 drafts.

Everything here is mechanical and idempotent — no model involved. It fixes the
defect classes that review found in *our* text (as opposed to the reference
edition), and it is safe to re-run over the whole tree at any time.

Fixes
  1. Quote nesting per paragraph. Tolkien uses ‘…’ for the outer level, so the
     drafting models sometimes mirror that and emit dialogue as ‘…’. Chinese
     convention wants “…” outside and ‘…’ inside. Rebuilt with a depth machine.
  2. Intra-linequote normalisation ("…" straight quotes → “ ”).
  3. Traditional characters (one paragraph came back in complex Chinese).
  4. Project name drift: one canonical Chinese form per English name.
  5. Stray Latin letters that are *not* deliberate (B.B. and the G rune stay).
  6. Empty paragraphs, doubled blank lines, trailing spaces.
"""
from __future__ import annotations

import glob
import re
import sys

# ── 1/2. quotes ────────────────────────────────────────────────────────────
OD, CD, OS, CS = "“", "”", "‘", "’"


def fix_para_quotes(p: str) -> str:
    """Rebuild quote nesting for one paragraph: outermost pair is always “…”."""
    if not any(c in p for c in "“”‘’\""):
        return p
    p = _straight_to_curly(p)
    out = []
    dd = ds = 0
    for ch in p:
        if ch in (OD, OS):
            if dd > 0:
                out.append(OS)
                ds += 1
            else:
                out.append(OD)
                dd += 1
        elif ch in (CD, CS):
            if ds > 0:
                out.append(CS)
                ds -= 1
            elif dd > 0:
                out.append(CD)
                dd -= 1
            else:
                out.append(CD)
        else:
            out.append(ch)
    return "".join(out)


def _straight_to_curly(p: str) -> str:
    """Paired "..." → “...”; a lone ' inside CJK → ‘…’ when clearly a pair."""
    if '"' not in p and "'" not in p:
        return p
    out = []
    open_d = True
    for i, ch in enumerate(p):
        prev = p[i - 1] if i else ""
        if ch == '"':
            out.append(OD if open_d or not prev else CD)
            open_d = not open_d
        elif ch == "'" and not prev.isalnum():
            out.append(OS)
        else:
            out.append(ch)
    return "".join(out)


# ── 3. traditional characters ──────────────────────────────────────────────
_cc = None


def to_simplified(text: str) -> str:
    global _cc
    if not any(0x3400 <= ord(c) <= 0x9FFF and c in _TRAD_SEED for c in text):
        return text
    try:
        if _cc is None:
            import opencc
            _cc = opencc.OpenCC("t2s")
        return _cc.convert(text)
    except Exception:
        return text


_TRAD_SEED = set(
    "偉靜沒傳時來開將與爲為說這個們會對關發現實現點體國學長間問題經過還無麼樣種"
    "義務應該當經濟產業東並於從區見觀聽認據處這麼兒內兩隻幾頭義億萬歲歷飛風雲"
    "電氣龍馬鳥魚車軍農運進遠邊過達連標準樂習親識記錄號稱類數藝術節華麗嚴壯肅")


# ── 4. name drift ──────────────────────────────────────────────────────────
# English name -> (canonical Chinese, [wrong variants])
NAMES = {
    "Caras Galadhon": ("卡拉斯加拉顿", ["卡拉斯加拉松"]),
    "Galadhrim": ("加拉德林", ["加拉德民", "加拉兹民"]),
    "Nenya": ("能雅", ["南雅"]),
    "Nargothrond": ("纳国斯隆德", ["纳苟斯隆德"]),
    "Gondolin": ("刚多林", ["贡多林"]),
    "Kheled-zâram": ("凯雷德扎拉姆", ["凯勒德扎拉姆", "凯雷德-扎拉姆", "凯雷德–扎拉姆"]),
    "Kibil-nâla": ("基比尔纳拉", ["基比尔-纳拉", "基比尔–纳拉"]),
    "mallorn": ("梅隆树", ["瑁珑树", "瑁珑"]),
    "Lórien": ("罗斯洛立安", ["洛丝萝林", "洛丝罗瑞恩", "萝林", "罗瑞恩"]),
    "Eärendil": ("埃雅仁迪尔", []),      # Elendil = 埃兰迪尔, kept apart
    "Mithrandir": ("米斯兰迪尔", ["米斯兰迪"]),
    "Galadriel": ("凯兰崔尔", ["加拉德瑞尔"]),
    "Celeborn": ("凯勒鹏", ["凯勒博恩"]),
    "Durin": ("都灵", ["杜林"]),
    "Moria": ("摩瑞亚", ["莫利亚", "摩利亚"]),
    "Khazad-dûm": ("卡扎督姆", ["卡萨督姆"]),
}
_DROP_TO_MALLORN = ("瑁珑树",)   # 瑁珑 alone is the tree in the reference edition


def fix_names(text: str) -> str:
    for _en, (canon, variants) in NAMES.items():
        for v in sorted(variants, key=len, reverse=True):
            if not v or v not in text:
                continue
            # a variant that is a proper prefix of the canonical form (米斯兰迪 /
            # 米斯兰迪尔) must not eat the canonical's own tail
            if canon.startswith(v):
                text = re.sub(re.escape(v) + r"(?!" + re.escape(canon[len(v):len(v) + 1]) + r")",
                              canon, text)
            else:
                text = text.replace(v, canon)
    return text


# ── 5. latin leftovers ─────────────────────────────────────────────────────
KEEP_LATIN = re.compile(r"(?:^|[\s《（(“])(B\.B\.|G)(?=[\s》），。”]|$)")


def fix_latin(text: str) -> str:
    """Drop stray English words the model left in, keep the two real ones."""
    if not re.search(r"[A-Za-z]", text):
        return text

    def repl(m):
        w = m.group(0)
        if w.strip(" 　") in ("B.B.", "G"):
            return w
        return ""

    # remove latin runs that sit inside Chinese prose
    protected = []
    for m in KEEP_LATIN.finditer(text):
        protected.append((m.start(), m.end()))

    def is_protected(i):
        return any(a <= i < b for a, b in protected)

    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        if re.match(r"[A-Za-z]", ch) and not is_protected(i):
            j = i
            while j < len(text) and re.match(r"[A-Za-z'’\-\. ]", text[j]):
                j += 1
            # only strip if flanked by CJK (i.e. it is an intruder, not a citation)
            before = text[i - 1] if i else ""
            after = text[j] if j < len(text) else ""
            if (not before or re.match(r"[\u4e00-\u9fff]", before)) and \
               (not after or re.match(r"[\u4e00-\u9fff\s]", after)):
                i = j
                continue
            out.append(text[i:j])
            i = j
            continue
        out.append(ch)
        i += 1
    return "".join(out)


# ── 6. whitespace ──────────────────────────────────────────────────────────
def tidy(text: str) -> str:
    text = text.replace("\r", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"(?<=[\u4e00-\u9fff])[ \t]+(?=[\u4e00-\u9fff])", "", text)
    return text


def clean_doc(text: str) -> str:
    """Apply every fix, paragraph by paragraph (keeps the heading alone)."""
    text = to_simplified(text)
    text = fix_names(text)
    text = fix_latin(text)
    parts = re.split(r"(\n\s*\n)", text)
    for i in range(0, len(parts), 2):
        parts[i] = fix_para_quotes(parts[i])
    text = "".join(parts)
    return tidy(text)


# ── report ─────────────────────────────────────────────────────────────────
def quote_defects(paras: list[str]) -> list[str]:
    """Chinese dialogue convention: each continuation paragraph re-opens with “
    and only the *last* paragraph of the run closes with ”. So a paragraph that
    ends open must be followed by a paragraph that starts open; and a paragraph
    that starts open must either close or be followed by another open one.

    <verse> blocks are transparent: a song quoted inside a speech is its own
    paragraph but the speech keeps running through it."""
    out = []
    depth = 0
    # A song quoted inside a speech is its own paragraph but the speech keeps
    # running through it, so trailing verse blocks do not release the open quote.
    prose = [(i, p) for i, p in enumerate(paras) if not p.startswith("<verse>")]
    for k, (i, p) in enumerate(prose):
        d = depth
        for ch in p:
            if ch == OD:
                d += 1
            elif ch == CD:
                d = max(0, d - 1)
        j = prose[k + 1][0] if k + 1 < len(prose) else len(paras)
        verse_between = any(x.startswith("<verse>") for x in paras[i + 1:j])
        nxt = prose[k + 1][1].lstrip() if k + 1 < len(prose) else ""
        if d != 0:
            if nxt.startswith(OD) or verse_between:
                depth = 0          # continuation: next para re-opens, or a
                                   # quoted song sits in between
            else:
                out.append(f"[{i}] 引号未闭合且下一段不续引：…{p[-24:]}")
                depth = d
        elif depth != 0:
            out.append(f"[{i}] 上段续引在此段未收尾：{p[:24]}…")
            depth = 0
        else:
            depth = 0
    return out


def audit(path: str) -> list[str]:
    t = open(path, encoding="utf-8").read()
    body = [p for p in re.split(r"\n\s*\n", t) if p.strip()]
    issues = []
    if body:
        body = body[1:]
    for i, p in enumerate(body):
        if ("‘" in p or "’" in p) and "“" not in p and "”" not in p:
            issues.append(f"[{i}] 整段只有单引号")
        if '"' in p:
            issues.append(f"[{i}] 半角引号")
    issues += quote_defects(body)
    for en, (canon, variants) in NAMES.items():
        for v in variants:
            if not v or v not in t:
                continue
            if canon.startswith(v):
                if re.search(re.escape(v) + r"(?!" + re.escape(canon[len(v):len(v) + 1]) + r")", t):
                    issues.append(f"专名漂移 {v} → {canon}")
            else:
                issues.append(f"专名漂移 {v} → {canon}")
    latin = [w for w in re.findall(r"[A-Za-z]{2,}", t) if w != "verse"]
    if latin:
        issues.append(f"拉丁残留 {sorted(set(latin))[:5]}")
    if any(c in _TRAD_SEED for c in t):
        issues.append("繁体字")
    return issues


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    dry = "--apply" not in sys.argv
    files = sorted(glob.glob("E:/Translate/work/out/*/chapter.md")) + \
            sorted(glob.glob("E:/Translate/work/out/*/chunk*/final.txt"))
    changed = 0
    for f in files:
        raw = open(f, encoding="utf-8").read()
        new = clean_doc(raw)
        if new != raw:
            changed += 1
            if dry:
                for a, b in zip(re.split(r"\n\s*\n", raw), re.split(r"\n\s*\n", new)):
                    if a != b:
                        print(f"--- {f}")
                        print("OLD:", a[:80].replace("\n", "|"))
                        print("NEW:", b[:80].replace("\n", "|"))
                        break
            else:
                open(f, "w", encoding="utf-8").write(new)
    print(f"{'would change' if dry else 'changed'} {changed}/{len(files)}")
