# 数据管理计划（DMP）— 前列安汇（probiopsy-rag）

> **文档用途**：IRB 申请材料、期刊 Data Availability 节、研究全周期数据治理参考
> **创建日期**：2026-09-13
> **版本**：v1.0
> **配套文档**：[ETHICS.md](ETHICS.md) | [IRB_Protocol_Summary.md](IRB_Protocol_Summary.md)

---

## 1. 数据概述

### 1.1 数据来源

| # | 数据源 | 类型 | 是否含 PHI | 体量 | 许可证 / 协议 |
|---|---|---|---|---|---|
| 1 | [TODO: hospital_name] EMR | 回顾性病历 | **是** | 0 例 | DUA [TODO: dua_id] |
| 2 | CTD (ctdbase.org) | 化学-基因-疾病 | 否 | 94M+ 连接 | CC BY 4.0 (curated)；API ToS |
| 3 | EPA ToxCast/Tox21 (invitroDB V4.2) | 体外高通量 | 否 | 9500 化学 × 625 assays | 公开（联邦政府作品） |
| 4 | EPA CompTox Chemicals Dashboard | 化学综合 | 否 | 1M+ 化学 | 公开 |
| 5 | TEDX Endocrine Disruptor Exchange | EDC 列表 | 否 | ~1500 | 学术免费 |
| 6 | 加州 Prop 65 列表 | 生殖毒物 | 否 | ~300 | 公开 |
| 7 | ECHA REACH SVHC | 高关注物质 | 否 | ~235 | CC BY 4.0 |
| 8 | ATSDR Toxicological Profiles | 毒理专论 | 否 | ~180 | 公开 |
| 9 | DisGeNET | 基因-疾病 | 否 | 1M+ | CC BY-NC 4.0（部分付费） |
| 10 | KEGG / Reactome | 通路 | 否 | 标准库 | 各自 license |
| 11 | NHANES (CDC) | 人群生物监测 | 否（已去标识化） | 多周期 | 公开 |
| 12 | PubMed E-utilities | 文献 | 否 | 36M+ 摘要 | NCBI API ToS |
| 13 | FDA DailyMed | 药品说明书 | 否 | 100k+ | 公开 |
| 14 | IARC Monographs | 致癌/生殖毒理 | 否 | ~100 专论 | 公开 |
| 15 | NTP Reports | 毒理 | 否 | 数百报告 | 公开 |

### 1.2 数据分类

- **Tier 1（PHI）**：医院 EMR 数据 —— 受 PIPL / HIPAA-equivalent 保护
- **Tier 2（敏感人群数据）**：去标识化的医院数据 —— 受 DUA 约束
- **Tier 3（公开数据）**：上述 #2-#15 —— 遵循各源许可证

---

## 2. 数据收集与获取

### 2.1 医院数据（Tier 1 + 2）

**收集流程**：

```
[医院 EMR 系统]
     ↓ 经医院 IT 部门协助导出（受控环境）
[医院内安全服务器]
     ↓ HIPAA Safe Harbor 去标识化（见 §3）
[Tier 2 数据]
     ↓ 加密传输（TLS 1.3）至研究服务器
[Huanyu 研究服务器]
```

**收集字段**：
- 人口学：年龄段（10 年分层）、性别、地区（省/直辖市级别）
- 诊断：ICD-11 编码、亚型（PCOS/POI/...）
- 暴露史：职业（行业大类）、生活方式（吸烟 / 饮酒 / 饮食模式）
- 结局：IVF 周期数、临床妊娠、活产（如适用）
- 实验室：激素水平（聚合到正常/异常二分类）

**排除字段**（永不收集）：
- 姓名、身份证号、医保号、电话、邮箱
- 详细地址（精确到街道以下）
- 完整出生日期（仅留年龄）
- 就诊日期（仅留年份）
- 影像学原始文件

### 2.2 公开数据（Tier 3）

- 通过各源 API / 批量下载
- 记录**数据 release date**（用于版本锁定）
- 命名约定：`data/raw/<source>/release-YYYY-MM.json`

---

## 3. 去标识化协议

### 3.1 标准

遵循 **HIPAA Safe Harbor** 18 identifiers（45 CFR 164.514(b)(2)(i)）+ **中国《个人信息保护法》第 28 条** 敏感个人信息要求。

### 3.2 18 identifiers 处理表

