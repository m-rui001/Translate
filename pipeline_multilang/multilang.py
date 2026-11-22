#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""multilang.py — 把一份文本按段拆开，每段随机分配一种语言（100+ 语种不重复），
分段翻译、装配、抽检。

四个阶段：

    python -X utf8 pipeline_multilang/multilang.py prepare  IN.txt -o WORK [--seed 7]
    python -X utf8 pipeline_multilang/multilang.py translate -o WORK [--model M] [--workers 4]
    python -X utf8 pipeline_multilang/multilang.py assemble  -o WORK [--title T]
    python -X utf8 pipeline_multilang/multilang.py verify     -o WORK

产物：

    WORK/segments.json   分段 + 语种分配 + 译文（唯一真源，可手改）
    WORK/cache.json      翻译缓存（sha1(语种+原文) → 译文）
    WORK/manifest.md     人工/外部翻译用的清单（含原文与语种，便于逐条填）
    WORK/out/*.multi.txt 成品：每段前一行语种标记
    WORK/out/INDEX.md    段号 / 语种 / 字数 / 校验状态 对照表

设计要点：
- 围栏代码块（``` ... ```）整块保留，不拆不译。
- 标题行、分隔线 `---`、纯 HTML 标签行按原样跳过（kind=skip）。
- 语种按「池内不重复」轮转分配；段数超过池容量时重洗一轮。
- 译文缺失不静默通过：assemble 与 verify 都会报缺段。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from langpool import BY_CODE, LANGS  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------- 文字系统

# 用于抽检「译文是否真的落在目标文字系统里」。只收常见系统，缺的按 Latn 处理。
RANGES = {
    "Hani": [(0x4E00, 0x9FFF), (0x3400, 0x4DBF)],
    "Jpan": [(0x3040, 0x30FF), (0x4E00, 0x9FFF)],
    "Hang": [(0xAC00, 0xD7AF), (0x1100, 0x11FF)],
    "Cyrl": [(0x0400, 0x04FF)],
    "Grek": [(0x0370, 0x03FF)],
    "Arab": [(0x0600, 0x06FF), (0x0750, 0x077F)],
    "Hebr": [(0x0590, 0x05FF)],
    "Deva": [(0x0900, 0x097F)],
    "Beng": [(0x0980, 0x09FF)],
    "Guru": [(0x0A00, 0x0A7F)],
    "Gujr": [(0x0A80, 0x0AFF)],
    "Orya": [(0x0B00, 0x0B7F)],
    "Taml": [(0x0B80, 0x0BFF)],
    "Telu": [(0x0C00, 0x0C7F)],
    "Knda": [(0x0C80, 0x0CFF)],
    "Mlym": [(0x0D00, 0x0D7F)],
    "Sinh": [(0x0D80, 0x0DFF)],
    "Thai": [(0x0E00, 0x0E7F)],
    "Laoo": [(0x0E80, 0x0EFF)],
    "Tibt": [(0x0F00, 0x0FFF)],
    "Mymr": [(0x1000, 0x109F)],
    "Geor": [(0x10A0, 0x10FF)],
    "Ethi": [(0x1200, 0x137F)],
    "Cher": [(0x13A0, 0x13FF)],
    "Cans": [(0x1400, 0x167F)],
    "Khmr": [(0x1780, 0x17FF)],
    "Mong": [(0x1800, 0x18AF)],
    "Thaa": [(0x0780, 0x07BF)],
    "Armn": [(0x0530, 0x058F)],
    "Tfng": [(0x2D30, 0x2D7F)],
}
LATIN_EXTRA = [
    (0x00C0, 0x024F), (0x1E00, 0x1EFF), (0x2C60, 0x2C7F),
    (0xA720, 0xA7FF), (0x0100, 0x017F),
]


def script_ratio(text: str, script: str) -> float:
    """目标文字系统字符占「字母类字符」的比例。"""
    letters = 0
    hit = 0
    ranges = RANGES.get(script)
    for ch in text:
        if not ch.isalpha():
            continue
        letters += 1
        cp = ord(ch)
        if ranges:
            if any(a <= cp <= b for a, b in ranges):
                hit += 1
        else:  # Latn
            if cp < 0x250 or any(a <= cp <= b for a, b in LATIN_EXTRA):
                hit += 1
    return 1.0 if letters == 0 else hit / letters


def digest(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------- 分段

FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEAD_RE = re.compile(r"^\s{0,3}#{1,6}\s")
HR_RE = re.compile(r"^\s{0,3}([-*_])(\s*\1){2,}\s*$")
HTML_ONLY_RE = re.compile(r"^\s*</?[A-Za-z][^>]*>\s*$")


def split_segments(text: str, skip_headings: bool = True, min_chars: int = 0):
    """返回 [(kind, body)]，kind ∈ text / code / skip。"""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    segs: list[tuple[str, str]] = []
    buf: list[str] = []
    code: list[str] | None = None

    def flush():
        nonlocal buf
        if buf:
            body = "\n".join(buf).strip("\n")
            if body.strip():
                segs.append(("text", body))
            buf = []

    for line in lines:
        if code is not None:
            code.append(line)
            if FENCE_RE.match(line) and line.strip().strip("`~") == "":
                segs.append(("code", "\n".join(code)))
                code = None
            continue
        if FENCE_RE.match(line):
            flush()
            code = [line]
            continue
        if not line.strip():
            flush()
            continue
        if skip_headings and (HEAD_RE.match(line) or HR_RE.match(line) or HTML_ONLY_RE.match(line)):
            flush()
            segs.append(("skip", line))
            continue
        buf.append(line)
    if code is not None:                       # 未闭合的代码块
        flush()
        segs.append(("code", "\n".join(code)))
    flush()

    if min_chars > 0:                          # 合并过短的正文段
        merged: list[tuple[str, str]] = []
        carry = None
        for kind, body in segs:
            if carry is not None:
                if kind == "text" and carry[0] == "text":
                    body = carry[1] + "\n" + body
                else:
                    merged.append(carry)
                    carry = None
            if kind == "text" and len(body) < min_chars:
                carry = (kind, body)
                continue
            if carry is not None:
                merged.append(carry)
                carry = None
            merged.append((kind, body))
        if carry is not None:
            merged.append(carry)
        segs = merged
    return segs


# ---------------------------------------------------------------- 语种分配

def assign_languages(n: int, seed: int, pool: list[tuple], avoid: set[str]) -> list[dict]:
    rnd = random.Random(seed)
    chosen: list[tuple] = []
    while len(chosen) < n:
        round_ = [x for x in pool if x[0] not in {c[0] for c in chosen}]
        if not round_:
            break
        rnd.shuffle(round_)
        chosen.extend(round_)
    out = []
    for i in range(n):
        code, zh, nat, sc = chosen[i]
        out.append({"code": code, "zh": zh, "native": nat, "script": sc,
                    "avoid_same_as": code in avoid})
    return out


# ---------------------------------------------------------------- 模型调用

SYSTEM_PROMPT = (
    "You are a professional literary translator. Translate the text the user sends "
    "into {lang}. Rules: output ONLY the translation, no preface, no notes, no "
    "romanization, no explanation. Preserve the original line breaks, list markers, "
    "em dashes and punctuation style. Keep proper nouns, code identifiers, numbers, "
    "URLs and file paths unchanged. If the text contains a glossary, follow it exactly."
)


# 语体变形：把已译好的段落再改写成另一种「语言形态」。
# 键名即 --styles 里可用的值。
STYLE_PROMPTS = {
    "symbolic": (
        "Rewrite the text below as a SYMBOL LANGUAGE. Express each content word with "
        "one emoji or Unicode symbol, keep the original word order, separate tokens "
        "with single spaces, drop function words, keep at most minimal punctuation. "
        "Output ONLY the symbol sequence, nothing else."
    ),
    "telegraphic": (
        "Rewrite the text below in TELEGRAM STYLE: keep only content words, delete "
        "articles, prepositions, conjunctions, pronouns and auxiliary verbs, all "
        "lowercase, no punctuation, tokens separated by ' STOP '. Output ONLY the "
        "telegram, nothing else."
    ),
    "mixed": (
        "Rewrite the text below as a MIXED-LANGUAGE paragraph: code-switch at clause "
        "boundaries between at least three different languages of your choice, keeping "
        "one coherent reading and the same meaning and length. Output ONLY the text."
    ),
    "gloss": (
        "Rewrite the text below as SIGN-LANGUAGE GLOSS: uppercase content-word tokens "
        "only, drop function words, use hyphens inside multi-word concepts, separate "
        "clauses with ' / '. Output ONLY the gloss, nothing else."
    ),
    "abbrev": (
        "Rewrite the text below as pure SMS/telegraph abbreviations: consonant skeletons, "
        "no vowels where unambiguous, no punctuation, single spaces. Output ONLY the "
        "abbreviated text."
    ),
}


def call_model(base: str, key: str, model: str, lang_desc: str, text: str,
               timeout: int = 180, sys_prompt: str | None = None) -> str:
    url = base.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "temperature": 0.3,
        "messages": [
            {"role": "system",
             "content": sys_prompt if sys_prompt is not None
             else SYSTEM_PROMPT.format(lang=lang_desc)},
            {"role": "user", "content": text},
        ],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()



def chunk_text(text: str, limit: int) -> list[str]:
    """按行切块，保留行序，每块 <= limit 字符（单行超长则整行成块）。"""
    if limit <= 0 or len(text) <= limit:
        return [text]
    chunks, cur, n = [], [], 0
    for line in text.split(NL):
        if cur and n + len(line) + 1 > limit:
            chunks.append(NL.join(cur))
            cur, n = [], 0
        cur.append(line)
        n += len(line) + 1
    if cur:
        chunks.append(NL.join(cur))
    return chunks


NL = chr(10)


def get_env(name: str, default: str = "") -> str:
    return os.environ.get(name, default) or default


# ---------------------------------------------------------------- 各阶段

def load_work(work: Path) -> dict:
    p = work / "segments.json"
    if not p.exists():
        sys.exit(f"找不到 {p}，先跑 prepare")
    return json.loads(p.read_text(encoding="utf-8"))


def save_work(work: Path, doc: dict) -> None:
    (work / "segments.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")


def cmd_prepare(args) -> None:
    src = Path(args.input)
    text = src.read_text(encoding="utf-8")
    segs = split_segments(text, skip_headings=not args.keep_headings,
                          min_chars=args.min_chars)
    text_idx = [(i, s) for i, s in enumerate(segs) if s[0] == "text"]
    pool = [x for x in LANGS if not args.only or x[0] in set(args.only.split(","))]
    if args.exclude_script:
        bad = set(args.exclude_script.split(","))
        pool = [x for x in pool if x[3] not in bad]
    langs = assign_languages(len(text_idx), args.seed, pool, set())
    if len(pool) < len(text_idx) and not args.allow_repeat:
        print(f"[warn] 正文段数 {len(text_idx)} > 语种池 {len(pool)}，语种会重复。"
              f" 用 --only/--exclude-script 缩池，或 --allow-repeat 确认。")

    out = []
    li = 0
    for kind, body in segs:
        item = {"id": len(out), "kind": kind, "source": body, "translation": None}
        if kind == "text":
            item["lang"] = langs[li]
            li += 1
        out.append(item)

    work = Path(args.out)
    work.mkdir(parents=True, exist_ok=True)
    doc = {
        "source_file": str(src.resolve()),
        "seed": args.seed,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "segments": out,
    }
    save_work(work, doc)

    used = sorted({s["lang"]["code"] for s in out if s.get("lang")})
    print(f"段：{len(out)}（正文 {len(text_idx)} / 代码 "
          f"{sum(1 for s in out if s['kind']=='code')} / 跳过 "
          f"{sum(1 for s in out if s['kind']=='skip')}）")
    print(f"语种：{len(used)} 种不重复 → {work / 'segments.json'}")
    if len(text_idx) > len(pool):
        print(f"[warn] 池内只有 {len(pool)} 种语言，已开始第二轮。")

    # 人工清单
    lines = [f"# 翻译清单 · {src.name}", "",
             f"段数 {len(text_idx)}，语种 {len(used)} 种。每段只译成标注的那一种语言。", ""]
    for s in out:
        if s["kind"] != "text":
            continue
        L = s["lang"]
        lines += [f"## {s['id']:03d} · {L['zh']} / {L['code']} / {L['native']}", "",
                  "```text", s["source"], "```", ""]
    (work / "manifest.md").write_text("\n".join(lines), encoding="utf-8")


def cmd_translate(args) -> None:
    work = Path(args.out)
    doc = load_work(work)
    cache_p = work / "cache.json"
    cache = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else {}

    base = args.base or get_env("FREEAI_BASE", "http://127.0.0.1:8317")
    key = args.key or get_env("FREEAI_KEY", "sk-local")
    model = args.model or get_env("MULTILANG_MODEL", "")
    if not model:
        sys.exit("缺模型名：加 --model，或设 MULTILANG_MODEL。")

    only_ids = None
    if args.ids:
        only_ids = {int(x) for x in args.ids.replace(" ", "").split(",") if x}

    todo = []
    for s in doc["segments"]:
        if args.force and only_ids is not None and s["id"] in only_ids:
            s["translation"] = None
            s.pop("error", None)
        if s["kind"] != "text" or s["translation"]:
            continue
        if only_ids is not None and s["id"] not in only_ids:
            continue
        L = s["lang"]
        ck = digest(f"{L['code']}\x00{s['source']}\x00{model}")
        if ck in cache and not args.no_cache:
            s["translation"] = cache[ck]
            s["lang"]["from_cache"] = True
            continue
        todo.append((s, ck))

    print(f"待译 {len(todo)} 段（命中缓存 {sum(1 for s in doc['segments'] if (s.get('lang') or {}).get('from_cache'))}）")
    save_work(work, doc)
    if not todo:
        return

    def job(item):
        s, ck = item
        L = s["lang"]
        desc = f"{L['zh']} ({L['native']}, ISO {L['code']})"
        last = ""
        for attempt in range(args.retries):
            try:
                parts = chunk_text(s["source"], args.max_chunk)
                out = NL.join(
                    call_model(base, key, model, desc, part, timeout=args.timeout)
                    for part in parts)
                if out:
                    return s, ck, out, ""
                last = "空译文"
            except Exception as e:                                  # noqa: BLE001
                last = f"{type(e).__name__}: {e}"
                time.sleep(min(2 ** attempt, 8))
        return s, ck, None, last

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(job, t) for t in todo]
        for f in as_completed(futs):
            s, ck, out, err = f.result()
            if out:
                s["translation"] = out
                if not args.no_cache:
                    cache[ck] = out
                done += 1
                print(f"  [{done}/{len(todo)}] #{s['id']:03d} {s['lang']['code']} ok")
            else:
                s["error"] = err
                print(f"  #{s['id']:03d} {s['lang']['code']} 失败：{err}")
            if done % 10 == 0:
                save_work(work, doc)
                cache_p.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    save_work(work, doc)
    cache_p.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    print(f"完成 {done}，仍缺 {sum(1 for s in doc['segments'] if s['kind']=='text' and not s['translation'])}")


def cmd_restyle(args) -> None:
    """随机抽段（或按 --ids 指定），把该段改写成指定语体形态。"""
    work = Path(args.out)
    doc = load_work(work)
    cache_p = work / "cache.json"
    cache = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else {}
    base = args.base or get_env("FREEAI_BASE", "http://127.0.0.1:8317")
    key = args.key or get_env("FREEAI_KEY", "sk-local")
    model = args.model or get_env("MULTILANG_MODEL", "")
    if not model:
        sys.exit("缺模型名：加 --model，或设 MULTILANG_MODEL。")

    styles = [x.strip() for x in args.styles.split(",") if x.strip()]
    bad = [x for x in styles if x not in STYLE_PROMPTS]
    if bad:
        sys.exit(f"未知语体 {bad}；可选 {list(STYLE_PROMPTS)}")

    pool = [s for s in doc["segments"] if s["kind"] == "text" and s.get("translation")]
    if args.ids:
        want = {int(x) for x in args.ids.replace(" ", "").split(",") if x}
        picked = [s for s in pool if s["id"] in want]
    else:
        rnd = random.Random(args.seed)
        picked = rnd.sample(pool, min(args.sample, len(pool)))
    if not picked:
        sys.exit("没有可改写的段（需要已译文本；先跑 translate）")

    use_source = args.base_text == "source"
    jobs = []
    for s in picked:
        text = s["source"] if use_source else s["translation"]
        for st in styles:
            ck = digest(f"STYLE:{st}\x00{text}\x00{model}")
            if ck in cache and not args.no_cache:
                s.setdefault("styles", {})[st] = cache[ck]
                continue
            jobs.append((s, st, text, ck))

    print(f"抽中 {len(picked)} 段 × {len(styles)} 语体，待处理 {len(jobs)}"
          f"（缓存命中 {len(picked)*len(styles)-len(jobs)}）")
    print("段号：" + ", ".join(str(s["id"]) for s in picked))
    save_work(work, doc)
    if not jobs:
        return

    def job(item):
        s, st, text, ck = item
        last = ""
        for attempt in range(args.retries):
            try:
                out = call_model(base, key, model, "", text, timeout=args.timeout,
                                 sys_prompt=STYLE_PROMPTS[st])
                if out:
                    return s, st, ck, out, ""
                last = "空输出"
            except Exception as e:                                  # noqa: BLE001
                last = f"{type(e).__name__}: {e}"
                time.sleep(min(2 ** attempt, 8))
        return s, st, ck, None, last

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for s, st, ck, out, err in [f.result() for f in
                                    [ex.submit(job, j) for j in jobs]]:
            if out:
                s.setdefault("styles", {})[st] = out
                cache[ck] = out
                done += 1
                print(f"  #{s['id']:03d} {st} ok ({len(out)} 字符)")
            else:
                print(f"  #{s['id']:03d} {st} 失败：{err}")
    save_work(work, doc)
    cache_p.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    print(f"完成 {done}/{len(jobs)}")


def cmd_assemble(args) -> None:
    work = Path(args.out)
    doc = load_work(work)
    title = args.title or Path(doc["source_file"]).stem
    out_dir = work / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    missing = [s["id"] for s in doc["segments"] if s["kind"] == "text" and not s["translation"]]
    if missing and not args.allow_missing:
        sys.exit(f"{len(missing)} 段缺译文（#{missing[:8]}…）；补齐或加 --allow-missing")

    tag = args.tag_format
    style_tag = args.style_tag_format
    body, index_rows, styled = [], [], []
    for s in doc["segments"]:
        if s["kind"] == "text":
            L = s["lang"]
            body.append(tag.format(native=L["native"], zh=L["zh"], code=L["code"]))
            body.append(s["translation"] or f"[缺译文 · {L['code']}]")
            body.append("")
            if s.get("styles") and not args.no_styles:
                for st, val in s["styles"].items():
                    body.append(style_tag.format(style=STYLE_LABELS.get(st, st)))
                    body.append(val)
                    body.append("")
                styled.append((s["id"], L["code"], ",".join(s["styles"])))
            ratio = script_ratio(s["translation"] or "", L["script"])
            index_rows.append((s["id"], L["zh"], L["code"], L["script"],
                               len(s["source"]), len(s["translation"] or ""),
                               f"{ratio:.0%}"))
        elif s["kind"] == "code":
            body.append(s["source"])
            body.append("")
        else:
            body.append(s["source"])

    txt = "\n".join(body).rstrip() + "\n"
    target = out_dir / f"{args.name or title}.multi.txt"
    target.write_text(txt, encoding="utf-8")

    head = "| 段 | 语种 | code | 文字 | 原文字符 | 译文字符 | 目标文字系统占比 |\n|---|---|---|---|---|---|---|\n"
    rows = "\n".join("| {} | {} | {} | {} | {} | {} | {} |".format(*r) for r in index_rows)
    (out_dir / "INDEX.md").write_text(
        f"# {title} · 多语种版本\n\n"
        f"源文件：`{doc['source_file']}`\n段数：{len(index_rows)}"
        f"（语种 {len({r[2] for r in index_rows})} 种）\n\n{head}{rows}\n",
        encoding="utf-8")
    print(f"装配完成 → {target}（{len(index_rows)} 段 / "
          f"{len({r[2] for r in index_rows})} 种语言）")
    print(f"对照表 → {out_dir / 'INDEX.md'}")


def cmd_verify(args) -> None:
    work = Path(args.out)
    doc = load_work(work)
    problems = []
    seen: dict[str, int] = {}
    for s in doc["segments"]:
        if s["kind"] != "text":
            continue
        L, src, dst = s["lang"], s["source"], s["translation"] or ""
        seen[L["code"]] = seen.get(L["code"], 0) + 1
        if not dst.strip():
            problems.append((s["id"], L["code"], "缺译文"))
            continue
        if dst.strip() == src.strip() and len(src) > 40:
            problems.append((s["id"], L["code"], "译文与原文相同"))
        r = script_ratio(dst, L["script"])
        if r < 0.5:
            problems.append((s["id"], L["code"],
                             f"文字系统不符（{L['script']} 占比 {r:.0%}）"))
        if len(src) > 200 and len(dst) < 0.25 * len(src):
            problems.append((s["id"], L["code"], f"长度异常（{len(dst)}/{len(src)}）"))
        if re.search(r"(抱歉|无法|作为.{0,6}(AI|模型|助手))", dst[:80]):
            problems.append((s["id"], L["code"], "疑似拒译/说明文字"))
    dup = {k: v for k, v in seen.items() if v > 1}
    print(f"正文段 {sum(seen.values())}，语种 {len(seen)} 种"
          + (f"，重复语种 {len(dup)} 个" if dup else "，无重复"))
    if problems:
        print(f"问题 {len(problems)} 条：")
        for pid, code, why in problems[:40]:
            print(f"  #{pid:03d} [{code}] {why}")
        if args.strict:
            sys.exit(1)
    else:
        print("抽检通过：无缺段、无占位、无文字系统错配。")



def cmd_reassign(args) -> None:
    """把指定段改派到池内尚未使用的语种（模型做不好的语种换掉）。"""
    work = Path(args.out)
    doc = load_work(work)
    ids = {int(x) for x in args.ids.replace(" ", "").split(",") if x}
    used = {s["lang"]["code"] for s in doc["segments"] if s.get("lang")}
    pool = [x for x in LANGS if not args.same_script or True]
    if args.same_script:
        targets = [("", "", "", "")]
    rnd = random.Random(args.seed)
    cand = [x for x in pool if x[0] not in used]
    if args.codes:
        wanted = [c.strip() for c in args.codes.split(",") if c.strip()]
        cand = [BY_CODE[c] for c in wanted if c in BY_CODE]
    if len(cand) < len(ids):
        sys.exit(f"可用语种不足：需要 {len(ids)}，池内剩 {len(cand)}")
    rnd.shuffle(cand)
    for cid, (code, zh, nat, sc) in zip(sorted(ids), cand):
        for s in doc["segments"]:
            if s["id"] == cid:
                if s["kind"] != "text":
                    sys.exit(f"#{cid} 不是正文段")
                old = s["lang"]["code"]
                s["lang"] = {"code": code, "zh": zh, "native": nat, "script": sc}
                s["translation"] = None
                s.pop("error", None)
                print(f"  #{cid:03d} {old} → {code} ({zh})")
    save_work(work, doc)
    print("改派完成；接着跑 translate --ids ... --force --no-cache")

# ---------------------------------------------------------------- CLI

def main() -> None:
    ap = argparse.ArgumentParser(description="分段随机多语种翻译流水线")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prepare", help="切段 + 分配语种")
    p.add_argument("input")
    p.add_argument("-o", "--out", required=True, help="工作目录")
    p.add_argument("--seed", type=int, default=20261122)
    p.add_argument("--min-chars", type=int, default=0, help="合并短于此长度的段")
    p.add_argument("--keep-headings", action="store_true", help="标题行也当正文翻译")
    p.add_argument("--only", default="", help="仅用这些 code，逗号分隔")
    p.add_argument("--exclude-script", default="", help="排除这些文字系统，如 Hani,Latn")
    p.add_argument("--allow-repeat", action="store_true")
    p.set_defaults(func=cmd_prepare)

    p = sub.add_parser("translate", help="调模型逐段翻译")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--model", default="")
    p.add_argument("--base", default="")
    p.add_argument("--key", default="")
    p.add_argument("--no-cache", action="store_true", help="忽略缓存，强制重译")
    p.add_argument("--ids", default="", help="只处理这些段号，逗号分隔")
    p.add_argument("--force", action="store_true", help="配合 --ids 重译已有译文")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--max-chunk", type=int, default=0,
                   help="单次请求的原文上限字符数，0=不切块")
    p.set_defaults(func=cmd_translate)

    p = sub.add_parser("assemble", help="装配成品 + 对照表")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--title", default="")
    p.add_argument("--name", default="", help="输出文件名（不含 .multi.txt）")
    p.add_argument("--tag-format", default="〔{native} · {code}〕",
                   help="语种标记行模板，可用 {native} {zh} {code}")
    p.add_argument("--allow-missing", action="store_true")
    p.set_defaults(func=cmd_assemble)

    p = sub.add_parser("reassign", help="把指定段改派到未使用的语种")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--ids", required=True, help="段号，逗号分隔")
    p.add_argument("--codes", default="", help="指定目标语种 code，逗号分隔")
    p.add_argument("--same-script", action="store_true")
    p.add_argument("--seed", type=int, default=20261122)
    p.set_defaults(func=cmd_reassign)

    p = sub.add_parser("verify", help="抽检")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--strict", action="store_true", help="有问题即非零退出")
    p.set_defaults(func=cmd_verify)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()