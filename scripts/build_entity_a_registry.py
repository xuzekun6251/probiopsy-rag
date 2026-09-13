# -*- coding: utf-8 -*-
"""Build Entity A registry (patient clinical scenario elements) for probiopsy-rag.

Source of truth:
  - ProBIOPSY consensus (Chernysheva et al., Eur Urol 2026, doi:10.1016/j.eururo.2026.06.012)
    Tables 1-3 statement conditioning variables (112 statements, 36 stems)
  - EAU PCa Guidelines 2024 (ref [12] of the consensus) risk/candidate factors
  - PI-RADS v2.1 lexicon (lesion descriptors)

Column semantics (TongYuan-compatible headers, reinterpreted for this domain):
  patient_clinical_scenario_id  stable snake_case id
  primary_name                  EN clinical name
  aliases                       '|'-separated synonyms (EN + zh-CN)
  category                      imaging | lab_biomarker | clinical | history_risk |
                                treatment_intent | resource_availability
  active_mechanisms             '|'-separated decision-mechanism tags
                                (how the element modulates biopsy decisions)
  flags                         '|'-separated machine-matching tags consumed by
                                configs/rules.yaml (entity_a_flags)
  evidence_sources              '|'-separated ProBIOPSY statement ids / guideline refs
"""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "seed" / "entities_a.csv"

HEADER = [
    "patient_clinical_scenario_id", "primary_name", "aliases", "category",
    "active_mechanisms", "flags", "evidence_sources",
]

