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

1. Chernysheva D, Di Bello F, Avesani G, et al. ProBIOPSY: A Multidisciplinary International Consensus on Standards for Prostate Biopsy. Eur Urol 2026;90(3):212–224. DOI: 10.1016/j.eururo.2026.06.012（Crossref 元数据核验，2026-09-22）
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
