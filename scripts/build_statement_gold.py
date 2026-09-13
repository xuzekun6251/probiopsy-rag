# -*- coding: utf-8 -*-
"""Build the ProBIOPSY statement-level gold standard (112 statements).

Source: Chernysheva F, Di Bello F, Avesani G, et al. ProBIOPSY: A Multidisciplinary
International Consensus on Standards for Prostate Biopsy. Eur Urol 2026.
doi:10.1016/j.eururo.2026.06.012 — Tables 1-3 (verbatim statement texts, medians,
30th/70th percentiles, modified RAND/UCLA interpretation).

Output: data/seed/probiopsy_statements.csv with columns
  statement_id, domain, stem_no, stem_name, statement_text_en, statement_type,
  median, p30, p70, interpretation, soq_option, soq_pct, decision_item_id,
  scenario_flags, expected_system_action, source_locator

`expected_system_action` is the gold label for the statement-fidelity benchmark:
  endorse         statement endorsed by consensus -> system should recommend it
  endorse_option  SOQ with consensus -> system should report the winning option
  report_option   SOQ plurality without consensus -> system should report it as
                  "most popular choice, no formal consensus"
  against         panel disagrees -> system should recommend against
  conditional     panel neither agrees nor disagrees -> system should express
                  conditional/uncertain stance (no firm recommendation)

Text normalization: PDF ligatures fixed (fi/fl), curly quotes straightened.
"""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "seed" / "probiopsy_statements.csv"

HEADER = [
    "statement_id", "domain", "stem_no", "stem_name", "statement_text_en",
    "statement_type", "median", "p30", "p70", "interpretation",
    "soq_option", "soq_pct", "decision_item_id", "scenario_flags",
    "expected_system_action", "source_locator",
]

STEM_NAMES = {
    1: "Magnetic field strength requirements for MRI",
    2: "PI-QUAL quality standards",
    3: "mpMRI vs bpMRI",
    4: "Number of lesions at MRI",
    5: "Indeterminate lesion on MRI - role of additional tools",
    6: "New imaging modalities - PSMA PET",
    7: "New imaging modalities - Micro-ultrasound",
    8: "Artificial Intelligence in MRI readings",
    9: "Targeted Bx - number of targeted cores (PIRADS adaptation)",
    10: "Targeted Bx - number of targeted cores (visible lesion)",
    11: "Targeted Bx - number of targeted cores (PIRADS 4-5)",
    12: "Bx around the ROI - defining term",
    13: "Bx around the ROI - distance range",
    14: "Bx around the ROI - size dependence",
    15: "Bx around the ROI - small lesions (<10 mm)",
    16: "Bx around the ROI - large lesions (>10 mm)",
    17: "Bx scheme - unifocal MRI visible lesion",
    18: "Bx scheme - multifocal MRI visible lesions (ipsilateral & bilateral)",
    19: "Systematic Bx - which scheme",
    20: "Negative MRI but high suspicion of csPCa - which scheme",
    21: "Approach (standard route)",
    22: "Anaesthesia for transrectal biopsy",
    23: "Anaesthesia for transperineal biopsy",
    24: "Antibiotic prophylaxis - transperineal",
    25: "Antibiotic prophylaxis - transrectal",
    26: "Planning focal therapy - unifocal lesion",
    27: "Planning nerve sparing - unifocal lesion",
    28: "Planning nerve sparing - bilateral lesions",
    29: "Planning lymph node dissection - unifocal lesion",
    30: "Planning lymph node dissection - bilateral lesions",
    31: "Planning whole gland radiotherapy - unifocal lesion",
    32: "Planning whole gland radiotherapy - bilateral lesions",
    33: "Planning focal radiotherapy boost - unifocal lesion",
    34: "Planning focal radiotherapy boost - bilateral lesions",
    35: "Planning ADT length - unifocal lesion",
    36: "Planning ADT length - bilateral lesions",
}

