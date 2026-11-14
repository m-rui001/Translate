"""Language polishing pass for finished chapters.

The deterministic hygiene pass (pipeline/hygiene.py) fixes mechanical defects.
This pass addresses what only a reader can judge: 生硬句、译腔、词不达意、
语域分层模糊、诗句失韵。 It is *not* a re-translation — the draft is already
faithful, and every change has to survive hard checks:

  1. paragraph count and per-paragraph verse line count must be preserved;
  2. no name may drift (checked against the glossary *and* against the draft);
  3. no sentence may vanish and none may be invented (loose ratio guard);
  4. banned punctuation (semicolon, half-width quotes) is rejected;
  5. a paragraph whose new length differs wildly from the draft is dropped.

Anything that fails a check falls back to the draft, so the pass can only
improve the text (never silently break it). Results are cached per chunk, so
the whole book can be re-run cheaply.

Usage
    python pipeline/polish.py --chapters book2c07 --dry
    python pipeline/polish.py --all --workers 6
    python pipeline/polish.py --chapters book2c07 --apply
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import threading
import time

import providers
from glossary import G

OUT = "E:/Translate/work/out"
SRC = "E:/Translate/work/src"
CACHE = "E:/Translate/work/polish"
LOG = "E:/Translate/work/polish_calls.jsonl"

MODEL = os.environ.get("POLISH_MODEL", "css:deepseek-v4.1-flash")
PARAS_PER_CALL = 26          # keeps a call inside one context window with room to spare
MAX_TOKENS = 9000

_cfg_lock = threading.Lock()
_sem = threading.Semaphore(int(os.environ.get("POLISH_CONCURRENCY", "4")))

SYS = """你是资深中文文学译者兼编辑，长期翻译托尔金、勒古恩一系作品，汉语笔力老到，也懂得克制。
眼下不是重译，而是在一份已经合格的译稿上做语言打磨：让它读起来是汉语本来会有的说法，
同时保住原文的骨头。你改一个字都要有理由。"""

PROMPT = """下面是《魔戒》一段英文原文与一份已经合格的中文译稿。请做语言层打磨，不是重译。

<english>
{en}
</english>

<draft>
{zh}
</draft>

【审读意见，必须逐条落实】
1. 生硬句、文白夹杂、绵长的"的"字链，改成汉语本来会有的说法。原文意思不能动。
2. 刮掉译腔：英语式定语从句、被动句、抽象名词化，改成中文的动词句、短句、顺语序。
3. 词汇自然度：凡中文里不这么说的词（如"族民""小种人""原始族群"这一类生造或拗口的说法），
   换成地道说法。但**语域必须分层**：精灵王侯的对白庄重典雅、有音韵；霍比特人的口语土气、
   带幽默；两层不许拉平，不许把精灵写成乡下人，也不许把山姆写成读书人。
4. 诗歌：一行对一行，保住行数；尽力押尾韵或近韵，顿数大致整齐；挽歌要沉，山姆那种歪诗
   就该歪、该土，不要替它精雅。
5. 同音近音的歧义、指代不明、说话人不明，一并修掉。

【语域红线：最容易犯的错】
口语只能出现在霍比特人的对白里。叙述文字、精灵与人类贵族的对白，一律用书面语。
反例（这些都被判为不合格）：
  ✗ 一时间仿佛高得没法量   ✓ 仿佛高得不可度量
  ✗ 慢慢变大，直涨到几乎占满整面镜子   ✓ 渐渐扩大，几乎占满整面镜子
  ✗ 好些人正忙活着干活   ✓ 许多人正在忙碌
  ✗ 我不是出主意的人   ✓ 我并非谋士
  ✗ 他心里是有数的   ✓ 他自有道理
  ✗ 他慌急地说   ✓ 他慌张地说
  ✗ 我不会变黑   ✓ 我不会变得黑暗

【硬性禁止】
- 不许增译：不许加原文没有的意象、解释、情绪渲染、心理补白。
- 不许漏译：不许丢分句、数量、颜色、方位、动作顺序。
- 不许合并或拆分段落，不许改诗行数。
- 不许改动任何专名（人名、地名、族名），一律照原译稿。
- 不用分号，不用半角引号，不用英文标点；数字写中文。
- 不要写成文言，也不要写成大白话新闻体；目标是托尔金式的现代汉语书面语。

