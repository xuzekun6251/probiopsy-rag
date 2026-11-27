# QianLieAnHui: development and benchmark validation of a hybrid rule-engine, knowledge-graph, and large language model arbitration decision-support agent for the prostate biopsy pathway, against the ProBIOPSY international consensus

**Running title:** A hybrid rule engine–knowledge graph–LLM agent for prostate biopsy decisions

XU Zekun<sup>1,\*</sup>

<sup>1</sup> Department of Urology, Affiliated Jinhua Hospital, Zhejiang University School of Medicine.

<sup>\*</sup> Corresponding author: xuzekunurology@163.com

**Keywords:** prostate cancer; prostate biopsy; clinical decision support; large language model; knowledge graph; retrieval-augmented generation

**Word count:** abstract 249 / main text 3,987 (Introduction–Conclusions, excl. tables, captions, legends, references, declarations)

> 2026-11-28 (JAMIA version): derived from manuscript.en.md for submission to JAMIA (Research and Applications) — abstract restructured to the JAMIA five-section format (Objective / Materials and Methods / Results / Discussion / Conclusion, ≤250 words); BMJ-specific elements removed (What this study adds / How this study might affect research, practice or policy / Patient and public involvement); main text compressed to within the 4,000-word limit per the JAMIA instructions (Acknowledgments and References excluded); title abbreviation expanded ("LLM-arbitration" → "large language model arbitration"); keywords trimmed to six; Table 4 body added from outputs/tables/table4_validation.md (previously caption-only); supplementary cross-references completed (S2, S5). All benchmark numbers, all 58 references, the action-space terminology scheme, and Figures 1–5 retained unchanged.

---

## Abstract

**Objective:** To evaluate whether chaining deterministic rules, knowledge-graph retrieval, and large language model (LLM) arbitration can turn the written ProBIOPSY consensus into an executable, auditable decision-support agent for prostate biopsy.

**Materials and Methods:** Four configurations answered the 112 ProBIOPSY consensus statements across five seeds under one generator (2,240 runs): a pure LLM, naive retrieval-augmented generation (RAG), GraphRAG-only retrieval, and the full agent QianLieAnHui, chaining a deterministic rule engine (16 hard-constraint rules), risk-guided retrieval over a GraphRAG knowledge graph, and an LLM arbiter emitting one of five consensus-semantic actions with statement-level citations. Baselines were repeated with a flagship generator, the arbiter with five-way self-consistency voting; all 560 evidence packs were reconstructed to localise residual errors.

**Results:** Exact-5 accuracy 0.805 ± 0.012 (agent) versus 0.613 (GraphRAG-only), 0.605 (naive RAG), 0.304 (pure LLM); κ 0.730 ± 0.016 versus 0.525 / 0.512 / 0.079 (all FDR-corrected p ≤ 8.9 × 10⁻⁴). Against-class F1 reached 0.908 at specificity 0.986. Retrieval baselines collapsed onto frequent classes (conditional endorsement in 0.8% of runs versus 17.0%); a flagship generator deepened the collapse (naive RAG 0.605 → 0.538) and self-consistency voting lowered exact-5 to 0.777. Retrieval coverage was saturated; all 109 residual misclassifications were arbitration-layer.

**Discussion:** Retrieval augmentation alone cannot express conditional, guideline-qualified commitments; fine-grained action competence must be built into the architecture, and coarse metrics overestimate unconstrained medical RAG systems.

**Conclusion:** A written international consensus can be operationalised into an auditable decision-support agent ready for pilot evaluation; deployment requires arbiter-layer calibration, versioned guideline corpora, and governance integration.

---

## Introduction

Prostate cancer is among the most common malignancies in men [1,2]. Population-level prostate-specific antigen (PSA) screening lowers disease-specific mortality [3], and the biopsy — gateway to every treatment decision — determines whether a man is monitored, offered focal therapy, or scheduled for radical treatment. Its contemporary goal is to raise clinically significant cancer detection while reducing complications and avoiding over-biopsy. Yet the pathway's decision points are still actively debated: whether systematic cores should be added to magnetic resonance imaging (MRI)-targeted cores [4], which sampling scheme is sufficient in the era of MRI targeting [5], transperineal versus transrectal access [6,7], and targeted versus empirical prophylaxis [8]. MRI-targeted sampling improves clinically significant cancer detection [9-12], but biopsy-to-prostatectomy grade discordance complicates downstream planning [13]. The measurements that drive these choices are themselves imperfect: multiparametric MRI (mpMRI) misses clinically significant cancer in a minority of men [14], Prostate Imaging Reporting and Data System (PI-RADS) readings agree only moderately between readers [15,16], image quality gates their interpretation [17], and PSA-density thresholds temper but do not settle it [18].

The ProBIOPSY international consensus documented substantial practice variation across exactly these choices [21]. The European Association of Urology (EAU) Prostate Cancer Guidelines [22], the American Urological Association (AUA)/American Society for Radiation Oncology (ASTRO) guideline [23] with its 2026 Amendment [24], and the consensus itself converge on the same decision points — yet a guideline is reference material, not an instrument: at the decision point the clinician must assemble 51 scenario archetypes against 54 biopsy decisions, and no lookup table covers that combinatorics. Large language models (LLMs) supply linguistic flexibility [27,28] and approach expert performance on medical question answering [29,30], and specialised agents exist for atrial fibrillation [25], hypertension [31], prostate-cancer education [26], dietetics [32], and gene-set analysis [33]. Their limitations translate into clinical risk: hallucination without verifiable provenance [34], guideline drift [35], and confidently generic advice where patient-specific context changes the answer — asked whether a man with suspected locally advanced disease should undergo extended systematic biopsy, a general-purpose LLM recites the 12-core template, while the consensus recommends reducing it to six or fewer, since curative treatment is no longer the goal [21].

Retrieval-augmented generation (RAG) grounds generation in an external corpus [36], and medical RAG benchmarks show promise [37]: in guideline-based chronic kidney disease question answering, clinician-rated correctness rose from 70.8% (plain LLM) to 76.6% (RAG) and 75.6% (GraphRAG), yet on a question outside the corpus both retrieval systems collapsed to 0.28 and 0.10 [38]. Retrieval alone cannot forbid a fluent recommendation that contradicts the guideline; rule-based clinical decision support is deterministic but slow to update [39], breeds alert fatigue [40], and cannot digest natural-language evidence [41]. What is needed combines the linguistic flexibility of LLMs, the traceable evidence chain of knowledge-graph retrieval, and the deterministic safety of hard constraints, each covering the others' failure modes [42].

We developed QianLieAnHui (前列安汇; "probiopsy-rag"), a decision-support agent that turns the written consensus into an executable checklist: a rule engine mechanically forbids consensus-contradicting output; a dual retrieval layer (GraphRAG knowledge graph plus deterministic lexical index) makes every recommendation traceable to numbered evidence; and an LLM arbiter, bound by hard constraints, emits one of five actions with statement-level citations. Reporting follows the TRIPOD+AI [43] and DECIDE-AI [44] items applicable to decision-support benchmarks. We assess, statement by statement against the 112 final statements, how much consensus conformance the architecture achieves, which layer carries the performance, and where residual errors arise. Three contributions distinguish this work: (1) the consensus's final statements become an executable gold standard — 2,240 runs across four architectures and five seeds, the action space bound to consensus voting semantics; (2) the deterministic lexical layer allows every run to be decomposed into retrieval and arbitration contributions, locating all 109 residual misclassifications; and (3) the same frozen evidence chain supports source-traceable lay-language patient education. Rather than a novel architecture, QianLieAnHui assembles off-the-shelf components under architecture-level principles — the configuration most likely to be adopted without specialist natural-language-processing expertise.

