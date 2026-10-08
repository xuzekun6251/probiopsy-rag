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

## S7. Patient-education mode: verbatim consultations

**Design.** The education mode reuses the frozen 357-chunk benchmark corpus
and knowledge-graph retrieval (context-only), keyword-matches the patient's
question against a curated, source-traceable patient-education fact base
(`data/seed/patient_education_facts.csv`, ten entries covering biopsy sampling
logic, biopsy indication, benign reports, HGPIN, ASAP, pain and anaesthesia,
preparation, post-biopsy warning signs, result interpretation, and shared
decision-making), and generates one lay-language Chinese answer with a
safety-netting paragraph and an explicit referral to the treating clinician.
The mode is not part of the 2,240-run benchmark. Transcripts below are
verbatim; matched fact ids are shown per consultation.

## Patient consultation 1 (verbatim)

**Patient question (Chinese):** 医生，我穿刺结果是良性的，是不是以后就不用管了，也不用再查PSA了？

**Matched fact entries:** edu_negative_result, edu_biopsy_sampling — sources: probiopsy (ProBIOPSY consensus, Chernysheva et al., Eur Urol 2026); eau_guideline (EAU Prostate Cancer Guidelines, uroweb.org, living guideline); borghesi_comp (Borghesi et al., complications after prostate biopsy, Eur Urol 2017); probiopsy (ProBIOPSY consensus, Chernysheva et al., Eur Urol 2026); eau_guideline (EAU Prostate Cancer Guidelines, uroweb.org, living guideline)

**Retrieval:** 6 evidence chunks (frozen benchmark corpus) + knowledge-graph context (context-only mode)

**Agent answer (Chinese, verbatim):**

您好，先说结论：穿刺报告是良性的确是个好消息，但“良性”不等于“以后就不用管了”。

1. 良性结果的意思是：这次取出来的那些组织样本里，没有发现癌细胞。它不代表前列腺一辈子都不会长癌 [edu_negative_result]。
2. 穿刺是一种“抽样”检查：医生用很细的针，从前列腺里取出少量组织条，由病理科医生放在显微镜下看。它只能检查取到的那一部分，看不了整个前列腺，所以结果正常也不能百分之百排除癌症 [edu_biopsy_sampling]。
3. 又小、又藏得深的肿瘤有可能没被针取到；还有些异常是以后才出现、或慢慢发展起来的 [edu_negative_result]。
4. 所以PSA抽血检查（PSA就是“前列腺特异抗原”，一种通过验血反映前列腺情况的指标）和体格检查，还需要按泌尿科医生给您安排的时间继续做。医生有时还会参考“PSA密度”（PSA数值除以前列腺体积）这类指标，来判断要不要做进一步检查 [edu_negative_result][证据5]。如果医生仍然有怀疑，可能会建议做磁共振（MRI，一种给前列腺做详细成像、不用开刀的检查），或者再做一次穿刺 [edu_negative_result]。

什么情况要及时就医：即使您自我感觉很好，也要按时复诊、按时抽血查PSA [edu_negative_result]。如果PSA又升高了，或者身体出现新的症状、新的不舒服，不要等到下一次预约的时间，请尽早联系您的主诊泌尿科医生 [edu_negative_result]。另外，如果您对报告内容或穿刺过程有任何不清楚的地方，也可以请医生把报告“一条一条、一针一针”地给您讲解 [edu_biopsy_sampling]。

最后提醒一句：每个人的情况都不同，建议您带着穿刺报告，和您的主诊泌尿科医生一起商量出属于您自己的复查计划。

**Timings:** graph 42.0s · lexical 0.00s · generation 48.4s

## Patient consultation 2 (verbatim)

**Patient question (Chinese):** 我报告上写着非典型小腺泡增生（ASAP），这是什么意思？严重吗？

**Matched fact entries:** edu_asap — sources: asap_rate_2024 (clinically significant cancer on repeat biopsy after ASAP, Oncology 2024, doi:10.1159/000535123); eau_guideline (EAU Prostate Cancer Guidelines, uroweb.org, living guideline)

**Retrieval:** 0 evidence chunks (frozen benchmark corpus) + knowledge-graph context (context-only mode)

**Agent answer (Chinese, verbatim):**

您好，别太紧张，我来用简单的话给您解释一下。

**1. ASAP是什么意思？**
ASAP的中文全称是“非典型小腺泡增生”。简单说：病理科医生（就是专门在显微镜下看组织的医生）在您的组织样本里，看到一小团长得不太正常的腺体（腺体是前列腺里负责分泌液体的小组织），它们“像”癌细胞，但因为取到的组织太少，还不能确定就是癌 [edu_asap]。