【格式】原样输出 {n} 段，段首标 [1]..[{n}]，段间空一行。诗行用 <verse> 与 </verse> 包住。
只输出正文，不写任何说明、评语、标题。"""


# ─────────────────────────────────────────────── helpers
def log(rec: dict) -> None:
    with _cfg_lock, open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def render_src(b: dict) -> str:
    if b["type"] == "p":
        return b["text"].strip()
    return "<verse>\n" + "\n".join(l.strip() for l in b["lines"]) + "\n</verse>"


def split_paras(text: str) -> list[str]:
    return [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]


def join_paras(paras: list[str]) -> str:
    return "\n\n".join(paras)


_CN = r"\u4e00-\u9fff"
SENT_END = "。！？…”’」』"


def sent_count(p: str) -> int:
    p = re.sub(r"<verse>|</verse>", "", p)
    p = re.sub(r"\n+", "", p)
    return len([s for s in re.split(r"(?<=[。！？])", p) if s.strip()])


def cjk_len(p: str) -> int:
    return len(re.findall(rf"[{_CN}]", p))


# ─────────────────────────────────────────────── validation
BANNED = [
    ("；", "分号"),
    ('"', "半角双引号"),
    ("'", "半角单引号"),
    ("...", "英文省略号"),
    (",", "半角逗号"),
    ("?", "半角问号"),
    ("!", "半角叹号"),
]

# Colloquialisms that may live in a hobbit's mouth but never in the narrator's
# voice or in the speech of Elves and lords. Checked only on non-dialogue
# paragraphs, so Sam can still say 鬼名堂.
NARRATIVE_BANNED = [
    "没法", "忙活", "直涨", "出主意的人", "那会儿", "打这儿", "干嘛",
    "自个儿", "一股脑", "瞧瞧", "好家伙", "心里有数", "慌急", "闹不好",
    "整面", "压过来", "住在这儿", "得慌",
]


def register_drift(draft_p: str, new_p: str) -> list[str]:
    """Narration must stay written; only dialogue may dip into the vernacular."""
    if draft_p.lstrip().startswith(("“", "‘")):
        return []
    return [w for w in NARRATIVE_BANNED if w in new_p and w not in draft_p]

NAME_PATTERNS = {zh for zh in G.values() if len(zh) >= 2}


def names_in(text: str) -> set[str]:
    return {n for n in NAME_PATTERNS if n in text}


def check_chunk(draft: list[str], new: list[str], src: list[dict]) -> tuple[list[str], list[str]]:
    """Return (accepted paragraphs, reasons for rejections)."""
    reasons: list[str] = []
    if len(new) != len(draft):
        return draft, [f"段数 {len(new)}≠{len(draft)}"]

    out = []
    for i, (d, n) in enumerate(zip(draft, new)):
        why = []

        d_verse = d.startswith("<verse>")
        n_verse = n.startswith("<verse>")
        if d_verse != n_verse:
            why.append("诗/散文类型变了")
        if d_verse and n_verse:
            dl = len([l for l in d.splitlines() if l.strip() and not l.strip().startswith("<")])
            nl = len([l for l in n.splitlines() if l.strip() and not l.strip().startswith("<")])
            if dl != nl:
                why.append(f"诗行数 {nl}≠{dl}")

        for bad, label in BANNED:
            if bad in n:
                why.append(f"出现{label}")

        drift = register_drift(d, n)
        if drift:
            why.append(f"叙述语域下沉 {drift[:3]}")

        # name drift: nothing may appear that was not in the draft, unless the
        # source itself introduces it
        extra = names_in(n) - names_in(d)
        if extra and not any(x in render_src(src[i]) for x in extra):
            why.append(f"新增专名 {sorted(extra)[:3]}")

        # length guard: polishing should not lengthen or shorten a paragraph much
        dl_, nl_ = cjk_len(d), cjk_len(n)
        if dl_ > 40:
            ratio = nl_ / dl_
            if ratio < 0.72 or ratio > 1.28:
                why.append(f"长度变化 {ratio:.2f}")

        # sentence guard for prose: ±1 sentence is noise, ±2 is a rewrite
        if not d_verse and sent_count(d) >= 3:
            if abs(sent_count(n) - sent_count(d)) > 1:
                why.append(f"句数 {sent_count(n)}≠{sent_count(d)}")

        if why:
            reasons.append(f"[{i+1}] " + "；".join(why))
            out.append(d)
        else:
            out.append(n)
    return out, reasons


# ─────────────────────────────────────────────── model call
def call_model(en: str, zh: str, n: int, tag: str) -> list[str] | None:
    prompt = PROMPT.format(en=en, zh=zh, n=n)
    with _sem:
        try:
            txt, used = providers.chat(
                [{"role": "system", "content": SYS}, {"role": "user", "content": prompt}],
                MODEL, temperature=0.45, max_tokens=MAX_TOKENS, tag=tag, retries=3,
                timeout=420.0)
        except Exception as e:  # noqa: BLE001
            log({"ts": round(time.time(), 1), "tag": tag, "error": str(e)[:200]})
            return None
    items = re.split(r"(?m)^\s*\[(\d+)\]\s*", txt)
    got: dict[int, str] = {}
    for k in range(1, len(items) - 1, 2):
        try:
            got[int(items[k])] = items[k + 1].strip()
        except ValueError:
            continue
    if len(got) < n:
        log({"ts": round(time.time(), 1), "tag": tag, "model": used,
             "warn": f"only {len(got)}/{n} paragraphs"})
        return None
    return [got[i] for i in range(1, n + 1)]


RETRY = """上一稿在这一段没通过硬校验：{why}
请重试同一段，务必避开该问题（诗行数必须一行对一行，不得出现分号）。

英文：
{en}

译稿：
{zh}

