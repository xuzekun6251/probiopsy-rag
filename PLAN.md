# 前列安汇（probiopsy-rag）LightRAG混合决策支持系统:患者临床情境×穿刺决策项 Agent — 完整执行方案

> **项目代号**：probiopsy-rag / 前列安汇
> **方法学骨架来源**：TongYuan (FDI screening, *Nutrients* submission) — 80% 代码复用
> **创建日期**：2026-09-13
> **目标期刊**（一志愿）：*European Urology Open Science*；备选：*Journal of Medical Internet Research*, *BJU International*
> **预计工作量**：10 周（含数据构建、验证、写作）
> **当前状态**：📋 规划中（PLAN.md 由 medical-agent-planner 生成，等待 coding agent 启动 Phase 0）

---

## 0. 文档使用说明

本文档是 **从零到投稿** 的执行蓝图。每个任务都给出：
- **执行内容**：做什么
- **验收标准（verify）**：怎样算完成
- **Subagent 策略**：是否并行、用哪类 subagent
- **依赖任务**：必须先完成哪些前置

> **执行入口**：按 §9 任务清单顺序执行。Phase 0 全部顺序执行（小任务），Phase 1 启动 3 个并行 Explore subagent（entities_a / entities_b / evidence），完成后 Claude 整合 → Phase 2 顺序 → Phase 3 单 Agent → Phase 4 并行启动 3 个 Explore subagent → Phase 5 由 Claude 主导 → Phase 6 单 Agent → Phase 7 由 Claude + 用户协作 → Phase 8 投稿。

---

## §X. Literature Landscape & Feasibility (Phase 2 输出)

> 本节由 medical-agent-planner Phase 2 (online validation) 于 2026-09-13 联网验证后填写。

### X.1 研究前景（Research Prospect）

- **方向**：前列腺穿刺活检全流程标准化 + LLM/RAG 决策支持
- **领域热度**：AI×前列腺穿刺活检为当前热点——BMJ 2025 发表首项 AI 辅助前列腺 MRI 判读 RCT（未辅助阅片漏诊 20% csPCa vs AI 辅助 8.9%）；JAMA Network Open 2025 实时并发阅片研究；Eur Urol Focus 2025 bpMRI AI 判读诊断准确性研究
- **LLM×指南方向**：UroBot 研究（Eur Urol Focus 2025, PMID 39914758, DOI 10.1016/j.euf.2025.101766）显示 GPT-4 在 EAU 指南问题上准确率 76.0%，仍低于人类泌尿外科医生（79.3%，p=0.031）——纯 LLM 不足以满足临床标准，为"规则+KG-RAG+LLM 混合架构"留下明确空间；GPT-4o 在 640 道 EAU 自测题约 80%（差距在缩小，方法学窗口期存在）
- **在研试验**：GAITeR（ISRCTN68770080，AI 引导经会阴靶向穿刺）、ART（ISRCTN12160772，AI 辅助 MRI 阅片）
- **判定**：**strong**

### X.2 数据可及性（Data Availability）

| 数据源 | 类型 | 覆盖实体 | 可访问性 | 备注 |
|---|---|---|---|---|
| ProBIOPSY 共识主文 + mmc1（37 页） | 共识声明 + 投票结果 | both | ✅ 已在本地（CC BY 开放获取, Eur Urol 2026） | 36 stems / 96 条声明 / 34 国专家三轮 Delphi / 改良 RAND 法；29/36 stems 达成共识 |
| EAU Prostate Cancer Guidelines 2026 | 指南 PDF | both | ✅ 已验证可下载（uroweb.org） | 2026 为 2025 有限更新，含 micro-US 穿刺指征新章节；A 级证据 |
| AUA/SUO Prostate Cancer Guideline | 指南网页/PDF | both | ✅ 公开（auanet.org） | B 级证据 |
| NICE NG131 | 指南网页 | both | ✅ 公开（nice.org.uk） | B 级证据 |
| PubMed 文献池（2015–2026） | 摘要 API | both | ✅ 公开 E-utilities（bio-entrez 批量抓取） | 靶向穿刺/系统穿刺/PI-RADS 检索式，C/D 级证据 |

