# 引言 (Introduction)

> 中文工作稿（Writer Phase 7_3；2026-10-11 引言整体替换为去重润色版）。2026-10-12：12 条参考文献经 Crossref/arXiv API 逐条复核，更正 MIRAGE（DOI 与页码，原误作 2024.findings-acl.37/633-54）与 PI-RADS v2.1（第一作者，原误作 Weinreb）两处条目错误，并按正文首次出现次序重新编号；编号为本稿编号，与英文稿 manuscript.en.md 不同。2026-10-26：引言补入疾病负担与"穿刺是治疗决策入口"临床开篇，新增 GLOBOCAN、中国癌症负担、ERSPC 三条文献（Crossref 复核），全部编号顺移为 16 条。2026-10-31：仿 Tung 等（JMIR 2025）引言范式重构——系统架构描述压缩进一段并移入方法部分，引言以研究目的收尾，不再预告结果；编号按新版式重新排序。2026-11-20：P3 补入 Sesen 等（BMJ Digit Health 2026）外部证据句，骨架新增一条文献（Crossref 复核）。同日按 Sesen 等引言范式重构：LLM 局限与检索—约束对策拆分为两段；新增"本文考察"段、报告框架界定段（TRIPOD+AI/DECIDE-AI：适用条目已对齐、外部验证与前瞻影响评估列为未来工作）与编号三项贡献段（含"现成组件组合"定位句）；骨架条目未增减，编号按新版式重排。

前列腺癌是男性最常见的恶性肿瘤之一，也是导致男性癌症死亡的主要原因之一[1,2]。人群水平的前列腺特异性抗原（PSA）筛查能够降低前列腺癌特异性死亡率[3]，而筛查发现 PSA 升高之后，患者后续能否得到及时规范的处理，在很大程度上取决于穿刺活检。现阶段前列腺穿刺活检的目标，是在提高有临床意义前列腺癌检出率的同时减少穿刺带来的并发症，并避免过度穿刺。然而前列腺穿刺是一个复杂的、多步骤、术者主观选择多样的过程，并且因为各地区、各医疗中心本身存在差异，穿刺技术仍有待进一步标准化：系统穿刺与磁共振成像（MRI）靶向穿刺如何组合、是否饱和穿刺、选择经会阴还是经直肠入路，目前均无统一答案。ProBIOPSY 国际共识对这些决策点逐一进行了表决，同时记录了各国各中心间显著的实践差异（Chernysheva 等，Eur Urol 2026）[4]，说明标准化的缺口真实存在，并且涉及每一个决策点。

患者侧的困难同样制约着穿刺路径的效率。医疗资源分布不均、部分患者缺少可靠的信息渠道、健康素养参差不齐，使一部分本应尽快穿刺的可疑前列腺癌患者在"建议"与"治疗"之间滞留。此时患者面临双重不利：疾病本身带来高度的不确定与脆弱，而支撑决策的关键信息，即穿刺为什么必要、报告如何解读、下一步意味着什么，又以专业语言写成。弥合这一鸿沟的常规途径是医患沟通，但这类对话耗时且难以计价，在紧凑的门诊议程中经常让位于优先级更高的诊疗任务；当医疗资源紧张时，它往往第一个被划去。结果是：最终承担决策的患者，得不到与决策相称的教育支持。

新兴证据显示，大语言模型（LLM）能够就前列腺穿刺活检与前列腺癌相关问题给出高质量、具备临床相关性的回答，例如基于电子病历系统开展前列腺癌患者个性化教育的 LLM 智能体研究[5]。但是将大语言模型用于穿刺决策和患者教育时，其局限性会带来实际的临床风险。模型可能编造指南中并不存在的推荐内容，医生如果不加甄别地采纳，患者可能因此接受一次不必要的穿刺。模型给出的结论无法回溯到指南原文，医生在决策前难以核对，事后也难以复核。面向患者的解释往往使用专业语言，健康素养有限的患者难以真正理解。此外，模型输出随提问方式波动，同一位患者在不同时间的提问可能得到不同的回答[6-8]。这些问题的根源在于模型本身，单靠调整提示词难以解决，需要在架构层面采取对策。

