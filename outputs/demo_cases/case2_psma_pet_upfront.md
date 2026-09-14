# 前列安汇 demo — PSMA PET 替代 MRI 先行 (PSMA PET instead of MRI upfront)

**Scenario**: 68-year-old biopsy-naive man, PSA 9.1 ng/mL, high clinical suspicion. The centre offers PSMA PET-CT and considers skipping MRI.

**case_id**: `case2_psma_pet_upfront` · elapsed 0.0s · graph no

## 前列安汇 decision report

**Decision under consideration:** For a biopsy-naive man with elevated PSA and high clinical suspicion, should PSMA PET-CT be preferred over MRI as the primary imaging test before prostate biopsy?

**Patient scenario flags:** imaging_available, psa_elevated, psma_pet_available, suspicion_high

### Verdict: 有条件考虑 (Conditional / neither)

rule-only mode (no LLM arbiter) — verdict class not determined

*Confidence:* 0.00

### Triggered consensus rules

- **upfront_new_imaging_rejection** (high) — If psma_pet_available or microultrasound_available, do NOT route the patient to these modalities as the primary biopsy gate. Use PI-QUAL-checked MRI first; reserve PSMA PET / microultrasound for the ancillary indications encoded in R02/R03. *[citations: 10.1016/j.eururo.2026.06.012 (ProBIOPSY consensus, Eur Urol 2026; statements Q17, Q20)]*
  - HARD: the consensus explicitly REJECTS 'd_reject_psma_pet_upfront' (Do NOT prefer PSMA PET over MRI for primary PCa diagnosis) — do not endorse it.

### Evidence grounding

- [EV0045|B_consensus|Table 1 (Q19)] (score 14.31)
- [EV0043|B_consensus|Table 1 (Q17)] (score 11.52)
- [EV0044|B_consensus|Table 1 (Q18)] (score 11.25)
- [EV0009|D_review|Main text / results_d1_novel] (score 10.90)
- [EV0022|D_review|SM2 / sm2_d1_biomarkers] (score 8.44)

---
*Decision support only — not a substitute for clinical judgement. Verdicts trace to ProBIOPSY consensus statements (Eur Urol 2026).*