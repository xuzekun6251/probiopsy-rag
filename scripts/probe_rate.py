"""Probe the Zhipu account-level RPM ceiling: N small calls at a fixed interval.

Usage: py scripts/probe_rate.py [interval_s] [n_calls]
Prints per-call status; counts 429/1302 hits.
"""
import io
import os
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

from probiopsy_rag_agent.llm_client import LLMClient

interval = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
n = int(sys.argv[2]) if len(sys.argv) > 2 else 8

# disable the client-side throttle — we are probing the SERVER's ceiling
os.environ["LLM_MIN_INTERVAL"] = "0"

c = LLMClient(provider="deepseek", max_tokens=256)
ok = fail = 0
t0 = time.time()
for i in range(n):
    r = c.complete(prompt=f"Reply with exactly: P{i}", system="probe")
    hit = r.degraded and ("429" in r.text or "1302" in r.text)
    if r.degraded:
        fail += 1
    else:
        ok += 1
    print(f"  call {i+1}/{n}: degraded={r.degraded} 429={hit} "
          f"({time.time()-t0:.1f}s elapsed) {r.text[:60]!r}")
    if i < n - 1:
        time.sleep(interval)
print(f"RESULT interval={interval}s n={n}: ok={ok} fail={fail} "
      f"-> demand {60.0/interval:.0f} RPM")
