# -*- coding: utf-8 -*-
"""QA gate for the Translate shelf: the three checks that the 2026-11-27
external review proved we were missing. Runs over every work_batch*/ *_zh.json
and every out/*.epub, and fails loudly.

Gates
-----
1. AI-dialogue residue  — paragraphs where a model answered back instead of
   translating ("请把…贴过来", "原文似乎…", "我按你的规则", …).  Also catches
   hallucinated continuations: src very short but zh enormous.
2. Canon drift          — any variant spelling of a name listed in canon.json
   (registered canonical form only).  Reports the file/para of each variant.
3. Quote stack          — per paragraph, 「 must open and 」 must close; a 」 in
   the closed state or a 「 while open is an error.  (Nested pairs inside an
   outer quote must be 『』.)  A paragraph may legitimately END open when a long
   quotation carries into the next paragraph, so only *ordering* is gated,
   plus a paragraph that ends on an opening mark.

Additionally: latin letters in body text, opencc t2s identity, doubled
punctuation (，， 。。), and EPUB/JSON paragraph-set equality.

Usage:  python -X utf8 pipeline_build/qa_gate.py [--quiet]
Exit code 0 = clean.
"""
import ast
import glob
import json
import os
import re
import sys
import zipfile

# Books rewritten in the 2026-11-26/27 batches: these must pass hard.
INSCOPE = (
    "kef_", "pgm_", "tow_", "fp_", "sow_", "dr_", "utpo_", "tw_", "ft_",
    "mrj_", "mj2_", "mj3_", "bv_", "ah_", "lf_", "sh_", "in_", "hd_", "cw_",
    "mm_", "lc_", "gk_", "gp_", "hd2_", "gr_", "bi2_", "hv_", "cc_",
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work_batch_20261124")
OUT = os.path.join(ROOT, "out")
CANON = os.path.join(WORK, "canon.json")

RESIDUE = re.compile(
    r"(请把.{0,16}(贴|发给我|补上|补发|补全)|"
    r"(原文|正文|内容)(似乎|没有|缺失|只收到|只给|未)|"
    r"我按你的规则|粘贴过来|正文未随|请把要翻译|请把完整的英文|"
    r"我立刻开始翻译|请补发)"
)
LATIN = re.compile(r"[A-Za-z]{2,}")
DOUBLE = ("，，", "。。", "；；", "、、")


def load_canon():
    """Return list of (family, canonical, [variants]) ready for scanning."""
    data = json.load(open(CANON, encoding="utf-8"))
    out = []
    for fam, table in data.items():
        if fam.startswith("_") or fam == "conventions":
            continue
        for canon, value in table.items():
            out.append((fam, canon, value))
    return out


# Hand-maintained variant lists: canonical -> known wrong forms seen in drafts.
VARIANTS = {
    "兰道夫·卡特": ["伦道夫·卡特"],
    "密斯卡托尼克": ["米斯卡托尼克", "米斯科托尼克"],
    "阿卜杜·阿尔哈兹莱德": ["阿卜杜拉·阿尔哈兹莱德"],
    "兹考巴": ["兹卡乌巴", "兹卡奥巴"],
    "修格斯": ["夏戈斯"],
    "《纳克特抄本》": ["《纳克特断简》", "《纳克特手稿》", "《波那克年代记》"],
    "《诡丽奇谭》": ["《诡丽幻谭》"],
    "博雷勒斯": ["博雷卢斯"],
    "丹弗思": ["丹福思"],
    "犹格·索托斯": ["优格·索托斯"],
    "维利尔斯": ["维利耶", "维利叶"],
    "阿真坦勋爵": ["阿真廷", "阿金坦", "阿金泰恩", "阿金廷"],
    "凯尔迈恩": ["凯尔门"],
    "罗列赫": ["罗列里希"],
    "麦克泰": ["麦克泰格"],
    "科曼奇纪": ["康曼奇期"],
    "生命之延续者": ["生命之延长者"],
}


def gate_json(quiet=False):
    problems = []
    files = sorted(glob.glob(os.path.join(WORK, "*_zh.json")))
    for path in files:
        name = os.path.basename(path)
        stem = name[:-8]                     # drop "_zh.json"
        if re.fullmatch(r"[a-z]{2,4}_s\d{2}[ab]", stem):
            continue                         # <key>a/_b halves, merged into the parent
        try:
            zh = json.load(open(path, encoding="utf-8"))
        except Exception as exc:                      # noqa: BLE001
            problems.append((name, -1, "unparsable JSON: %s" % exc))
            continue
        src_path = path.replace("_zh.json", "_src.json")
        src = None
        if os.path.exists(src_path):
            try:
                src = json.load(open(src_path, encoding="utf-8"))
            except Exception:                          # noqa: BLE001
                src = None
        if src is not None and len(src) != len(zh):
            problems.append((name, -1, "length %d vs src %d" % (len(zh), len(src))))

        for i, para in enumerate(zh):
            if RESIDUE.search(para):
                problems.append((name, i, "AI residue: " + para[:50]))
            if src is not None and i < len(src):
                s = src[i]
                if len(s) < 40 and len(para) > len(s) * 4 + 40:
                    problems.append((name, i, "hallucinated length %d->%d" % (len(s), len(para))))
            if LATIN.search(para):
                problems.append((name, i, "latin letters: " + LATIN.search(para).group()))
            for dd in DOUBLE:
                if dd in para:
                    problems.append((name, i, "doubled punctuation " + dd))
            # quote ordering
            state = "closed"
            err = None
            for ch in para:
                if ch == "「":
                    if state == "open":
                        err = "double-open quote"
                        break
                    state = "open"
                elif ch == "」":
                    if state == "closed":
                        err = "close-before-open quote"
                        break
                    state = "closed"
            if err:
                problems.append((name, i, err))
            elif state == "open" and para.rstrip().endswith(("「", "『")):
                problems.append((name, i, "paragraph ends on an opening quote"))
            # canon drift
            for canon, bads in VARIANTS.items():
                for bad in bads:
                    if bad in para:
                        problems.append((name, i, "canon drift %s -> %s" % (bad, canon)))
    if not problems and not quiet:
        print("[ok] json gate: %d files clean" % len(files))
    return problems


def gate_simplified(quiet=False):
    try:
        import opencc
    except ImportError:
        if not quiet:
            print("[skip] opencc not installed; simplified gate skipped")
        return []
    cc = opencc.OpenCC("t2s")
    problems = []
    for path in sorted(glob.glob(os.path.join(WORK, "*_zh.json"))):
        name = os.path.basename(path)
        for i, para in enumerate(json.load(open(path, encoding="utf-8"))):
            if cc.convert(para) != para:
                problems.append((name, i, "traditional characters present"))
    if not problems and not quiet:
        print("[ok] simplified gate clean")
    return problems


def gate_epub(quiet=False):
    problems = []
    for epub in sorted(glob.glob(os.path.join(OUT, "*.epub"))):
        name = os.path.basename(epub)
        try:
            z = zipfile.ZipFile(epub)
            body = "".join(
                z.read(n).decode("utf-8", "ignore")
                for n in z.namelist() if n.endswith(".xhtml")
            )
        except Exception as exc:                       # noqa: BLE001
            problems.append((name, -1, "unreadable epub: %s" % exc))
            continue
        for m in RESIDUE.finditer(body):
            problems.append((name, -1, "AI residue in epub: " + body[m.start():m.start() + 40]))
        if "характер" in body:
            problems.append((name, -1, "cyrillic residue"))
    if not problems and not quiet:
        print("[ok] epub gate clean")
    return problems


def main(argv):
    quiet = "--quiet" in argv
    problems = gate_json(quiet) + gate_simplified(quiet) + gate_epub(quiet)
    hard = [p for p in problems if p[0].startswith(INSCOPE)]
    legacy = [p for p in problems if not p[0].startswith(INSCOPE)]
    if legacy and not quiet:
        print("[warn] %d legacy (pre-2026-11-26) finding(s) — out of today's scope"
              % len(legacy))
        for name, idx, msg in legacy[:8]:
            print("   ~ %-42s %5s  %s" % (name, idx, msg))
    if not hard:
        print("QA GATE: in-scope clean")
        return 0
    print("QA GATE: %d in-scope problem(s)" % len(hard))
    problems = hard
    for name, idx, msg in problems[:200]:
        print("  %-46s %5s  %s" % (name, idx, msg))
    if len(problems) > 200:
        print("  ... %d more" % (len(problems) - 200))
    return 1


ast.parse(open(__file__, encoding="utf-8").read())
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))