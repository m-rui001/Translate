"""Extra OpenAI-compatible providers (from ~/.pi/agent/models.json) + Gemini direct.

Model ids are namespaced:
    ox:<model>   openox.tech reseller (Gemini / GPT / DeepSeek)
    lc:<model>   LongCat
    ia:<model>   intern-ai
    gemini-<x>   Google AI Studio direct (needs the US-routed proxy)
    anything else -> the local free gateway on :8317
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
except Exception:
    pass

_sems: dict[str, threading.Semaphore] = {}
_sem_lock = threading.Lock()
# openox.tech drops long connections when hammered; keep its in-flight count low
LIMITS = {"ox": 2, "lc": 2, "ia": 2, "tc": 4, "mm": 4, "qw": 8, "km": 3, "gl": 3, "ds": 8}
# bailian rejects a temperature field on some models
NO_TEMPERATURE = {"km"}

# openox enforces a rolling rate limit; pace ourselves instead of eating 429s
_pace_lock = threading.Lock()
_pace_last = {"t": 0.0}
MIN_INTERVAL = float(os.environ.get("OX_PACE_SECONDS", "3"))


def _sem(ns: str) -> threading.Semaphore:
    with _sem_lock:
        if ns not in _sems:
            _sems[ns] = threading.Semaphore(LIMITS.get(ns, 3))
        return _sems[ns]

MODELS_JSON = r"C:\Users\hp\.pi\agent\models.json"
PROXY = os.environ.get("LOCAL_PROXY", "http://127.0.0.1:7897")
_TIMEOUT = float(os.environ.get("PROVIDER_TIMEOUT", "600"))

_cfg = None


def _providers() -> dict:
    global _cfg
    if _cfg is None:
        _cfg = json.load(open(MODELS_JSON, encoding="utf-8"))["providers"]
    return _cfg


def _resolve(model: str):
    """-> (base_url, api_key, real_model, use_proxy) or None for gateway models."""
    if ":" not in model:
        return None
    ns, real = model.split(":", 1)
    p = _providers()
    mapping = {"ox": "openox gemini", "oxg": "openox-gpt61", "oxd": "openox-deepseek",
               "lc": "longcat", "ia": "intern-ai", "css": "cssmapi", "css2": "cssmapi2",
               "css3": "cssmapi3", "css4": "cssmapi4",
               # Alibaba Model Studio: one key, several independent families
               "qw": "bailian", "km": "bailian", "gl": "bailian", "ds": "bailian"}
    key = mapping.get(ns)
    if not key or key not in p:
        return None
    prov = p[key]
    base = prov["baseUrl"].rstrip("/")
    # openox serves several models behind one host; pick the right key per model
    if ns == "ox":
        for name, pp in p.items():
            if name.startswith("openox") and any(
                    m.get("id") == real for m in pp.get("models", [])):
                base, key_name = pp["baseUrl"].rstrip("/"), name
                prov = p[key_name]
                break
    # cssmapi.fun answers from mainland directly; routing it through the US proxy only
    # adds a hop that dies whenever the proxy is not running.
    return base, prov["apiKey"], real, ns in ("ox", "oxg", "oxd", "lc", "ia")


def _json_utf8(r):
    """cssmapi omits charset; requests would decode UTF-8 bytes as latin-1."""
    import json as _json
    try:
        return _json.loads(r.content.decode("utf-8"))
    except Exception:
        return r.json()


def chat(messages, model, temperature=0.7, max_tokens=8000, tag="", retries=2,
         timeout=None, with_meta=False):
    if model.startswith("mm:"):
        return minimax(messages, model[3:], temperature=temperature, max_tokens=max_tokens,
                       tag=tag, retries=retries, timeout=timeout or 300.0,
                       with_meta=with_meta)
    if model.startswith("tc:"):
        return tokencome(messages, model[3:], temperature=temperature, max_tokens=max_tokens,
                         tag=tag, retries=retries, timeout=timeout or 240.0,
                         with_meta=with_meta)
    if model.startswith("ah:"):
        return aihorde(messages, model[3:], temperature=temperature, max_tokens=max_tokens,
                       tag=tag, retries=retries, timeout=timeout or _TIMEOUT,
                       with_meta=with_meta)
    target = _resolve(model)
    if target is None:
        raise ValueError("not a namespaced provider model: " + model)
    base, key, real, use_proxy = target
    ns = model.split(":", 1)[0]
    sem = _sem(ns)
    body = {"model": real, "messages": messages, "max_tokens": max_tokens}
    if ns not in NO_TEMPERATURE:
        body["temperature"] = temperature
    # bailian wraps reasoning models; glm-5.3 refuses enable_thinking=False
    if ns in ("qw", "ds", "km", "gl"):
        body["enable_thinking"] = ns == "gl"
    last = None
    if ns == "ox":
        with _pace_lock:
            gap = time.time() - _pace_last["t"]
            if gap < MIN_INTERVAL:
                time.sleep(MIN_INTERVAL - gap)
            _pace_last["t"] = time.time()

    for attempt in range(retries):
        t0 = time.time()
        sem.acquire()
        try:
            # openox is reachable both directly and via the local proxy; try both,
            # because the proxy occasionally drops long-lived connections.
            routes = [{"http": "", "https": ""}]
            if use_proxy:
                routes += [{"http": PROXY, "https": PROXY}, {"http": "", "https": ""}]
            r = None
            err = None
            for pr in routes:
                try:
                    r = requests.post(f"{base}/chat/completions",
                                      headers={"Authorization": "Bearer " + key,
                                               "Content-Type": "application/json"},
                                      json=body, proxies=pr,
                                      timeout=(10, timeout or _TIMEOUT))
                    break
                except Exception as e:  # noqa: BLE001
                    err = e
                    continue
            if r is None:
                raise err
            d = _json_utf8(r)
            if "error" in d and not d.get("choices"):
                raise RuntimeError(str(d["error"])[:300])
            ch = d["choices"][0]
            text = (ch.get("message") or {}).get("content") or ""
            if not text.strip():
                raise RuntimeError("empty content")
            rec = {"ts": round(time.time(), 1), "tag": tag, "model": model,
                   "secs": round(time.time() - t0, 1), "usage": d.get("usage"),
                   "finish": ch.get("finish_reason"), "out_chars": len(text)}
            _log(rec)
            return (text, model, rec) if with_meta else (text, model)
        except Exception as e:  # noqa: BLE001
            last = e
            _log({"ts": round(time.time(), 1), "tag": tag, "model": model,
                  "error": str(e)[:200], "secs": round(time.time() - t0, 1)})
            msg = str(e)
            if "upstream" in msg or "nonjson" in msg or "Expecting value" in msg:
                time.sleep(2 + attempt * 2)
                continue
            if "429" in msg:
                time.sleep(20 + attempt * 20)
            elif "Expecting value" in msg or "Connection aborted" in msg:
                time.sleep(8 + attempt * 8)
            else:
                time.sleep(3 + attempt * 4)
        finally:
            sem.release()
    raise RuntimeError(f"provider failed for {model}: {last}")


def _log(rec):
    path = os.environ.get("FREEAI_LOG", "E:/Translate/work/llm_calls.jsonl")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


# ───────────────────────────────────── AI Horde (keyless volunteer grid)
AIHORDE_BASE = "https://oai.aihorde.net/v1"
AIHORDE_KEY = os.environ.get("AIHORDE_KEY", "0000000000")  # anonymous sentinel


def aihorde(messages, model, temperature=0.7, max_tokens=8000, tag="", timeout=600.0,
            retries=1, with_meta=False):
    """Last-resort keyless fallback. Volunteer queue: slow and inconsistent."""
    body = {"model": model, "messages": messages, "temperature": temperature,
            "max_tokens": max_tokens}
    last = None
    for attempt in range(retries):
        t0 = time.time()
        try:
            r = requests.post(f"{AIHORDE_BASE}/chat/completions",
                              headers={"Authorization": "Bearer " + AIHORDE_KEY,
                                       "Content-Type": "application/json"},
                              json=body, timeout=timeout)
            d = _json_utf8(r)
            if "error" in d and not d.get("choices"):
                raise RuntimeError(str(d["error"])[:200])
            ch = d["choices"][0]
            text = (ch.get("message") or {}).get("content") or ""
            if not text.strip():
                raise RuntimeError("empty content")
            rec = {"ts": round(time.time(), 1), "tag": tag, "model": "ah:" + model,
                   "secs": round(time.time() - t0, 1), "usage": d.get("usage"),
                   "finish": ch.get("finish_reason"), "out_chars": len(text)}
            _log(rec)
            return (text, "ah:" + model, rec) if with_meta else (text, "ah:" + model)
        except Exception as e:  # noqa: BLE001
            last = e
            _log({"ts": round(time.time(), 1), "tag": tag, "model": "ah:" + model,
                  "error": str(e)[:200], "secs": round(time.time() - t0, 1)})
            time.sleep(3 + attempt * 3)
    raise RuntimeError(f"aihorde failed for {model}: {last}")


# ───────────────────────── tokencome.org (free, fast, reasoning-heavy)
# Models JSON calls the base "https://tokencome.org" but the real path is /v1.
# Reasoning eats the whole output budget on long inputs, so callers must keep
# chunks short and we force thinking off on every request.
_prov = json.load(open(MODELS_JSON, encoding="utf-8"))["providers"]
TOKENCOME_KEY = _prov.get("tokencome", {}).get("apiKey", "")
TOKENCOME_BASE = "https://tokencome.org/v1"


def tokencome(messages, model, temperature=0.7, max_tokens=8000, tag="", timeout=240.0,
              retries=3, with_meta=False):
    body = {"model": model, "messages": messages, "temperature": temperature,
            "max_tokens": max_tokens, "enable_thinking": False}
    last = None
    for attempt in range(retries):
        t0 = time.time()
        sem = _sem("tc")
        sem.acquire()
        try:
            r = None
            err = None
            for pr in ({"http": "", "https": ""},
                       {"http": PROXY, "https": PROXY}):
                try:
                    r = requests.post(f"{TOKENCOME_BASE}/chat/completions",
                                      headers={"Authorization": "Bearer " + TOKENCOME_KEY,
                                               "Content-Type": "application/json"},
                                      json=body, proxies=pr, timeout=(10, timeout),
                                      verify=False)
                    break
                except Exception as e:  # noqa: BLE001
                    err = e
                    continue
            if r is None:
                raise err
            d = _json_utf8(r)
            if "error" in d and not d.get("choices"):
                raise RuntimeError(str(d["error"])[:200])
            ch = d["choices"][0]
            m = ch.get("message") or {}
            text = (m.get("content") or "").strip()
            # a reasoning-only response is useless: the model burned its budget thinking
            if not text or len(text) < 20:
                raise RuntimeError(f"empty/short content (reasoning={len(m.get('reasoning_content') or '')})")
            rec = {"ts": round(time.time(), 1), "tag": tag, "model": "tc:" + model,
                   "secs": round(time.time() - t0, 1), "usage": d.get("usage"),
                   "finish": ch.get("finish_reason"), "out_chars": len(text)}
            _log(rec)
            return (text, "tc:" + model, rec) if with_meta else (text, "tc:" + model)
        except Exception as e:  # noqa: BLE001
            last = e
            _log({"ts": round(time.time(), 1), "tag": tag, "model": "tc:" + model,
                  "error": str(e)[:200], "secs": round(time.time() - t0, 1)})
            time.sleep(2 + attempt * 3)
        finally:
            sem.release()
    raise RuntimeError(f"tokencome failed for {model}: {last}")


# ─────────────────────────────── MiniMax (api.minimax.cn)
# M3 puts its scratchpad into the content field; only M3.1-Flash is usable.
MINIMAX_KEY = json.load(open(MODELS_JSON, encoding="utf-8"))["providers"]["cc-switch-mini-max"]["apiKey"]
MINIMAX_BASE = "https://api.minimax.cn/v1"


def minimax(messages, model, temperature=0.7, max_tokens=8000, tag="", timeout=300.0,
            retries=3, with_meta=False):
    body = {"model": model, "messages": messages, "temperature": temperature,
            "max_tokens": max_tokens, "enable_thinking": False}
    last = None
    for attempt in range(retries):
        t0 = time.time()
        sem = _sem("mm")
        sem.acquire()
        try:
            r = requests.post(f"{MINIMAX_BASE}/chat/completions",
                              headers={"Authorization": "Bearer " + MINIMAX_KEY,
                                       "Content-Type": "application/json"},
                              json=body, proxies={"http": "", "https": ""},
                              timeout=(10, timeout))
            d = _json_utf8(r)
            if "error" in d and not d.get("choices"):
                raise RuntimeError(str(d["error"])[:200])
            ch = d["choices"][0]
            text = ((ch.get("message") or {}).get("content") or "").strip()
            if not text or len(text) < 20:
                raise RuntimeError("empty/short content")
            rec = {"ts": round(time.time(), 1), "tag": tag, "model": "mm:" + model,
                   "secs": round(time.time() - t0, 1), "usage": d.get("usage"),
                   "finish": ch.get("finish_reason"), "out_chars": len(text)}
            _log(rec)
            return (text, "mm:" + model, rec) if with_meta else (text, "mm:" + model)
        except Exception as e:  # noqa: BLE001
            last = e
            _log({"ts": round(time.time(), 1), "tag": tag, "model": "mm:" + model,
                  "error": str(e)[:200], "secs": round(time.time() - t0, 1)})
            time.sleep(2 + attempt * 3)
        finally:
            sem.release()
    raise RuntimeError(f"minimax failed for {model}: {last}")
