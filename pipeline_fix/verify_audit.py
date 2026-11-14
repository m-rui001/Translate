"""审校结果二次核验：逐条判 keep/reject，压掉风格性改动与反向改错。

输入 audit jsonl，输出 verified jsonl（同 key，只留 keep 的 issue）。
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm

SYSTEM = """你是译稿终审。下面给你原文、译文，以及别人提出的若干处修改。
你的任务是**挑掉不该改的**：多数提议是多余的、只改文风、或改完反而错。
逐条判断，只有同时满足以下三条才 keep：
1. 原译确有错误（意思错、漏、多、中文不成句、专名数字错）；
2. 提议的改法确实修掉了这个错误；
3. 改法本身没有引入新错误，也没有把通顺的句子改差。

只改文风、同义替换、语气微调、把对的改成另一种说法 —— 一律 reject。
如果提议把全书统一的专名改成另一种写法（如"多塞特"改成"杜塞特"），一律 reject。

输出严格 JSON：{"v":[{"i":0,"keep":true,"why":"不超过12字"}]}
i 是提议的序号（从 0 开始）。"""

_CACHE = {}


def load_pair(key):
    root, cid, idx = key.split("|")
    plan = os.path.join(root, "chunks", cid + ".json")
    if plan not in _CACHE:
        _CACHE[plan] = json.load(open(plan, encoding="utf-8")).get("chunks") or []
    chs = _CACHE[plan]
    i = int(idx)
    src = "\n".join(b.get("text", "") for b in chs[i]) if i < len(chs) else ""
    zh = open(os.path.join(root, "out", cid, "c%02d" % i, "final.txt"), encoding="utf-8").read()
    return src, zh


def one(rec):
    src, zh = load_pair(rec["key"])
    items = rec["issues"]
    lines = []
    for i, x in enumerate(items):
        lines.append("[%d] 类型:%s 原译:「%s」 改为:「%s」 理由:%s 原文:「%s」"
                     % (i, x.get("type", ""), x["zh"], x["fix"], x.get("why", ""), x.get("src", "")[:120]))
    msg = [{"role": "system", "content": SYSTEM},
           {"role": "user", "content": "【原文】\n" + src + "\n\n【译文】\n" + zh
            + "\n\n【待审提议】\n" + "\n".join(lines)}]
    txt = llm.chat(msg, max_tokens=1200, temperature=0.1)
    try:
        d = llm.extract_json(txt)
        v = d.get("v") or []
    except Exception:
        v = []
    keep = {}
    for x in v:
        if isinstance(x, dict) and isinstance(x.get("i"), int) and x.get("keep"):
            keep[x["i"]] = x.get("why", "")
    out = []
    for i, x in enumerate(items):
        if i in keep:
            y = dict(x)
            y["vwhy"] = keep[i]
            out.append(y)
    return {"key": rec["key"], "book": rec["book"], "path": rec.get("path", ""),
            "issues": out, "n_in": len(items)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", default="scratch/audit_full.jsonl")
    ap.add_argument("--out", default="scratch/audit_verified.jsonl")
    ap.add_argument("--threads", type=int, default=24)
    a = ap.parse_args()
    recs = []
    for line in open(a.inp, encoding="utf-8"):
        r = json.loads(line)
        if r.get("issues"):
            recs.append(r)
    done = set()
    if os.path.exists(a.out):
        for line in open(a.out, encoding="utf-8"):
            try:
                done.add(json.loads(line)["key"])
            except Exception:
                pass
    todo = [r for r in recs if r["key"] not in done]
    print("records", len(recs), "todo", len(todo), flush=True)
    fh = open(a.out, "a", encoding="utf-8")
    import time
    t0 = time.time()

    def on_done(d, total):
        if d % 50 == 0 or d == total:
            print("  %d/%d %.0fs" % (d, total, time.time() - t0), flush=True)

    res = llm.pool(todo, one, threads=a.threads, on_done=on_done)
    for r in res:
        if isinstance(r, Exception):
            print("ERR", r, flush=True)
            continue
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    fh.close()
    ok = [r for r in res if not isinstance(r, Exception)]
    print("kept", sum(len(r["issues"]) for r in ok), "of", sum(r["n_in"] for r in ok))


if __name__ == "__main__":
    main()
