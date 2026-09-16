"""Reset non-processed docs in kv_store_doc_status.json so a resumed insert
re-enqueues them (LightRAG dedupes by content-hash doc_id in ANY status, so
failed/interrupted docs would otherwise be skipped forever).

Run ONLY while no build is running (no file locks).
Keeps 'processed' and 'processed_staleness'... rows intact; deletes everything
else (failed / parsing / processing / analyzing / pending).

Usage: py scripts/reset_doc_status.py [--dry]
"""
import io
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DS = Path("data/processed/lightrag_index/kv_store_doc_status.json")
KEEP = {"processed"}

dry = "--dry" in sys.argv
data = json.loads(DS.read_text(encoding="utf-8"))
before = Counter(v.get("status") for v in data.values())
print("before:", dict(before))

keep_rows = {k: v for k, v in data.items() if v.get("status") in KEEP}
removed = len(data) - len(keep_rows)
print(f"keeping {len(keep_rows)} processed rows; will delete {removed} rows")

if dry:
    print("(dry run — no changes written)")
else:
    DS.write_text(json.dumps(keep_rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("doc_status reset written")
