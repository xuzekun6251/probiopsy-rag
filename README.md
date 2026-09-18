# QianLieAnHui (前列安汇 / probiopsy-rag)

**A hybrid rule-engine + knowledge-graph + LLM-arbitration decision-support system for the prostate biopsy pathway, validated statement-by-statement against the ProBIOPSY international consensus.**

QianLieAnHui turns the [ProBIOPSY consensus](https://doi.org/10.1016/j.eururo.2026.06.012) (Chernysheva et al., *European Urology*, 2026) into an executable, auditable clinical decision-support pipeline: for a given patient scenario it emits one of five actions — `endorse`, `endorse_option`, `conditional`, `report_option`, `against` — each traceable to numbered consensus statements, rule firings, and knowledge-graph evidence chunks.

## Headline results (4 methods × 5 seeds × 112 consensus statements = 2,240 runs)

| Method | Exact-5 accuracy | Cohen's κ | Macro-F1 | Against-F1 |
|---|---|---|---|---|
| **QianLieAnHui (full)** | **0.805 ± 0.012** | **0.730 ± 0.016** | **0.825 ± 0.022** | **0.908** (spec. 0.986) |
| LightRAG only | 0.613 | 0.525 | — | — |
| Naive RAG | 0.605 | — | — | — |
| Pure LLM | 0.304 | — | — | — |

All full-vs-baseline differences are significant under paired two-sided *t*-tests across seeds with Benjamini–Hochberg FDR correction (worst adjusted *p* = 8.9 × 10⁻⁴). Retrieval-augmented baselines structurally collapse onto frequent action classes (the nuanced `conditional` class: 0.8% of baseline runs vs 17.0% for the full system); upgrading the generator tier does not rescue them (naive-RAG exact-5: 0.605 → 0.538). Architecture, not model scale, is the dominant lever.

## Architecture

1. **Rule engine (hard constraints, `configs/rules.yaml`)** — 16 deterministic safety rules mechanically constrain the output space before any generation.
2. **Risk-guided LightRAG retrieval (`src/probiopsy_rag_agent/lightrag_adapter.py`)** — 357 evidence chunks / 1,864 entities / 3,078 relations built from the consensus; retrieval scope steered by patient risk stratum.
3. **LLM arbiter (`pipeline.py`, `safety_agent.py`)** — emits the five-class action with a citation chain (Q-numbers + evidence-chunk ids); a safety agent re-checks the verdict against fired rules.

A four-expert blinded face-validity review (5 composite propositions, two-part blinded booklet) found system-vs-expert-majority agreement Cohen's κ = 1.000 in decisive cases and 5/5 Likert ratings on all 20 clarity/usefulness items.

## Repository layout

```
configs/            rules.yaml (16 rules), prompts.yaml, author_info.yaml
src/probiopsy_rag_agent/   pipeline, rule engine, LightRAG adapter, LLM/embedding clients, schemas
app/streamlit_app.py       interactive demo (decision report + free-form Q&A)
scripts/            build & run & evaluate pipeline (see below)
data/seed/          consensus statements (gold), entity registries, evidence chunks
data/processed/     LightRAG index (local build artifact)
outputs/            figures, tables, manuscripts, submission pack, demo case reports
```

## Quickstart

```bash
git clone <repo-url> probiopsy-rag && cd probiopsy-rag
python -m venv .venv
.venv\Scripts\pip install -e ".[streamlit]"     # Windows; on POSIX: .venv/bin/pip ...
```

Create a `.env` in the project root with your API credentials (never commit it — it is gitignored):

| Variable | Purpose |
|---|---|
| `HUANYU_BULK_API_KEY` (or `DEEPSEEK_API_KEY`) | chat/arbitration LLM |
| `HUANYU_BULK_BASE_URL`, `HUANYU_BULK_MODEL` (or `LLM_CHAT_MODEL`) | endpoint + model name |
| `HUANYU_EMBED_API_KEY` (or `ARK_DOUBAO_API_KEY`) | embedding service |
| `HUANYU_EMBED_BASE_URL`, `HUANYU_EMBED_ENDPOINT_ID` / `HUANYU_EMBED_MODEL`, `HUANYU_EMBED_DIM` | embedding endpoint + dimension |

Build the corpus and run the benchmark:

```bash
.venv\Scripts\python scripts\build_entity_a_registry.py
.venv\Scripts\python scripts\build_entity_b_registry.py
.venv\Scripts\python scripts\build_evidence_base.py
.venv\Scripts\python scripts\build_lightrag_index.py     # requires embedding API
.venv\Scripts\python scripts\build_statement_gold.py
.venv\Scripts\python scripts\run_multiseed.py            # 4 methods × 5 seeds × 112 statements
.venv\Scripts\python scripts\evaluate.py
.venv\Scripts\python scripts\run_demo_cases.py           # 5 end-to-end demonstration cases
.venv\Scripts\streamlit run app\streamlit_app.py         # interactive interface
```

## Data provenance and copyright

All gold-standard content derives from the ProBIOPSY consensus, which is published Open Access under a **CC BY 4.0** license. Consensus text in `data/seed/` and `data/evidence/` is redistributed **verbatim, without modification, with attribution** (see [LICENSE](LICENSE)). If you extend the corpus with differently licensed guideline text, verify redistribution rights first (see [`docs/publish_github_zenodo.md`](docs/publish_github_zenodo.md)); `scripts/scrub_statement_text.py` can strip consensus text if ever needed.

No patient data, biological samples, or identifiable human data are used; the expert review was anonymous and voluntary.

## License

Code: MIT (see [LICENSE](LICENSE)). Data files under `data/seed/` and `data/evidence/`: CC BY 4.0, inherited from the ProBIOPSY consensus article.

## Citation

If you use this codebase, please cite the manuscript (see `outputs/paper/manuscript.en.md`) and the Zenodo archive (DOI: see `configs/author_info.yaml` → `zenodo_doi`).

```bibtex
@software{qianlieanhui2026,
  title  = {QianLieAnHui: a hybrid rule-engine, knowledge-graph, and LLM-arbitration
            decision-support system for the prostate biopsy pathway},
  year   = {2026},
  doi    = {10.5281/zenodo.XXXXXXX},   % fill after Zenodo deposit
  url    = {https://github.com/<user>/probiopsy-rag}
}
```
