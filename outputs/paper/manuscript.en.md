# QianLieAnHui: development and benchmark validation of a hybrid rule-engine, knowledge-graph, and LLM-arbitration decision-support system for the prostate biopsy pathway, against the ProBIOPSY international consensus

**Running title:** A hybrid rule engine–knowledge graph–LLM system for prostate biopsy decisions

XU Zekun<sup>1,\*</sup>

<sup>1</sup> Department of Urology, Affiliated Jinhua Hospital, Zhejiang University School of Medicine.

<sup>\*</sup> Corresponding author: xuzekunurology@163.com

**Keywords:** prostate cancer; prostate biopsy; clinical decision support; knowledge graph; LightRAG; retrieval-augmented generation; large language models; ProBIOPSY

**Word count:** abstract 248 / main text ~3,300 (excl. tables, legends, references)

---

## Abstract

**Background:** Prostate biopsy decisions must weigh patient-specific MRI quality, biopsy scheme, route, prophylaxis, and treatment-planning needs. The ProBIOPSY consensus (112 final statements) codifies this pathway but is not an executable decision artifact. Large language models (LLMs) hallucinate and lack traceability; retrieval-augmented generation (RAG) mitigates hallucination but provides no deterministic safety guarantees.

**Methods:** We developed QianLieAnHui, a three-layer hybrid: (1) a deterministic rule engine (12 consensus + 4 patient-factor escalation rules) emitting hard constraints; (2) risk-guided retrieval over a LightRAG knowledge graph (357 evidence chunks, 1,864 entities, 3,078 relations, traceable to the consensus); (3) an LLM arbiter emitting one of five executable actions with statement-level citations. Four methods × five seeds × 112 statements (2,240 runs) were benchmarked with one fixed generator (GLM-5.3-Flash), isolating architectural contributions; baselines were re-run with flagship GLM-5.3 (1,120 runs).

**Results:** The full system achieved exact-5 accuracy 0.805±0.012 (±SD over 5 seeds), Cohen's κ 0.730±0.016, and against-class F1 0.908±0.023, versus strongest baseline LightRAG-only (0.613, 0.536, 0.525, 0.881), naive RAG (0.605, 0.514, 0.512, 0.890), and pure LLM (0.304, 0.254, 0.079, 0.346); all differences significant (FDR-adjusted p ≤ 0.001). Retrieval baselines collapsed onto frequent classes (conditional: 9 of 1,120 runs, 0.8%, versus 17.0% for the full system). Upgrading the generator did not rescue naive RAG (0.605→0.538).

**Conclusions:** Fine-grained action-space competence must be built into the architecture—rule-level priors and hard constraints—not delegated to prompting or larger models. Architecture, not generator tier, was the dominant lever; every output traces to consensus statements and evidence chunks, supporting clinical governance audits.

---

## Introduction

Prostate cancer is among the most common malignancies in men [1,2]; population-level PSA screening reduces disease-specific mortality [3] and directs a diagnostic pathway whose cornerstone is biopsy [4]. The modern biopsy pathway extends far beyond a single "to biopsy or not" question: whether to add systematic cores to MRI-targeted cores [5], which saturation scheme to use [6], transperineal versus transrectal access and its complication profile [7,8], anaesthesia and antimicrobial prophylaxis, and whether the harvested tissue satisfies the demands of subsequent treatment planning must all be weighed against patient-specific factors — PI-RADS grade, PSA density, MRI quality, prior negative biopsy, anticoagulation, urinary-tract-infection risk factors, prostate volume, and more [4,9-12]. This modern pathway rests on validated mpMRI diagnostic accuracy [13] and repeated demonstrations that MRI-targeted sampling improves clinically significant cancer detection [14-17]. The ProBIOPSY consensus, a multidisciplinary international effort published in 2026, codified this pathway into 112 final statements and documented substantial international practice variation [4].

A consensus document, however, is not executable. Clinicians face a combinatorial space of patient scenarios × biopsy decisions (51 scenario archetypes × 54 decision items in the registries developed here); static lookup cannot cover the interactions. Rule-based clinical decision support systems (CDSS) capture deterministic logic but are slow to update [18], contribute to alert fatigue [19], and struggle with natural-language evidence [20]. Large language models promise flexible language understanding [21,22] and are approaching expert performance on medical question answering [23,24], yet carry well-documented risks in medicine — hallucination, unstable outputs, and unverifiable provenance [25] — and can diverge from clinical guidelines [26]. RAG grounds generation in an external corpus [27], and medical RAG benchmarks show promise [28], but purely retrieval-based pipelines have no mechanism to *forbid* a plausible-sounding recommendation that contradicts the guideline.

