# -*- coding: utf-8 -*-
"""Translate the real missing trailing chunks (holes in published EPUBs) via the
codebuddy CLI (free `deepseek-v4.1-flash`), reusing `workflow.translate_chunk`
unchanged -- same prompts, same structural validation, same final.txt format.

The local :8317 gateway is down, so `llm.chat_pool` is replaced by a codebuddy
backend. Prompts keep the whale wording but 《白鲸》/麦尔维尔 are genericised to the
book at hand so the framing is not factually wrong.

Targets verified as REAL holes (src tail blocks absent from the built EPUB):
  diana c010/c03 (4842 words), germinie c013/c01, guarany c003/c01,
  guarany c040/c01, timar c039/c01.
Everything else the chunk scan flagged is front matter / publisher ads /
textual-variant apparatus / glossary pages, which the established 体例 skips.

Usage:  python pipeline_gutenberg/_cb_translate_20261126.py
"""
import ast
import json
import re
import subprocess
import sys

HERE = __import__("os").path.dirname(__file__)
ROOT = __import__("os").path.dirname(HERE)
for p in (ROOT + "/pipeline_gutenberg", ROOT + "/pipeline_whale",
          ROOT + "/pipeline_private"):
    sys.path.insert(0, p)

import workflow as wf                      # noqa: E402
import llm                                 # noqa: E402

MODEL = "deepseek-v4.1-flash"
BOOKNAME = {}          # tag -> (title_zh, author) for prompt genericisation


def _strip(out: str) -> str:
    m = re.search(r"<(first_translation|polished|improved_translation|proofread)>"
                  r"(.*?)</\1>", out, re.S)
    if m:
        return m.group(2).strip()
    return out.strip()


def chat_pool(messages, models, **kw):
    """codebuddy backend for llm.chat_pool: system+user via stdin, retries."""
    prompt = "\n\n".join(m["content"] for m in messages)
    # genericise the whale-specific framing to the book actually being translated
    title_zh, author = BOOKNAME.get(kw.get("tag", ""), ("本书", "原作者"))
    prompt = (prompt
              .replace("《白鲸》", "《%s》" % title_zh)
              .replace("麦尔维尔", author)
              .replace("亚哈", "书中人物"))
    last = ""
    for attempt in range(4):
        try:
            r = subprocess.run(
                [r"C:/Users/hp/AppData/Roaming/npm/codebuddy.cmd", "-p",
                 "--model", MODEL],
                input=prompt, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=1200)
            got = _strip(r.stdout or "")
            if got:
                if attempt >= 1 or any("\u4e00" <= c <= "\u9fff" for c in got):
                    return got, "cb:" + MODEL
                # model echoed the source instead of translating: push it again
                prompt = (prompt + "\n\n注意：你上一次的回复只是原样重复了原文，"
                          "没有翻译。请把原文完整译成地道的文学中文，"
                          "保持段落一一对应，只输出译文本身。")
                continue
            last = (r.stderr or "")[:200] or "empty output"
        except subprocess.TimeoutExpired:
            last = "timeout"
    raise llm.LLMError("codebuddy failed: " + last)


llm.chat_pool = chat_pool

TARGETS = [
    ("work_gutenberg", "diana", "c010", 3, "戴安娜的交叉", "梅雷迪思"),
    ("work_gutenberg", "germinie", "c013", 1, "热尔米妮·拉瑟尔特", "龚古尔兄弟"),
    ("work_gutenberg", "guarany", "c003", 1, "瓜拉尼人", "阿伦卡尔"),
    ("work_gutenberg", "guarany", "c040", 1, "瓜拉尼人", "阿伦卡尔"),
    ("work_gutenberg", "timar", "c039", 1, "金人", "约卡伊"),
]

pools = {"writer": ["cb:" + MODEL], "polisher": ["cb:" + MODEL]}

for root, book, cid, i, tzh, author in TARGETS:
    tag = "%s:%s/c%02d" % (book, cid, i)
    BOOKNAME[tag] = (tzh, author)
    spec = json.load(open("%s/%s/chunks/%s.json" % (root, book, cid),
                          encoding="utf-8"))
    blocks = spec["chunks"][i]
    outdir = "%s/%s/out/%s/c%02d" % (root, book, cid, i)
    r = wf.translate_chunk(blocks, outdir, pools, tag, nums=True, resume=True,
                           audit=False, polish=True, analysis_text="")
    print(tag, "cached" if r.get("cached") else "done",
          "notes=%s skipped=%s" % (r.get("notes"), r.get("skipped")), flush=True)

ast.parse(open(__file__, encoding="utf-8").read())