| # | Identifier | 处理方式 |
|---|---|---|
| 1 | 姓名 | 删除，替换为伪 ID（hash） |
| 2 | 地理位置（小于州/省） | 仅保留省/直辖市级别 |
| 3 | 日期（除年份） | 仅保留年份；所有日期偏移随机天数 |
| 4 | 电话 / 传真 | 删除 |
| 5 | 邮箱 | 删除 |
| 6 | SSN / 身份证号 | 删除 |
| 7 | 医保号 | 删除 |
| 8 | 账户号 | 删除 |
| 9 | 证书 / 执照号 | 删除 |
| 10 | 车辆 ID / 车牌 | 删除 |
| 11 | 设备 ID / 序列号 | 删除 |
| 12 | URL | 删除 |
| 13 | IP 地址 | 删除 |
| 14 | 生物特征 | 删除 |
| 15 | 纹身等独特标识 | 删除 |
| 16 | 照片 | 删除（如必须，遮挡面部） |
| 17 | 年龄 > 89 | 合并为 "≥ 90" |
| 18 | 其他唯一代码 | 删除 |

### 3.3 去标识化执行

- **执行者**：医院 IT 部门 + 研究数据管理员（[TODO: data_manager_name]）
- **执行环境**：医院内安全服务器，不离开医院网络
- **审计**：保留去标识化操作日志
- **重识别测试**：由独立人员抽样检查 100 例，确认无重识别可能

---

## 4. 数据存储与访问

### 4.1 存储位置

| 数据 Tier | 存储位置 | 加密 |
|---|---|---|
| Tier 1（PHI） | 医院内安全服务器（**不外传**） | AES-256 + TLS 1.3 |
| Tier 2（去标识化） | 本地工作站(加密磁盘),仅使用公开数据（机构受控云） | AES-256 + TLS 1.3 |
| Tier 3（公开） | 本地项目服务器 | 不要求加密（已公开） |

### 4.2 访问控制

- **RBAC**（基于角色的访问控制）
- **最小权限原则**
- **双因子认证**（2FA）对所有可访问 PHI/Tier 2 的账户
- **审计日志**：所有数据访问记录，保留 5+ 年

### 4.3 备份

- **频率**：每日增量，每周完整
- **保留期**：6 个月
- **离线副本**：每季度 1 次离线备份

---

## 5. 数据共享

### 5.1 共享原则

**FAIR 原则**（Findable, Accessible, Interoperable, Reusable）+ 受控访问（受保护数据）。

### 5.2 共享层级

| 数据类型 | 共享方式 |
|---|---|
| **代码** | GitHub 公开（MIT / Apache 2.0） |
| **去标识化数据集（Tier 2）** | IRB 批准后发布至 Zenodo / OSF（DOI 化） |
| **公开数据快照（Tier 3）** | GitHub releases（版本锁定） |
| **LLM 调用日志** | 受控保留 5 年；之后销毁 |
| **PHI（Tier 1）** | **永不共享**；其他研究者可通过 DUA 申请访问（仅限合作医院内） |

### 5.3 数据使用协议（DUA）

跨机构数据共享需 DUA：

- **模板**：[TODO: dua_template_reference]
- **审批流程**：PI → 数据管理员 → 双方机构法务 → IRB 备案
- **典型条款**：仅用于批准的研究目的；不得再共享；研究结束销毁

### 5.4 数据可用性声明（论文用）

> "The code supporting this study is available at https://github.com/<TODO>/huanyu under the MIT license. De-identified clinical data will be available upon reasonable request to the corresponding author, subject to a Data Use Agreement and approval by the institutional review board. Public data sources (CTD, ToxCast, Prop 65, ECHA, ATSDR, etc.) are accessible via their respective APIs under the licenses noted in Supplementary Table S1."

---

## 6. 数据保留与销毁

### 6.1 保留期

| 数据 | 保留期 | 依据 |
|---|---|---|
| PHI（Tier 1） | 研究结束后 5 年 | 期刊 + IRB 要求 |
| Tier 2 去标识化 | 研究结束后 5 年 | 复现 / 重审 |
| Tier 3 公开快照 | 永久（DOI 化） | 复现 |
| LLM 调用日志 | 5 年 | AI 透明度 |
| 审计日志 | 5 年 | 合规 |

### 6.2 销毁方式

- **电子数据**：使用 NIST SP 800-88 "Clear/Purge" 标准擦除（≥ 3 次覆写）
- **物理介质**：物理销毁（硬盘粉碎）
- **销毁证明**：保留销毁证明文档，提交 IRB 终期报告

### 6.3 销毁时间表

