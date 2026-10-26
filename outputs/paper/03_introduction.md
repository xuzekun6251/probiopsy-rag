# 引言 (Introduction)

> 中文工作稿（Writer Phase 7_3；2026-10-11 引言整体替换为去重润色版）。2026-10-12：12 条参考文献经 Crossref/arXiv API 逐条复核，更正 MIRAGE（DOI 与页码，原误作 2024.findings-acl.37/633-54）与 PI-RADS v2.1（第一作者，原误作 Weinreb）两处条目错误，并按正文首次出现次序重新编号；编号为本稿编号，与英文稿 manuscript.en.md 不同。2026-10-26：引言补入疾病负担与"穿刺是治疗决策入口"临床开篇，新增 GLOBOCAN、中国癌症负担、ERSPC 三条文献（Crossref 复核），全部编号顺移为 16 条。

前列腺癌是男性最常见的恶性肿瘤之一，也是男性癌症相关死亡的主要原因之一[1,2]；人群层面的 PSA 筛查能够降低疾病特异性死亡率[3]。而 PSA 升高之后，真正决定患者走向的是穿刺：穿刺发现的肿瘤分级、负荷与空间分布，决定了一名患者此后是进入主动监测、接受局灶治疗，还是接受根治性治疗——穿刺是前列腺癌每一个治疗决策的入口。这个入口处的当代目标是一个三难权衡：提高临床显著前列腺癌（clinically significant prostate cancer, csPCa）的检出、控制穿刺相关并发症、避免对低获益人群的过度穿刺。三项指标此消彼长，而穿刺本身又是多步骤、高度依赖术者主观判断的过程：系统穿刺与 MRI 靶向穿刺如何组合、是否饱和、经会阴抑或经直肠入路，目前均无唯一答案。ProBIOPSY 国际共识对这些决策点逐一表决，同时记录了各国各中心间显著的实践差异（Chernysheva 等，Eur Urol 2026）[4]。标准化的缺口是真实的，而且精确地落在每一个决策点上。

患者侧的困难同样制约着穿刺路径的效率。医疗资源分布不均、部分患者缺少可靠的信息渠道、健康素养参差不齐，使一部分本应尽快穿刺的可疑前列腺癌患者在"建议"与"治疗"之间滞留。此时患者面临双重不利：疾病本身带来高度的不确定与脆弱，而支撑决策的关键信息，即穿刺为什么必要、报告如何解读、下一步意味着什么，又以专业语言写成。弥合这一鸿沟的常规途径是医患沟通，但这类对话耗时且难以计价，在紧凑的门诊议程中经常让位于优先级更高的诊疗任务；当医疗资源紧张时，它往往第一个被划去。结果是：最终承担决策的患者，得不到与决策相称的教育支持。

新兴证据显示，大语言模型能够就前列腺穿刺活检与前列腺癌相关问题给出高质量、具备临床相关性的回答（如基于电子病历系统个性化前列腺癌患者教育的 LLM 智能体研究 [5]）。但放进穿刺决策与患者教育这两个具体任务，通用 LLM 的四重落差各有其临床对应物：知识失真（幻觉）对应一条指南里并不存在的"推荐"，落到患者身上可能就是一次不必要的穿刺及其并发症；结论无法回溯到指南原文（不可溯源），医生既无法在决策前核对，也无法在事后复核中自证；语言对非专业读者不够友好（可读性），患者教育就停在字面上、进不到心里；输出随提问方式波动（不稳定），同一位患者在两次提问之间可能得到两个不同的方案[6-8]。这些落差无法靠提示词修补，需要架构级对策：确定性约束防止越界输出，检索使结论可回溯，生成提示控制语言层级并明确安全边界。

为弥合上述双重缺口，本研究基于 ProBIOPSY 国际共识（112 条最终陈述）[4] 构建了前列安汇（QianLieAnHui）决策支持智能体。系统由三层串联而成：16 条确定性规则（与 EAU、AUA/ASTRO 指南交叉核对）在机制上禁止与共识相悖的输出；LightRAG [9] 知识图谱与词法证据库构成双层检索，使每条建议都能回溯到编号证据；GLM 仲裁器在硬约束解码下输出五类可执行动作之一，并附陈述级引用。患者教育模式复用同一冻结证据基座，将患者提问与十条逐项可溯源的策展事实匹配，以通俗语言生成包含"何时须就医"安全提示的回答，并将患者引导回其主管医生。设计目标不是替代沟通，而是把重复性的解释工作从临床时间中卸载，把共同决策的时间留给真正需要权衡的决策；这对健康素养有限的患者尤为重要。