# Statement-id -> stem mapping. Table 1 stems 1-8; Table 2 stems 9-25
# (per printed tables: 18 covers Q46a-Q50 multifocal both sides; 19 SBx scheme;
#  20 negative-MRI scheme; 21 route; 22/23 anaesthesia; 24/25 prophylaxis);
# Table 3 stems 26-36 (11 treatment-planning stems).
STEM_MAP: dict[str, int] = {
    "Q1": 1, "Q4a": 2, "Q4b": 2, "Q5": 3, "Q6": 3, "Q7": 3, "Q8": 4,
    "Q10a": 5, "Q10b": 5, "Q11": 5, "Q12": 5, "Q13": 5, "Q14": 5,
    "Q15": 5, "Q16": 5, "Q17": 6, "Q18": 6, "Q19": 6, "Q20": 7,
    "Q21": 7, "Q22": 7, "Q25": 7, "Q26": 8,
    "Q34": 9, "Q35": 10, "Q36": 11, "Q37a": 12, "Q38": 13, "Q39": 14,
    "Q40": 15, "Q41": 16, "Q42": 17, "Q43": 17, "Q44a": 17, "Q44": 17,
    "Q45": 17, "Q46a": 18, "Q46b": 18, "Q47a": 18, "Q47": 18, "Q48": 18,
    "Q49a": 18, "Q49": 18, "Q50": 18, "Q51": 19, "Q52": 19, "Q53": 19,
    "Q54": 19, "Q55a": 20, "Q55b": 20, "Q56": 20, "Q57": 20, "Q58": 21,
    "Q59": 22, "Q60": 23, "Q62": 24, "Q63": 25,
    "Q64": 26, "Q64a": 26, "Q65a": 26, "Q65": 26, "Q66": 26,
    "Q67a": 27, "Q67": 27, "Q68a": 27, "Q68": 27, "Q69": 27,
    "Q70a": 28, "Q70": 28, "Q71a": 28, "Q71": 28, "Q72": 28,
    "Q73a": 29, "Q73": 29, "Q74a": 29, "Q74": 29, "Q75": 29,
    "Q76a": 30, "Q76": 30, "Q77a": 30, "Q77": 30, "Q78": 30,
    "Q79a": 31, "Q79": 31, "Q80a": 31, "Q80": 31, "Q81": 31,
    "Q82a": 32, "Q82": 32, "Q83a": 32, "Q83": 32, "Q84": 32,
    "Q85a": 33, "Q85": 33, "Q86a": 33, "Q86": 33, "Q87": 33,
    "Q88a": 34, "Q88": 34, "Q89a": 34, "Q89": 34, "Q90": 34,
    "Q91a": 35, "Q91": 35, "Q92a": 35, "Q92": 35, "Q93": 35,
    "Q94a": 36, "Q94": 36, "Q95a": 36, "Q95": 36, "Q96": 36,
}

R = []

def domain_of(stem_no: int) -> str:
    if stem_no <= 8:
        return "indication"
    if stem_no <= 25:
        return "procedure"
    return "treatment_planning"

ACTION = {
    "Consensus agree": "endorse",
    "Consensus disagree": "against",
    "Consensus to neither agree nor disagree": "conditional",
    "No consensus": "report_option",
    "Consensus": "endorse_option",
}

def add(qid, text, typ, med, p30, p70, interp, soq="", pct="", dec="", flags="", table="1"):
    stem = STEM_MAP[qid]
    R.append((qid, stem, text, typ, med, p30, p70, interp, soq, pct, dec, flags, table))

