# 论文伦理声明（Manuscript Ethics Statement）— 前列安汇（probiopsy-rag）

> **文档用途**：投稿时直接复制到 manuscript 的 Declarations 节、Cover Letter、投稿系统各字段
> **创建日期**：2026-09-13
> **版本**：v1.0
> **配套文档**：[ETHICS.md](ETHICS.md) 完整叙述

---

## 1. Ethics Approval（伦理批准）

### 标准声明（填入 manuscript Declarations → Ethics）

> This study was approved by the Institutional Review Board of [TODO: hospital_name] ([TODO: irb_committee_name], approval no. [TODO: irb_approval_id]). The study was conducted in accordance with the Declaration of Helsinki (2013), the CIOMS International Ethical Guidelines for Health-related Research Involving Humans (2016), and the applicable Chinese regulations including the Measures for Ethical Review of Biomedical Research Involving Humans (2016) and the Personal Information Protection Law (PIPL, 2021).

### 中文版（如需中文期刊）

> 本研究获得 [TODO: hospital_name] 伦理委员会批准（[TODO: irb_committee_name]，批件号 [TODO: irb_approval_id]）。研究遵循《赫尔辛基宣言》（2013 版）、《CIOMS 涉及人的健康相关研究国际伦理准则》（2016 版），以及中国《涉及人的生物医学研究伦理审查办法》（2016）和《个人信息保护法》（PIPL，2021）等适用法规。

---

## 2. Informed Consent（知情同意）

### 回顾性研究（HuanYu 默认 — 申请豁免）

> Given the retrospective nature of this study using de-identified electronic medical records, the requirement for informed consent was waived by the IRB of [TODO: hospital_name] under [TODO: waiver_citation, e.g., 45 CFR 46.116(f) / 《伦理审查办法》第 32 条]. All data were de-identified prior to analysis in accordance with the HIPAA Safe Harbor standard.

### 前瞻性研究（如有）

> Written informed consent was obtained from all individual participants included in the study. The consent process is documented per institutional policy and the consent forms are retained by the PI for a minimum of 5 years following study completion.

---

## 3. Data Availability（数据可用性）

> The code supporting this study is available at https://github.com/[TODO: github_org]/probiopsy-rag under the MIT license (archived DOI: [TODO: zenodo_doi]). De-identified clinical data will be available upon reasonable request to the corresponding author, subject to a Data Use Agreement and approval by the institutional review board. Public data sources (CTD, ToxCast/Tox21, California Prop 65, ECHA SVHC, ATSDR, DisGeNET, KEGG, Reactome, NHANES, FDA DailyMed, IARC Monographs, NTP Reports) are accessible via their respective APIs under the licenses noted in Supplementary Table S1. LLM call logs are retained for 5 years per AI transparency policy and are not publicly available.

---

## 4. Conflict of Interest（利益冲突）

### 标准声明

> The authors declare that they have no conflict of interest.

### 详细披露（如有 COI）

> [TODO: pi_name] reports [TODO: coi_description]. All other authors declare no conflict of interest.

### LLM 提供商关系

> DeepSeek (Hangzhou), Volcengine Ark (ByteDance), and OpenAI are third-party API providers. None of the authors have financial relationships with these providers. The providers did not influence study design, data analysis, or manuscript preparation.

---

## 5. Funding（资助）

> This work was supported by [TODO: funding_source] (grant no. [TODO: funding_id]). The funders had no role in study design, data collection and analysis, decision to publish, or preparation of the manuscript.

---

## 6. CRediT Author Contributions

按 CRediT (Contributor Roles Taxonomy) 分类：

| Author | Roles |
|---|---|
| **[TODO: pi_name]** | Conceptualization, Methodology, Software, Writing – Original Draft, Supervision, Funding acquisition |
| **[TODO: coauthor_1_name]** | Data curation, Investigation, Writing – Review & Editing |
| **[TODO: coauthor_2_name]** | Validation, Formal analysis, Visualization |
| **[TODO: expert_reviewer_1_name]** | Investigation (expert review), Writing – Review & Editing |
| **[TODO: expert_reviewer_2_name]** | Investigation (expert review), Writing – Review & Editing |
| **[TODO: expert_reviewer_3_name]** | Investigation (expert review) |
| **[TODO: expert_reviewer_4_name]** | Investigation (expert review) |

**CRediT role definitions**（参考）：
- Conceptualization / Methodology / Software / Validation / Formal analysis / Investigation / Resources / Data curation / Writing – Original Draft / Writing – Review & Editing / Visualization / Supervision / Project administration / Funding acquisition

---

## 7. AI / LLM Use Disclosure

依 ICJME 2023 / 《Nature》2023 AI 使用政策：

### During research（研究阶段）