**综合判定**：**strong**（全部数据源公开可及，核心金标准语料已在本机）

### X.3 同类工作对比（Prior Art）

| 系统 | 年份 | 出处 | 性质 | 局限 | 本项目填补的空白 |
|---|---|---|---|---|---|
| RAG vs. GraphRAG 泌尿评测（PERICLES Group, arXiv:2506.13674） | 2025 | arXiv | RAG 方法基准评测（LightRAG/naive RAG/GraphRAG/pgvector，SUO 指南答题） | 仅 QA 评测，无规则引擎、无可执行决策输出、无共识金标准验证、非活检流程 | 首个**决策支持系统**（非 QA）+ 声明级保真度验证；LightRAG 在其评测中速度/成功率最佳，支撑选型 |
| UroBot（arXiv 及 Eur Urol Focus 2025, PMID 39914758） | 2025 | Eur Urol Focus | 纯 LLM vs 泌尿医生答题对比 | 无检索增强、无知识溯源、准确率低于人类专家 | 混合架构可解释、可溯源，目标超越纯 LLM 基线 |
| MedGraphRAG | 2024 | arXiv | 通用医疗图 RAG QA | 通用医学问答，非外科操作流程 | 聚焦穿刺活检全流程（影像→指征→方案→并发症→治疗规划） |
| GraphRAG（Microsoft）/ LightRAG（HKUDS, arXiv:2410.05779） | 2024 | arXiv | 通用图 RAG 框架 | 非医疗专用 | 作为本项目 LightRAG 底座（非竞争关系） |
| AI×前列腺 MRI 判读系列（BMJ 2025 RCT 等） | 2024–2025 | BMJ/JAMA/EUF | 影像 AI 判读 | 仅影像环节，不覆盖活检决策全链路 | 本项目覆盖影像之后的完整决策链 |

**判定**：**clear_gap**（检索增强泌尿 QA 已有工作，但"规则引擎+LightRAG+LLM 仲裁"三混合架构用于外科操作流程标准化决策、并以 96 条国际共识声明做声明级保真度验证的工作未见先例。注意：论文中不可声称"首个 LightRAG 泌尿应用"，需正面引用 arXiv:2506.13674 并明确定位差异）

### X.4 期刊适配（Journal Fit）

| 期刊 | IF（约） | 适配判定 | 近 24 月类似文章 |
|---|---|---|---|
| European Urology Open Science | ~4-6 | **fit（一志愿）** | Kasivisvanathan et al. 2024 "AI in Prostate MRI Quality, Interpretation, and Targeted Biopsy"（S2588931124000191）；ProBIOPSY 共识母刊 Eur Urol 同门 |
| Journal of Medical Internet Research | ~5-8 | fit | AI/LLM 临床决策支持系统论文常规接收 |
| BJU International | ~4-5 | fit（备选） | Paolone et al. 2025 AI in urological malignancies narrative review（10.1111/bju.70026） |
| Eur Urol Focus | ~4-6 | 潜在备选 | UroBot 研究（10.1016/j.euf.2025.101766） |

**投稿策略**：一志愿 European Urology Open Science（与 ProBIOPSY 同属 EAU 期刊家族、共识声明验证直接契合其读者群）→ 二志愿 JMIR（方法学叙事更强）→ 三志愿 BJU International。

**四项判定汇总**：前景 strong / 数据 strong / 先例 clear_gap / 期刊 fit → ✅ Phase 2 通过，可进入 Phase 3/4

---

## 1. 项目定位与差异化

### 1.1 一句话定位

**前列安汇 是adult_men_with_suspected_prostate_cancer的LightRAG混合决策支持系统:患者临床情境×穿刺决策项决策支持系统**：通过indication_matching, imaging_pathway_selection, biopsy_scheme_selection, perioperative_management, complication_risk_management, treatment_planning_linkage机制规则 + 图组织证据检索，在 50+ 患者临床情境要素 × 40+ 穿刺决策项 的所有组合上，提供可追溯、可解释的安全性/推荐性分级报告。

### 1.2 与参考项目的差异（防 Salami-Slicing）

