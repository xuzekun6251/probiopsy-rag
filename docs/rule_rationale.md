# Rule Rationale — 前列安汇 (probiopsy-rag) rule engine

**Version:** 1.0 (Executor Phase 3)
**Gold standard:** ProBIOPSY international consensus (Chernysheva et al., *Eur Urol* 2026;90(3):212–224, doi:10.1016/j.eururo.2026.06.012) — 34 experts, modified Delphi (3 rounds), 112 final statements in 36 stems, 29/36 stems with consensus agreement.
**Design:** each rule = one pathway checkpoint; fires when `entity_a_flags ∩ patient.flags` **and** `entity_b_flags ∩ available decision items` (A×B interaction skeleton, 49 patient-scenario flags × 54 decision items). Every rule cites the consensus DOI (the validation gold standard itself) plus — where the consensus reference list contains a directly supporting trial/meta-analysis — that DOI as second literature source. All citations are DOI-based (`source_type: literature`) so they pass the kuku Rule 3 (≥2 independent sources) + Rule 4 (retraction) hard gate; EAU/AUA guideline URLs are deliberately kept out of `citations` because the gate's guideline whitelist does not cover them.

**Action semantics** (inherited from the B registry `flags` column): `endorsement_{consensus|majority|against|neither}` + `action_{recommend|against|conditional|report_only}`. A matched rule therefore carries not one verdict but the consensus verdict per decision item it touches, which is exactly the statement-fidelity target evaluated in Phase 5 (`expected_system_action` per statement: Consensus agree→endorse; Consensus disagree→against; neither→conditional; SOQ Consensus→endorse_option; SOQ No consensus→report_option).

---

## R01 `mri_acquisition_quality_pathway` — severity high — imaging_pathway

| | |
|---|---|
| Entity A flags | `bpmri`, `mpmri`, `mri_15t`, `mri_3t`, `quality_inadequate` |
| Entity B items | `d_mri_driven_pathway`, `d_accept_any_field_strength`, `d_mri_quality_check`, `d_use_piqual_v2`, `d_bpmri_acceptable` |
| Statements | Q1 (field strength equivalence, median 8, agree) · Q4a (quality standards, median 9, agree) · Q4b (PI-QUAL v2, median 8, agree) · Q5–Q7 (bpMRI acceptable, median 8, agree) |

**Rationale.** The pathway gate is MRI *quality*, not field strength or protocol richness. PI-QUAL v2 is the checking instrument; quality-assured bpMRI (T2W+DWI) is acceptable for detection, so contrast is not routinely required. An MRI failing quality standards must not generate a "negative MRI" conclusion — repeat/complete imaging first.

**Citations:** consensus DOI; *(no extra trial DOI — quality-criteria literature is cited inside the consensus statements).*

## R02 `indeterminate_lesion_ancillary_workup` — severity medium — ancillary_workup

| | |
|---|---|
| Entity A flags | `indeterminate_lesion`, `pirads_3`, `psad_intermediate`, `psad_intermediate_high`, `psad_high`, `risk_calculator_available`, `biomarker_available`, `contrast_mri_available` |
| Entity B items | `d_contrast_mri_for_pz_indeterminate`, `d_followup_indeterminate_bpmri`, `d_psad_gate_bpmri_indeterminate`, `d_psad_gate_mpmri_indeterminate`, `d_riskcalc_gate_bpmri_indeterminate`, `d_riskcalc_gate_mpmri_indeterminate`, `d_biomarker_gate_bpmri_indeterminate`, `d_biomarker_gate_mpmri_indeterminate`, `d_psma_pet_indeterminate_ancillary`, `d_reject_microultrasound_indeterminate` |
| Statements | Q10a (contrast for PZ indeterminate on bpMRI, median 7, agree) · Q10b (follow-up imaging, median 8, agree) · Q11 (PSAD gate bpMRI, median 7, agree) · Q12 (risk calculator bpMRI, median 6, neither) · Q13/Q16 (biomarkers, median 4, neither) · Q14 (PSAD gate mpMRI, median 8, agree) · Q15 (risk calculator mpMRI, median 7, agree) · Q18 (PSMA PET, median 6, neither) · Q21 (microultrasound, median 3, neither) |

**Rationale.** PSAD is the workhorse gate for PI-RADS 3 (stronger endorsement on mpMRI), contrast MRI is a bpMRI-specific option for peripheral-zone indeterminate findings, and follow-up imaging is an acceptable alternative. Risk calculators are conditional (endorsed only for mpMRI), biomarkers are conditional everywhere — the engine must surface these as `action_conditional`/`report_option`, not as endorsements. This rule is the statement-fidelity stress test: it mixes agree/neither/no-consensus actions in one checkpoint.

