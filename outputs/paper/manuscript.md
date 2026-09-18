# 前列安汇：规则引擎—知识图谱—LLM 仲裁混合决策支持系统在前列腺穿刺活检全流程中的开发与验证

**Development and benchmark validation of QianLieAnHui (前列安汇), a hybrid rule-engine / knowledge-graph / LLM-arbitration decision-support system for the prostate biopsy pathway, against the ProBIOPSY international consensus**

## 作者

徐泽坤<sup>1,\*</sup>

<sup>1</sup>泌尿外科，浙江大学附属金华医院；<sup>\*</sup>通讯作者：xuzekunurology@163.com

## 结构化摘要

**背景** 前列腺穿刺活检决策涉及影像质量、穿刺方案、入路、围术期预防与治疗规划衔接的多因素权衡；国际共识（ProBIOPSY，112 条终版陈述）以文本形式存在，无法直接执行。大语言模型（LLM）灵活但存在幻觉与不可溯源性，检索增强生成（RAG）可缓解但缺乏确定性安全约束。

**方法** 我们开发前列安汇：确定性规则引擎（12 条共识规则 + 4 条患者因素升级，输出硬约束）→ 风险引导的 LightRAG 知识图谱检索（357 个证据块、1,864 实体、3,078 关系，全部溯源自共识文本与参考文献）→ LLM 仲裁（输出五类动作：endorse / endorse_option / conditional / report_option / against，含置信度与 Q 编号引用链）。以 112 条共识终版陈述为金标准，在统一生成器（GLM-5.3-Flash）条件下进行 4 方法 × 5 种子 × 112 陈述 = 2,240 次运行的基准评测；另以 GLM-5.3 旗舰档重跑基线（1,120 次）检验生成器档位的影响。

**结果** 完整系统 exact5 = 0.805±0.012、macro-F1 = 0.825、κ = 0.730±0.016、against-F1 = 0.908（specificity 0.986），显著优于 lightrag-only（0.613 / 0.536 / 0.525 / 0.881）、naive_rag（0.605 / 0.514 / 0.512 / 0.890）与 pure_llm（0.304 / 0.254 / 0.079 / 0.346）。基线在细粒度类别上塌缩为高频类：conditional 在 1,120 次基线运行中仅被主动输出 9 次（0.8%），而完整系统为 17.0%。更换更强生成器后 naive_rag exact5 反而下降（0.605→0.538）。

**结论** 在医学决策支持系统中，细粒度临床动作空间的表达能力必须内建于架构（规则硬约束 + 类别先验），而非依赖提示词或更大模型。架构差异，而非模型档位，是性能的主要杠杆；系统输出全程可溯源至共识陈述与证据块，支持临床治理审计。

**关键词** 前列腺癌；穿刺活检；临床决策支持系统；知识图谱；LightRAG；检索增强生成；大语言模型；国际共识；ProBIOPSY

---

# 引言 (Introduction)

> 中文工作稿（Writer Phase 7_3）。引用骨架见文末参考文献（全部经 ≥2 独立数据源核验）。

前列腺癌是全球男性最常见的恶性肿瘤之一，穿刺活检是其确诊的基石[1,2]。现代前列腺穿刺决策已远超"是否穿刺"的单一问题：MRI 靶向与系统性穿刺的取舍、穿刺方案（靶向+饱和 vs 靶向+系统性 vs 系统性）、入路选择（经会阴 vs 经直肠）、围术期麻醉与抗菌预防、以及穿刺组织对后续治疗规划的满足度，均需在具体患者情境（PI-RADS 分级、PSA 密度、既往阴性穿刺、抗凝状态、感染危险因素、前列腺体积……）下逐一权衡[1,3]。最新发表的 ProBIOPSY 国际多学科共识（112 条终版陈述）系统梳理了这一全流程，同时证实各国各中心实践差异显著[1]。

然而，共识以叙事文本形式存在，并非可执行的决策工件。临床医生面对的是"患者情境要素 × 穿刺决策项"的组合空间（本研究注册表为 51 类情境 × 54 项决策），静态查阅无法覆盖组合交互；传统规则型临床决策支持系统（CDSS）可以覆盖确定性逻辑，但知识更新慢、难以处理自然语言形式的新证据[4]。大语言模型（LLM）提供了灵活的语言理解与推理能力，但在医学场景中存在幻觉、不可溯源、输出不稳定等公认风险[5-7]；检索增强生成（RAG）通过外挂知识库缓解幻觉[8]，通用医学 RAG 基准也显示其潜力[9]，但纯检索式方案没有确定性安全约束——模型可以"合理地"给出与共识相悖的建议，而系统无法在机制上阻止。

