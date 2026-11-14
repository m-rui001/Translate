"""Unified client for the local free-model gateway (CLIProxyAPI on :8317).

Features: model pool with fallback, retries, streaming-free JSON calls,
per-call logging, and token accounting. OpenAI-compatible protocol.
"""
from __future__ import annotations

import json
import os
import random
import threading
import time
import urllib.error
import urllib.request

BASE = os.environ.get("FREEAI_BASE", "http://127.0.0.1:8317")
KEY = os.environ.get("FREEAI_KEY", "")
LOG_PATH = os.environ.get("FREEAI_LOG", "work/llm_calls.jsonl")

_log_lock = threading.Lock()
_sem_lock = threading.Lock()
_sems: dict[str, threading.Semaphore] = {}

# concurrent-request budget per model family (Google free tier rejects bursts)
CONCURRENCY = {"gemini": 2, "default": 8}


def _sem(model: str) -> threading.Semaphore:
    key = "gemini" if model.startswith("gemini") else "default"
    with _sem_lock:
        if key not in _sems:
            _sems[key] = threading.Semaphore(CONCURRENCY[key])
        return _sems[key]


class LLMError(RuntimeError):
    pass


def _post(path: str, payload: dict, timeout: float = 900.0) -> dict:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        BASE + path,
        data=body,
        headers={
            "Authorization": "Bearer " + KEY,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _log(rec: dict) -> None:
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with _log_lock, open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


def chat(
    messages: list[dict],
    model: str | None = None,
    models: list[str] | None = None,
    temperature: float = 0.75,
    max_tokens: int = 8000,
    retries: int = 3,
    tag: str = "",
    timeout: float = 240.0,
    with_meta: bool = False,
):
    """Call a model pool with fallback across backends. Returns (text, model[, meta])."""
    pool = models or ([model] if model else DEFAULT_POOL)
    last_err = None
    for attempt in range(retries):
        for m in pool:
            t0 = time.time()
            try:
                if ":" in m:  # extra OpenAI-compatible provider (openox/longcat/intern)
                    import providers
                    return providers.chat(
                        messages, m, temperature=temperature, max_tokens=max_tokens,
                        tag=tag, retries=4, timeout=timeout, with_meta=with_meta)
                if m.startswith("gemini-"):  # Google AI Studio direct
                    return gemini(messages, m, temperature=temperature, max_tokens=max_tokens,
                                  tag=tag, timeout=timeout, retries=1, with_meta=with_meta)
                sem = _sem(m)
                sem.acquire()
                try:
                    d = _post(
                        "/v1/chat/completions",
                        {"model": m, "messages": messages, "temperature": temperature,
                         "max_tokens": max_tokens},
                        timeout=timeout,
                    )
                finally:
                    sem.release()
                msg = d["choices"][0]["message"]
                content = msg.get("content") or ""
                if not content.strip():
                    raise LLMError("empty content")
                fin = d["choices"][0].get("finish_reason")
                rec = {"ts": round(time.time(), 1), "tag": tag, "model": m,
                       "secs": round(time.time() - t0, 1), "usage": d.get("usage"),
                       "finish": fin, "out_chars": len(content)}
                _log(rec)
                return (content, m, rec) if with_meta else (content, m)
            except Exception as e:  # noqa: BLE001
                last_err = e
                _log({"ts": round(time.time(), 1), "tag": tag, "model": m,
                      "error": str(e)[:300], "secs": round(time.time() - t0, 1)})
                continue
        # back off harder when every model in the pool just failed (provider outage
        # or shared rate-limit cooldown) — hammering only extends the outage window
        time.sleep(min(20, 5 * (attempt + 1)) + random.random() * 3)
    raise LLMError(f"all models failed for tag={tag}: {last_err}")


# ─────────────────────────────────────────── Gemini (Google AI Studio, direct)
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_BASE = "https://generativelanguage.googleapis.com/v1beta"
PROXY = os.environ.get("LOCAL_PROXY", "http://127.0.0.1:7897")


def gemini(messages, model, temperature=0.7, max_tokens=8000, tag="", timeout=600.0,
           retries=2, with_meta=False):
    """Call Gemini through the local proxy (HK egress is unsupported by Google)."""
    import requests

    system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
    contents = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]}
        for m in messages
        if m["role"] != "system"
    ]
    body = {
        "contents": contents,
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    last = None
    for attempt in range(retries):
        t0 = time.time()
        sem = _sem(model)
        sem.acquire()
        try:
            r = requests.post(
                f"{GOOGLE_BASE}/models/{model}:generateContent",
                headers={"x-goog-api-key": GOOGLE_KEY, "Content-Type": "application/json"},
                json=body,
                proxies={"http": PROXY, "https": PROXY},
                timeout=timeout,
            )
            d = r.json()
            if "error" in d:
                raise LLMError(str(d["error"])[:300])
            cand = d["candidates"][0]
            parts = cand.get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
            if not text.strip():
                raise LLMError("empty gemini content")
            _log({"ts": round(time.time(), 1), "tag": tag, "model": model,
                  "secs": round(time.time() - t0, 1), "usage": d.get("usageMetadata"),
                  "finish": cand.get("finishReason"), "out_chars": len(text)})
            return (text, model, {"finish": cand.get("finishReason"), "usage": d.get("usageMetadata")}) if with_meta else (text, model)
        except Exception as e:  # noqa: BLE001
            last = e
            _log({"ts": round(time.time(), 1), "tag": tag, "model": model,
                  "error": str(e)[:300], "secs": round(time.time() - t0, 1)})
            time.sleep(2 + attempt * 2)
        finally:
            sem.release()
    raise LLMError(f"gemini failed for tag={tag}: {last}")