# ---------------- Table 1: Indication ----------------
add("Q1", "The 3T and 1.5T MRIs are equally recommended for prostate cancer diagnosis, irrespective of the type of MRI scheduled (multiparametric vs biparametric).", "likert", 8, 7, 8, "Consensus agree", dec="d_accept_any_field_strength", flags="quality_adequate")
add("Q4a", "All the MRI sequences should be checked for quality standards.", "likert", 9, 9, 9, "Consensus agree", dec="d_mri_quality_check", flags="")
add("Q4b", "All the MRI sequences should be checked for quality standards according to PI-QUAL V.2 scores.", "likert", 8, 8, 8, "Consensus agree", dec="d_use_piqual_v2", flags="")
add("Q5", "The bpMRI and mpMRI may be equally recommended for prostate cancer diagnosis, provided that image quality is adequate for decision-making.", "likert", 8, 8, 8, "Consensus agree", dec="d_bpmri_acceptable", flags="quality_adequate")
add("Q6", "The bpMRI could be informative enough for prostate cancer diagnosis in patients under an early detection cancer pathway (opportunistic screening).", "likert", 8, 8, 8, "Consensus agree", dec="d_bpmri_acceptable", flags="bpmri|opportunistic_screening|quality_adequate")
add("Q7", "The bpMRI could be informative enough for prostate cancer diagnosis in patients under an organised cancer screening pathway.", "likert", 8, 8, 8, "Consensus agree", dec="d_bpmri_acceptable", flags="bpmri|organised_screening|quality_adequate")
add("Q8", "In case of multiple visible lesions, the maximal number of lesions to be reported should be (please, mark your best choice).", "soq", 0, 0, 0, "No consensus", soq="3 lesions", pct=53, dec="d_report_max3_lesions", flags="multiple_lesions")
add("Q10a", "In case of an indeterminate lesion at bpMRI, biopsy should be indicated by the result of an additional contrast-enhanced MRI sequence in case of a peripheral zone lesion.", "likert", 7, 7, 8, "Consensus agree", dec="d_contrast_mri_for_pz_indeterminate", flags="indeterminate_lesion|bpmri|pz_lesion")
add("Q10b", "In case of an indeterminate lesion at bpMRI, follow-up is needed.", "likert", 8, 8, 8, "Consensus agree", dec="d_followup_indeterminate_bpmri", flags="indeterminate_lesion|bpmri")
add("Q11", "In case of an indeterminate lesion at bpMRI, biopsy should be indicated by the result of PSA density.", "likert", 7, 7, 7, "Consensus agree", dec="d_psad_gate_bpmri_indeterminate", flags="indeterminate_lesion|bpmri")
add("Q12", "In case of an indeterminate lesion at bpMRI, biopsy should be indicated by the result of the risk calculator.", "likert", 6, 5, 6, "Consensus to neither agree nor disagree", dec="d_riskcalc_gate_bpmri_indeterminate", flags="indeterminate_lesion|bpmri|risk_calculator_available")
add("Q13", "In case of an indeterminate lesion at bpMRI, biopsy should be indicated by the result of serum or urine biomarkers.", "likert", 4, 3, 4, "Consensus to neither agree nor disagree", dec="d_biomarker_gate_bpmri_indeterminate", flags="indeterminate_lesion|bpmri|biomarker_available")
add("Q14", "In case of an indeterminate lesion at mpMRI, biopsy should be indicated by the result of PSA density.", "likert", 8, 8, 8, "Consensus agree", dec="d_psad_gate_mpmri_indeterminate", flags="indeterminate_lesion|mpmri")
add("Q15", "In case of an indeterminate lesion at mpMRI, biopsy should be indicated by the result of the risk calculator.", "likert", 7, 5, 7, "Consensus agree", dec="d_riskcalc_gate_mpmri_indeterminate", flags="indeterminate_lesion|mpmri|risk_calculator_available")
add("Q16", "In case of an indeterminate lesion at mpMRI, biopsy should be indicated by the result of serum or urine biomarkers.", "likert", 4, 3, 4, "Consensus to neither agree nor disagree", dec="d_biomarker_gate_mpmri_indeterminate", flags="indeterminate_lesion|mpmri|biomarker_available")
add("Q17", "PSMA PET should be preferred to MRI if available/feasible for primary prostate cancer diagnosis.", "likert", 2, 2, 2, "Consensus disagree", dec="d_reject_psma_pet_upfront", flags="psma_pet_available")
add("Q18", "In patients with an indeterminate MRI lesion, PSMA/PET-CT could be considered as an ancillary test, if available, to indicate a biopsy.", "likert", 6, 5, 7, "Consensus to neither agree nor disagree", dec="d_psma_pet_indeterminate_ancillary", flags="indeterminate_lesion|psma_pet_available")
add("Q19", "In case of a negative MRI and persistence of high suspicion of csPCa, PSMA PET-CT could be considered as an ancillary test, if available, to indicate a biopsy.", "likert", 8, 8, 8, "Consensus agree", dec="d_psma_pet_negative_mri_ancillary", flags="negative_mri|suspicion_high|psma_pet_available")
add("Q20", "Micro-ultrasound should be preferred to MRI if available/feasible for primary prostate cancer diagnosis.", "likert", 2, 1, 2, "Consensus disagree", dec="d_reject_microultrasound_upfront", flags="microultrasound_available")
add("Q21", "In patients with an indeterminate MRI lesion, prostate micro-ultrasound should be performed, if available, to indicate a biopsy.", "likert", 3, 2, 3, "Consensus to neither agree nor disagree", dec="d_reject_microultrasound_indeterminate", flags="indeterminate_lesion|microultrasound_available")
add("Q22", "In case of a negative MRI and persistence of high suspicion of csPCa, prostate micro-ultrasound should be performed.", "likert", 3, 2, 3, "Consensus to neither agree nor disagree", dec="d_reject_microultrasound_negative_mri", flags="negative_mri|suspicion_high|microultrasound_available")
add("Q25", "In case of a negative MRI and persistence of high suspicion of csPCa, systematic prostate biopsy should be performed.", "likert", 7, 7, 7, "Consensus agree", dec="d_sbx_negative_mri_high_suspicion", flags="negative_mri|suspicion_high")
add("Q26", "If available, AI algorithms should be used upfront to identify suspicious lesions on MRI (before radiologists' assessment).", "likert", 7, 7, 7, "Consensus agree", dec="d_ai_mri_lesion_aid", flags="ai_software_available")

