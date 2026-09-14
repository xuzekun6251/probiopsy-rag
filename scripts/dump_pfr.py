"""Dump patient_factor_rules from rules.yaml to stdout (file-based to dodge cmd quirks)."""
import json

import yaml

d = yaml.safe_load(open("configs/rules.yaml", encoding="utf-8"))
pfr = d.get("patient_factor_rules", [])
print("PFR count:", len(pfr))
for r in pfr:
    print(json.dumps(r, ensure_ascii=False)[:500])
