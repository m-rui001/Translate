"""Unified paragraph-level polish engine, driven by the local gateway.

Not a re-translation: every paragraph must come back as the same paragraph,
same index, same information, with only the faults fixed. Hard validation:

  * the response must contain exactly n numbered lines, [0]..[n-1] in order;
  * no line may be empty; no line may be absurdly short or long;
  * placeholder markers (⟦ ⟧ 『 』) must survive byte-identical in count.

Anything that fails falls back to a retry, then to the original text, so the
pass can only ever improve the manuscript.

Concurrency: this used to point at cssmapi.fun with a 150-wide global cap. That
endpoint stopped answering /chat/completions on 2026-10-26 (the gateway still
listed models; the backend hung), and the only writer left standing in a 41-model
sweep was the local gateway at 127.0.0.1:8317 -- which measures ~6 concurrent
requests before it starts queueing. So the cap is 6 here, not 150; raising it
turns a slow pass into a hung one.
"""
from __future__ import annotations

import json
import difflib
import os
import random
import re
import threading
import time

import requests

# Endpoint comes from the same providers entry llm.py uses, so a future move needs
# one edit in models.json rather than two in code. The local gateway at 127.0.0.1:8317
# was the previous choice and died on 2026-10-26 (upstream RegionError, port gone);
# xiaomi measured 0.99 ok/s at 4-way concurrency, the best of what survived.
_PROV = json.load(open(r"C:\Users\hp\.pi\agent\models.json",
                       encoding="utf-8"))["providers"]["xiaomi"]
BASE = _PROV["baseUrl"].rstrip("/")
KEY = _PROV["apiKey"]
MODEL = "mimo-v2.6-flash"
TIMEOUT = 600.0

_local = threading.local()
_log_lock = threading.Lock()
LOG_PATH = "E:/Translate/work_polish2/calls.jsonl"

# The local gateway queues past ~6 in flight rather than refusing outright, so a wide
# cap does not fail fast -- it just stalls every request behind the queue. Seven books
# still run in parallel, each with its own pool, and they all queue on this one gate.
GLOBAL_CAP = int(os.environ.get("POLISH_GLOBAL_CONCURRENCY", "6"))
_gate = threading.Semaphore(GLOBAL_CAP)

CJK = re.compile(r"[\u4e00-\u9fff]")


# The backend's content filter sometimes leaves a canned apology glued to the
# end of an otherwise good paragraph. It is not part of the book.
REFUSAL = re.compile(
    r"(?:\s|\n)*(?:Sorry,?\s*I\s*(?:can(?:'|’)t|cannot)\s*(?:respond|help)"
    r"|I\s+apologi[sz]e|我无法(?:回答|协助|帮助)|抱歉[，,]\s*我(?:无法|不能))[^\n]*"
    r"\s*$", re.I)


def strip_refusal(s: str) -> str:
    """Drop a trailing canned refusal left by the content filter."""
    prev = None
    while prev != s:
        prev = s
        s = REFUSAL.sub("", s).strip()
    return s


def split_sentences(p: str, budget=420) -> list[str]:
    """Split one long paragraph into sentence-safe chunks, for retry."""
    parts = re.findall(r"[^。！？…”』」]*[。！？…”』」]+|[^。！？…”』」]+$", p)
    out, cur = [], ""
    for s in parts:
        if cur and len(cur) + len(s) > budget:
            out.append(cur)
            cur = s
        else:
            cur += s
    if cur:
        out.append(cur)
    return out or [p]


def _ok_one(b: str, a: str, terms: list[str] | None) -> bool:
    """Per-paragraph acceptance: same substance, same terms, same markers."""
    if CJK.search(b):
        if not CJK.search(a):
            return False
        if len(a) < 0.55 * len(b) or len(a) > 1.75 * len(b):
            return False
        if len(a) < 0.75 * len(b) and len(b) > 40:
            return False
    for m in MARKERS:
        if b.count(m) != a.count(m):
            return False
    if terms:
        for h in terms:
            if h in b and h not in a:
                return False
    if b.rstrip()[-1:] in END_PUNCT and a.rstrip()[-1:] not in END_PUNCT:
        return False
    for o, q in (("“", "”"), ("「", "」"), ("『", "』")):
        if b.count(o) == b.count(q) != a.count(o):
            return False
    return True


