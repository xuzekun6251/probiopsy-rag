# Data Availability Statement

**Code.** The complete implementation (rule engine, evidence store, LightRAG adapter, LLM arbiter, Streamlit application, benchmark runner, evaluation scripts, and figure renderers) is available at https://github.com/xuzekun6251/probiopsy-rag and archived on Zenodo at 10.5281/zenodo.22898439 at the time of acceptance.

**Data.** All artifacts needed to reproduce the benchmark are released:

- `configs/rules.yaml` — the 12 consensus rules + 4 patient-factor rules (with Q-statement provenance); SHA-256 `f500802ee82a4be9fc7a7b6b951e2e7083c09e9ef6a521e7dd280726dbe0ee62` is recorded at index build time for version integrity.
- `data/seed/entities_a.csv`, `entities_b.csv` — the two registries (51 patient-scenario archetypes; 54 decision items).
- `data/seed/evidence_chunks.jsonl` — the 357-chunk evidence corpus with source, evidence level, PMID/DOI where applicable, and verification status.
- `data/seed/probiopsy_statements.csv` — the 112 gold-standard statements with expected five-class actions and source locators.
- `outputs/baseline_predictions.jsonl` — all 2,240 primary benchmark predictions (method × seed × statement) with per-run context size and retrieved-chunk counts; `outputs/baseline_predictions_glm53.jsonl` — the 1,122-run flagship-tier supplementary experiment.
- `outputs/evaluation_summary.json` (+ `_glm53_baselines.json`) — per-seed and aggregate metrics.
- `outputs/figures/source_data/*.csv`, `outputs/tables/*.csv` — figure and table source data.

**Third-party services.** Entity/relation extraction and arbitration used Zhipu GLM-5.3 / GLM-5.3-Flash via API (https://open.bigmodel.cn, accessed September 2026); embeddings used doubao-embedding-vision-251215 (Volcengine Ark). No patient-identifiable data were transmitted to any service.

**Licensing.** Code under MIT. Data files derived from the ProBIOPSY consensus (`data/seed/`, `data/evidence/`) are redistributed under the source article's Creative Commons Attribution (CC BY 4.0) license (© the consensus authors; Chernysheva et al., 2026, doi:10.1016/j.eururo.2026.06.012) — statement text is reproduced verbatim, without modification, with attribution. All other data files are released under CC BY 4.0.
