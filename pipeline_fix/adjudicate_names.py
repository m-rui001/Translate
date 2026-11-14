
"""Ask a model which near-identical Chinese names are the same person.

The scanner is deliberately loose: it proposes pairs that differ by at most two
characters and share almost every character. Whether a pair is one person written
two ways, two different people, or a name plus the next word is a judgement call that
needs the sentence, which is what this pass supplies.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests

BASE = "https://cssmapi.fun/v1"
KEY = os.environ.get("CSSM_KEY", "")
MODEL = "deepseek-v4.1-flash"

SYS = """你是中文译本的校勘编辑。下面每一组给出两个写法不同的中文专名，以及各自在译文中的一处上下文。
判断它们是不是同一个人/地点/事物：
- same：同一实体，只是译名写法不统一（含音译字不同、多一个字少一个字）。
- diff：两个不同的实体（例如父子、两个不同的人）。
- artifact：较少见的那个其实不是专名，而是"专名+下一个字"之类的切分错误，或普通词语。
只输出 JSON 数组，每项形如 {"i":0,"verdict":"same","keep":"A"}，keep 填 A 表示以第一个写法为准，B 表示以第二个为准。不要输出解释。"""


def ask(batch):
    lines = []
    for i, r in enumerate(batch):
        lines.append(f'{i}. A="{r["major"]}"（{r["n_major"]}次） 上下文：{r["ctx_major"]}')
        lines.append(f'   B="{r["minor"]}"（{r["n_minor"]}次） 上下文：{r["ctx_minor"]}')
    user = "\n".join(lines)
    for k in range(3):
        try:
            resp = requests.post(BASE + "/chat/completions",
                                 headers={"Authorization": "Bearer " + KEY},
                                 json={"model": MODEL, "stream": True, "temperature": 0,
                                       "messages": [{"role": "system", "content": SYS},
                                                    {"role": "user", "content": user}]},
                                 timeout=180, stream=True)
            if resp.status_code != 200:
                time.sleep(2 + 3 * k)
                continue
            out = []
            for line in resp.iter_lines():
                if not line or not line.startswith(b"data: "):
                    continue
                d = line[6:]
                if d == b"[DONE]":
                    break
                try:
                    j = json.loads(d)
                except Exception:
                    continue
                out.append(j["choices"][0]["delta"].get("content") or "")
            txt = "".join(out)
            m = re.search(r"\[.*\]", txt, re.S)
            if not m:
                continue
            return json.loads(m.group(0))
        except Exception:                                        # noqa: BLE001
            time.sleep(2 + 3 * k)
    return []


def main():
    data = json.load(open("scratch/audit/name_pairs.json", encoding="utf-8"))
    jobs = []
    for book, pairs in data.items():
        for i in range(0, len(pairs), 8):
            jobs.append((book, i, pairs[i:i + 8]))
    print("batches", len(jobs), flush=True)

    def run(job):
        book, start, batch = job
        res = ask(batch)
        out = []
        for r in res:
            try:
                i = int(r.get("i"))
            except Exception:
                continue
            if i < 0 or i >= len(batch):
                continue
            out.append({"major": batch[i]["major"], "minor": batch[i]["minor"],
                        "verdict": r.get("verdict", ""), "keep": r.get("keep", "A")})
        return book, out

    results = {}
    with ThreadPoolExecutor(8) as ex:
        for book, out in ex.map(run, jobs):
            results.setdefault(book, []).extend(out)
    json.dump(results, open("scratch/audit/name_verdicts.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    same = sum(1 for v in results.values() for r in v if r["verdict"] == "same")
    print("pairs", sum(len(v) for v in results.values()), "same", same)


if __name__ == "__main__":
    main()
