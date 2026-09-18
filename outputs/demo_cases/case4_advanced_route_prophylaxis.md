# 前列安汇 demo — 晚期疾病穿刺方案与路线 (Advanced disease: reduced SBx, TP route, no ABx)

**Scenario**: 77-year-old man, PSA 54 ng/mL, suspected locally advanced disease, unfit for curative treatment. No infection risk factors.

**case_id**: `case4_advanced_route_prophylaxis` · elapsed 31.7s · graph yes

## 前列安汇 decision report

**Decision under consideration:** For a man with suspected locally advanced disease who is unfit for curative treatment, should systematic biopsy be reduced to a maximum of 6 cores, and should a transperineal route without antibiotic prophylaxis be used?

**Patient scenario flags:** advanced_disease, locally_advanced_suspected, psa_gt_50, unfit_curative

### Verdict: 推荐 (Consensus endorse)

Q57 (median 8, consensus agree) endorses reducing systematic biopsy to max 6 cores for suspected locally advanced disease (DRE and/or PSA>50) or unfitness for curative treatment. Q58 (97%) endorses transperineal as standard route; Q62 (88%) supports omitting antibiotic prophylaxis for transperineal biopsy absent infection risk factors.

*Confidence:* 0.90

### Triggered consensus rules

- **advanced_disease_reduced_systematic_scheme** (high) — For advanced_disease / unfit_curative patients (e.g. psa_gt_50, locally_advanced_suspected), offer a reduced 6-core systematic biopsy (plus lesion-targeted cores when a visible lesion exists); do not use saturation templates. *[citations: 10.1016/j.eururo.2026.06.012 (ProBIOPSY consensus, Eur Urol 2026; statements Q57, Q54, Q56)]*
  - HARD: the consensus ENDORSES 'd_sbx_reduced_6core_advanced' (Reduce SBx to max 6 cores for suspected locally advanced disease, PSA>50, or unfit for curative treatment) — do not reject it outright.
- **route_anaesthesia_prophylaxis** (high) — Default to d_route_transperineal. Use periprostatic nerve block for either route. If the patient carries infection_risk_factor (Q62 catalogue) and a transrectal route is unavoidable, give augmented antibiotic prophylaxis (report as majority position); antibiotic omission is acceptable only for transperineal biopsy without risk factors. *[citations: 10.1016/j.eururo.2026.06.012 (ProBIOPSY consensus, Eur Urol 2026; statements Q58-Q63); 10.1016/j.euo.2026.01.009 (Marra et al., Eur Urol Oncol 2026 — transperineal versus transrectal prostate biopsy: systematic review and meta-analysis of RCTs)]*
  - HARD: the consensus ENDORSES 'd_omit_abx_tp_no_risk' (Omit antibiotic prophylaxis for transperineal biopsy unless infection risk factors present) — do not reject it outright.
  - HARD: the consensus ENDORSES 'd_route_transperineal' (Use transperineal approach as standard route) — do not reject it outright.
- **PF-unfit_for_curative_treatment** (medium) —  *[citations: ]*
  - HARD: the consensus ENDORSES 'd_sbx_reduced_6core_advanced' (Reduce SBx to max 6 cores for suspected locally advanced disease, PSA>50, or unfit for curative treatment) — do not reject it outright.

### Evidence grounding

- [EV0079|B_consensus|Table 2 (Q57)] (score 15.28)
- [EV0320|C_rct_meta|SM2 ref 57] (score 10.03)
- [EV0013|D_review|Main text / results_d2_route] (score 9.54)
- [EV0324|C_rct_meta|SM2 ref 62] (score 7.36)
- [EV0084|B_consensus|Table 2 (Q63)] (score 6.30)

### Citations

Q57, Q58, Q62, EV0079, EV0013, EV0320

---
*Decision support only — not a substitute for clinical judgement. Verdicts trace to ProBIOPSY consensus statements (Eur Urol 2026).*