# 伦理叙述文档 — 前列安汇（probiopsy-rag）

> **文档用途**：IRB 申请材料封面叙述、基金申请书伦理章节、论文 Methods Ethics 节原始素材
> **创建日期**：2026-09-13
> **版本**：v1.0（scaffold 生成，需 PI 审核签字后提交）
> **配套文档**：[IRB_Protocol_Summary.md](IRB_Protocol_Summary.md) | [Data_Management_Plan.md](Data_Management_Plan.md) | [Informed_Consent.md](Informed_Consent.md) | [Manuscript_Ethics_Statement.md](Manuscript_Ethics_Statement.md)

---

## 1. 研究概况

### 1.1 研究题目

前列安汇：基于规则引擎、知识图谱与 LLM 仲裁的 LightRAG混合决策支持系统:患者临床情境×穿刺决策项 筛查决策支持系统

### 1.2 研究类型

- **研究设计**：回顾性病例系列 + 文献证据回顾 + 公开数据库分析（如适用）
- **数据来源**：
  - 主要：ProBIOPSY consensus main text + mmc1 supplementary, EAU Prostate Cancer Guidelines (biopsy chapter), AUA/SUO Prostate Cancer Guideline (2023/amended), NICE NG131 Prostate Cancer...
  - 临床：合作医院回顾性病例（0 例）
  - 公开数据：ProBIOPSY consensus main text + mmc1 supplementary, EAU Prostate Cancer Guidelines (biopsy chapter), AUA/SUO Prostate Cancer Guideline (2023/amended), NICE NG131 Prostate Cancer, PubMed abstract pool (targeted biopsy / systematic biopsy / PI-RADS, 2015-2026)
- **干预**：**无**（仅分析与建模，不涉及前瞻性干预）
- **随访**：**无**

### 1.3 研究目的

在前列腺穿刺活检决策中,规则引擎+LightRAG知识图谱+LLM仲裁混合系统能否依据ProBIOPSY国际共识与EAU指南,为特定患者临床情境生成规范化的穿刺决策建议?

### 1.4 预期受益

- **个体层面**：为 adult_men_with_suspected_prostate_cancer 提供 患者临床情境要素 × 穿刺决策项 相互作用的可追溯、可解释的决策支持
- **群体层面**：促进 穿刺决策项 暴露风险管理，降低 患者临床情境要素 相关不良结局
- **科学层面**：首个将规则引擎 + KG + LLM 仲裁三层架构用于该 A×B 组合的系统化筛查工具

---

## 2. IRB / 伦理审查路径

### 2.1 审查类型

- [x] **快速审查**（Expedited Review）—— 适用于 minimal risk 回顾性研究
- [ ] 豁免审查（Exemption）
- [ ] 全体委员会审查（Full Board Review）

### 2.2 依据法规

- 《医疗机构管理条例》及实施细则
- 《人类生物医学研究伦理审查办法》（国家卫生计生委令第 11 号，2016）
- 《涉及人的生物医学研究伦理审查规范》（WS/T 656-2019）
- 《个人信息保护法》（PIPL，2021）
- 《健康医疗大数据管理办法》（2018）
- **Declaration of Helsinki**（2013 版）
- **CIOMS International Ethical Guidelines**（2016 版）

### 2.3 伦理委员会信息

- **委员会名称**：[TODO: irb_committee_name]
- **依托机构**：[TODO: hospital_name]
- **委员会编号**：[TODO: irb_committee_id]
- **联系人**：[TODO: irb_contact_name] / [TODO: irb_contact_email] / [TODO: irb_contact_phone]
- **申请提交日期**：[TODO: submission_date]
- **预期审批日期**：[TODO: expected_approval_date]

### 2.4 PI 与研究人员

- **PI**：[TODO: pi_name]（[TODO: pi_title]，[TODO: pi_department]）
- **联系方式**：[TODO: pi_email] / [TODO: pi_phone]
- **共同研究者**：[TODO: coinvestigator_names]
- **数据管理员**：[TODO: data_manager_name]
- **统计分析员**：[TODO: statistician_name]

---

## 3. 受试者保护

### 3.1 风险分类

按 45 CFR 46.110 /《伦理审查办法》第 32 条，本研究为 **Minimal Risk**：

- **风险描述**：仅回顾性查阅病历，**无干预、无侵入性操作、无前瞻性接触**
- **风险等级**：≤ 日常生活风险
- **主要风险来源**：
  1. **隐私泄露风险**（PHI 外泄） —— 见 §4 缓解
  2. **数据错误关联风险**（模型误判） —— 见 §6 缓解
  3. **群体污名化风险**（特定亚型被标签化） —— 见 §5 缓解

### 3.2 风险最小化措施