| 维度 | 参考项目 | 本项目 |
|---|---|---|
| 实体 A | food | 患者临床情境要素 |
| 实体 B | drug | 穿刺决策项 |
| 相互作用类型 | FDI | indication_matching, imaging_pathway_selection, biopsy_scheme_selection, perioperative_management, complication_risk_management, treatment_planning_linkage |
| 规则数 | 15 | 12 |
| 数据源 | FDA + USDA + LiverTox | ProBIOPSY consensus main text + mmc1 supplementary, EAU Prostate Cancer Guidelines (biopsy chapter), AUA/SUO Prostate Cancer Guideline (2023/amended), NICE NG131 Prostate Cancer |
| 文化/临床故事 | 药食同源 + 全球化营养学 | 方法学创新(首个面向外科操作标准化的规则+LightRAG+LLM混合架构)+领域首创(前列腺穿刺全流程知识图谱:影像-指征-方案-并发症-治疗规划一体化)+临床验证强度(96条共识声明还原度+专家盲评+4基线消融) |
| 目标期刊 | Nutrients | European Urology Open Science |
| 患者人群 | general + high-risk subgroups | mri_visible_lesion, mri_indeterminate, prior_negative_biopsy, anticoagulated, focal_therapy_candidate |

**审稿人最可能问的差异化问题**：与已有LightRAG混合决策支持系统:患者临床情境×穿刺决策项工作有何不同？ → 答案：方法学创新(首个面向外科操作标准化的规则+LightRAG+LLM混合架构)+领域首创(前列腺穿刺全流程知识图谱:影像-指征-方案-并发症-治疗规划一体化)+临床验证强度(96条共识声明还原度+专家盲评+4基线消融)

### 1.3 核心创新点（Highlights 草案）

1. 首个针对该 A×B 组合的系统化筛查工具
2. 12+ 条确定性规则，覆盖多类机制
3. 规则 + 图检索的混合架构，可解释、非黑箱
4. 方法学创新(首个面向外科操作标准化的规则+LightRAG+LLM混合架构)+领域首创(前列腺穿刺全流程知识图谱:影像-指征-方案-并发症-治疗规划一体化)+临床验证强度(96条共识声明还原度+专家盲评+4基线消融)
5. 四阶段验证（规则一致性 → 文献 → 临床 → 专家盲法）

---

## 2. 方法学设计

### 2.1 整体架构（复用 TongYuan 流水线）

```
用户输入（患者临床情境要素 + 穿刺决策项 + 患者因素）
  → 实体归一化（normalize.py）
  → 规则引擎风险评估（risk_rules.py + rules.yaml）
  → LightRAG 图组织证据检索（lightrag_adapter.py）
  → 证据压缩（top-k + 字符上限）
  → 结构化安全报告生成（report.py）
  → 验证 / 专家盲评导出
```

### 2.2 与 TongYuan 代码复用率

| 模块 | TongYuan 源文件 | 复用程度 | 修改要点 |
|---|---|---|---|
| 数据模型 | `schemas.py` | 90% | `Food` → `PatientClinicalScenario`；字段定制 |
| 归一化 | `normalize.py` | 80% | 扩展别名表 |
| 规则引擎 | `risk_rules.py` | 95% | YAML 配置不同，逻辑零改动 |
| Evidence Store | `evidence_store.py` | 85% | 同 TongYuan |
| LightRAG Adapter | `lightrag_adapter.py` | 95% | 仅索引内容不同 |
| Naive RAG | `naive_rag.py` | 95% | 同上 |
| Safety Agent | `safety_agent.py` | 85% | 入口字段重命名 |
| 报告生成 | `report.py` | 80% | 提示词模板改写 |
| Streamlit | `streamlit_app.py` | 70% | UI 文案、导航 |

**总复用率：约 80%。新增工作集中在：数据构建、规则 YAML、UI 调整、论文写作。**

---

## 3. 知识库构建计划

### 3.1 EntityA 实体注册表（目标 50+ 条）

**结构**（`data/seed/entities_a.csv`）：

```csv
patient_clinical_scenario_id,patient_clinical_scenario_name,aliases,category,active_mechanisms,flags,evidence_sources


```

**实体来源**：

