# IRB Protocol Summary — 前列安汇 (probiopsy-rag)

> **Purpose**: Summary application form submitted to [TODO: irb_committee_name]
> **Created**: 2026-09-13
> **Version**: v1.0
> **Companion docs**: Full narrative at [ETHICS.en.md](ETHICS.en.md) | [Data_Management_Plan.en.md](Data_Management_Plan.en.md)

---

## 1. Basic Information

| Field | Value |
|---|---|
| **Study Title** | 前列安汇: A rule-engine + knowledge-graph + LLM-arbiter decision support system for LightRAG混合决策支持系统:患者临床情境×穿刺决策项 screening |
| **Study Type** | Retrospective case series + literature evidence review |
| **PI** | [TODO: pi_name] ([TODO: pi_title]) |
| **PI Department** | [TODO: pi_department], [TODO: hospital_name] |
| **Contact** | Email: [TODO: pi_email] / Phone: [TODO: pi_phone] |
| **Co-investigators** | [TODO: coinvestigator_names] |
| **Funder** | [TODO: funding_source] |
| **Grant ID** | [TODO: funding_id] |
| **Duration** | 10 weeks |
| **Expected enrollment** | 0 (retrospective) |
| **Site** | [TODO: hospital_name] (single center) |

---

## 2. Background & Significance

### 2.1 Scientific Background

在前列腺穿刺活检决策中,规则引擎+LightRAG知识图谱+LLM仲裁混合系统能否依据ProBIOPSY国际共识与EAU指南,为特定患者临床情境生成规范化的穿刺决策建议?

### 2.2 Current State

- pending data availability (see [ETHICS.en.md](ETHICS.en.md) §1.2)
- Existing gap: No A×B matrix screening tool
- Contribution: First rule + KG + LLM three-layer architecture for LightRAG混合决策支持系统:患者临床情境×穿刺决策项

### 2.3 Clinical Significance

Provides adult_men_with_suspected_prostate_cancer with traceable, explainable risk grading for 患者临床情境要素 × 穿刺决策项.

---

## 3. Objectives

### 3.1 Primary

Build and validate 前列安汇, outputting explainable risk grading across all 50 患者临床情境要素 × 40 穿刺决策项 combinations.

### 3.2 Secondary

1. Compare 4 baselines (pure_llm / naive_rag / lightrag / full system)
2. Evaluate clinical effectiveness on 200 retrospective cases
3. Assess face validity via 4-expert blind review

---

## 4. Methods

### 4.1 Design

**Retrospective, single-center, model development and validation study.**

### 4.2 Data Sources

| # | Source | Type | Volume | Use |
|---|---|---|---|---|
| 1 | [TODO: hospital_name] EMR | Retrospective records | 0 | Phase 3 clinical validation |
| 2 | CTD / ToxCast / Prop 65 / ECHA / etc. | Public databases | See DMP | Model construction |
| 3 | PubMed E-utilities | Public literature | ~250 abstracts | Evidence base |

### 4.3 Inclusion Criteria (Retrospective)

- [ ] Treated at [TODO: hospital_name] between 20XX-XX-XX and 20XX-XX-XX
- [ ] Diagnosed with one of the 患者临床情境要素 (per WHO ICD-11 / ASRM)
- [ ] Exposure history documented in record (self-report or biomonitoring)
- [ ] Basic demographic data available

### 4.4 Exclusion Criteria

- [ ] Incomplete records (missing key outcomes)
- [ ] Patient opted out of research use (prospective opt-out)

### 4.5 Primary Analysis

- System output vs literature gold standard: sens / spec / F1 / Cohen's κ
- System output vs expert blind review: Fleiss κ + system agreement
- Multi-seed (≥5) × multi-baseline paired t-test, p < 0.05

### 4.6 Data Safety Monitoring

- **DSMB/DMC**: Not applicable (minimal risk, no intervention)
- **Data security**: See DMP §4