def polish_para(zh: str, src: str | None, term_note: str = "",
                terms: list[str] | None = None) -> str:
    """Polish one paragraph, splitting it by sentence if the first try fails.

    Very long paragraphs trip the backend's content filter, which truncates the
    answer and appends an apology. Sentence-sized requests do not, so the
    paragraph is recovered piece by piece and rejoined verbatim. Anything that
    still does not pass keeps its original wording.
    """
    got, status = polish_batch([(zh, src)], term_note, terms, allow_split=False)
    if status == "ok":
        return got[0]
    if len(zh) < 300:
        return zh
    chunks = split_sentences(zh)
    if len(chunks) < 2:
        return zh
    out = []
    for c in chunks:
        g, st = polish_batch([(c, None)], term_note, terms, allow_split=False)
        out.append(g[0] if st == "ok" else c)
    joined = "".join(out)
    return joined if _ok_one(zh, joined, terms) else zh


def _session() -> requests.Session:
    s = getattr(_local, "s", None)
    if s is None:
        s = requests.Session()
        s.mount("https://", requests.adapters.HTTPAdapter(
            pool_connections=4, pool_maxsize=4, max_retries=0))
        _local.s = s
    return s


def _log(rec: dict) -> None:
    try:
        with _log_lock:
            os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


SYS = """你是资深中文文学编辑，长期从事严肃文学译稿的出版前精校。你的活是修稿，不是重译。

铁律：
一、逐段一一对应。输入几段，输出几段，段落编号 [n] 原样保留，不得合并、拆分、增删段落。
二、不得增删信息。不许补主语、不许替作者解释、不许加形容词、不许删掉重复与迟疑。
三、不许改写。原文已经译对的地方，一个字都不动。只有确实有毛病的地方才动。
四、只修这几类毛病：语句不通、搭配错误、翻译腔（「被」「进行」「对于」「使得」「作为一个」式句型）、
    指代不清、语气前后不匀、标点误用、虚词堆叠（同一句里「究竟/无论/又或者/诚然/然而/于是/遂/便」出现两次以上）。
五、不追求「更流畅」「更优美」。读起来顺不顺不是你的事，准不准、通不通才是。
六、原文的长句结构要保住。原作者一口气写下来的长句，不要替他把句子拆短。
七、特殊标记 ⟦ ⟧ 『 』 及其中的内容一律原样保留，位置和数量都不得变。

输出格式：每段一行，严格写作
[n] 修订后的整段文字
不要任何解释、不要标题、不要前言后语。"""


def build_prompt(pairs: list[tuple[str, str | None]], term_note: str = "") -> str:
    """pairs: [(zh, source or None), ...] already numbered from 0.

    Source lines carry an asterisk in the index ([3*]) so the model can never
    mistake them for the paragraph it is supposed to rewrite, and so a
    careless echo of both lines does not look like a duplicate index.
    """
    blocks = []
    for i, (zh, src) in enumerate(pairs):
        if src:
            blocks.append(f"[{i}*] FR: {src}\n[{i}] ZH: {zh}")
        else:
            blocks.append(f"[{i}] {zh}")
    head = ("下面是一部中译稿的若干段落。请逐段润色精修，段数必须与输入完全相同。\n"
            "带 * 的 FR 行只是原文备查，不要输出。只输出 [n] 译文行。\n")
    if term_note:
        head += term_note + "\n"
    return (head + "只输出修订结果，格式 `[n] 修订后的段落`，n 与输入一致。\n\n"
            + "\n\n".join(blocks))


LINE = re.compile(r"^\s*\[(\d+)\]\s*(.*)$")
SRC_LINE = re.compile(r"^\s*\[\d+\*\]")
# the model sometimes keeps the prompt's own label in the body
LABEL = re.compile(r"^\s*(?:ZH|FR|译文|原文|中文|English)\s*[:：]\s*")


