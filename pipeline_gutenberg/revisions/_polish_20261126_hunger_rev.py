# -*- coding: utf-8 -*-
"""《饥饿艺术家》精修——作用于真正进入 EPUB 的 revision.json。

备份 revision.json 后，按"改出最好作品"标准对 c001 段落做最小打磨。
"""
import ast
import json
import shutil

PATH = "E:/Translate/pipeline_gutenberg/revisions/hungerkuenstler.json"
BAK = PATH + ".bak_20261126"

EDITS = [
    ("乐队响亮地奏出一阵短曲，仿佛把方才的一切又确认了一遍",
     "乐队响亮地吹奏一通，仿佛把方才的一切又确认了一遍",
     "⑥硬伤: ein großer Tusch=盛大的吹奏/号角齐鸣,非'短曲'(short piece)"),
    ("往好处想，只当他谦虚。",
     "说得好听些，也不过当他谦逊。",
     "günstigstenfalls=说得好听些, 更准"),
    ("居然还有脸把这事半遮半掩地认下来",
     "居然还厚着脸皮把这事半遮半掩地认下来",
     "die Stirn hatte=厚着脸皮, 更准更顺"),
]

shutil.copy(PATH, BAK)
raw = open(PATH, encoding="utf-8").read()
data = json.loads(raw)
paras = data["c001"]["paragraphs"]
n_before = len(paras)
for old, new, reason in EDITS:
    hits = sum(p.count(old) for p in paras)
    assert hits == 1, (old, hits)
    for i, p in enumerate(paras):
        if old in p:
            paras[i] = p.replace(old, new)
            break
assert len(paras) == n_before
out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
open(PATH, "w", encoding="utf-8", newline="").write(out)
print("applied", len(EDITS), "refinements to revision.json; paras", len(paras))

ast.parse(open(__file__, encoding="utf-8").read())
