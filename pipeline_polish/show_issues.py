"""Show before/after for the paragraphs the verifier flagged, so they can be judged
by eye rather than by score."""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = "E:/Translate"
BAK = os.path.join(ROOT, "work_polish2", "_backup_polish3")


def paras(t: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    kind = sys.argv[1] if len(sys.argv) > 1 else "REWRITE"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    issues = [x for x in json.load(open(os.path.join(ROOT, "work_polish2",
                                                     "_verify_issues.json"),
                                        encoding="utf-8"))
              if x["kind"] == kind]
    if kind == "REWRITE":
        issues.sort(key=lambda x: float(x["detail"]))
    for x in issues[:limit]:
        f = x["file"].replace("\\", "/")
        rel = os.path.relpath(f, ROOT).replace(os.sep, "__")
        bak = os.path.join(BAK, rel)
        if not os.path.exists(bak):
            print("no backup", rel)
            continue
        a = paras(open(bak, encoding="utf-8").read())
        b = paras(open(f, encoding="utf-8").read())
        i = x["para"]
        if i >= len(a) or i >= len(b):
            continue
        print(f"=== {f} p{i}  {x['detail']}")
        print(f"BEFORE ({len(a[i])}): {a[i][:300]}")
        print(f"AFTER  ({len(b[i])}): {b[i][:300]}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
