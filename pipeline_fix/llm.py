"""并行 LLM 客户端：8317 本地路由网关为主通道（fill-first 多上游）。

2026-10-29：cssmapi 停用；opencode(10000) 上游超时；8317 网关（CLIProxyAPI）聚合
opencode / modelscope / siliconflow / openrouter / cloudflare 多上游并自动 failover。
实测 modelscope 的 `ms-qwen3.8-flash` 可用（2.8s、出干净中文），故定为主模型；
`cf-llama4-scout` 作兜底。统一非流式请求。
"""
import json, os, random, threading, time, urllib.request, urllib.error

GATE_URL = "http://127.0.0.1:8317/v1/chat/completions"
GATE_KEY = os.environ.get("FREEAI_KEY", "")

MODELS = ["cf-llama4-scout", "ms-qwen3.8-flash"]
DEFAULT_MODEL = MODELS[0]

CSSM_URL = "https://cssmapi.fun/v1/chat/completions"
CSSM_KEY = os.environ.get("CSSM_KEY", "")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
FENCE = chr(96) * 3


def _post(body, timeout, url, key):
    req = urllib.request.Request(
        url, json.dumps(body).encode(),
        {"Authorization": "Bearer " + key, "Content-Type": "application/json",
         "User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    c = (d.get("choices") or [{}])[0].get("message", {}).get("content")
    if not c:
        raise RuntimeError("empty content")
    return c


def chat(messages, model=None, max_tokens=4096,
         temperature=0.3, timeout=300, tries=4):
    models = [model] if model else MODELS
    last = None
    for m in models:
        body = {"model": m, "stream": False, "messages": messages,
                "max_tokens": max_tokens, "temperature": temperature}
        for i in range(tries):
            try:
                return _post(body, timeout, GATE_URL, GATE_KEY)
            except urllib.error.HTTPError as e:
                txt = e.read()[:200].decode("utf8", "ignore")
                last = "HTTP%d %s" % (e.code, txt)
                if e.code in (401, 402, 403, 404):
                    break
            except Exception as e:
                last = repr(e)[:160]
            time.sleep(min(20, (2 ** i) * 0.5 + random.random()))
    raise RuntimeError("all models failed: " + str(last))


def pool(items, fn, threads=8, on_done=None):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    res = [None] * len(items)
    done = 0
    with ThreadPoolExecutor(threads) as ex:
        futs = {ex.submit(fn, it): i for i, it in enumerate(items)}
        for f in as_completed(futs):
            i = futs[f]
            try:
                res[i] = f.result()
            except Exception as e:
                res[i] = e
            done += 1
            if on_done:
                on_done(done, len(items))
    return res


def extract_json(s):
    s = s.strip()
    if s.startswith(FENCE):
        s = s.split("\n", 1)[-1]
        if s.rstrip().endswith(FENCE):
            s = s.rstrip()[:-3]
    for i, ch in enumerate(s):
        if ch in "{[":
            depth = 0
            for j in range(i, len(s)):
                if s[j] in "{[":
                    depth += 1
                elif s[j] in "}]":
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(s[i:j + 1])
                        except Exception:
                            break
    raise ValueError("no json: " + s[:120])
