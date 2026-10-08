## Patient consultation 1 (verbatim)

**Patient question (Chinese):** 医生，我穿刺结果是良性的，是不是以后就不用管了，也不用再查PSA了？

**Matched fact entries:** edu_negative_result, edu_biopsy_sampling — sources: probiopsy (ProBIOPSY consensus, Chernysheva et al., Eur Urol 2026); eau_guideline (EAU Prostate Cancer Guidelines, uroweb.org, living guideline); borghesi_comp (Borghesi et al., complications after prostate biopsy, Eur Urol 2017); probiopsy (ProBIOPSY consensus, Chernysheva et al., Eur Urol 2026); eau_guideline (EAU Prostate Cancer Guidelines, uroweb.org, living guideline)

**Retrieval:** 6 evidence chunks (frozen benchmark corpus) + knowledge-graph context (context-only mode)

**Agent answer (Chinese, verbatim):**

您好，先说结论：穿刺报告是良性的确是个好消息，但“良性”不等于“以后就不用管了”。

1. 良性结果的意思是：这次取出来的那些组织样本里，没有发现癌细胞。它不代表前列腺一辈子都不会长癌 [edu_negative_result]。
2. 穿刺是一种“抽样”检查：医生用很细的针，从前列腺里取出少量组织条，由病理科医生放在显微镜下看。它只能检查取到的那一部分，看不了整个前列腺，所以结果正常也不能百分之百排除癌症 [edu_biopsy_sampling]。
3. 又小、又藏得深的肿瘤有可能没被针取到；还有些异常是以后才出现、或慢慢发展起来的 [edu_negative_result]。
4. 所以PSA抽血检查（PSA就是“前列腺特异抗原”，一种通过验血反映前列腺情况的指标）和体格检查，还需要按泌尿科医生给您安排的时间继续做。医生有时还会参考“PSA密度”（PSA数值除以前列腺体积）这类指标，来判断要不要做进一步检查 [edu_negative_result][证据5]。如果医生仍然有怀疑，可能会建议做磁共振（MRI，一种给前列腺做详细成像、不用开刀的检查），或者再做一次穿刺 [edu_negative_result]。

什么情况要及时就医：即使您自我感觉很好，也要按时复诊、按时抽血查PSA [edu_negative_result]。如果PSA又升高了，或者身体出现新的症状、新的不舒服，不要等到下一次预约的时间，请尽早联系您的主诊泌尿科医生 [edu_negative_result]。另外，如果您对报告内容或穿刺过程有任何不清楚的地方，也可以请医生把报告“一条一条、一针一针”地给您讲解 [edu_biopsy_sampling]。

最后提醒一句：每个人的情况都不同，建议您带着穿刺报告，和您的主诊泌尿科医生一起商量出属于您自己的复查计划。

**Timings:** graph 42.0s · lexical 0.00s · generation 48.4s
