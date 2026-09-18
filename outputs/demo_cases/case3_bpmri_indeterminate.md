# 前列安汇 demo — bpMRI 不确定病灶处理 (Indeterminate bpMRI lesion workup)

**Scenario**: 71-year-old man, PSA 4.8 ng/mL, PSA density 0.12. bpMRI with adequate quality shows a PI-RADS 3 peripheral-zone lesion; mpMRI is unavailable.

**case_id**: `case3_bpmri_indeterminate` · elapsed 64.2s · graph yes

## 前列安汇 decision report

**Decision under consideration:** For a man with an indeterminate (PI-RADS 3) peripheral-zone lesion on adequate-quality bpMRI, should PSA density be used to gate the biopsy decision, and should contrast-enhanced MRI or scheduled follow-up imaging be used as ancillary workup?

**Patient scenario flags:** bpmri, indeterminate_lesion, pirads_3, psa_elevated, psad_high, quality_adequate

### Verdict: 推荐 (Consensus endorse)

PSAD gating for indeterminate bpMRI lesions reached consensus agreement (Q11, median 7); contrast-enhanced MRI for peripheral-zone indeterminate lesions (Q10a, median 7) and follow-up imaging (Q10b, median 8) both achieved consensus agreement. All components of the decision are endorsed; contrast MRI and follow-up are endorsed ancillary alternatives.

*Confidence:* 0.85

### Triggered consensus rules

- **indeterminate_lesion_ancillary_workup** (medium) — When indeterminate_lesion (PI-RADS 3) is present, compute PSAD first: biopsy when psad_high/psad_intermediate_high, defer with MRI follow-up when psad_low. On mpMRI also apply a risk calculator when risk_calculator_available. Treat biomarkers, PSMA PET and microultrasound as conditional ancillary options only — report_option, not endorsement. *[citations: 10.1016/j.eururo.2026.06.012 (ProBIOPSY consensus, Eur Urol 2026; statements Q10a-Q16, Q18, Q21, Q22); 10.1111/bju.15277 (Schoots & Padhani, BJU Int 2021 — risk-adapted biopsy decision based on prostate MRI and PSA density)]*
  - HARD: the consensus ENDORSES 'd_contrast_mri_for_pz_indeterminate' (Add contrast-enhanced MRI sequence for peripheral-zone indeterminate bpMRI lesion) — do not reject it outright.
  - HARD: the consensus ENDORSES 'd_followup_indeterminate_bpmri' (Schedule follow-up imaging for indeterminate bpMRI lesion) — do not reject it outright.
  - HARD: the consensus ENDORSES 'd_psad_gate_bpmri_indeterminate' (Use PSA density to gate biopsy for indeterminate bpMRI lesion) — do not reject it outright.

### Evidence grounding

- [EV0008|D_review|Main text / results_d1_ancillary] (score 19.51)
- [EV0035|B_consensus|Table 1 (Q10a)] (score 11.21)
- [EV0288|C_rct_meta|SM2 ref 7] (score 10.16)
- [EV0022|D_review|SM2 / sm2_d1_biomarkers] (score 9.19)
- [EV0036|B_consensus|Table 1 (Q10b)] (score 7.72)

### Citations

Q11, Q10a, Q10b, EV0008, EV0035

---
*Decision support only — not a substitute for clinical judgement. Verdicts trace to ProBIOPSY consensus statements (Eur Urol 2026).*