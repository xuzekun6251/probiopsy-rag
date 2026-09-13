# IRB 申请摘要表 — 前列安汇（probiopsy-rag）

> **文档用途**：提交至 [TODO: irb_committee_name] 的伦理审查申请摘要
> **创建日期**：2026-09-13
> **版本**：v1.0
> **配套文档**：[ETHICS.md](ETHICS.md) 完整叙述 | [Data_Management_Plan.md](Data_Management_Plan.md)

---

## 1. 基本信息

| 字段 | 内容 |
|---|---|
| **研究题目** | 前列安汇：基于规则引擎、知识图谱与 LLM 仲裁的 LightRAG混合决策支持系统:患者临床情境×穿刺决策项 筛查决策支持系统 |
| **研究类型** | 回顾性病例系列 + 文献证据回顾 |
| **PI** | [TODO: pi_name]（[TODO: pi_title]） |
| **PI 单位** | [TODO: pi_department], [TODO: hospital_name] |
| **联系方式** | Email: [TODO: pi_email] / Phone: [TODO: pi_phone] |
| **共同研究者** | [TODO: coinvestigator_names] |
| **资助方** | [TODO: funding_source] |
| **资助编号** | [TODO: funding_id] |
| **预期研究周期** | 10 周 |
| **预计纳入病例数** | 0 例（回顾性） |
| **研究地点** | [TODO: hospital_name]（单中心） |

---

## 2. 研究背景与意义

### 2.1 科学背景

在前列腺穿刺活检决策中,规则引擎+LightRAG知识图谱+LLM仲裁混合系统能否依据ProBIOPSY国际共识与EAU指南,为特定患者临床情境生成规范化的穿刺决策建议?

### 2.2 研究现状

- pending 数据可及性（见 [ETHICS.md](ETHICS.md) §1.2）
- 现有研究缺口：缺乏 A×B 矩阵系统化筛查工具
- 本研究填补：首创规则 + KG + LLM 三层架构用于 LightRAG混合决策支持系统:患者临床情境×穿刺决策项

### 2.3 临床意义

为 adult_men_with_suspected_prostate_cancer 提供 患者临床情境要素 × 穿刺决策项 风险分级的可追溯、可解释决策支持。

---

## 3. 研究目的与具体目标

### 3.1 主要目的

构建并验证 前列安汇 筛查系统，在 50 个 患者临床情境要素 × 40 个 穿刺决策项 的所有 A×B 组合上输出可解释的风险分级。

### 3.2 次要目的

1. 评估 4 个 baseline（pure_llm / naive_rag / lightrag / full system）的性能差异
2. 在 200 例回顾性病例上评估临床有效性
3. 在 4 名专家盲评中评估 face validity

---

## 4. 研究方法

### 4.1 研究设计

**回顾性、单中心、模型开发与验证研究**。

### 4.2 数据来源

| # | 数据源 | 类型 | 数据量 | 用途 |
|---|---|---|---|---|
| 1 | [TODO: hospital_name] EMR | 回顾性病历 | 0 例 | Phase 3 临床验证 |
| 2 | CTD / ToxCast / Prop 65 / ECHA 等 | 公开数据库 | 见 DMP | 模型构建 |
| 3 | PubMed E-utilities | 公开文献 | ~250 篇 | 证据库 |

### 4.3 纳入标准（回顾性病例）

- [ ] 20XX-XX-XX 至 20XX-XX-XX 期间在 [TODO: hospital_name] 就诊
- [ ] 诊断为 患者临床情境要素之一（按 WHO ICD-11 / ASRM 标准）
- [ ] 病历中含暴露史记录（自报或生物监测）
- [ ] 完成基本人口学信息

### 4.4 排除标准

- [ ] 病历不完整（缺关键结局指标）
- [ ] 拒绝数据用于研究（前瞻性 opt-out 患者）

### 4.5 主要分析

- 系统输出 vs 文献金标准：sens / spec / F1 / Cohen's κ
- 系统输出 vs 专家盲评：Fleiss κ + 系统一致性
- 多 seed（≥5）×多 baseline 配对 t 检验，p < 0.05

### 4.6 数据安全监测

- **DSMB/DMC**：不适用（minimal risk，无干预）
- **数据安全**：见 DMP §4