| 类别 | 数量 | 数据源 |
|---|---:|---|
| 主名录 | 50 | ProBIOPSY 36 stems + EAU/AUA guidelines risk factors + PI-RADS v2.1 lexicon |
| 补充名录 | — | TBD |
| **合计目标** | **≥ 50** | — |

**字段标准**：`flags` 命名遵循 snake_case，从 `domain_playbooks.md` 对应 playbook 的 flag catalog 选取。

### 3.2 EntityB 实体注册表（目标 40+ 条）

（同上结构，`data/seed/entities_b.csv`）

### 3.3 Evidence Base（目标 250+ 条）

**结构**（`data/seed/evidence_chunks.jsonl`）：复用 TongYuan `EvidenceChunk` schema。

**来源优先级**：
1. **Level A**（最高）：监管标签（FDA / NMPA）
2. **Level B**：LiverTox / NCCIH / EFSA
3. **Level C**：PubMed RCT 与系统综述
4. **Level D**：体外 PK 研究
5. **Level E**：病例报告

**PubMed 检索词模板**：
- `("{{direction_keyword_en}" OR variants) AND (warfarin, statin, ...)`
- 中文文献：CNKI / 万方（手工补 20–30 篇）

---

## 4. 规则引擎设计（12 条候选规则）

> 风格与 TongYuan `configs/rules.yaml` 完全一致，YAML 配置，引擎代码零改动。

### 4.1 规则列表（草稿，需 Phase 2 后最终确定）

| # | 规则 ID | 严重度 | 机制 | 触发条件 |
|---:|---|---|---|---|
| 1 | cyp3a4_inhibition | high | pharmacokinetic | entity_a: cyp3a4_inhibitor × entity_b: cyp3a4_substrate |
| ... | | | | |

（完整规则见 `configs/rules.yaml` 与 `docs/rule_rationale.md`）

### 4.2 患者因素规则

- `liver_disease`：与 hepatotoxic 实体叠加升级
- `elderly`：≥ 65 岁，high 风险信号维持
- ...

### 4.3 规则 YAML 示例

见 `configs/rules.yaml`（scaffold 后生成骨架）。

---

## 5. 基线对比设计

完全复用 TongYuan `run_baselines.py` 的四档对照：

| 方法 ID | 描述 |
|---|---|
| `pure_llm` | 无检索，直接问 LLM |
| `naive_rag` | 关键词检索 + LLM |
| `lightrag` | LightRAG 图索引（无规则） |
| `probiopsy-rag` | **完整系统**：规则 + LightRAG + 报告 |

**核心对比指标**（5 项）：
1. High-risk sensitivity
2. High-risk specificity
3. F1
4. Exact 4-level accuracy
5. Cohen's κ

加上检索效率指标：context char count、evidence chunks retrieved、expert Likert。

---

## 6. 验证设计（四阶段）

详见 medical-agent-planner `references/validation_design.md`。

### Phase 1：规则一致性测试（n = 400）

**验收**：完整系统在 cases 上达成 100% 一致。

### Phase 2：文献回顾验证（n = 200）

**分配**：High 80 / Medium 60 / Low 50 / Unknown 10

**验收**：sens ≥ 0.70，spec ≥ 0.60，4-level ≥ 0.50。

### Phase 3：临床回顾验证（n = 0）

**关键协作**：复用既有临床合作伙伴

**验收**：sens ≥ 0.70，spec ≥ 0.80。

### Phase 4：盲法专家评估（n = 8 cases × 3 experts）

**验收**：系统-专家 κ ≥ 0.6；Fleiss κ ≥ 0.6。

---

## 7. 项目结构