These failure modes are complementary. A deterministic rule engine can mechanically veto non-compliant outputs; knowledge-graph retrieval can expose a traceable evidence chain; an LLM arbiter can supply linguistic flexibility. Chained as *rule gate → graph evidence → LLM arbitration* — an integration consistent with emerging roadmaps for unifying large language models and knowledge graphs [29] — each layer covers the others' failure modes while preserving a complete audit trail from every output back to numbered consensus statements and evidence chunks. At the retrieval layer we adopt LightRAG [30], a graph-based dual-level retrieval framework that outperforms Microsoft GraphRAG [31] on domain question answering at a fraction of the token cost.

We developed and validated QianLieAnHui (前列安汇; "probiopsy-rag"), a hybrid decision-support system for the prostate biopsy pathway, and quantified each architectural layer's contribution with a multi-method, multi-seed benchmark against the 112 ProBIOPSY final statements. Our contributions are:

1. **Architecture.** To our knowledge the first biopsy-pathway decision-support system chaining deterministic rule hard constraints, LightRAG knowledge-graph retrieval, and LLM arbitration, aligned statement-by-statement with an international consensus.
2. **Gold-standard alignment.** All 112 final statements mapped to five executable actions (endorse / endorse_option / conditional / report_option / against); we show that the two nuance-bearing classes — conditional and endorse_option — are almost never emitted by retrieval-augmented baselines, and are placed correctly by no baseline method.
3. **Reproducible benchmark.** With the generator tier held fixed, the full system reached exact-5 0.805 (κ 0.730) versus pure-LLM 0.304, naive RAG 0.605, and LightRAG-only 0.613; upgrading the generator tier did not rescue baseline architectures (naive RAG exact-5 fell to 0.538).
4. **Reproducibility.** Rules, registries, evidence corpus, all 2,240 raw predictions, and evaluation scripts are released; the index records the rule-file SHA-256 at build time so the app can verify index–rules version integrity.

## Methods

### Study design and ethics

This is a system-development and benchmark-validation study. The computational evaluation involved no patient data or biological samples: the corpus derives solely from the published ProBIOPSY consensus and its supplementary material, the gold standard consists of the consensus' 112 published final statements, and demonstration cases are synthetic vignettes constructed by the study team. A four-expert blinded face-validity review was subsequently conducted (anonymous, voluntary participation; synthetic cases only; no identifiable data collected; participation-information sheet embedded in the questionnaire). Because no patient data and no interventional procedures were involved, institutional review board approval was not required (assessment documented during project planning).

### Validation set: 112 ProBIOPSY final statements

All 112 final statements of the ProBIOPSY consensus [4] served as the gold standard. Each statement was mapped to an expected system action in a pre-defined five-class taxonomy: **endorse** (support as stated), **endorse_option** (support as one of several acceptable options), **conditional** (support under specified conditions), **report_option** (present as an available pathway without active recommendation), and **against** (recommend against). The gold-standard action distribution is endorse 190, conditional 185, against 125, endorse_option 35, and report_option 25. Statements span three domains: indication (n = 23), procedure (n = 34), and treatment planning (n = 55, anchored by ISUP grade-group–driven treatment decisions [32]); 25 statements (22.3%) are against-class, providing a demanding test for systems with optimism bias. The five demonstration vignettes described under Results are synthetic cases built on the same registries and are not part of the 112-statement evaluation set.

### System architecture

The input is a pair (patient clinical scenario × biopsy decision item); the output is a structured verdict: one of five actions, a confidence value, triggered rules, and citations to numbered consensus statements and evidence chunks (Figure 1).

**Input layer: dual registries.** Entity A (patient scenarios) contains 51 archetypes with 49 distinct scenario flags across imaging (PI-RADS grade, mpMRI/bpMRI, field strength, PI-QUAL quality [11]), laboratory markers (PSA, PSA density), history and risk (prior negative biopsy, family history, infection risk factors, anticoagulation), treatment intent, and resource availability (Table 1). Entity B (decision items) contains 54 items with 20 flags across indication (22), procedure (22), and treatment-planning linkage (10).

**Layer 1: deterministic rule engine.** The rule base (YAML) holds 16 rules: 12 consensus rules and 4 patient-factor escalation rules (Table 2). Each rule specifies trigger flag combinations (Entity A × Entity B flags), severity, mechanism category (imaging pathway, scheme selection, targeted biopsy, perioperative, treatment planning), and recommended action. Matching is fully deterministic — no LLM involved — and produces hard constraints for downstream layers (e.g., a mandatory veto or mandatory escalation), each carrying ProBIOPSY statement numbers (Q-codes) for provenance. Patient-factor rules escalate consensus rules in context (e.g., infection risk factors → prefer transperineal route or augmented prophylaxis; unfit for curative treatment → simplified biopsy scheme).

