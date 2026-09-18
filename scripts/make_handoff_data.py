"""Generate handoff artifacts: outputs/tables/*.csv + outputs/figures/source_data/*.csv.

All values come from real project artifacts:
  - configs/rules.yaml                     -> rule_list.csv, figure4 severities
  - data/seed/entities_{a,b}.csv           -> registry_summary.csv
  - data/seed/probiopsy_statements.csv     -> validation_distribution.csv
  - outputs/evaluation_summary.json        -> performance_matrix.csv, figure2
  - outputs/demo_cases/case*.json          -> figure3 (system side), figure4, figure5
  - data/seed/evidence_chunks.jsonl        -> figure4 evidence levels/sources
  - data/processed/lightrag_index graphml  -> figure5_paths.csv (top-weight edges)

No value is invented: expert-panel columns (figure3) are emitted blank because
the expert blind review (Planner phase 4.5) is a pending manual step; blank
means "not yet collected", never "measured".
"""
from __future__ import annotations

import csv
import json
import re
import time
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
SRC = ROOT / "outputs" / "figures" / "source_data"
TABLES.mkdir(parents=True, exist_ok=True)
SRC.mkdir(parents=True, exist_ok=True)

METHOD_LABEL = {
    "pure_llm": "pure_llm",
    "naive_rag": "naive_rag",
    "lightrag": "lightrag",
    "probiopsy-rag": "full_system",
}
ACTIONS = ["endorse", "endorse_option", "conditional", "report_option", "against"]


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    print(f"  {path.relative_to(ROOT)}  ({len(rows)} rows)")


def first_sentence(text: str, limit: int = 220) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= limit:
        return text
    cut = text[:limit]
    stop = max(cut.rfind(". "), cut.rfind("。"), cut.rfind("; "))
    return (cut[: stop + 1] if stop > 40 else cut.rstrip() + "…")


# --------------------------------------------------------------------------- #
# 1. registry_summary.csv
# --------------------------------------------------------------------------- #
def gen_registry() -> None:
    rows = []
    for reg, fname in (("A_patient_scenarios", "entities_a.csv"),
                       ("B_decision_items", "entities_b.csv")):
        with (ROOT / "data" / "seed" / fname).open(encoding="utf-8-sig") as fh:
            items = list(csv.DictReader(fh))
        cats = Counter(r["category"] if reg.startswith("A") else r["drug_class"] for r in items)
        n_flags = len({f.strip() for r in items for f in (r.get("flags") or "").split("|") if f.strip()})
        cat_str = "; ".join(f"{k}={v}" for k, v in sorted(cats.items(), key=lambda x: -x[1]))
        rows.append([reg, len(items), n_flags, cat_str, f"data/seed/{fname}"])
    write_csv(TABLES / "registry_summary.csv",
              ["registry", "n_items", "n_unique_flags", "category_breakdown", "source_file"], rows)


# --------------------------------------------------------------------------- #
# 2. rule_list.csv
# --------------------------------------------------------------------------- #
def gen_rules() -> None:
    cfg = yaml.safe_load((ROOT / "configs" / "rules.yaml").read_text(encoding="utf-8"))
    rows = []
    for r in cfg.get("rules", []):
        rows.append([r["id"], "consensus", r.get("severity", ""), r.get("risk_type", ""),
                     len(r.get("entity_a_flags") or []), len(r.get("entity_b_flags") or []),
                     first_sentence(r.get("rationale", ""))])
    pfr = cfg.get("patient_factor_rules", {})
    pfr_items = (pfr.items() if isinstance(pfr, dict)
                 else enumerate(pfr))
    for rid, r in pfr_items:
        if isinstance(r, dict) and "id" not in r:
            r = {"id": rid, **r}
        a_flags = r.get("matching_entity_a_flags") or r.get("entity_a_flags")
        b_flags = r.get("matching_entity_b_flags") or r.get("entity_b_flags")
        rows.append([r["id"], "patient_factor", r.get("severity", ""), r.get("risk_type", ""),
                     len(a_flags or []), len(b_flags or []),
                     first_sentence(r.get("rationale", ""))])
    write_csv(TABLES / "rule_list.csv",
              ["rule_id", "rule_set", "severity", "risk_type", "n_trigger_flags_a",
               "n_target_flags_b", "rationale_first_sentence"], rows)
    return cfg