```
<project_root>/
├── README.md
├── PLAN.md                         # 本文档
├── pyproject.toml
├── .gitignore
├── .env.example
├── .planner.config.json            # Phase 1 调研输出（scaffold 已生成）
│
├── src/probiopsy_rag_agent/           # 核心包
│   ├── __init__.py
│   ├── schemas.py
│   ├── normalize.py
│   ├── risk_rules.py
│   ├── evidence_store.py
│   ├── lightrag_adapter.py
│   ├── naive_rag.py
│   ├── llm_client.py
│   ├── safety_agent.py
│   └── report.py
│
├── configs/
│   ├── rules.yaml                  # 规则配置
│   ├── prompts.yaml
│   └── settings.example.yaml
│
├── data/
│   ├── raw/
│   ├── seed/
│   │   ├── entities_a.csv
│   │   ├── entities_b.csv
│   │   ├── evidence_chunks.jsonl
│   │   ├── interactions_gold.jsonl
│   │   └── interactions_layer1_literature.jsonl
│   └── processed/lightrag_index/
│
├── scripts/
│   ├── build_entity_a_registry.py
│   ├── build_entity_b_registry.py
│   ├── fetch_pubmed.py
│   ├── build_evidence_base.py
│   ├── build_lightrag_index.py
│   ├── generate_cases.py
│   ├── run_baselines.py
│   ├── run_multiseed.py
│   ├── evaluate.py
│   ├── generate_paper_figures.py
│   ├── generate_paper_tables.py
│   └── run_demo_cases.py
│
├── app/streamlit_app.py
│
├── tests/
│   ├── test_normalize.py
│   ├── test_risk_rules.py
│   ├── test_evidence_store.py
│   └── test_integration.py
│
├── outputs/
│   ├── figures/
│   ├── tables/
│   ├── paper/
│   └── baseline_predictions.jsonl
│
└── docs/
    ├── data_sources.md
    └── rule_rationale.md
```

---

## 8. 数据源清单（带访问方法）

> 详见 §X.2 数据可及性表的填充版本。每条数据源记录：类型、用途、访问方式、国内镜像、备选。

| 数据源 | 类型 | 用途 | 访问方式 | 国内镜像 |
|---|---|---|---|---|
| TBD | ... | ... | ... | ... |

---

## 9. 详细任务清单（可执行块）

> 每个 Phase 内的任务尽可能并行；Phase 之间一般有依赖。

### Phase 0：项目初始化（预计 0.5 天）

- [ ] **T0.1** 在 `<project_root>` 初始化 git 仓库
  - verify: `git status` 显示 main 分支
- [ ] **T0.2** 编写 `pyproject.toml`、`.gitignore`、`.env.example`、`README.md`（scaffold 已生成骨架）
  - verify: `pip install -e .` 成功
- [ ] **T0.3** 复制 TongYuan `src/tongyuan_agent/*.py` → `src/probiopsy_rag_agent/*.py`，全局替换命名
  - verify: `python -c "import probiopsy_rag_agent"` 不报错
- [ ] **T0.4** 运行 `pytest` 确认基线测试通过
  - verify: 所有测试通过

### Phase 1：知识库构建（预计 1.5–2 周，**最大瓶颈**）

**并行 Subagent 任务**：

- [ ] **T1.1** 构建 `data/seed/entities_a.csv`（50+ 条）
  - **Subagent A1（Explore）**：调研 ProBIOPSY 36 stems + EAU/AUA guidelines risk factors + PI-RADS v2.1 lexicon
  - **Subagent A2（Explore）**：调研 TBD
  - **Subagent A3（编码）**：合并为 CSV，手工标注 flags
  - verify: `wc -l data/seed/entities_a.csv ≥ 50`

- [ ] **T1.2** 构建 `data/seed/entities_b.csv`（40+ 条）
  - 同 T1.1 模式

- [ ] **T1.3** 构建 `data/seed/evidence_chunks.jsonl`（250+ 条证据）
  - **Subagent C1（Explore）**：PubMed E-utilities 检索
  - **Subagent C2（Explore）**：FDA DailyMed 抓取
  - **Subagent C3（Explore）**：LiverTox / NCCIH 抓取
  - verify: 证据级别分布合理；至少 50 条 Level A/B

### Phase 2：规则引擎（预计 3 天）

- [ ] **T2.1** 编写 `configs/rules.yaml`（12 条规则 + 患者因素规则）
  - **Subagent D（Explore）**：为每条规则检索 2–3 篇 PubMed 支持文献
  - verify: YAML 合法；每条规则至少有 1 篇文献支持
- [ ] **T2.2** 运行规则引擎单元测试
  - verify: `pytest tests/test_risk_rules.py` 通过
- [ ] **T2.3** 编写 `docs/rule_rationale.md`
  - verify: 文档完整覆盖所有规则

### Phase 3：检索与基线（预计 1 周）

