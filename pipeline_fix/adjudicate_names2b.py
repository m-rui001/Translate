"""Second opinion with the pair order reversed; a verdict that flips is not applied."""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm
from adjudicate_names2 import SYSTEM, batches


def main():
    rows = [r for r in json.load(open("scratch/name_verdicts2.json", encoding="utf-8")) if r["same"]]
    cands = {(r["book"], r["major"], r["minor"]): r for r in
             json.load(open("scratch/name_cands2.json", encoding="utf-8"))}
    items = []
    for r in rows:
        c = cands[(r["book"], r["major"], r["minor"])]
        items.append({"book": r["book"], "major": r["minor"], "minor": r["major"],
                      "n_major": c["n_minor"], "n_minor": c["n_major"],
                      "ctx_major": c["ctx_minor"], "ctx_minor": c["ctx_major"]})
    print("recheck", len(items), flush=True)

    def work(grp):
        lines = ["%d. 甲：%s ｜乙：%s ｜甲上下文：%s ｜乙上下文：%s"
                 % (k, r["major"], r["minor"], r["ctx_major"][:70], r["ctx_minor"][:70])
                 for k, r in enumerate(grp, 1)]
        txt = llm.chat([{"role": "system", "content": SYSTEM},
                        {"role": "user", "content": "\n".join(lines)}],
                       max_tokens=900, temperature=0.1)
        d = llm.extract_json(txt)
        got = {x.get("i"): x for x in (d.get("v") or []) if isinstance(x, dict)}
        out = []
        for k, r in enumerate(grp, 1):
            x = got.get(k) or {}
            if (x.get("a") or "").strip() != r["major"] or (x.get("b") or "").strip() != r["minor"]:
                continue
            out.append({"book": r["book"], "major": r["minor"], "minor": r["major"],
                        "same": bool(x.get("same")), "why": x.get("why", "")})
        return out

    res = llm.pool(list(batches(items)), work, threads=12)
    stable = []
    for r in res:
        if isinstance(r, Exception):
            continue
        stable += [x for x in r if x["same"]]
    json.dump(stable, open("scratch/name_verdicts2_stable.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("stable", len(stable), "of", len(items))
    for x in sorted(stable, key=lambda y: -y["n_major"])[:25]:
        print("  %-20s %s <- %s" % (x["book"][:20], x["major"], x["minor"]))


if __name__ == "__main__":
    main()