# --------------------------------------------------------------------------- #
# 3. performance_matrix.csv + figure2_performance.csv
# --------------------------------------------------------------------------- #
def gen_performance() -> None:
    summary = json.loads((ROOT / "outputs" / "evaluation_summary.json").read_text(encoding="utf-8"))
    wide, per_seed = [], []
    for method, block in summary["methods"].items():
        agg = block["aggregate"]

        def cell(k: str) -> str:
            m, s = agg[k]["mean"], agg[k]["sd"]
            return f"{m:.3f}±{s:.3f}"

        wide.append([METHOD_LABEL.get(method, method),
                     cell("exact5"), cell("exact3"), cell("macro_f1"), cell("kappa"),
                     cell("against_sensitivity"), cell("against_specificity"),
                     cell("against_f1"), f"{agg['context_chars']['mean']:.0f}"])
        for sd in block["seeds"]:
            per_seed.append([METHOD_LABEL.get(method, method), "benchmark", sd["seed"],
                             round(sd["against_sensitivity"], 4), round(sd["against_specificity"], 4),
                             round(sd["against_f1"], 4), round(sd["exact5"], 4),
                             round(sd["kappa"], 4), round(sd["context_chars"], 1)])
    write_csv(TABLES / "performance_matrix.csv",
              ["method", "exact5", "exact3", "macro_f1", "cohens_kappa",
               "against_sensitivity", "against_specificity", "against_f1",
               "mean_context_chars"], wide)
    write_csv(SRC / "figure2_performance.csv",
              ["method", "phase", "seed", "sensitivity_high", "specificity_high",
               "f1_high", "exact_4_level_accuracy", "cohens_kappa", "context_chars"], per_seed)
    return summary


# --------------------------------------------------------------------------- #
# 4. validation_distribution.csv
# --------------------------------------------------------------------------- #
def gen_validation() -> None:
    with (ROOT / "data" / "seed" / "probiopsy_statements.csv").open(encoding="utf-8-sig") as fh:
        gold = list(csv.DictReader(fh))
    domains = sorted({r["domain"] for r in gold})
    rows = []
    for dom in domains:
        sub = [r for r in gold if r["domain"] == dom]
        acts = Counter(r["expected_system_action"] for r in sub)
        rows.append([dom, len(sub)] + [acts.get(a, 0) for a in ACTIONS]
                    + [f"{acts.get('against', 0) / len(sub):.1%}"])
    tot = len(gold)
    all_acts = Counter(r["expected_system_action"] for r in gold)
    rows.append(["ALL", tot] + [all_acts.get(a, 0) for a in ACTIONS]
                + [f"{all_acts.get('against', 0) / tot:.1%}"])
    write_csv(TABLES / "validation_distribution.csv",
              ["domain", "n_statements"] + [f"gold_{a}" for a in ACTIONS]
              + ["pct_against"], rows)


# --------------------------------------------------------------------------- #
# 5. figure1_architecture.csv
# --------------------------------------------------------------------------- #
def gen_fig1() -> None:
    rows = [
        ["normalize", "deterministic", "patient scenario + decision item + free-text factors",
         "normalized flag set (Entity A flags × Entity B flags) + patient factors",
         "src/probiopsy_rag_agent/normalize.py"],
        ["rule_engine", "deterministic", "normalized flags × decision items",
         "matched consensus rules + patient-factor escalations + hard constraints",
         "src/probiopsy_rag_agent/risk_rules.py; configs/rules.yaml (16 rules)"],
        ["evidence_store", "retrieval", "question + entity boosts",
         "top-k lexical evidence chunks (BM25-style scoring)",
         "src/probiopsy_rag_agent/evidence_store.py; data/seed/evidence_chunks.jsonl (n=?…)"],
        ["lightrag_kg", "retrieval", "question (risk-guided)",
         "knowledge-graph context: entities, relations, chunks (mode=hybrid, context-only)",
         "src/probiopsy_rag_agent/lightrag_adapter.py; data/processed/lightrag_index"],
        ["llm_arbiter", "arbitration", "rules hard constraints + graph context + lexical evidence",
         "5-class action verdict + confidence + rationale + statement citations",
         "src/probiopsy_rag_agent/safety_agent.py; src/probiopsy_rag_agent/llm_client.py"],
    ]
    chunks = sum(1 for _ in (ROOT / "data" / "seed" / "evidence_chunks.jsonl").open(encoding="utf-8"))
    rows[2][4] = rows[2][4].replace("(n=?…)", f"(n={chunks})")
    write_csv(SRC / "figure1_architecture.csv",
              ["component", "layer", "inputs", "outputs", "source_code_file"], rows)


# --------------------------------------------------------------------------- #
# 6. figure3_expert_agreement.csv (system side only; expert columns BLANK)
# --------------------------------------------------------------------------- #
def gen_fig3() -> None:
    rows = []
    for jp in sorted((ROOT / "outputs" / "demo_cases").glob("case*.json")):
        d = json.loads(jp.read_text(encoding="utf-8"))
        for expert in (1, 2, 3, 4):
            rows.append([d["case_id"], expert, "", "", "", d["verdict"]["action"],
                         "", "", "", "", ""])
    write_csv(SRC / "figure3_expert_agreement.csv",
              ["case_id", "expert_id", "expert_rating", "system_output",
               "expert_majority", "llm_arbiter_decision",
               "likert_clarity", "likert_usefulness", "likert_recommendation",
               "likert_evidence", "note"], rows)


