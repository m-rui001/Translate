"""Decide whether two spellings in the same book name the same referent.

Batches of 8 pairs per request with a context window on each side. The model must echo
both spellings back, so a shifted index cannot silently attach the wrong verdict
(that bug once turned 阿托斯 / 阿拉密斯 into "same").
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm

SYSTEM = """下面每一条是同一本书里两个相近的译名，各附一句上下文。
判断它们指的是不是同一个人/地方/事物（即同一个外文名的两种译法）。

判 same 的情形：同一人物的不同音译（波尔托斯/波托斯）、同一地名的不同写法。
判 diff 的情形：两个不同的人物（哪怕名字只差一个字）、亲属称谓、普通词语、
                书名篇名、原文里本就是两个人。

只输出 JSON，每条必须把甲、乙两个名字原样抄回：
{"v":[{"i":1,"a":"甲名","b":"乙名","same":true,"why":"不超过12字"}]}
i 从 1 开始，与题号一致。"""


def batches(items, n=8):
    for i in range(0, len(items), n):
        yield items[i:i + n]


def main():
    rows = json.load(open("scratch/name_cands2.json", encoding="utf-8"))
    out_path = "scratch/name_verdicts2.json"
    done = {}
    if os.path.exists(out_path):
        for r in json.load(open(out_path, encoding="utf-8")):
            done[(r["book"], r["major"], r["minor"])] = r
    todo = [r for r in rows if (r["book"], r["major"], r["minor"]) not in done]
    print("todo", len(todo), "cached", len(done), flush=True)

    def work(items):
        lines = []
        for k, r in enumerate(items, 1):
            lines.append("%d. 甲：%s ｜乙：%s ｜甲上下文：%s ｜乙上下文：%s"
                         % (k, r["major"], r["minor"], r["ctx_major"][:70], r["ctx_minor"][:70]))
        msg = [{"role": "system", "content": SYSTEM},
               {"role": "user", "content": "\n".join(lines)}]
        txt = llm.chat(msg, max_tokens=900, temperature=0.1)
        d = llm.extract_json(txt)
        got = {x.get("i"): x for x in (d.get("v") or []) if isinstance(x, dict)}
        out = []
        for k, r in enumerate(items, 1):
            x = got.get(k) or {}
            if (x.get("a") or "").strip() != r["major"] or (x.get("b") or "").strip() != r["minor"]:
                continue                      # 抄回对不上，整条丢弃
            out.append({"book": r["book"], "major": r["major"], "minor": r["minor"],
                        "n_major": r["n_major"], "n_minor": r["n_minor"],
                        "same": bool(x.get("same")), "why": x.get("why", "")})
        return out

    res = llm.pool(list(batches(todo)), work, threads=12)
    bad = 0
    for r in res:
        if isinstance(r, Exception):
            bad += 1
            continue
        for x in r:
            done[(x["book"], x["major"], x["minor"])] = x
    allrows = list(done.values())
    json.dump(allrows, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    same = [x for x in allrows if x["same"]]
    print("same", len(same), "of", len(allrows), "batch errors", bad)
    for x in sorted(same, key=lambda y: -(y["n_major"] + y["n_minor"]))[:40]:
        print("  %-20s %s(%d) <- %s(%d)" % (x["book"][:20], x["major"], x["n_major"],
                                            x["minor"], x["n_minor"]))


if __name__ == "__main__":
    main()
