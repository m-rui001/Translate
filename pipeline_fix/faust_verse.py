"""Restore the verse lineation of Faust Part One.

The translation is faithful but every verse speech was flattened into one run-on
paragraph, so the page reads as prose. This pass asks the model to put the line breaks
back **without touching a single character**: the gate is that the joined lines must be
byte-identical to the original paragraph. Anything else is discarded.
"""
import argparse, json, os, re, shutil, sys, zipfile
from html import escape, unescape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm

EPUB = "out/浮士德上册（坟头草译）.epub"
SYSTEM = """这是《浮士德》第一部中译。原文是诗体，但排版时被合并成了一整段。
你的任务：把诗体段落还原成原文的分行。

规则：
1. 只插入换行，不得增删或改动任何一个字、一个标点。
2. 分行位置依原文的诗行；中文一行对应原文一行，长短不必整齐。
3. 舞台说明、散文段落（如《晦暗的日子·旷野》《夜·旷野》整场是散文）不要分行，
   verse 填 false。
4. 每行不要带行首行尾空格。

输出严格 JSON：
{"v":[{"i":1,"verse":true,"lines":["第一行","第二行"]}]}
i 从 1 开始，与题号一致。verse 为 false 时 lines 省略。"""


def paras(html):
    return [(m.start(), m.end(), unescape(re.sub(r"<[^>]+>", "", m.group(2))))
            for m in re.finditer(r"<p([^>]*)>(.*?)</p>", html, re.S)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threads", type=int, default=12)
    ap.add_argument("--out", default="scratch/faust_verse.json")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    with zipfile.ZipFile(EPUB) as z:
        files = {n: z.read(n).decode("utf-8") for n in z.namelist() if n.endswith(".xhtml")}
        order = [n for n in z.namelist()]
        raw = {n: z.read(n) for n in order}

    jobs = []
    for name in order:
        if not name.endswith(".xhtml") or name.endswith(("nav.xhtml", "title.xhtml")):
            continue
        for idx, (s, e, text) in enumerate(paras(files[name])):
            if len(text) >= 60 and "\n" not in text:
                jobs.append({"file": name, "idx": idx, "text": text})
    if a.limit:
        jobs = jobs[:a.limit]
    print("paragraphs to judge", len(jobs), flush=True)

    def work(batch):
        lines = ["%d. %s" % (k, j["text"]) for k, j in enumerate(batch, 1)]
        txt = llm.chat([{"role": "system", "content": SYSTEM},
                        {"role": "user", "content": "\n\n".join(lines)}],
                       max_tokens=3000, temperature=0.1)
        d = llm.extract_json(txt)
        got = {x.get("i"): x for x in (d.get("v") or []) if isinstance(x, dict)}
        out = []
        for k, j in enumerate(batch, 1):
            x = got.get(k) or {}
            if not x.get("verse"):
                continue
            ls = [s.strip() for s in (x.get("lines") or []) if s.strip()]
            if len(ls) < 2:
                continue
            if "".join(ls) != j["text"]:      # 改动了字，整条丢弃
                continue
            out.append({"file": j["file"], "idx": j["idx"], "lines": ls})
        return out

    batches = [jobs[i:i + 3] for i in range(0, len(jobs), 3)]
    res = llm.pool(batches, work, threads=a.threads,
                   on_done=lambda d, t: print("  %d/%d" % (d, t), flush=True) if d % 20 == 0 else None)
    keep = [x for r in res if not isinstance(r, Exception) for x in r]
    json.dump(keep, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("verse paragraphs", len(keep), "of", len(jobs))


if __name__ == "__main__":
    main()