架构对策的核心是检索与约束。检索增强生成（RAG）把外部语料中检索到的证据交给生成模型，使输出可以回溯到来源[9]；生成提示则控制语言层级并明确安全边界。这一对策方向近期获得了外部证据：在慢性肾脏病指南问答的对照评估中，检索增强把医生评定的回答正确率从纯生成模型的 70.8% 提高到 76.6% 与 75.6%，但在语料未覆盖的问题上，检索反而使正确率从 1.00 降至 0.28 与 0.10[10]。检索只解决"依据从哪里来"，不解决"输出能否越界"：对一条与指南相悖但语言流畅的推荐，检索本身没有机制去禁止它。经典规则式临床决策支持恰恰相反——确定性足够，却难以跟上指南更新，也无法消化以自然语言写成的证据。因此，可用的系统需要三者互补：LLM 的语言灵活性、检索层的可溯源证据链、硬约束的确定性安全边界，让每一层堵住其余各层的失灵模式。

为弥合上述双重缺口，本研究基于 ProBIOPSY 国际共识（112 条终版陈述）[4] 构建了前列安汇（QianLieAnHui）决策支持智能体，把书面共识转化为决策点上可执行的清单：确定性规则引擎在机制上禁止与共识相悖的输出，基于图检索增强生成（GraphRAG，以 LightRAG [11] 实现）的知识图谱与词法证据库构成双层检索，使每条建议都能回溯到编号证据，LLM 仲裁器在硬约束下输出五类可执行动作并附陈述级引用；同一冻结证据链亦支撑面向患者与家属的通俗教育模式（系统与各层方法详见方法部分）。本文以这 112 条终版陈述为金标准，考察该混合架构所能达到的共识一致性、各架构层对性能的贡献，以及残留误判在检索层与仲裁层之间的分布。

报告框架方面，TRIPOD+AI [12] 与 DECIDE-AI [13] 分别为临床预测模型与 AI 决策支持系统的早期临床评估提供了报告规范；两项清单与一项决策支持智能体的架构级基准并不完全对应，凡适用的条目——模型与基准配置的透明报告、评估数据集的描述、局限性的声明——本稿均已在相应章节对齐，而真实世界数据上的外部验证与前瞻性临床影响评估不在本研究范围内，作为未来工作处理。

与既有工作相比，本研究做出三项贡献：（1）把一份国际共识的 112 条终版陈述本身转化为可执行的金标准与基准任务，在统一生成器下以 4 方法 × 5 种子 × 112 陈述共 2,240 次运行进行架构级评测，动作空间绑定共识表决语义；（2）利用词法检索的确定性，把全部完整系统运行分解为检索贡献与仲裁贡献，证据包对决策项的覆盖率为 100%，全部残留误判均定位在仲裁层，为下一步改进指明校准对象；（3）患者教育模式复用同一冻结证据链，提供逐项可溯源的通俗语言咨询（定性演示）。本研究并非提出新的检索或图谱架构，而是把规则引擎、GraphRAG 与提示式仲裁器等现成组件在架构级准则下组合，刻画在不具备专科自然语言处理团队的现实配置下所能达到的共识一致性水平——从概念验证走向临床可解读的评估。

## 参考文献骨架（编号按正文首次出现次序；2026-10-12 经 Crossref/arXiv API 全部复核，更正两处条目；2026-10-26 新增 1–3 三条并整体顺移）；2026-10-31 仿 Tung（JMIR 2025）版式重构后按正文首次出现次序重新编号；2026-11-20 新增 17–19 三条（Sesen BMJ Digit Health 2026；TRIPOD+AI；DECIDE-AI），均经 Crossref 复核；2026-11-21 按 Sesen 引言范式重构后按新版式重新编号

