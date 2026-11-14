"""源文对读审校：逐段比对原文与译文，只报确凿错误，输出可机械替换的修订。

用法：
  python pipeline_fix/audit_run.py --limit 20 --out scratch/audit_pilot.jsonl
  python pipeline_fix/audit_run.py --threads 24 --out scratch/audit_full.jsonl
断点续跑：已出现在 out 里的 key 会跳过。
每条 issue 必须给出原文的逐字引用，引用对不上就丢弃——这是防止模型编造的主闸门。
"""
import argparse, glob, json, os, sys, threading, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm

SYSTEM = """你是资深文学翻译审校，母语中文。给你一段原文和它的译文（一一对应），
你只报告**确凿的错误**，不提风格偏好。

可报的类型：
- 误译：意思译错、主宾颠倒、否定反了
- 漏译：原文成句的内容没译
- 增译：译文出现原文没有的实质内容
- 硬译：中文不成句、搭配不通、读者要回读才懂
- 专名：人名地名前后不一或与常见译法冲突
- 数字：年代、数量、年龄、金额译错
- 文白夹杂：叙述里突然出现文言虚词堆叠（"遂""乃""矣""焉"作句读），与全篇语体冲突
- 标点：引号不配对、对话缺引号、句末连用两个句号

不要报：用词偏好、句序调整、可读但不同于你的译法、原文本身歧义。

输出严格 JSON：
{"issues":[{"src":"原文里逐字复制的片段，不超过80字","zh":"译文里逐字复制的片段，不超过40字","type":"误译","fix":"改后的中文，只改 zh 这一处","why":"不超过15字"}]}
要求：
1. src 必须原样出现在给你的原文里（逐字，含标点），不许改写、不许翻译。
2. zh 必须原样出现在给你的译文里（逐字，含标点）。
3. fix 只替换 zh 那一段，前后文不动。
4. 没有确凿错误就输出 {"issues":[]}。宁可漏报，不可误报。
5. 最多 8 条。"""

# 诗歌类另行处理，不进入本流程
SKIP_BOOKS = {"faust", "neuegedichte", "stundenbuch", "betrachtung", "jedermann",
              "torundtod", "hungerkuenstler"}


def pairs():
    out = []
    for plan in sorted(glob.glob("work_*/*/chunks/c*.json")):
        root = os.path.dirname(os.path.dirname(plan))
        cid = os.path.basename(plan)[:-5]
        book = root.replace("\\", "/").split("/")[-1]
        if book in SKIP_BOOKS:
            continue
        try:
            d = json.load(open(plan, encoding="utf-8"))
        except Exception:
            continue
        chs = d.get("chunks") or []
        for i, f in enumerate(sorted(glob.glob(root + "/out/" + cid + "/*/final.txt"))):
            if i >= len(chs):
                continue
            src = "\n".join(b.get("text", "") for b in chs[i])
            zh = open(f, encoding="utf-8").read()
            if len(zh) < 200 or not src.strip():
                continue
            out.append({"key": "%s|%s|%02d" % (root.replace("\\", "/"), cid, i),
                        "book": book, "src": src, "zh": zh,
                        "path": f.replace("\\", "/")})
    return out


def norm(s):
    return " ".join(s.split())


def run_one(it):
    msg = [{"role": "system", "content": SYSTEM},
           {"role": "user", "content": "【原文】\n" + it["src"] + "\n\n【译文】\n" + it["zh"]}]
    issues = None
    for attempt in range(2):
        txt = llm.chat(msg, max_tokens=2000, temperature=0.2)
        try:
            d = llm.extract_json(txt)
            issues = d.get("issues") if isinstance(d, dict) else None
            if issues is None:
                raise ValueError("no issues key")
            break
        except Exception:
            issues = []
    srcn, zhn = norm(it["src"]), norm(it["zh"])
    kept = []
    for x in issues:
        s = norm(x.get("src") or "")
        zh, fix = (x.get("zh") or ""), (x.get("fix") or "")
        if not s or not zh or not fix or zh == fix:
            continue
        if s not in srcn:          # 原文引用对不上 → 丢弃
            continue
        if zh not in zhn:          # 译文引用对不上 → 丢弃
            continue
        kept.append({"src": s, "zh": zh, "fix": fix,
                     "type": x.get("type", ""), "why": x.get("why", "")})
    return {"key": it["key"], "book": it["book"], "issues": kept, "path": it["path"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--threads", type=int, default=24)
    ap.add_argument("--out", default="scratch/audit.jsonl")
    ap.add_argument("--book", default="")
    a = ap.parse_args()

    items = pairs()
    if a.book:
        items = [i for i in items if i["book"] == a.book]
    if a.limit:
        items = items[:a.limit]
    done = set()
    if os.path.exists(a.out):
        for line in open(a.out, encoding="utf-8"):
            try:
                done.add(json.loads(line)["key"])
            except Exception:
                pass
    todo = [i for i in items if i["key"] not in done]
    print("todo", len(todo), "done", len(done), flush=True)
    if not todo:
        return
    t0 = time.time()
    fh = open(a.out, "a", encoding="utf-8")

    def on_done(d, total):
        if d % 50 == 0 or d == total:
            el = time.time() - t0
            print("  %d/%d  %.0fs  %.1f/min  eta %.0fmin"
                  % (d, total, el, d / el * 60, (total - d) / (d / el) / 60), flush=True)

    res = llm.pool(todo, run_one, threads=a.threads, on_done=on_done)
    for r in res:
        if isinstance(r, Exception):
            continue
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    fh.close()
    tot = sum(len(r["issues"]) for r in res if not isinstance(r, Exception))
    err = sum(1 for r in res if isinstance(r, Exception))
    print("segments", len(res), "issues", tot, "errors", err)


if __name__ == "__main__":
    main()
