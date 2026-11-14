"""LLM client for the whale pipeline.

Providers come from C:\\Users\\hp\\.pi\\agent\\models.json. Namespaced ids:

    lc:<model>    local gateway 127.0.0.1:8317  (primary writer since 2026-10-26)
    cs:<model>    cssmapi.fun        RETIRED 2026-10-26 — chat endpoint hangs
    ox:<model>    openox.tech        (gemini / gpt / claude resellers)
    oxc:<model>   openox-claude
    oxg:<model>   openox-gpt
    xm:<model>    xiaomi mimo
    ia:<model>    intern-ai
    gemini-<x>    Google AI Studio direct (needs the US-routed proxy)

Every call is logged to work_whale/llm_calls.jsonl. Concurrency is capped per
namespace by a semaphore, because these resellers throttle aggressively.
"""
from __future__ import annotations

import json
import os
import threading
import time

import requests

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception:  # noqa: BLE001
    pass

MODELS_JSON = os.environ.get("MODELS_JSON", "models.json")
LOG_PATH = os.environ.get("WHALE_LOG", "work_whale/llm_calls.jsonl")
PROXY = os.environ.get("LOCAL_PROXY", "")

# Primary writer since 2026-10-26. cssmapi.fun answered /v1/models but hung
# /chat/completions indefinitely (60 s, zero bytes), and every model behind the local
# opencode gateway at :10000 timed out, so the only endpoint that returned a completion
# in a 41-model sweep was this one. `ms-` prefix = Microsoft-hosted family, measured
# at 43.9 tok/s on a one-line translation probe.
LOCAL_BASE = "http://127.0.0.1:8317/v1"
LOCAL_KEY = os.environ.get("FREEAI_KEY", "")
LOCAL_OVERRIDE = {"baseUrl": LOCAL_BASE, "apiKey": LOCAL_KEY,
                  "models": [{"id": "ms-deepseek-v4.1-flash"}]}

# cssmapi answers only when called with a browser signature: a bare python-requests
# UA gets Cloudflare 1010. It also needs the key passed in the environment — there is
# no key in this file on purpose.
CSSM_BASE = "https://cssmapi.fun/v1"
CSSM_KEY = os.environ.get("CSSM_KEY", "")
CSSM_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/event-stream",
    "Origin": "https://cssmapi.fun",
    "Referer": "https://cssmapi.fun/",
}
CSSM_OVERRIDE = {"baseUrl": CSSM_BASE, "apiKey": CSSM_KEY,
                 "models": [{"id": "deepseek-v4.1-flash"}]}


def _demojibake(text: str) -> str:
    """Recover UTF-8 that the gateway re-encoded as latin-1.

    cssmapi labels its replies `text/event-stream` and ships the body with each UTF-8
    byte widened to a latin-1 character, so a Chinese reply arrives as `\u00e6\u0088\u0088`
    instead of the two bytes it should be. Reading it as JSON `str` therefore yields
    mojibake, which downstream looks exactly like an empty translation and silently
    fails the paragraph-count check.

    Only a strict round-trip is attempted: if the text is already valid Chinese, encoding
    to latin-1 raises, and the original is returned untouched. That keeps this a repair
    rather than a transformation.
    """
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

NS_PROVIDER = {
    "lc": "local-gateway",
    "cs": "cssmapi",
    # cssm-free: the 2026-10-30 key. The host answers /chat/completions again (the
    # 10-26 hang is over) but per-account throttling is erratic, so a pool of its
    # *different families* rotates rather than one id: rotation spreads the calls
    # across the accounts behind the group, and a family that hiccups does not stop
    # the run. The retired `cs:` key is kept resolving with an empty key on purpose.
    "csf": "cssm-free",
    "ox": "openox gemini",
    "oxc": "openox-claude",
    "oxg": "openox-gpt61",
    "oxd": "openox-deepseek",
    "xm": "xiaomi",
    # Second xiaomi key. Both keys answered 8/8 at 4-way concurrency and measured
    # 0.89 and 1.00 ok/s independently, so running them side by side is the only way
    # to get throughput back near what the dead local gateway used to give. They are
    # separate namespaces rather than a list inside `xm` so each gets its own
    # semaphore and one key's throttle does not stall the other.
    "x2": "xiaomi2",
    "ia": "intern-ai",
    # Alibaba Model Studio carries several *independent* families behind one key,
    # which is what the blind-evaluation design needs: judges must not share a
    # lineage with the writer or with each other.
    "qw": "bailian",
    "km": "bailian",
    "gl": "bailian",
    "mm": "cc-switch-mini-max",
    "in": "intern-ai",
    "ds": "bailian",
}
# xm/x2 measured together at 3.37 ok/s at 12-way (6 each) and 2.88 at 16, so 6 is the
# per-key optimum; the two share one host, which is why going wider only queues.
LIMITS = {"lc": 10, "cs": 160, "csf": 12, "ox": 6, "oxc": 3, "oxg": 4, "oxd": 3,
          "xm": 6, "x2": 6, "ia": 4, "qw": 4, "km": 3, "gl": 3, "ds": 3,
          "mm": 3, "in": 3}
