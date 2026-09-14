"""Heavy extraction probe against glm-5.3-flash: quality + speed + repeat rate.

Runs the extraction-style prompt N times back-to-back at 3s spacing to check
(1) format fidelity (entity tuples + COMPLETE delimiter), (2) latency,
(3) whether the flash tier tolerates burst demand (no 1302).
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
os.environ["LLM_MIN_INTERVAL"] = "3"

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

for model in ["glm-5.3-flash", "glm-4.7"]:
    c = LLMClient(provider="deepseek", max_tokens=16384)
    c.model = model  # override
    print(f"=== {model}")
    ok = 0
    for i in range(4):
        t0 = time.time()
        r = c.complete(prompt=prompt)
        dt = time.time() - t0
        n_ent = r.text.count("'entity'") + r.text.count("entity<|#|>")
        has_complete = "COMPLETE" in r.text
        if not r.degraded and has_complete:
            ok += 1
        print(f"  call {i+1}: {dt:5.1f}s degraded={r.degraded} len={len(r.text):5d} "
              f"entities~{n_ent} COMPLETE={has_complete}")
        if i == 0 and not r.degraded:
            print("  sample:", r.text[:160].replace("\n", " | "))
        time.sleep(3)
    print(f"  -> {ok}/4 valid")
