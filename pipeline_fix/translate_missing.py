
import json, os, re, sys, time
import requests

BASE = "https://cssmapi.fun/v1"
KEY = os.environ.get("CSSM_KEY", "")
MODEL = "deepseek-v4.1-flash"

SYS = """你是文学译者，正在补译弗吉尼亚·伍尔夫《星期一或星期二》短篇集中缺失的两篇。
伍尔夫这两篇是实验性的散文诗：句子短促、意象跳跃、标点被用来控制呼吸。译文要求：
1. 逐句译，不增不减，不解释，不加注。
2. 保留原文的破折号、省略号、分号所制造的停顿；不要为了通顺把短句合并成长句。
3. 原文没有分段的地方不要擅自分段；原文用空行分隔的地方保留空行。
4. 用现代汉语书面语，不用方言、不用网络语、不用四字成语堆砌。
5. 只输出译文，不要任何说明。"""


def call(src, tries=3):
    last = ""
    for k in range(tries):
        try:
            r = requests.post(BASE + "/chat/completions",
                              headers={"Authorization": "Bearer " + KEY},
                              json={"model": MODEL, "stream": True, "temperature": 0.4,
                                    "messages": [{"role": "system", "content": SYS},
                                                 {"role": "user", "content": src}]},
                              timeout=300, stream=True)
            if r.status_code != 200:
                last = f"HTTP {r.status_code} {r.text[:120]}"
                time.sleep(3 + 4 * k)
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
            return "".join(out).strip()
        except Exception as e:                                    # noqa: BLE001
            last = f"{type(e).__name__} {e}"
            time.sleep(3 + 4 * k)
    raise RuntimeError(last)


def split(src, n=6000):
    """Cut on paragraph or sentence ends, never mid-sentence."""
    out, cur = [], ""
    for para in re.split(r"(\n\n+)", src):
        if len(cur) + len(para) > n and cur:
            out.append(cur)
            cur = para.lstrip("\n")
        else:
            cur += para
    if cur.strip():
        out.append(cur)
    return out


if __name__ == "__main__":
    srcs = {"星期一或星期二": open("scratch/audit/monday_src.txt", encoding="utf-8").read(),
            "蓝与绿": open("scratch/audit/green_src.txt", encoding="utf-8").read()}
    res = {}
    for k, v in srcs.items():
        parts = split(v)
        got = []
        for i, p in enumerate(parts):
            t0 = time.time()
            z = call(p)
            got.append(z)
            print(f"{k} {i+1}/{len(parts)} {len(p)}->{len(z)} {time.time()-t0:.0f}s", flush=True)
        res[k] = "\n\n".join(got)
    json.dump(res, open("scratch/audit/monday_zh.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for k, v in res.items():
        print(k, len(v))