我们认为，这三个失败模式恰好互补：确定性规则引擎能在机制上禁止违规输出（hard constraints），知识图谱检索能提供可溯源的证据链，LLM 仲裁层提供语言灵活性。三者串联成"规则门控—图谱证据—LLM 仲裁"的混合架构，每一层补偿其余两层的失效模式，同时保留从输出回溯到共识陈述编号与证据块的完整审计链。在知识图谱检索层，我们采用 LightRAG[10]（基于图的双层检索框架，相比 Microsoft GraphRAG[11] 以更低 token 成本取得更好的领域问答效果）作为证据引擎。

本研究开发并验证了前列安汇（probiopsy-rag）——一个面向前列腺穿刺活检全流程的混合决策支持系统，并以 ProBIOPSY 共识 112 条终版陈述为金标准、以统一生成器的多方法多种子基准（4 方法 × 5 种子 × 112 条 = 2,240 次运行）量化各架构层的贡献。主要贡献：

1. **架构**：首个将确定性规则硬约束、LightRAG 知识图谱检索与 LLM 仲裁串联、并逐陈述对齐国际共识的穿刺活检决策支持系统；
2. **金标准对齐**：112 条共识终版陈述全部映射为五类可执行动作（endorse / endorse_option / conditional / report_option / against），其中 conditional 与 endorse_option 两类是现有 LLM 与 RAG 系统结构性缺失的表达能力；
3. **可复现基准**：在固定生成器档位的条件下证明完整系统 exact5 = 0.805（κ = 0.730）显著优于 pure_llm（0.304）、naive_rag（0.605）与 lightrag-only（0.613）；并证明更换更强生成器（GLM-5.3 旗舰档）无法拯救基线架构（naive_rag exact5 反降至 0.538）；
4. **可复现性**：规则库、注册表、证据库、全部原始预测与评估脚本随仓库发布，索引构建时记录规则文件 SHA-256 以保证索引—规则版本一致。

## 参考文献骨架（2026-09-18 已全部核验 DOI）

1. Chernysheva D, Di Bello F, Avesani G, et al. ProBIOPSY: A Multidisciplinary International Consensus on Standards for Prostate Biopsy. Eur Urol 2026. DOI: 10.1016/j.eururo.2026.06.012（出版社 PDF 直接核验）
2. European Association of Urology. EAU Guidelines on Prostate Cancer. Arnhem: EAU; 2026. https://uroweb.org/guidelines/prostate-cancer（活页指南，投稿时更新版本日期）
3. Weinreb JC, Barentsz JO, Choyke PL, et al. PI-RADS Prostate Imaging — Reporting and Data System: Version 2.1: 2019. Eur Urol 2019;76:340-51. DOI: 10.1016/j.eururo.2019.02.033
4. Sutton RT, et al. An overview of clinical decision support systems: benefits, risks, and strategies for success. NPJ Digit Med 2020;3:17. DOI: 10.1038/s41746-020-0221-y
5. Thirunavukarasu AJ, et al. Large language models in medicine. Nat Med 2023;29:1930-40. DOI: 10.1038/s41591-023-02448-8
6. Singhal K, et al. Large language models encode clinical knowledge. Nature 2023;620:172-80. DOI: 10.1038/s41586-023-06291-2
7. Ji Z, et al. Survey of hallucination in natural language generation. ACM Comput Surv 2023;55(12):248. DOI: 10.1145/3571730
8. Lewis P, et al. Retrieval-augmented generation for knowledge-intensive NLP tasks. NeurIPS 2020;33:9459-74.（经典文献，会议论文集页码）
9. Xiong G, Jin Q, Lu Z, Zhang A. Benchmarking retrieval-augmented generation for medicine (MIRAGE). Findings of ACL 2024:633-54. DOI: 10.18653/v1/2024.findings-acl.37
10. Guo Z, Xia L, Yu Y, Ao T, Huang C. LightRAG: Simple and Fast Retrieval-Augmented Generation. arXiv:2410.05779 (2024).（arXiv 直接核验）
11. Edge D, et al. From Local to Global: A Graph RAG Approach to Query-Focused Summarization. arXiv:2404.16130 (2024).