- [ ] **T3.1** 构建 LightRAG 索引
  - verify: `data/processed/lightrag_index/` 含完整 KV stores
- [ ] **T3.2** 实现四档基线
  - verify: 四种方法在 5 个示例 case 上都能输出报告
- [ ] **T3.3** Naive RAG 测试
  - verify: 经典 high-risk case 能召回关键证据

### Phase 4：验证集构建（预计 1 周）

- [ ] **T4.1** Phase 1 验证集：脚本枚举生成 cases
- [ ] **T4.2** Phase 2 验证集：文献派生 cases
- [ ] **T4.3** Phase 3 临床协作入组（**最早启动，异步进行**）
- [ ] **T4.4** Phase 4 专家盲评包导出

### Phase 5：评估与论文图（预计 1 周）

- [ ] **T5.1** 运行 `scripts/evaluate.py`，输出性能矩阵
- [ ] **T5.2** 生成论文图（架构、性能、检索效率、专家一致性、Demo、推理轨迹）
  - **调用 `nature-figure` skill**，按 **`outputs/figures/contracts/figure{1-5}_*.yaml`** 中的 contract 生成。Contract 由 scaffold 自动 emit（Python backend，NMI pastel palette，600 dpi，SVG+PDF+TIFF+PNG，可编辑文本）。
  - **5 张标准图**：
    - Figure 1 — 系统架构（`schematic_led_composite`）
    - Figure 2 — 性能多 seed（`quantitative_grid`，forest + 混淆矩阵 + metric bar + 效率散点）
    - Figure 3 — 专家一致性（`quantitative_grid`，Fleiss κ + system-vs-expert heatmap + Likert）
    - Figure 4 — Demo case 报告（`image_plate_plus_quant`，input + rules + evidence pyramid + traceability）
    - Figure 5 — 推理轨迹（`schematic_led_composite`，swim-lane + latency + KG path network）
  - 每张图必须附 `outputs/figures/source_data/figure{N}_*.csv`（YAML contract 中已声明 schema）
  - 后端锁定 **Python**（matplotlib + seaborn + networkx），不混用 R
  - 配色锁定 **NMI pastel**（色盲安全，CMYK 友好）
  - verify: `ls outputs/figures/figure{1-5}_*.{svg,pdf,tiff,png}` 共 20 个文件
- [ ] **T5.3** 生成论文表（注册表、规则、性能、验证分布）

### Phase 6：交互式界面（预计 2–3 天）

- [ ] **T6.1** 复用并改写 TongYuan `streamlit_app.py`
  - verify: `streamlit run app/streamlit_app.py` 启动；demo case 返回正确报告

### Phase 7：论文写作（预计 2–3 周）

> **Nature skill 编排**：本阶段大量调用 `nature-*` skill 完成 Nature 风格稿件生产。

- [ ] **T7.1** 论文大纲（IMRaD）—— 用 `nature-writing` 选定 article architecture
- [ ] **T7.2** Methods —— 用 `nature-writing` 起草，复用 TongYuan 方法节，按域改写
- [ ] **T7.3** Results（基于 Phase 5 数据）—— 用 `nature-writing` evidence ladder
- [ ] **T7.4** Introduction —— 用 `nature-citation` 给段落补 CNS 引用 backbone；用 `nature-reader` 深读 3–5 篇 cornerstone 引用做中英对照
- [ ] **T7.5** Discussion —— 用 `nature-writing` 中心贡献 + 证据意义 + 与前人关系 + 限制 + 未来
- [ ] **T7.6** 每节定稿后用 `nature-polishing` 润色（含中文初稿翻译）
- [ ] **T7.7** Data Availability 节用 `nature-data` 起草（GitHub + Zenodo + 数据源 + LLM provider）
- [ ] **T7.8** Highlights + Graphical Abstract + Cover Letter
- [ ] **T7.9** Supplementary

### Phase 8：投稿准备（预计 3–5 天）

- [ ] **T8.1** 按目标期刊格式调整
- [ ] **T8.2** 参考文献整理（Vancouver / Harvard / MDPI）—— 用 `nature-academic-search` 验证 DOI 和元数据
- [ ] **T8.3** GitHub 仓库整理 + Zenodo DOI
- [ ] **T8.4** Cover letter + CRediT + 数据可用性声明（T7.7 已起草）

