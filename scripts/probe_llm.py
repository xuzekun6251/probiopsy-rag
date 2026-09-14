"""Probe: LLMClient SDK path (bounded timeout + client reuse) works against GLM."""
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

c = LLMClient(provider="deepseek", max_tokens=256)
print(f"model={c.model} base={c.base_url} max_tokens={c.max_tokens} degraded={c.degraded}")
t0 = time.time()
r = c.complete(prompt="Reply with exactly: OK", system="You are a test probe.")
print(f"elapsed={time.time()-t0:.1f}s degraded={r.degraded} text={r.text[:80]!r}")
t0 = time.time()
r2 = c.complete(prompt="Reply with exactly: SECOND-OK", system="You are a test probe.")
print(f"second elapsed={time.time()-t0:.1f}s degraded={r2.degraded} text={r2.text[:80]!r}")
assert not r.degraded and not r2.degraded, "probe failed"
print("PROBE PASS")