| 风险 | 缓解措施 |
|---|---|
| PHI 泄露 | 见 [Data_Management_Plan.md](Data_Management_Plan.md) §3 去标识化协议 |
| 模型误判 | LLM 输出**仅作决策支持**，最终判断由临床医生做出 |
| 群体污名化 | 论文 Limitations 节明示"亚型标签不应作为患者身份标识" |
| 数据再识别 | 公开数据集仅用聚合统计；个体级数据不上传任何公开仓库 |

### 3.3 受益最大化

- 所有 A×B 对的判读结果**免费开源**给临床合作医院，提升本地临床决策水平
- 系统输出 4 种报告视图（医生 / 患者 / 研究 / 政策），可直接用于患者教育

---

## 4. 数据保护与隐私

### 4.1 数据来源与流向量

```
[公开数据库] ─────┐
                  ├──→ [Huanyu 系统服务器] ──→ [去标识化证据库] ──→ [LightRAG 索引]
[合作医院病历] ──┘
                  ↑
                  └─ 经 HIPAA Safe Harbor 去标识化后传输
```

### 4.2 数据类型

- **PHI（个人健康信息）**：仅在合作医院内处理；传输前完成去标识化
- **去标识化数据**：上传至系统服务器参与建模
- **公开数据**：CTD、ToxCast 等（无 PHI）

### 4.3 去标识化标准

遵循 HIPAA Safe Harbor 18 identifiers（45 CFR 164.514(b)(2)(i)）：

1. 姓名
2. 地理位置（小于州的细分）
3. 日期（除年份外的所有日期元素；年龄 > 89 岁合并为"≥90"）
4. 电话 / 传真 / 邮箱 / SSN / 医保号 / 账户号
5. 证书 / 设备 ID / URL / IP / 生物特征
6. 任何其他可识别代码

详见 [Data_Management_Plan.md](Data_Management_Plan.md) §3。

### 4.4 数据存储与访问

- **存储位置**：本地工作站(加密磁盘),仅使用公开数据（机构受控服务器 / 加密云）
- **访问控制**：基于角色的访问控制（RBAC）；最小权限原则
- **加密**：传输 TLS 1.3；存储 AES-256
- **备份**：每日增量，每周完整；保留 6 个月
- **审计日志**：所有数据访问记录，保留 5+ 年

---

## 5. 弱势群体保护

### 5.1 涉及的潜在弱势群体

本研究涵盖以下亚组，需特别保护：

| 群体 | 保护措施 |
|---|---|
| **妊娠期女性** | 不直接干预；分析时遵循 ICH E8(R1) 妊娠数据特殊处理 |
| **儿科患者**（如有） | 数据按年龄分层；不单独识别 < 18 岁个体 |
| **不孕症患者**（敏感身份） | 公开报告仅用聚合统计；不暴露个体亚型标签 |
| **职业暴露人群**（如化工工人） | 与雇主数据隔离；不用于雇佣决策 |

### 5.2 公平性考量

- **入选标准**：回顾性纳入所有合作医院就诊的符合标准病例，无性别 / 种族 / 经济状况歧视
- **亚组分析**：按性别、年龄段、地理区域分层报告性能差异
- **外推性**：在 Limitations 中明示"训练数据可能偏向中国汉族人群；外推至其他人群需谨慎"

---

## 6. AI / 算法透明度

### 6.1 系统定位

**Huanyu 是决策支持系统，不是诊断设备**：
- 输出：分级风险报告 + 证据链 + 推荐意见
- **最终判断权**：临床医生
- **使用范围**：临床咨询 / 患者教育 / 研究假设生成；**不用于自动诊断或自动决策**

### 6.2 算法可解释性

| 层级 | 解释方式 |
|---|---|
| 规则层 | YAML 配置公开；每条规则有 rationale + citation |
| 检索层 | KG 路径可视化；证据 chunk 可点击查看原文 |
| 仲裁层 | LLM 输出附 prompt + response log；不黑箱 |

### 6.3 模型版本与可重复性

锁定模型版本：

- `deepseek-v4-flash`（DeepSeek，构建知识图谱）
- `doubao-embedding-vision-251215`（火山方舟，向量索引，dim=2048）
- `gpt-4-turbo-2024-04-09`（OpenAI，最终报告仲裁）

所有 LLM 调用 log：`{input, output, model_version, timestamp, token_count}`，保留 5+ 年。

### 6.4 偏见与局限

- **训练数据偏见**：DeepSeek / GPT-4 训练数据偏向英文 / 西方医学文献；可能在中文临床语境下产生偏差
- **缓解**：规则引擎作为"grounding"，限制 LLM 自由发挥；在中文病例验证集（n=200）上做 sens/spec 评估
- **披露**：论文 Methods + Limitations 节明示

### 6.5 适用报告框架