1. Bray F, Laversanne M, Sung H, et al. Global cancer statistics 2022: GLOBOCAN estimates of incidence and mortality worldwide for 36 cancers in 185 countries. CA Cancer J Clin 2024;74:229-63. DOI: 10.3322/caac.21834（2026-10-26 Crossref 复核）
2. Cao W, Chen HD, Yu YW, et al. Changing profiles of cancer burden worldwide and in China: a secondary analysis of the global cancer statistics 2020. Chin Med J 2021;134:783-91. DOI: 10.1097/cm9.0000000000001474（2026-10-26 Crossref 复核）
3. Schröder FH, Hugosson J, Roobol MJ, et al. Prostate-cancer mortality at 11 years of follow-up. N Engl J Med 2012;366:981-90. DOI: 10.1056/NEJMoa1113135（2026-10-26 Crossref 复核）
4. Chernysheva D, Di Bello F, Avesani G, et al. ProBIOPSY: A Multidisciplinary International Consensus on Standards for Prostate Biopsy. Eur Urol 2026;90(3):212–224. DOI: 10.1016/j.eururo.2026.06.012（Crossref 元数据核验，2026-09-22；2026-10-12 复核；原编号 4）
5. Hao Y, Holmes J, Waddle MR, et al. Personalizing prostate cancer education for patients using an EHR-integrated LLM agent. npj Digit Med 2025;8:770. DOI: 10.1038/s41746-025-02166-0（英文稿文献 36，2026-10-12 复核；原编号 5）
6. Thirunavukarasu AJ, et al. Large language models in medicine. Nat Med 2023;29:1930-40. DOI: 10.1038/s41591-023-02448-8（2026-10-12 复核；原编号 6）
7. Singhal K, et al. Large language models encode clinical knowledge. Nature 2023;620:172-80. DOI: 10.1038/s41586-023-06291-2（2026-10-12 复核；原编号 7）
8. Ji Z, et al. Survey of hallucination in natural language generation. ACM Comput Surv 2023;55(12):248. DOI: 10.1145/3571730（2026-10-12 复核；原编号 8）
9. Lewis P, et al. Retrieval-augmented generation for knowledge-intensive NLP tasks. NeurIPS 2020;33:9459-74.（arXiv:2005.11401，2026-10-12 复核；原编号 17）
10. Sesen MB, Au Yeung JA, Asgari E. Development and evaluation of Retrieval-Augmented Generation (RAG) and GraphRAG for guideline-based clinical decision support in chronic kidney disease. BMJ Digit Health 2026;2(1):e000041. DOI: 10.1136/bmjdh-2026-000041（2026-11-20 Crossref 复核）（原编号 9）
11. Guo Z, Xia L, Yu Y, Ao T, Huang C. LightRAG: Simple and Fast Retrieval-Augmented Generation. arXiv:2410.05779 (2024).（arXiv 直接核验，2026-10-12 复核；原编号 10）
12. Collins GS, Moons KGM, Dhiman P, Riley RD, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ 2024;385:e078378. DOI: 10.1136/bmj-2023-078378（2026-11-20 Crossref 复核）（原编号 13）
13. Vasey B, Nagendran M, Campbell B, Clifton DA, et al. Reporting guideline for the early stage clinical evaluation of decision support systems driven by artificial intelligence: DECIDE-AI. BMJ 2022;377:e070904. DOI: 10.1136/bmj-2022-070904（2026-11-20 Crossref 复核）（原编号 14）
14. Turkbey B, Rosenkrantz AB, Haider MA, et al. Prostate Imaging Reporting and Data System Version 2.1: 2019 Update of Prostate Imaging Reporting and Data System Version 2. Eur Urol 2019;76:340-51. DOI: 10.1016/j.eururo.2019.02.033（2026-10-12 更正第一作者：原误作 Weinreb JC；Weinreb 为 PI-RADS v2（2016）第一作者；原编号 11）
15. European Association of Urology. EAU Guidelines on Prostate Cancer. Arnhem: EAU; 2026. https://uroweb.org/guidelines/prostate-cancer（活页指南，投稿时更新版本日期；2026-10-12 链接复核；原编号 12）
16. Tung JYM, et al. Performance of retrieval-augmented generation large language models in guideline-concordant prostate-specific antigen testing: comparative study with junior clinicians. J Med Internet Res 2025;27:e78393. DOI: 10.2196/78393（2026-10-26 Crossref 复核；作者提供的全文 PDF 与元数据一致；原编号 15）
17. Xiong G, Jin Q, Lu Z, Zhang A. Benchmarking retrieval-augmented generation for medicine (MIRAGE). Findings of ACL 2024:6233-6251. DOI: 10.18653/v1/2024.findings-acl.372（2026-10-12 更正 DOI 与页码：原误作 2024.findings-acl.37、633-54；原编号 16）
18. Edge D, et al. From Local to Global: A Graph RAG Approach to Query-Focused Summarization. arXiv:2404.16130 (2024).（arXiv 直接核验，2026-10-12 复核；原编号 18）
19. Sutton RT, et al. An overview of clinical decision support systems: benefits, risks, and strategies for success. NPJ Digit Med 2020;3:17. DOI: 10.1038/s41746-020-0221-y（2026-10-12 复核；原编号 19）
