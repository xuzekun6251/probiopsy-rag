# Supplementary Material — QianLieAnHui (probiopsy-rag)

All values in this document are generated programmatically from the released
evaluation artifacts (`outputs/evaluation_summary.json`,
`outputs/tables/internal_review_stats.json`, `outputs/baseline_predictions.jsonl`,
`outputs/evaluation_summary_glm53_baselines.json`, `outputs/demo_cases/`).

## S1. Full-system confusion analysis (flash-tier benchmark, 560 runs)

**Table S1a. Aggregated confusion matrix, QianLieAnHui (rows = gold, columns = predicted).**

| gold \ predicted | endorse | endorse_option | conditional | report_option | against |
|---|---|---|---|---|---|
| **endorse** | 190 | 0 | 0 | 0 | 0 |
| **endorse_option** | 0 | 35 | 0 | 0 | 0 |
| **conditional** | 74 | 0 | 95 | 10 | 6 |
| **report_option** | 0 | 3 | 0 | 22 | 0 |
| **against** | 16 | 0 | 0 | 0 | 109 |

Conditional recall = 95/185 = 0.513; gold-conditional errors: →endorse 74, →report_option 10, →against 6.

**Table S1b. Per-domain confusion matrices, QianLieAnHui (n per domain in header).**

*Domain: indication (n = 115 runs)*

| gold \ predicted | endorse | endorse_option | conditional | report_option | against |
|---|---|---|---|---|---|
| **endorse** | 70 | 0 | 0 | 0 | 0 |
| **endorse_option** | 0 | 0 | 0 | 0 | 0 |
| **conditional** | 0 | 0 | 25 | 5 | 0 |
| **report_option** | 0 | 0 | 0 | 5 | 0 |
| **against** | 0 | 0 | 0 | 0 | 10 |

*Domain: procedure (n = 170 runs)*

| gold \ predicted | endorse | endorse_option | conditional | report_option | against |
|---|---|---|---|---|---|
| **endorse** | 30 | 0 | 0 | 0 | 0 |
| **endorse_option** | 0 | 35 | 0 | 0 | 0 |
| **conditional** | 15 | 0 | 37 | 5 | 3 |
| **report_option** | 0 | 3 | 0 | 17 | 0 |
| **against** | 1 | 0 | 0 | 0 | 24 |

*Domain: treatment_planning (n = 275 runs)*

| gold \ predicted | endorse | endorse_option | conditional | report_option | against |
|---|---|---|---|---|---|
| **endorse** | 90 | 0 | 0 | 0 | 0 |
| **endorse_option** | 0 | 0 | 0 | 0 | 0 |
| **conditional** | 59 | 0 | 33 | 0 | 3 |
| **report_option** | 0 | 0 | 0 | 0 | 0 |
| **against** | 15 | 0 | 0 | 0 | 75 |

**Table S1c. Paired seed-level t-tests (two-sided, n = 5 seed pairs), Benjamini–Hochberg FDR over all six comparisons.**

| comparison | metric | t(4) | p (raw) | p (BH-FDR) |
|---|---|---|---|---|
| probiopsy-rag vs lightrag | exact5 | 22.045 | 2.51e-05 | 4.00e-05 |
| probiopsy-rag vs lightrag | kappa | 21.669 | 2.68e-05 | 4.00e-05 |
| probiopsy-rag vs naive_rag | exact5 | 10.377 | 4.87e-04 | 5.84e-04 |
| probiopsy-rag vs naive_rag | kappa | 8.875 | 8.90e-04 | 8.90e-04 |
| probiopsy-rag vs pure_llm | exact5 | 25.286 | 1.45e-05 | 4.00e-05 |
| probiopsy-rag vs pure_llm | kappa | 23.72 | 1.87e-05 | 4.00e-05 |

## S2. Generator-robustness supplement (flagship GLM-5.3 tier, 1,120 runs)

| method | generator tier | exact-5 (mean ± SD) | Cohen's κ | macro-F1 |
|---|---|---|---|---|
| naive_rag | flagship GLM-5.3 | 0.537 ± 0.012 | 0.450 ± 0.016 | 0.497 ± 0.020 |
| pure_llm | flagship GLM-5.3 | 0.287 ± 0.013 | 0.132 ± 0.013 | 0.255 ± 0.024 |

Flash-tier reference values: naive_rag exact-5 0.605 ± 0.033 (κ 0.512), pure_llm exact-5 0.304 ± 0.039 (κ 0.079). The flagship tier did not rescue either baseline architecture (naive_rag 0.538, κ 0.450; pure_llm 0.288, κ 0.132).

## S3. Demonstration case reports (verbatim)

### case1 unifocal scheme

# 前列安汇 demo — 单发病灶穿刺方案 (Unifocal lesion: TBx+PLBx vs add SBx)