# (id, name, aliases, category, mechanisms, flags, sources)
ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    # ---------------- imaging: pathway & quality ----------------
    ("mri_quality_adequate", "Prostate MRI with adequate image quality",
     "PI-QUAL>=3|影像质量合格",
     "imaging", "enables_mri_driven_pathway",
     "quality_adequate|imaging_available", "ProBIOPSY Q4a Q4b Q5|PI-QUAL v2"),
    ("mri_quality_inadequate", "Prostate MRI with inadequate image quality",
     "PI-QUAL<3|影像质量不合格",
     "imaging", "blocks_mri_driven_pathway",
     "quality_inadequate|imaging_available", "ProBIOPSY Q4a Q4b|PRIME trial"),
    ("bpmri_performed", "Biparametric prostate MRI performed",
     "bpMRI|双参数MRI",
     "imaging", "alternative_primary_imaging",
     "bpmri|imaging_available", "ProBIOPSY Q5 Q6 Q7"),
    ("mpmri_performed", "Multiparametric prostate MRI performed",
     "mpMRI|多参数MRI",
     "imaging", "reference_primary_imaging",
     "mpmri|imaging_available", "ProBIOPSY Q5 Q14 Q15"),
    ("mri_3t", "3T MRI scanner",
     "3特斯拉",
     "imaging", "field_strength_unrestricted",
     "mri_3t", "ProBIOPSY Q1"),
    ("mri_15t", "1.5T MRI scanner",
     "1.5特斯拉",
     "imaging", "field_strength_unrestricted",
     "mri_15t", "ProBIOPSY Q1"),
    ("opportunistic_screening_pathway", "Patient under opportunistic early-detection pathway",
     "机会性筛查",
     "clinical", "screening_context_bpmri",
     "opportunistic_screening", "ProBIOPSY Q6"),
    ("organised_screening_pathway", "Patient under organised screening pathway",
     "组织化筛查",
     "clinical", "screening_context_bpmri",
     "organised_screening", "ProBIOPSY Q7"),
    # ---------------- imaging: lesion pattern ----------------
    ("mri_negative", "Negative prostate MRI (no visible lesion)",
     "MRI阴性|无可疑病灶",
     "imaging", "tbx_not_applicable",
     "negative_mri|imaging_available", "ProBIOPSY Q19 Q22 Q25 Q55a"),
    ("mri_indeterminate_lesion", "Indeterminate lesion on MRI (PI-RADS 3)",
     "PI-RADS 3|不确定性病灶",
     "imaging", "ancillary_gating_required",
     "indeterminate_lesion|pirads_3|imaging_available", "ProBIOPSY Q10a-Q16 Q18 Q21"),
    ("mri_visible_lesion_pirads4", "Visible lesion PI-RADS 4",
     "PI-RADS 4",
     "imaging", "tbx_indicated",
     "visible_lesion|pirads_4_5|imaging_available", "ProBIOPSY Q35 Q36"),
    ("mri_visible_lesion_pirads5", "Visible lesion PI-RADS 5",
     "PI-RADS 5",
     "imaging", "tbx_indicated",
     "visible_lesion|pirads_4_5|imaging_available", "ProBIOPSY Q35 Q36"),
    ("unifocal_lesion", "Unifocal MRI-visible lesion",
     "单发病灶",
     "imaging", "scheme_selection_key",
     "visible_lesion|unifocal", "ProBIOPSY Q43-Q45 Q64-Q81"),
    ("multifocal_ipsilateral_lesions", "Multifocal ipsilateral MRI-visible lesions",
     "同侧多发病灶",
     "imaging", "scheme_selection_key",
     "visible_lesion|multifocal_ipsilateral", "ProBIOPSY Q46a-Q48"),
    ("multifocal_bilateral_lesions", "Multifocal bilateral MRI-visible lesions",
     "双侧多发病灶",
     "imaging", "scheme_selection_key",
     "visible_lesion|multifocal_bilateral", "ProBIOPSY Q49 Q50 Q70-Q96"),
    ("lesion_size_lt_10mm", "Index lesion <10 mm",
     "小病灶|病灶<10mm",
     "imaging", "plbx_count_upward_adjust",
     "lesion_small", "ProBIOPSY Q39 Q40"),
    ("lesion_size_gte_10mm", "Index lesion >=10 mm",
     "大病灶|病灶>=10mm",
     "imaging", "plbx_count_downward_adjust",
     "lesion_large", "ProBIOPSY Q39 Q41"),
    ("lesion_peripheral_zone", "Indeterminate lesion in peripheral zone",
     "外周带病灶",
     "imaging", "contrast_mri_add_on",
     "pz_lesion", "ProBIOPSY Q10a"),
    ("multiple_lesions_gt3", "More than three MRI-visible lesions",
     "病灶数>3",
     "imaging", "reporting_cap_question",
     "multiple_lesions", "ProBIOPSY Q8"),
    # ---------------- lab / biomarker ----------------
    ("psa_elevated", "Elevated PSA",
     "PSA升高",
     "lab_biomarker", "raises_clinical_suspicion",
     "psa_elevated", "ProBIOPSY Q25|EAU 2024"),
    ("psa_density_lt_0.10", "PSA density <0.10 ng/mL/cc",
     "PSAD低",
     "lab_biomarker", "low_csPCa_probability",
     "psad_low", "Schoots 2021 (consensus SM2 ref 12)"),
    ("psa_density_0.10_0.15", "PSA density 0.10-0.15 ng/mL/cc",
     "PSAD中",
     "lab_biomarker", "intermediate_csPCa_probability",
     "psad_intermediate", "Schoots 2021 (consensus SM2 ref 12)"),
    ("psa_density_0.15_0.20", "PSA density 0.15-0.20 ng/mL/cc",
     "PSAD中高",
     "lab_biomarker", "gates_biopsy_indication",
     "psad_intermediate_high", "ProBIOPSY Q11 Q14 Q25"),
    ("psa_density_gte_0.20", "PSA density >=0.20 ng/mL/cc",
     "PSAD高",
     "lab_biomarker", "strong_biopsy_indicator",
     "psad_high", "ProBIOPSY Q11 Q14 Q25"),
    ("psa_gt_50", "PSA >50 ng/mL",
     "PSA大于50",
     "lab_biomarker", "advanced_disease_indicator",
     "psa_gt_50|advanced_disease", "ProBIOPSY Q57"),
    ("risk_calculator_available", "Validated risk calculator available (EAU Rotterdam)",
     "风险计算器",
     "lab_biomarker", "ancillary_gating_mpMRI",
     "risk_calculator_available", "ProBIOPSY Q12 Q15|EAU 2024"),
    ("serum_urine_biomarker_available", "Serum/urine biomarker available (e.g. Proclarix, PHI)",
     "血清或尿液标志物",
     "lab_biomarker", "no_consensus_gating_value",
     "biomarker_available", "ProBIOPSY Q13 Q16"),
    ("nonsterile_urine_culture", "Non-sterile pre-biopsy urine culture",
     "尿液培养非无菌",
     "lab_biomarker", "infection_risk_marker",
     "infection_risk_factor", "ProBIOPSY Q62"),
    # ---------------- clinical presentation ----------------
    ("positive_dre", "Abnormal digital rectal examination",
     "DRE阳性|直肠指检异常",
     "clinical", "raises_clinical_suspicion",
     "dre_positive", "ProBIOPSY Q25 Q57"),
    ("suspected_locally_advanced", "Suspected locally advanced disease (cT3 on DRE)",
     "疑局部晚期|cT3",
     "clinical", "reduced_sbx_scheme",
     "locally_advanced_suspected|advanced_disease", "ProBIOPSY Q57"),
    ("high_suspicion_cspca", "Persistent high clinical suspicion of csPCa (composite)",
     "高度临床怀疑",
     "clinical", "biopsy_despite_negative_mri",
     "suspicion_high", "ProBIOPSY Q19 Q22 Q25"),
    ("family_history_pca", "Family history of prostate cancer",
     "家族史",
     "clinical", "raises_clinical_suspicion",
     "family_history", "ProBIOPSY Q25|EAU 2024"),
    ("black_ethnicity", "Black ethnicity",
     "黑人人种",
     "demographic", "raises_clinical_suspicion",
     "black_ethnicity", "ProBIOPSY Q25|EAU 2024"),
    ("prior_negative_biopsy", "Prior negative prostate biopsy",
     "既往穿刺阴性|再穿刺",
     "history_risk", "rebiopsy_context",
     "prior_negative_biopsy", "ProBIOPSY SM2 (FUTURE/in-bore evidence)"),
    ("unfit_curative_treatment", "Unfit for curative treatment",
     "不适合根治治疗",
     "clinical", "reduced_sbx_scheme",
     "unfit_curative", "ProBIOPSY Q57"),
    # ---------------- history: infection risk factors (ProBIOPSY Q62 footnote) ----------------
    ("antibiotic_use_6mo", "Antibiotic use within previous 6 months",
     "近6月抗生素使用",
     "history_risk", "infection_risk_marker",
     "infection_risk_factor", "ProBIOPSY Q62"),
    ("international_travel_6mo", "International travel within previous 6 months",
     "近6月国际旅行",
     "history_risk", "infection_risk_marker",
     "infection_risk_factor", "ProBIOPSY Q62"),
    ("hospitalisation_6mo", "Hospitalisation within previous 6 months",
     "近6月住院",
     "history_risk", "infection_risk_marker",
     "infection_risk_factor", "ProBIOPSY Q62"),
    ("uti_6mo", "Urinary tract infection within previous 6 months",
     "近6月尿路感染",
     "history_risk", "infection_risk_marker",
     "infection_risk_factor", "ProBIOPSY Q62"),
    ("decompensated_diabetes", "Sub(de)compensated diabetes mellitus",
     "糖尿病控制不佳",
     "history_risk", "infection_risk_marker",
     "infection_risk_factor", "ProBIOPSY Q62"),
    # ---------------- treatment intent (Domain 3, stems 26-36) ----------------
    ("planned_focal_therapy", "Focal therapy candidate / planning",
     "局灶治疗",
     "treatment_intent", "contralateral_sbx_required",
     "intent_focal_therapy", "ProBIOPSY Q64-Q66"),
    ("planned_nerve_sparing", "Nerve-sparing surgical planning",
     "神经保留手术",
     "treatment_intent", "tbx_plbx_sufficient",
     "intent_nerve_sparing", "ProBIOPSY Q67-Q72"),
    ("planned_plnd", "Pelvic lymphadenectomy decision",
     "盆腔淋巴结清扫",
     "treatment_intent", "nomogram_dependent",
     "intent_plnd", "ProBIOPSY Q73-Q78"),
    ("planned_whole_gland_rt", "Whole-gland radiotherapy planning",
     "全腺体放疗",
     "treatment_intent", "tbx_plbx_sufficient",
     "intent_whole_gland_rt", "ProBIOPSY Q79-Q84"),
    ("planned_focal_boost_rt", "Focal radiotherapy boost planning",
     "局灶放疗加量",
     "treatment_intent", "tbx_plbx_sufficient",
     "intent_focal_boost", "ProBIOPSY Q85-Q90"),
    ("planned_adt_duration", "ADT duration planning (with radiotherapy)",
     "ADT疗程规划",
     "treatment_intent", "tbx_plbx_sufficient",
     "intent_adt_duration", "ProBIOPSY Q91-Q96"),
    # ---------------- resource availability ----------------
    ("psma_pet_available", "PSMA PET-CT available",
     "PSMA PET可及",
     "resource_availability", "ancillary_in_negative_mri",
     "psma_pet_available", "ProBIOPSY Q17-Q19"),
    ("microultrasound_available", "Prostate micro-ultrasound available",
     "微超声可及",
     "resource_availability", "not_endorsed_any_scenario",
     "microultrasound_available", "ProBIOPSY Q20-Q22"),
    ("ai_mri_software_available", "AI MRI reading software available",
     "AI辅助读片可及",
     "resource_availability", "radiologist_aid_endorsed",
     "ai_software_available", "ProBIOPSY Q26|PI-CAI"),
    ("contrast_mri_available", "Contrast-enhanced MRI sequence available",
     "增强MRI可及",
     "resource_availability", "indeterminate_pz_workup",
     "contrast_mri_available", "ProBIOPSY Q10a"),
    ("fusion_platform_available", "MRI-US software fusion platform available",
     "融合穿刺平台可及",
     "resource_availability", "tbx_execution_mode",
     "fusion_platform_available", "ProBIOPSY SM2 (fusion-type evidence)"),
]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        for row in ROWS:
            w.writerow(row)
    ids = [r[0] for r in ROWS]
    assert len(ids) == len(set(ids)), "duplicate entity_a ids"
    print(f"[ok] entities_a.csv written: {len(ROWS)} rows -> {OUT}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