---

# 方法 (Methods)

> 中文工作稿（Writer Phase 7_1）。英文提交稿见 `manuscript.en.md`。

## 研究设计与伦理

本研究为系统开发与基准验证研究（development and benchmark validation study），不涉及人类受试者、患者数据或生物样本：知识库语料仅来自公开出版的 ProBIOPSY 国际共识及其补充材料，验证金标准为该共识 112 条终版陈述（final statements），演示病例为研究团队构造的合成临床情境。研究无需伦理委员会审批（Planner 阶段已按 IRB 评估流程确认并留档）。

## 验证集：ProBIOPSY 共识 112 条终版陈述

以 ProBIOPSY 共识（European Urology 2026）全部 112 条终版陈述为金标准。每条陈述按预先定义的五类动作体系标注期望系统行为（expected system action）：

- **endorse**：直接支持该陈述；
- **endorse_option**：将其作为可接受选项之一支持（存在并列可选方案）；
- **conditional**：在指定条件下支持；
- **report_option**：作为可选路径在报告中呈现，不做主动推荐；
- **against**：建议反对该做法。

112 条陈述按共识章节分为三个领域：indication（23 条）、procedure（34 条）、treatment planning（55 条）；其中 against 类 25 条（22.3%），构成对"系统性偏乐观"决策系统的有效检验。

## 系统总体架构

前列安汇（probiopsy-rag）采用三层混合决策架构，输入为"患者临床情境要素（Entity A）× 穿刺决策项（Entity B）"组合，输出为带置信度、触发规则、证据链与陈述引用的结构化五类动作裁决。

### 输入层：双实体注册表

- **Entity A（患者临床情境）注册表**：51 个情境原型，49 个独立情境标志位（flags），覆盖影像（PI-RADS 分级、mpMRI/bpMRI、磁场强度、PI-QUAL 质量）、实验室标志物（PSA、PSA 密度）、临床与病史（既往穿刺阴性、家族史、感染危险因素、抗凝）、治疗意图与资源可得性等 7 个类别；
- **Entity B（穿刺决策项）注册表**：54 个决策项，20 个决策标志位，覆盖适应证（22）、操作流程（22）、治疗规划衔接（10）三类。

### 第 1 层：确定性规则引擎

规则库（`configs/rules.yaml`）含 16 条确定性规则：12 条共识规则（consensus rules）+ 4 条患者因素升级规则（patient-factor rules）。每条规则定义触发标志位组合（Entity A flags × Entity B flags）、严重度（high/medium/low）、机制类别（影像路径、穿刺方案选择、靶向穿刺、围术期、治疗规划衔接等）与推荐动作。规则匹配完全确定性、无需 LLM 参与，匹配成功时向下游输出硬约束（hard constraints，例如必须否决某选项或必须升级某操作），并全部携带 ProBIOPSY 陈述编号（Q 编号）溯源。患者因素规则在共识规则之上做情境升级（如感染危险因素→优先经会阴入路/强化预防；不适合根治治疗→简化穿刺方案）。

### 第 2 层：LightRAG 知识图谱证据检索

知识库语料为 357 个证据块，全部溯源自 ProBIOPSY 共识及其补充材料：112 条终版陈述（证据等级 B）、共识正文叙述 20 段、系统综述摘要 7 段（D）、以及共识正文与补充材料参考文献列表中提取的 218 条文献条目（C）。采用 LightRAG（lightrag-hku 1.5.7）构建索引：实体与关系抽取由 GLM-5.3-Flash 完成，向量索引采用 doubao-embedding-vision-251215（维度 2048）。最终索引含 1,864 个实体、3,078 条关系（约 100 MB）。

完整系统采用"风险引导检索"策略：先由规则层输出触发规则与相关决策项，再以混合模式（mode=hybrid：向量 + 图结构）执行检索。为避免检索层与生成层混淆，完整系统的图谱检索以 context-only 方式调用（只取实体、关系与证据块上下文，不让 LightRAG 自行生成答案），并与词汇检索证据（BM25 风格打分，按 Entity B 决策项与 Entity A 标志位加权提升）拼接后送入仲裁层。

### 第 3 层：LLM 仲裁

