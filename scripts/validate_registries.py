# -*- coding: utf-8 -*-
"""Validate Phase 1 registries + statement gold standard, then mark phase1 complete.

Checks:
  1. entities_a.csv rows parse as schemas.EntityA; flags snake_case, non-empty
  2. entities_b.csv rows parse as schemas.EntityB; endorsement/action/topic tags valid
  3. probiopsy_statements.csv: 112 rows; decision_item_id refs exist in entities_b;
     scenario_flags exist in the union of entity-A flags
  4. 29/36 stems with consensus agreement (paper abstract consistency)
"""
from __future__ import annotations

import csv
import io
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from probiopsy_rag_agent.schemas import EntityA, EntityB  # noqa: E402

MASTER_SCRIPTS = Path.home() / ".zcode" / "skills" / "medical-agent" / "scripts"

FLAG_RE = re.compile(r"^[a-z][a-z0-9_.]*$")
VALID_DOMAINS = {"indication", "procedure", "treatment_planning"}
TOPIC_TAGS = {
    "topic_imaging_pathway", "topic_reporting", "topic_ancillary", "topic_ai",
    "topic_tbx_cores", "topic_plbx", "topic_scheme", "topic_sbx_template",
    "topic_route", "topic_anaesthesia", "topic_prophylaxis", "topic_treatment_planning",
}


def load_a() -> list[EntityA]:
    out = []
    with io.open(ROOT / "data/seed/entities_a.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["aliases"] = [x for x in (row.get("aliases") or "").split("|") if x]
            row["active_mechanisms"] = [x for x in (row.get("active_mechanisms") or "").split("|") if x]
            row["flags"] = [x for x in (row.get("flags") or "").split("|") if x]
            row["evidence_sources"] = [x for x in (row.get("evidence_sources") or "").split("|") if x]
            out.append(EntityA(**row))
    return out


def load_b() -> list[EntityB]:
    out = []
    with io.open(ROOT / "data/seed/entities_b.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["aliases"] = [x for x in (row.get("aliases") or "").split("|") if x]
            row["flags"] = [x for x in (row.get("flags") or "").split("|") if x]
            row["metabolic_pathways"] = [x for x in (row.get("metabolic_pathways") or "").split("|") if x]
            row["transporter_substrates"] = [x for x in (row.get("transporter_substrates") or "").split("|") if x]
            row["narrow_therapeutic_index"] = row.get("narrow_therapeutic_index", "0") in ("1", "True", "true")
            out.append(EntityB(**row))
    return out


def main() -> int:
    errors: list[str] = []

    a_rows = load_a()
    b_rows = load_b()
    print(f"[check] EntityA rows: {len(a_rows)} (target >=50)")
    print(f"[check] EntityB rows: {len(b_rows)} (target >=40)")
    if len(a_rows) < 50:
        errors.append(f"EntityA {len(a_rows)} < 50")
    if len(b_rows) < 40:
        errors.append(f"EntityB {len(b_rows)} < 40")

    a_flags: set[str] = set()
    for e in a_rows:
        if not e.flags:
            errors.append(f"EntityA {e.entity_a_id}: empty flags")
        for fl in e.flags:
            if not FLAG_RE.match(fl):
                errors.append(f"EntityA {e.entity_a_id}: bad flag '{fl}'")
            a_flags.add(fl)

    b_ids: set[str] = set()
    for e in b_rows:
        b_ids.add(e.entity_b_id)
        tags = set(e.flags)
        endorsement = tags & {"endorsement_consensus", "endorsement_majority",
                              "endorsement_against", "endorsement_neither"}
        action = tags & {"action_recommend", "action_against",
                         "action_conditional", "action_report_only"}
        if len(endorsement) != 1:
            errors.append(f"EntityB {e.entity_b_id}: endorsement tags = {endorsement}")
        if len(action) != 1:
            errors.append(f"EntityB {e.entity_b_id}: action tags = {action}")
        bad_topic = {t for t in tags if t.startswith("topic_")} - TOPIC_TAGS
        if bad_topic:
            errors.append(f"EntityB {e.entity_b_id}: unknown topic tags {bad_topic}")

    # statements gold standard
    stmts: list[dict] = []
    with io.open(ROOT / "data/seed/probiopsy_statements.csv", encoding="utf-8") as f:
        stmts = list(csv.DictReader(f))
    print(f"[check] gold statements: {len(stmts)} (target 112)")
    if len(stmts) != 112:
        errors.append(f"statements {len(stmts)} != 112")
    if {s["domain"] for s in stmts} != VALID_DOMAINS:
        errors.append("statement domains incomplete")

    unknown_dec = {s["decision_item_id"] for s in stmts} - b_ids - {""}
    if unknown_dec:
        errors.append(f"statement decision_item_id not in EntityB: {unknown_dec}")

    unknown_flags: set[str] = set()
    for s in stmts:
        for fl in (s.get("scenario_flags") or "").split("|"):
            if fl and fl not in a_flags:
                unknown_flags.add(fl)
    if unknown_flags:
        errors.append(f"statement scenario_flags not in EntityA flag vocab: {unknown_flags}")

    stems_agreed = {s["stem_no"] for s in stmts
                    if s["interpretation"] in ("Consensus agree", "Consensus")}
    if len(stems_agreed) != 29:
        errors.append(f"consensus stems {len(stems_agreed)} != 29")
    else:
        print(f"[check] consensus stems: {len(stems_agreed)}/36 (paper: 29/36) OK")

    if errors:
        print("\n[FAIL] validation errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("\n[PASS] all registry + gold-standard checks passed")
    _mark_phase_complete()
    return 0


def _mark_phase_complete() -> None:
    progress_path = ROOT / ".executor" / "progress.json"
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress: dict = {}
    if progress_path.exists():
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
    progress.setdefault("phases", {})["phase1"] = {"status": "complete"}
    progress_path.write_text(json.dumps(progress, indent=2), encoding="utf-8")
    if MASTER_SCRIPTS.exists():
        subprocess.run(
            [sys.executable, str(MASTER_SCRIPTS / "update_state.py"),
             "--project-root", str(ROOT),
             "--phase", "executor.phase1",
             "--stage", "executor",
             "--event", "executor.phase1 completed",
             "--skill", "medical-agent-executor"],
            check=False,
        )


if __name__ == "__main__":
    sys.exit(main())