- [x] **TRIPOD-AI**：AI 预测模型报告规范
- [x] **DECIDE-AI**：早期阶段 AI 临床评估
- [ ] CONSORT-AI（非 RCT，不适用）
- [ ] SPIRIT-AI（非 protocol，不适用）

---

## 7. 知情同意（如适用）

### 7.1 回顾性研究（HuanYu 默认路径）

依据 45 CFR 46.116(f) / 《伦理审查办法》第 32 条，**回顾性病历研究可申请知情同意豁免**，需满足：

- [x] 研究涉及 ≤ minimal risk
- [x] 豁免不会对受试者权利与福利产生不利影响
- [x] 研究无法在不接触 PHI 的前提下完成（去标识化后进行）
- [x] 受试者事后无法被合理告知研究存在（病历已归档）

→ **申请豁免知情同意**（在 IRB Protocol Summary 中明示）

### 7.2 前瞻性研究（如未来扩展）

若项目扩展为前瞻性（如随访新病例、采集生物样本），**必须使用 [Informed_Consent.md](Informed_Consent.md) 模板取得书面同意**。

---

## 8. 数据共享与发表

### 8.1 数据共享

- **代码**：GitHub 开源（MIT 或 Apache 2.0 许可证）
- **去标识化数据**：经 IRB 批准后，在 Zenodo / OSF 发布快照（DOI 化）
- **PHI**：**永不公开共享**；如其他研究者需要复现，可通过 DUA 申请访问
- **LLM 调用日志**：5 年内 PI 受控保留；之后销毁

### 8.2 发表伦理

- **作者资格**：遵循 ICMJE 4 条标准；具体贡献用 CRediT 分类（见 [Manuscript_Ethics_Statement.md](Manuscript_Ethics_Statement.md)）
- **AI 工具使用披露**：依 ICJME 2023 指南，在 Methods 节披露 LLM 使用（model + version + 用途）
- **预印本**：允许在 medRxiv / bioRxiv 预印，不影响期刊投稿
- **数据虚假**：遵循 COPE 指南处理

---

## 9. 不良事件 / 数据安全事件处理

### 9.1 不良事件（仅前瞻性适用）

不适用（回顾性研究无干预）。

### 9.2 数据安全事件

| 事件类型 | 响应时间 | 报告对象 |
|---|---|---|
| PHI 泄露 | 24 小时内 | IRB + 医院信息安全部 + 受影响个人 |
| 未经授权访问 | 48 小时内 | IRB + PI + 机构 DPO |
| 数据损坏 / 丢失 | 72 小时内 | PI + 备份恢复 |
| 算法重大偏差 | 7 天内 | IRB + 期刊（如已发表） |

### 9.3 应急预案

- 数据泄露：立即撤销访问权限、隔离受影响系统、启动取证
- LLM 输出严重错误：暂停系统使用、评估影响范围、通报临床用户

---

## 10. 利益冲突

### 10.1 财务利益冲突

- **PI 与研究人员**：[TODO: coi_disclosure — 列出所有 COI]
- **资助方**：[TODO: funding_source] —— 资助方**不参与**研究设计、数据收集分析、发表决策
- **LLM 提供商**：DeepSeek / OpenAI / 火山方舟 —— **仅作为工具提供商，无研究资助关系**

### 10.2 非财务利益冲突

- 学术声誉 / 发表压力 / 知识产权等

### 10.3 管理

所有 COI 在投稿、IRB 申请、公开演讲时**完整披露**。

---

## 11. 伦理审查后续监督

### 11.1 修正案（Amendment）

任何方案变更（数据源、PI、研究范围、AI 模型等）需提交 IRB 修正审查。

### 11.2 年度审查（Continuing Review）

按 IRB 要求，通常每年一次提交研究进度报告。

### 11.3 终止报告

研究结束后 90 天内提交终期报告；数据按 DMP §6 销毁或归档。

---

## 12. PI 签字确认

本人已审阅本伦理叙述文档，确认所有信息准确无误，研究将严格按照本方案执行。

**PI 签字**：____________________  **日期**：____________________

**IRB 主任签字**（审查后填）：____________________  **日期**：____________________

---

## 附录：参考文献

1. World Medical Association. Declaration of Helsinki (2013). JAMA, 310(20), 2191-2194.
2. National Commission for the Protection of Human Subjects of Biomedical and Behavioral Research. The Belmont Report (1979).
3. Council for International Organizations of Medical Sciences. International Ethical Guidelines for Health-related Research Involving Humans (2016).
4. 中国国家卫生计生委. 涉及人的生物医学研究伦理审查办法 (2016).
5. 全国人大常委会. 中华人民共和国个人信息保护法 (2021).
6. Collins GS, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models. BMJ (2024).
7. Sounderajah V, et al. Developing specific reporting guidelines for artificial intelligence-assisted clinical trials (CONSORT-AI). Nature Medicine (2020).