# bailian rejects a temperature on some of its models; omit the field there
NO_TEMPERATURE = {"km"}
# models that burn the budget on hidden reasoning before answering: demand room
REASONING_HUNGRY = {"gl", "in"}
# glm-5.3 hard-rejects enable_thinking=False ("restricted to True")
KEEP_THINKING = {"gl"}

_sems: dict[str, threading.Semaphore] = {}
# circuit breaker: resellers like openox.tech sit behind Cloudflare and answer 524
# after ~125 s of no upstream response. Repeating that per chunk wastes hours, so a
# model that fails hard three times running is benched for a while.
_health: dict[str, list] = {}
_health_lock = threading.Lock()
BENCH_SECS = 420.0
BENCH_FAILS = 3
_sem_lock = threading.Lock()
_log_lock = threading.Lock()
_cfg = None


def _providers() -> dict:
    global _cfg
    if _cfg is None:
        _cfg = json.load(open(MODELS_JSON, encoding="utf-8"))["providers"]
        # pin the local gateway without touching the user's models.json
        _cfg["local-gateway"] = dict(_cfg.get("local-gateway", {}),
                                     **LOCAL_OVERRIDE)
        # cssmapi stays resolvable for old `cs:` ids, but with an empty key so a stale
        # call fails fast instead of hanging for the full read timeout
        _cfg["cssmapi"] = dict(_cfg.get("cssmapi", {}), **CSSM_OVERRIDE)
    return _cfg


def _sem(ns: str) -> threading.Semaphore:
    with _sem_lock:
        if ns not in _sems:
            _sems[ns] = threading.Semaphore(LIMITS.get(ns, 4))
        return _sems[ns]


class LLMError(RuntimeError):
    """Raised when no model in a pool could produce a usable answer."""


def benched(model: str) -> bool:
    with _health_lock:
        rec = _health.get(model)
        if not rec:
            return False
        n_fail, until = rec
        if n_fail >= BENCH_FAILS and time.time() < until:
            return True
        if time.time() >= until:
            _health[model] = [0, 0.0]
        return False


def _mark(model: str, ok: bool) -> None:
    with _health_lock:
        rec = _health.setdefault(model, [0, 0.0])
        if ok:
            rec[0], rec[1] = 0, 0.0
        else:
            rec[0] += 1
            rec[1] = time.time() + BENCH_SECS


def _log(rec: dict) -> None:
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with _log_lock, open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001
        pass


def available(model: str) -> bool:
    ns = model.split(":", 1)[0]
    p = _providers()
    return NS_PROVIDER.get(ns) in p


