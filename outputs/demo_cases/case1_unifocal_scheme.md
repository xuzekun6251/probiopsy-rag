# 前列安汇 demo — 单发病灶穿刺方案 (Unifocal lesion: TBx+PLBx vs add SBx)

**Scenario**: 62-year-old man, PSA 6.2 ng/mL. 3T mpMRI with adequate image quality (PI-QUAL v2 = 3) shows a single 9 mm PI-RADS 4 lesion in the left peripheral zone.

**case_id**: `case1_unifocal_scheme` · elapsed 0.0s · graph no

## 前列安汇 decision report

**Decision under consideration:** For a 62-year-old man with a single 9 mm PI-RADS 4 peripheral-zone lesion on adequate-quality 3T mpMRI, should the biopsy scheme be targeted biopsy plus perilesional biopsy, and should a full systematic biopsy be added?

**Patient scenario flags:** lesion_small, mpmri, mri_3t, pirads_4_5, psa_elevated, pz_lesion, quality_adequate, unifocal, visible_lesion

### Verdict: 有条件考虑 (Conditional / neither)

rule-only mode (no LLM arbiter) — verdict class not determined

*Confidence:* 0.00

### Triggered consensus rules

- **biopsy_scheme_by_lesion_distribution** (medium) — Choose the scheme by lesion distribution: unifocal → targeted + perilesional (no routine contralateral systematic cores; report contralateral addition as an option); multifocal_bilateral → bilateral targeted + perilesional. Never append a full systematic template to targeted+perilesional by default. *[citations: 10.1016/j.eururo.2026.06.012 (ProBIOPSY consensus, Eur Urol 2026; statements Q42-Q50)]*
  - HARD: the consensus explicitly REJECTS 'd_scheme_unifocal_add_sbx' (Unifocal visible lesion: add full systematic biopsy) — do not endorse it.
  - HARD: the consensus ENDORSES 'd_scheme_unifocal_tbx_plbx' (Unifocal visible lesion: targeted biopsy + perilesional biopsy) — do not reject it outright.

### Evidence grounding

- [EV0024|D_review|SM2 / sm2_d2_systematic] (score 8.88)
- [EV0004|D_review|Main text / introduction] (score 4.54)
- [EV0027|D_review|SM2 / sm2_d3_planning] (score 4.38)
- [EV0075|B_consensus|Table 2 (Q54)] (score 4.02)
- [EV0014|D_review|Main text / results_d3_focal] (score 3.72)

---
*Decision support only — not a substitute for clinical judgement. Verdicts trace to ProBIOPSY consensus statements (Eur Urol 2026).*