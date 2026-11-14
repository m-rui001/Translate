
"""Take the regional and internet register out of the narration.

The complaint is specific and mechanical: 甭, 咋, 啥, 这号, 那号, 得嘞, 这当儿,
那光景, 得了吧 and 压根 belong to a northern storyteller's voice, not to a translated
nineteenth-century novel. This pass finds the paragraphs that contain them and asks
for the smallest edit that removes them, keeping every other word.

Guards: the paragraph count must match, the length may not move more than 15%, and a
reply that rewrites the sentence instead of the phrase is rejected.
"""
from __future__ import annotations

import difflib
import html
import json
import os
import re
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor

import requests

BASE = "https://cssmapi.fun/v1"
KEY = os.environ.get("CSSM_KEY", "")
MODEL = "deepseek-v4.1-flash"

MARK = ["甭管", "甭提", "甭说", "甭", "咋", "啥", "这号", "那号", "得嘞",
        "这当儿", "那光景", "得了吧", "我说岔了", "压根", "捅娄子", "瞎琢磨"]

SYS = """你是中文译本的文字编辑。下面几段译文里混进了北方口语和网络化的说法，
与全书书面语不协调。请做**最小改动**：
- 只替换方言词、口语套话、时代错位的表达（例如 甭→别、咋→怎么、啥→什么、
  这号→这种、得嘞→好、这当儿→这时、压根→根本、得了吧→算了）。
- 其余的字词、语序、标点、专名、数字一律不动。
- 不增删任何信息，不解释，不改写句子，不调整段落。
输出与输入段数相同的段落，用空行分隔，不要编号，不要任何说明。"""


def call(paras: list[str], tries: int = 3) -> list[str] | None:
    user = "\n\n".join(paras)
    for k in range(tries):
        try:
            r = requests.post(BASE + "/chat/completions",
                              headers={"Authorization": "Bearer " + KEY},
                              json={"model": MODEL, "stream": True, "temperature": 0.2,
                                    "messages": [{"role": "system", "content": SYS},
                                                 {"role": "user", "content": user}]},
                              timeout=180, stream=True)
            if r.status_code != 200:
                time.sleep(2 + 3 * k)
                continue
            out = []
            for line in r.iter_lines():
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
            txt = "".join(out).strip()
            got = [p.strip() for p in re.split(r"\n\s*\n", txt) if p.strip()]
            if len(got) != len(paras):
                return None
            for a, b in zip(paras, got):
                if not (0.85 <= len(b) / max(1, len(a)) <= 1.15):
                    return None
                if difflib.SequenceMatcher(None, a, b).ratio() < 0.72:
                    return None
                if b.count("“") != a.count("“") or b.count("”") != a.count("”"):
                    return None
            return got
        except Exception:                                        # noqa: BLE001
            time.sleep(2 + 3 * k)
    return None


TEXT = re.compile(r"(<p[^>]*>)(.*?)(</p>)", re.S)


def process(path: str) -> dict:
    book = os.path.basename(path).replace("（坟头草译）.epub", "")
    zin = zipfile.ZipFile(path)
    items = [(i, zin.read(i.filename)) for i in zin.infolist()]
    zin.close()
    # locate flagged paragraphs
    jobs = []          # (item index, match span start, text)
    for ii, (info, data) in enumerate(items):
        if not info.filename.endswith(".xhtml"):
            continue
        s = data.decode("utf-8")
        for m in TEXT.finditer(s):
            t = html.unescape(m.group(2))
            if any(w in t for w in MARK) and len(t) >= 20:
                jobs.append((ii, m.start(2), m.end(2), t))
    if not jobs:
        return {"book": book, "paras": 0, "changed": 0}
    # batch four at a time
    batches = [jobs[i:i + 4] for i in range(0, len(jobs), 4)]

    def run(b):
        got = call([j[3] for j in b])
        return b, got

    results = []
    with ThreadPoolExecutor(12) as ex:
        for b, got in ex.map(run, batches):
            if got:
                results.extend(zip(b, got))
    # write back, per file, right to left
    by_file = {}
    for (ii, a, z, old), new in results:
        by_file.setdefault(ii, []).append((a, z, new))
    changed = 0
    log = []
    for ii, edits in by_file.items():
        info, data = items[ii]
        s = data.decode("utf-8")
        for a, z, new in sorted(edits, reverse=True):
            old = html.unescape(s[a:z])
            if old != new:
                log.append({"book": book, "old": old, "new": new})
            s = s[:a] + html.escape(new, quote=False) + s[z:]
            changed += 1
    if log:
        with open("scratch/audit/register_log.jsonl", "a", encoding="utf-8") as fh:
            for row in log:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        items[ii] = (info, s.encode("utf-8"))
    if changed:
        tmp = path + ".tmp"
        with zipfile.ZipFile(tmp, "w") as z:
            for info, data in items:
                z.writestr(info, data)
        os.replace(tmp, path)
    return {"book": book, "paras": len(jobs), "changed": changed}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    only = sys.argv[1:]
    tot_p = tot_c = 0
    for f in sorted(os.listdir("out")):
        if not f.endswith(".epub"):
            continue
        if only and not any(o in f for o in only):
            continue
        r = process(os.path.join("out", f))
        tot_p += r["paras"]
        tot_c += r["changed"]
        if r["paras"]:
            print(f'{r["book"][:24]:26s} flagged={r["paras"]:4d} changed={r["changed"]:4d}',
                  flush=True)
    print("TOTAL flagged", tot_p, "changed", tot_c)


if __name__ == "__main__":
    main()