**Scenario**: 62-year-old man, PSA 6.2 ng/mL. 3T mpMRI with adequate image quality (PI-QUAL v2 = 3) shows a single 9 mm PI-RADS 4 lesion in the left peripheral zone.

**case_id**: `case1_unifocal_scheme` · elapsed 52.9s · graph yes

## 前列安汇 decision report

**Decision under consideration:** For a 62-year-old man with a single 9 mm PI-RADS 4 peripheral-zone lesion on adequate-quality 3T mpMRI, should the biopsy scheme be targeted biopsy plus perilesional biopsy, and should a full systematic biopsy be added?

**Patient scenario flags:** lesion_small, mpmri, mri_3t, pirads_4_5, psa_elevated, pz_lesion, quality_adequate, unifocal, visible_lesion

### Verdict: 不推荐 (Consensus against)

For a unifocal visible lesion, consensus endorses targeted+perilesional biopsy (Q43 median 7, agree) but rejects adding full systematic biopsy (Q45 median 3, disagree); contralateral systematic yield is only 0.3-4% (EV0024). Recommend TBx+PLBx alone, against the combined scheme.

*Confidence:* 0.90

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

### Citations

Q43, Q45, Q44a, EV0024

---
*Decision support only — not a substitute for clinical judgement. Verdicts trace to ProBIOPSY consensus statements (Eur Urol 2026).*

### case2 psma pet upfront

# 前列安汇 demo — PSMA PET 替代 MRI 先行 (PSMA PET instead of MRI upfront)

**Scenario**: 68-year-old biopsy-naive man, PSA 9.1 ng/mL, high clinical suspicion. The centre offers PSMA PET-CT and considers skipping MRI.

**case_id**: `case2_psma_pet_upfront` · elapsed 19.0s · graph yes

## 前列安汇 decision report

**Decision under consideration:** For a biopsy-naive man with elevated PSA and high clinical suspicion, should PSMA PET-CT be preferred over MRI as the primary imaging test before prostate biopsy?

**Patient scenario flags:** imaging_available, psa_elevated, psma_pet_available, suspicion_high

### Verdict: 不推荐 (Consensus against)

ProBIOPSY Q17 (median 2, consensus disagree) explicitly rejects preferring PSMA PET over MRI for primary prostate cancer diagnosis in biopsy-naive men. MRI remains the upfront triage test; PSMA PET-CT is only an ancillary option after negative MRI with persistent suspicion (Q19, median 8).

*Confidence:* 0.99

### Triggered consensus rules

- **upfront_new_imaging_rejection** (high) — If psma_pet_available or microultrasound_available, do NOT route the patient to these modalities as the primary biopsy gate. Use PI-QUAL-checked MRI first; reserve PSMA PET / microultrasound for the ancillary indications encoded in R02/R03. *[citations: 10.1016/j.eururo.2026.06.012 (ProBIOPSY consensus, Eur Urol 2026; statements Q17, Q20)]*
  - HARD: the consensus explicitly REJECTS 'd_reject_psma_pet_upfront' (Do NOT prefer PSMA PET over MRI for primary PCa diagnosis) — do not endorse it.

### Evidence grounding

- [EV0045|B_consensus|Table 1 (Q19)] (score 14.31)
- [EV0043|B_consensus|Table 1 (Q17)] (score 11.52)
- [EV0044|B_consensus|Table 1 (Q18)] (score 11.25)
- [EV0009|D_review|Main text / results_d1_novel] (score 10.90)
- [EV0022|D_review|SM2 / sm2_d1_biomarkers] (score 8.44)

### Citations

Q17, Q19, EV0043, EV0045, EV0009

---
*Decision support only — not a substitute for clinical judgement. Verdicts trace to ProBIOPSY consensus statements (Eur Urol 2026).*

### case3 bpmri indeterminate

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

### case4 advanced route prophylaxis

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

### case5 infection risk escalation

# 前列安汇 demo — 感染风险患者因素升级 (Patient-factor escalation: infection risk)

**Scenario**: 66-year-old man with prior prostatitis and recent hospitalisation (infection risk factors, Q62 catalogue), undergoing repeat biopsy after a prior negative biopsy with persisting suspicion.

**case_id**: `case5_infection_risk_escalation` · elapsed 47.4s · graph yes

## 前列安汇 decision report

**Decision under consideration:** For a man with infection risk factors undergoing repeat prostate biopsy, should the transperineal route be preferred, and should antibiotic prophylaxis be augmented if transrectal access is used?

**Patient scenario flags:** infection_risk_factor, prior_negative_biopsy, psa_elevated

### Verdict: 推荐选项 (SOQ-endorsed option)

Q58 SOQ consensus (97%) endorses the transperineal route as standard; hard constraints mandate endorsement. With infection risk factors, Q62 still permits prophylaxis for transperineal. If transrectal access is unavoidable, Q63 reached no consensus; augmented prophylaxis was the 67% majority choice — report alongside.

