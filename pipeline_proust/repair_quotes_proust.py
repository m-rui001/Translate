"""Repair quote direction and level in the Proust supplement.

The drafts sometimes open speech with a closing quote (”…”) and close it with
another ”, which reads as garbage. This walks the text with a nesting stack and
repairs direction first, then promotes top-level single quotes to double.
"""
from __future__ import annotations

import glob
import io
import os
import re
import sys

OUT = "E:/Translate/work_proust/out"
O2, C2, O1, C1 = "“", "”", "‘", "’"


def repair(text: str) -> str:
    out: list[str] = []
    stack: list[str] = []
    for ch in text:
        if ch == C2:
            if stack and stack[-1] == O2:
                stack.pop()
                out.append(C2)
            elif not stack:
                # a closing quote with nothing open: it was meant to open
                stack.append(O2)
                out.append(O2)
            else:
                stack.pop()
                out.append(C2)
        elif ch == O2:
            stack.append(O2)
            out.append(O2)
        elif ch == C1:
            if stack and stack[-1] == O1:
                stack.pop()
                out.append(C1)
            elif not stack:
                stack.append(O2)      # top-level single -> promote
                out.append(O2)
            else:
                stack.pop()
                out.append(C1)
        elif ch == O1:
            if stack and stack[-1] == O2:
                stack.append(O1)
                out.append(O1)
            else:
                stack.append(O2)      # top-level single -> promote
                out.append(O2)
        else:
            out.append(ch)
            if ch == "\n":            # a level may stay open across a line break
                pass
    return "".join(out)


def balance_report(text: str) -> tuple[int, int]:
    return text.count(O1) - text.count(C1), text.count(O2) - text.count(C2)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    touched = 0
    for f in sorted(glob.glob(os.path.join(OUT, "*", "chunk*", "final.txt"))):
        raw = io.open(f, encoding="utf-8").read()
        new = repair(raw)
        if new != raw:
            io.open(f, "w", encoding="utf-8").write(new)
            touched += 1
    print(f"repaired {touched} chunks")
    tot1 = tot2 = 0
    for f in glob.glob(os.path.join(OUT, "*", "chunk*", "final.txt")):
        t = io.open(f, encoding="utf-8").read()
        s, d = balance_report(t)
        tot1 += s
        tot2 += d
    print(f"net balance — single: {tot1:+d}  double: {tot2:+d}  (cross-paragraph speech leaves these open)")


if __name__ == "__main__":
    main()