## Methods

### Study design and ethics

This is a system-development and benchmark-validation study involving no patient data or biological samples: the corpus derives solely from the published consensus and its supplementary material, the gold standard is its 112 published final statements, and demonstration cases are synthetic vignettes. A four-expert blinded face-validity review (anonymous, voluntary; synthetic cases only) required no institutional review board approval; the assessment is documented during project planning.

### Validation set: 112 ProBIOPSY final statements

All 112 final statements [21] served as the gold standard. Each statement was mapped to an expected system action in a pre-defined five-class taxonomy: **endorse** (support as stated), **equivalent-option endorsement** (`endorse_option`; support as one of several acceptable options), **conditional** (support under specified conditions), **optional-pathway reporting** (`report_option`; present as an available pathway without active recommendation), and **against** (recommend against). The gold-standard action distribution is endorse 190, conditional 185, against 125, equivalent-option endorsement 35, and optional-pathway reporting 25. Statements span three domains: indication (n = 23), procedure (n = 34), and treatment planning (n = 55, anchored by International Society of Urological Pathology (ISUP) grade-group–driven treatment decisions [45]); 25 statements (22.3%) are against-class. The five demonstration vignettes (Results) are synthetic cases on the same registries, not part of the evaluation set.

### System architecture

The input is a pair (patient clinical scenario × biopsy decision item); the output is a structured verdict: one of five actions, a confidence value, triggered rules, and citations to numbered consensus statements and evidence chunks (Figure 1).

**Input layer: dual registries.** Entity A (patient scenarios) contains 51 archetypes with 49 distinct flags across imaging (PI-RADS grade, mpMRI and biparametric MRI (bpMRI), field strength, MRI quality (PI-QUAL) score [17]), laboratory markers (PSA, PSA density), history and risk, treatment intent, and resource availability; Entity B (decision items) contains 54 items with 20 flags (Table 1).

**Table 1.** Dual entity registries: item and flag counts with category breakdown. The full registries are released as `data/seed/entities_a.csv` and `data/seed/entities_b.csv`; category names follow the category keys of the released files.

| Registry | Items | Unique flags | Category breakdown | Source file |
|---|---|---|---|---|
| A — patient scenarios | 51 | 49 | imaging 17; laboratory biomarkers 9; clinical 7; history/risk 6; treatment intent 6; resource availability 5; demographic 1 | data/seed/entities_a.csv |
| B — decision items | 54 | 20 | indication 22; procedure 22; treatment planning 10 | data/seed/entities_b.csv |

**Layer 1: deterministic rule engine.** The rule base (YAML) holds 16 rules — 12 consensus rules and 4 patient-factor escalation rules (Table 2). Each rule specifies trigger flag combinations (Entity A × Entity B flags), severity, mechanism category, and recommended action. Matching is fully deterministic and produces hard constraints for downstream layers, each carrying ProBIOPSY statement numbers (Q-codes) for provenance. Patient-factor rules escalate consensus rules in context (e.g., infection risk factors → transperineal route or augmented prophylaxis).

**Table 2.** The 16-rule base: 12 consensus rules and 4 patient-factor escalation rules. Trigger-flag counts are per rule set; full trigger definitions, recommended actions, and Q-code citations are released in `configs/rules.yaml`, whose `rule_id` keys match the rule names below in lowercase snake case.

| Rule | Set | Severity | Mechanism | Trigger flags (A) | Target flags (B) | Rationale (first sentence) |
|---|---|---|---|---|---|---|
| MRI acquisition quality pathway | consensus | high | imaging pathway | 5 | 5 | Every prostate MRI must be checked against PI-QUAL v2 quality criteria before the biopsy pathway is decided (Q4a median 9, Q4b median 8 — consensus agree); a quality-assured scan — 1.5T or 3T, biparametric without routine contrast-enhanced sequences — is acceptable (Q1, Q5-Q7 median 8), and MRI that fails quality standards must not gate the biopsy decision. |
| Indeterminate lesion: ancillary workup | consensus | medium | ancillary workup | 8 | 10 | For an indeterminate lesion (PI-RADS 3), ProBIOPSY endorses PSAD as the primary gate to reduce unnecessary biopsies — for bpMRI (Q11 median 7) and even more strongly for mpMRI (Q14 median 8) — whereas PSMA PET and microultrasound remain conditional options rather than standard workup (Q18, Q21). |
| Negative MRI with high clinical suspicion | consensus | high | imaging pathway | 7 | 4 | When MRI is negative but clinical suspicion remains high (abnormal DRE, persistently elevated PSA, strong family history, Black ethnicity, or prior negative biopsy), a 12-core systematic biopsy is still endorsed (Q25 median 7 — consensus agree; Q55a median 7) and PSMA PET may serve as an ancillary test (Q19 median 8 — consensus agree). |
| Upfront new-imaging rejection | consensus | high | imaging pathway | 3 | 2 | ProBIOPSY explicitly rejects PSMA PET/MRI as an upfront first-line biopsy-decision tool (Q17 median 2 — consensus disagree) and microultrasound as an upfront alternative to prostate MRI (Q20 median 2 — consensus disagree); both modalities have defined ancillary niches but must not replace quality-assured MRI at triage. |
| AI MRI lesion-detection aid | consensus | low | AI decision support | 4 | 1 | ProBIOPSY endorses AI software as an aid to MRI lesion detection and characterization, with interpretation remaining the radiologist's responsibility (Q26 median 7 — consensus agree). |
| Advanced disease: reduced systematic scheme | consensus | high | scheme selection | 4 | 2 | ProBIOPSY endorses a reduced (6-core) systematic scheme in advanced disease, where detection of any grade group confirms management rather than changing mapping precision (Q57 median 8 — consensus agree). |
| Systematic template selection | consensus | medium | scheme selection | 4 | 4 | ProBIOPSY endorses the 12-core systematic template as the standard when systematic cores are indicated (Q52 median 8 — consensus agree) and rejects the classical 6-core sextant template (Q51 median 3), the Ginsburg 4-6 core template (Q53 median 3) and saturation biopsy (Q54 median 2) — all by consensus disagree. |
| Targeted core-count adaptation | consensus | low | targeted biopsy | 5 | 2 | ProBIOPSY reached no consensus on a fixed targeted-core count: adapting the number of targeted cores to PI-RADS score was rated 'neither' (Q34 median 6) and the proposed minimum of 3 cores per target failed to reach consensus in both rounds (Q35, Q36), so the system reports core count as an open option rather than enforcing a fixed number. |
| Perilesional biopsy technique | consensus | low | targeted biopsy | 5 | 5 | ProBIOPSY adopts the term 'perilesional biopsy' for cores placed just outside the MRI lesion margin (Q37a — SOQ consensus), requires targeted cores to be placed within 10 mm of the lesion (Q38 — SOQ consensus) and scales the number of perilesional cores to lesion size (Q39 median 7 — consensus agree), with a maximum of 2 cores per large lesion (Q41 — SOQ consensus). |
| Biopsy scheme by lesion distribution | consensus | medium | scheme selection | 5 | 5 | For a unifocal lesion, ProBIOPSY endorses targeted + perilesional biopsy without contralateral systematic cores (Q43 median 7 — consensus agree) and bilateral targeted+perilesional schemes for multifocal bilateral disease (Q49 median 7 — consensus agree), while adding full systematic biopsy to a targeted+perilesional scheme is rejected (Q45 median 3 — consensus disagree). |
| Route, anaesthesia and prophylaxis | consensus | high | perioperative | 4 | 5 | ProBIOPSY endorses the transperineal route as the standard for prostate biopsy (Q58 — SOQ consensus) with periprostatic nerve block for both transrectal (Q59) and transperineal (Q60) approaches (both SOQ consensus). |
| Treatment-planning tissue requirements | consensus | high | treatment planning | 6 | 10 | ProBIOPSY links biopsy scheme to downstream treatment intent: for focal therapy, targeted+perilesional alone is deemed insufficient and contralateral systematic biopsy must be added (Q65 median 7 — consensus agree), whereas nerve sparing, whole-gland radiotherapy, focal boost and ADT-duration planning are adequately served by targeted+perilesional schemes (Q67, Q70, Q79, Q85, Q88, Q91, Q94 median 7-8). |
| Immunocompromised or infection history | patient factor | high |  | 1 | 2 | Infection risk factors (Q62 catalogue: immunosuppression, prior prostatitis, recent instrumentation, MRSA colonization) escalate the perioperative rule R11 — prefer the transperineal route and augmented prophylaxis when transrectal access is unavoidable. |
| Unfit for curative treatment | patient factor | medium |  | 2 | 1 | Patients unfit for curative treatment shift the goal from mapping precision to confirmation — R06 reduced systematic scheme applies. |
| Repeat-biopsy setting | patient factor | medium |  | 1 | 2 | Prior negative biopsy with persisting suspicion raises sepsis risk on repeat access and keeps the 12-core template relevant (R03/R11 escalation). |
| Suspicious DRE without MRI lesion | patient factor | medium |  | 1 | 1 | Abnormal DRE with negative MRI keeps clinical suspicion high — systematic 12-core biopsy per R03. |

