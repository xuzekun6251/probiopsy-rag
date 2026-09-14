"""Reproduce ONE heavy (extraction-like) call to see server behavior.

Builds a ~3k-token prompt (mimics LightRAG extraction), calls GLM-5.3 with
max_tokens=16384 through the real client (throttle disabled), prints timing
and response shape.
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
os.environ["LLM_MIN_INTERVAL"] = "0"

from probiopsy_rag_agent.llm_client import LLMClient

filler = (
    "The ProBIOPSY consensus on prostate biopsy addresses MRI-driven pathways, "
    "PI-RADS classification, targeted and systematic biopsy schemes, perilesional "
    "biopsy technique, anaesthesia, antibiotic prophylaxis, and treatment planning. "
)
prompt = (
    "-Entity extraction-\n"
    "Extract entities and relationships from the text below in the format "
    "('entity'<|#|>NAME<|#|>TYPE<|#|>DESC) and end with <|COMPLETE|>.\n\n"
    "######################\n" + filler * 18 + "\n######################"
)
print(f"prompt chars: {len(prompt)} (~{len(prompt)//4} tokens)")

c = LLMClient(provider="deepseek", max_tokens=16384)
t0 = time.time()
r = c.complete(prompt=prompt, system=None)
dt = time.time() - t0
print(f"elapsed: {dt:.1f}s degraded={r.degraded}")
print(f"text len: {len(r.text)}")
print("first 300:", r.text[:300].replace("\n", " | "))
if "COMPLETE" in r.text:
    print("COMPLETE delimiter present: YES")