只输出这一段正文，不要编号，不要说明。"""


def call_one(en: str, zh: str, why: str, tag: str) -> str | None:
    with _sem:
        try:
            txt, _ = providers.chat(
                [{"role": "system", "content": SYS},
                 {"role": "user", "content": RETRY.format(why=why, en=en, zh=zh)}],
                MODEL, temperature=0.35, max_tokens=3000, tag=tag, retries=2, timeout=300.0)
            return txt.strip() or None
        except Exception as e:  # noqa: BLE001
            log({"ts": round(time.time(), 1), "tag": tag, "error": str(e)[:200]})
            return None


# ─────────────────────────────────────────────── driver
def polish_chapter(cid: str, apply: bool = False, dry: bool = False) -> dict:
    src = json.load(open(os.path.join(SRC, cid + ".json"), encoding="utf-8"))
    blocks = src["blocks"]
    ch_path = os.path.join(OUT, cid, "chapter.md")
    if not os.path.exists(ch_path):
        return {"cid": cid, "skip": "no chapter.md"}
    raw = open(ch_path, encoding="utf-8").read()
    lines = raw.split("\n", 1)
    title = lines[0]
    draft = split_paras(lines[1])

    if len(draft) != len(blocks):
        return {"cid": cid, "skip": f"段数不符 {len(draft)}≠{len(blocks)}"}

    os.makedirs(os.path.join(CACHE, cid), exist_ok=True)
    final: list[str] = []
    all_reasons: list[str] = []
    changed = 0
    for start in range(0, len(draft), PARAS_PER_CALL):
        stop = min(start + PARAS_PER_CALL, len(draft))
        n = stop - start
        cache_p = os.path.join(CACHE, cid, f"p{start:03d}-{stop:03d}.json")
        if os.path.exists(cache_p):
            res = json.load(open(cache_p, encoding="utf-8"))
        else:
            en = "\n\n".join(f"[{i - start + 1}] {render_src(blocks[i])}" for i in range(start, stop))
            zh = "\n\n".join(f"[{i - start + 1}] {draft[i]}" for i in range(start, stop))
            tag = f"{cid}:{start}-{stop}"
            new = call_model(en, zh, n, tag)
            if new is None:
                res = {"accepted": draft[start:stop], "reasons": ["call failed"], "ok": False}
            else:
                acc, why = check_chunk(draft[start:stop], new, blocks[start:stop])
                # Second chance: a rejection often means the model added a
                # semicolon or broke a verse line, not that it mistranslated.
                for w in list(why):
                    m = re.match(r"\[(\d+)\]\s*(.+)", w)
                    if not m:
                        continue
                    k = int(m.group(1)) - 1
                    i = start + k
                    again = call_one(render_src(blocks[i]), draft[i], m.group(2),
                                     f"{tag}:retry{k+1}")
                    if again is None:
                        continue
                    acc2, why2 = check_chunk([draft[i]], [again], [blocks[i]])
                    if not why2:
                        acc[k] = again
                        why = [x for x in why if x != w]
                res = {"accepted": acc, "reasons": why, "ok": True,
                       "changed": sum(1 for a, b in zip(acc, draft[start:stop]) if a != b)}
            json.dump(res, open(cache_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        final += res["accepted"]
        all_reasons += res.get("reasons", [])
        changed += res.get("changed", 0)

    result = {"cid": cid, "paras": len(draft), "changed": changed,
              "rejected": len(all_reasons), "reasons": all_reasons[:12]}
    if dry:
        for i, (a, b) in enumerate(zip(draft, final)):
            if a != b:
                print(f"  [{i+1}] OLD: {a[:70]}")
                print(f"       NEW: {b[:70]}")
    if apply:
        open(ch_path, "w", encoding="utf-8").write(title + "\n\n" + join_paras(final) + "\n")
    return result


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    if a.all:
        cids = [os.path.basename(os.path.dirname(p))
                for p in sorted(glob.glob(os.path.join(OUT, "*", "chunks.json")))]
    elif a.chapters:
        cids = expand(a.chapters)
    else:
        ap.error("need --chapters or --all")

    results = []
    lock = threading.Lock()

    def work(cid):
        r = polish_chapter(cid, apply=a.apply, dry=a.dry)
        with lock:
            results.append(r)
            print(json.dumps({k: v for k, v in r.items() if k != "reasons"},
                             ensure_ascii=False))

    threads = []
    for cid in cids:
        while threading.active_count() > a.workers:
            time.sleep(0.4)
        t = threading.Thread(target=work, args=(cid,), daemon=True)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    ok = [r for r in results if "changed" in r]
    print(f"\nchapters {len(results)}  polished {len(ok)}  "
          f"paragraphs changed {sum(r['changed'] for r in ok)}  "
          f"rejected by checks {sum(r['rejected'] for r in ok)}")


def expand(spec: str) -> list[str]:
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            m1 = re.match(r"([a-z]+\d*c?)(\d+)$", a)
            m2 = re.match(r"([a-z]+\d*c?)(\d+)$", b)
            if m1 and m2 and m1.group(1) == m2.group(1):
                for i in range(int(m1.group(2)), int(m2.group(2)) + 1):
                    out.append(f"{m1.group(1)}{i:02d}")
                continue
        out.append(part)
    return out


if __name__ == "__main__":
    main()
