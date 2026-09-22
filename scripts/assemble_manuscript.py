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
]
blocks = []
for f in parts:
    blocks.append(f.read_text(encoding="utf-8").strip())

tail = f"""

---

## 数据与代码可用性 (Data Availability)

规则库（configs/rules.yaml）、双实体注册表（data/seed/entities_a.csv, entities_b.csv）、证据块库（data/seed/evidence_chunks.jsonl，357 条）、金标准标注（data/seed/probiopsy_statements.csv，112 条）、全部 2,240 条原始预测记录（outputs/baseline_predictions.jsonl，含每次运行的上下文字符数与检索块数）、旗舰档补充数据（outputs/baseline_predictions_glm53.jsonl）、评估脚本（scripts/evaluate.py）与图表源数据（outputs/figures/source_data/）随代码仓库发布：{repo}（Zenodo 归档：{doi}）。

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
"""

manuscript = "\n\n---\n\n".join(blocks) + tail
(P / "manuscript.md").write_text(manuscript, encoding="utf-8")
print(f"[assemble] outputs/paper/manuscript.md  ({len(manuscript)} chars)")