**Citations:** consensus DOI; Schoots & Padhani, BJU Int 2021 (doi:10.1111/bju.15277 — risk-adapted biopsy decision based on prostate MRI and PSA density), extracted from consensus ref list.

## R03 `negative_mri_high_suspicion_pathway` — severity high — imaging_pathway

| | |
|---|---|
| Entity A flags | `negative_mri`, `suspicion_high`, `psa_elevated`, `dre_positive`, `family_history`, `black_ethnicity`, `prior_negative_biopsy` |
| Entity B items | `d_sbx_negative_mri_high_suspicion`, `d_psma_pet_negative_mri_ancillary`, `d_reject_microultrasound_negative_mri`, `d_sbx_12core_template` |
| Statements | Q19 (PSMA PET ancillary after negative MRI, median 8, agree) · Q25 (systematic biopsy despite negative MRI + high suspicion, median 7, agree) · Q55a (12-core template in this setting, median 7, agree) · Q22 (microultrasound, median 3, neither) |

**Rationale.** A negative MRI never discharges a patient with high clinical suspicion; the consensus explicitly keeps the 12-core systematic biopsy on the table and positions PSMA PET as the ancillary test of choice.

**Citations:** consensus DOI.

## R04 `upfront_new_imaging_rejection` — severity high — imaging_pathway

| | |
|---|---|
| Entity A flags | `psma_pet_available`, `microultrasound_available`, `imaging_available` |
| Entity B items | `d_reject_psma_pet_upfront`, `d_reject_microultrasound_upfront` |
| Statements | Q17 (PSMA PET upfront, median 2, **disagree**) · Q20 (microultrasound upfront, median 2, **disagree**) |

**Rationale.** The strongest negative statements in the consensus (medians of 2). Resource availability (`*_available` flags) must not translate into upfront routing — these modalities have only the ancillary niches encoded in R02/R03. This rule makes the "against" arm of the action taxonomy reachable by the rule engine, which is required for high-risk specificity in the Phase 5 benchmark.

**Citations:** consensus DOI.

## R05 `ai_mri_lesion_detection_aid` — severity low — ai_decision_support

| | |
|---|---|
| Entity A flags | `ai_software_available`, `bpmri`, `mpmri`, `visible_lesion` |
| Entity B items | `d_ai_mri_lesion_aid` |
| Statements | Q26 (AI as lesion-detection aid, median 7, agree) |

**Rationale.** AI is endorsed as a *second reader* — detection/characterization aid with the radiologist remaining accountable. PI-CAI (Saha et al., Lancet Oncol 2024) provides the direct evidence base (AI-assisted reading non-inferior for csPCa detection).

**Citations:** consensus DOI; PI-CAI, Lancet Oncol 2024 (doi:10.1016/S1470-2045(24)00220-1).

## R06 `advanced_disease_reduced_systematic_scheme` — severity high — scheme_selection

| | |
|---|---|
| Entity A flags | `advanced_disease`, `unfit_curative`, `locally_advanced_suspected`, `psa_gt_50` |
| Entity B items | `d_sbx_reduced_6core_advanced`, `d_reject_saturation_bx` |
| Statements | Q57 (reduced 6-core scheme in advanced disease, median 8, agree) · Q54 (saturation, median 2, disagree) · Q56 (saturation, median 2, disagree) |

**Rationale.** When curative intent is off the table the biopsy goal shifts from mapping precision to confirmation; a reduced 6-core systematic scheme (plus targeted cores if a lesion is visible) suffices. Saturation templates are rejected.

**Citations:** consensus DOI.

## R07 `systematic_template_selection` — severity medium — scheme_selection

| | |
|---|---|
| Entity A flags | `psa_elevated`, `dre_positive`, `prior_negative_biopsy`, `visible_lesion` |
| Entity B items | `d_sbx_12core_template`, `d_reject_sextant_template`, `d_reject_ginsburg_template`, `d_reject_saturation_bx` |
| Statements | Q51 (sextant, median 3, disagree) · Q52 (12-core, median 8, agree) · Q53 (Ginsburg, median 3, disagree) · Q54 (saturation, median 2, disagree) |

**Rationale.** The 12-core template is the only endorsed systematic template; sextant, Ginsburg and saturation are all consensus-disagreed. R06 is the sole override (reduced scheme in advanced disease).

**Citations:** consensus DOI.

## R08 `targeted_core_count_adaptation` — severity low — targeted_bx

