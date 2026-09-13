# 前列安汇（probiopsy-rag）

**前列安汇** — A indication_matching, imaging_pathway_selection, biopsy_scheme_selection, perioperative_management, complication_risk_management, treatment_planning_linkage rule-based decision support framework for screening **LightRAG混合决策支持系统:患者临床情境×穿刺决策项** in mri_visible_lesion, mri_indeterminate, prior_negative_biopsy, anticoagulated, focal_therapy_candidate, with a focus on 方法学创新(首个面向外科操作标准化的规则+LightRAG+LLM混合架构)+领域首创(前列腺穿刺全流程知识图谱:影像-指征-方案-并发症-治疗规划一体化)+临床验证强度(96条共识声明还原度+专家盲评+4基线消融).

This project reuses the methodology skeleton of **TongYuan** (FDI screening, *Nutrients* submission) and applies it to a new domain: 患者临床情境要素 × 穿刺决策项 combinations.

## Project Status

📋 **In planning.** This project was scaffolded by the `medical-agent-planner` skill. The PLAN.md, README.md, pyproject.toml, schemas, and rule YAML templates are in place; the coding agent should now execute Phase 0 → Phase 8 per [PLAN.md](PLAN.md).

## Quick Navigation

| Document | Purpose |
|---|---|
| [PLAN.md](PLAN.md) | Master execution plan (8 phases, task list, subagent strategy, timeline) |
| `.planner.config.json` | Phase 1 investigation output (input to scaffold) |
| `src/probiopsy_rag_agent/` | Core source code (to be migrated from TongYuan) |
| `configs/rules.yaml` | Rule engine configuration (to be authored) |
| `data/seed/` | Knowledge base: entities_a.csv, entities_b.csv, evidence_chunks.jsonl (to be built) |

## Differentiation from Reference Project

| Dimension | Reference (TongYuan) | This Project |
|---|---|---|
| Entity A | food | 患者临床情境要素 |
| Entity B | drug | 穿刺决策项 |
| Interaction type | FDI | indication_matching, imaging_pathway_selection, biopsy_scheme_selection, perioperative_management, complication_risk_management, treatment_planning_linkage |
| Rules | 15 | 12 |
| Data sources | FDA + USDA + LiverTox | ProBIOPSY consensus main text + mmc1 supplementary, EAU Prostate Cancer Guidelines (biopsy chapter), AUA/SUO Prostate Cancer Guideline (2023/amended), NICE NG131 Prostate Cancer |
| Target journal | Nutrients | European Urology Open Science |

## Methodology Pipeline

```text
User input (患者临床情境要素 + 穿刺决策项 + patient factors)
  → entity normalization
  → rule-based screening (12 rules)
  → graph-organized evidence retrieval (LightRAG)
  → evidence compression (top-k, char limit)
  → structured safety report
  → expert-review export / evaluation
```

## Setup (conda env per project, Chinese mirrors pre-configured)

The default flow creates a **conda env named after this project** (`probiopsy-rag`) and installs all deps there.

```bash
python scripts/setup_environment.py --project-root . --mirror cn
conda activate probiopsy-rag
```

This will:
- `conda create -n probiopsy-rag python=3.11 -y` if the env doesn't exist (idempotent)
- Install `[dev, llm, lightrag, streamlit]` extras from `pyproject.toml`
- Configure Tsinghua PyPI / TUNA conda / hf-mirror.com mirrors
- Prompt for `DEEPSEEK_API_KEY` (chat) and `ARK_DOUBAO_API_KEY` (火山方舟 embedding) on first run

Alternatives:

```bash
# Different Python version
python scripts/setup_environment.py --project-root . --mirror cn --python 3.12

# Non-interactive (CI / scripted): pre-fill keys in .env first
python scripts/setup_environment.py --project-root . --mirror cn --non-interactive

# Fallback to local .venv if conda is unavailable
python scripts/setup_environment.py --project-root . --mirror cn --env-mode venv
```

Later sessions inside this project can re-discover the env via:

```bash
python C:/Users/heyb1/.claude/skills/medical-agent-planner/scripts/conda_helper.py discover --project-root .
```

## Execution Entry Point

The full development plan is in [PLAN.md](PLAN.md). To regenerate all artifacts from scratch:

```bash
# 1. Build knowledge base
python scripts/build_entity_a_registry.py
python scripts/build_entity_b_registry.py
python scripts/build_evidence_base.py

# 2. Fetch real evidence (needs NCBI + LLM keys in .env)
python scripts/fetch_pubmed.py --max-pairs 40
python scripts/build_real_evidence.py

# 3. Build validation sets + run baselines + evaluate
python scripts/generate_cases.py --target 400
python scripts/run_baselines.py
python scripts/run_multiseed.py --seeds 5
python scripts/evaluate.py

# 4. Generate figures/tables
python scripts/generate_paper_figures.py
python scripts/generate_paper_tables.py
```

## Interactive Demo (Streamlit)

```bash
pip install -e ".[streamlit]"
streamlit run app/streamlit_app.py
```

Then open http://localhost:8501.

> ⚠️ The demo is for clinical decision support only and does not replace clinician or pharmacist judgement.

## Target Output

- Reproducible Python package with ~80% code reuse from TongYuan
- Validated LightRAG混合决策支持系统:患者临床情境×穿刺决策项 screening system (4-phase validation)
- Manuscript submitted to *European Urology Open Science* (or fallback journal)

## License

For peer review and academic reproducibility. All data derived from publicly available sources.
