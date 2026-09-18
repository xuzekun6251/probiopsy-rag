# Cover Letter

**To:** The Editor, *European Urology Open Science*
**Date:** 2026-09-18
**Manuscript title:** QianLieAnHui: development and benchmark validation of a hybrid rule-engine, knowledge-graph, and LLM-arbitration decision-support system for the prostate biopsy pathway, against the ProBIOPSY international consensus
**Submission type:** Original Research Article (Methods/Technology)

---

Dear Editor,

We are pleased to submit our manuscript, "QianLieAnHui: development and benchmark validation of a hybrid rule-engine, knowledge-graph, and LLM-arbitration decision-support system for the prostate biopsy pathway, against the ProBIOPSY international consensus," for consideration by *European Urology Open Science*.

**Why this journal.** *EUOS* has positioned itself as the open-access home for rigorously validated methodology in urological practice and technology. Our study is a statement-by-statement validation against the ProBIOPSY consensus published in your sister journal *European Urology* (Chernysheva et al., 2026, doi:10.1016/j.eururo.2026.06.012); the readership best placed to judge and use an executable form of that consensus is precisely yours.

**Main contribution.** We present QianLieAnHui (前列安汇), a decision-support system for the prostate biopsy pathway combining a 16-rule deterministic engine (hard constraints), risk-guided LightRAG knowledge-graph retrieval (357 evidence chunks; 1,864 entities; 3,078 relations), and an LLM arbiter emitting five executable actions. Benchmarking 4 methods × 5 seeds × 112 consensus statements (2,240 runs, generator tier fixed), the full system achieves exact-5-class accuracy 0.805 ± 0.012 and Cohen's κ 0.730 ± 0.016 versus 0.613 / 0.525 for the strongest baseline, with against-class F1 0.908 at specificity 0.986.

**Novelty.** Beyond reporting scores, we isolate *where* the performance comes from: retrieval-augmented baselines structurally collapse onto frequent action classes (the nuanced conditional class was actively emitted in 0.8% of 1,120 baseline runs versus 17.0% for our system), and upgrading the generator tier does not rescue them (naive-RAG exact-5 fell 0.605 → 0.538 with the flagship tier). Architecture — rule-level priors and mechanically enforced hard constraints — is the dominant lever, not model scale.

**Fit.** Every output traces to numbered consensus statements and evidence chunks, and the system's rule-file/index integrity is version-locked — properties directly relevant to clinical governance of AI tools, a standing interest of your readership.

**Declarations:**
- All authors have read and approved the manuscript.
- The work is original, not under review elsewhere, and not previously published.
- Ethics: no human participants, patient data, or biological samples were involved; corpus and gold standard derive from the published ProBIOPSY consensus; demonstration cases are synthetic.
- Data and code will be available upon publication via GitHub + Zenodo (rules, registries, evidence corpus, all 2,240 raw predictions, evaluation scripts).

Thank you for your consideration. We look forward to your response.

Sincerely,

[PI Name TODO]
[Title TODO]
[Department, Institution TODO]
[Email TODO]
