# -*- coding: utf-8 -*-
"""Build the expert blind-review pack (planner Phase 4.5 pre-registered design).

v2: 按评审设计修正 —— 每个病例以「陈述句决策项 + 组合命题」呈现（非是非问句），
Part A 专家对组合命题给出五类动作; Part B 揭示系统对同一命题的判定。

Produces, from the 5 real demonstration-case JSONs only:
- outputs/expert_review/expert_review_protocol.md  (PI 操作手册, 中文)
- outputs/expert_review/expert_booklet.md          (可直接打印的专家问卷, 每位一份)
- outputs/expert_review/answer_worksheet.csv       (回收后填写 → finalize 脚本转录)
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "outputs" / "demo_cases"
DEST = ROOT / "outputs" / "expert_review"
DEST.mkdir(parents=True, exist_ok=True)

ACTIONS = ["endorse", "endorse_option", "conditional", "report_option", "against"]
ACTION_ZH = {
    "endorse": "完全支持（按陈述原样支持）",
    "endorse_option": "支持为可接受选项之一（等同选项）",
    "conditional": "有条件支持（需满足特定条件）",
    "report_option": "仅作为可报告的备选路径（不作主动推荐）",
    "against": "不建议 / 反对",
}
LIKERT_ZH = {
    "likert_clarity": "条理清晰度：系统输出的表述是否清晰、易懂、无歧义",
    "likert_usefulness": "临床有用性：该输出对真实临床决策是否有帮助",
    "likert_recommendation": "推荐认可度：你对系统推荐意见本身的认可程度",
    "likert_evidence": "证据充分性：所引用的共识条目/证据是否足以支撑该结论",
}

# 病例中文材料 —— 病例摘要译自 case JSON 的 question 字段; 决策项陈述句译自
# hard_constraints 中对应 decision item 的英文描述，不添加额外临床信息。
CASE_ZH = {
    "case1_unifocal_scheme": {
        "summary": "62 岁男性，3T mpMRI（图像质量合格）示外周带单发 9 mm PI-RADS 4 病灶。",
        "items": [
            "穿刺方案采用「靶向穿刺＋病灶旁穿刺」（针对单发可视病灶）；",
            "在此基础上加做完整系统性穿刺。",
        ],
        "combo": "①＋②",
    },
    "case2_psma_pet_upfront": {
        "summary": "穿刺初诊男性，PSA 升高、临床怀疑度高。",
        "items": [
            "以 PSMA PET-CT 替代 MRI，作为前列腺穿刺前的一线影像学检查。",
        ],
        "combo": "①",
    },
    "case3_bpmri_indeterminate": {
        "summary": "bpMRI（图像质量合格）示外周带 PI-RADS 3（不确定性）病灶。",
        "items": [
            "以 PSA 密度作为该类病灶穿刺决策的门槛；",
            "对该类病灶加做增强 MRI 序列；",
            "对该类病灶安排计划性随访影像。",
        ],
        "combo": "①＋②＋③",
    },
    "case4_advanced_route_prophylaxis": {
        "summary": "疑似局部晚期疾病、不适合根治性治疗的患者。",
        "items": [
            "对疑似局部晚期疾病和/或不适合根治性治疗者，系统性穿刺减至最多 6 针；",
            "以经会阴路径作为标准穿刺路径；",
            "无感染危险因素时，经会阴穿刺不加用抗生素预防。",
        ],
        "combo": "①＋②＋③",
    },
    "case5_infection_risk_escalation": {
        "summary": "存在感染危险因素、拟行重复前列腺穿刺的患者。",
        "items": [
            "以经会阴路径作为标准穿刺路径；",
            "若经直肠入路不可避免，则强化抗生素预防。",
        ],
        "combo": "①＋②",
    },
}

cases = []
for p in sorted(CASES_DIR.glob("*.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    cases.append(d)
assert len(cases) == 5, cases

NUM = "①②③④⑤"

# ---------------------------------------------------------------- booklet
B = []
B.append("# 前列腺穿刺决策支持系统「系统 A」— 临床专家盲评问卷")
B.append("")
B.append("> 感谢您参与本次独立评审。本问卷共 2 部分、5 个病例，约需 20–30 分钟。")
B.append("> **请先完成第一部分全部 5 例后，再翻阅第二部分**（第二部分展示系统输出，提前查看会使您的第一部分作答失效）。")
B.append("> 评审为匿名（仅以专家 1–4 编号）、自愿参加，结果仅以汇总形式用于学术研究，不涉及任何患者个人信息（全部病例为合成教学病例）。")
B.append("")
B.append("**评审对象说明**：每个病例给出若干**陈述句式决策项**（①②③…）。您需要评审的命题是：")
B.append("**「同时采纳该病例的全部决策项所构成的组合方案」**（即 ①＋②＋…）。")
B.append("第一部分请您对这一组合命题给出自己的推荐动作；第二部分将展示系统 A 对**同一组合命题**的总体判定。")
B.append("")
B.append("## 五类处置动作定义（第一部分作答用）")
B.append("")
for a in ACTIONS:
    B.append(f"- **{a}** — {ACTION_ZH[a]}")
B.append("")
B.append("## Likert 评分说明（第二部分作答用）：1=非常不同意/很差 … 5=非常同意/很好")
B.append("")
for k, v in LIKERT_ZH.items():
    B.append(f"- **{k}** — {v}")
B.append("")
B.append("---")
B.append("")
B.append("# 第一部分（请先完成本部分；本部分不展示任何系统输出）")
B.append("")
for i, c in enumerate(cases, 1):
    zh = CASE_ZH[c["case_id"]]
    B.append(f"## 病例 {i}：{c['title']}")
    B.append("")
    B.append(f"**病例摘要**：{zh['summary']}")
    B.append("")
    B.append(f"*Original question:* {c['question']}")
    B.append("")
    B.append("**决策项（陈述句）：**")
    B.append("")
    for j, item in enumerate(zh["items"]):
        B.append(f"- {NUM[j]} {item}")
    B.append("")
    B.append(f"**待评审命题**：同时采纳 {zh['combo']} 所构成的组合方案。")
    B.append("")
    B.append("**您对该组合命题的推荐动作（五选一，请勾选）：**")
    B.append("")
    for a in ACTIONS:
        B.append(f"- [ ] {a} — {ACTION_ZH[a]}")
    B.append("")
    B.append("**一句话理由（选填）：** ______________________________________________")
    B.append("")
B.append("---")
B.append("")
B.append("# 第二部分（第一部分全部完成后作答）")
B.append("")
B.append("以下为「系统 A」对上述 5 个病例**同一组合命题**的总体判定（动作、置信度、依据、引用）。")
B.append("请逐例对系统输出进行 Likert 1–5 评分。")
B.append("")
for i, c in enumerate(cases, 1):
    zh = CASE_ZH[c["case_id"]]
    v = c["verdict"]
    B.append(f"## 病例 {i}：系统 A 对组合方案（{zh['combo']}）的判定")
    B.append("")
    B.append(f"**系统动作**：{v['action']}　**置信度**：{v['confidence']}")
    B.append("")
    B.append(f"**依据**：{v['rationale']}")
    B.append("")
    B.append(f"**引用**：{'、'.join(v['citations'])}")
    B.append("")
    for k, dsc in LIKERT_ZH.items():
        B.append(f"- {k}（{dsc}）：1　2　3　4　5")
    B.append("- 备注（选填）：______________________________________________")
    B.append("")

(DEST / "expert_booklet.md").write_text("\n".join(B) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- worksheet
try:
    with open(DEST / "answer_worksheet.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["expert_id", "case_id", "action_choice", "likert_clarity",
                    "likert_usefulness", "likert_recommendation", "likert_evidence", "note"])
        for e in range(1, 5):
            for c in cases:
                w.writerow([e, c["case_id"], "", "", "", "", "", ""])
    print("written:", DEST / "answer_worksheet.csv", "(20 rows)")
except PermissionError:
    print("SKIP: answer_worksheet.csv 被占用（可能正在 Excel 中打开），内容未变，跳过")

# ---------------------------------------------------------------- protocol
P = []
P.append("# 专家盲评操作手册（PI 用）")
P.append("")
P.append("**目标**：完成 pre-registered 的 4 专家 × 5 病例盲评（figure3 + 稿件 face-validity 段）。")
P.append("")
P.append("## 0. 评审设计要点（v2，已修正）")
P.append("- 每个病例以**陈述句决策项**（①②③…）呈现，评审命题 = **同时采纳全部决策项的组合方案**，")
P.append("  与系统输出的判定对象完全一致（系统 verdict 即对该组合命题的总体动作）。")
P.append("- 不使用「是否…」问句——五类动作评的是命题立场，不是是非题。")
P.append("- 系统依据（rationale）中的分项立场（如支持①、拒绝②）属于 Part B 展示内容，")
P.append("  Part A 不出现，保证盲评。")
P.append("")
P.append("## 1. 专家入选（4 名）")
P.append("- 建议构成：泌尿外科 ≥2、影像科 ≥1、放疗/肿瘤 ≥1；副高及以上；**未参与本项目开发**。")
P.append("- 独立评审：专家之间不讨论、不同时填卷。")
P.append("")
P.append("## 2. 评审流程（每位专家约 20–30 分钟）")
P.append("1. 打印或发送 `expert_booklet.md`（PDF/纸质均可），每位一份。")
P.append("2. 专家先完成**第一部分**：5 个病例各自的组合命题推荐动作（五选一）＋选填一句理由。")
P.append("3. 第一部分收齐或专家自行翻页后，展示**第二部分**（系统 A 对同一命题的判定），填 4 项 Likert 1–5。")
P.append("4. 盲评纪律：第一部分完成前不得翻看第二部分；booklet 中系统以「系统 A」匿名。")
P.append("")
P.append("## 3. 回收与转录")
P.append("- 方式 A（推荐）：把 4 份答卷拍照/打字发给我，我来转录。")
P.append("- 方式 B：自行填写 `answer_worksheet.csv`（20 行，已建好行框架），列含义：")
P.append("  - `action_choice`：五类动作之一（endorse / endorse_option / conditional / report_option / against，精确拼写）")
P.append("  - `likert_*`：1–5 整数")
P.append("  - `note`：可空")
P.append("- 填好后运行：`.venv\\Scripts\\python.exe scripts\\finalize_expert_review.py`")
P.append("  （校验取值 → 回填官方 `figure3_expert_agreement.csv` → 计算 Fleiss κ / Cohen κ →")
P.append("  写 `outputs/tables/expert_review_stats.json`）；随后由我渲染图3并更新稿件。")
P.append("")
P.append("## 4. 预注册统计规则（写进 Methods，避免事后挑选）")
P.append("- 专家一致性：整体 Fleiss κ（5 病例 × 4 评分者）；逐病例报告原始一致率（x/4）。")
P.append("  （契约原设想「逐病例 Fleiss κ」在单病例 4 评分者下无定义，故按此调整。）")
P.append("- 系统 vs 专家：系统动作 vs 专家多数票的 Cohen κ；**2:2 平票的病例记 no-majority，从该 κ 中剔除并在图注披露**。")
P.append("- κ ≥0.6 判为支持 face validity（Landis–Koch）；n 小，所有 κ 报告解释为 preliminary。")
P.append("")
P.append("## 5. 伦理")
P.append("- 匿名（expert_id 1–4）、自愿、无患者数据（病例为合成）；知情说明已印在问卷首页。")
P.append("")
P.append("*Pack v2 generated 2026-09-18 from outputs/demo_cases/*.json (5 cases, verdicts unchanged; ")
P.append("decision items rendered as declarative propositions translated from rule-base item descriptions).*")

(DEST / "expert_review_protocol.md").write_text("\n".join(P) + "\n", encoding="utf-8")

print("written:", DEST / "expert_booklet.md")
print("written:", DEST / "expert_review_protocol.md")