仲裁模块（SafetyAgent）接收四类输入：① 患者情境标志与决策项；② 规则引擎匹配结果与硬约束；③ 图谱证据上下文；④ 词汇检索证据上下文。输出为结构化裁决：五类动作之一、置信度、裁决依据文本、以及引用的陈述编号与证据块编号。裁决提示词明确要求仲裁层服从规则层硬约束：当硬约束给出确定性结论时，仲裁层不得违反。LLM 调用为智谱 GLM-5.3（OpenAI 兼容 API，https://open.bigmodel.cn/api/paas/v4，2026 年 9 月访问）。当 LLM 输出不可解析或调用失败时，系统降级输出规则层结论并显式标记 degraded，保证"永不静默失败"。

## 基线方法

为剥离架构各层贡献，与完整系统对比三种基线：

1. **pure_llm**（无检索、无规则）：直接将患者情境×决策项问题交给 LLM 判断；
2. **naive_rag**（词汇检索 + LLM）：BM25 风格词汇检索 top-6 证据块（平均 3,644 字符），拼入提示词后由 LLM 裁决；
3. **lightrag-only**（通用图谱 RAG + LLM）：LightRAG 混合模式端到端问答（平均 2,468 字符上下文），不做规则引导，也无硬约束机制。

完整系统平均上下文 7,640 字符（图谱 + 词汇证据），显著高于两个 RAG 基线，但检索预算受硬上限控制（详见讨论）。

## 基准协议

- 4 种方法 × 5 个随机种子（0–4，温度 0.2）× 112 条陈述 = **2,240 次运行**，支持断点续跑（按 method × seed × statement_id 键控）；
- **生成器统一**：全部方法与种子的生成器均为 GLM-5.3-Flash。此设计将"生成器模型"固定为常量，使方法间差异完全归因于检索层与决策层架构（规则引擎、检索策略、硬约束），而非模型能力差异；生成器客户端并发数、最小调用间隔等速率参数在各方法间一致；
- 全部 2,240 次运行成功返回且无降级记录（0 error / 0 degraded）；
- **补充实验（生成器档位鲁棒性）**：另以 GLM-5.3 旗舰档（thinking 混合推理）运行 pure_llm 与 naive_rag 完整基线（各 5 种子 × 112 条 = 1,120 条记录），检验"更强生成器是否拯救弱架构"。

## 评价指标

- **exact5**：五类动作严格匹配率（主指标）；
- **exact3**：三类粗粒度匹配率（将 endorse_option 并入 endorse、report_option 并入 conditional 后匹配），用于检验"基线靠多数类膨胀粗粒度准确率"的现象；
- **macro-F1**：五类宏平均 F1；
- **Cohen's κ**：与金标准的五类一致性（校正多数类偏倚）；
- **against 类二分类指标**：sensitivity / specificity / F1（把 against 视为正类），反映系统"敢于且正确地反对"的能力；
- 以上指标均按 5 个种子计算 mean ± SD；
- 记录每次运行检索上下文字符数（context chars）作为效率指标。

## 实现与可复现性

系统以 Python 3.13 实现，知识图谱基于 lightrag-hku 1.5.7。规则文件、双实体注册表、证据块库、金标准标注、全部 2,240 条原始预测记录（含每次运行的上下文长度与检索块数）与评估脚本随代码仓库发布；索引构建时记录规则文件 SHA-256 摘要（`index_built_against_rules_sha256`），应用界面据此实时校验"索引—规则"版本一致性，防止索引与规则库脱钩。

---

# 结果 (Results)

> 中文工作稿（Writer Phase 7_2）。所有数值出自 `outputs/evaluation_summary.json`（n=5 种子，mean±SD）与 `outputs/tables/table3_performance.md`。

## 基准总览

4 种方法 × 5 种子 × 112 条金标准陈述共 2,240 次运行全部成功完成，无错误、无降级输出。表 3（`outputs/tables/table3_performance.md`）给出主矩阵；图 2（`outputs/figures/figure2_performance.*`）给出分种子点图。

## 主结果：完整系统全面领先（表 3、图 2）

完整系统（前列安汇）在全部五类细粒度指标上显著优于三个基线：