**2. 严重吗？**
它**不是癌症的诊断**，只是“怀疑但还没证实”。不过它确实需要重视：它和另一种叫“孤立性HGPIN”（高级别前列腺上皮内瘤变，一种异常但不是癌的改变）的情况不同，ASAP更要认真对待 [edu_asap]。

**3. 为什么要重视？**
因为有ASAP的人在再次活检（就是再做一次前列腺穿刺取组织）时，有相当一部分人会被查出“有临床意义的癌”——意思是需要治疗或密切关注的癌症 [edu_asap]。

**4. 接下来一般会怎么做？**
泌尿外科医生通常会建议尽早做一次重复活检，而且常常会配合MRI（磁共振检查，一种用磁场给前列腺拍详细图像的检查）来对准同一个部位，提高准确性 [edu_asap]。

**什么情况要及时就医：**
如果医生已经建议您做重复活检，请不要拖延，尽快安排；另外，如果您还没做过MRI，或者上次MRI是在这次活检之前做的，可以主动问一下医生：是否应该在重复活检之前，先做一次新的、更详细的mpMRI（多参数磁共振，一种能看得更清楚的前列腺磁共振检查）[edu_asap]。

每个人的情况都不一样，建议您带着这份报告，和您的主诊泌尿外科医生详细商量属于您自己的下一步安排。

**Timings:** graph 10.3s · lexical 0.00s · generation 27.2s

## Patient consultation 3 (verbatim)

**Patient question (Chinese):** 我很怕疼，所以一直不敢做前列腺穿刺，能不做吗？

**Matched fact entries:** edu_biopsy_sampling, edu_pain_fear — sources: probiopsy (ProBIOPSY consensus, Chernysheva et al., Eur Urol 2026); eau_guideline (EAU Prostate Cancer Guidelines, uroweb.org, living guideline); probiopsy (ProBIOPSY consensus, Chernysheva et al., Eur Urol 2026); bryant_translate (TRANSLATE RCT, Bryant et al., Lancet Oncol); yang_tps_meta (transperineal vs transrectal RCT meta-analysis, Eur Urol Open Sci)

**Retrieval:** 0 evidence chunks (frozen benchmark corpus) + knowledge-graph context (context-only mode)

**Agent answer (Chinese, verbatim):**

您好，特别理解您的担心，怕疼是人之常情。下面先直接回答您的问题：

1. **怕疼很常见，也值得说出来。** 很多男士都有同样的顾虑，这不是难为情的事 [edu_pain_fear]。

2. **穿刺通常会打麻药。** 医生一般会先做局部麻醉（就是让身体一小块区域暂时不疼的打药方式），常用的方法叫“前列腺周围神经阻滞”——把麻药打在前列腺周围神经旁边，让穿刺时不那么疼。不管是从直肠（肛门里面）进针，还是从会阴（阴囊和肛门之间的皮肤）进针，这都是标准做法；经会阴的穿刺甚至可以完全在局部麻醉下完成 [edu_pain_fear]。

3. **大多数男性都能顺利完成。** 不舒服的感觉通常是一种短暂的压迫感，而不是尖锐的疼 [edu_pain_fear]。

4. **关于“能不能不做”：** 穿刺是用细针取出几条很小的前列腺组织，由病理医生在显微镜下检查有没有癌细胞；只要取到的组织里有癌，就能确诊 [edu_biopsy_sampling]。但要注意：如果医生已经判断您需要做，却因为害怕一直拖着，可能会耽误一个本来有机会治愈的癌症的诊断 [edu_pain_fear]。所以“做不做”这件事，请一定和医生一起商量，而不是自己默默决定不做。

什么情况要及时就医：请在穿刺之前就把怕疼告诉治疗团队，这样麻醉方案可以提前安排好；如果恐惧让您觉得难以承受，请一定说出来——这是医疗上需要认真对待的事，不是丢人的事，必要时还可以安排镇静（用药物帮助您放松）或者加用局部麻醉 [edu_pain_fear]。另外，如果您对穿刺的流程或报告有任何不清楚的地方，请直接请主管的泌尿科医生逐条给您讲解 [edu_biopsy_sampling]。

每个人的情况都不一样，建议您带着自己的检查结果和顾虑，和主治的泌尿科医生当面商量最适合您的方案。

**Timings:** graph 15.4s · lexical 0.00s · generation 27.4s

