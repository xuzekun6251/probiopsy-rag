"""Poll build log + baseline predictions progress (read-only)."""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

p = os.path.join(ROOT, "outputs", "phase4_build_log.txt")
if os.path.exists(p):
    lines = open(p, encoding="utf-8", errors="ignore").read().splitlines()
    print(f"BUILD LOG lines: {len(lines)}")
    for l in lines[-12:]:
        print("  |", l)
else:
    print("no build log")

pp = os.path.join(ROOT, "outputs", "baseline_predictions.jsonl")
if os.path.exists(pp):
    rows = [json.loads(l) for l in open(pp, encoding="utf-8") if l.strip()]
    print(f"PRED rows: {len(rows)}")
    for r in rows:
        print(
            f"  | {r['method']} seed{r['seed']} {r['statement_id']} "
            f"gold={r['gold_action']} pred={r['pred_action']}"
        )
else:
    print("no predictions file")

# lightrag index state
idx = os.path.join(ROOT, "data", "processed", "lightrag_index")
if os.path.isdir(idx):
    for f in sorted(os.listdir(idx)):
        fp = os.path.join(idx, f)
        print(f"  IDX {f}: {os.path.getsize(fp)/1e6:.2f} MB")