| | |
|---|---|
| Entity A flags | `visible_lesion`, `pirads_4_5`, `pirads_3`, `pz_lesion`, `lesion_small` |
| Entity B items | `d_tbx_cores_adapt_pirads`, `d_tbx_min3_cores` |
| Statements | Q34 (adapt cores to PI-RADS, median 6, neither) · Q35/Q36 (≥3 cores per target, no consensus both rounds) |

**Rationale.** A deliberately *non-committal* rule: the consensus is silent on fixed targeted-core counts, so the engine must emit `report_option` (not endorse). This tests that the hybrid system reports uncertainty instead of hallucinating a standard — a core claim of the paper.

**Citations:** consensus DOI.

## R09 `perilesional_plbx_technique` — severity low — targeted_bx

| | |
|---|---|
| Entity A flags | `visible_lesion`, `unifocal`, `multifocal_ipsilateral`, `lesion_large`, `lesion_small` |
| Entity B items | `d_adopt_term_perilesional`, `d_plbx_within_10mm`, `d_plbx_count_by_lesion_size`, `d_plbx_2cores_small_lesion`, `d_plbx_max2cores_large_lesion` |
| Statements | Q37a (term "perilesional", SOQ consensus) · Q38 (within 10 mm, SOQ consensus) · Q39 (scale count to lesion size, median 7, agree) · Q40 (exactly 2 cores small lesion, no consensus) · Q41 (max 2 cores large lesion, SOQ consensus) |

**Rationale.** Technique-level checkpoint: cores within 10 mm of the lesion margin, perilesional count scaled to lesion size, standardized terminology in the report. Brisbane et al. (Eur Urol 2022) supply the primary evidence (umbra/penumbra under-sampling).

**Citations:** consensus DOI; Brisbane et al., Eur Urol 2022 (doi:10.1016/j.eururo.2022.01.008).

## R10 `biopsy_scheme_by_lesion_distribution` — severity medium — scheme_selection

| | |
|---|---|
| Entity A flags | `unifocal`, `multifocal_ipsilateral`, `multifocal_bilateral`, `multiple_lesions`, `visible_lesion` |
| Entity B items | `d_scheme_unifocal_tbx_plbx`, `d_scheme_unifocal_add_contralateral`, `d_scheme_unifocal_add_sbx`, `d_scheme_ipsilateral_multifocal`, `d_scheme_bilateral_tbx_plbx` |
| Statements | Q42 (unifocal TBx+PLBX, median 4, neither) · Q43 (unifocal TBx+PLBX without contralateral SBx, median 7, agree) · Q44a/Q44 (add contralateral, neither) · Q45 (add full SBx, median 3, disagree) · Q46a–Q48 (ipsilateral multifocal variants, neither) · Q49 (bilateral TBx+PLBX for multifocal bilateral, median 7, agree) · Q50 (neither) |

**Rationale.** Scheme is chosen by lesion distribution: unifocal → targeted+perilesional alone; multifocal bilateral → bilateral targeted+perilesional. Adding full systematic cores to a targeted+perilesional scheme is consensus-disagreed. The ipsilateral-multifocal cells are majority-neither and stay conditional.

**Citations:** consensus DOI.

## R11 `route_anaesthesia_prophylaxis` — severity high — perioperative

| | |
|---|---|
| Entity A flags | `infection_risk_factor` (6 Q62-catalogue entities), `prior_negative_biopsy`, `unfit_curative`, `advanced_disease` |
| Entity B items | `d_route_transperineal`, `d_pnb_tr`, `d_pnb_tp`, `d_omit_abx_tp_no_risk`, `d_augmented_abx_tr` |
| Statements | Q58 (transperineal route, SOQ consensus) · Q59 (PNB transrectal, SOQ consensus) · Q60 (PNB transperineal, SOQ consensus) · Q62 (omit abx for TP without risk factors, SOQ consensus) · Q63 (augmented abx for TR with risk factors, no consensus — majority position) |

**Rationale.** Patient-safety checkpoint. Transperineal is the default route; periprostatic nerve block for both routes; antibiotic omission is tied to *both* transperineal route *and* absence of the six Q62 infection risk factors; augmented prophylaxis for transrectal access in risk-factor patients is a majority (not consensus) position and must be reported as such. Marra et al. (Eur Urol Oncol 2026, RCT meta-analysis) corroborate the infection-safety gradient transperineal < transrectal.

**Citations:** consensus DOI; Marra et al., Eur Urol Oncol 2026 (doi:10.1016/j.euo.2026.01.009).

## R12 `treatment_planning_tissue_requirements` — severity high — treatment_planning

