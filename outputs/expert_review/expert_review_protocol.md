# 专家盲评操作手册（PI 用）

**目标**：完成 pre-registered 的 4 专家 × 5 病例盲评（figure3 + 稿件 face-validity 段）。

## 0. 评审设计要点（v2，已修正）
- 每个病例以**陈述句决策项**（①②③…）呈现，评审命题 = **同时采纳全部决策项的组合方案**，
  与系统输出的判定对象完全一致（系统 verdict 即对该组合命题的总体动作）。
- 不使用「是否…」问句——五类动作评的是命题立场，不是是非题。
- 系统依据（rationale）中的分项立场（如支持①、拒绝②）属于 Part B 展示内容，
  Part A 不出现，保证盲评。

## 1. 专家入选（4 名）
- 建议构成：泌尿外科 ≥2、影像科 ≥1、放疗/肿瘤 ≥1；副高及以上；**未参与本项目开发**。
- 独立评审：专家之间不讨论、不同时填卷。

## 2. 评审流程（每位专家约 20–30 分钟）
1. 打印或发送 `expert_booklet.md`（PDF/纸质均可），每位一份。
2. 专家先完成**第一部分**：5 个病例各自的组合命题推荐动作（五选一）＋选填一句理由。
3. 第一部分收齐或专家自行翻页后，展示**第二部分**（系统 A 对同一命题的判定），填 4 项 Likert 1–5。
4. 盲评纪律：第一部分完成前不得翻看第二部分；booklet 中系统以「系统 A」匿名。

## 3. 回收与转录
- 方式 A（推荐）：把 4 份答卷拍照/打字发给我，我来转录。
- 方式 B：自行填写 `answer_worksheet.csv`（20 行，已建好行框架），列含义：
  - `action_choice`：五类动作之一（endorse / endorse_option / conditional / report_option / against，精确拼写）
  - `likert_*`：1–5 整数
  - `note`：可空
- 填好后运行：`.venv\Scripts\python.exe scripts\finalize_expert_review.py`
  （校验取值 → 回填官方 `figure3_expert_agreement.csv` → 计算 Fleiss κ / Cohen κ →
  写 `outputs/tables/expert_review_stats.json`）；随后由我渲染图3并更新稿件。

## 4. 预注册统计规则（写进 Methods，避免事后挑选）
- 专家一致性：整体 Fleiss κ（5 病例 × 4 评分者）；逐病例报告原始一致率（x/4）。
  （契约原设想「逐病例 Fleiss κ」在单病例 4 评分者下无定义，故按此调整。）
- 系统 vs 专家：系统动作 vs 专家多数票的 Cohen κ；**2:2 平票的病例记 no-majority，从该 κ 中剔除并在图注披露**。
- κ ≥0.6 判为支持 face validity（Landis–Koch）；n 小，所有 κ 报告解释为 preliminary。

## 5. 伦理
- 匿名（expert_id 1–4）、自愿、无患者数据（病例为合成）；知情说明已印在问卷首页。

*Pack v2 generated 2026-09-18 from outputs/demo_cases/*.json (5 cases, verdicts unchanged; 
decision items rendered as declarative propositions translated from rule-base item descriptions).*