> Large Language Models (LLMs) were used in this study as follows: (1) DeepSeek `deepseek-v4-flash` was used for biomedical entity extraction and knowledge graph construction via LightRAG; (2) Volcengine Ark `doubao-embedding-vision-251215` was used for embedding-based vector indexing; (3) OpenAI `gpt-4-turbo-2024-04-09` was used for final report arbitration on the top-10% high-risk A×B pairs (~500 calls). All LLM calls are logged with input/output/timestamp/model_version and retained for 5 years.

### During manuscript writing（写作阶段）

依 ICJME 2023 指南：

> [TODO: ai_writing_use — 如使用了 LLM 协助写作，必须披露。如：During preparation of this manuscript, the authors used [model name and version] for [purpose, e.g., language editing]. The authors reviewed and edited all LLM-generated content and take full responsibility for the content of the published article.]
>
> **如未使用 LLM 协助写作**：则省略此段。

---

## 8. TRIPOD-AI Compliance（AI 报告框架）

本研究遵循 TRIPOD+AI（2024）报告规范。完成的 checklist 见 **Supplementary Table S2**。

关键合规点：
- [x] 研究问题与 AI 系统定位（章节 1-2）
- [x] 数据来源与样本（章节 3-5）
- [x] 模型构建细节（章节 6-9）
- [x] 性能评估（章节 10-13）
- [x] 模型版本锁定（`deepseek-v4-flash`, `gpt-4-turbo-2024-04-09`）
- [x] 不确定性量化（5-seed 多次重复）
- [x] 局限性与外推性（章节 14-15）

---

## 9. Limitations（与伦理相关部分）

> This study has several ethical and methodological limitations. First, clinical validation was performed using retrospective data only; no prospective validation was conducted. Second, the AI models used (DeepSeek, GPT-4-Turbo) were trained primarily on English-language and Western-centric medical literature, which may introduce bias when applied to Chinese clinical contexts. Third, the four-expert panel, while methodologically appropriate for face validity assessment, provides limited geographic and institutional diversity. Fourth, public external validation cohorts (UK Biobank) were not accessible due to authorization constraints; sensitivity analysis was limited to NHANES exposure distributions. Finally, the rule-based engine, while interpretable, encodes domain assumptions that may not generalize to all clinical scenarios.

---

## 10. Acknowledgements（致谢）

> The authors thank the IRB of [TODO: hospital_name] for ethical review, the clinical team led by [TODO: clinical_lead] for patient record review, and the four expert reviewers ([TODO: expert_reviewer_1_name], [TODO: expert_reviewer_2_name], [TODO: expert_reviewer_3_name], [TODO: expert_reviewer_4_name]) for blind evaluation. We also acknowledge the Comparative Toxicogenomics Database (CTD), EPA ToxCast program, and other public data providers (see Supplementary Table S1) whose open data made this research possible.

---

## 11. Author ORCID

| Author | ORCID |
|---|---|
| [TODO: pi_name] | [TODO: pi_orcid] |
| [TODO: coauthor_1_name] | [TODO: coauthor_1_orcid] |
| ... | ... |

---

## 12. Submission Cover Letter Template

```
Dear Editor,

We submit our manuscript entitled "[title]" for consideration by [journal name].

In this work, we introduce 前列安汇, the first-of-kind A×B matrix screening system that integrates a rule engine, knowledge graph retrieval, and LLM arbitration to evaluate 患者临床情境要素 × 穿刺决策项 interactions. We validated the system across 4 methodological phases (rule consistency, literature gold-standard, 200 retrospective clinical cases, and 4-expert blind review).

Why this fits [journal name]:
- The study addresses a critical gap in LightRAG混合决策支持系统:患者临床情境×穿刺决策项 screening
- Methodologically rigorous (TRIPOD-AI compliant, 5-seed multi-baseline comparison)
- Aligned with the journal's recent interests in AI/ML for prostate cancer diagnosis and biopsy standardization

Declarations:
- Ethics: Approved by IRB of [TODO: hospital_name] (approval no. [TODO: irb_approval_id])
- All authors have read and approved the manuscript
- No conflict of interest to declare
- Code available at https://github.com/[TODO: github_org]/probiopsy-rag

We confirm that this manuscript has not been published and is not under consideration elsewhere. We thank you for your time and look forward to your response.

Sincerely,
[TODO: pi_name]
[TODO: pi_title]
[TODO: pi_email]
```

---

## 13. Quick-Fill Reference

| Field | Value |
|---|---|
| Study title | 前列安汇：基于规则引擎、知识图谱与 LLM 仲裁的 LightRAG混合决策支持系统:患者临床情境×穿刺决策项 筛查决策支持系统 |
| Keywords | 患者临床情境要素, 穿刺决策项, knowledge graph, LLM arbiter, decision support, 患者临床情境要素 screening |
| Article type | Research Article |
| Target journal | European Urology Open Science |
| Manuscript word count | [TODO: word_count] |
| Figures | 5 (per Phase 5 plan) |
| Tables | 4 (registry / rules / performance / validation distribution) |
| Supplementary | Checklist (TRIPOD-AI) + data sources + extended results |