---

## 5. Human Subjects Protection

### 5.1 Risk Level

**Minimal Risk** (no greater than daily life risk)

### 5.2 Informed Consent

**Waiver requested**, per:
- 45 CFR 46.116(f) / China Ethical Review Measures Article 32
- Meets 4 waiver criteria (see [ETHICS.en.md](ETHICS.en.md) §7.1)

### 5.3 Privacy Protection

- HIPAA Safe Harbor de-identification (18 identifiers)
- Only de-identified data leaves hospital; PHI never transferred
- See [Data_Management_Plan.en.md](Data_Management_Plan.en.md) §3

### 5.4 Vulnerable Populations

Includes: mri_visible_lesion, mri_indeterminate, prior_negative_biopsy, anticoagulated, focal_therapy_candidate
Protections per [ETHICS.en.md](ETHICS.en.md) §5.

---

## 6. Data Management

See [Data_Management_Plan.en.md](Data_Management_Plan.en.md).

**Key Points**:
- Retention: 5 years post-study (destroy 20XX-XX-XX)
- Storage: 本地工作站(加密磁盘),仅使用公开数据
- Public sharing: De-identified dataset (Zenodo / OSF, DOI); PHI never public

---

## 7. AI / Algorithm-Specific

### 7.1 System Positioning

**Decision support system, not a diagnostic device**. Clinical judgment remains with physician.

### 7.2 LLM / AI Models Used

| Model | Use | Version Lock |
|---|---|---|
| `deepseek-v4-flash` | LightRAG knowledge graph construction | Locked |
| `doubao-embedding-vision-251215` | Vector indexing (dim=2048) | Locked |
| `gpt-4-turbo-2024-04-09` | Final report arbitration (~500 calls) | Locked |

### 7.3 AI-Specific Risks

- **Training data bias**: DeepSeek/GPT-4 favor English literature, may affect Chinese applicability
- **Mitigation**: Rule engine as "grounding"

### 7.4 Reporting Frameworks

- TRIPOD-AI (AI prediction models)
- DECIDE-AI (early AI clinical evaluation)

---

## 8. Conflict of Interest

- **Financial COI**: [TODO: coi_disclosure, 若无请写'无']
- **Non-financial COI**: [TODO: nonfinancial_coi]
- **Management**: Full disclosure in publications + presentations

---

## 9. Timeline

| Phase | Week | Activities | Ethics-related |
|---|---|---|---|
| IRB submission | 0 | Submit this application | **This step** |
| IRB review period | 1-3 | Await approval | — |
| System construction | 1-4 | Phase 0-2 (no clinical data) | — |
| Clinical data acquisition | 4 | **Post-IRB approval**, de-identified | Critical milestone |
| Model validation | 5-9 | Phase 3-5 | — |
| Writing | 9-11 | Phase 6-7 | TRIPOD-AI check |
| Submission | 12 | Phase 8 | Report IRB approval # |

---

## 10. PI Commitments

I commit to:
1. Conduct the study per this protocol; submit amendments for any changes
2. Record and report data truthfully and completely
3. Protect participant privacy and rights
4. Promptly report any adverse events or security incidents
5. Accept IRB oversight and continuing review
6. Submit closure report within 90 days of study completion

**PI signature**: ____________________  **Date**: ____________________

---

## 11. Appendices Checklist

- [ ] Full ETHICS narrative ([ETHICS.en.md](ETHICS.en.md))
- [ ] Data Management Plan ([Data_Management_Plan.en.md](Data_Management_Plan.en.md))
- [ ] Informed Consent Form template ([Informed_Consent.en.md](Informed_Consent.en.md), if applicable)
- [ ] PI CV
- [ ] Partner hospital credentials
- [ ] Data Use Agreement (DUA)
- [ ] Full protocol ([PLAN.md](../PLAN.md))
- [ ] AI/ML model documentation (TRIPOD-AI checklist)