系统价值经两条独立线索初步验证：在 2,240 次运行的基准（4 种架构 × 5 个随机种子 × 112 条陈述）中，细粒度裁决准确率 exact-5 0.805±0.012、Cohen's κ 0.730、against-F1 0.908，较最强基线高 19.2 个百分点；患者教育模式经三例真实咨询完成定性演示（详见结果部分与补充材料 S7）。

## 参考文献骨架（编号按正文首次出现次序；2026-10-12 经 Crossref/arXiv API 全部复核，更正两处条目；2026-10-26 新增 1–3 三条并整体顺移）

1. Bray F, Laversanne M, Sung H, et al. Global cancer statistics 2022: GLOBOCAN estimates of incidence and mortality worldwide for 36 cancers in 185 countries. CA Cancer J Clin 2024;74:229-63. DOI: 10.3322/caac.21834（2026-10-26 Crossref 复核）
2. Cao W, Chen HD, Yu YW, et al. Changing profiles of cancer burden worldwide and in China: a secondary analysis of the global cancer statistics 2020. Chin Med J 2021;134:783-91. DOI: 10.1097/cm9.0000000000001474（2026-10-26 Crossref 复核）
3. Schröder FH, Hugosson J, Roobol MJ, et al. Prostate-cancer mortality at 11 years of follow-up. N Engl J Med 2012;366:981-90. DOI: 10.1056/NEJMoa1113135（2026-10-26 Crossref 复核）
4. Chernysheva D, Di Bello F, Avesani G, et al. ProBIOPSY: A Multidisciplinary International Consensus on Standards for Prostate Biopsy. Eur Urol 2026;90(3):212–224. DOI: 10.1016/j.eururo.2026.06.012（Crossref 元数据核验，2026-09-22；2026-10-12 复核；原编号 1）
5. Hao Y, Holmes J, Waddle MR, et al. Personalizing prostate cancer education for patients using an EHR-integrated LLM agent. npj Digit Med 2025;8:770. DOI: 10.1038/s41746-025-02166-0（英文稿文献 36，2026-10-12 复核；原编号 2）
6. Thirunavukarasu AJ, et al. Large language models in medicine. Nat Med 2023;29:1930-40. DOI: 10.1038/s41591-023-02448-8（2026-10-12 复核；原编号 3）
7. Singhal K, et al. Large language models encode clinical knowledge. Nature 2023;620:172-80. DOI: 10.1038/s41586-023-06291-2（2026-10-12 复核；原编号 4）
8. Ji Z, et al. Survey of hallucination in natural language generation. ACM Comput Surv 2023;55(12):248. DOI: 10.1145/3571730（2026-10-12 复核；原编号 5）
9. Guo Z, Xia L, Yu Y, Ao T, Huang C. LightRAG: Simple and Fast Retrieval-Augmented Generation. arXiv:2410.05779 (2024).（arXiv 直接核验，2026-10-12 复核；原编号 6）
10. Turkbey B, Rosenkrantz AB, Haider MA, et al. Prostate Imaging Reporting and Data System Version 2.1: 2019 Update of Prostate Imaging Reporting and Data System Version 2. Eur Urol 2019;76:340-51. DOI: 10.1016/j.eururo.2019.02.033（2026-10-12 更正第一作者：原误作 Weinreb JC；Weinreb 为 PI-RADS v2（2016）第一作者；原编号 7）
11. European Association of Urology. EAU Guidelines on Prostate Cancer. Arnhem: EAU; 2026. https://uroweb.org/guidelines/prostate-cancer（活页指南，投稿时更新版本日期；2026-10-12 链接复核；原编号 8）
12. Xiong G, Jin Q, Lu Z, Zhang A. Benchmarking retrieval-augmented generation for medicine (MIRAGE). Findings of ACL 2024:6233-6251. DOI: 10.18653/v1/2024.findings-acl.372（2026-10-12 更正 DOI 与页码：原误作 2024.findings-acl.37、633-54；原编号 9）
13. Lewis P, et al. Retrieval-augmented generation for knowledge-intensive NLP tasks. NeurIPS 2020;33:9459-74.（arXiv:2005.11401，2026-10-12 复核；原编号 10）
14. Edge D, et al. From Local to Global: A Graph RAG Approach to Query-Focused Summarization. arXiv:2404.16130 (2024).（arXiv 直接核验，2026-10-12 复核；原编号 11）
15. Sutton RT, et al. An overview of clinical decision support systems: benefits, risks, and strategies for success. NPJ Digit Med 2020;3:17. DOI: 10.1038/s41746-020-0221-y（2026-10-12 复核；原编号 12）
16. Tung JYM, et al. Performance of retrieval-augmented generation large language models in guideline-concordant prostate-specific antigen testing: comparative study with junior clinicians. J Med Internet Res 2025;27:e78393. DOI: 10.2196/78393（2026-10-26 Crossref 复核；作者提供的全文 PDF 与元数据一致；原编号 13）