**Layer 2: risk-guided LightRAG retrieval.** The corpus comprises 357 evidence chunks, all sourced from the ProBIOPSY consensus and its supplementary material: the 112 final statements (evidence level B), 20 narrative passages, 7 systematic-review summaries, and 218 literature entries extracted from the consensus reference lists (level C). The index was built with LightRAG [30] (lightrag-hku 1.5.7); entity and relation extraction used GLM-5.3-Flash, and the vector index used doubao-embedding-vision-251215 (dimension 2,048). The final index contains 1,864 entities and 3,078 relations (~100 MB). The full system performs risk-guided retrieval: rule matches and active decision items drive entity-boosted hybrid queries (vector + graph structure), executed in context-only mode (retrieving entities, relations, and chunks without letting LightRAG generate the answer itself). Graph context is concatenated with lexical evidence (BM25-style scoring with boosts for active decision items and scenario flags) and passed to the arbiter.

**Layer 3: LLM arbitration.** The arbiter receives (i) scenario flags and decision items, (ii) rule matches with hard constraints, (iii) graph context, and (iv) lexical evidence, and outputs a structured verdict: one of five actions, confidence, a rationale, and citations. The arbitration prompt enforces rule-layer hard constraints: when a hard constraint determines the outcome, the arbiter may not contradict it. Arbitration used Zhipu GLM-5.3 via an OpenAI-compatible API (https://open.bigmodel.cn/api/paas/v4, accessed September 2026). On unparseable or failed LLM output the system degrades to the rule-layer conclusion and flags the record as degraded — failures are never silent.

### Baseline methods

1. **pure_llm** — question answered directly by the LLM with no retrieval and no rules;
2. **naive_rag** — BM25-style lexical retrieval of top-6 chunks (mean 3,644 characters) inserted into the prompt;
3. **lightrag-only** — end-to-end LightRAG hybrid-mode question answering (mean 2,468 characters), with no rule guidance and no hard constraints.

The full system uses a mean of 7,640 characters (graph + lexical), substantially more than the RAG baselines but bounded by a hard context budget.

### Benchmark protocol

Four methods × five seeds (0–4; temperature 0.2) × 112 statements = **2,240 runs**, resumable by (method, seed, statement_id) key. **The generator was held fixed at GLM-5.3-Flash for all methods and seeds**, so that inter-method differences are attributable to retrieval and decision architecture (rules, retrieval strategy, hard constraints) rather than model capability; rate-limiting parameters were identical across methods. All 2,240 runs returned successfully with zero errors and zero degraded records. As a generator-robustness supplement, pure_llm and naive_rag were re-run in full with the flagship GLM-5.3 tier (5 seeds × 112 statements = 1,120 records).

### Expert blinded review

The five demonstration cases were rated by an independent four-expert panel (two urological surgeons, one radiologist, one radiation oncologist; none involved in development). Each case was presented as a composite proposition assembled from declarative decision items. In a blinded first pass, experts selected their own five-class action for the composite proposition; the system verdict (action, confidence, rationale, citations) was then revealed, and experts rated four Likert dimensions (clarity, usefulness, recommendation agreement, evidence sufficiency; 1–5). Pre-registered analysis rules: expert majority = modal rating; 2:2 splits recorded as no-majority and excluded from the system-versus-majority Cohen κ; all agreement statistics interpreted as preliminary given the sample size. The questionnaire and verbatim expert comments are provided in Supplementary S6.

### Metrics

Exact-5-class accuracy (primary), exact-3 accuracy (collapsing endorse_option→endorse and report_option→conditional, to expose majority-class inflation), five-class macro-F1, Cohen's κ [33] against the gold standard, and binary against-class sensitivity/specificity/F1. All metrics are reported as mean ± SD over the five seeds. Method differences were assessed with two-sided paired t-tests across seeds (full system vs each baseline; exact-5 and κ; six comparisons), with Benjamini–Hochberg false-discovery-rate correction [34]. Context characters per run were logged as an efficiency metric.

### Implementation and reproducibility

The system is implemented in Python 3.13 on lightrag-hku 1.5.7. The rule base, both registries, the evidence corpus, the gold-standard annotations, all 2,240 raw predictions (with per-run context size and retrieved-chunk counts), and the evaluation scripts are released with the code. At index build time the SHA-256 of the rule file is recorded (`index_built_against_rules_sha256`); the application UI verifies this digest against the live rule file to prevent silent index–rules divergence.

## Results

### Overview

All 2,240 runs (4 methods × 5 seeds × 112 statements) completed successfully with zero errors and zero degraded outputs. Table 3 reports the performance matrix; Figure 2 shows per-seed distributions.

### Headline performance (Table 3, Figure 2)

The full system outperformed all three baselines on every fine-grained metric (Table 3): exact-5 0.805 ± 0.012 versus 0.613 (LightRAG-only), 0.605 (naive RAG), and 0.304 (pure LLM); κ 0.730 ± 0.016 versus 0.525, 0.512, and 0.079; macro-F1 0.825 ± 0.022 versus 0.536, 0.514, and 0.254. Relative to the strongest baseline this is **+19.2 percentage points exact-5 and +0.205 κ**. All six paired seed-level comparisons (full system vs each baseline; exact-5 and κ) remain significant after Benjamini–Hochberg FDR correction (paired t(4) = 8.9–25.3, all adjusted p ≤ 8.9 × 10⁻⁴). Seed-to-seed variation was small (exact-5 SD 0.012), indicating the advantage is not a stochastic artifact.

### Baselines collapse onto frequent classes (Figure 2C)

The macro-F1 pattern exposes a failure mode invisible to exact-3: both RAG baselines reach high exact-3 accuracy (0.920 / 0.905 — nominally above the full system's 0.823) while their exact-5 (~0.61) and macro-F1 (~0.52) reveal class collapse. Their predicted distributions over 560 runs each concentrate on three frequent classes — LightRAG-only: endorse 162, report_option 168, against 159, endorse_option 68, **conditional 3**; naive RAG: endorse 175, report_option 165, against 154, endorse_option 60, **conditional 6** (Figure 2C). Pure LLM emits conditional and endorse_option more often (14 and 90 of 560 runs) but places them almost never correctly (κ 0.079). The full system uses all five classes substantively: endorse 280, conditional 95, against 115, report_option 32, endorse_option 38. In other words, retrieval-augmented baselines almost never express *conditional endorsement* and *equivalent-option endorsement* — the two actions most critical for nuanced clinical communication — emitting them in 0.5–1.1% of runs versus 17.0% and 6.8% for the full system, and no baseline places them in the right places (κ 0.730 versus ~0.52).

### Against-class behaviour: safe vetoing

Against is the safety-critical class (22.3% of the gold standard). The full system achieved against-F1 0.908 ± 0.023 (sensitivity 0.872 ± 0.018, specificity 0.986 ± 0.010). LightRAG-only reached F1 0.881 with sensitivity 1.000 but specificity only 0.922 — over-calling against — and naive RAG behaved identically (F1 0.890; sens 0.992 / spec 0.931). Pure LLM achieved F1 0.346 (sens 0.416 / spec 0.720). The full system trades a modest sensitivity reduction for near-zero false vetoes, a behavioural difference attributable to hard-constrained arbitration: against is emitted only when rules or evidence explicitly support it.

### Residual errors: conditional endorsement is the hardest class

The full system's aggregated confusion matrix (Supplementary Table S1) shows near-perfect endorsement behaviour (gold endorse: 190/190 correct) but conditional recall of 95/185 (0.51): of the 185 gold-conditional statements, 74 were predicted endorse, 10 report_option, and 6 against. Errors on conditional therefore skew over-permissive — the direction clinical governance is most concerned about — motivating class-specific calibration as future work. Per-domain confusion matrices (Supplementary Table S1) show this pattern is most pronounced in treatment planning, the against-densest domain.

### Generator tier does not rescue baseline architectures (supplementary experiment)

Re-running pure_llm and naive_rag with the flagship GLM-5.3 tier (1,120 runs) changed the conclusion qualitatively not at all and quantitatively for the worse: naive_rag exact-5 fell from 0.605 to 0.538 ± 0.012 (κ 0.512 → 0.450) and pure_llm remained at 0.288 ± 0.013 (κ 0.132). A stronger generator cannot compensate for a missing rule layer and hard constraints; flagship-tier models collapse onto majority classes just as flash-tier models do. This isolates *architecture* — not model selection — as the differentiator.

### Domain breakdown (Table 4)

Against-class density varies sharply by domain (indication 8.7%, procedure 14.7%, treatment planning 32.7%). The full system retains its overall advantage in the against-densest domain; per-domain confusion matrices are provided in Supplementary Table S1.

### Demonstration cases (Figures 4, 5)

Five synthetic demonstration vignettes (unifocal-lesion biopsy scheme, upfront biopsy after PSMA PET, indeterminate bpMRI lesions, advanced-disease route and prophylaxis, infection-risk escalation) ran end-to-end, each producing the correct five-class action, the expected consensus rules (including patient-factor escalations), and a citation chain traceable to Q-codes and evidence chunks (case reports in Supplementary S3).

### Face validity: four-expert blinded review (Figure 3)

Experts agreed with each other substantially: raw agreement 17/20 ratings, with per-case modal share 4/4 in three cases, 3/4 in one (case 2), and a 2:2 split in case 1 (Figure 3A). The overall Fleiss κ [35] of −0.09 reflects the known instability of κ under uneven category marginals at this sample size — the agreement paradox described by Feinstein and Cicchetti — rather than poor agreement [36]. The system matched the expert majority in all four cases with a decisive majority (Cohen κ = 1.000, n = 4; Figure 3B). In the split case — whether to add systematic biopsy to targeted plus perilesional biopsy — the two experts favouring conditional endorsement cited treatment-plan dependence (whole-gland versus focal therapy alters the value of added systematic cores), the same consideration the system's evidence chain raises (contralateral systematic yield 0.3–4% [EV0024]). All 80 Likert ratings of the system output were 5/5 (clarity, usefulness, recommendation, evidence; ceiling noted, Figure 3C). At this sample size, all agreement estimates are preliminary.

### Runtime cost

The full system uses a mean of 7,640 characters of context (~2,500–3,000 tokens). With eight concurrent workers and the flash generator, median end-to-end latency per verdict was ~20–40 s (per-case breakdown: Figure 5A, source data in Supplementary S4). The system supports interactive use (a Streamlit interface with a decision-report module and a free-form RAG question-answering module).

## Discussion

### Principal findings

Under a fixed generator, multi-method, multi-seed benchmarking, this study answers a precise question: **performance differences in prostate-biopsy decision support come primarily from architecture, not from the model.** Three evidence chains converge: (i) the full system reached exact-5 0.805 / κ 0.730, +19.2 points over the strongest baseline; (ii) both RAG baselines nominally "beat" the full system on coarse exact-3 accuracy while collapsing onto three frequent classes — conditional was actively emitted 9 times in 1,120 retrieval-baseline runs (0.8%; pure LLM 14 times in 560) versus 17.0% for the full system; and (iii) upgrading the generator tier made naive RAG *worse* (exact-5 0.605 → 0.538). Fine-grained clinical action-space competence must be built into the system architecture — rule-derived class priors and hard constraints — and cannot be prompted back in.

### Relation to prior work

Large language models are approaching expert-level medical question answering [24] and have generated patient-facing responses rated as more empathetic than physician responses [37]; for constrained, auditable decision support, however, our results indicate that decision architecture — not model capability — is the dominant lever. Medical RAG benchmarks such as MIRAGE [28] evaluate open-question answering accuracy, typically multiple-choice or free text; we instead map an international consensus' final statements onto five executable actions and evaluate *guideline conformance*, a property closer to clinical governance needs. Relative to GraphRAG [31] and LightRAG [30], our contribution is system-level: LightRAG remains the evidence engine, but the lightrag-only baseline demonstrates exactly what happens without a rule layer — against over-calling (sensitivity 1.000, specificity 0.922) and conditional silence. Relative to rule-based CDSS [20], our architecture compresses the auditable rule base to 16 consensus rules and delegates long-tail knowledge to graph retrieval, coupling the two via hard constraints rather than parallel voting.

### Clinical implications

The system is not designed to replace clinician judgement; its value is governability: (1) **safe vetoing** — against-F1 0.908 with specificity 0.986 means the system "dares to dissent but rarely over-dissents", a behaviour mechanically enforced by requiring rule or evidence support for any veto; (2) **full traceability** — every output carries Q-codes, triggered rules, and evidence-chunk citations, enabling governance audits that pure-LLM pipelines cannot provide; (3) **version integrity** — the rule-file SHA-256 recorded at index build and verified live by the UI prevents the classic CDSS failure mode of a silently stale knowledge base [18].

### Limitations

First, **corpus–gold-standard homology**: corpus and gold standard both derive from the ProBIOPSY consensus, so this is a *consensus-conformance* evaluation rather than independent clinical validity; the system never saw action labels during development and the rule base covers only 16 topics, but exposure to statement text cannot be excluded, and prospective external validation is the necessary next step. Second, **the residual conditional weakness**: conditional recall is 0.51 with an over-permissive error skew (74/185 gold-conditional statements predicted endorse); deployed without the rule layer's hard constraints, such errors would shift towards false endorsement, so class-specific calibration is required before clinical piloting. Third, **the face-validity panel is small**: four experts rated five composite propositions; agreement statistics at this n are unstable (a negative Fleiss κ despite 17/20 raw agreement illustrates the artefact [36]), all Likert ratings hit the ceiling, and the panel was single-institution — the review therefore supports preliminary face validity only. Fourth, **synthetic scenarios**: the 51 scenario archetypes and five demonstration cases are synthetic and do not span the full comorbidity complexity of real patients. Fifth, **single generator family**: the benchmark used the GLM family (flash and flagship tiers); cross-vendor generalisation is untested, although the supplement shows generator tier is not the decisive factor. Sixth, **combinatorial coverage**: 112 statements cover the high-frequency region of the 51 × 54 interaction space; long-tail coverage is unquantified. Seventh, **context cost**: the full system's 7,640-character mean context is ~3× the strongest baseline, traded for +19.2 points exact-5; rule-gated short-circuiting (pure-rule combinations skip graph retrieval) can amortise this further. Eighth, **language and region**: the corpus is English, the scenario registry and UI Chinese; cross-lingual transfer is untested.

### Future work

(i) extending the expert panel to a multi-centre face-validity and usability study, including treatment-intent-conditioned scenarios of the kind flagged by the reviewers in the split case; (ii) a prospective registry study with real cases, reported under emerging AI-evaluation standards [38,39]; (iii) extending the rule base to other guideline chapters (active surveillance, imaging follow-up) and emerging PSMA-PET–first pathways [40] to test architecture portability; (iv) FHIR integration for automatic scenario filling from the EMR; (v) on-premises generator deployment to eliminate PHI-transfer concerns.

### Conclusions

QianLieAnHui demonstrates that chaining deterministic rule hard constraints, knowledge-graph evidence retrieval, and LLM arbitration — each layer covering the others' failure modes — raises fine-grained clinical decision accuracy to a level suitable for pilot clinical evaluation (exact-5 0.805, κ 0.730, against-F1 0.908) against an international consensus gold standard, with every output traceable to numbered statements and evidence chunks. Architecture, not a larger model, is currently the dominant lever for medical decision support.

## Data availability

The rule base (configs/rules.yaml), both registries (entities_a.csv, entities_b.csv), the evidence corpus (evidence_chunks.jsonl, 357 chunks), the gold-standard annotations (probiopsy_statements.csv, 112 statements), all 2,240 raw predictions with per-run context sizes and retrieved-chunk counts (baseline_predictions.jsonl), the flagship-tier supplement (baseline_predictions_glm53.jsonl), the evaluation script (evaluate.py), and all figure source data are released with the repository.

## Ethics statement

No patient data or biological samples were involved. The evidence corpus and gold standard derive solely from the published ProBIOPSY consensus and its supplementary material; all demonstration cases are synthetic vignettes constructed by the study team. No patient-identifiable data were transmitted to third-party model APIs. The four-expert blinded review used anonymous, voluntary participation (experts 1–4; no identifiable data collected; participation-information sheet embedded in the questionnaire). Institutional review board approval was therefore not required; the assessment is documented in the project ethics file accompanying the repository.

## Figure legends

**Figure 1.** System architecture. Patient scenario and decision item flow through (1) a deterministic rule engine (12 consensus rules + 4 patient-factor escalation rules) emitting hard constraints, (2) risk-guided retrieval over the LightRAG knowledge graph fused with lexical evidence, and (3) an LLM arbiter producing a five-class action verdict with citations and a rule-enforced constraint check.

**Figure 2.** Multi-seed benchmark (4 methods × 5 seeds × 112 statements). **(a)** Core metrics by method (mean ± SD across 5 seeds): exact-5 accuracy, exact-3 accuracy, macro-F1, Cohen's κ, and against-class F1. **(b)** Exact-5 accuracy per seed (dots; dash = mean). **(c)** Predicted class distribution per method over 560 runs (bars) with the gold-standard distribution (diamonds) — retrieval baselines almost never emit conditional; the full system's distribution tracks the gold standard most closely.

**Figure 3.** Four-expert blinded review of the five demonstration cases (composite propositions). **(a)** Per-case inter-rater agreement (modal-rating share of 4 experts; dashed line = 3/4). The Fleiss κ of −0.09 (marked *) is a small-sample artefact — raw agreement is 17/20. **(b)** Ratings by case and rater (End = endorse, EndO = endorse_option, Cond = conditional, RepO = report_option, Aga = against). The System column shows the system verdict, which matches the expert majority in all four cases with a decisive majority; case 1 was a 2:2 tie (excluded per the pre-registered rule). **(c)** Expert Likert ratings of the system output (clarity, usefulness, recommendation, evidence; uniformly 5 — ceiling).

**Figure 4.** Demonstration cases. **(a)** Consensus rules fired per case, coloured by recommended action. **(b)** Evidence corpus composition (112 consensus statements, 218 literature entries, 20 narrative passages, 7 systematic-review summaries).

**Figure 5.** Runtime and knowledge-graph statistics. **(a)** End-to-end latency per demonstration case (log scale), split into the rule-engine layer (red) and the remaining pipeline (grey). **(b)** Top-12 knowledge-graph edge weights by relation type.

## Acknowledgments

The author gratefully thanks the four urology experts who participated in the blinded face-validity review (anonymous by design of the study), and the ProBIOPSY consensus group whose statement-level work made an executable, statement-by-statement validation possible.

## Funding

This research received no external funding

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

4. Chernysheva D, Di Bello F, Avesani G, et al. ProBIOPSY: A Multidisciplinary International Consensus on Standards for Prostate Biopsy. European Urology. 2026;90(3):212-224. https://doi.org/10.1016/j.eururo.2026.06.012

5. Tracy CR, Flynn KJ, Sjoberg DD, Gellhaus PT, Metz CM, Ehdaie B. Optimizing MRI-targeted prostate biopsy: the diagnostic benefit of additional targeted biopsy cores. Urologic Oncology: Seminars and Original Investigations. 2021;39(3):193.e1-193.e6. https://doi.org/10.1016/j.urolonc.2020.09.019

6. Deng R, Shang J, Wu J, et al. A head-to-head comparison of sextant-systematic biopsy vs. extended-systematic biopsy for prostate cancer diagnosis in the era of MRI-targeted biopsy: SEXTANT-PRO non-inferiority randomized clinical trial. eClinicalMedicine. 2025;90:103630. https://doi.org/10.1016/j.eclinm.2025.103630

7. Loeb S, Vellekoop A, Ahmed HU, et al. Systematic Review of Complications of Prostate Biopsy. European Urology. 2013;64(6):876-892. https://doi.org/10.1016/j.eururo.2013.05.049

8. Nam RK, Saskin R, Lee Y, et al. Increasing Hospital Admission Rates for Urological Complications After Transrectal Ultrasound Guided Prostate Biopsy. Journal of Urology. 2010;183(3):963-969. https://doi.org/10.1016/j.juro.2009.11.043

9. European Association of Urology. EAU Guidelines on Prostate Cancer. Arnhem: European Association of Urology; 2026. https://uroweb.org/guidelines/prostate-cancer (living guideline, accessed September 2026).

10. Turkbey B, Rosenkrantz AB, Haider MA, et al. Prostate Imaging Reporting and Data System Version 2.1: 2019 Update of Prostate Imaging Reporting and Data System Version 2. European Urology. 2019;76(3):340-351. https://doi.org/10.1016/j.eururo.2019.02.033

11. Giganti F, Allen C, Emberton M, Moore CM, Kasivisvanathan V. Prostate Imaging Quality (PI-QUAL): A New Quality Control Scoring System for Multiparametric Magnetic Resonance Imaging of the Prostate from the PRECISION trial. European Urology Oncology. 2020;3(5):615-619. https://doi.org/10.1016/j.euo.2020.06.007

12. Yusim I, Krenawi M, Mazor E, Novack V, Mabjeesh NJ. The use of prostate specific antigen density to predict clinically significant prostate cancer. Sci Rep. 2020;10(1):20015. https://doi.org/10.1038/s41598-020-76786-9

13. Ahmed HU, El-Shater Bosaily A, Brown LC, et al. Diagnostic accuracy of multi-parametric MRI and TRUS biopsy in prostate cancer (PROMIS): a paired validating confirmatory study. The Lancet. 2017;389(10071):815-822. https://doi.org/10.1016/s0140-6736(16)32401-1

14. Ahdoot M, Wilbur AR, Reese SE, et al. MRI-Targeted, Systematic, and Combined Biopsy for Prostate Cancer Diagnosis. N Engl J Med. 2020;382(10):917-928. https://doi.org/10.1056/nejmoa1910038

15. Klotz L, Chin J, Black PC, et al. Comparison of Multiparametric Magnetic Resonance Imaging–Targeted Biopsy With Systematic Transrectal Ultrasonography Biopsy for Biopsy-Naive Men at Risk for Prostate Cancer: A Phase 3 Randomized Clinical Trial. JAMA Oncol. 2021;7(4):534. https://doi.org/10.1001/jamaoncol.2020.7589

16. Elkhoury FF, Felker ER, Kwan L, et al. Comparison of Targeted vs Systematic Prostate Biopsy in Men Who Are Biopsy Naive: The Prospective Assessment of Image Registration in the Diagnosis of Prostate Cancer (PAIREDCAP) Study. JAMA Surg. 2019;154(9):811. https://doi.org/10.1001/jamasurg.2019.1734

17. Costa DN, Goldberg K, Leon ADD, et al. Magnetic Resonance Imaging–guided In-bore and Magnetic Resonance Imaging-transrectal Ultrasound Fusion Targeted Prostate Biopsies: An Adjusted Comparison of Clinically Significant Prostate Cancer Detection Rate. European Urology Oncology. 2019;2(4):397-404. https://doi.org/10.1016/j.euo.2018.08.022

18. Hao S, Chai C, Li G, Tang N, Wang N, Yu X. Outdated Fact Detection in Knowledge Bases. In: 2020 IEEE 36th International Conference on Data Engineering (ICDE). IEEE; 2020:1890-1893. https://doi.org/10.1109/icde48307.2020.00196

19. Ray CE, Wilson GM, Hughes AM, et al. Alert fatigue measurement in clinical decision support: a systematic review. Journal of the American Medical Informatics Association. 2026;33(8):1523-1531. https://doi.org/10.1093/jamia/ocag064

20. Sutton RT, Pincock D, Baumgart DC, Sadowski DC, Fedorak RN, Kroeker KI. An overview of clinical decision support systems: benefits, risks, and strategies for success. npj Digit. Med. 2020;3(1):17. https://doi.org/10.1038/s41746-020-0221-y

21. Rajpurkar P, Chen E, Banerjee O, Topol EJ. AI in health and medicine. Nat Med. 2022;28(1):31-38. https://doi.org/10.1038/s41591-021-01614-0

22. Thirunavukarasu AJ, Ting DSJ, Elangovan K, Gutierrez L, Tan TF, Ting DSW. Large language models in medicine. Nat Med. 2023;29(8):1930-1940. https://doi.org/10.1038/s41591-023-02448-8

23. Singhal K, Azizi S, Tu T, et al. Large language models encode clinical knowledge. Nature. 2023;620(7972):172-180. https://doi.org/10.1038/s41586-023-06291-2

24. Singhal K, Tu T, Gottweis J, et al. Toward expert-level medical question answering with large language models. Nat Med. 2025;31(3):943-950. https://doi.org/10.1038/s41591-024-03423-7

25. Ji Z, Lee N, Frieske R, et al. Survey of Hallucination in Natural Language Generation. ACM Comput. Surv. 2023;55(12):1-38. https://doi.org/10.1145/3571730

26. Fast D, Adams LC, Busch F, et al. Autonomous medical evaluation for guideline adherence of large language models. npj Digit. Med. 2024;7(1):358. https://doi.org/10.1038/s41746-024-01356-6

27. Lewis P, Perez E, Piktus A, et al. Retrieval-augmented generation for knowledge-intensive NLP tasks. Adv Neural Inf Process Syst. 2020;33:9459-74. arXiv:2005.11401 (verified via arXiv API).

28. Xiong G, Jin Q, Lu Z, Zhang A. Benchmarking Retrieval-Augmented Generation for Medicine. Findings of the Association for Computational Linguistics ACL 2024. 2024:6233-6251. https://doi.org/10.18653/v1/2024.findings-acl.372

29. Pan S, Luo L, Wang Y, Chen C, Wang J, Wu X. Unifying Large Language Models and Knowledge Graphs: A Roadmap. IEEE Trans. Knowl. Data Eng. 2024;36(7):3580-3599. https://doi.org/10.1109/tkde.2024.3352100

30. Guo Z, Xia L, Yu Y, Ao T, Huang C. LightRAG: simple and fast retrieval-augmented generation. arXiv:2410.05779, 2024 (verified against arXiv listing).

31. Edge D, Trinh H, Cheng N, et al. From local to global: a Graph RAG approach to query-focused summarization. arXiv:2404.16130, 2024 (verified via arXiv API).

32. Epstein JI, Amin MB, Reuter VE, Humphrey PA. Contemporary Gleason Grading of Prostatic Carcinoma: An Update With Discussion on Practical Issues to Implement the 2014 International Society of Urological Pathology (ISUP) Consensus Conference on Gleason Grading of Prostatic Carcinoma. American Journal of Surgical Pathology. 2017;41(4):e1-e7. https://doi.org/10.1097/pas.0000000000000820

33. Cohen J. A Coefficient of Agreement for Nominal Scales. Educational and Psychological Measurement. 1960;20(1):37-46. https://doi.org/10.1177/001316446002000104

34. Benjamini Y, Hochberg Y. Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing. Journal of the Royal Statistical Society Series B: Statistical Methodology. 1995;57(1):289-300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x

35. Fleiss JL. Measuring nominal scale agreement among many raters.. Psychological Bulletin. 1971;76(5):378-382. https://doi.org/10.1037/h0031619

36. Feinstein AR, Cicchetti DV. High agreement but low Kappa: I. the problems of two paradoxes. Journal of Clinical Epidemiology. 1990;43(6):543-549. https://doi.org/10.1016/0895-4356(90)90158-l

37. Ayers JW, Poliak A, Dredze M, et al. Comparing Physician and Artificial Intelligence Chatbot Responses to Patient Questions Posted to a Public Social Media Forum. JAMA Intern Med. 2023;183(6):589. https://doi.org/10.1001/jamainternmed.2023.1838

38. Vasey B, Nagendran M, Campbell B, et al. Reporting guideline for the early stage clinical evaluation of decision support systems driven by artificial intelligence: DECIDE-AI. BMJ. 2022;377:e070904. https://doi.org/10.1136/bmj-2022-070904

39. Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ. 2024;385:e078378. https://doi.org/10.1136/bmj-2023-078378

40. Al-Khanaty A, Hennes D, Hofman MS, et al. Avoiding Prostate Biopsy in Early Prostate Cancer Detection: From Liquid Biopsy to PSMA-PET. European Urology Focus. 2026. https://doi.org/10.1016/j.euf.2026.05.019

> **Reference QC:** all 40 references verified programmatically on 2026-09-17 — DOI-based entries resolved against the Crossref API (api.crossref.org; metadata auto-generated in `scripts/renumber_refs.py`, cache `outputs/paper/refs_vancouver.json`), arXiv entries (refs for LightRAG, GraphRAG, Lewis RAG) verified via the arXiv API / arXiv listings; the EAU guideline is a living web citation — update edition and access date at submission time.

