"""Measure new-doc completion rate over a window (doc_status is ground truth).

Usage: py scripts/rate_check.py [wait_seconds]
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DS = ROOT / "data" / "processed" / "lightrag_index" / "kv_store_doc_status.json"


def counts() -> dict:
    data = json.loads(DS.read_text(encoding="utf-8"))
    out: dict[str, int] = {}
    for row in data.values():
        out[row.get("status", "?")] = out.get(row.get("status", "?"), 0) + 1
    return out


def pid_snapshot() -> set:
    """doc ids currently in processing/pending/extracting states."""
    data = json.loads(DS.read_text(encoding="utf-8"))
    return {
        k
        for k, v in data.items()
        if v.get("status") in ("processing", "pending") and not k.startswith("dup-")
    }


wait = int(sys.argv[1]) if len(sys.argv) > 1 else 300
c0 = counts()
p0 = pid_snapshot()
t0 = time.time()
print(f"t0   status={c0}  in-flight(non-dup)={len(p0)}", flush=True)
time.sleep(wait)
c1 = counts()
p1 = pid_snapshot()
dt = time.time() - wait
print(f"t+{wait:.0f}s status={c1}  in-flight(non-dup)={len(p1)}", flush=True)
done = c1.get("processed", 0) - c0.get("processed", 0)
print(f"delta processed={done:+d} over {wait}s -> {done / (wait / 60):.2f} docs/min", flush=True)
if done > 0:
    rem = 357 - c1.get("processed", 0)
    eta = rem / (done / (wait / 60))
    print(f"remaining={rem}  ETA={eta / 60:.1f} h", flush=True)