### Phase 9：修回（投稿后，预计 1–4 周，按 major/minor revision 决定）

> **Nature skill 编排**：用 `nature-response` 处理 editor decision letter。

- [ ] **T9.1** 解析 editor decision letter + reviewer comments，建立 R1.1/R1.2/R2.1 编号
- [ ] **T9.2** 用 `nature-response` 起草逐点回复（response strategy + tracker table + draft letter）
- [ ] **T9.3** 按回复信承诺修改 manuscript，记录 line/figure/table 变更
- [ ] **T9.4** 补做 reviewer 要求的实验/分析（如适用）；不能做的标 `AUTHOR_INPUT_NEEDED`
- [ ] **T9.5** 重投 + 更新 cover letter

### Phase 10（可选）：会议汇报

- [ ] **T10.1** 用 `nature-paper2ppt` 把 manuscript 转成中文 PPTX（12–16 页，16:9）
- [ ] **T10.2** QA report + asset manifest

---

## 10. Subagent 并行策略

### 10.1 Subagent 类型选择

| 任务 | Subagent 类型 | 数量 | 并行度 |
|---|---|---:|---|
| 文献调研（数据库/监管源/政策） | `Explore` | 4–6 | 高 |
| 数据抓取与整合 | `Explore` + 编码 | 2–3 | 中 |
| 代码迁移与改写 | 默认（编码） | 1 | 低（顺序） |
| 规则依据文献检索 | `Explore` | 1 | 中 |
| 验证用例构建 | `Explore` | 3 | 高 |
| 论文章节撰写 | 默认 | 1（顺序） | 低 |

### 10.2 关键并行机会

**机会 1：知识库三件套同时构建**（Phase 1）
**机会 2：四档基线 + 评估流水线**（Phase 3 完成后）
**机会 3：论文章节并行初稿**（Phase 5 完成后）

---

## 11. 时间线（乐观估计）

| 周 | 主要工作 |
|---:|---|
| 1 | Phase 0 + Phase 1 启动 |
| 2 | Phase 1 完成 + Phase 2 规则 |
| 3 | Phase 3 检索与基线 |
| 4 | Phase 4 验证集构建 |
| 5–6 | Phase 5 评估 + Phase 6 Streamlit |
| 6 | **联系临床团队启动 Phase 3 临床病例收集**（异步） |
| 7–9 | Phase 7 论文写作 |
| 10 | Phase 8 投稿准备 |
| 11–11 | 内审 + 投稿 |

**关键路径**：Phase 1（数据）→ Phase 3（检索）→ Phase 5（评估）→ Phase 7（写作）。
**异步任务**：Phase 4.3 临床病例收集（最长，需 IRB + 临床团队配合，应最早启动）。

---

## 12. 目标期刊与投稿策略

### 12.1 一志愿：*European Urology Open Science*

**适配理由**：
- 主题范围包含该研究方向
- 接受方法学 + 决策支持系统类稿件

**Special Issue 关注**：留意相关专刊征稿

### 12.2 备选

| 期刊 | IF | 适配点 | 风险 |
|---|---:|---|---|
| Journal of Medical Internet Research | TBD | TBD | TBD |

### 12.3 投稿顺序策略

1. 投 *European Urology Open Science* → 若 reject 转 *Journal of Medical Internet Research*
2. 若再 reject → *BJU International* 兜底

---

## 13. 风险与缓解

| 风险 | 概率 | 缓解 |
|---|---|---|
| 主名录数据获取难 | 中 | 多源核对（监管公告 + 已发表论文） |
| 临床病例收集周期长 | ... | ... |
| 临床病例收集周期长（IRB + 协调） | 高 | 尽早启动；先用文献验证支撑投稿 |
| 与已有工作重复 | 中 | Introduction 明确区分；规则、数据、目标人群全不同 |
| PubMed 检索召回率低 | 低 | 与文献管理员合作；中英文双查 |
| LightRAG 索引内存不足 | 低 | 复用 TongYuan 索引配置；分批构建 |
| 专家盲评协调难 | 低 | 复用既有专家网络 |