*Confidence:* 0.85

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

### Citations

Q58, Q62, Q63, EV0013, EV0083, EV0084

---
*Decision support only — not a substitute for clinical judgement. Verdicts trace to ProBIOPSY consensus statements (Eur Urol 2026).*

## S4. Runtime per demonstration case

**Table S4. End-to-end pipeline steps per demonstration case (source: `outputs/figures/source_data/figure5_reasoning_trace.csv`; plotted in Figure 5A). The rule-engine layer is deterministic (0 ms); latency is dominated by the arbitration pass (retrieval + GLM arbitration).**

| case | step | layer | duration (ms) | input | output |
|---|---|---|---|---|---|
| case1_unifocal_scheme | 1 | rule_engine | 0.0 | 9 flags × 2 items | 1 rule(s) fired |
| case1_unifocal_scheme | 2 | llm_arbiter | 52900.0 | 1 rule(s) + graph & lexical evidence | action=against, confidence=0.9 |
| case2_psma_pet_upfront | 1 | rule_engine | 0.0 | 4 flags × 1 items | 1 rule(s) fired |
| case2_psma_pet_upfront | 2 | llm_arbiter | 18960.0 | 1 rule(s) + graph & lexical evidence | action=against, confidence=0.99 |
| case3_bpmri_indeterminate | 1 | rule_engine | 0.0 | 6 flags × 3 items | 1 rule(s) fired |
| case3_bpmri_indeterminate | 2 | llm_arbiter | 64160.0 | 1 rule(s) + graph & lexical evidence | action=endorse, confidence=0.85 |
| case4_advanced_route_prophylaxis | 1 | rule_engine | 0.0 | 4 flags × 3 items | 3 rule(s) fired |
| case4_advanced_route_prophylaxis | 2 | llm_arbiter | 31690.0 | 3 rule(s) + graph & lexical evidence | action=endorse, confidence=0.9 |
| case5_infection_risk_escalation | 1 | rule_engine | 0.0 | 3 flags × 2 items | 3 rule(s) fired |
| case5_infection_risk_escalation | 2 | llm_arbiter | 47400.0 | 3 rule(s) + graph & lexical evidence | action=endorse_option, confidence=0.85 |

Arbitration pass latency across the five cases: median 47400 ms, range 18960–64160 ms (interactive single-case use; benchmark throughput used eight concurrent workers).

## S5. Arbitration prompt and action definitions

The arbitration prompt template (action definitions, rule-constraint enforcement instructions, citation requirements) and the five-class action taxonomy are included in the repository (`configs/prompts.yaml`, rule base `configs/rules.yaml`, SHA-256 `f500802ee82a4be9fc7a7b6b951e2e7083c09e9ef6a521e7dd280726dbe0ee62` recorded at index build).
## S6. Expert blinded review (four experts × five composite propositions)

**Design.** Each case was presented as a composite proposition assembled from
declarative decision items. Blinded first pass: experts chose their own
five-class action; the system verdict was then revealed and four Likert
dimensions (1–5) were rated. Pre-registered rules: majority = modal rating;
2:2 ties = no-majority, excluded from system-vs-majority Cohen κ; all
agreement statistics interpreted as preliminary. Full questionnaire:
`outputs/expert_review/expert_booklet.md`; protocol:
`outputs/expert_review/expert_review_protocol.md`.

**Results.** Per-case modal share — case1_unifocal_scheme 2/4; case2_psma_pet_upfront 3/4; case3_bpmri_indeterminate 4/4; case4_advanced_route_prophylaxis 4/4; case5_infection_risk_escalation 4/4; Fleiss κ (overall) = -0.092; Cohen κ (system vs expert majority, n = 4) = 1.0; Likert means — clarity 5.0; usefulness 5.0; recommendation 5.0; evidence 5.0.

**Verbatim expert comments (Chinese original).**

- Expert 1, case1_unifocal_scheme (rated conditional): 如果后续患者不做前列腺根治性切除术，而选择内放疗或者不可逆电穿孔手术，则需要明确是否确实是单发病灶。如果是多发病灶，则系统穿刺可以协助明确肿瘤具体位置
- Expert 1, case2_psma_pet_upfront (rated report_option): 如果这名患者TPSA非常高，比如＞100ng/ml，很可能已经发生淋巴结转移或者骨转移，则应该考虑将PSMA PET-CT代替增强MR作为前列腺穿刺前的影像学检查。因为这类患者在穿刺病例证实为前列腺癌以后，绝对有必要探明有无前列腺癌局部或远处转移
- Expert 2, case1_unifocal_scheme (rated conditional): 是否增加系统穿刺，需要考虑患者手术方案的选择

