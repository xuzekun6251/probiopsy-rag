"""Locate LightRAG's dedup/reprocess decision logic."""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
src = open(r".venv/Lib/site-packages/lightrag/lightrag.py", encoding="utf-8").read()

for pat in ["unique documents", "Duplicate document", "is_new_document", "status.*failed"]:
    for m in list(re.finditer(pat, src, re.I))[:3]:
        start = src.rfind("\n", max(0, m.start() - 600), m.start())
        snippet = src[max(0, m.start() - 600):m.start() + 250]
        print(f"--- {pat} @ {m.start()} ---")
        print(snippet[-700:])
        print()
