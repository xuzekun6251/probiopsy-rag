#!/usr/bin/env python
"""Validate configs/rules.yaml against the entity registries (Executor Phase 3).

Checks (pre-gate sanity, no network):
  1. YAML parses; >=12 rules; ids unique.
  2. Every entity_b_flag is a real decision-item id in data/seed/entities_b.csv.
  3. Every entity_a_flag is a real flag in data/seed/entities_a.csv `flags` column.
  4. Every rule has >=1 citation with source_type: literature and a DOI.
  5. Report B-item coverage (how many d_* ids are wired into rules).

Usage:
    .venv/Scripts/python.exe scripts/validate_rules.py
"""
from __future__ import annotations

import csv
import re
import sys
import io
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\]\"',]+", re.IGNORECASE)


def main() -> int:
    rules = yaml.safe_load((ROOT / "configs" / "rules.yaml").read_text(encoding="utf-8"))
    rule_list = rules.get("rules", [])
    errors: list[str] = []

    if len(rule_list) < 12:
        errors.append(f"only {len(rule_list)} rules (target 12)")
    ids = [r.get("id") for r in rule_list]
    if len(set(ids)) != len(ids):
        errors.append("duplicate rule ids")

    b_ids: set[str] = set()
    with (ROOT / "data" / "seed" / "entities_b.csv").open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            b_ids.add((list(row.values())[0] or "").strip())

    a_flags: set[str] = set()
    with (ROOT / "data" / "seed" / "entities_a.csv").open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            for f in (row.get("flags") or "").split("|"):
                f = f.strip()
                if f:
                    a_flags.add(f)

    covered_b: set[str] = set()
    for r in rule_list:
        rid = r.get("id")
        for f in r.get("entity_b_flags", []) or []:
            if f not in b_ids:
                errors.append(f"{rid}: unknown entity_b flag {f}")
            covered_b.add(f)
        for f in r.get("entity_a_flags", []) or []:
            if f not in a_flags:
                errors.append(f"{rid}: unknown entity_a flag {f}")
        cits = r.get("citations", []) or []
        if not cits:
            errors.append(f"{rid}: no citations")
        for c in cits:
            ref = c.get("ref", "") if isinstance(c, dict) else str(c)
            st = c.get("source_type") if isinstance(c, dict) else None
            if st != "literature" or not DOI_RE.search(ref):
                errors.append(f"{rid}: citation not literature+DOI: {ref!r}")

    print(f"[validate_rules] rules={len(rule_list)}  "
          f"b_coverage={len(covered_b)}/{len(b_ids)}  "
          f"a_flags_used={sum(len(r.get('entity_a_flags') or []) for r in rule_list)}")
    for r in rule_list:
        n_cit = len(r.get("citations") or [])
        print(f"  {r['id']:<44} sev={r['severity']:<6} A={len(r['entity_a_flags'])} "
              f"B={len(r['entity_b_flags'])} cits={n_cit}")
    if errors:
        print("\n[validate_rules] FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("[validate_rules] OK — all flags/citations cross-reference cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
