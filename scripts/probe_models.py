"""Probe which Zhipu models the account can call (fast fail on invalid names)."""
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

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("HUANYU_BULK_API_KEY"),
    base_url=os.getenv("HUANYU_BULK_BASE_URL"),
    timeout=45.0,
    max_retries=0,
)

CANDIDATES = [
    "glm-5.3",          # current (thinking flagship)
    "glm-5.3-air",
    "glm-5-air",
    "glm-5.3-flash",
    "glm-5-flash",
    "glm-4.7-flash",
    "glm-4-flash",
    "glm-4.7-air",
    "glm-4.7",
    "glm-4.6",
]
for m in CANDIDATES:
    t0 = time.time()
    try:
        r = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
            max_tokens=8192,
        )
        dt = time.time() - t0
        txt = (r.choices[0].message.content or "").strip()[:30]
        usage = getattr(r, "usage", None)
        ct = getattr(usage, "completion_tokens", None) if usage else None
        print(f"  {m:16s} OK   {dt:5.1f}s  content={txt!r} completion_tokens={ct}")
    except Exception as e:
        dt = time.time() - t0
        msg = str(e).replace("\n", " ")[:110]
        print(f"  {m:16s} FAIL {dt:5.1f}s  {msg}")
    time.sleep(1.0)
