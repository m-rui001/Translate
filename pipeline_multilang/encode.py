#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""encode.py — 随机抽取文本中约 N% 的字符，逐个改写为随机一种编码形式。

    python -X utf8 pipeline_multilang/encode.py encode IN.txt -o OUT.txt --ratio 0.10
    python -X utf8 pipeline_multilang/encode.py verify IN.txt OUT.txt
    python -X utf8 pipeline_multilang/encode.py decode OUT.txt -o BACK.txt

支持的编码形式（--schemes 可选，逗号分隔）：

    u4     \\u4F60          JSON/Python 风格的 4 位转义
    u8     \\U00004F60      8 位转义
    html   &#20320;         十进制 HTML 实体
    hhex   &#x4F60;         十六进制 HTML 实体
    pct    %E4%BD%A0        percent-encoding（UTF-8 字节）
    hex    \\xe4\\xbd\\xa0     C 风格十六进制字节转义
    oct    \\344\\275\\240    C 风格八进制字节转义
    uplus  U+4F60           Unicode 码位写法
    b64    ⟦5L2g⟧          单字符 base64（带定界符，避免歧义）

默认八个形式全开（b64 除外）。空白字符（空格/制表/换行）一律不动，
否则版面会散架；`--include-space` 可放开。

encode 会同时写出 `OUT.txt.report.json`：每个位置用了哪种形式，以及
编码前后长度；`verify` 用它对整个文件做往返校验（decode(密文) == 原文）。
"""

from __future__ import annotations

import argparse
import base64
import json
import random
import re
import sys
import urllib.parse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------- 编码器

def enc_u4(ch: str) -> str:
    cp = ord(ch)
    return f"\\u{cp:04X}" if cp < 0x10000 else f"\\U{cp:08X}"


def enc_u8(ch: str) -> str:
    return f"\\U{ord(ch):08X}"


def enc_html(ch: str) -> str:
    return f"&#{ord(ch)};"


def enc_hhex(ch: str) -> str:
    return f"&#x{ord(ch):X};"


def enc_pct(ch: str) -> str:
    return urllib.parse.quote(ch, safe="")


def enc_hex(ch: str) -> str:
    return "".join(f"\\x{b:02x}" for b in ch.encode("utf-8"))


def enc_oct(ch: str) -> str:
    return "".join(f"\\{b:03o}" for b in ch.encode("utf-8"))


def enc_uplus(ch: str) -> str:
    cp = ord(ch)
    return f"U+{cp:04X}" if cp < 0x10000 else f"U+{cp:06X}"


def enc_b64(ch: str) -> str:
    return "⟦" + base64.b64encode(ch.encode("utf-8")).decode() + "⟧"


ENCODERS = {
    "u4": enc_u4,
    "u8": enc_u8,
    "html": enc_html,
    "hhex": enc_hhex,
    "pct": enc_pct,
    "hex": enc_hex,
    "oct": enc_oct,
    "uplus": enc_uplus,
    "b64": enc_b64,
}
DEFAULT_SCHEMES = ["u4", "u8", "html", "hhex", "pct", "hex", "oct", "uplus"]

# ---------------------------------------------------------------- 解码器
# 单趟扫描，顺序即优先级。必须先长后短（\U 在 \u 前、&#x 在 &# 前）。

_U8 = re.compile(r"\\U([0-9A-Fa-f]{8})")
_U4 = re.compile(r"\\u([0-9A-Fa-f]{4})")
_HEXESC = re.compile(r"(?:\\x([0-9A-Fa-f]{2}))+")
_OCTESC = re.compile(r"(?:\\[0-7]{1,3})+")
_HHEX = re.compile(r"&#x([0-9A-Fa-f]+);")
_HTML = re.compile(r"&#(\d+);")
_PCT = re.compile(r"(?:%[0-9A-Fa-f]{2})+")
_UPLUS = re.compile(r"U\+([0-9A-Fa-f]{4,6})")
_B64 = re.compile(r"⟦([A-Za-z0-9+/=]+)⟧")


def _bytes_of(regex: re.Pattern, s: str, prefix_len: int) -> bytes:
    """把 '\\xe4\\xbd\\xa0' / '\\344' 这类重复单元还原成字节串。"""
    out = bytearray()
    for m in re.finditer(r"\\(?:x([0-9A-Fa-f]{2})|([0-7]{1,3}))", s):
        if m.group(1):
            out.append(int(m.group(1), 16))
        else:
            out.append(int(m.group(2), 8) & 0xFF)
    return bytes(out)


def decode_all(text: str) -> str:
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "\\" or ch == "&" or ch == "%" or ch == "U" or ch == "⟦":
            m = _U8.match(text, i)
            if m:
                out.append(chr(int(m.group(1), 16)))
                i = m.end()
                continue
            m = _U4.match(text, i)
            if m:
                out.append(chr(int(m.group(1), 16)))
                i = m.end()
                continue
            m = _HEXESC.match(text, i)
            if m:
                out.append(_bytes_of(_HEXESC, m.group(0), 2).decode("utf-8", "replace"))
                i = m.end()
                continue
            m = _OCTESC.match(text, i)
            if m:
                out.append(_bytes_of(_OCTESC, m.group(0), 1).decode("utf-8", "replace"))
                i = m.end()
                continue
            m = _HHEX.match(text, i)
            if m:
                out.append(chr(int(m.group(1), 16)))
                i = m.end()
                continue
            m = _HTML.match(text, i)
            if m:
                out.append(chr(int(m.group(1))))
                i = m.end()
                continue
            m = _PCT.match(text, i)
            if m:
                raw = bytes(int(x, 16) for x in re.findall(r"%([0-9A-Fa-f]{2})", m.group(0)))
                out.append(raw.decode("utf-8", "replace"))
                i = m.end()
                continue
            m = _UPLUS.match(text, i)
            if m:
                out.append(chr(int(m.group(1), 16)))
                i = m.end()
                continue
            m = _B64.match(text, i)
            if m:
                try:
                    out.append(base64.b64decode(m.group(1)).decode("utf-8", "replace"))
                    i = m.end()
                    continue
                except Exception:                                   # noqa: BLE001
                    pass
        out.append(ch)
        i += 1
    return "".join(out)


# ---------------------------------------------------------------- 命令

# 会与解码器混淆的“伪转义”字面量：出现在原文里就必须连它一起编码，
# 否则解码时会被误认为我们写进去的转义，往返校验不可能一致。
AMBIG_PATTERNS = [
    r"\\U[0-9A-Fa-f]{8}",
    r"\\u[0-9A-Fa-f]{4}",
    r"(?:\\x[0-9A-Fa-f]{2})+",
    r"(?:\\[0-7]{1,3})+",
    r"&#x[0-9A-Fa-f]+;",
    r"&#[0-9]+;",
    r"(?:%[0-9A-Fa-f]{2})+",
    r"U\+[0-9A-Fa-f]{4,6}",
    r"⟦[A-Za-z0-9+/=]+⟧",
]
AMBIG_RE = [re.compile(p) for p in AMBIG_PATTERNS]


def ambiguous_positions(text: str) -> set[int]:
    pos: set[int] = set()
    for pat in AMBIG_RE:
        for m in pat.finditer(text):
            pos.update(range(m.start(), m.end()))
    return pos


def walk_code(text: str):
    """返回 (是否在围栏代码块内) 的逐字符判定函数。"""
    fences = []
    inside = [False]
    pos = 0
    for line in text.splitlines(keepends=True):
        is_fence = re.match(r"^\s*(```|~~~)", line) is not None
        start, end = pos, pos + len(line)
        fences.append((start, end, is_fence))
        pos = end

    def check(idx: int) -> bool:
        state = False
        for start, _end, is_fence in fences:
            if start > idx:
                break
            if is_fence:
                state = not state
        return state

    return check


def cmd_encode(args) -> None:
    src = Path(args.input)
    text = src.read_text(encoding="utf-8")
    rnd = random.Random(args.seed)
    schemes = [x.strip() for x in args.schemes.split(",") if x.strip()]
    bad = [x for x in schemes if x not in ENCODERS]
    if bad:
        sys.exit(f"未知编码形式 {bad}；可选 {list(ENCODERS)}")
    skip_code = walk_code(text) if args.skip_code else (lambda i: False)

    eligible = [i for i, c in enumerate(text)
                if (args.include_space or not c.isspace())
                and not skip_code(i) and c != "\ufeff"]
    target = max(1, round(len(eligible) * args.ratio))
    chosen = set(rnd.sample(eligible, min(target, len(eligible))))
    forced = {i for i in ambiguous_positions(text) if i not in chosen} if args.fix_ambiguous else set()
    chosen |= forced

    out: list[str] = []
    report = []
    counts: dict[str, int] = {k: 0 for k in schemes}
    for i, ch in enumerate(text):
        if i in chosen:
            st = rnd.choice(schemes)
            enc = ENCODERS[st](ch)
            counts[st] += 1
            report.append({"pos": i, "char": ch, "scheme": st, "encoded": enc})
            out.append(enc)
        else:
            out.append(ch)
    enc_text = "".join(out)

    dst = Path(args.out)
    dst.write_text(enc_text, encoding="utf-8")
    (dst.parent / (dst.name + ".report.json")).write_text(
        json.dumps({"source": str(src), "ratio": args.ratio, "seed": args.seed,
                    "counts": counts, "total": len(report),
                    "items": report}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    total = len(text)
    print(f"字符总数 {total}，可编码 {len(eligible)}，抽取 {target}，"
          f"另强制编码伪转义字面量 {len(forced)} 个，共替换 {len(report)}")
    print(f"实际比例 {len(report)/total:.2%}")
    print("形式分布：" + "，".join(f"{k}={v}" for k, v in counts.items() if v))
    print(f"长度 {total} → {len(enc_text)}（+{len(enc_text)-total}）")
    back = decode_all(enc_text)
    print("往返校验：" + ("通过" if back == text else "失败"))
    if back != text:
        for i, (a, b) in enumerate(zip(back, text)):
            if a != b:
                print(f"  首个不一致位置 {i}：解码 {a!r} vs 原文 {b!r}")
                break
        sys.exit(2)
    print(f"→ {dst}")


def cmd_decode(args) -> None:
    text = Path(args.input).read_text(encoding="utf-8")
    back = decode_all(text)
    if args.out:
        Path(args.out).write_text(back, encoding="utf-8")
        print(f"→ {args.out}（{len(back)} 字符）")
    else:
        sys.stdout.write(back)


def cmd_verify(args) -> None:
    orig = Path(args.original).read_text(encoding="utf-8")
    enc = Path(args.encoded).read_text(encoding="utf-8")
    back = decode_all(enc)
    ok = back == orig
    print(f"原文 {len(orig)} 字符，密文 {len(enc)} 字符，解码 {len(back)} 字符")
    print("往返一致" if ok else "往返不一致")
    if not ok:
        for i, (a, b) in enumerate(zip(back, orig)):
            if a != b:
                print(f"  首个不一致位置 {i}：{a!r} vs {b!r}")
                break
        sys.exit(1)
    rp = Path(str(Path(args.encoded)) + ".report.json")
    if rp.exists():
        d = json.loads(rp.read_text(encoding="utf-8"))
        print(f"报告：替换 {d['total']} 字符，比例 {d['total']/len(orig):.2%}，"
              f"形式 {d['counts']}")


def main() -> None:
    ap = argparse.ArgumentParser(description="字符级随机编码混淆/还原/校验")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("encode")
    p.add_argument("input")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--ratio", type=float, default=0.10, help="占比，默认 0.10")
    p.add_argument("--schemes", default=",".join(DEFAULT_SCHEMES))
    p.add_argument("--seed", type=int, default=20261122)
    p.add_argument("--skip-code", action="store_true", help="跳过围栏代码块")
    p.add_argument("--no-fix-ambiguous", dest="fix_ambiguous",
                   action="store_false",
                   help="不强制编码原文里已有的伪转义字面量（会造成往返不一致）")
    p.set_defaults(fix_ambiguous=True)
    p.add_argument("--include-space", action="store_true", help="连空白也编码")
    p.set_defaults(func=cmd_encode)

    p = sub.add_parser("decode")
    p.add_argument("input")
    p.add_argument("-o", "--out", default="")
    p.set_defaults(func=cmd_decode)

    p = sub.add_parser("verify")
    p.add_argument("original")
    p.add_argument("encoded")
    p.set_defaults(func=cmd_verify)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()