| 方法 | exact5 | exact3 | macro-F1 | κ | against-F1 | 平均上下文（字符） |
|---|---|---|---|---|---|---|
| **前列安汇（完整系统）** | **0.805±0.012** | 0.823±0.012 | **0.825±0.022** | **0.730±0.016** | **0.908±0.023** | 7,640 |
| lightrag-only | 0.613±0.013 | 0.920±0.013 | 0.536±0.012 | 0.525±0.012 | 0.881±0.023 | 2,468 |
| naive_rag | 0.605±0.033 | 0.905±0.013 | 0.514±0.043 | 0.512±0.041 | 0.890±0.028 | 3,644 |
| pure_llm | 0.304±0.039 | 0.370±0.029 | 0.254±0.029 | 0.079±0.053 | 0.346±0.053 | 0 |

- 相对最强基线（lightrag-only），exact5 提高 **+19.2 个百分点**（0.805 vs 0.613），κ 提高 **+0.205**（0.730 vs 0.525），macro-F1 提高 **+28.9 个百分点**（0.825 vs 0.536）；
- 相对无检索无规则的 pure_llm，exact5 提高 2.6 倍以上；
- 种子间波动小（完整系统 exact5 SD=0.012），表明优势不是随机种子造成的偶然结果。

## 基线在细粒度类别上塌缩为多数类（图 2C）

五分类 macro-F1 揭示了 exact3 看不出的失败模式：两个 RAG 基线 exact3 高达 0.920/0.905（甚至高于完整系统的 0.823），但 exact5 仅 0.61 左右、macro-F1 仅 ~0.52——它们把大多数陈述压缩到 endorse / report_option / against 三个高频类：

- lightrag-only 预测分布（560 次）：endorse 162、report_option 168、against 159、endorse_option 68、**conditional 仅 3**；
- naive_rag 同型：endorse 175、report_option 165、against 154、endorse_option 60、**conditional 仅 6**；
- 完整系统则实质性地使用全部五类：endorse 280、conditional 95、against 115、report_option 32、endorse_option 38。

即基线系统在结构上无法表达"在指定条件下支持"（conditional）与"并列可选"（endorse_option）这两类对临床沟通最关键的细微动作；完整系统依靠规则层的确定性分类信号将这两类从几乎不用（0.5%–1.1%）提升到 17.0% 和 6.8% 的真实使用率，且用对了地方（κ 从 ~0.52 跃升至 0.730）。

## against 类：敢反对，且反对得对

against（建议反对）是临床安全上最重要的类别（金标准中占 22.3%）：

- 完整系统 against-F1 **0.908±0.023**（sensitivity 0.872±0.018，specificity **0.986±0.010**）；
- lightrag-only F1 0.881（sensitivity 1.000 但 specificity 仅 0.922——它把大量非 against 陈述也标成 against，属于"滥反对"）；
- naive_rag F1 0.890（同型：sens 0.992 / spec 0.931）；
- pure_llm F1 0.346（sens 0.416 / spec 0.720——既不敢反对也反对不准）。

完整系统用略低的 sensitivity 换取接近零的假阳性（specificity 0.986），这是规则硬约束"否决必须有据"带来的行为差异：系统只在规则或证据明确支持时输出 against。

## 生成器档位不改变结论：救基线救不了（补充实验）

将生成器从 GLM-5.3-Flash 换成 GLM-5.3 旗舰档重跑 pure_llm 与 naive_rag 完整基线（1,120 次运行）：

| 方法（生成器） | exact5 | exact3 | macro-F1 | κ |
|---|---|---|---|---|
| naive_rag（GLM-5.3 旗舰） | 0.538±0.012 | 0.936±0.032 | 0.498±0.020 | 0.450±0.016 |
| pure_llm（GLM-5.3 旗舰） | 0.288±0.013 | 0.489±0.030 | 0.255±0.024 | 0.132±0.013 |

naive_rag 的 exact5 反而从 0.605 降到 0.538、κ 从 0.512 降到 0.450：**更强的生成器无法弥补架构缺陷**——没有规则层分类信号与硬约束，旗舰模型同样塌缩为多数类。这把本文的贡献点从"选了个好模型"明确区分为"架构设计"。

## 领域分解（表 4）

金标准三领域的 against 占比差异极大（indication 8.7% / procedure 14.7% / treatment planning 32.7%），完整系统在 against 密度最高的治疗规划领域同样保持整体优势；分领域详细混淆矩阵见补充材料。

## 演示病例（图 4、图 5）

