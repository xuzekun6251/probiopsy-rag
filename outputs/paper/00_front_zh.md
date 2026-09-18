# 前列安汇：规则引擎—知识图谱—LLM 仲裁混合决策支持系统在前列腺穿刺活检全流程中的开发与验证

**Development and benchmark validation of QianLieAnHui (前列安汇), a hybrid rule-engine / knowledge-graph / LLM-arbitration decision-support system for the prostate biopsy pathway, against the ProBIOPSY international consensus**

## 作者

[PI 姓名 TODO]<sup>1,\*</sup>，[合作者 TODO]

<sup>1</sup>[科室/单位 TODO]；<sup>\*</sup>通讯作者：[邮箱 TODO]

## 结构化摘要

**背景** 前列腺穿刺活检决策涉及影像质量、穿刺方案、入路、围术期预防与治疗规划衔接的多因素权衡；国际共识（ProBIOPSY，112 条终版陈述）以文本形式存在，无法直接执行。大语言模型（LLM）灵活但存在幻觉与不可溯源性，检索增强生成（RAG）可缓解但缺乏确定性安全约束。

**方法** 我们开发前列安汇：确定性规则引擎（12 条共识规则 + 4 条患者因素升级，输出硬约束）→ 风险引导的 LightRAG 知识图谱检索（357 个证据块、1,864 实体、3,078 关系，全部溯源自共识文本与参考文献）→ LLM 仲裁（输出五类动作：endorse / endorse_option / conditional / report_option / against，含置信度与 Q 编号引用链）。以 112 条共识终版陈述为金标准，在统一生成器（GLM-5.3-Flash）条件下进行 4 方法 × 5 种子 × 112 陈述 = 2,240 次运行的基准评测；另以 GLM-5.3 旗舰档重跑基线（1,120 次）检验生成器档位的影响。

**结果** 完整系统 exact5 = 0.805±0.012、macro-F1 = 0.825、κ = 0.730±0.016、against-F1 = 0.908（specificity 0.986），显著优于 lightrag-only（0.613 / 0.536 / 0.525 / 0.881）、naive_rag（0.605 / 0.514 / 0.512 / 0.890）与 pure_llm（0.304 / 0.254 / 0.079 / 0.346）。基线在细粒度类别上塌缩为高频类：conditional 在 1,120 次基线运行中仅被主动输出 9 次（0.8%），而完整系统为 17.0%。更换更强生成器后 naive_rag exact5 反而下降（0.605→0.538）。

**结论** 在医学决策支持系统中，细粒度临床动作空间的表达能力必须内建于架构（规则硬约束 + 类别先验），而非依赖提示词或更大模型。架构差异，而非模型档位，是性能的主要杠杆；系统输出全程可溯源至共识陈述与证据块，支持临床治理审计。

**关键词** 前列腺癌；穿刺活检；临床决策支持系统；知识图谱；LightRAG；检索增强生成；大语言模型；国际共识；ProBIOPSY