**Layer 2: risk-guided GraphRAG retrieval.** The corpus comprises 357 evidence chunks, all from the consensus and its supplementary material: the 112 final statements (level B), 20 narrative passages, 7 systematic-review summaries, and 218 literature entries (level C). The GraphRAG index was built with LightRAG [46] (lightrag-hku 1.5.7), with GLM-5.3-Flash extraction and a 2,048-dimension doubao embedding model; the index contains 1,864 entities and 3,078 relations. The full system performs risk-guided retrieval: rule matches and active decision items drive entity-boosted hybrid queries in context-only mode, and graph context is fused with lexical evidence (BM25-style scoring with boosts) before arbitration.

**Layer 3: LLM arbitration.** The arbiter receives scenario flags, decision items, rule matches with hard constraints, and both evidence streams, and outputs a structured verdict: one of five actions, confidence, a rationale, and citations. Rule-layer hard constraints bind the arbiter: when a hard constraint determines the outcome, the arbiter may not contradict it. Arbitration used Zhipu GLM-5.3 via an OpenAI-compatible application programming interface (API); the arbitration prompt and action definitions are in Supplementary S5. On unparseable or failed output the system degrades to the rule-layer conclusion and flags the record — failures are never silent.

**Alignment with external guidelines.** The rule base was cross-checked against the EAU Prostate Cancer Guidelines [22] and the AUA/ASTRO guideline [23] with its 2026 Amendment [24]; all 16 rules are consistent at the action level. External guideline text was deliberately excluded from the retrieval corpus to keep the evaluation controlled; guideline recommendations enter through the rule layer's cross-check, not retrieval.

**Patient-facing education mode.** The same frozen evidence chain supports a patient-facing education mode: (i) retrieval over the 357-chunk corpus and knowledge graph; (ii) a curated ten-entry fact base, every entry source-traceable (the consensus [21], the EAU and AUA/ASTRO guidelines [22,23], the TRANSLATE trial [6], the complication review [47], and peer-reviewed accounts of isolated high-grade prostatic intraepithelial neoplasia (HGPIN) [48] and atypical small acinar proliferation (ASAP) management [49]); and (iii) a generation prompt enforcing lay language, no invented statistics, an explicit safety-netting paragraph, and referral to the treating clinician. The mode issues no action verdict and is demonstrated qualitatively in Results.

### Baseline methods

1. **Pure LLM** (`pure_llm`) — question answered directly by the LLM with no retrieval and no rules;
2. **Naive RAG** (`naive_rag`) — BM25-style lexical retrieval of top-6 chunks (mean 3,644 characters) inserted into the prompt;
3. **GraphRAG-only** — end-to-end GraphRAG hybrid-mode question answering (mean 2,468 characters), no rule guidance, no hard constraints.

The full system uses a mean of 7,640 characters (graph + lexical).

### Benchmark protocol

Four methods × five seeds (0–4; temperature 0.2) × 112 statements = **2,240 runs**. **The generator was held fixed at GLM-5.3-Flash for all methods and seeds**, so inter-method differences are attributable to architecture rather than model capability. All 2,240 runs completed with zero errors and zero degraded records. In supplements, pure LLM and naive RAG were re-run in full with the flagship GLM-5.3 tier (1,120 records), and the arbiter was sampled five times per statement at temperature 0.7 with plurality voting (560 calls; all raw votes logged).

### Expert blinded review

The five demonstration cases were rated by an independent four-expert panel (two urological surgeons, one radiologist, one radiation oncologist; none involved in development). In a blinded first pass, experts selected their own five-class action for each composite proposition; the verdict was then revealed and experts rated four Likert dimensions (clarity, usefulness, recommendation, evidence; 1–5). Pre-registered rules: expert majority = modal rating; 2:2 splits excluded from the system-versus-majority κ; all agreement statistics interpreted as preliminary. The questionnaire and expert comments are in Supplementary S6.

### Metrics

Exact-5-class accuracy (primary), exact-3 accuracy (collapsing equivalent-option endorsement into endorse and optional-pathway reporting into conditional, exposing majority-class inflation), five-class macro-F1, Cohen's κ [50], and binary against-class sensitivity/specificity/F1; mean ± standard deviation (SD) over the five seeds. Method differences were assessed with two-sided paired t-tests across seeds (six comparisons) with Benjamini–Hochberg false-discovery-rate (FDR) correction [51].

### Implementation and reproducibility

Implemented in Python 3.13 on lightrag-hku 1.5.7; the rule base, registries, evidence corpus, gold-standard annotations, all 2,240 raw predictions, and evaluation scripts are released with the code; the rule file's SHA-256 is recorded at index build (`index_built_against_rules_sha256`) and verified live to prevent silent index–rules divergence.

## Results

### Benchmark overview and headline performance (Table 3, Figure 2)

Four configurations answered the same 112 statements under one generator (2,240 runs, zero errors, zero degraded records). The full system leads every fine-grained metric (Table 3; Figure 2): exact-5 accuracy 0.805 ± 0.012, +19.2 points over the strongest baseline GraphRAG-only (0.613), naive RAG 0.605, pure LLM 0.304; κ 0.730 ± 0.016 versus 0.525 / 0.512 / 0.079. All six paired seed-level comparisons remain significant after FDR correction (paired t(4) = 8.9–25.3, adjusted p ≤ 8.9 × 10⁻⁴), and seed-to-seed variation was small (SD 0.012).