# ---------------- Table 2: Procedure ----------------
add("Q34", "The optimal number of targeted cores per lesion should be adjusted based on PIRADS/Likert score.", "likert", 6, 6, 6, "Consensus to neither agree nor disagree", dec="d_tbx_cores_adapt_pirads", flags="visible_lesion", table="2")
add("Q35", "For a visible MRI lesion, the targeting should include not less than (mark your best choice).", "soq", 0, 0, 0, "No consensus", soq="3 cores", pct=66, dec="d_tbx_min3_cores", flags="visible_lesion", table="2")
add("Q36", "For PIRADS/Likert 4-5 lesions, the targeting should include not less than (mark your best choice).", "soq", 0, 0, 0, "No consensus", soq="3 cores", pct=68, dec="d_tbx_min3_cores", flags="visible_lesion|pirads_4_5", table="2")
add("Q37a", "If doing it, which term best describes extra cores taken around the region of interest (mark your best choice).", "soq", 0, 0, 0, "Consensus", soq="Perilesional", pct=97, dec="d_adopt_term_perilesional", flags="", table="2")
add("Q38", "If doing it, extra cores taken around the region of interest (ROI) should be taken in a range of (mark your best choice).", "soq", 0, 0, 0, "Consensus", soq="10 mm around ROI", pct=82, dec="d_plbx_within_10mm", flags="", table="2")
add("Q39", "If doing it, the number of extra cores taken around the region of interest (ROI) should depend on the size of the MRI lesion.", "likert", 7, 7, 7, "Consensus agree", dec="d_plbx_count_by_lesion_size", flags="visible_lesion", table="2")
add("Q40", "If doing it, the minimum number of extra cores taken around the region of interest (ROI) for smaller visible MRI lesions (<10 mm) is (mark your best choice).", "soq", 0, 0, 0, "No consensus", soq="2 cores", pct=67, dec="d_plbx_2cores_small_lesion", flags="lesion_small", table="2")
add("Q41", "For larger visible MRI lesions (>10 mm), the maximum number of extra cores taken around the region of interest (ROI) is (mark your best choice).", "soq", 0, 0, 0, "Consensus", soq="2 cores", pct=76, dec="d_plbx_max2cores_large_lesion", flags="lesion_large", table="2")
add("Q42", "In case of a visible MRI lesion, ONLY a targeted biopsy should be performed.", "likert", 4, 3, 4, "Consensus to neither agree nor disagree", dec="d_scheme_unifocal_tbx_plbx", flags="visible_lesion", table="2")
add("Q43", "In case of a unifocal visible MRI lesion, targeted biopsy (Bx) + Bx of the area around the ROI should be performed.", "likert", 7, 7, 8, "Consensus agree", dec="d_scheme_unifocal_tbx_plbx", flags="visible_lesion|unifocal", table="2")
add("Q44a", "In case of unifocal visible MRI lesions, targeted biopsy (Bx) + contralateral Bx should be performed.", "likert", 5, 4, 6, "Consensus to neither agree nor disagree", dec="d_scheme_unifocal_add_contralateral", flags="visible_lesion|unifocal", table="2")
add("Q44", "In case of a unifocal visible MRI lesion, targeted biopsy (Bx) + Bx of the area around the ROI + contralateral Bx should be performed.", "likert", 6, 5, 6, "Consensus to neither agree nor disagree", dec="d_scheme_unifocal_add_contralateral", flags="visible_lesion|unifocal", table="2")
add("Q45", "In case of a unifocal visible MRI lesion, targeted biopsy (Bx) + Bx of the area around the ROI + systematic Bx should be performed.", "likert", 3, 3, 3, "Consensus disagree", dec="d_scheme_unifocal_add_sbx", flags="visible_lesion|unifocal", table="2")
add("Q46a", "In case of a multifocal ipsilateral visible MRI lesion, ONLY a targeted biopsy should be performed.", "likert", 6, 6, 6, "Consensus to neither agree nor disagree", dec="d_scheme_ipsilateral_multifocal", flags="visible_lesion|multifocal_ipsilateral", table="2")
add("Q46b", "In case of multifocal ipsilateral visible MRI lesions, targeted biopsy (Bx) + Bx of the area around the ROI should be performed.", "likert", 6, 6, 7, "Consensus to neither agree nor disagree", dec="d_scheme_ipsilateral_multifocal", flags="visible_lesion|multifocal_ipsilateral", table="2")
add("Q47a", "In case of multifocal ipsilateral visible MRI lesions, targeted biopsy (Bx) + contralateral Bx should be performed.", "likert", 4, 2, 6, "Consensus to neither agree nor disagree", dec="d_scheme_ipsilateral_multifocal", flags="visible_lesion|multifocal_ipsilateral", table="2")
add("Q47", "In case of multifocal ipsilateral visible MRI lesions, targeted biopsy (Bx) + Bx of the area around the ROI + contralateral Bx should be performed.", "likert", 5, 3, 5, "Consensus to neither agree nor disagree", dec="d_scheme_ipsilateral_multifocal", flags="visible_lesion|multifocal_ipsilateral", table="2")
add("Q48", "In case of multifocal ipsilateral visible MRI lesions, targeted biopsy (Bx) + Bx of the area around the ROI + systematic Bx should be performed.", "likert", 4, 2, 4, "Consensus to neither agree nor disagree", dec="d_scheme_ipsilateral_multifocal", flags="visible_lesion|multifocal_ipsilateral", table="2")
add("Q49a", "In case of multifocal bilateral visible MRI lesions, ONLY targeted biopsy (Bx) should be performed.", "likert", 6, 6, 7, "Consensus to neither agree nor disagree", dec="d_scheme_bilateral_tbx_plbx", flags="visible_lesion|multifocal_bilateral", table="2")
add("Q49", "In case of multifocal bilateral visible MRI lesions, targeted biopsy (Bx) + Bx of the area around the ROI should be performed.", "likert", 7, 6, 8, "Consensus agree", dec="d_scheme_bilateral_tbx_plbx", flags="visible_lesion|multifocal_bilateral", table="2")
add("Q50", "In case of multifocal bilateral visible MRI lesions, targeted biopsy (Bx) + Bx of the area around the ROI + systematic Bx should be performed.", "likert", 4, 2, 4, "Consensus to neither agree nor disagree", dec="d_scheme_bilateral_tbx_plbx", flags="visible_lesion|multifocal_bilateral", table="2")
add("Q51", "In the case systematic biopsy is indicated, the sextant (3 cores per lobe) biopsy template should be used.", "likert", 3, 2, 3, "Consensus disagree", dec="d_reject_sextant_template", flags="", table="2")
add("Q52", "In the case systematic biopsy is indicated, the 12-core (6 cores per lobe) biopsy template should be used.", "likert", 8, 8, 8, "Consensus agree", dec="d_sbx_12core_template", flags="", table="2")
add("Q53", "In the case systematic biopsy is indicated, the Ginsburg biopsy template (at least 12 cores per lobe) should be used.", "likert", 3, 3, 3, "Consensus disagree", dec="d_reject_ginsburg_template", flags="", table="2")
add("Q54", "In the case that systematic biopsy is indicated, the 0.5 mm saturation biopsy should be used.", "likert", 2, 1, 2, "Consensus disagree", dec="d_reject_saturation_bx", flags="", table="2")
add("Q55a", "In the case of a negative MRI but high suspicion of csPCa, 12 cores (6 cores per lobe) systematic biopsy should be performed.", "likert", 7, 7, 7, "Consensus agree", dec="d_sbx_12core_template", flags="negative_mri|suspicion_high", table="2")
add("Q55b", "In the case of a negative MRI but high suspicion of csPCa, systematic biopsy according to the Ginsburg scheme should be performed.", "likert", 6, 4, 6, "Consensus to neither agree nor disagree", dec="d_reject_ginsburg_template", flags="negative_mri|suspicion_high", table="2")
add("Q56", "In the case of a negative MRI but high suspicion of csPCa, saturation biopsy should be performed (24 cores).", "likert", 2, 1, 2, "Consensus disagree", dec="d_reject_saturation_bx", flags="negative_mri|suspicion_high", table="2")
add("Q57", "Systematic biopsy should be reduced to a maximum of 6 cores in total in men with suspicion of locally advanced disease on digital rectal examination and/or PSA > 50 ng/mL, or those who are not fit for curative treatments.", "likert", 8, 8, 8, "Consensus agree", dec="d_sbx_reduced_6core_advanced", flags="locally_advanced_suspected|psa_gt_50|unfit_curative", table="2")
add("Q58", "The standard approach for prostate biopsy should be (mark your best choice).", "soq", 0, 0, 0, "Consensus", soq="Transperineal approach", pct=97, dec="d_route_transperineal", flags="", table="2")
add("Q59", "Anaesthesia standard for transrectal biopsy should be (mark your best choice).", "soq", 0, 0, 0, "Consensus", soq="Periprostatic nerve block", pct=83, dec="d_pnb_tr", flags="", table="2")
add("Q60", "Anaesthesia standard for transperineal biopsy should be (mark your best choice).", "soq", 0, 0, 0, "Consensus", soq="Periprostatic nerve block", pct=90, dec="d_pnb_tp", flags="", table="2")
add("Q62", "In case of transperineal biopsy, antibiotic prophylaxis regimen should be (mark your best choice). Risk factors: antibiotic use in the previous 6 months, international travelling in the previous 6 months, hospitalisation in the previous 6 months, non-sterile urine culture, UTI in the previous 6 months, sub(de)compensated DM.", "soq", 0, 0, 0, "Consensus", soq="Omitted for every patient except those with risk factors", pct=88, dec="d_omit_abx_tp_no_risk", flags="", table="2")
add("Q63", "In case of transrectal biopsy, the preferred antibiotic prophylaxis regimen is (mark your best choice).", "soq", 0, 0, 0, "No consensus", soq="Augmented antibiotic prophylaxis", pct=67, dec="d_augmented_abx_tr", flags="", table="2")