- 研究结束日期：[TODO: study_end_date]（预计 10 周后）
- 强制销毁日期：[TODO: destruction_date]（研究结束后 5 年）

---

## 7. 数据质量与完整性

### 7.1 质量控制

- **数据录入**：双人独立录入 + 第三人仲裁
- **逻辑检查**：自动校验（如年龄不能 > 120；诊断与性别一致）
- **异常值**：标记并复核

### 7.2 版本控制

- **代码**：Git（GitHub / Gitee）
- **数据快照**：`data/raw/<source>/release-YYYY-MM.json`，附 SHA-256 校验
- **模型 checkpoint**：`outputs/checkpoints/<date>/<seed>/`

### 7.3 元数据

每个数据集附 `manifest.json`：

```json
{
  "source": "CTD",
  "release_date": "2026-03",
  "url": "https://ctdbase.org/downloads/",
  "downloaded_at": "2026-04-15T10:30:00Z",
  "sha256": "...",
  "license": "CC BY 4.0",
  "n_records": 94000000,
  "schema_version": "v1.2"
}
```

---

## 8. 数据安全事件响应

### 8.1 事件分级

| 级别 | 定义 | 响应时间 |
|---|---|---|
| 一级（重大） | PHI 泄露至未授权方 | 24 小时内通知 IRB + 受影响个人 |
| 二级（重大） | 未经授权访问研究数据 | 48 小时内通知 IRB |
| 三级（一般） | 内部误操作，未外泄 | 72 小时内记录 + 复盘 |

### 8.2 应急流程

1. **发现**：任何人（研究人员 / IT / 审计员）发现立即报告 PI
2. **隔离**：立即撤销访问权限、隔离受影响系统
3. **取证**：保留日志、评估影响范围
4. **通知**：按级别通知相关方
5. **补救**：修复漏洞、加强控制
6. **记录**：完整记录事件与响应

---

## 9. 法规遵循

### 9.1 中国法规

- ✅ 《个人信息保护法》（PIPL，2021）—— 28 条敏感个人信息处理规范
- ✅ 《数据安全法》（DSL，2021）
- ✅ 《健康医疗大数据管理办法》（2018）
- ✅ 《人类生物医学研究伦理审查办法》（2016）

### 9.2 国际法规（如适用）

- ✅ GDPR（如服务欧盟数据主体）—— Article 9 特殊类别数据
- ✅ HIPAA Privacy Rule（如服务美国主体）
- ✅ Declaration of Helsinki（2013）

### 9.3 标准遵循

- ISO 27001（信息安全管理）
- ISO 27701（隐私信息管理）
- NIST SP 800-88（数据销毁）
- FAIR Data Principles

---

## 10. DMP 维护与更新

- **维护责任人**：数据管理员 [TODO: data_manager_name]
- **更新触发**：数据源变更、IRB 修正案、法规更新
- **版本**：每更新一次版本号 +0.1
- **存档**：所有版本永久保留

---

## 附录 A：数据源许可证详细表

| 数据源 | 完整许可证 | 商业使用 | 衍生作品 |
|---|---|---|---|
| CTD curated | CC BY 4.0 | 允许（署名） | 允许 |
| ToxCast | Public Domain（联邦作品） | 允许 | 允许 |
| DisGeENT | CC BY-NC 4.0 | **不允许** | 允许（非商业） |
| KEGG | 学术免费 / 商业付费 | 取决于订阅 | 取决于订阅 |
| PubMed abstracts | NCBI API ToS | 引用允许 | 摘要不构成衍生 |
| Prop 65 | Public Domain | 允许 | 允许 |
| ECHA | CC BY 4.0 | 允许（署名） | 允许 |
| ATSDR | Public Domain | 允许 | 允许 |
| IARC | CC BY-NC-ND 3.0 IGO | **不允许** | **不允许** |

→ **重要**：论文发表后，使用 DisGeNET / IARC 数据的部分需在 Limitations 中说明非商业用途限制。

---

## 附录 B：去标识化自检 Checklist

提交 IRB 前由数据管理员核对：

- [ ] 所有 18 个 HIPAA Safe Harbor identifiers 已处理
- [ ] 任何单一数据集的样本量 ≥ 5（避免小样本重识别）
- [ ] 地理位置粒度 ≥ 省/州级别
- [ ] 日期已偏移或仅保留年份
- [ ] 年龄 > 89 已合并
- [ ] 抽样检查 100 例，无法通过交叉信息重识别
- [ ] 操作日志完整保留
- [ ] 独立人员复核签字

完成日期：____________________  数据管理员签字：____________________