**Table 3.** Benchmark performance matrix: mean ± SD over five seeds (560 runs per method; 2,240 total). Context = mean retrieved characters per run.

| Method | exact-5 | exact-3 | macro-F1 | Cohen's κ | against sens. | against spec. | against-F1 | Mean context (chars) |
|---|---|---|---|---|---|---|---|---|
| GraphRAG-only | 0.613±0.013 | 0.920±0.013 | 0.536±0.012 | 0.525±0.012 | 1.000±0.000 | 0.922±0.017 | 0.881±0.023 | 2468 |
| naive RAG | 0.605±0.033 | 0.905±0.013 | 0.514±0.043 | 0.512±0.041 | 0.992±0.018 | 0.931±0.021 | 0.890±0.028 | 3644 |
| Full agent (QianLieAnHui) | 0.805±0.012 | 0.823±0.012 | 0.825±0.022 | 0.730±0.016 | 0.872±0.018 | 0.986±0.010 | 0.908±0.023 | 7640 |
| pure LLM | 0.304±0.039 | 0.370±0.029 | 0.254±0.029 | 0.079±0.053 | 0.416±0.083 | 0.720±0.021 | 0.346±0.053 | 0 |

### Retrieval baselines collapse onto frequent classes (Figure 2C)

Both RAG baselines scored exact-3 of 0.920 / 0.905 — nominally above the full system's 0.823 — yet their exact-5 (~0.61) and macro-F1 (~0.52) reveal collapse onto the three frequent classes. The clearest signature is conditional endorsement: GraphRAG-only emitted it in 3 of 560 runs and naive RAG in 6 (0.8% combined) versus 95 of 560 (17.0%) for the full system — in the right places, lifting κ from ~0.52 to 0.730 (Figure 2C). Pure LLM produced conditional and equivalent-option endorsement often enough (14 and 90 of 560) but almost never correctly (κ 0.079).

Against is the safety-critical class (22.3% of the gold standard). The full system traded modest sensitivity (0.872) for near-zero false vetoes (against-F1 0.908 ± 0.023, specificity 0.986 ± 0.010), whereas the retrieval baselines matched or exceeded its sensitivity (1.000 / 0.992) with specificity of only 0.922 / 0.931, and pure LLM was low on both counts (F1 0.346) — the trade follows from the hard constraint that a veto must be evidence-backed.

### Residual errors: arbitration, not retrieval

