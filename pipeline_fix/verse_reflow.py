"""Restore verse lineation in a book whose poems were flattened into paragraphs.

Same contract as the Faust pass: the model may only insert line breaks, and the joined
lines must be byte-identical to the original paragraph, or the edit is dropped.
"""
import argparse, json, os, re, shutil, sys, zipfile
from html import escape, unescape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm

SYSTEM = """这是一部诗集中译本。原文的诗行在排版时被合并成了一整段。
你的任务：把它还原成诗行。

规则：
1. 只插入换行，不得增删或改动任何一个字、一个标点。
2. 分行位置依原诗的节奏与句法；中文一行对应原诗一行，长短不必整齐。
3. 散文段落不要分行，verse 填 false。
4. 每行不要带行首行尾空格。

输出严格 JSON：
{"v":[{"i":1,"verse":true,"lines":["第一行","第二行"]}]}
i 从 1 开始，与题号一致。"""


def paras(html):
    return [unescape(re.sub(r"<[^>]+>", "", m.group(2)))
            for m in re.finditer(r"<p([^>]*)>(.*?)</p>", html, re.S)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("epub")
    ap.add_argument("--threads", type=int, default=12)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--minlen", type=int, default=60)
    a = ap.parse_args()

    with zipfile.ZipFile(a.epub) as z:
        files = {n: z.read(n).decode("utf-8") for n in z.namelist() if n.endswith(".xhtml")}

    jobs = []
    for name, html in files.items():
        if name.endswith(("nav.xhtml", "title.xhtml")):
            continue
        for idx, text in enumerate(paras(html)):
            if len(text) >= a.minlen and "\n" not in text:
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
            if len(ls) < 2 or "".join(ls) != j["text"]:
                continue
            out.append({"file": j["file"], "idx": j["idx"], "lines": ls})
        return out

    batches = [jobs[i:i + 3] for i in range(0, len(jobs), 3)]
    res = llm.pool(batches, work, threads=a.threads)
    keep = [x for r in res if not isinstance(r, Exception) for x in r]
    json.dump(keep, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("verse paragraphs", len(keep), "of", len(jobs))


if __name__ == "__main__":
    main()
