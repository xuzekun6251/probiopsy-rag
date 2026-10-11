"""Assemble outputs/paper/manuscript.md from the numbered section files.

Back-matter (funding / COI / CRediT / repo links) is filled from
configs/author_info.yaml so the zh manuscript stays in sync with the en one.
"""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "outputs" / "paper"

info = yaml.safe_load((ROOT / "configs" / "author_info.yaml").read_text(encoding="utf-8")) or {}
pi = info.get("pi") or {}
coauthors = info.get("coauthors") or []
funding_zh = (info.get("funding") or {}).get("zh") or "[TODO]"
coi_zh = (info.get("coi") or {}).get("zh") or "[TODO]"
repo = info.get("github_repo") or "[GitHub 仓库地址待发布后回填]"
doi = info.get("zenodo_doi") or "[Zenodo DOI 待发布后回填]"

credit_pi = (pi.get("name_zh") or "[PI TODO]") + "：概念化、方法学、软件、验证、初稿撰写"
credit_lines = [credit_pi] + [
    f'{co.get("name_zh") or co.get("name_en", "[合作者]")}：{co.get("contribution", "写作——审阅与修改")}'
    for co in coauthors]

parts = [
    P / "00_front_zh.md",
    P / "03_introduction.md",
    P / "01_methods.md",
    P / "02_results.md",
    P / "04_discussion.md",
    P / "05_limitations.md",
    P / "06_conclusion.md",
]
blocks = []
for f in parts:
    blocks.append(f.read_text(encoding="utf-8").strip())

tail = f"""

---

## 数据与代码可用性 (Data Availability)

规则库（configs/rules.yaml）、双实体注册表（data/seed/entities_a.csv, entities_b.csv）、证据块库（data/seed/evidence_chunks.jsonl，357 条）、患者教育事实库（data/seed/patient_education_facts.csv，10 条逐项可溯源）、患者教育逐字咨询记录（outputs/demo_cases/patient_edu/）、金标准标注（data/seed/probiopsy_statements.csv，112 条）、全部 2,240 条原始预测记录（outputs/baseline_predictions.jsonl，含每次运行的上下文字符数与检索块数）、旗舰档补充数据（outputs/baseline_predictions_glm53.jsonl）、评估脚本（scripts/evaluate.py）与图表源数据（outputs/figures/source_data/）随代码仓库发布：{repo}（Zenodo 归档：{doi}）。

## 伦理声明 (Ethics)

本研究的计算评估不涉及患者数据或生物样本：知识库语料与验证金标准均来自公开出版的 ProBIOPSY 共识，演示病例为合成情境；四专家盲评为匿名、自愿参与，不含任何可识别个人信息。详见 Manuscript_Ethics_Statement.md。

## 资金 (Funding)

{funding_zh}

## 利益冲突 (Conflict of Interest)

{coi_zh}

## 作者贡献 (CRediT)

{chr(10).join(f"- {ln}" for ln in credit_lines)}

## 图表清单

- **图 1** 系统架构（outputs/figures/figure1_architecture.*）
- **图 2** 多方法多种子性能对比（outputs/figures/figure2_performance.*）
- **图 3** 四专家盲评一致性（outputs/figures/figure3_expert_agreement.*）
- **图 4** 演示病例报告（outputs/figures/figure4_demo_case.*）
- **图 5** 推理链追踪（outputs/figures/figure5_reasoning_trace.*）
- **表 1** 双实体注册表摘要（outputs/tables/table1_registry.md）
- **表 2** 规则清单（outputs/tables/table2_rules.md）
- **表 3** 性能矩阵（outputs/tables/table3_performance.md）
- **表 4** 金标准领域×动作分布（outputs/tables/table4_validation.md）

## 图注 (Figure legends)

**图 1** 系统架构与基准设计。ProBIOPSY 共识语料（112 条终版陈述、357 个证据块、LightRAG 索引 1,864 实体/3,078 关系）在构建期蒸馏为 16 条确定性规则与检索索引。运行时，患者情境×决策项查询依次经过：(1) 输出 Q 编号硬约束的确定性规则引擎（虚线箭头绑定仲裁器）；(2) LightRAG 知识图谱与词法证据库融合的风险引导检索；(3) 在硬约束解码下输出带陈述级引用的五类动作裁决的 LLM 仲裁器（GLM-5.3）。图中给出示例查询（局灶治疗计划下的限局性 PI-RADS 4 病灶）与对应的结构化输出。管线之下为第二个运行模式条带：患者教育复用同一冻结证据库，患者的通俗提问经关键词匹配到含 10 个条目、逐项可溯源的策展事实库，同一生成器产生带"何时须就医"安全网段落并引导回主管医生的通俗回答（定性演示，不属于基准评测）。底部条带：多方法多种子基准（112 条陈述 × 4 方法 × 5 种子 = 2,240 次运行，生成器固定）。

**图 2** 多种子基准（4 方法 × 5 种子 × 112 条陈述）。(a) 各方法核心指标（5 种子 mean±SD）：exact-5、exact-3、macro-F1、Cohen's κ 与 against 类 F1；(b) 各种子的 exact-5（点，虚线为均值）；(c) 各方法 560 次运行的预测类别分布（柱）与金标准分布（菱形）：检索基线几乎不输出 conditional，完整系统的分布最贴近金标准。

**图 3** 四专家对五个演示病例（组合命题）的盲评。(a) 各病例的专家间一致率（4 专家中众数评分占比；虚线 = 3/4）；Fleiss κ = −0.09（标 *）为小样本伪影，原始一致率 17/20；(b) 各病例各专家的评分（End = endorse，EndO = endorse_option，Cond = conditional，RepO = report_option，Aga = against）；System 列为系统裁决，在 4 个有多数票的病例中均与专家多数一致，case1 为 2:2 平票（按预设规则不计入）；(c) 专家对系统输出的 Likert 评分（清晰度、有用性、认可度、证据充分性；一致 5 分，触顶）。

**图 4** 演示病例。(a) 各病例触发的共识规则数，柱色与标注为该病例的裁决动作；(b) 证据语料构成（文献条目 C 218、共识陈述 B 112、共识叙述 20、系统综述摘要 7，共 357 块）。

**图 5** 运行时与知识图谱统计。(a) 各演示病例的决策通过时延（对数轴）：规则引擎层（蓝）与检索加仲裁（黄）；(b) 最强知识图谱关系：按边权重排序的前 12 条（共 3,078 条边）。

**表 1** 双实体注册表的条目数、标志位数与类别分布；完整注册表见 data/seed/entities_a.csv 与 entities_b.csv。

**表 2** 16 条规则（12 条共识规则 + 4 条患者因素升级规则）；触发定义、推荐动作与 Q 编号引用见 configs/rules.yaml。

**表 3** 基准性能矩阵（5 种子 mean±SD；每方法 560 次，共 2,240 次）；上下文为每次运行的平均检索字符数。

**表 4** 112 条终版陈述的金标准领域×动作分布（indication 23、procedure 34、treatment planning 55；against 类 25 条，合计 22.3%）。
"""

manuscript = "\n\n---\n\n".join(blocks) + tail
(P / "manuscript.md").write_text(manuscript, encoding="utf-8")
print(f"[assemble] outputs/paper/manuscript.md  ({len(manuscript)} chars)")