---

## 5. 受试者保护

### 5.1 风险等级

**Minimal Risk**（≤ 日常生活风险）

### 5.2 知情同意

**申请豁免知情同意**，依据：
- 45 CFR 46.116(f) / 《伦理审查办法》第 32 条
- 满足 4 条豁免要件（见 [ETHICS.md](ETHICS.md) §7.1）

### 5.3 隐私保护

- HIPAA Safe Harbor 去标识化（18 identifiers）
- 仅去标识化数据离开医院；PHI 永不外传
- 见 [Data_Management_Plan.md](Data_Management_Plan.md) §3

### 5.4 弱势群体

涵盖：mri_visible_lesion, mri_indeterminate, prior_negative_biopsy, anticoagulated, focal_therapy_candidate
保护措施见 [ETHICS.md](ETHICS.md) §5。

---

## 6. 数据管理

详见 [Data_Management_Plan.md](Data_Management_Plan.md)。

**关键点**：
- 数据保留：研究结束后 5 年（20XX-XX-XX 销毁）
- 数据存储：本地工作站(加密磁盘),仅使用公开数据
- 公开共享：去标识化数据集（Zenodo / OSF，DOI 化）；PHI 永不公开

---

## 7. AI / 算法相关

### 7.1 系统定位

**决策支持系统，非诊断设备**。最终判断由临床医生做出。

### 7.2 使用的 LLM / AI 模型

| 模型 | 用途 | 版本锁定 |
|---|---|---|
| `deepseek-v4-flash` | LightRAG 知识图谱构建 | 已锁定 |
| `doubao-embedding-vision-251215` | 向量索引（dim=2048） | 已锁定 |
| `gpt-4-turbo-2024-04-09` | 最终报告仲裁（~500 次调用） | 已锁定 |

### 7.3 AI 特定风险

- **训练数据偏见**：DeepSeek/GPT-4 偏向英文文献，可能影响中文临床适用性
- **缓解**：规则引擎作为"grounding"，限制 LLM 自由发挥

### 7.4 报告框架遵循

- TRIPOD-AI（AI 预测模型）
- DECIDE-AI（早期 AI 临床评估）

---

## 8. 利益冲突

- **财务 COI**：[TODO: coi_disclosure, 若无请写'无']
- **非财务 COI**：[TODO: nonfinancial_coi]
- **管理计划**：在论文 + 演讲中完整披露

---

## 9. 研究进度安排

| 阶段 | 时间 | 主要工作 | 与伦理相关 |
|---|---|---|---|
| IRB 申请提交 | 第 0 周 | 提交本申请材料 | **本步骤** |
| IRB 审批周期 | 第 1-3 周 | 等待 IRB 批准 | — |
| 系统构建 | 第 1-4 周 | Phase 0-2（不依赖临床数据） | — |
| 临床数据获取 | 第 4 周 | **IRB 批准后**，去标识化获取 200 例病历 | 关键节点 |
| 模型验证 | 第 5-9 周 | Phase 3-5 | — |
| 论文写作 | 第 9-11 周 | Phase 6-7 | TRIPOD-AI 检查 |
| 投稿 | 第 12 周 | Phase 8 | 报告 ethics 批准号 |

---

## 10. 主要研究者承诺

本人承诺：
1. 严格按照本方案开展研究，不得擅自修改；如需修改，提交 IRB 修正审查
2. 真实、准确、完整地记录与报告数据
3. 保护受试者隐私与权益
4. 及时报告任何不良事件或数据安全事件
5. 接受 IRB 的监督与审查
6. 研究结束后 90 天内提交终期报告

**PI 签字**：____________________  **日期**：____________________

---

## 11. 附件清单

- [ ] 完整 ETHICS 叙述（[ETHICS.md](ETHICS.md)）
- [ ] 数据管理计划（[Data_Management_Plan.md](Data_Management_Plan.md)）
- [ ] 知情同意书模板（[Informed_Consent.md](Informed_Consent.md)，如适用）
- [ ] PI CV
- [ ] 合作医院资质证明
- [ ] 数据使用协议（DUA）
- [ ] 研究方案完整版（[PLAN.md](../PLAN.md)）
- [ ] AI/ML 模型文档（TRIPOD-AI checklist）
