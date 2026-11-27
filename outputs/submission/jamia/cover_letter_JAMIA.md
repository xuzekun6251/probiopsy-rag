# Cover Letter — JAMIA submission (Research and Applications)

Dear Editors,

We are pleased to submit our original research manuscript, "QianLieAnHui: development and benchmark validation of a hybrid rule-engine, knowledge-graph, and large language model arbitration decision-support agent for the prostate biopsy pathway, against the ProBIOPSY international consensus," for consideration in the Research and Applications category of the Journal of the American Medical Informatics Association.

Prostate biopsy is the gateway to every treatment decision in prostate cancer, and the new ProBIOPSY international consensus codified the pathway into 112 final statements — yet a written consensus cannot be executed at the point of care. Our study turns those final statements directly into an executable gold standard: the agent QianLieAnHui chains a deterministic rule engine (16 hard-constraint rules), risk-guided retrieval over a GraphRAG knowledge graph (357 evidence chunks), and a large language model arbiter bound by those constraints, emitting one of five consensus-semantic actions with statement-level citations. Under a strictly fixed generator, 4 methods × 5 seeds × 112 statements = 2,240 runs showed exact-5 accuracy of 0.805 ± 0.012 (Cohen's κ 0.730) for the full agent versus 0.613 (GraphRAG-only), 0.605 (naive RAG), and 0.304 (pure LLM); against-class F1 reached 0.908 at specificity 0.986. Offline reconstruction of all 560 evidence packs demonstrated saturated retrieval coverage, locating all 109 residual misclassifications in the arbitration layer, and both a flagship-generator supplement and a self-consistency voting supplement confirmed that fine-grained action competence is a property of the architecture, not of scale or inference strategy. To our knowledge, this is the first biopsy-pathway decision-support agent validated statement by statement against an international consensus.

We believe the manuscript fits JAMIA's readership squarely: it is an architecture-level study of clinical decision support — how deterministic rule constraints, knowledge-graph retrieval, and LLM arbitration can be combined so that each layer covers the others' failure modes — benchmarked with informatics-grade rigour (multi-seed statistics, FDR-corrected paired comparisons, an offline layer-attribution method, and complete release of the rule base, registries, corpus, gold standard, and all raw predictions at https://github.com/xuzekun6251/probiopsy-rag, archived on Zenodo). Reporting follows the TRIPOD+AI and DECIDE-AI items applicable to decision-support systems; a completed DECIDE-AI checklist can be supplied with the submission. The study involved no patient data or biological samples and required no institutional review board approval; the four-expert blinded face-validity review used anonymous, voluntary participation with synthetic cases only.

This manuscript is original, is not published elsewhere, and is not under consideration by any other journal. All authors have approved the submission and declare no conflicts of interest. The work received no external funding. During preparation, large language model tools (GLM; Zhipu AI) were used to assist with software implementation, corpus curation support, and manuscript drafting, with the author reviewing and editing all content and taking full responsibility for it; this use is disclosed in the manuscript's declaration section.

Suggested reviewers: we have no specific reviewer requests and defer to the editors' judgement.

Thank you for your consideration.

Sincerely,

XU Zekun, MD
Department of Urology, Affiliated Jinhua Hospital, Zhejiang University School of Medicine
Email: xuzekunurology@163.com
