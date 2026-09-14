"""Analyze phase4 build log: batch progress, extraction counts, error waves."""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

lines = open("outputs/phase4_build_log.txt", encoding="utf-8", errors="ignore").read().splitlines()
build_lines = [l for l in lines if l.startswith("BUILD")]
print("BUILD script lines:")
for l in build_lines[-15:]:
    print("  ", l)

n_done = sum(1 for l in lines if "Completed processing file" in l)
n_extracting = sum(1 for l in lines if "Extracting stage" in l)
n_retry = sum(1 for l in lines if "Retrying request" in l)
n_200 = sum(1 for l in lines if "HTTP/1.1 200 OK" in l)
n_err = sum(1 for l in lines if "LLM degraded" in l or "empty content" in l)
n_complete_delim = sum(1 for l in lines if "Complete delimiter can not be found" in l)
print(f"chunks completed={n_done} extracting_stages={n_extracting} "
      f"http200={n_200} retries={n_retry} degraded={n_err} missing_delim={n_complete_delim}")

# cache health
import json
try:
    cache = json.load(open("data/processed/lightrag_index/kv_store_llm_response_cache.json", encoding="utf-8"))
    vals = list(cache.values())
    poison = sum(1 for v in vals if isinstance(v, dict) and "llm error" in str(v.get("return", "")))
    print(f"cache entries={len(vals)} poison={poison}")
except FileNotFoundError:
    print("no cache file")