---

## 14. 执行入口

**Claude 开始执行时的标准流程**：

```
1. 读取本 PLAN.md（已完成）
2. 检查 git status & 当前文件树
3. 按 Phase 顺序执行（见 §0 与 §9）
4. 每完成一个 Phase 更新 TodoWrite
5. 关键节点（如数据构建完成、评估完成）通知用户确认
```

**Claude 启动命令**（用户在与 Claude 的下一轮对话时使用）：

> 请按 `<project_root>/PLAN.md` 执行 Phase 0，然后启动 Phase 1 的三个并行 subagent。

或更精细：

> 请执行 `<project_root>/PLAN.md` 的 T0.1–T0.4，verify 全部通过后停下来等我审查。

---

## 15. 附录：关键文件草稿

### 15.1 `pyproject.toml`

见 scaffold 生成的实际文件。

### 15.2 实体清单采样（写入 README）

（待 Phase 1 完成后填充）

### 15.3 论文标题（候选）——Writer 阶段已定稿

1. **QianLieAnHui: development and benchmark validation of a hybrid rule-engine, knowledge-graph, and LLM-arbitration decision-support system for the prostate biopsy pathway, against the ProBIOPSY international consensus**（主选，中文题见 outputs/paper/00_front_zh.md）
2. Architecture, not model scale: a rule-gated LightRAG decision-support system validated statement-by-statement against the ProBIOPSY consensus (112 statements)
3. Safe vetoing with full traceability: hybrid rule engine + knowledge-graph retrieval + LLM arbitration for prostate biopsy decisions

---

**PLAN.md v1.0 — 2026-09-13**（由 medical-agent-planner skill 生成）

---

## 16. 执行日志 / Progress Log

| 日期 | 事件 | 操作者 |
|---|---|---|
| 2026-09-13 | PLAN.md v1.0 创建，项目立项 | medical-agent-planner skill |
| 2026-09-13 | **LLM 模型别名记录**:DeepSeek 官方公告——旧 API 模型名 `deepseek-v4-flash`(及 `deepseek-v4-flash-vision-exp`)仍可调用,但底层模型已下线,请求实际由 **DeepSeek-V4.1-Flash** 提供服务。故本项目 `.env`/`.planner.config.json` 中保留 `HUANYU_BULK_MODEL=deepseek-v4-flash`(别名调用,零风险),**论文 Methods 写法应为:"DeepSeek-V4.1-Flash (accessed via API alias `deepseek-v4-flash`, September 2026)"**。若 DeepSeek 未来移除别名导致调用失败,将 API 模型名替换为其官方文档中的现行 ID 后重试即可。Executor Phase 0 API 冒烟测试时应从响应头/响应体确认实际服务模型并回填本表 | medical-agent-planner skill |
| 2026-09-13 | Planner 阶段(Phase 0–4.5)完成:配置 3/3 验证通过、脚手架生成、.venv 环境就绪(Python 3.13.7 + lightrag-hku 1.5.7)、10 份伦理文档、5 个图表契约、planner→executor 交接验证 OK | medical-agent-planner skill |
| 2026-09-13 | **Chat LLM 切换为智谱 GLM-5.3**:`.env`/`.env.example` 中 `HUANYU_BULK_MODEL=glm-5.3`、`HUANYU_BULK_BASE_URL=https://open.bigmodel.cn/api/paas/v4`、`HUANYU_BULK_MAX_TOKENS` 1024→4096(GLM-5.3 混合推理架构,预留 thinking tokens 空间);`.planner.config.json` 同步 `llm_provider=zhipu` + `custom_chat` 启用。`llm_client.py` 为通用 OpenAI 兼容客户端,零代码改动。**Embedding 保持火山方舟 doubao-embedding-vision-251215 不变**(`ArkVisionEmbedding` 专用客户端)。**论文 Methods 写法:"Zhipu GLM-5.3 (OpenAI-compatible API, https://open.bigmodel.cn/api/paas/v4, September 2026) for entity extraction and arbitration; doubao-embedding-vision-251215 (dim=2048) for LightRAG vector index"**。注意:GLM 模型 ID 必须小写(错误 1211) | medical-agent-planner skill |
