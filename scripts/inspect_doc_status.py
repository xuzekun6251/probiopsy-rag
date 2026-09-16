"""Inspect doc_status rows: are failed rows junk duplicates or real failures?"""
import io
import json
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ds = json.load(open("data/processed/lightrag_index/kv_store_doc_status.json", encoding="utf-8"))
fails = [(k, v) for k, v in ds.items() if v.get("status") == "failed"]
print("failed rows:", len(fails))
for k, v in fails[:4]:
    summary = (v.get("content_summary") or v.get("error_msg") or "")[:110]
    print("  ", k[:22], "|", summary)
proc = [(k, v) for k, v in ds.items() if v.get("status") == "processed"]
print("processed rows:", len(proc))
print("all keys sample:", list(ds)[:3])
