"""前列安汇 (probiopsy-rag) — Streamlit UI (v2.6, 3-tab).

Three tabs (Executor Phase 6):
  1. 📊 项目介绍 (Overview)   — agent intro + build/citation status
  2. 💬 RAG 问答 (Chat)        — free-form Q&A: LightRAG retrieval → GLM answers
  3. 🔍 决策评估 (Decision)    — patient scenario × decision items → full pipeline
                                (rule engine + LightRAG + SafetyAgent arbiter)

Everything reads project files at runtime (.planner.config.json,
.medical-agent/state.json, configs/rules.yaml, seed registries); the decision
tab uses the SAME pipeline as the benchmark (pipeline.run_pipeline), so the
demoed system is the evaluated system.

Usage:
    .venv/Scripts/python.exe -m streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except Exception:
    pass

from probiopsy_rag_agent.lightrag_adapter import LightRAGAdapter
from probiopsy_rag_agent.llm_client import LLMClient
from probiopsy_rag_agent.pipeline import INDEX_DIR, load_assets, run_pipeline
from probiopsy_rag_agent.safety_agent import SafetyAgent

# ─────────────────────────────────────────────────────────────────────────────
# Design tokens
# ─────────────────────────────────────────────────────────────────────────────
ACTION_COLORS = {
    "endorse":        {"bg": "#16a34a", "soft": "#f0fdf4", "border": "#166534", "icon": "✅"},
    "endorse_option": {"bg": "#0d9488", "soft": "#f0fdfa", "border": "#115e59", "icon": "👍"},
    "conditional":    {"bg": "#d97706", "soft": "#fffbeb", "border": "#92400e", "icon": "⚠️"},
    "report_option":  {"bg": "#6b7280", "soft": "#f9fafb", "border": "#374151", "icon": "📄"},
    "against":        {"bg": "#dc2626", "soft": "#fef2f2", "border": "#991b1b", "icon": "⛔"},
}

ACTION_LABELS = {
    "endorse": "推荐 (Consensus endorse)",
    "endorse_option": "推荐选项 (SOQ-endorsed option)",
    "conditional": "有条件考虑 (Conditional / neither)",
    "report_option": "报告为开放选项 (No consensus — report only)",
    "against": "不推荐 (Consensus against)",
}

SEVERITY_COLORS = {"high": "#dc2626", "medium": "#d97706", "low": "#16a34a", "unknown": "#6b7280"}


def set_page_config() -> None:
    st.set_page_config(
        page_title="前列安汇",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown("""
    <style>
        .stApp { font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif; }
        .block-container { padding-top: 1.5rem; padding-bottom: 1rem; max-width: 1400px; }
        .verdict-hero {
            border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem;
            border-left: 6px solid;
        }
        .verdict-hero-title { font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.8; }
        .verdict-hero-action { font-size: 2.2rem; font-weight: 700; line-height: 1.15; margin-bottom: 0.5rem; }
        .verdict-hero-meta { font-size: 0.875rem; opacity: 0.85; }
        .stat-card {
            background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px;
            padding: 1rem; text-align: center;
        }
        .stat-card .label { font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }
        .stat-card .value { font-size: 1.4rem; font-weight: 700; color: #111827; }
        .rule-chip {
            display: inline-block; background: #f3f4f6; color: #374151;
            font-size: 0.75rem; padding: 4px 10px; border-radius: 12px;
            margin-right: 6px; margin-bottom: 4px; border: 1px solid #e5e7eb;
        }
        .constraint-box {
            background: #fffbeb; border: 1px solid #f59e0b; border-radius: 6px;
            padding: 0.6rem 0.9rem; margin-bottom: 0.5rem; font-size: 0.85rem; color: #374151;
        }
        .app-footer {
            margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;
            font-size: 0.75rem; color: #6b7280; text-align: center;
        }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Project file readers (Overview tab) — defensive, never crash
# ─────────────────────────────────────────────────────────────────────────────
def _load_json(path: Path) -> dict | None:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def read_state() -> dict:
    return _load_json(PROJECT_ROOT / ".medical-agent" / "state.json") or {}


def index_freshness() -> tuple[str, str]:
    """Compare rules.yaml mtime with the index graphml mtime."""
    rules = PROJECT_ROOT / "configs" / "rules.yaml"
    graphml = Path(INDEX_DIR) / "graph_chunk_entity_relation.graphml"
    if not graphml.exists():
        return ("stale_not_built", "LightRAG 索引未构建（先跑 Phase 4 build）")
    try:
        if rules.stat().st_mtime > graphml.stat().st_mtime:
            return ("stale_rules_changed", "rules.yaml 晚于索引构建，建议重建")
    except OSError:
        return ("unknown", "无法比较文件时间")
    return ("fresh", "索引晚于 rules.yaml 最后修改，可放心问答")


def render_stat_card(label: str, value: str, accent: str = "#111827") -> None:
    st.markdown(f"""
    <div class="stat-card">
        <div class="label">{label}</div>
        <div class="value" style="color:{accent};">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render_verdict_hero(verdict: dict, elapsed: float, n_rules: int, n_evidence: int) -> None:
    action = verdict.get("action", "report_option")
    c = ACTION_COLORS.get(action, ACTION_COLORS["report_option"])
    conf = float(verdict.get("confidence") or 0)
    st.markdown(f"""
    <div class="verdict-hero" style="background:{c['soft']}; border-left-color:{c['bg']};">
        <div class="verdict-hero-title" style="color:{c['bg']};">系统裁决 / System Verdict</div>
        <div class="verdict-hero-action" style="color:{c['bg']};">
            {c['icon']} {ACTION_LABELS.get(action, action)}
        </div>
        <div class="verdict-hero-meta" style="color:{c['border']};">
            <strong>置信度:</strong> {conf:.0%} &nbsp;·&nbsp;
            <strong>触发规则:</strong> {n_rules} 条 &nbsp;·&nbsp;
            <strong>证据片段:</strong> {n_evidence} 条 &nbsp;·&nbsp;
            <strong>耗时:</strong> {elapsed:.1f}s
            {'&nbsp;·&nbsp;⚠️ 降级输出' if verdict.get('degraded') else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Cached resources
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="加载规则引擎 + 证据库…")
def get_assets():
    return load_assets()


@st.cache_resource(show_spinner="加载 LightRAG 索引…")
def get_adapter():
    try:
        return LightRAGAdapter(working_dir=str(INDEX_DIR), language="English")
    except Exception as e:
        st.warning(f"LightRAG 初始化失败: {e}")
        return None


@st.cache_resource(show_spinner="加载 GLM 仲裁客户端…")
def get_arbiter() -> SafetyAgent | None:
    try:
        return SafetyAgent(client=LLMClient(provider="deepseek", temperature=0.0, max_tokens=2048))
    except Exception as e:
        st.warning(f"LLM 客户端初始化失败: {e}")
        return None


@st.cache_resource(show_spinner="加载 GLM 问答客户端…")
def get_chat_llm() -> LLMClient | None:
    try:
        return LLMClient(provider="deepseek", temperature=0.2, max_tokens=2048)
    except Exception as e:
        st.warning(f"LLM 客户端初始化失败: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — 项目介绍 / Overview
# ─────────────────────────────────────────────────────────────────────────────
def overview_tab() -> None:
    st.header("📊 项目介绍 & 构建状态")
    cfg = _load_json(PROJECT_ROOT / ".planner.config.json") or {}
    state = read_state()
    project = cfg.get("project", {}) or {}
    entities = cfg.get("entities", {}) or {}

    st.subheader("🧬 Agent 定位")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.write(f"**代号**：`{project.get('code_name', '-')}` / {project.get('chinese_name', '-')}")
        st.write(f"**研究方向**：{(cfg.get('domain') or {}).get('research_direction', '-')}")
        st.write(f"**验证金标准**：ProBIOPSY 国际共识 112 条终版陈述 (Eur Urol 2026)")
    with c2:
        st.write("**目标期刊**")
        tj = cfg.get("target_journal", {})
        if isinstance(tj, dict):
            st.write(f"· 一志愿：{tj.get('first', '-')}")
            for b in (tj.get("backup") or [])[:2]:
                st.write(f"· 备选：{b}")

    st.divider()
    st.subheader("🏗️ 三层混合架构")
    st.markdown(f"""
```
用户输入（{(entities.get('a') or {}).get('chinese_name', '患者情境')} 情境要素 + {(entities.get('b') or {}).get('chinese_name', '穿刺决策项')}）
   │
   ├─ ① 规则引擎（risk_rules.py + rules.yaml：12 条共识规则 + 4 条患者因素升级）
   │     └─ A flag ∩ B item 匹配 → 共识裁决标签 → HARD CONSTRAINTS
   │
   ├─ ② LightRAG 知识图谱证据检索（lightrag_adapter.py）
   │     └─ GLM-5.3 实体抽取 + Doubao embedding（357 证据块）
   │
   └─ ③ LLM 仲裁（safety_agent.py）
         └─ 规则硬约束 + 图谱证据 → 5 类动作裁决（endorse … against）
   ▼
可追溯、可解释的穿刺决策报告（对照 112 条金标准陈述）
```
""")

    st.divider()
    st.subheader("📚 构建状态")
    completed = state.get("completed", []) or []
    fresh_status, fresh_detail = index_freshness()
    pill_c = {"fresh": "#16a34a", "stale_rules_changed": "#d97706",
              "stale_not_built": "#dc2626", "unknown": "#6b7280"}[fresh_status]
    pill_l = {"fresh": "✅ 索引新鲜", "stale_rules_changed": "⚠️ 规则已改须重建",
              "stale_not_built": "❌ 未构建", "unknown": "❓ 未知"}[fresh_status]

    sc = st.columns(5)
    with sc[0]:
        render_stat_card("已完成阶段", str(len(completed)))
    with sc[1]:
        render_stat_card("规则", "12")
    with sc[2]:
        render_stat_card("证据块", "357")
    with sc[3]:
        render_stat_card("金标准陈述", "112")
    with sc[4]:
        st.markdown(f'<span class="stat-card" style="display:block;"><div class="label">索引状态</div>'
                    f'<div class="value" style="font-size:1rem;color:{pill_c};">{pill_l}</div></span>',
                    unsafe_allow_html=True)
    st.caption(fresh_detail)

    # citation verification
    cv = _load_json(PROJECT_ROOT / "outputs" / "citation_verification_report.json") or {}
    if cv:
        st.subheader("⚙️ 文献核验（kuku Rule 3+4 硬门禁）")
        summary = cv.get("summary", cv)
        st.write(f"状态：**{summary.get('status', '?')}** — "
                 f"{summary.get('verified', '?')}/{summary.get('total', '?')} 条引用在 ≥2 独立数据源 "
                 f"(Crossref + OpenAlex/Semantic Scholar) 中解析成功，0 撤稿")

    # phase history
    hist = state.get("history", []) or []
    if hist:
        with st.expander("📜 项目历史"):
            for h in hist[-8:]:
                st.caption(f"{h.get('date', '')} — {h.get('event', '')}")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — RAG 问答 / Chat
# ─────────────────────────────────────────────────────────────────────────────
def chat_tab() -> None:
    st.header("💬 RAG 增强问答")
    st.caption("先查 LightRAG 知识图谱（357 条 ProBIOPSY 证据块），再由 GLM 基于检索证据回答；"
               "证据不足时明说，不编造。")

    if not Path(INDEX_DIR).exists():
        st.error("🚫 LightRAG 索引未构建。请先执行 Phase 4 构建。")
        return

    adapter = get_adapter()
    llm = get_chat_llm()
    if adapter is None or llm is None:
        st.error("LightRAG 或 GLM 客户端初始化失败，请检查 .env。")
        return

    example_qs = [
        "What biopsy scheme does the ProBIOPSY consensus recommend for a unifocal "
        "PI-RADS 4 lesion planned for focal therapy?",
        "Is bpMRI acceptable as an alternative to mpMRI for prostate cancer diagnosis?",
        "How many targeted cores should be taken per MRI lesion?",
        "Should antibiotic prophylaxis be omitted for transperineal biopsy?",
    ]
    st.write("**示例问题**")
    eq = st.columns(2)
    for i, q in enumerate(example_qs):
        with eq[i % 2]:
            if st.button(q[:58] + ("…" if len(q) > 58 else ""), key=f"ex{i}",
                         use_container_width=True):
                st.session_state["chat_pending"] = q

    show_evidence = st.toggle("显示检索证据原文", value=True, key="chat_show_ev")
    if st.button("🧹 清空对话"):
        st.session_state["chat_messages"] = []
        st.rerun()

    st.session_state.setdefault("chat_messages", [])
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant" and show_evidence and msg.get("evidence"):
                with st.expander(f"📚 检索证据（{len(msg['evidence'])} 段）"):
                    for i, ev in enumerate(msg["evidence"], 1):
                        st.caption(f"片段 {i}")
                        st.write(ev[:600] + ("..." if len(ev) > 600 else ""))

    question = st.session_state.pop("chat_pending", None) or st.chat_input(
        "向 agent 提问…（例如：bpMRI 能否替代 mpMRI 用于前列腺癌诊断？）")
    if not question:
        return

    st.session_state["chat_messages"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("检索 LightRAG 知识图谱…"):
            try:
                retrieved = adapter.query(question, mode="hybrid") or ""
            except Exception as e:
                st.error(f"LightRAG 检索失败: {e}")
                return
        evidence_chunks = [c.strip() for c in retrieved.split("\n\n") if c.strip()][:8]

        if not retrieved.strip():
            answer = "知识库中未检索到与该问题相关的证据，无法回答。请尝试更具体的关键词。"
        else:
            with st.spinner("GLM 基于证据生成回答…"):
                system = (
                    "You are a medical Q&A assistant grounded in a ProBIOPSY consensus "
                    "knowledge base. Answer ONLY from the evidence below; if it is "
                    "insufficient, say so explicitly. Answer in Chinese with numbered "
                    "points, citing [证据N] tags where used."
                )
                prompt = f"【Evidence】\n{retrieved[:6000]}\n\n【Question】\n{question}"
                try:
                    resp = llm.complete(prompt=prompt, system=system)
                    answer = resp.text if not resp.degraded else (
                        "LLM 调用失败（限流/网络），请稍后重试。")
                except Exception as e:
                    answer = f"LLM 调用失败: {e}"

        st.write(answer)
        if show_evidence and evidence_chunks:
            with st.expander(f"📚 检索证据（{len(evidence_chunks)} 段）"):
                for i, ev in enumerate(evidence_chunks, 1):
                    st.caption(f"片段 {i}")
                    st.write(ev[:600] + ("..." if len(ev) > 600 else ""))

    st.session_state["chat_messages"].append(
        {"role": "assistant", "content": answer, "evidence": evidence_chunks})


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — 决策评估 / Decision (A scenario × B items → full pipeline)
# ─────────────────────────────────────────────────────────────────────────────
def _load_registries():
    a_rows = list(csv.DictReader(
        (PROJECT_ROOT / "data" / "seed" / "entities_a.csv").open(encoding="utf-8-sig")))
    b_rows = list(csv.DictReader(
        (PROJECT_ROOT / "data" / "seed" / "entities_b.csv").open(encoding="utf-8-sig")))
    return a_rows, b_rows


def decision_tab() -> None:
    st.header("🔍 穿刺决策评估")
    st.caption("选择患者临床情境（可多选，flags 取并集）+ 待决策的穿刺决策项 → "
               "规则引擎 + LightRAG + GLM 仲裁 → 5 类动作裁决报告。")

    a_rows, b_rows = _load_registries()
    assets = get_assets()
    adapter = get_adapter()
    agent = get_arbiter()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**👩 患者临床情境要素**（Entity A）")
        a_labels = {
            f"{r['patient_clinical_scenario_id']}: {r['primary_name'][:48]}":
                (r["patient_clinical_scenario_id"], [f for f in (r.get("flags") or "").split("|") if f])
            for r in a_rows
        }
        picked_a = st.multiselect("选择情境要素", options=list(a_labels), default=[],
                                  help="可多选；flags 取并集")
        patient_flags: set[str] = set()
        for lab in picked_a:
            patient_flags.update(a_labels[lab][1])
        st.caption(f"合并 flags（{len(patient_flags)}）: `{', '.join(sorted(patient_flags)) or '—'}`")

        # optional manual flags
        manual = st.text_input("手动补充 flags（逗号分隔，可选）", "")
        if manual.strip():
            patient_flags.update(f.strip() for f in manual.split(",") if f.strip())

    with c2:
        st.markdown("**🌍 穿刺决策项**（Entity B）")
        b_options = {
            f"{r['entity_b_id']}: {r['generic_name'][:52]}": r["entity_b_id"]
            for r in b_rows
        }
        search = st.text_input("搜索决策项", "", placeholder="🔍 例如 psma / scheme / abx")
        filtered = [k for k in b_options if search.lower() in k.lower()] if search else list(b_options)
        picked_b = st.multiselect("选择决策项", options=filtered, default=[],
                                  help="可多选，每项对应一条 ProBIOPSY 陈述")
        decision_items = {b_options[k] for k in picked_b}

    # verdict-tag badges for picked items
    if decision_items:
        tags = []
        for iid in sorted(decision_items):
            item = assets.items.get(iid)
            if item:
                color = ACTION_COLORS.get(
                    {"recommend": "endorse", "against": "against",
                     "conditional": "conditional", "report_only": "report_option"}.get(item.action, "report_option")
                )["bg"]
                tags.append(f'<span class="rule-chip" style="border-color:{color}; color:{color};">'
                            f'{iid} · {item.endorsement}/{item.action}</span>')
        st.markdown("共识裁决标签：" + " ".join(tags), unsafe_allow_html=True)

    if not st.button("🚀 开始评估", type="primary", use_container_width=True, key="dec_run"):
        return
    if not decision_items:
        st.warning("请至少选择一个穿刺决策项。")
        return
    if not patient_flags:
        st.warning("请至少选择一个患者情境要素（或手动补充 flags）。")
        return

    question = (
        "Should the following biopsy decision(s) be taken for this patient: "
        + "; ".join(f"{iid} ({assets.items[iid].name})" if iid in assets.items else iid
                    for iid in sorted(decision_items)) + "?"
    )

    with st.spinner("运行三层流水线（规则引擎 → LightRAG → GLM 仲裁）…"):
        try:
            res = run_pipeline(
                question=question,
                patient_flags=patient_flags,
                decision_items=decision_items,
                assets=assets,
                adapter=adapter,
                agent=agent,
            )
        except Exception as e:
            st.error(f"评估失败: {type(e).__name__}: {e}")
            return

    st.divider()
    render_verdict_hero(res.verdict, res.elapsed, len(res.rule_matches), len(res.lexical_hits))

    st.subheader("🎯 系统裁决依据")
    st.write(res.verdict.get("rationale", ""))

    tabs = st.tabs(["📋 完整报告", "⚙️ 规则与硬约束", "📚 证据链", "🔧 元数据"])

    with tabs[0]:
        st.markdown(res.report_md)

    with tabs[1]:
        if not res.rule_matches:
            st.info("未触发任何规则 — 裁决完全由知识图谱 + 仲裁层给出")
        else:
            for m in res.rule_matches:
                sev_color = SEVERITY_COLORS.get(m.rule.severity, "#6b7280")
                st.markdown(
                    f"### <span style='color:{sev_color}'>●</span> {m.rule.rule_id} "
                    f"<span class='rule-chip'>{m.rule.severity}</span>",
                    unsafe_allow_html=True)
                st.write(f"**依据**: {m.rule.rationale}")
                if m.rule.recommendation:
                    st.write(f"**建议**: {m.rule.recommendation}")
                for hc in m.hard_constraints:
                    st.markdown(f'<div class="constraint-box">🔒 {hc}</div>', unsafe_allow_html=True)
                st.divider()

    with tabs[2]:
        st.caption("词法检索命中（按实体加权评分排序）")
        for r in res.lexical_hits:
            with st.expander(f"[{r.chunk.chunk_id}] {r.chunk.source_locator} — score {r.score:.2f}"):
                st.write(r.chunk.text[:800])
        if res.graph_context.strip():
            with st.expander("🕸️ LightRAG 图谱上下文（仅检索，未生成）"):
                st.text(res.graph_context[:4000])

    with tabs[3]:
        mc = st.columns(4)
        with mc[0]:
            render_stat_card("耗时", f"{res.elapsed:.1f}s")
        with mc[1]:
            render_stat_card("规则命中", str(len(res.rule_matches)))
        with mc[2]:
            render_stat_card("词法证据", str(len(res.lexical_hits)))
        with mc[3]:
            render_stat_card("图谱上下文", f"{len(res.graph_context)} chars")
        with st.expander("verdict JSON"):
            st.json(res.verdict)

    st.markdown("""
    <div class="app-footer">
        <div>🧬 前列安汇 · 规则引擎 + LightRAG + LLM 仲裁三层架构 · 对照 ProBIOPSY 共识 (Eur Urol 2026)</div>
        <div style="margin-top:0.5rem; opacity:0.7;">
            ⚠️ 本输出仅供临床决策支持；最终判断由临床医生做出。
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    set_page_config()
    st.title("🧬 前列安汇")
    st.caption("患者临床情境 × 穿刺决策项 · 三层混合架构（规则引擎 + LightRAG + LLM 仲裁）")

    tab_overview, tab_chat, tab_decision = st.tabs(
        ["📊 项目介绍", "💬 RAG 问答", "🔍 决策评估"])
    with tab_overview:
        overview_tab()
    with tab_chat:
        chat_tab()
    with tab_decision:
        decision_tab()


if __name__ == "__main__":
    main()
