"""Benchmark gateway models on a real LOTR chunk: speed, completeness, Chinese quality."""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import llm
import workflow as wf
from glossary import relevant, render as render_glossary
from style import STYLE

ch = json.load(open("E:/Translate/work/src/book5c07.json", encoding="utf-8"))
chunks = wf.chunk_blocks(ch["blocks"], target_words=600, max_words=750)
blocks = chunks[1]
source = wf.render_source(blocks)

MODELS = sys.argv[1].split(",") if len(sys.argv) > 1 else [
    "glm-5.3-flash", "sf-glm-5.2", "ms-glm-5.2", "sf-deepseek-v4-pro",
    "or-nemotron-3-ultra", "minimax-m3.1-flash", "ms-mistral-large", "longcat-2.5",
]

PROMPT = f"""{render_glossary(relevant(source))}

把下面这段《魔戒》原文完整译成中文。逐段对应，一段不漏，诗行保留分行。
把译文放在 <first_translation> 与 </first_translation> 之间。

<source>
{source}
</source>"""


def run(m):
    t0 = time.time()
    try:
        text, used = llm.chat(
            [{"role": "system", "content": STYLE}, {"role": "user", "content": PROMPT}],
            models=[m], max_tokens=4000, temperature=0.7, tag=f"bench:{m}",
            retries=1, timeout=240,
        )
        out = wf.tag(text, "first_translation") or text
        return m, time.time() - t0, len(out), out
    except Exception as e:  # noqa: BLE001
        return m, time.time() - t0, -1, str(e)[:200]


with ThreadPoolExecutor(max_workers=8) as ex:
    for m, secs, n, out in ex.map(run, MODELS):
        print(f"\n===== {m}  {secs:.0f}s  {n} chars")
        print(out[:900])