| | |
|---|---|
| Entity A flags | `intent_focal_therapy`, `intent_nerve_sparing`, `intent_plnd`, `intent_whole_gland_rt`, `intent_focal_boost`, `intent_adt_duration` |
| Entity B items | `d_tp_focal_add_contralateral`, `d_tp_focal_tbx_only_not_enough`, `d_tp_nss_unifocal_tbx_plbx`, `d_tp_nss_bilateral_tbx_adequate`, `d_tp_plnd_unifocal_no_consensus`, `d_tp_plnd_bilateral_tbx_plbx`, `d_tp_wg_rt_tbx_plbx`, `d_tp_focal_boost_tbx_plbx`, `d_tp_adt_duration_tbx_plbx`, `d_tp_reject_adding_systematic_universal` |
| Statements | Q64–Q66 (focal therapy: TBx+PLBX alone insufficient, neither; Q65 contralateral SBx required, median 7, agree) · Q67–Q69 (NSS unifocal: TBx+PLBX, Q67 median 7 agree) · Q70a–Q72 (NSS bilateral: adequate bilateral tissue, Q70a/Q70 median 7 agree; Q71 disagree) · Q73a–Q75 (PLND unifocal: no consensus) · Q76a–Q78 (PLND bilateral: TBx+PLBX, Q76a/Q76 median 7 agree) · Q79a–Q81 (whole-gland RT: Q79a/Q79 median 7–8 agree; Q81 reject universal SBx, disagree) · Q82a–Q84 (RT recurrence: same pattern) · Q85a–Q87 (focal boost primary: Q85a/Q85 agree) · Q88a–Q90 (focal boost salvage: Q88a/Q88 agree) · Q91a–Q93 (ADT primary: Q91a/Q91 agree) · Q94a–Q96 (ADT salvage: Q94a/Q94 agree; universal SBx add-on rejected throughout) |

**Rationale.** The consensus's distinctive contribution: biopsy scheme adequacy is *treatment-intent dependent*. Focal therapy is the one intent that *requires* adding contralateral systematic tissue (Q65); whole-gland RT, focal boost and ADT planning are served by targeted+perilesional; universally appending systematic biopsy for planning is consensus-disagreed. Van den Kroonenberg et al. (Eur Urol Open Sci 2024 — the target journal) provide direct evidence on omitting contralateral systematic biopsy in surgical planning.

**Citations:** consensus DOI; van den Kroonenberg et al., Eur Urol Open Sci 2024 (doi:10.1016/j.euros.2024.03.006).

---

## Patient factor escalation rules

| Factor | Escalates | Mechanism |
|---|---|---|
| `immunocompromised_or_infection_history` | R11 | Any of the 6 Q62 infection-risk-factor entities → prefer transperineal + augmented prophylaxis if transrectal unavoidable |
| `unfit_for_curative_treatment` | R06 | Goal shifts to confirmation → reduced 6-core scheme |
| `repeat_biopsy_setting` | R03, R11 | Prior negative biopsy + persisting suspicion → keep 12-core template; route sepsis-safety |
| `suspicious_dre_without_mri_lesion` | R03 | DRE-positive with negative MRI → systematic 12-core |

## Decision-item coverage

53/54 Entity-B decision items are wired into the 12 rules (98%); the remainder (`d_report_max3_lesions` — a no-consensus reporting item, Q8) is deliberately left to the LightRAG + LLM-arbiter layer, which is the system's designed handling for items the consensus itself left open. The rule layer thus covers **all pathway checkpoints with consensus agreement** and delegates open questions — the paper's central argument for the hybrid architecture.

## Citation-gate notes (verify_rule_citations.py v2.6)

- All citations are `source_type: literature` with DOI-first refs → sniffed type matches declaration (no `source_type_mismatch`).
- Primary source = the gold-standard consensus paper itself; supporting DOIs were **extracted from the consensus reference list** (mmc1 refs [55]–[90]) so every citation is traceable to the local corpus used for the evidence base (Phase 2).
- The gate's keyword-relevance vocabulary is COPD-specific (TongYuan heritage); for this domain the relevance verdict is therefore carried by the gate's LLM relevance layer (project `LLMClient`, GLM-5.3), which judges title/abstract against the rule rationale. This is a designed fallback of the gate, not a bypass — authenticity (≥2-source cross-verification + retraction check) remains keyword-independent.
- Guideline-path citations (EAU/AUA URLs) are intentionally avoided: `GUIDELINE_TOKENS` in the gate does not whitelist those acronyms; guideline context lives in the rationale text and evidence base instead.