The aggregated confusion matrix (Supplementary Table S1) shows near-perfect endorsement (190/190) but conditional recall of 95/185 (0.51) with 74 gold-conditional statements predicted endorse — an over-permissive skew, most pronounced in treatment planning. To locate the responsible layer, we reconstructed offline, for all 560 full-system runs, the exact evidence pack the arbiter saw (the lexical layer's scoring is deterministic): all packs contained item-linked evidence (100% coverage; no corpus gap), so all 109 residual misclassifications are arbitration errors. A stricter criterion — the gold statement's own chunk (by Q-code) in the pack — was met in 385 of 560 runs (68.8%); 66 of the 109 errors occurred with the gold chunk already in the pack (including all 16 against→endorse and all 10 conditional→optional-pathway-reporting transitions); 77 of 109 sit in treatment planning. With retrieval saturated, the residual conditional weakness is an arbitration-layer calibration problem; the per-run decomposition is released with the repository.

### Generator tier does not rescue baseline architectures (Supplementary S2)

Re-running pure LLM and naive RAG with the flagship GLM-5.3 tier (1,120 runs) left the numbers worse: naive RAG exact-5 fell 0.605 → 0.538 ± 0.012 (κ 0.450), pure LLM stayed at 0.288 ± 0.013 (κ 0.132). Without the rule layer's class signals and hard constraints, flagship models collapse onto majority classes as flash-tier ones do — architecture, not generator selection, is the differentiator.

### Self-consistency voting does not substitute for architectural class priors

In a self-consistency ablation (identical to the full system except five arbiter samples at temperature 0.7 combined by plurality vote), votes were highly consistent — 106/112 statements drew five unanimous votes (degraded votes 9/560) — so the degradation is systematic: exact-5 fell to 0.777 (95% confidence interval (CI) 0.696–0.857) versus 0.805, κ to 0.690, conditional recall from 0.514 to 0.432, with three endorse votes outvoting the correct class on gold-conditional Q64; against-specificity rose to 1.000 (no false veto in 560 votes). Majority voting reproduces and magnifies whatever preference the single call already expresses; it cannot supply a class prior the architecture lacks.

### Domain breakdown (Table 4)

Against-class density varies sharply by domain (Table 4: indication 8.7%, procedure 14.7%, treatment planning 32.7%); the full system retains its advantage in the against-densest domain (per-domain matrices in Supplementary Table S1).

**Table 4.** Gold-standard domain × action distribution across the 112 final statements (statement counts; the run-level distribution reported in the text multiplies each cell by five seeds).

| Domain | Statements | Endorse | Equivalent-option endorsement | Conditional | Optional-pathway reporting | Against | Against (%) |
|---|---|---|---|---|---|---|---|
| Indication | 23 | 14 | 0 | 6 | 1 | 2 | 8.7 |
| Procedure | 34 | 6 | 7 | 12 | 4 | 5 | 14.7 |
| Treatment planning | 55 | 18 | 0 | 19 | 0 | 18 | 32.7 |
| All | 112 | 38 | 7 | 37 | 5 | 25 | 22.3 |

### Demonstration cases and patient-facing education (Figures 4, 5)

Five synthetic vignettes — unifocal scheme, upfront prostate-specific membrane antigen (PSMA) positron emission tomography (PET), indeterminate bpMRI lesions, advanced disease, infection-risk escalation — ran end-to-end, each producing the correct five-class action, the expected rules including escalations, and a citation chain traceable to Q-codes and evidence chunks (Supplementary S3). Three daily consultations were submitted to the education mode in Chinese (transcripts in Supplementary S7): asked whether a benign biopsy report ends follow-up, the agent answered that a biopsy samples only the cores taken, small tumours can be missed, and PSA testing should continue, closing with a safety-netting paragraph; asked what ASAP means, it distinguished ASAP from isolated HGPIN and advised against delaying the repeat biopsy [49]; asked whether fear of pain justifies declining, it described periprostatic nerve block [6,21] and warned that avoidance can delay a curable diagnosis. All outputs cited their fact entries, referred the patient to the treating clinician, and invented no numbers; these are demonstrations, not benchmarked results.

### Face validity: four-expert blinded review (Figure 3)

Raw inter-expert agreement was 17/20 ratings (modal share 4/4 ×3, 3/4 ×1, one 2:2 split; Figure 3A); the overall Fleiss κ [52] of −0.09 reflects the known instability of κ at this sample size [53] rather than poor agreement. The system matched the expert majority in all four decisive cases (Cohen κ = 1.000; Figure 3B); in the split case the dissenting experts cited treatment-plan dependence, the same consideration the system's evidence chain raises (contralateral systematic yield 0.3–4%, EV0024). All 80 Likert ratings were 5/5 (ceiling; Figure 3C). At this sample size, all agreement estimates are preliminary.

### Runtime cost

The 7,640-character mean context (~2,500–3,000 tokens) yields a median latency of ~20–40 s per verdict (flash generator, eight workers; Figure 5A, Supplementary S4); an interactive Streamlit interface supports use.

## Discussion

### Principal findings

QianLieAnHui operationalises the decision points where prostate-biopsy practice varies most; benchmarked under a strictly fixed generator against all 112 ProBIOPSY final statements, it reached exact-5 0.805 (κ 0.730, against-F1 0.908, specificity 0.986), +19.2 points over the strongest baseline. To our knowledge, this is the first biopsy-pathway decision-support agent validated statement by statement against an international consensus. More informative than the margin is how the baselines lost: across 1,120 retrieval-baseline runs, conditional endorsement was actively emitted 9 times (0.8%; pure LLM 14 of 560) against 17.0% for the full system (Figure 2C). Retrieval-augmented models are not ignorant of the consensus text; they simply do not narrow or qualify their commitments as the patient's condition changes. The baselines' superior exact-3 is majority-class inflation — coarse metrics overestimate unconstrained medical RAG systems, and evaluation should be reported at fine-grained action level.

The full system's own errors also have a clinical profile: endorsement is near-perfect (190/190), but 74 of 185 gold-conditional statements were predicted endorse (recall 0.51) — an over-permissive skew, the direction governance worries about most, since misreading conditional support as unconditional endorsement leaves a scheme mismatched to the treatment intent. The four-expert review adds a human line of evidence: expert judgements matched the system in all four decisive cases (Cohen κ = 1.000; Figure 3), the split-case dissent citing treatment-plan dependence — the same consideration the evidence chain raises (EV0024). The system presents reasoning material experts can verify, not a black-box verdict.

### Clinical implications

The pathway's decisions are made by individual clinicians in busy clinics, and the variation documented by the consensus panel itself [21] indicates they are inconsistent across centres. Urologists in non-specialised centres gain consensus-level recommendations where dedicated support is unavailable and mismatches most likely; residents get every recommendation linked to its statement; experienced surgeons shed routine scheme checking. For patients, each avoided unnecessary biopsy is one fewer exposure to complications [19,20,47]; the against class (F1 0.908, almost no false vetoes) declines when appropriate, and explicit conditionals may support shared decision-making. A RAG tool grounded in the EAU and AUA guidelines provided guideline-concordant PSA recommendations in 95.5% of scenarios versus 62.3%–74.1% for junior clinicians [54]; our system extends this to the biopsy pathway against all 112 statements of an international consensus. Its decision points sit on current guidelines — mpMRI before biopsy, MRI-targeted sampling, risk-adapted prophylaxis, transperineal access [22,23,24], consistent with recent trials [6-8]. The rule base encodes the stable skeleton while the updating periphery lives in retrieval: as evidence shifts, the corpus is rebuilt without touching the rules (SHA-256-checked coupling); reader-variability dependence [16] is carried as flags, grade-discordance-aware planning [13] anchored by the largest domain. For deployment, the asymmetry to emphasise is the unequal cost of veto error directions: an unsupported "yes" can mean biopsy despite inadequate image quality or transrectal access without prophylaxis escalation; a conservative "no" costs one more imaging review. The system therefore suppresses false vetoes first — specificity 0.986 is the mechanical consequence of requiring rule or evidence support for every veto — and traceability plus version integrity prevent the silently stale knowledge base [39], making governance audits possible.

The pathway is incomplete if the agent serves only the clinician's half of the consultation — the asymmetry that motivates patient-facing agents elsewhere [25,26]. The education mode reuses the frozen evidence chain with a curated, source-traceable fact base, so a patient answer is auditable like a clinician verdict. Isolated HGPIN generally does not mandate early repeat biopsy, whereas ASAP warrants re-sampling because a meaningful fraction of re-biopsies detect clinically significant cancer [48,49] — messages patients miss when counselling time is short. The mode issues no action verdict, keeping the five-action layer exclusive to clinician decisions.

### Technical considerations

Sixteen rules tell the arbiter deterministically when a commitment must be narrowed and forbid any veto or endorsement that neither a rule nor retrieved evidence supports; conditional and equivalent-option endorsement thereby rise from near-disuse to routine output. Upgrading the generator tier made naive RAG worse (0.605 → 0.538) and extra inference-time compute did not help (self-consistency 0.777) — fine-grained action-space competence is a property of the architecture, not an emergent bonus of scale. The cost is context (7,640 characters, ~3× the strongest baseline, traded for +19.2 points); rule-gated short-circuiting (pure-rule combinations skip graph retrieval) can amortise it. Medical RAG benchmarks such as MIRAGE [37] measure what a model knows; we measure whether a system can execute a consensus as auditable clinical actions. Retrieval anchors generation [36] but nothing intercepts a fluent contradicting recommendation — the chronic kidney disease evaluation shows the same pattern from outside (correctness 1.00 → 0.28 and 0.10 beyond the corpus [38]); our architecture addresses both ends: a closed five-class action space under hard constraints, and coverage audited statement by statement. This also fixes the role of general graph-retrieval schemes (Microsoft GraphRAG [55]; LightRAG [46]): the GraphRAG layer remains the evidence engine while classification and restraint are delegated to the rule layer, compressing the maintenance burden documented for rule-based clinical decision support [41] into sixteen auditable rules. In a field where LLMs approach expert-level question answering [30] and chatbot responses have been rated more empathetic than physician responses [56], the closest contemporaries — PULSE for atrial fibrillation [25], its hypertension analogue [31], an electronic-health-record-integrated education agent [26], GeneAgent [33] — show that retrieval plus prompt optimisation raises rated response quality; our results explain why such gains do not automatically transfer to procedural decision support: perceived quality does not measure guideline conformance, prompt-level safeguards persuade but do not bind, and a fluent answer can still misplace a veto.

### Limitations

First, **corpus–gold-standard homology**: both derive from the consensus, so this is a consensus-conformance evaluation, not independent clinical validity; retrieval-level guideline concordance is untested and prospective external validation is the necessary next step. Second, **the residual conditional weakness** (recall 0.51, over-permissive) requires class-specific calibration before piloting. Third, **the face-validity panel is small** (four experts, five propositions; a negative Fleiss κ despite 17/20 agreement illustrates the small-sample artefact [53]; ceiling Likert; single-institution). Fourth, **synthetic scenarios** do not span real comorbidity complexity. Fifth, **one generator family** (GLM); cross-vendor generalisation is untested, though the supplement shows generator tier is not decisive. Sixth, **combinatorial coverage**: 112 statements cover the high-frequency region of the 51 × 54 space; long-tail coverage unquantified. Seventh, **context cost** (~3× the strongest baseline). Eighth, **language**: an English corpus with a Chinese registry and interface; cross-lingual transfer is untested. Ninth, **the education mode** is demonstrated, not evaluated.

### Future directions

The path toward piloting follows from these gaps: a multi-centre face-validity and usability study; a prospective registry study with real cases reported under DECIDE-AI and TRIPOD+AI [43,44]; Fast Healthcare Interoperability Resources (FHIR) integration for automatic scenario filling; on-premises generator deployment to eliminate protected-health-information transfer; and a supervised pilot of the education mode. Two governance provisions complete the roadmap: a versioned, multi-sourced evidence stack where a guideline revision triggers a versioned index rebuild and benchmark re-run, not silent drift; and out-of-scope or low-confidence detection that degrades to an explicit alert. Extending the rule base to other guideline chapters and PSMA-PET–first pathways [57] tests how generalisable statement-level consensus executability is: any consensus terminating in explicit statements could travel the same route from static text to an auditable, executable checklist at the point of decision.

## Conclusions

QianLieAnHui demonstrates that chaining deterministic rule constraints, knowledge-graph evidence retrieval, and LLM arbitration — each layer covering the others' failure modes — raises fine-grained decision accuracy to a level suitable for pilot evaluation (exact-5 0.805, κ 0.730, against-F1 0.908), with every output traceable to numbered statements and evidence chunks and the same frozen evidence chain supporting auditable lay-language patient education. The benchmark establishes consensus conformance; independent clinical validity awaits prospective validation. Architecture, not a larger model, is currently the dominant lever.

## Data availability

The rule base (configs/rules.yaml), both registries (entities_a.csv, entities_b.csv), the evidence corpus (evidence_chunks.jsonl, 357 chunks), the patient-education fact base (patient_education_facts.csv, ten source-traceable entries), the verbatim patient-education transcripts (demo_cases/patient_edu/), the gold-standard annotations (probiopsy_statements.csv, 112 statements), all 2,240 raw predictions with per-run context sizes and retrieved-chunk counts (baseline_predictions.jsonl), the flagship-tier supplement (baseline_predictions_glm53.jsonl), the self-consistency supplement with all 560 raw votes (selfconsistency_predictions.jsonl), the offline failure decomposition of all 560 full-system runs (failure_decomposition.json; figures/source_data/failure_decomposition_runs.csv), the evaluation script (evaluate.py), and all figure source data are released with the repository (https://github.com/xuzekun6251/probiopsy-rag) and archived on Zenodo [58].

## Ethics statement

No patient data or biological samples were involved. The evidence corpus and gold standard derive solely from the published ProBIOPSY consensus and its supplementary material; all demonstration cases are synthetic vignettes constructed by the study team. No patient-identifiable data were transmitted to third-party model APIs. The four-expert blinded review used anonymous, voluntary participation (experts 1–4; no identifiable data collected; participation-information sheet embedded in the questionnaire). Institutional review board approval was therefore not required; the assessment is documented in the project ethics file accompanying the repository.

## Figure legends

**Figure 1.** System architecture and benchmark design. The ProBIOPSY consensus corpus (112 final statements; 357 evidence chunks; GraphRAG index of 1,864 entities and 3,078 relations, built with LightRAG) is distilled at build time into 16 deterministic rules and the retrieval index. At run time, a patient-scenario × decision-item query passes through (1) the deterministic rule engine, which emits Q-coded hard constraints (dashed arrow binding the arbiter), (2) risk-guided retrieval over the GraphRAG knowledge graph fused with the lexical evidence store, and (3) an LLM arbiter (GLM-5.3) that produces a five-class action verdict with statement-level citations under hard-constrained decoding. An example query (unifocal PI-RADS 4 lesion, focal therapy planned) and the corresponding structured output are shown. A second runtime mode (strip below the pipeline) reuses the identical frozen evidence base for patient-facing education: the patient's lay question is keyword-matched against a curated, source-traceable fact base (ten entries), and the same generator produces a plain-language answer with an explicit safety-netting paragraph and referral to the treating urologist (demonstrated qualitatively; not part of the benchmark). Bottom strip: the multi-method, multi-seed benchmark (112 statements × 4 methods × 5 seeds = 2,240 runs, generator held fixed).

**Figure 2.** Multi-seed benchmark (4 methods × 5 seeds × 112 statements). **(a)** Core metrics by method (mean ± SD across 5 seeds): exact-5 accuracy, exact-3 accuracy, macro-F1, Cohen's κ, and against-class F1. **(b)** Exact-5 accuracy per seed (dots; dash = mean). **(c)** Predicted class distribution per method over 560 runs (bars) with the gold-standard distribution (diamonds) — retrieval baselines almost never emit conditional; the full system's distribution tracks the gold standard most closely.

**Figure 3.** Four-expert blinded review of the five demonstration cases (composite propositions). **(a)** Per-case inter-rater agreement (modal-rating share of 4 experts; dashed line = 3/4). The Fleiss κ of −0.09 (marked *) is a small-sample artefact — raw agreement is 17/20. **(b)** Ratings by case and rater (End = endorse, EndO = endorse_option, Cond = conditional, RepO = report_option, Aga = against). The System column shows the system verdict, which matches the expert majority in all four cases with a decisive majority; case 1 was a 2:2 tie (excluded per the pre-registered rule). **(c)** Expert Likert ratings of the system output (clarity, usefulness, recommendation, evidence; uniformly 5 — ceiling).

**Figure 4.** Demonstration cases. **(a)** Consensus rules fired per case, coloured by recommended action. **(b)** Evidence corpus composition (112 consensus statements, 218 literature entries, 20 narrative passages, 7 systematic-review summaries).

**Figure 5.** Runtime and knowledge-graph statistics. **(a)** Decision-pass latency per demonstration case (log scale): the rule-engine layer (blue) versus retrieval + arbitration (yellow). **(b)** Strongest knowledge-graph relations: the top-12 of 3,078 edges by relation weight.

## Acknowledgments

The author gratefully thanks the four urology experts who participated in the blinded face-validity review (anonymous by design of the study), and the ProBIOPSY consensus group whose statement-level work made an executable, statement-by-statement validation possible.

## Funding

This research received no external funding.

## Conflicts of interest

The authors declare no conflicts of interest.

## CRediT author contributions

XU Zekun: Conceptualization, Methodology, Software, Validation, Writing – original draft.

## Declaration of generative AI and AI-assisted technologies in the writing process

During the preparation of this work the author used large language model tools (GLM; Zhipu AI) in order to assist with software implementation, corpus curation support, and manuscript drafting. After using these tools, the author reviewed and edited all content as needed and takes full responsibility for the content of the published article. The evaluated system itself — including all reported benchmark results — additionally uses LLM components as an object of study, as described in Methods; all quantitative results were produced and verified by deterministic evaluation scripts.

## References

1. Bray F, Laversanne M, Sung H, et al. Global cancer statistics 2022: GLOBOCAN estimates of incidence and mortality worldwide for 36 cancers in 185 countries. CA A Cancer J Clinicians. 2024;74(3):229-263. https://doi.org/10.3322/caac.21834

2. Cao W, Chen HD, Yu YW, Li N, Chen WQ. Changing profiles of cancer burden worldwide and in China: a secondary analysis of the global cancer statistics 2020. Chinese Medical Journal. 2021;134(7):783-791. https://doi.org/10.1097/cm9.0000000000001474

3. Schröder FH, Hugosson J, Roobol MJ, et al. Prostate-Cancer Mortality at 11 Years of Follow-up. N Engl J Med. 2012;366(11):981-990. https://doi.org/10.1056/nejmoa1113135

4. Tracy CR, Flynn KJ, Sjoberg DD, Gellhaus PT, Metz CM, Ehdaie B. Optimizing MRI-targeted prostate biopsy: the diagnostic benefit of additional targeted biopsy cores. Urologic Oncology: Seminars and Original Investigations. 2021;39(3):193.e1-193.e6. https://doi.org/10.1016/j.urolonc.2020.09.019

5. Deng R, Shang J, Wu J, et al. A head-to-head comparison of sextant-systematic biopsy vs. extended-systematic biopsy for prostate cancer diagnosis in the era of MRI-targeted biopsy: SEXTANT-PRO non-inferiority randomized clinical trial. eClinicalMedicine. 2025;90:103630. https://doi.org/10.1016/j.eclinm.2025.103630

6. Bryant RJ, Marian IR, Williams R, et al. Local anaesthetic transperineal biopsy versus transrectal prostate biopsy in prostate cancer detection (TRANSLATE): a multicentre, randomised, controlled trial. The Lancet Oncology. 2025;26(5):583-595. https://doi.org/10.1016/s1470-2045(25)00100-7

7. Yang YJ, Yang EJ, Nguyen TT, Choi SY. Transperineal Versus Transrectal Prostate Biopsy: A Systematic Review and Meta-analysis of Randomized Controlled Trials Across Settings With and Without Magnetic Resonance Imaging Targeting. European Urology Open Science. 2026;83:205-218. https://doi.org/10.1016/j.euros.2025.12.008

8. Liss MA, Kim W, Moskowitz D, Szabo RJ. Comparative Effectiveness of Targeted vs Empirical Antibiotic Prophylaxis to Prevent Sepsis from Transrectal Prostate Biopsy: A Retrospective Analysis. Journal of Urology. 2015;194(2):397-402. https://doi.org/10.1016/j.juro.2015.03.110

9. Ahdoot M, Wilbur AR, Reese SE, et al. MRI-Targeted, Systematic, and Combined Biopsy for Prostate Cancer Diagnosis. N Engl J Med. 2020;382(10):917-928. https://doi.org/10.1056/nejmoa1910038

10. Klotz L, Chin J, Black PC, et al. Comparison of Multiparametric Magnetic Resonance Imaging–Targeted Biopsy With Systematic Transrectal Ultrasonography Biopsy for Biopsy-Naive Men at Risk for Prostate Cancer: A Phase 3 Randomized Clinical Trial. JAMA Oncol. 2021;7(4):534. https://doi.org/10.1001/jamaoncol.2020.7589

11. Elkhoury FF, Felker ER, Kwan L, et al. Comparison of Targeted vs Systematic Prostate Biopsy in Men Who Are Biopsy Naive: The Prospective Assessment of Image Registration in the Diagnosis of Prostate Cancer (PAIREDCAP) Study. JAMA Surg. 2019;154(9):811. https://doi.org/10.1001/jamasurg.2019.1734

12. Costa DN, Goldberg K, Leon ADD, et al. Magnetic Resonance Imaging–guided In-bore and Magnetic Resonance Imaging-transrectal Ultrasound Fusion Targeted Prostate Biopsies: An Adjusted Comparison of Clinically Significant Prostate Cancer Detection Rate. European Urology Oncology. 2019;2(4):397-404. https://doi.org/10.1016/j.euo.2018.08.022

13. Epstein JI, Feng Z, Trock BJ, Pierorazio PM. Upgrading and Downgrading of Prostate Cancer from Biopsy to Radical Prostatectomy: Incidence and Predictive Factors Using the Modified Gleason Grading System and Factoring in Tertiary Grades. European Urology. 2012;61(5):1019-1024. https://doi.org/10.1016/j.eururo.2012.01.050

14. Ahmed HU, El-Shater Bosaily A, Brown LC, et al. Diagnostic accuracy of multi-parametric MRI and TRUS biopsy in prostate cancer (PROMIS): a paired validating confirmatory study. The Lancet. 2017;389(10071):815-822. https://doi.org/10.1016/s0140-6736(16)32401-1

15. Turkbey B, Rosenkrantz AB, Haider MA, et al. Prostate Imaging Reporting and Data System Version 2.1: 2019 Update of Prostate Imaging Reporting and Data System Version 2. European Urology. 2019;76(3):340-351. https://doi.org/10.1016/j.eururo.2019.02.033

16. Park KJ, Choi SH, Lee JS, Kim JK, Kim MH. Interreader Agreement with Prostate Imaging Reporting and Data System Version 2 for Prostate Cancer Detection: A Systematic Review and Meta-Analysis. Journal of Urology. 2020;204(4):661-670. https://doi.org/10.1097/ju.0000000000001200

17. Giganti F, Allen C, Emberton M, Moore CM, Kasivisvanathan V. Prostate Imaging Quality (PI-QUAL): A New Quality Control Scoring System for Multiparametric Magnetic Resonance Imaging of the Prostate from the PRECISION trial. European Urology Oncology. 2020;3(5):615-619. https://doi.org/10.1016/j.euo.2020.06.007

18. Yusim I, Krenawi M, Mazor E, Novack V, Mabjeesh NJ. The use of prostate specific antigen density to predict clinically significant prostate cancer. Sci Rep. 2020;10(1):20015. https://doi.org/10.1038/s41598-020-76786-9

19. Loeb S, Vellekoop A, Ahmed HU, et al. Systematic Review of Complications of Prostate Biopsy. European Urology. 2013;64(6):876-892. https://doi.org/10.1016/j.eururo.2013.05.049

20. Nam RK, Saskin R, Lee Y, et al. Increasing Hospital Admission Rates for Urological Complications After Transrectal Ultrasound Guided Prostate Biopsy. Journal of Urology. 2010;183(3):963-969. https://doi.org/10.1016/j.juro.2009.11.043

21. Chernysheva D, Di Bello F, Avesani G, et al. ProBIOPSY: A Multidisciplinary International Consensus on Standards for Prostate Biopsy. European Urology. 2026;90(3):212-224. https://doi.org/10.1016/j.eururo.2026.06.012

22. European Association of Urology. EAU Guidelines on Prostate Cancer. Arnhem: European Association of Urology; 2026. https://uroweb.org/guidelines/prostate-cancer (living guideline, accessed September 2026).

23. Eastham JA, Auffenberg GB, Barocas DA, et al. Clinically Localized Prostate Cancer: AUA/ASTRO Guideline, Part I: Introduction, Risk Assessment, Staging, and Risk-Based Management. Journal of Urology. 2022;208(1):10-18. https://doi.org/10.1097/ju.0000000000002757

24. Eastham JA, Barocas DA, Chu CE, et al. Clinically Localized Prostate Cancer: AUA/ASTRO Guideline Amendment (2026). J Urol. 2026;216(1):2-11. https://doi.org/10.1097/ju.0000000000005060

25. Wang Y, Peng C, Hu R, et al. A knowledge-enhanced domain-aware large language model agent for atrial fibrillation management. npj Digit. Med. 2026. https://doi.org/10.1038/s41746-026-03038-x

26. Hao Y, Holmes J, Waddle MR, et al. Personalizing prostate cancer education for patients using an EHR-Integrated LLM agent. npj Digit. Med. 2025;8(1):770. https://doi.org/10.1038/s41746-025-02166-0

27. Rajpurkar P, Chen E, Banerjee O, Topol EJ. AI in health and medicine. Nat Med. 2022;28(1):31-38. https://doi.org/10.1038/s41591-021-01614-0

28. Thirunavukarasu AJ, Ting DSJ, Elangovan K, Gutierrez L, Tan TF, Ting DSW. Large language models in medicine. Nat Med. 2023;29(8):1930-1940. https://doi.org/10.1038/s41591-023-02448-8

29. Singhal K, Azizi S, Tu T, et al. Large language models encode clinical knowledge. Nature. 2023;620(7972):172-180. https://doi.org/10.1038/s41586-023-06291-2

30. Singhal K, Tu T, Gottweis J, et al. Toward expert-level medical question answering with large language models. Nat Med. 2025;31(3):943-950. https://doi.org/10.1038/s41591-024-03423-7

31. Wang Y, Tan W, Cheng S, et al. Large Language Model Agent for Managing Patients With Suspected Hypertension. Hypertension. 2026;83(1):212-224. https://doi.org/10.1161/hypertensionaha.125.25305

32. Sha H, Gong F, Liu B, Liu R, Wang H, Wu T. Leveraging Retrieval-Augmented Large Language Models for Dietary Recommendations With Traditional Chinese Medicine's Medicine Food Homology: Algorithm Development and Validation. JMIR Med Inform. 2025;13:e75279-e75279. https://doi.org/10.2196/75279

33. Wang Z, Jin Q, Wei CH, et al. GeneAgent: self-verification language agent for gene-set analysis using domain databases. Nat Methods. 2025;22(8):1677-1685. https://doi.org/10.1038/s41592-025-02748-6

34. Ji Z, Lee N, Frieske R, et al. Survey of Hallucination in Natural Language Generation. ACM Comput. Surv. 2023;55(12):1-38. https://doi.org/10.1145/3571730

35. Fast D, Adams LC, Busch F, et al. Autonomous medical evaluation for guideline adherence of large language models. npj Digit. Med. 2024;7(1):358. https://doi.org/10.1038/s41746-024-01356-6

36. Lewis P, Perez E, Piktus A, et al. Retrieval-augmented generation for knowledge-intensive NLP tasks. Adv Neural Inf Process Syst. 2020;33:9459-74. arXiv:2005.11401 (verified via arXiv API).

37. Xiong G, Jin Q, Lu Z, Zhang A. Benchmarking Retrieval-Augmented Generation for Medicine. Findings of the Association for Computational Linguistics ACL 2024. 2024:6233-6251. https://doi.org/10.18653/v1/2024.findings-acl.372

38. Sesen MB, Au Yeung JA, Asgari E. Development and evaluation of Retrieval-Augmented Generation (RAG) and GraphRAG for guideline-based clinical decision support in chronic kidney disease. BMJ Digit Health. 2026;2(1):e000041. https://doi.org/10.1136/bmjdh-2026-000041 (verified via Crossref API, 2026-11-20; author name as printed in the article byline).

39. Hao S, Chai C, Li G, Tang N, Wang N, Yu X. Outdated Fact Detection in Knowledge Bases. In: 2020 IEEE 36th International Conference on Data Engineering (ICDE). IEEE; 2020:1890-1893. https://doi.org/10.1109/icde48307.2020.00196

40. Ray CE, Wilson GM, Hughes AM, et al. Alert fatigue measurement in clinical decision support: a systematic review. Journal of the American Medical Informatics Association. 2026;33(8):1523-1531. https://doi.org/10.1093/jamia/ocag064

41. Sutton RT, Pincock D, Baumgart DC, Sadowski DC, Fedorak RN, Kroeker KI. An overview of clinical decision support systems: benefits, risks, and strategies for success. npj Digit. Med. 2020;3(1):17. https://doi.org/10.1038/s41746-020-0221-y

42. Pan S, Luo L, Wang Y, Chen C, Wang J, Wu X. Unifying Large Language Models and Knowledge Graphs: A Roadmap. IEEE Trans. Knowl. Data Eng. 2024;36(7):3580-3599. https://doi.org/10.1109/tkde.2024.3352100

43. Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ. 2024;385:e078378. https://doi.org/10.1136/bmj-2023-078378

44. Vasey B, Nagendran M, Campbell B, et al. Reporting guideline for the early stage clinical evaluation of decision support systems driven by artificial intelligence: DECIDE-AI. BMJ. 2022;377:e070904. https://doi.org/10.1136/bmj-2022-070904

45. Epstein JI, Amin MB, Reuter VE, Humphrey PA. Contemporary Gleason Grading of Prostatic Carcinoma: An Update With Discussion on Practical Issues to Implement the 2014 International Society of Urological Pathology (ISUP) Consensus Conference on Gleason Grading of Prostatic Carcinoma. American Journal of Surgical Pathology. 2017;41(4):e1-e7. https://doi.org/10.1097/pas.0000000000000820

46. Guo Z, Xia L, Yu Y, Ao T, Huang C. LightRAG: simple and fast retrieval-augmented generation. arXiv:2410.05779, 2024 (verified against arXiv listing).

47. Borghesi M, Ahmed H, Nam R, et al. Complications After Systematic, Random, and Image-guided Prostate Biopsy. European Urology. 2017;71(3):353-365. https://doi.org/10.1016/j.eururo.2016.08.004

48. Morote J, Schwartzmann I, Celma A, et al. The current recommendation for the management of isolated high‐grade prostatic intraepithelial neoplasia. BJU International. 2021;129(5):627-633. https://doi.org/10.1111/bju.15568

49. Ji WT, Jin XF, Wang Y. The Rate of Clinically Significant Prostate Cancer on Repeat Biopsy after a Diagnosis of Atypical Small Acinar Proliferation: A Systematic Review and Meta-Analysis. Oncology. 2023;102(7):631-640. https://doi.org/10.1159/000535123

50. Cohen J. A Coefficient of Agreement for Nominal Scales. Educational and Psychological Measurement. 1960;20(1):37-46. https://doi.org/10.1177/001316446002000104

51. Benjamini Y, Hochberg Y. Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing. Journal of the Royal Statistical Society Series B: Statistical Methodology. 1995;57(1):289-300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x

52. Fleiss JL. Measuring nominal scale agreement among many raters.. Psychological Bulletin. 1971;76(5):378-382. https://doi.org/10.1037/h0031619

53. Feinstein AR, Cicchetti DV. High agreement but low Kappa: I. the problems of two paradoxes. Journal of Clinical Epidemiology. 1990;43(6):543-549. https://doi.org/10.1016/0895-4356(90)90158-l

54. Tung JYM, Le Q, Yao J, et al. Performance of Retrieval-Augmented Generation Large Language Models in Guideline-Concordant Prostate-Specific Antigen Testing: Comparative Study With Junior Clinicians. J Med Internet Res. 2025;27:e78393-e78393. https://doi.org/10.2196/78393

55. Edge D, Trinh H, Cheng N, et al. From local to global: a Graph RAG approach to query-focused summarization. arXiv:2404.16130, 2024 (verified via arXiv API).

56. Ayers JW, Poliak A, Dredze M, et al. Comparing Physician and Artificial Intelligence Chatbot Responses to Patient Questions Posted to a Public Social Media Forum. JAMA Intern Med. 2023;183(6):589. https://doi.org/10.1001/jamainternmed.2023.1838

57. Al-Khanaty A, Hennes D, Hofman MS, et al. Avoiding Prostate Biopsy in Early Prostate Cancer Detection: From Liquid Biopsy to PSMA-PET. European Urology Focus. 2026. https://doi.org/10.1016/j.euf.2026.05.019

58. XU Z. QianLieAnHui (probiopsy-rag): a hybrid rule-engine, knowledge-graph, and LLM-arbitration decision-support system for the prostate biopsy pathway, validated against the ProBIOPSY consensus [software, version v1.0.1]. Zenodo. 2026. https://doi.org/10.5281/zenodo.22898439 (verified via DataCite API).

> **Reference QC:** all 58 references verified programmatically — DOI-based entries resolved against the Crossref API (api.crossref.org; metadata auto-generated in `scripts/renumber_refs.py`, cache `outputs/paper/refs_vancouver.json`); arXiv entries (refs 36, 46, 55) verified via the arXiv API / arXiv listings; the Zenodo software deposit via the DataCite API; the EAU guideline is a living web citation — update edition and access date at submission time. The QC annotations on refs 36, 38, 46, 55, 58 are verification provenance, not part of the citation display.
