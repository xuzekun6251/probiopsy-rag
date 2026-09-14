"""Run the Phase 6 demo cases through the full three-layer pipeline.

Each case is a clinically coherent patient scenario (Entity A flags) plus the
biopsy decision item(s) under consideration (Entity B ids). The pipeline is
the SAME composition the benchmark validates (rule engine → LightRAG graph
context + lexical retrieval → SafetyAgent arbiter), so the demoed system is
the evaluated system.

Outputs: outputs/demo_cases/<case_id>.md (rendered report) and
         outputs/demo_cases/<case_id>.json (machine-readable verdict/meta).

Usage:
    .venv/Scripts/python.exe scripts/run_demo_cases.py [--case case1,...] [--no-llm] [--no-graph]
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from probiopsy_rag_agent.lightrag_adapter import LightRAGAdapter  # noqa: E402
from probiopsy_rag_agent.llm_client import LLMClient              # noqa: E402
from probiopsy_rag_agent.pipeline import (                        # noqa: E402
    INDEX_DIR, ProjectAssets, load_assets, run_pipeline,
)
from probiopsy_rag_agent.safety_agent import SafetyAgent          # noqa: E402

DEMO_CASES = [
    {
        "case_id": "case1_unifocal_scheme",
        "title": "单发病灶穿刺方案 (Unifocal lesion: TBx+PLBx vs add SBx)",
        "scenario": (
            "62-year-old man, PSA 6.2 ng/mL. 3T mpMRI with adequate image quality "
            "(PI-QUAL v2 = 3) shows a single 9 mm PI-RADS 4 lesion in the left "
            "peripheral zone."
        ),
        "patient_flags": [
            "psa_elevated", "mpmri", "mri_3t", "quality_adequate",
            "visible_lesion", "pirads_4_5", "pz_lesion", "unifocal", "lesion_small",
        ],
        "decision_items": ["d_scheme_unifocal_tbx_plbx", "d_scheme_unifocal_add_sbx"],
        "question": (
            "For a 62-year-old man with a single 9 mm PI-RADS 4 peripheral-zone "
            "lesion on adequate-quality 3T mpMRI, should the biopsy scheme be "
            "targeted biopsy plus perilesional biopsy, and should a full "
            "systematic biopsy be added?"
        ),
    },
    {
        "case_id": "case2_psma_pet_upfront",
        "title": "PSMA PET 替代 MRI 先行 (PSMA PET instead of MRI upfront)",
        "scenario": (
            "68-year-old biopsy-naive man, PSA 9.1 ng/mL, high clinical suspicion. "
            "The centre offers PSMA PET-CT and considers skipping MRI."
        ),
        "patient_flags": ["psa_elevated", "suspicion_high", "psma_pet_available", "imaging_available"],
        "decision_items": ["d_reject_psma_pet_upfront"],
        "question": (
            "For a biopsy-naive man with elevated PSA and high clinical suspicion, "
            "should PSMA PET-CT be preferred over MRI as the primary imaging test "
            "before prostate biopsy?"
        ),
    },
    {
        "case_id": "case3_bpmri_indeterminate",
        "title": "bpMRI 不确定病灶处理 (Indeterminate bpMRI lesion workup)",
        "scenario": (
            "71-year-old man, PSA 4.8 ng/mL, PSA density 0.12. bpMRI with adequate "
            "quality shows a PI-RADS 3 peripheral-zone lesion; mpMRI is unavailable."
        ),
        "patient_flags": [
            "psa_elevated", "bpmri", "quality_adequate", "pirads_3",
            "indeterminate_lesion", "psad_high",
        ],
        "decision_items": [
            "d_psad_gate_bpmri_indeterminate",
            "d_contrast_mri_for_pz_indeterminate",
            "d_followup_indeterminate_bpmri",
        ],
        "question": (
            "For a man with an indeterminate (PI-RADS 3) peripheral-zone lesion on "
            "adequate-quality bpMRI, should PSA density be used to gate the biopsy "
            "decision, and should contrast-enhanced MRI or scheduled follow-up "
            "imaging be used as ancillary workup?"
        ),
    },
    {
        "case_id": "case4_advanced_route_prophylaxis",
        "title": "晚期疾病穿刺方案与路线 (Advanced disease: reduced SBx, TP route, no ABx)",
        "scenario": (
            "77-year-old man, PSA 54 ng/mL, suspected locally advanced disease, "
            "unfit for curative treatment. No infection risk factors."
        ),
        "patient_flags": [
            "psa_gt_50", "advanced_disease", "locally_advanced_suspected", "unfit_curative",
        ],
        "decision_items": [
            "d_sbx_reduced_6core_advanced", "d_route_transperineal", "d_omit_abx_tp_no_risk",
        ],
        "question": (
            "For a man with suspected locally advanced disease who is unfit for "
            "curative treatment, should systematic biopsy be reduced to a maximum "
            "of 6 cores, and should a transperineal route without antibiotic "
            "prophylaxis be used?"
        ),
    },
    {
        "case_id": "case5_infection_risk_escalation",
        "title": "感染风险患者因素升级 (Patient-factor escalation: infection risk)",
        "scenario": (
            "66-year-old man with prior prostatitis and recent hospitalisation "
            "(infection risk factors, Q62 catalogue), undergoing repeat biopsy "
            "after a prior negative biopsy with persisting suspicion."
        ),
        "patient_flags": ["infection_risk_factor", "prior_negative_biopsy", "psa_elevated"],
        "decision_items": ["d_route_transperineal", "d_augmented_abx_tr"],
        "question": (
            "For a man with infection risk factors undergoing repeat prostate "
            "biopsy, should the transperineal route be preferred, and should "
            "antibiotic prophylaxis be augmented if transrectal access is used?"
        ),
    },
]

OUT_DIR = ROOT / "outputs" / "demo_cases"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default="all", help="comma-separated case ids, or 'all'")
    ap.add_argument("--no-llm", action="store_true", help="rule engine + retrieval only")
    ap.add_argument("--no-graph", action="store_true", help="skip LightRAG, lexical only")
    args = ap.parse_args()

    cases = DEMO_CASES if args.case == "all" else [
        c for c in DEMO_CASES if c["case_id"] in {s.strip() for s in args.case.split(",")}
    ]
    unknown = {args.case} - {c["case_id"] for c in cases} if args.case != "all" else set()
    if unknown:
        print(f"[demo] unknown case ids: {unknown}")
        return 1

    load_env = ROOT / ".env"
    if load_env.exists():
        for line in load_env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                import os
                os.environ.setdefault(k.strip(), v.strip())

    assets: ProjectAssets = load_assets()
    adapter = None
    agent = None
    if not args.no_graph:
        try:
            adapter = LightRAGAdapter(working_dir=str(INDEX_DIR), language="English")
        except Exception as e:
            print(f"[demo] LightRAG unavailable ({e}); falling back to lexical-only")
    if not args.no_llm:
        agent = SafetyAgent(client=LLMClient(provider="deepseek", temperature=0.0, max_tokens=2048))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[demo] {len(cases)} cases | llm={'on' if agent else 'OFF'} "
          f"graph={'on' if adapter else 'OFF'}\n")

    for c in cases:
        print(f"=== {c['case_id']} — {c['title']}")
        res = run_pipeline(
            question=c["question"],
            patient_flags=c["patient_flags"],
            decision_items=c["decision_items"],
            assets=assets,
            adapter=adapter,
            agent=agent,
            use_graph=not args.no_graph,
        )
        header = (
            f"# 前列安汇 demo — {c['title']}\n\n"
            f"**Scenario**: {c['scenario']}\n\n"
            f"**case_id**: `{c['case_id']}` · elapsed {res.elapsed:.1f}s · "
            f"graph {'yes' if res.graph_context.strip() and 'failed' not in res.graph_context[:40] else 'no'}\n\n"
        )
        (OUT_DIR / f"{c['case_id']}.md").write_text(header + res.report_md, encoding="utf-8")
        meta = {
            "case_id": c["case_id"],
            "title": c["title"],
            "question": c["question"],
            "patient_flags": res.patient_flags,
            "decision_items": res.decision_items,
            "rules_fired": [m.rule.rule_id for m in res.rule_matches],
            "hard_constraints": [hc for m in res.rule_matches for hc in m.hard_constraints],
            "verdict": res.verdict,
            "elapsed_s": round(res.elapsed, 2),
            "lexical_top": [
                {"evidence_id": r.chunk.chunk_id, "score": round(r.score, 2),
                 "locator": r.chunk.source_locator}
                for r in res.lexical_hits[:3]
            ],
        }
        (OUT_DIR / f"{c['case_id']}.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        v = res.verdict
        print(f"  verdict: {v.get('action')} (conf {v.get('confidence')})"
              f"{' [degraded]' if v.get('degraded') else ''}")
        print(f"  rules: {', '.join(m.rule.rule_id for m in res.rule_matches) or '(none)'}")
        seen_hc: set[str] = set()
        for hc in [h for m in res.rule_matches for h in m.hard_constraints]:
            if hc in seen_hc:
                continue
            seen_hc.add(hc)
            print(f"    {hc[:120]}")
        print(f"  saved: outputs/demo_cases/{c['case_id']}.md\n")

    print(f"[demo] done → {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