# ---------------- Table 3: Treatment planning ----------------
add("Q64", "In patients with unifocal visible MRI, targeted biopsy (Bx) ONLY is informative enough for focal treatment planning.", "likert", 5, 4, 6, "Consensus to neither agree nor disagree", dec="d_tp_focal_tbx_only_not_enough", flags="unifocal|intent_focal_therapy", table="3")
add("Q64a", "In patients with unifocal visible MRI, targeted biopsy (Bx) + Bx of the area around the ROI only is informative enough for focal treatment planning.", "likert", 5, 5, 6, "Consensus to neither agree nor disagree", dec="d_tp_focal_tbx_only_not_enough", flags="unifocal|intent_focal_therapy", table="3")
add("Q65a", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) + contralateral Bx should be performed for focal treatment planning.", "likert", 5, 4, 7, "Consensus to neither agree nor disagree", dec="d_tp_focal_tbx_only_not_enough", flags="unifocal|intent_focal_therapy", table="3")
add("Q65", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) + Bx of the area around the ROI + contralateral systematic Bx should be performed for focal treatment planning.", "likert", 7, 5, 7, "Consensus agree", dec="d_tp_focal_add_contralateral", flags="unifocal|intent_focal_therapy", table="3")
add("Q66", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) + bilateral systematic Bx should be performed for focal treatment planning.", "likert", 5, 4, 5, "Consensus to neither agree nor disagree", dec="d_tp_focal_tbx_only_not_enough", flags="unifocal|intent_focal_therapy", table="3")
add("Q67a", "In patients with unifocal visible MRI, targeted biopsy (Bx) ONLY is informative enough for nerve-sparing surgical planning.", "likert", 6, 5, 7, "Consensus to neither agree nor disagree", dec="d_tp_nss_unifocal_tbx_plbx", flags="unifocal|intent_nerve_sparing", table="3")
add("Q67", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) + Bx of the area around the ROI only is informative enough for nerve-sparing surgical planning.", "likert", 7, 7, 7, "Consensus agree", dec="d_tp_nss_unifocal_tbx_plbx", flags="unifocal|intent_nerve_sparing", table="3")
add("Q68a", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) + contralateral Bx should be performed for nerve-sparing surgical planning.", "likert", 5, 3, 6, "Consensus to neither agree nor disagree", dec="d_tp_nss_unifocal_tbx_plbx", flags="unifocal|intent_nerve_sparing", table="3")
add("Q68", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) + Bx of the area around the ROI + contralateral systematic Bx should be performed for nerve-sparing surgical planning.", "likert", 4, 2, 4, "Consensus to neither agree nor disagree", dec="d_tp_nss_unifocal_tbx_plbx", flags="unifocal|intent_nerve_sparing", table="3")
add("Q69", "In patients with unifocal visible MRI lesion, targeted biopsy (Bx) + bilateral systematic Bx should be performed for nerve-sparing surgical planning.", "likert", 4, 2, 4, "Consensus to neither agree nor disagree", dec="d_tp_nss_unifocal_tbx_plbx", flags="unifocal|intent_nerve_sparing", table="3")
add("Q70a", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) ONLY is informative enough for nerve-sparing surgical planning.", "likert", 7, 7, 7, "Consensus agree", dec="d_tp_nss_bilateral_tbx_adequate", flags="multifocal_bilateral|intent_nerve_sparing", table="3")
add("Q70", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + Bx of the area around the ROI only is informative enough for nerve-sparing surgical planning.", "likert", 7, 7, 8, "Consensus agree", dec="d_tp_nss_bilateral_tbx_adequate", flags="multifocal_bilateral|intent_nerve_sparing", table="3")
add("Q71a", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + contralateral Bx should be performed for nerve-sparing surgical planning.", "likert", 4, 2, 5, "Consensus to neither agree nor disagree", dec="d_tp_nss_bilateral_tbx_adequate", flags="multifocal_bilateral|intent_nerve_sparing", table="3")
add("Q71", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + Bx of the area around the ROI + systematic Bx should be performed for nerve-sparing surgical planning.", "likert", 3, 3, 3, "Consensus disagree", dec="d_tp_nss_bilateral_tbx_adequate", flags="multifocal_bilateral|intent_nerve_sparing", table="3")
add("Q72", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + bilateral systematic Bx should be performed for nerve-sparing surgical planning.", "likert", 4, 3, 4, "Consensus to neither agree nor disagree", dec="d_tp_nss_bilateral_tbx_adequate", flags="multifocal_bilateral|intent_nerve_sparing", table="3")
add("Q73a", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) ONLY is informative enough for selecting patients as candidates for lymphadenectomy.", "likert", 6, 5, 6, "Consensus to neither agree nor disagree", dec="d_tp_plnd_unifocal_no_consensus", flags="unifocal|intent_plnd", table="3")
add("Q73", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) + Bx of the area around the ROI only is informative enough for selecting patients as candidates for lymphadenectomy.", "likert", 6, 6, 7, "Consensus to neither agree nor disagree", dec="d_tp_plnd_unifocal_no_consensus", flags="unifocal|intent_plnd", table="3")
add("Q74a", "In patients with unifocal visible MRI lesion, targeted biopsy (Bx) + contralateral Bx should be performed to select patients as candidates for lymphadenectomy.", "likert", 4, 2, 6, "Consensus to neither agree nor disagree", dec="d_tp_plnd_unifocal_no_consensus", flags="unifocal|intent_plnd", table="3")
add("Q74", "In patients with unifocal visible MRI lesion, targeted biopsy (Bx) + Bx of the area around the ROI + contralateral systematic Bx should be performed to select patients as candidates for lymphadenectomy.", "likert", 3, 2, 3, "Consensus disagree", dec="d_tp_plnd_unifocal_no_consensus", flags="unifocal|intent_plnd", table="3")
add("Q75", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) + bilateral systematic Bx should be performed to select patients as candidates for lymphadenectomy.", "likert", 3, 2, 3, "Consensus disagree", dec="d_tp_plnd_unifocal_no_consensus", flags="unifocal|intent_plnd", table="3")
add("Q76a", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) ONLY is informative enough for selecting patients as candidates for lymphadenectomy.", "likert", 7, 6, 7, "Consensus agree", dec="d_tp_plnd_bilateral_tbx_plbx", flags="multifocal_bilateral|intent_plnd", table="3")
add("Q76", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + Bx of the area around the ROI only is informative enough for selecting patients as candidates for lymphadenectomy.", "likert", 7, 7, 7, "Consensus agree", dec="d_tp_plnd_bilateral_tbx_plbx", flags="multifocal_bilateral|intent_plnd", table="3")
add("Q77a", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + contralateral Bx should be performed for selecting patients candidate to lymphadenectomy.", "likert", 4, 2, 5, "Consensus to neither agree nor disagree", dec="d_tp_plnd_bilateral_tbx_plbx", flags="multifocal_bilateral|intent_plnd", table="3")
add("Q77", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + Bx of the area around the ROI + systematic Bx should be performed for selecting patients as candidates for lymphadenectomy.", "likert", 3, 2, 3, "Consensus disagree", dec="d_tp_plnd_bilateral_tbx_plbx", flags="multifocal_bilateral|intent_plnd", table="3")
add("Q78", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + bilateral systematic Bx should be performed for selecting patients candidate to lymphadenectomy.", "likert", 2, 2, 2, "Consensus disagree", dec="d_tp_plnd_bilateral_tbx_plbx", flags="multifocal_bilateral|intent_plnd", table="3")
add("Q79a", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) ONLY is informative enough for whole gland radiotherapy planning.", "likert", 7, 7, 8, "Consensus agree", dec="d_tp_wg_rt_tbx_plbx", flags="unifocal|intent_whole_gland_rt", table="3")
add("Q79", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) + Bx of the area around the ROI only is informative enough for whole gland radiotherapy planning.", "likert", 8, 7, 8, "Consensus agree", dec="d_tp_wg_rt_tbx_plbx", flags="unifocal|intent_whole_gland_rt", table="3")
add("Q80a", "In patients with unifocal visible MRI lesion, targeted biopsy (Bx) + contralateral Bx should be performed for whole gland radiotherapy planning.", "likert", 4, 2, 6, "Consensus to neither agree nor disagree", dec="d_tp_wg_rt_tbx_plbx", flags="unifocal|intent_whole_gland_rt", table="3")
add("Q80", "In patients with unifocal visible MRI lesion, targeted biopsy (Bx) + Bx of the area around the ROI + contralateral systematic Bx should be performed for whole gland radiotherapy planning.", "likert", 4, 2, 4, "Consensus to neither agree nor disagree", dec="d_tp_wg_rt_tbx_plbx", flags="unifocal|intent_whole_gland_rt", table="3")
add("Q81", "In patients with unifocal visible MRI lesion, targeted biopsy (Bx) + bilateral systematic Bx should be performed for whole gland radiotherapy planning.", "likert", 3, 2, 3, "Consensus disagree", dec="d_tp_reject_adding_systematic_universal", flags="unifocal|intent_whole_gland_rt", table="3")
add("Q82a", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) ONLY is informative enough for whole gland radiotherapy planning.", "likert", 7, 7, 8, "Consensus agree", dec="d_tp_wg_rt_tbx_plbx", flags="multifocal_bilateral|intent_whole_gland_rt", table="3")
add("Q82", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + Bx of the area around the ROI only is informative enough for whole gland radiotherapy planning.", "likert", 7, 7, 8, "Consensus agree", dec="d_tp_wg_rt_tbx_plbx", flags="multifocal_bilateral|intent_whole_gland_rt", table="3")
add("Q83a", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + contralateral Bx should be performed for whole-gland radiotherapy planning.", "likert", 3, 2, 4, "Consensus disagree", dec="d_tp_reject_adding_systematic_universal", flags="multifocal_bilateral|intent_whole_gland_rt", table="3")
add("Q83", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + Bx of the area around the ROI + systematic Bx should be performed for whole gland radiotherapy planning.", "likert", 3, 2, 3, "Consensus disagree", dec="d_tp_reject_adding_systematic_universal", flags="multifocal_bilateral|intent_whole_gland_rt", table="3")
add("Q84", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + systematic Bx should be performed for whole gland radiotherapy planning.", "likert", 3, 2, 3, "Consensus disagree", dec="d_tp_reject_adding_systematic_universal", flags="multifocal_bilateral|intent_whole_gland_rt", table="3")
add("Q85a", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) ONLY is informative enough for focal radiotherapy boost planning.", "likert", 8, 7, 8, "Consensus agree", dec="d_tp_focal_boost_tbx_plbx", flags="unifocal|intent_focal_boost", table="3")
add("Q85", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) + Bx of the area around the ROI only is informative enough for focal radiotherapy boost planning.", "likert", 7, 7, 7, "Consensus agree", dec="d_tp_focal_boost_tbx_plbx", flags="unifocal|intent_focal_boost", table="3")
add("Q86a", "In patients with unifocal visible MRI lesion, targeted biopsy (Bx) + contralateral Bx should be performed for focal radiotherapy boost planning.", "likert", 4, 2, 5, "Consensus to neither agree nor disagree", dec="d_tp_focal_boost_tbx_plbx", flags="unifocal|intent_focal_boost", table="3")
add("Q86", "In patients with unifocal visible MRI lesion, targeted biopsy (Bx) + Bx of the area around the ROI + contralateral systematic Bx should be performed for focal radiotherapy boost planning.", "likert", 4, 3, 4, "Consensus to neither agree nor disagree", dec="d_tp_focal_boost_tbx_plbx", flags="unifocal|intent_focal_boost", table="3")
add("Q87", "In patients with unifocal visible MRI lesion, targeted biopsy (Bx) + bilateral systematic Bx should be performed for focal radiotherapy boost planning.", "likert", 3, 2, 3, "Consensus disagree", dec="d_tp_reject_adding_systematic_universal", flags="unifocal|intent_focal_boost", table="3")
add("Q88a", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) ONLY is informative enough for focal radiotherapy boost planning.", "likert", 7, 7, 7, "Consensus agree", dec="d_tp_focal_boost_tbx_plbx", flags="multifocal_bilateral|intent_focal_boost", table="3")
add("Q88", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + Bx of the area around the ROI only is informative enough for focal radiotherapy boost planning.", "likert", 8, 8, 8, "Consensus agree", dec="d_tp_focal_boost_tbx_plbx", flags="multifocal_bilateral|intent_focal_boost", table="3")
add("Q89a", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + contralateral Bx should be performed for focal radiotherapy boost planning.", "likert", 3, 2, 3, "Consensus disagree", dec="d_tp_reject_adding_systematic_universal", flags="multifocal_bilateral|intent_focal_boost", table="3")
add("Q89", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + Bx of the area around the ROI + systematic Bx should be performed for focal radiotherapy boost planning.", "likert", 3, 2, 3, "Consensus disagree", dec="d_tp_reject_adding_systematic_universal", flags="multifocal_bilateral|intent_focal_boost", table="3")
add("Q90", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + systematic Bx should be performed for focal radiotherapy boost planning.", "likert", 3, 2, 3, "Consensus disagree", dec="d_tp_reject_adding_systematic_universal", flags="multifocal_bilateral|intent_focal_boost", table="3")
add("Q91a", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) ONLY is informative enough for ADT length planning.", "likert", 7, 7, 7, "Consensus agree", dec="d_tp_adt_duration_tbx_plbx", flags="unifocal|intent_adt_duration", table="3")
add("Q91", "In patients with a unifocal visible MRI lesion, targeted biopsy (Bx) + Bx of the area around the ROI only is informative enough for ADT length planning.", "likert", 8, 8, 8, "Consensus agree", dec="d_tp_adt_duration_tbx_plbx", flags="unifocal|intent_adt_duration", table="3")
add("Q92a", "In patients with unifocal visible MRI lesion, targeted biopsy (Bx) + contralateral Bx should be performed for ADT length planning.", "likert", 4, 2, 5, "Consensus to neither agree nor disagree", dec="d_tp_adt_duration_tbx_plbx", flags="unifocal|intent_adt_duration", table="3")
add("Q92", "In patients with unifocal visible MRI lesion, targeted biopsy (Bx) + Bx of the area around the ROI + contralateral systematic Bx should be performed for ADT length planning.", "likert", 3, 3, 3, "Consensus disagree", dec="d_tp_reject_adding_systematic_universal", flags="unifocal|intent_adt_duration", table="3")
add("Q93", "In patients with unifocal visible MRI lesion, targeted biopsy (Bx) + bilateral systematic Bx should be performed for ADT length planning.", "likert", 3, 2, 3, "Consensus disagree", dec="d_tp_reject_adding_systematic_universal", flags="unifocal|intent_adt_duration", table="3")
add("Q94a", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) ONLY is informative enough for ADT length planning.", "likert", 7, 7, 7, "Consensus agree", dec="d_tp_adt_duration_tbx_plbx", flags="multifocal_bilateral|intent_adt_duration", table="3")
add("Q94", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + Bx of the area around the ROI only is informative enough for ADT length planning.", "likert", 8, 7, 8, "Consensus agree", dec="d_tp_adt_duration_tbx_plbx", flags="multifocal_bilateral|intent_adt_duration", table="3")
add("Q95a", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + contralateral Bx should be performed for ADT length planning.", "likert", 3, 2, 4, "Consensus disagree", dec="d_tp_reject_adding_systematic_universal", flags="multifocal_bilateral|intent_adt_duration", table="3")
add("Q95", "In patients with bilateral visible MRI lesions, targeted biopsy (Bx) + perilesional Bx + systematic Bx should be performed for ADT length planning.", "likert", 2, 2, 2, "Consensus disagree", dec="d_tp_reject_adding_systematic_universal", flags="multifocal_bilateral|intent_adt_duration", table="3")
add("Q96", "In patients with bilateral visible MRI lesion, targeted biopsy (Bx) + systematic Bx should be performed for ADT length planning.", "likert", 2, 2, 2, "Consensus disagree", dec="d_tp_reject_adding_systematic_universal", flags="multifocal_bilateral|intent_adt_duration", table="3")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # sanity: 112 statements, unique ids, stems within 1-36
    qids = [r[0] for r in R]
    assert len(R) == 112, f"expected 112 statements, got {len(R)}"
    assert len(set(qids)) == 112, "duplicate statement ids"
    stems = {r[1] for r in R}
    assert stems == set(range(1, 37)), f"stem coverage broken: {sorted(stems)}"
    with io.open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        for (qid, stem, text, typ, med, p30, p70, interp, soq, pct, dec, flags, table) in R:
            w.writerow([
                qid, domain_of(stem), stem, STEM_NAMES[stem], text, typ,
                med if typ == "likert" else "", p30 if typ == "likert" else "",
                p70 if typ == "likert" else "", interp, soq, pct, dec, flags,
                ACTION[interp], f"Table {table} ({qid})",
            ])
    n_agree = sum(1 for r in R if r[7] == "Consensus agree")
    n_against = sum(1 for r in R if r[7] == "Consensus disagree")
    n_neither = sum(1 for r in R if r[7] == "Consensus to neither agree nor disagree")
    n_soq_cons = sum(1 for r in R if r[7] == "Consensus")
    n_soq_no = sum(1 for r in R if r[7] == "No consensus")
    # consistency check vs paper abstract: "Consensus was achieved for 29 of 36 stems"
    stems_agreed = {r[1] for r in R if r[7] in ("Consensus agree", "Consensus")}
    assert len(stems_agreed) == 29, (
        f"expected 29 stems with consensus agreement (paper abstract), got {len(stems_agreed)}"
    )
    print(f"[ok] probiopsy_statements.csv written: {len(R)} statements -> {OUT}")
    print(f"     agree={n_agree} disagree={n_against} neither={n_neither} "
          f"soq_consensus={n_soq_cons} soq_noconsensus={n_soq_no}")
    print(f"     stems with consensus agreement = {len(stems_agreed)}/36 (paper: 29/36)")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
