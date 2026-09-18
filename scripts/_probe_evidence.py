import json
from collections import Counter

rows = [json.loads(l) for l in open("data/seed/evidence_chunks.jsonl", encoding="utf-8") if l.strip()]
print("n =", len(rows))
print("source_type:", dict(Counter(r.get("source_type", "") for r in rows)))
print("level:", dict(Counter(r.get("evidence_level", "") for r in rows)))
print("source:", dict(Counter((r.get("source") or "")[:45] for r in rows)))