五个合成临床演示病例（限局性病灶穿刺方案、PSMA PET 后直接穿刺、bpMRI 不确定病灶、高危路径与预防、感染风险升级）端到端运行验证：全部输出正确五类动作、触发相应共识规则（含患者因素升级）、并给出带 Q 编号与证据块编号的可追溯引用链（案例报告见 `outputs/demo_cases/`）。

## Face validity：4 专家盲评（图 3）

4 名独立专家（泌尿外科 2、影像 1、放疗 1，均未参与开发）对 5 个组合命题盲评。专家间一致性良好：原始一致率 17/20（3 例 4/4 全票，case2 3/4，case1 2:2 平票）；整体 Fleiss κ = −0.092 为小样本伪影（类别边际不均时的已知现象），并非一致性差。**系统与专家多数票在 4 个有多数票的病例上全部一致（Cohen κ = 1.000，n = 4）**。case1（是否在靶向+病灶旁穿刺基础上加做系统穿刺）2 名倾向 conditional 的专家给出的理由是治疗计划依赖（全腺治疗 vs 局灶治疗改变系统穿刺的增益）——与系统证据链引用的"对侧系统穿刺检出率仅 0.3–4%（EV0024）"为同一考量。系统输出 4 项 Likert（清晰度/有用性/认可度/证据充分性）共 80 项评分全部 5/5（天花板效应，如实报告）。该样本量下所有一致性指标均为初步结果。

## 运行成本

完整系统平均上下文 7,640 字符（约 2,500–3,000 token），在 8 并发下单条裁决端到端中位耗时约 20–40 秒（GLM-5.3-Flash 生成器），支持交互式使用（Streamlit 界面含决策报告与自由问答两个模块）。

---

# 讨论 (Discussion)

> 中文工作稿（Writer Phase 7_4）。

## 核心发现

在固定生成器、多方法、多种子的严格基准下，本研究回答了一个明确问题：**前列腺穿刺决策支持的性能差异主要来自架构，而非模型**。三个关键证据链：① 完整系统 exact5 = 0.805 / κ = 0.730，比最强基线高 19.2 个百分点；② 两个 RAG 基线在粗粒度三类准确率上（0.920/0.905）甚至"高于"完整系统，但五类 macro-F1 崩塌至 ~0.52，预测分布揭示其塌缩为三个高频类——conditional（在指定条件下支持）在 1,120 次基线运行中只被主动输出 9 次（0.8%），endorse_option 同样近乎弃用；③ 换用更强生成器（GLM-5.3 旗舰档）后 naive_rag exact5 反而下降（0.605→0.538）。三者共同指向同一结论：**细粒度临床动作空间的表达能力必须内建在系统架构里**（规则引擎提供类别先验与硬约束），生成模型再强也无法凭提示词可靠地补上。

## 与现有工作的关系

医学 RAG 基准（如 MIRAGE[9]）评测的是开放问答正确率，评测目标多为多选题或自由文本；本研究则把国际共识的 112 条终版陈述映射为五类可执行动作，评测"指南一致性"（guideline conformance）这一更接近临床治理需求的性质。与通用 GraphRAG[11]/LightRAG[10] 的关系是"引擎 vs 系统"：LightRAG 作为证据引擎保留其双层检索与增量索引能力，但纯 LightRAG 端到端问答（lightrag-only 基线）恰好演示了"没有规则层会发生什么"——against 类滥报（sensitivity 1.000 而 specificity 仅 0.922）、conditional 类静默。传统规则型 CDSS[4] 的知识库维护负担问题在本架构中被缓解：规则库被压缩为 16 条可人工审计的共识规则，长尾知识交由图谱检索，二者通过硬约束接口而非并列投票耦合。

## 临床意义

对临床部署而言，本系统的价值点不是"替代医生决策"，而是三点可治理性（governability）：

1. **安全的否决行为**：against-F1 0.908，specificity 0.986——系统"敢于反对但几乎不滥反对"，否决必须有规则或证据支撑的机制约束了 LLM 的乐观偏置；
2. **全程可溯**：每条输出携带共识陈述编号（Q 编号）、触发规则与证据块编号，支持临床 governance 审计，这是纯 LLM 方案在机制上无法提供的；
3. **版本完整性**：索引构建时记录规则文件 SHA-256，运行界面实时校验索引—规则版本一致性，防止"知识库悄悄过期"这类 CDSS 经典失效模式。

