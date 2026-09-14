# 前列安汇 demo — 感染风险患者因素升级 (Patient-factor escalation: infection risk)

**Scenario**: 66-year-old man with prior prostatitis and recent hospitalisation (infection risk factors, Q62 catalogue), undergoing repeat biopsy after a prior negative biopsy with persisting suspicion.

**case_id**: `case5_infection_risk_escalation` · elapsed 0.0s · graph no

## 前列安汇 decision report

**Decision under consideration:** For a man with infection risk factors undergoing repeat prostate biopsy, should the transperineal route be preferred, and should antibiotic prophylaxis be augmented if transrectal access is used?

**Patient scenario flags:** infection_risk_factor, prior_negative_biopsy, psa_elevated

### Verdict: 有条件考虑 (Conditional / neither)

rule-only mode (no LLM arbiter) — verdict class not determined

*Confidence:* 0.00

### Triggered consensus rules

- **route_anaesthesia_prophylaxis** (high) — Default to d_route_transperineal. Use periprostatic nerve block for either route. If the patient carries infection_risk_factor (Q62 catalogue) and a transrectal route is unavoidable, give augmented antibiotic prophylaxis (report as majority position); antibiotic omission is acceptable only for transperineal biopsy without risk factors. *[citations: 10.1016/j.eururo.2026.06.012 (ProBIOPSY consensus, Eur Urol 2026; statements Q58-Q63); 10.1016/j.euo.2026.01.009 (Marra et al., Eur Urol Oncol 2026 — transperineal versus transrectal prostate biopsy: systematic review and meta-analysis of RCTs)]*
  - HARD: the consensus ENDORSES 'd_route_transperineal' (Use transperineal approach as standard route) — do not reject it outright.
- **PF-immunocompromised_or_infection_history** (high) —  *[citations: ]*
  - HARD: the consensus ENDORSES 'd_route_transperineal' (Use transperineal approach as standard route) — do not reject it outright.
- **PF-repeat_biopsy_setting** (medium) —  *[citations: ]*
  - HARD: the consensus ENDORSES 'd_route_transperineal' (Use transperineal approach as standard route) — do not reject it outright.

### Evidence grounding

- [EV0013|D_review|Main text / results_d2_route] (score 11.86)
- [EV0084|B_consensus|Table 2 (Q63)] (score 10.87)
- [EV0083|B_consensus|Table 2 (Q62)] (score 10.25)
- [EV0324|C_rct_meta|SM2 ref 62] (score 9.03)
- [EV0325|C_rct_meta|SM2 ref 63] (score 5.57)

---
*Decision support only — not a substitute for clinical judgement. Verdicts trace to ProBIOPSY consensus statements (Eur Urol 2026).*