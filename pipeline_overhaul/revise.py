"""Chapter-level revision: the editor returns only the paragraphs it changed.

Why an edit list and not a rewrite: the delivered text contains passages the
reader explicitly praised (Moncada's execution, Amaranta's death, the yellow
butterflies). A full rewrite would put those at risk for no gain. The model is
therefore asked for <edit i="n">…</edit> blocks, and everything it does not
touch stays byte-identical.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "pipeline_whale"))

import common  # noqa: E402
import llm  # noqa: E402
import brief  # noqa: E402

MODELS = ["xm:mimo-v2.6-flash", "ox:gemini-3.8-flash"]
LOG = os.path.join(common.WORK, "revise.log")
_lock = threading.Lock()

EDIT_RE = re.compile(r"<edit\s+i=\"(\d+)\"\s*>(.*?)</edit>", re.S)


def log(msg: str) -> None:
    with _lock:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
        print(msg, flush=True)


# ────────────────────────────────────────────── term lists

_whale_g = None
_sol_g = None
_lotr_g = None


def terms_for(book: str, text: str, zh_text: str) -> str:
    global _whale_g, _sol_g, _lotr_g
    low = text.lower()
    rows = []
    if book == "whale":
        if _whale_g is None:
            from glossary import G
            _whale_g = G
        for k, v in _whale_g.items():
            base = k.split("’")[0].lower()
            if len(base) > 2 and re.search(r"\b" + re.escape(base) + r"\b", low):
                rows.append(f"{k}={v}")
    elif book == "soledad":
        if _sol_g is None:
            _sol_g = common.load_json(os.path.join(common.ROOT, "work_soledad/glossary.json"), {})
        for k, v in _sol_g.items():
            if k.startswith("_"):
                continue
            if k.lower() in low:
                rows.append(f"{k}={v}")
        rows += ["José Raquel Moncada=何塞·拉克尔·蒙卡达",
                 "Roque Carnicero=罗克·卡尔尼塞罗",
                 "médico invisible=看不见的医生"]
    else:
        if _lotr_g is None:
            _lotr_g = common.load_json(os.path.join(common.ROOT, "work/glossary.json"), {})
        for k, v in _lotr_g.items():
            forms = [v.get("zh", "")] + list(v.get("alt") or [])
            forms = [x for x in forms if x]
            if not forms:
                continue
            best = max(forms, key=lambda x: zh_text.count(x))
            if k.lower() in low or best in zh_text:
                rows.append(f"{k}={best}")
    seen, out = set(), []
    for r in rows:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return "；".join(out[:80])


# ────────────────────────────────────────────── prompt

def frag(t: str) -> str:
    """Mark paragraphs that stop mid-sentence: they came from a split source block."""
    t = t.rstrip()
    if t and t[-1] in "，、；":
        return "【残句，须对照原文补成完整一段】"
    return ""


def build_prompt(book: str, ch: dict) -> str:
    if book == "whale":
        lines = []
        for i, p in enumerate(ch["paras"]):
            lines.append(f"[{i}] EN: {p['src']}\nZH: {p['zh']}")
        src = "\n".join(lines)
        zh_text = "".join(p["zh"] for p in ch["paras"])
    else:
        zh = ch["zh"]
        numbered = "\n".join(f"[{i}]{frag(t)}{t}" for i, t in enumerate(zh))
        src = "\n\n".join(ch["src_paras"])
        src = src[:60000]
        zh_text = "".join(zh)
        lines = [numbered]
        src = src + "\n\n——译文段落（按编号）——\n" + numbered
    return src, zh_text


def revise_one(book: str, cid: str) -> str:
    path = common.chapter_path(book, cid)
    ch = common.load_json(path)
    out_path = os.path.join(common.WORK, book, "rev", cid + ".json")
    if os.path.exists(out_path):
        return f"skip {cid}"
    src, zh_text = build_prompt(book, ch)
    gl = terms_for(book, src, zh_text)
    sysmsg = brief.COMMON + "\n\n" + getattr(brief, book.upper())
    user = (f"术语表（必须遵守）：{gl}\n\n"
            f"原文与译文：\n{src}\n\n"
            "请只输出需要改动的段落，格式 <edit i=\"段号\">整段新译文</edit>。"
            "如果某段已经很好，不要输出它。")
    last = ""
    for model in MODELS:
        try:
            text, used = llm.chat(
                [{"role": "system", "content": sysmsg},
                 {"role": "user", "content": user}],
                model, max_tokens=16000, temperature=0.35,
                tag=f"{book}:rev:{cid}", timeout=900)
            edits = parse_edits(text, ch)
            bad = [e for e in edits if corrupted(e["old"], e["new"])]
            if bad:
                log(f"  {cid} {used}: {len(bad)} corrupted edits, retry")
                last = f"{len(bad)} corrupted"
                continue
            common.save_json(out_path, {"id": cid, "model": used, "edits": edits,
                                        "raw_len": len(text)})
            return f"{cid}: {len(edits)} edits via {used}"
        except Exception as e:  # noqa: BLE001
            last = str(e)[:160]
            log(f"!! {cid} {model} {last}")
    return f"{cid}: FAILED {last}"


CJK_SPACE = re.compile(r"(?<=[\u4e00-\u9fff\u3001-\u303f\uff01-\uff65])\s+"
                       r"(?=[\u4e00-\u9fff\u3001-\u303f\uff01-\uff65])")


def clean_new(s: str) -> str:
    s = s.replace("\r", "")
    s = re.sub(r"\n+", "", s)
    s = CJK_SPACE.sub("", s)
    return s.strip()


def corrupted(old: str, new: str) -> bool:
    """Catch decoder loops: a fragment repeated back to back.

    Broken runs look like 美人儿儿蕾梅黛丝 / 一层一层 / 它又缓缓升起。一时间.
    They are not style; a paragraph carrying them is worse than the one it
    replaced. We flag a repeat only when the NEW text has more of it than the
    OLD one, so natural reduplication (看着看着, 见识见识) is left alone.
    """
    for i in range(len(new) - 1):
        if "一" <= new[i] <= "鿿" and new[i] == new[i + 1]:
            pair = new[i] * 2
            if new.count(pair) > old.count(pair):
                return True
    for i in range(len(new) - 3):
        run = new[i:i + 2]
        if "一" <= run[0] <= "鿿" and run == new[i + 2:i + 4]:
            if new.count(run) > old.count(run):
                return True
    return False


def parse_edits(text: str, ch: dict) -> list[dict]:
    n = len(ch["paras"]) if "paras" in ch else len(ch["zh"])
    base = ch["paras"] if "paras" in ch else ch["zh"]
    out, seen = [], set()
    for m in EDIT_RE.finditer(text):
        i = int(m.group(1))
        new = clean_new(m.group(2))
        if i in seen or not (0 <= i < n) or not new:
            continue
        old = base[i]["zh"] if "paras" in ch else base[i]
        if not common.CJK.search(new):
            continue
        ratio = len(new) / max(1, len(old))
        if not (0.5 <= ratio <= 1.9):
            continue
        if "<" in new or ">" in new:
            continue
        if corrupted(old, new):
            continue
        seen.add(i)
        out.append({"i": i, "old": old, "new": new, "ratio": round(ratio, 2)})
    out.sort(key=lambda x: x["i"])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, choices=["whale", "soledad", "lotr"])
    ap.add_argument("--only", default="")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    d = os.path.join(common.WORK, a.book, "ch")
    cids = sorted(os.path.splitext(f)[0] for f in os.listdir(d))
    if a.only:
        want = set(a.only.split(","))
        cids = [c for c in cids if c in want]
    os.makedirs(os.path.join(common.WORK, a.book, "rev"), exist_ok=True)

    done = 0
    with ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(revise_one, a.book, c): c for c in cids}
        for f in as_completed(futs):
            done += 1
            try:
                log(f"[{done}/{len(cids)}] " + f.result())
            except Exception as e:  # noqa: BLE001
                log(f"[{done}/{len(cids)}] !! {futs[f]} {str(e)[:120]}")


if __name__ == "__main__":
    main()