def parse(text: str, n: int) -> list[str] | None:
    """Accept `[n] body` lines. Body may continue on following lines."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    got: dict[int, list[str]] = {}
    order: list[int] = []
    cur = None
    for ln in lines:
        if SRC_LINE.match(ln):
            continue                      # echoed source line, ignore
        ln = re.sub(r"^\s*\[\d+\*\]\s*", "", ln) if ln.lstrip().startswith("[") else ln
        m = LINE.match(ln)
        if m:
            idx = int(m.group(1))
            if idx in got:
                return None            # duplicated index
            cur = idx
            got[idx] = [m.group(2)]
            order.append(idx)
        elif cur is not None:
            if ln.strip():
                got[cur].append(ln.strip())
    if order != list(range(n)):
        return None
    out = []
    for i in range(n):
        body = "\n".join(got[i]).strip()
        body = LABEL.sub("", body)
        if not body:
            return None
        out.append(body)
    return out


MARKERS = ("⟦", "⟧", "『", "』")


END_PUNCT = "。！？…”』」·"


def check(before: list[str], after: list[str], terms: list[str] | None = None) -> str | None:
    """Return a reason string when the polish is not trustworthy."""
    # the model sometimes copies the neighbouring paragraph instead of editing
    # this one, which silently duplicates prose and loses the original
    for i in range(1, len(after)):
        if after[i] == after[i - 1] and before[i] != before[i - 1]:
            return f"duplicated paragraph at {i}"
    if terms:
        b_all = "\n".join(before)
        a_all = "\n".join(after)
        lost = [h for h in terms if h in b_all and h not in a_all]
        if lost:
            return "term dropped: " + "/".join(lost[:4])
    for m in MARKERS:
        b = sum(p.count(m) for p in before)
        a = sum(p.count(m) for p in after)
        if b != a:
            return f"marker {m} {b}->{a}"
    for b, a in zip(before, after):
        if not CJK.search(b):
            continue          # verse separators, dropped capitals, * lines
        if not CJK.search(a):
            return "no chinese"
        if len(a) < 0.55 * len(b) or len(a) > 1.75 * len(b):
            return f"length {len(b)}->{len(a)}"
        # a paragraph may not silently lose a lot of content
        if len(a) < 0.75 * len(b) and len(b) > 40:
            return f"shrink {len(b)}->{len(a)}"
        # nor may it lose its closing punctuation, which is what truncation
        # by the content filter looks like
        if b.rstrip()[-1:] in END_PUNCT and a.rstrip()[-1:] not in END_PUNCT:
            return f"unterminated {len(b)}->{len(a)}"
        # a balanced paragraph must stay balanced: polish sometimes turns a
        # closing  ” into a stray  “ and quietly breaks the dialogue
        for o, q in (("“", "”"), ("「", "」"), ("『", "』")):
            if b.count(o) == b.count(q) != a.count(o):
                return f"quotes {o}{q}"
        # a paragraph must remain recognisably the same paragraph; a very low
        # overlap means the model substituted other text for it
        if len(b) > 15:
            r = difflib.SequenceMatcher(None, b, a, autojunk=False).ratio()
            if r < 0.62:
                return f"rewritten {len(b)}->{len(a)} r={r:.2f}"
    return None


def call(messages, temperature=0.3, max_tokens=8000, retries=5) -> str:
    body = {"model": MODEL, "messages": messages,
            "max_tokens": max_tokens, "temperature": temperature}
    last = None
    for att in range(retries):
        t0 = time.time()
        try:
            _gate.acquire()
            try:
                r = _session().post(
                    BASE + "/chat/completions",
                    headers={"Content-Type": "application/json",
                             "Authorization": "Bearer " + KEY},
                    json=body, timeout=TIMEOUT)
            finally:
                _gate.release()
            dt = time.time() - t0
            if r.status_code != 200:
                last = f"HTTP{r.status_code}"
                _log({"tag": "http", "code": r.status_code, "dt": round(dt, 1)})
                time.sleep(min(20, 1.5 * (att + 1) + random.random() * 2))
                continue
            j = json.loads(r.content.decode("utf-8"))
            txt = j["choices"][0]["message"].get("content") or ""
            _log({"tag": "ok", "dt": round(dt, 1),
                  "usage": j.get("usage", {})})
            return txt
        except Exception as e:            # noqa: BLE001  (SSL, proxy, timeout)
            last = type(e).__name__
            _log({"tag": "err", "err": type(e).__name__,
                  "dt": round(time.time() - t0, 1)})
            time.sleep(min(20, 1.5 * (att + 1) + random.random() * 2))
    raise RuntimeError(f"api failed after {retries}: {last}")


def polish_batch(pairs: list[tuple[str, str | None]],
                 term_note: str = "", terms: list[str] | None = None,
                 allow_split: bool = True
                 ) -> tuple[list[str], str]:
    """Polish one batch. Returns (paragraphs, status). status in ok/kept/fail.

    Paragraphs with no Chinese at all (verse rules, dropped capitals, lone
    asterisks) are held back and reinserted verbatim: the model tends to skip
    them, which used to make whole batches unparseable.
    """
    keep = [i for i, (p, _) in enumerate(pairs) if CJK.search(p)]
    live = [pairs[i] for i in keep]
    originals = [p for p, _ in pairs]
    if not live:
        return originals, "ok"            # nothing to polish, not a failure

    before = [p for p, _ in live]
    prompt = build_prompt(live, term_note)
    for attempt in range(4):
        temp = 0.25 if attempt == 0 else 0.15 + 0.1 * attempt
        try:
            raw = call([{"role": "system", "content": SYS},
                        {"role": "user", "content": prompt}],
                       temperature=temp,
                       max_tokens=min(16000, 800 + 2 * sum(len(p) for p in before)))
        except Exception:
            continue
        got = parse(raw, len(before))
        if got is None:
            continue
        stripped = [strip_refusal(g) for g in got]
        if stripped != got:
            continue          # filter cut the answer short; retry, then split
        why = check(before, stripped, terms)
        if why:
            continue
        out = list(originals)
        for slot, zh in zip(keep, stripped):
            out[slot] = zh
        return out, "ok"
    # whole batch rejected: fall back to one paragraph at a time, which lets the
    # sentence splitter recover the paragraphs the content filter truncates
    if not allow_split:
        return originals, "kept"
    out = list(originals)
    for slot in keep:
        out[slot] = polish_para(originals[slot], pairs[slot][1], term_note, terms)
    return out, "ok"


# ─────────────────────────────────────────────────────────────── worklist
def batch(items: list[dict], char_budget=2600, max_paras=10) -> list[list[dict]]:
    """Group paragraph records into request-sized batches."""
    out, cur, n = [], [], 0
    for it in items:
        z = len(it["zh"])
        if cur and (n + z > char_budget or len(cur) >= max_paras):
            out.append(cur)
            cur, n = [], 0
        cur.append(it)
        n += z
    if cur:
        out.append(cur)
    return out


def run(units: list[tuple[str, list[dict]]], outdir: str, workers=150,
        resume=True, verbose=True, tb=None) -> dict:
    """units: [(uid, [{'zh':..., 'src':...}, ...]), ...] one unit = one batch.

    tb: optional EN->ZH termbase; canonical names found in a batch are pinned in
    the prompt and verified on the way out, so polish can never rename anyone.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    inv = None
    if tb:
        import terms as T
        inv = T.invert(tb)

    os.makedirs(outdir, exist_ok=True)
    todo = []
    for uid, items in units:
        p = os.path.join(outdir, uid.replace("/", "_") + ".json")
        if resume and os.path.exists(p):
            continue
        todo.append((uid, items, p))

    stat = {"ok": 0, "kept": 0, "cached": len(units) - len(todo), "fail": 0}
    t0 = time.time()
    lock = threading.Lock()

    def work(uid, items, path):
        try:
            pairs = [(it["zh"], it.get("src")) for it in items]
            note, hits = "", None
            if tb:
                import terms as T
                blob = "".join(it["zh"] for it in items)
                hits = T.guard_terms(blob, tb)
                note = T.term_prompt(hits, inv)
            got, status = polish_batch(pairs, note, hits)
        except Exception as e:                       # noqa: BLE001
            with lock:
                stat["fail"] += 1
            _log({"tag": "unitfail", "uid": uid, "err": str(e)[:120]})
            return uid, "fail"
        json.dump({"uid": uid, "zh": got, "status": status},
                  open(path, "w", encoding="utf-8"), ensure_ascii=False)
        return uid, status

    if verbose:
        print(f"  {len(todo)} batches to polish "
              f"({stat['cached']} cached), workers={workers}", flush=True)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(work, u, i, p) for u, i, p in todo]
        for k, f in enumerate(as_completed(futs), 1):
            uid, status = f.result()
            with lock:
                stat[status] = stat.get(status, 0) + 1
            if verbose and k % 25 == 0:
                dt = time.time() - t0
                rate = k / dt
                print(f"  {k}/{len(todo)}  ok={stat['ok']} kept={stat['kept']} "
                      f"fail={stat['fail']}  {dt:.0f}s  {rate:.1f} batch/s  "
                      f"eta={(len(todo)-k)/max(rate,1e-9):.0f}s", flush=True)
    stat["secs"] = round(time.time() - t0, 1)
    return stat