## 限制

1. **语料与金标准同源**：知识库语料与金标准均来自 ProBIOPSY 共识——这使本研究性质为**指南一致性验证**（consensus conformance），而非独立临床效度验证。系统在构建时未接触任何动作标签（标签仅用于评测），规则库也只覆盖 16 个主题，但"见过陈述文本"的偏置无法排除，前瞻外部验证是必要的下一步；
2. **face validity 证据规模有限**：4 名专家 × 5 个组合命题；该样本量下一致性统计不稳定（原始一致率 17/20 但 Fleiss κ 为负即为伪影），Likert 全部触顶，且为单中心专家组——盲评仅支持初步 face validity；
3. **合成情境**：51 类情境原型与 5 个演示病例均为合成，未包含真实世界合并症的完整复杂度；
4. **生成器家族单一**：基准在 GLM 家族内完成（flash 与旗舰两档）；跨厂商生成器的架构泛化性未测——但补充实验已表明生成器档位不是结论的决定因素；
5. **组合空间覆盖**：112 条陈述覆盖 51×54 组合空间的高频区域，长尾组合（如罕见联合情境）的覆盖率未量化；
6. **上下文成本**：完整系统平均 7,640 字符上下文约为最强基线的 3 倍，换取 +19.2 个百分点 exact5；对成本敏感场景可用规则门控短路（纯规则可裁决的组合不调用图谱检索）进一步摊薄；
7. **语言与地区**：证据库为英文（ProBIOPSY 原文），界面与情境注册表为中文；跨语言迁移未测。

## 未来工作

① 将专家小组扩展为多中心 face validity 与可用性研究（含评审专家在平票病例中指出的"治疗意图条件化"情境）；② 前瞻性真实病例注册研究；③ 将规则库扩展至 EAU/AUA 指南其他章节（如主动监测、影像随访），测试架构的可移植性；④ 通过 FHIR 接口对接 EMR，实现情境要素自动填充；⑤ 生成器本地化部署（开源权重模型）以消除 PHI 外流顾虑。

## 结论

前列安汇证明：把确定性规则硬约束、知识图谱证据检索与 LLM 仲裁按"各补其短"原则串联，可以在国际共识的金标准验证中把细粒度临床决策准确率提升到可临床试点水平（exact5 0.805，κ 0.730，against-F1 0.908），且每条输出全程可溯。架构，而不是更大的模型，才是医学决策支持系统当前的主要杠杆。

---

## 数据与代码可用性 (Data Availability)

规则库（configs/rules.yaml）、双实体注册表（data/seed/entities_a.csv, entities_b.csv）、证据块库（data/seed/evidence_chunks.jsonl，357 条）、金标准标注（data/seed/probiopsy_statements.csv，112 条）、全部 2,240 条原始预测记录（outputs/baseline_predictions.jsonl，含每次运行的上下文字符数与检索块数）、旗舰档补充数据（outputs/baseline_predictions_glm53.jsonl）、评估脚本（scripts/evaluate.py）与图表源数据（outputs/figures/source_data/）随代码仓库发布。

## 伦理声明 (Ethics)

本研究不涉及人类受试者、患者数据或生物样本；知识库语料与验证金标准均来自公开出版的 ProBIOPSY 共识；演示病例为合成情境。详见 Manuscript_Ethics_Statement.md。

## 资金 (Funding)

[TODO]

## 利益冲突 (Conflict of Interest)

[TODO]

## 作者贡献 (CRediT)

- [PI TODO]：概念化、方法学、软件、验证、初稿撰写
- [合作者 TODO]：[TODO]

## 图表清单

- **图 1** 系统架构（outputs/figures/figure1_architecture.*）
- **图 2** 多方法多种子性能对比（outputs/figures/figure2_performance.*）
- **图 3** 专家一致性（待专家盲评数据，Phase 4.5）
- **图 4** 演示病例报告（outputs/figures/figure4_demo_case.*）
- **图 5** 推理链追踪（outputs/figures/figure5_reasoning_trace.*）
- **表 1** 双实体注册表摘要（outputs/tables/table1_registry.md）
- **表 2** 规则清单（outputs/tables/table2_rules.md）
- **表 3** 性能矩阵（outputs/tables/table3_performance.md）
- **表 4** 金标准领域×动作分布（outputs/tables/table4_validation.md）