# --------------------------------------------------------------------------- #
# 7. figure4_demo_case.csv
# --------------------------------------------------------------------------- #
def gen_fig4(cfg) -> None:
    sev, rtype = {}, {}
    pfr = cfg.get("patient_factor_rules", {})
    pfr_items = (pfr.values() if isinstance(pfr, dict) else pfr)
    for r in list(cfg.get("rules", [])) + list(pfr_items):
        if isinstance(r, dict) and "id" not in r:
            continue  # keyed-by-id entries were flattened in gen_rules; skip raw dicts
        sev[r["id"]] = r.get("severity", "unknown")
        rtype[r["id"]] = r.get("risk_type", "")
    levels = {}
    with (ROOT / "data" / "seed" / "evidence_chunks.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                e = json.loads(line)
                levels[e["evidence_id"]] = (e.get("evidence_level", ""), e.get("pmid", ""))
    rows = []
    for jp in sorted((ROOT / "outputs" / "demo_cases").glob("case*.json")):
        d = json.loads(jp.read_text(encoding="utf-8"))
        case, action = d["case_id"], d["verdict"]["action"]
        rule_ids = d.get("rules_fired") or []
        evs = d.get("lexical_top") or []
        n = max(len(rule_ids), len(evs), 1)
        for i in range(n):
            rid = rule_ids[i] if i < len(rule_ids) else ""
            ev = evs[i] if i < len(evs) else {}
            eid = ev.get("evidence_id", "")
            lvl, pmid = levels.get(eid, ("", ""))
            rows.append([case, "", "; ".join(d.get("decision_items") or []),
                         "|".join(d.get("patient_flags") or []),
                         rid, sev.get(rid, ""), rtype.get(rid, ""),
                         eid, lvl, ev.get("locator", ""), pmid, action, action])
    write_csv(SRC / "figure4_demo_case.csv",
              ["case_id", "entity_a_id", "entity_b_id", "patient_factors", "rule_id",
               "rule_severity", "rule_mechanism", "evidence_chunk_id", "evidence_level",
               "evidence_source", "evidence_pmid", "llm_arbiter_decision",
               "final_risk_level"], rows)


# --------------------------------------------------------------------------- #
# 8. figure5_reasoning_trace.csv + figure5_paths.csv
# --------------------------------------------------------------------------- #
def gen_fig5(cfg) -> None:
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from probiopsy_rag_agent.risk_rules import (
        load_decision_items,
        load_patient_factor_rules,
        load_rules,
        match_patient_factors,
        match_rules,
    )

    rules = load_rules(ROOT / "configs" / "rules.yaml")
    items = load_decision_items(ROOT / "data" / "seed" / "entities_b.csv")
    pfrs = load_patient_factor_rules(ROOT / "configs" / "rules.yaml")

    rows, case_rows = [], []
    for jp in sorted((ROOT / "outputs" / "demo_cases").glob("case*.json")):
        d = json.loads(jp.read_text(encoding="utf-8"))
        flags = set(d.get("patient_flags") or [])
        dset = {x for x in (d.get("decision_items") or [])}
        t0 = time.perf_counter()
        m = match_rules(rules, flags, dset, items) + match_patient_factors(pfrs, flags, dset, items)
        rule_ms = (time.perf_counter() - t0) * 1000
        action = d["verdict"]["action"]
        case_rows.append([d["case_id"], 1, "rule_engine",
                          "match consensus rules (flags × decision items)",
                          round(rule_ms, 1), f"{len(flags)} flags × {len(dset)} items",
                          f"{len(m)} rule(s) fired"])
        case_rows.append([d["case_id"], 2, "llm_arbiter",
                          "full decision pass (rule gate + retrieval + GLM arbitration)",
                          round(float(d.get("elapsed_s") or 0) * 1000, 1),
                          f"{len(m)} rule(s) + graph & lexical evidence",
                          f"action={action}, confidence={d['verdict'].get('confidence')}"])
    rows = case_rows
    write_csv(SRC / "figure5_reasoning_trace.csv",
              ["case_id", "step_id", "layer", "step_label", "duration_ms",
               "input_summary", "output_summary"], rows)

    # top-weight graph edges from the built index (real LightRAG graphml)
    graphml = ROOT / "data" / "processed" / "lightrag_index" / "graph_chunk_entity_relation.graphml"
    edges = []
    if graphml.exists():
        ns = {"g": "http://graphml.graphdrawing.org/xmlns"}
        tree = ET.parse(graphml)
        names = {}
        for k in tree.findall(".//g:key", ns):
            if k.get("attr.name") == "weight":
                names[k.get("id")] = "weight"
        for e in tree.findall(".//g:edge", ns):
            w = 0.0
            for data in e.findall("g:data", ns):
                if data.get("key") in names:
                    try:
                        w = float(data.text or 0)
                    except ValueError:
                        pass
            kw = ""
            for data in e.findall("g:data", ns):
                pass
            edges.append((e.get("source"), e.get("target"), w))
        edges.sort(key=lambda x: -x[2])
    write_csv(SRC / "figure5_paths.csv",
              ["source_node", "target_node", "weight", "path_type"],
              [[s, t, round(w, 3), "knowledge_graph_edge"] for s, t, w in edges[:40]])


def main() -> int:
    print("[handoff-data] generating tables + figure source data")
    gen_registry()
    cfg = gen_rules()
    gen_performance()
    gen_validation()
    gen_fig1()
    gen_fig3()
    gen_fig4(cfg)
    gen_fig5(cfg)
    print("[handoff-data] done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