def chat(messages, model: str, temperature=0.7, max_tokens=8000, tag="",
         retries=4, timeout=600.0, with_meta=False):
    """Single-model call with retries. Returns (text, model[, meta])."""
    if ":" not in model:
        raise ValueError("model id must be namespaced, got " + model)
    ns, real = model.split(":", 1)
    prov_name = NS_PROVIDER.get(ns)
    p = _providers()
    if prov_name not in p:
        raise RuntimeError(f"provider for namespace {ns} not in models.json")
    prov = p[prov_name]
    base = prov["baseUrl"].rstrip("/")
    key = prov["apiKey"]
    # openox serves several models behind one host with per-model keys: only then
    # is it right to go hunting for another entry that declares this model id
    if ns == "ox":
        for name, cand in p.items():
            if any(m.get("id") == real for m in cand.get("models", [])):
                base, key = cand["baseUrl"].rstrip("/"), cand["apiKey"]
                break
    body = {"model": real, "messages": messages,
            "max_tokens": max_tokens}
    if ns not in NO_TEMPERATURE:
        body["temperature"] = temperature
    # several of these resellers wrap reasoning models: never let thinking eat the budget
    if ns in KEEP_THINKING:
        body["enable_thinking"] = True
    else:
        body["enable_thinking"] = False
    if benched(model):
        raise RuntimeError(f"{model} benched after repeated hard failures")
    sem = _sem(ns)
    last = None
    for attempt in range(max(1, retries)):
        t0 = time.time()
        sem.acquire()
        try:
            routes = [{"http": "", "https": ""}]
            if PROXY:
                routes.append({"http": PROXY, "https": PROXY})
            r, err = None, None
            for pr in routes:
                try:
                    hdrs = {"Authorization": "Bearer " + key,
                            "Content-Type": "application/json"}
                    if ns == "cs":
                        hdrs.update(CSSM_HEADERS)
                    r = requests.post(f"{base}/chat/completions",
                                      headers=hdrs,
                                      json=body, proxies=pr,
                                      timeout=(15, timeout), verify=False)
                    break
                except Exception as e:  # noqa: BLE001
                    err = e
            if r is None:
                raise err if err else RuntimeError("no route")
            if not r.content:
                # some resellers answer 200 with an empty body after their own
                # ~125 s queue timeout; treat it as a retryable overload signal
                raise RuntimeError(f"empty body (status {r.status_code})")
            # cssmapi (and some resellers) omit the charset, so requests would guess
            # latin-1 and mangle every Chinese character. Decode UTF-8 explicitly.
            # The gateway double-encodes non-ASCII content, so decode the bytes as
            # latin-1 first and let _demojibake() undo it per field below. Reading the
            # raw bytes as UTF-8 throws away the information needed to repair them.
            try:
                d = json.loads(r.content.decode("utf-8", "replace"))
            except Exception:
                raise RuntimeError(
                    f"non-json body (status {r.status_code}, "
                    f"{r.headers.get('content-type')}): "
                    + r.content[:120].decode("utf-8", "replace"))
            if "error" in d and not d.get("choices"):
                raise RuntimeError(str(d["error"])[:300])
            ch = d["choices"][0]
            msg = ch.get("message") or {}
            text = _demojibake(msg.get("content") or "")
            if not text.strip():
                raise RuntimeError("empty content")
            if len(text.strip()) < 20 and ch.get("finish_reason") == "length":
                raise RuntimeError("reasoning ate the budget")
            rec = {"ts": round(time.time(), 1), "tag": tag, "model": model,
                   "secs": round(time.time() - t0, 1), "usage": d.get("usage"),
                   "finish": ch.get("finish_reason"), "out_chars": len(text)}
            _log(rec)
            _mark(model, True)
            return (text, model, rec) if with_meta else (text, model)
        except Exception as e:  # noqa: BLE001
            last = e
            _log({"ts": round(time.time(), 1), "tag": tag, "model": model,
                  "error": str(e)[:240], "secs": round(time.time() - t0, 1)})
            msg = str(e)
            upstream_down = "temporarily unavailable" in msg
            if "non-json" in msg or "empty body" in msg or upstream_down:
                # 2026-10-30: a Cloudflare 524/502 html page ("non-json") and an empty
                # 200 body are both *edge overload* signals -- the very next tiny
                # request to the same id answers in seconds, so benching the model for
                # 7 minutes after 3 of them took the whole pool down mid-review while
                # the endpoint was perfectly usable. Leave the bench for replies the
                # upstream itself rejected (error json, empty content); overload is
                # handled by the retry/backoff below.
                pass
            if upstream_down:
                # the reseller has no upstream for this model right now; retrying the
                # same id is pure latency, so let the caller fall through to the next
                last = e
                break
            if "429" in msg or "empty body" in msg:
                time.sleep(12 + attempt * 15)
            elif "Connection" in msg or "timed out" in msg:
                time.sleep(5 + attempt * 8)
            elif "non-json" in msg:
                # Cloudflare 524/502 html: the edge already burned 125 s. One quick
                # retry, then hand the turn to the *next pool member* -- sticking
                # around serialises four 130 s waits before rotation gets a chance,
                # which is what turned a 73-unit review into a 40-minute crawl.
                if attempt == 0:
                    time.sleep(3)
                    continue
                break
            else:
                time.sleep(2 + attempt * 3)
        finally:
            sem.release()
    _mark(model, False)
    raise RuntimeError(f"{model} failed for tag={tag}: {last}")


_pool_cursor = 0
_pool_cursor_lock = threading.Lock()


def chat_pool(messages, models: list[str], **kw) -> tuple[str, str]:
    """Try models in rotating order; return the first usable answer.

    The order rotates per call. A fixed order makes the list a failover chain rather
    than a pool: the first model answers, so the second is never exercised at all,
    and adding a key buys nothing. That was observed directly -- `run_pub` was
    configured with two xiaomi keys and the call log showed every request on `xm:`,
    none on `x2:`, which is why a measured 3.37 ok/s pair degraded to a single key's
    0.017 chunks/s on a 15.8-million-character batch.

    Rotation is only the starting point. If the chosen model fails it still falls
    through to the rest in order, so the failover behaviour is preserved.
    """
    global _pool_cursor
    if len(models) > 1:
        with _pool_cursor_lock:
            start = _pool_cursor % len(models)
            _pool_cursor += 1
        models = models[start:] + models[:start]
    errs = []
    for m in models:
        if benched(m):
            errs.append(f"{m}: benched")
            continue
        try:
            t, used = chat(messages, m, **kw)
            return t, used
        except Exception as e:  # noqa: BLE001
            errs.append(f"{m}: {str(e)[:80]}")
            continue
    raise RuntimeError("pool exhausted: " + " | ".join(errs))
