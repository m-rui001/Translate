"""Minimal HTTP-over-Windows-named-pipe client for the Clash Verge / mihomo controller.

Clash Verge runs mihomo with `external-controller: ''` and only a named pipe,
so the REST API is reachable exclusively through that pipe.
"""
from __future__ import annotations

import glob
import json
import os
import sys

PIPE_GLOB = r"\\.\pipe\verge-mihomo-*"
SECRET = "set-your-secret"


def _pipe() -> str:
    hits = glob.glob(PIPE_GLOB)
    if not hits:
        raise SystemExit("no verge-mihomo pipe found")
    return hits[0]


def call(method: str, path: str, body: dict | None = None, timeout: float = 10.0) -> str:
    pipe = _pipe()
    payload = json.dumps(body).encode() if body is not None else b""
    headers = [
        f"{method} {path} HTTP/1.1",
        "Host: localhost",
        f"Authorization: Bearer {SECRET}",
        "Content-Type: application/json",
        f"Content-Length: {len(payload)}",
        "Connection: close",
        "",
        "",
    ]
    req = "\r\n".join(headers).encode() + payload

    f = open(pipe, "r+b", buffering=0)
    f.write(req)
    chunks = []
    while True:
        b = f.read(65536)
        if not b:
            break
        chunks.append(b)
    f.close()
    raw = b"".join(chunks)
    head, _, body_bytes = raw.partition(b"\r\n\r\n")
    # chunked transfer-encoding
    if b"chunked" in head.lower():
        out, rest = b"", body_bytes
        while rest:
            size_line, _, rest = rest.partition(b"\r\n")
            try:
                size = int(size_line.strip() or b"0", 16)
            except ValueError:
                break
            if size == 0:
                break
            out += rest[:size]
            rest = rest[size + 2:]
        body_bytes = out
    return body_bytes.decode("utf-8", errors="replace")


def get(path):
    return call("GET", path)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) == 1:
        d = json.loads(get("/proxies"))["proxies"]
        for name, p in d.items():
            if p.get("type") in ("Selector", "URLTest", "Fallback", "LoadBalance"):
                print(f"[{p['type']}] {name} -> {p.get('now')}  ({len(p.get('all', []))} opts)")
    else:
        print(get(sys.argv[1])[:4000])
