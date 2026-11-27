# JAMIA 投稿文件清单（本文件仅本地参考，不上传）

投稿系统：ScholarOne（mc.manuscriptcentral.com/jamia）· Article type: **Research and Applications** · 单盲评审（作者信息在正文内，无需匿名稿）。

| 文件 | ScholarOne 上传位置 | 说明 |
|---|---|---|
| manuscript_JAMIA.docx | Main Document | 正文（含标题页、摘要五段式 249 词、正文 3,987 词、4 张三线表、图注、58 条参考文献） |
| cover_letter_JAMIA.docx | Cover Letter | 投稿信；系统若只收文本，可从 cover_letter_JAMIA.md 复制粘贴 |
| supplementary_material_S1-S7.docx | Supplementary Material (File 1) | S1 混淆矩阵 / S2 旗舰档 / S3 演示病例 / S4 运行耗时 / S5 仲裁提示词 / S6 专家盲评 / S7 患者教育逐字稿 |
| figure1_architecture.tiff | Figures | 600 dpi |
| figure2_performance.tiff | Figures | 600 dpi（2026-11-27 修复 B 面板标注重叠后的最新版） |
| figure3_expert_agreement.tiff | Figures | 600 dpi |
| figure4_demo_case.tiff | Figures | 600 dpi |
| figure5_reasoning_trace.tiff | Figures | 600 dpi |
| DECIDE-AI_checklist.docx | Reporting checklist（如系统设有该项） | 完成的 DECIDE-AI 报告规范检查单 |

## 投稿前检查

1. 表单逐项填写：Funding = none；Competing interests = none；Data availability（稿内已有，GitHub + Zenodo）。
2. ORCID 关联通讯作者；作者信息核对（XU Zekun, xuzekunurology@163.com）。
3. 参考文献 [22]（EAU 活页指南）的访问日期更新为投稿当日。
4. 矢量图源（SVG/PDF）在 outputs/figures/，编辑部若要求可补交。
5. 重建本文件夹：先跑 scripts/build_jamia_docx.py，再跑 scripts/build_jamia_pkg.py。
