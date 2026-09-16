"""Search the whole lightrag package for the dedup/reprocess decision."""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
PKG = r".venv/Lib/site-packages/lightrag"
hits = 0
for root, _dirs, files in os.walk(PKG):
    for f in files:
        if not f.endswith(".py"):
            continue
        p = os.path.join(root, f)
        try:
            src = open(p, encoding="utf-8").read()
        except Exception:
            continue
        for m in re.finditer(r"(unique documents|Duplicate document|DocStatus\.FAILED)", src):
            s = src.rfind("\n", 0, m.start() - 500)
            snippet = src[max(0, m.start() - 500):m.start() + 400]
            if "def " in snippet or "status" in snippet.lower():
                print(f"===== {f}:{m.start()} =====")
                print("\n".join(snippet.splitlines()[-22:]))
                print()
                hits += 1
            if hits > 6:
                sys.exit(0)
