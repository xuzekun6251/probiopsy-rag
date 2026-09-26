"""前列安汇 (probiopsy-rag) — Streamlit UI (v3.0, 5-tab).

Five tabs:
  1. 📊 项目介绍 (Overview)     — agent intro + build/citation status
  2. 💬 智能问答 (Chat)          — context-only retrieval → single GLM answer with
                                   numbered evidence blocks + citation traceability
  3. 🔍 决策评估 (Decision)      — scenario × decision items → full pipeline with
                                   demo-case quick-load, timings breakdown, confidence
                                   gauge, citation provenance, rule-only fast preview
  4. 🕸️ 知识图谱 (Knowledge graph) — interactive entity search + n-hop subgraph
                                   (pyvis; matplotlib fallback)
  5. 📈 基准结果 (Benchmark)     — evaluation summary dashboard (Altair)

Everything reads project files at runtime; the decision tab uses the SAME
pipeline as the benchmark (pipeline.run_pipeline), so the demoed system is the
evaluated system.

Usage:
    .venv/Scripts/python.exe -m streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import csv
import json
import re
import time
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

PROJECT_ROOT = Path(__file__).resolve().parents[1]

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except Exception:
    pass

from probiopsy_rag_agent.lightrag_adapter import LightRAGAdapter
from probiopsy_rag_agent.llm_client import LLMClient
from probiopsy_rag_agent.pipeline import (
    INDEX_DIR,
    build_question,
    load_assets,
    run_pipeline,
)
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

ENTITY_TYPE_COLORS = {
    "person": "#3b82f6", "content": "#16a34a", "method": "#d97706", "concept": "#8b5cf6",
    "organization": "#ec4899", "location": "#14b8a6", "data": "#f59e0b", "UNKNOWN": "#6b7280",
    "artifact": "#0ea5e9", "event": "#84cc16",
}
ENTITY_TYPE_LABELS = {
    "person": "人物", "content": "文献/内容", "method": "方法/技术", "concept": "概念",
    "organization": "机构", "location": "地点", "data": "数据/指标", "UNKNOWN": "未分类",
    "artifact": "制品/工具", "event": "事件",
}

METRIC_LABELS = {
    "exact5": "exact-5 准确率", "exact3": "exact-3 准确率", "macro_f1": "macro-F1",
    "kappa": "Cohen's κ", "against_f1": "against-F1",
    "against_sensitivity": "against 敏感度", "against_specificity": "against 特异度",
}

ACTION_CLASSES_ORDER = ["endorse", "conditional", "against", "endorse_option", "report_option"]


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
        .flow-box {
            border-radius: 10px; padding: 0.7rem 1rem; text-align: center; flex: 1;
            border: 1px solid #e5e7eb; background: #ffffff;
        }
        .flow-box .t { font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.04em; }
        .flow-box .v { font-size: 1.05rem; font-weight: 700; color: #111827; margin-top: 2px; }
        .flow-box .m { font-size: 0.75rem; color: #6b7280; margin-top: 2px; }
        .flow-arrow { display: flex; align-items: center; font-size: 1.4rem; color: #9ca3af; }
        .cite-chip {
            display: inline-block; background: #eff6ff; color: #1d4ed8;
            font-size: 0.75rem; font-weight: 600; padding: 3px 9px; border-radius: 10px;
            margin-right: 5px; margin-bottom: 4px; border: 1px solid #bfdbfe;
        }
        .app-footer {
            margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;
            font-size: 0.75rem; color: #6b7280; text-align: center;
        }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


APP_FOOTER = """
<div class="app-footer">
    <div>🧬 前列安汇 · 规则引擎 + LightRAG + LLM 仲裁三层架构 · 对照 ProBIOPSY 共识 (Eur Urol 2026)</div>
    <div style="margin-top:0.5rem; opacity:0.7;">
        ⚠️ 本输出仅供临床决策支持；最终判断由临床医生做出。
    </div>
</div>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Project file readers — defensive, never crash
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
    """Integrity check: live rules.yaml sha256 vs the sha recorded at index build."""
    import hashlib
    rules = PROJECT_ROOT / "configs" / "rules.yaml"
    graphml = Path(INDEX_DIR) / "graph_chunk_entity_relation.graphml"
    if not graphml.exists():
        return ("stale_not_built", "LightRAG 索引未构建（先跑 Phase 4 build）")
    if not rules.exists():
        return ("unknown", "找不到 configs/rules.yaml")
    progress = _load_json(PROJECT_ROOT / ".executor" / "progress.json") or {}
    recorded = ((progress.get("phases") or {}).get("phase6") or {}).get(
        "index_built_against_rules_sha256")
    if not recorded:
        return ("unknown", "构建记录缺少 index_built_against_rules_sha256（旧版 progress.json）")
    try:
        live_sha = hashlib.sha256(rules.read_bytes()).hexdigest()
    except OSError:
        return ("unknown", "无法读取 rules.yaml")
    if live_sha != recorded:
        return ("stale_rules_changed",
                f"rules.yaml 与索引构建时的 sha256 不一致（当前 {live_sha[:12]}…），建议重建")
    return ("fresh", f"rules.yaml sha256 校验一致（{live_sha[:12]}…），索引与规则版本匹配")


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


@st.cache_resource(show_spinner="解析知识图谱 (1,864 实体 / 3,078 关系)…")
def get_kg():
    import networkx as nx
    graphml = Path(INDEX_DIR) / "graph_chunk_entity_relation.graphml"
    if not graphml.exists():
        return None
    g = nx.read_graphml(graphml)
    if g.is_directed():
        g = g.to_undirected()
    return g


@st.cache_data(show_spinner="加载演示案例归档…")
def load_demo_cases() -> list[dict]:
    cases = []
    for p in sorted((PROJECT_ROOT / "outputs" / "demo_cases").glob("case*.json")):
        try:
            cases.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue
    return cases


@st.cache_data(show_spinner="加载 112 条金标准陈述…")
def load_statements() -> dict[str, dict]:
    out: dict[str, dict] = {}
    p = PROJECT_ROOT / "data" / "seed" / "probiopsy_statements.csv"
    if not p.exists():
        return out
    for row in csv.DictReader(p.open(encoding="utf-8-sig")):
        out[row["statement_id"]] = {
            "text": row.get("statement_text_en", ""),
            "stem": row.get("stem_name", ""),
            "locator": row.get("source_locator", ""),
            "action": row.get("expected_system_action", ""),
        }
    return out


@st.cache_data(show_spinner="加载基准评估摘要…")
def load_eval_summary() -> dict | None:
    return _load_json(PROJECT_ROOT / "outputs" / "evaluation_summary.json")


# ─────────────────────────────────────────────────────────────────────────────
# Shared renderers
# ─────────────────────────────────────────────────────────────────────────────
def confidence_gauge(conf: float, action: str = "report_option"):
    """Altair donut gauge for the arbiter confidence."""
    import altair as alt
    conf = max(0.0, min(1.0, float(conf or 0)))
    color = ACTION_COLORS.get(action, ACTION_COLORS["report_option"])["bg"]
    df = pd.DataFrame({"v": [conf, max(0.0, 1 - conf)], "c": [color, "#e5e7eb"], "o": [0, 1]})
    arc = alt.Chart(df).mark_arc(innerRadius=52, outerRadius=82).encode(
        theta=alt.Theta("v:Q", stack=True),
        color=alt.Color("c:N", scale=None, legend=None),
        order=alt.Order("o:Q"),
    )
    txt = alt.Chart(pd.DataFrame({"t": [f"{conf:.0%}"]})).mark_text(
        fontSize=24, fontWeight="bold", color="#111827").encode(text="t:N")
    return (arc + txt).properties(width=190, height=190)


def render_pipeline_flow(timings: dict, n_rules: int, n_lexical: int,
                         graph_chars: int, action: str) -> None:
    """Horizontal 3-layer flow with per-stage wall-clock."""
    t = timings or {}
    rule_ms = float(t.get("rule_ms", 0))
    graph_ms = float(t.get("graph_ms", 0))
    lex_ms = float(t.get("lexical_ms", 0))
    arb_ms = float(t.get("arbiter_ms", 0))
    ev_ms = graph_ms + lex_ms
    c = ACTION_COLORS.get(action, ACTION_COLORS["report_option"])["bg"]

    def ms(v: float) -> str:
        return f"{v:,.0f} ms" if v >= 1 else "≈0 ms"

    st.markdown(f"""
    <div style="display:flex; gap:6px; align-items:stretch; margin: 0.4rem 0 0.8rem;">
      <div class="flow-box" style="border-top:4px solid #d97706;">
        <div class="t">① 规则引擎</div>
        <div class="v">{n_rules} 条命中</div>
        <div class="m">{ms(rule_ms)} · 纯确定性匹配</div>
      </div>
      <div class="flow-arrow">➜</div>
      <div class="flow-box" style="border-top:4px solid #0ea5e9;">
        <div class="t">② 证据检索</div>
        <div class="v">图谱 {graph_chars:,} 字 + 词法 {n_lexical} 块</div>
        <div class="m">{ms(ev_ms)} · 图谱 {ms(graph_ms)} / 词法 {ms(lex_ms)}</div>
      </div>
      <div class="flow-arrow">➜</div>
      <div class="flow-box" style="border-top:4px solid {c};">
        <div class="t">③ LLM 仲裁</div>
        <div class="v">{ACTION_LABELS.get(action, action).split(" (")[0]}</div>
        <div class="m">{ms(arb_ms)} · 硬约束受控生成</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_timing_bar(timings: dict) -> None:
    """Altair horizontal bars for per-stage latency."""
    import altair as alt
    t = timings or {}
    rows = [
        {"阶段": "① 规则引擎", "耗时 (ms)": float(t.get("rule_ms", 0))},
        {"阶段": "② 图谱检索", "耗时 (ms)": float(t.get("graph_ms", 0))},
        {"阶段": "② 词法检索", "耗时 (ms)": float(t.get("lexical_ms", 0))},
        {"阶段": "③ LLM 仲裁", "耗时 (ms)": float(t.get("arbiter_ms", 0))},
    ]
    df = pd.DataFrame(rows)
    total = max(1.0, df["耗时 (ms)"].sum())
    df["占比"] = (df["耗时 (ms)"] / total * 100).round(1).astype(str) + "%"
    ch = alt.Chart(df).mark_bar().encode(
        x=alt.X("耗时 (ms):Q", title="毫秒"),
        y=alt.Y("阶段:N", sort=["① 规则引擎", "② 图谱检索", "② 词法检索", "③ LLM 仲裁"]),
        color=alt.Color("阶段:N", legend=None,
                        scale=alt.Scale(range=["#d97706", "#0ea5e9", "#38bdf8", "#8b5cf6"])),
        tooltip=["阶段:N", alt.Tooltip("耗时 (ms):Q", format=",.0f"), "占比:N"],
    ).properties(height=170, title="三层流水线耗时分解")
    st.altair_chart(ch, width="stretch")


def render_citation_trace(citations: list, assets) -> None:
    """Chips + expandable provenance for verdict citations (Q-codes / EV ids)."""
    if not citations:
        st.caption("本次裁决未携带引用。")
        return
    chips = "".join(f'<span class="cite-chip">{c}</span>' for c in citations)
    st.markdown(f'<div style="margin:0.2rem 0 0.6rem;">引用溯源：{chips}</div>',
                unsafe_allow_html=True)
    statements = load_statements()
    chunk_map = {ch.chunk_id: ch for ch in assets.store.chunks}
    with st.expander(f"🔎 展开引用原文（{len(citations)} 条）"):
        for c in citations:
            if c in statements:
                s = statements[c]
                st.markdown(f"**{c}** · {s['stem']} · `{s['locator']}` · "
                            f"期望动作 `{s['action']}`")
                st.write(s["text"] or "（陈述文本缺失）")
            elif c in chunk_map:
                ch = chunk_map[c]
                st.markdown(f"**{c}** · {ch.source_locator} · level {ch.level}")
                st.write((ch.text or "")[:900])
            else:
                st.markdown(f"**{c}** — 未在金标准陈述或证据库中定位（可能是复合引用）")
            st.divider()


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
# TAB 2 — 智能问答 / Chat (context-only retrieval + single GLM pass)
# ─────────────────────────────────────────────────────────────────────────────
def _build_grounded_prompt(question: str, hits, graph_ctx: str) -> tuple[str, list[dict]]:
    """Number the evidence blocks so the model can cite [证据N] and we can trace back."""
    blocks, meta = [], []
    for i, r in enumerate(hits, 1):
        ch = r.chunk
        blocks.append(f"【证据{i}】({ch.chunk_id} | {ch.source_locator})\n{ch.text}")
        meta.append({"n": i, "chunk_id": ch.chunk_id, "locator": ch.source_locator,
                     "text": ch.text, "score": r.score})
    prompt = "【Evidence blocks】\n" + "\n\n".join(blocks)
    if graph_ctx.strip():
        prompt += "\n\n【Knowledge-graph context (entities/relations, retrieval-only)】\n" \
                  + graph_ctx[:3500]
    prompt += f"\n\n【Question】\n{question}"
    return prompt, meta


def chat_tab() -> None:
    st.header("💬 智能问答")
    st.caption("检索 LightRAG 知识图谱（仅上下文模式）+ 实体加权词法检索（357 条 ProBIOPSY 证据块），"
               "再由 GLM 单次生成回答；证据编号可溯源，不足时明说，不编造。")

    if not Path(INDEX_DIR).exists():
        st.error("🚫 LightRAG 索引未构建。请先执行 Phase 4 构建。")
        return

    adapter = get_adapter()
    llm = get_chat_llm()
    assets = get_assets()
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
                         width="stretch"):
                st.session_state["chat_pending"] = q

    show_evidence = st.toggle("显示检索证据原文", value=True, key="chat_show_ev")
    if st.button("🧹 清空对话"):
        st.session_state["chat_messages"] = []
        st.rerun()

    st.session_state.setdefault("chat_messages", [])
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                if msg.get("latency"):
                    st.caption(msg["latency"])
                if show_evidence and msg.get("evidence"):
                    _render_chat_evidence(msg["evidence"])

    question = st.session_state.pop("chat_pending", None) or st.chat_input(
        "向 agent 提问…（例如：bpMRI 能否替代 mpMRI 用于前列腺癌诊断？）")
    if not question:
        return

    st.session_state["chat_messages"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        answer, meta, latency = "", [], ""
        with st.status("🧠 三层证据检索 + GLM 生成中…", expanded=False) as status:
            t0 = time.perf_counter()
            try:
                t1 = time.perf_counter()
                graph_ctx = adapter.query(question, mode="hybrid", only_need_context=True) or ""
                t_graph = time.perf_counter() - t1
                status.update(label="🕸️ 图谱上下文就绪，词法检索中…")
                t2 = time.perf_counter()
                hits = assets.store.retrieve(question, k=6)
                t_lex = time.perf_counter() - t2
                status.update(label=f"✍️ GLM 生成中（思考模型约 10–50s）…")
                if not hits and not graph_ctx.strip():
                    answer = "知识库中未检索到与该问题相关的证据，无法回答。请尝试更具体的关键词。"
                else:
                    prompt, meta = _build_grounded_prompt(question, hits, graph_ctx)
                    t3 = time.perf_counter()
                    resp = llm.complete(
                        prompt=prompt,
                        system=(
                            "You are a medical Q&A assistant grounded in a ProBIOPSY consensus "
                            "knowledge base. Answer ONLY from the numbered evidence blocks and "
                            "graph context below; if they are insufficient, say so explicitly. "
                            "Answer in Chinese with numbered points, and cite [证据N] tags for "
                            "every claim that comes from an evidence block."
                        ),
                    )
                    t_gen = time.perf_counter() - t3
                    answer = resp.text if not resp.degraded else (
                        "LLM 调用失败（限流/网络），请稍后重试。")
                    latency = (f"⏱ 图谱检索 {t_graph:.1f}s · 词法检索 {t_lex:.2f}s · "
                               f"GLM 生成 {t_gen:.1f}s · 共 {time.perf_counter() - t0:.1f}s"
                               + (" · ⚠️ 降级输出" if resp.degraded else ""))
            except Exception as e:
                answer = f"检索/生成失败: {type(e).__name__}: {e}"
            status.update(label="回答完成", state="complete", expanded=False)

        st.write(answer)
        if latency:
            st.caption(latency)
        if show_evidence and meta:
            _render_chat_evidence(meta)

    st.session_state["chat_messages"].append(
        {"role": "assistant", "content": answer, "evidence": meta, "latency": latency})


def _render_chat_evidence(meta: list[dict]) -> None:
    with st.expander(f"📚 检索证据（{len(meta)} 段，编号与 [证据N] 对应）"):
        for m in meta:
            tag = f"**【证据{m['n']}】** `{m['chunk_id']}` · {m['locator']} · score {m['score']:.2f}"
            st.markdown(tag)
            st.write((m["text"] or "")[:600] + ("..." if len(m["text"] or "") > 600 else ""))
            st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — 决策评估 / Decision (scenario × items → full pipeline + visualisation)
# ─────────────────────────────────────────────────────────────────────────────
def _load_registries():
    a_rows = list(csv.DictReader(
        (PROJECT_ROOT / "data" / "seed" / "entities_a.csv").open(encoding="utf-8-sig")))
    b_rows = list(csv.DictReader(
        (PROJECT_ROOT / "data" / "seed" / "entities_b.csv").open(encoding="utf-8-sig")))
    return a_rows, b_rows


def _demo_case_loader(assets, a_labels: dict, b_options: dict) -> None:
    cases = load_demo_cases()
    if not cases:
        return
    st.subheader("🧪 演示案例一键加载")
    st.caption("论文 5 个端到端演示案例（Supplementary S3）——加载后可查看归档报告（零成本）或实时重跑"
               "（重跑直接使用归档 JSON 中的 flags/决策项，与归档裁决条件完全一致）。")
    cols = st.columns(len(cases))
    for i, case in enumerate(cases):
        with cols[i]:
            if st.button(case["title"].split("（")[0][:16], key=f"case{i}",
                         help=case["title"], width="stretch"):
                st.session_state["dec_case"] = case
                # prefill multiselects as a VISUAL HINT only (the run uses the case's
                # own flags/items — the archived cases predate a registry flag rename,
                # so reverse-mapping flags to scenarios is lossy). Scenarios are ranked
                # by flag-overlap ratio and the closest ones are shown.
                case_flags = set(case.get("patient_flags", []))
                scored = []
                for lab, (_fid, flags) in a_labels.items():
                    if flags:
                        overlap = len(case_flags & set(flags)) / len(flags)
                        scored.append((overlap, lab))
                scored.sort(reverse=True)
                st.session_state["dec_sel_a"] = [lab for ov, lab in scored[:8] if ov >= 0.5]
                inv_b = {v: k for k, v in b_options.items()}
                st.session_state["dec_sel_b"] = [inv_b[iid] for iid in case.get("decision_items", [])
                                                 if iid in inv_b]
                st.rerun()


def decision_tab() -> None:
    st.header("🔍 穿刺决策评估")
    st.caption("选择患者临床情境（可多选，flags 取并集）+ 待决策的穿刺决策项 → "
               "规则引擎 + LightRAG + GLM 仲裁 → 5 类动作裁决报告。")

    a_rows, b_rows = _load_registries()
    assets = get_assets()
    adapter = get_adapter()
    agent = get_arbiter()

    a_labels = {
        f"{r['patient_clinical_scenario_id']}: {r['primary_name'][:48]}":
            (r["patient_clinical_scenario_id"], [f for f in (r.get("flags") or "").split("|") if f])
        for r in a_rows
    }
    b_options = {
        f"{r['entity_b_id']}: {r['generic_name'][:52]}": r["entity_b_id"]
        for r in b_rows
    }

    _demo_case_loader(assets, a_labels, b_options)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**👩 患者临床情境要素**（Entity A）")
        picked_a = st.multiselect("选择情境要素", options=list(a_labels),
                                  key="dec_sel_a", help="可多选；flags 取并集")
        patient_flags: set[str] = set()
        for lab in picked_a:
            patient_flags.update(a_labels[lab][1])
        st.caption(f"合并 flags（{len(patient_flags)}）: `{', '.join(sorted(patient_flags)) or '—'}`")

        manual = st.text_input("手动补充 flags（逗号分隔，可选）", "")
        if manual.strip():
            patient_flags.update(f.strip() for f in manual.split(",") if f.strip())

    with c2:
        st.markdown("**🌍 穿刺决策项**（Entity B）")
        search = st.text_input("搜索决策项", "", placeholder="🔍 例如 psma / scheme / abx")
        filtered = [k for k in b_options if search.lower() in k.lower()] if search else list(b_options)
        picked_b = st.multiselect("选择决策项", options=filtered,
                                  key="dec_sel_b", help="可多选，每项对应一条 ProBIOPSY 陈述")
        decision_items = {b_options[k] for k in picked_b}

    # demo-mode banner: the run uses the archived case's own flags/items
    case = st.session_state.get("dec_case")
    if case:
        bc1, bc2 = st.columns([4, 1])
        with bc1:
            st.info(f"🧪 演示模式：《{case['title']}》— 评估将使用归档案例自带的 "
                    f"{len(case['patient_flags'])} 个 flags + {len(case['decision_items'])} 个决策项"
                    f"（与论文归档报告同条件），上方选择器仅作展示。")
        with bc2:
            if st.button("✖ 退出演示模式", width="stretch"):
                st.session_state.pop("dec_case", None)
                st.rerun()

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

    # archived demo-case report (zero-cost replay)
    if case and st.button(f"📄 查看《{case['title']}》归档报告（零 LLM 成本）",
                          width="stretch", key="dec_view_archived"):
        with st.expander("📋 归档报告（点击展开）", expanded=True):
            st.json(case)
            md_path = PROJECT_ROOT / "outputs" / "demo_cases" / f"{case['case_id']}.md"
            if md_path.exists():
                st.markdown(md_path.read_text(encoding="utf-8"))

    rule_only = st.checkbox(
        "⚡ 仅规则引擎快速预览（跳过图谱检索与 LLM 仲裁，秒级返回；裁决类别不出）",
        value=False, key="dec_rule_only")

    if not st.button("🚀 开始评估", type="primary", width="stretch", key="dec_run"):
        return
    if case is not None:
        # demo mode: replay the archived case under its EXACT original conditions
        patient_flags = set(case.get("patient_flags", []))
        decision_items = set(case.get("decision_items", []))
        question = case.get("question") or build_question(sorted(decision_items), assets.items)
    if not decision_items:
        st.warning("请至少选择一个穿刺决策项。")
        return
    if not patient_flags:
        st.warning("请至少选择一个患者情境要素（或手动补充 flags）。")
        return
    if case is None:
        question = build_question(sorted(decision_items), assets.items)

    use_adapter = None if rule_only else adapter
    use_agent = None if rule_only else agent
    with st.status("🚀 运行三层流水线…", expanded=True) as status:
        if rule_only:
            st.write("⚡ 快速预览模式：仅规则引擎（图谱检索与 LLM 仲裁已跳过）")
        else:
            st.write("① 规则引擎（确定性匹配）→ ② 图谱+词法证据检索 → ③ GLM 仲裁"
                     "（思考模型，约 20–55s）")
        try:
            res = run_pipeline(
                question=question,
                patient_flags=patient_flags,
                decision_items=decision_items,
                assets=assets,
                adapter=use_adapter,
                agent=use_agent,
                use_graph=not rule_only,
            )
            status.update(label="评估完成", state="complete", expanded=False)
        except Exception as e:
            status.update(label="评估失败", state="error")
            st.error(f"评估失败: {type(e).__name__}: {e}")
            return

    st.divider()
    hero_col, gauge_col = st.columns([4, 1])
    with hero_col:
        render_verdict_hero(res.verdict, res.elapsed, len(res.rule_matches), len(res.lexical_hits))
    with gauge_col:
        if not rule_only:
            st.altair_chart(confidence_gauge(res.verdict.get("confidence", 0),
                                             res.verdict.get("action", "report_option")),
                            width="stretch")

    if not rule_only:
        render_pipeline_flow(res.timings, len(res.rule_matches), len(res.lexical_hits),
                             len(res.graph_context), res.verdict.get("action", "report_option"))

    st.subheader("🎯 系统裁决依据")
    st.write(res.verdict.get("rationale", ""))

    if not rule_only and res.verdict.get("citations"):
        render_citation_trace(res.verdict["citations"], assets)

    tabs = st.tabs(["📋 完整报告", "⚙️ 规则与硬约束", "📚 证据链", "⏱ 耗时分析", "🔧 元数据"])

    with tabs[0]:
        st.markdown(res.report_md)

    with tabs[1]:
        if not res.rule_matches:
            st.info("未触发任何规则 — 裁决完全由知识图谱 + 仲裁层给出")
        else:
            sev_count: dict[str, int] = {}
            for m in res.rule_matches:
                sev_count[m.rule.severity] = sev_count.get(m.rule.severity, 0) + 1
            chips = " ".join(
                f'<span class="rule-chip" style="border-color:{SEVERITY_COLORS.get(s, "#6b7280")}; '
                f'color:{SEVERITY_COLORS.get(s, "#6b7280")};">{s} × {n}</span>'
                for s, n in sorted(sev_count.items()))
            st.markdown("严重度分布：" + chips, unsafe_allow_html=True)
            for m in res.rule_matches:
                sev_color = SEVERITY_COLORS.get(m.rule.severity, "#6b7280")
                rid = getattr(m.rule, "rule_id", None) or getattr(m.rule, "factor_id", "?")
                st.markdown(
                    f"### <span style='color:{sev_color}'>●</span> {rid} "
                    f"<span class='rule-chip'>{m.rule.severity}</span>",
                    unsafe_allow_html=True)
                st.write(f"**依据**: {m.rule.rationale}")
                rec = getattr(m.rule, "recommendation", "")
                if rec:
                    st.write(f"**建议**: {rec}")
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
        if rule_only:
            st.info("快速预览模式无耗时数据。")
        else:
            render_timing_bar(res.timings)

    with tabs[4]:
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
        with st.expander("timings JSON"):
            st.json(res.timings)

    st.markdown(APP_FOOTER, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — 知识图谱 / Knowledge graph explorer
# ─────────────────────────────────────────────────────────────────────────────
def _kg_subgraph(g, center: str, hops: int, max_nodes: int):
    """Weight-aware ego subgraph: center + top-weight neighbours, expanded by hops."""
    import networkx as nx
    nodes = {center}
    frontier = {center}
    for _ in range(hops):
        nxt = set()
        for u in frontier:
            edges = sorted(g[u].items(), key=lambda kv: -float(kv[1].get("weight", 0) or 0))
            for v, _data in edges:
                if v not in nodes and len(nodes) < max_nodes:
                    nodes.add(v)
                    nxt.add(v)
                if len(nodes) >= max_nodes:
                    break
            if len(nodes) >= max_nodes:
                break
        frontier = nxt
        if not frontier or len(nodes) >= max_nodes:
            break
    return g.subgraph(nodes).copy() if nodes else nx.Graph()


def _kg_pyvis_html(sub, center: str) -> str | None:
    try:
        from pyvis.network import Network
    except ImportError:
        return None
    net = Network(height="620px", width="100%", bgcolor="#ffffff",
                  font_color="#111827", cdn_resources="in_line", directed=False)
    for nid, data in sub.nodes(data=True):
        etype = (data.get("entity_type") or "UNKNOWN")
        color = ENTITY_TYPE_COLORS.get(etype, "#6b7280")
        desc = (data.get("description") or "")[:280]
        weight = float(data.get("weight", 0) or 0)
        label = nid if len(nid) <= 30 else nid[:28] + "…"
        title = (f"<div style='max-width:340px; font-family:sans-serif;'>"
                 f"<b>{nid}</b><br/><i>{ENTITY_TYPE_LABELS.get(etype, etype)}</i>"
                 f"<br/>weight {weight:.0f}<br/>{desc}…</div>")
        size = 22 if nid == center else max(12, min(30, 12 + weight / 3))
        net.add_node(nid, label=label, title=title, color=color, size=size)
    for u, v, data in sub.edges(data=True):
        w = float(data.get("weight", 0) or 0)
        desc = (data.get("description") or "").split("<SEP>")[0][:200]
        net.add_edge(u, v, value=max(0.4, min(8, w / 2)), title=f"w={w:.0f} · {desc}")
    net.force_atlas_2based(gravity=-30, spring_length=120)
    html = net.generate_html(notebook=False)
    return html


def _kg_static_png(sub, center: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import networkx as nx
    fig, ax = plt.subplots(figsize=(10, 7))
    pos = nx.spring_layout(sub, seed=42, k=0.6)
    types = {n: (sub.nodes[n].get("entity_type") or "UNKNOWN") for n in sub.nodes}
    colors = [ENTITY_TYPE_COLORS.get(types[n], "#6b7280") for n in sub.nodes]
    ws = [max(0.4, min(6, float(sub.edges[e].get("weight", 0) or 0) / 3)) for e in sub.edges]
    nx.draw_networkx_edges(sub, pos, ax=ax, width=ws, alpha=0.3)
    nx.draw_networkx_nodes(sub, pos, ax=ax, node_color=colors, node_size=220, alpha=0.9)
    if center in sub:
        nx.draw_networkx_nodes(sub, pos, ax=ax, nodelist=[center], node_color="#ef4444",
                               node_size=420)
    nx.draw_networkx_labels(
        sub, pos, ax=ax,
        labels={n: (n[:16] + "…" if len(n) > 18 else n) for n in sub.nodes}, font_size=7)
    ax.axis("off")
    st.pyplot(fig)
    plt.close(fig)


def kg_tab() -> None:
    st.header("🕸️ 知识图谱浏览器")
    st.caption("直接读取 LightRAG 索引的 GraphML（1,864 实体 / 3,078 关系，来源 357 条 ProBIOPSY 证据块）。"
               "搜索实体 → 展开邻域子图 → 拖拽/缩放/悬停查看属性。")

    g = get_kg()
    if g is None:
        st.error("🚫 未找到 graph_chunk_entity_relation.graphml — 请先构建 LightRAG 索引。")
        return

    top = st.columns(4)
    with top[0]:
        render_stat_card("实体", f"{g.number_of_nodes():,}")
    with top[1]:
        render_stat_card("关系", f"{g.number_of_edges():,}")
    with top[2]:
        import networkx as nx
        try:
            render_stat_card("连通分量", f"{nx.number_connected_components(g)}")
        except Exception:
            render_stat_card("连通分量", "—")
    with top[3]:
        render_stat_card("平均度", f"{2 * g.number_of_edges() / max(1, g.number_of_nodes()):.1f}")

    legend = " ".join(
        f'<span class="rule-chip" style="border-color:{c}; color:{c};">'
        f'{ENTITY_TYPE_LABELS.get(t, t)}</span>'
        for t, c in ENTITY_TYPE_COLORS.items())
    st.markdown("节点类型：" + legend, unsafe_allow_html=True)

    search = st.text_input("实体搜索", "", placeholder="🔍 例如 transperineal / PI-RADS / PSA density")
    if search.strip():
        matches = [n for n in g.nodes if search.lower() in n.lower()][:30]
        if not matches:
            st.warning("没有匹配的实体，试试更短的关键词。")
            return
        center = st.selectbox("选择中心实体", matches)
    else:
        by_weight = sorted(g.nodes(data=True),
                           key=lambda nd: -float(nd[1].get("weight", 0) or 0))[:15]
        center = st.selectbox("选择中心实体（未搜索时按权重 Top-15 推荐）",
                              [nd[0] for nd in by_weight])

    c1, c2 = st.columns(2)
    with c1:
        hops = st.slider("展开跳数", 1, 2, 1)
    with c2:
        max_nodes = st.slider("节点上限", 20, 120, 60, step=10)

    sub = _kg_subgraph(g, center, hops, max_nodes)
    if sub.number_of_nodes() == 0:
        st.warning("子图为空。")
        return

    st.subheader(f"「{center}」的 {hops}-跳邻域（{sub.number_of_nodes()} 节点 / "
                 f"{sub.number_of_edges()} 边）")
    html = _kg_pyvis_html(sub, center)
    if html is not None:
        components.html(html, height=650, scrolling=False)
    else:
        st.info("pyvis 未安装（`pip install pyvis` 后可交互拖拽/缩放）——当前为静态快照。")
        _kg_static_png(sub, center)

    st.subheader("权重 Top-20 边")
    top_edges = sorted(sub.edges(data=True), key=lambda e: -float(e[2].get("weight", 0) or 0))[:20]
    rows = [{"source": u, "relation": (d.get("description") or "").split("<SEP>")[0][:60],
             "target": v, "weight": float(d.get("weight", 0) or 0)}
            for u, v, d in top_edges]
    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — 基准结果 / Benchmark dashboard
# ─────────────────────────────────────────────────────────────────────────────
METHOD_LABELS = {
    "probiopsy-rag": "前列安汇（完整系统）",
    "lightrag": "LightRAG-only",
    "naive_rag": "naive RAG",
    "pure_llm": "pure LLM",
}
METHOD_COLORS = {
    "probiopsy-rag": "#dc2626", "lightrag": "#0ea5e9",
    "naive_rag": "#8b5cf6", "pure_llm": "#6b7280",
}


def benchmark_tab() -> None:
    st.header("📈 基准结果仪表盘")
    st.caption("4 方法 × 5 种子 × 112 条陈述（2,240 次运行），固定 GLM-5.3-Flash 生成器——"
               "与论文 Table 3 / Figure 2 同源数据。")

    summary = load_eval_summary()
    if not summary:
        st.info("未找到 outputs/evaluation_summary.json —— 先运行 scripts/evaluate.py 生成。")
        return
    methods = summary.get("methods", {})

    # ── grouped metric bars ──────────────────────────────────────────────
    import altair as alt
    metrics = ["exact5", "exact3", "macro_f1", "kappa", "against_f1"]
    rows = []
    for mkey, mdata in methods.items():
        for metric in metrics:
            agg = (mdata.get("aggregate") or {}).get(metric) or {}
            if agg:
                rows.append({
                    "方法": METHOD_LABELS.get(mkey, mkey), "_m": mkey,
                    "指标": METRIC_LABELS[metric], "均值": agg.get("mean", 0),
                    "SD": agg.get("sd", 0),
                })
    if rows:
        df = pd.DataFrame(rows)
        base = alt.Chart(df).encode(
            x=alt.X("指标:N", sort=[METRIC_LABELS[m] for m in metrics], title=None),
            y=alt.Y("均值:Q", scale=alt.Scale(domain=[0, 1]), title="得分"),
            color=alt.Color("方法:N", sort=list(METHOD_LABELS.values()),
                            scale=alt.Scale(
                                domain=[METHOD_LABELS[k] for k in METHOD_LABELS],
                                range=[METHOD_COLORS[k] for k in METHOD_LABELS])),
            tooltip=["方法:N", "指标:N", alt.Tooltip("均值:Q", format=".3f"),
                     alt.Tooltip("SD:Q", format=".3f")],
        )
        bars = base.mark_bar()
        st.altair_chart(bars, width="stretch")
        st.caption("条形 = 5 种子均值；详细数值见 tooltip（含 SD）。")

    c1, c2 = st.columns(2)

    # ── per-seed dots (exact-5) ─────────────────────────────────────────
    with c1:
        st.subheader("exact-5 每种子散点")
        seed_rows = []
        for mkey, mdata in methods.items():
            for s in (mdata.get("seeds") or []):
                seed_rows.append({"方法": METHOD_LABELS.get(mkey, mkey), "_m": mkey,
                                  "种子": f"seed {s.get('seed')}", "exact5": s.get("exact5", 0)})
        if seed_rows:
            df = pd.DataFrame(seed_rows)
            ch = alt.Chart(df).mark_circle(size=90, opacity=0.85).encode(
                x=alt.X("方法:N", sort=list(METHOD_LABELS.values()), title=None),
                y=alt.Y("exact5:Q", scale=alt.Scale(domain=[0, 1]), title="exact-5"),
                color=alt.Color("方法:N", legend=None,
                                scale=alt.Scale(domain=[METHOD_LABELS[k] for k in METHOD_LABELS],
                                                range=[METHOD_COLORS[k] for k in METHOD_LABELS])),
                tooltip=["方法:N", "种子:N", alt.Tooltip("exact5:Q", format=".3f")],
            ).properties(height=300, title="种子间波动小 → 结果稳健（full system SD 0.012）")
            st.altair_chart(ch, width="stretch")

    # ── predicted vs gold class distribution ────────────────────────────
    with c2:
        st.subheader("预测类别分布 vs 金标准")
        dist_rows = []
        for mkey, mdata in methods.items():
            pred = mdata.get("pred_distribution") or {}
            for action, count in pred.items():
                dist_rows.append({"方法": METHOD_LABELS.get(mkey, mkey), "_m": mkey,
                                  "类别": action, "次数": int(count), "类型": "预测"})
            gold = mdata.get("gold_distribution") or pred
            for action, count in gold.items():
                dist_rows.append({"方法": METHOD_LABELS.get(mkey, mkey), "_m": mkey,
                                  "类别": action, "次数": int(count), "类型": "金标准"})
        if dist_rows:
            df = pd.DataFrame(dist_rows)
            df = df[df["方法"] == METHOD_LABELS.get("probiopsy-rag", "probiopsy-rag")]
            ch = alt.Chart(df).mark_bar().encode(
                x=alt.X("类别:N", sort=list(ACTION_CLASSES_ORDER), title=None),
                xOffset="类型:N",
                y=alt.Y("次数:Q", title="运行次数（560/种子聚合）"),
                color=alt.Color("类型:N", scale=alt.Scale(
                    range=["#dc2626", "#9ca3af"]), legend=alt.Legend(title=None)),
                tooltip=["类别:N", "类型:N", "次数:Q"],
            ).properties(height=300, title="完整系统：预测分布贴近金标准")
            st.altair_chart(ch, width="stretch")

    # ── confusion matrix heatmap ─────────────────────────────────────────
    st.subheader("完整系统聚合混淆矩阵（gold → predicted）")
    conf = summary.get("confusion_probiopsy_rag") or {}
    if conf:
        cells = []
        for k, v in conf.items():
            gold, _, pred = k.partition("->")
            cells.append({"金标准": gold, "预测": pred, "次数": int(v)})
        df = pd.DataFrame(cells)
        ch = alt.Chart(df).mark_rect().encode(
            x=alt.X("预测:N", sort=list(ACTION_CLASSES_ORDER), title="预测"),
            y=alt.Y("金标准:N", sort=list(ACTION_CLASSES_ORDER), title="金标准"),
            color=alt.Color("次数:Q", scale=alt.Scale(scheme="blues"),
                            legend=alt.Legend(title="次数")),
            tooltip=["金标准:N", "预测:N", "次数:Q"],
        ).properties(height=320, title="对角线 = 正确；conditional 行的 endorse 泄漏 = 最难类")
        st.altair_chart(ch, width="stretch")
    else:
        st.caption("评估摘要中无混淆矩阵。")

    st.markdown(APP_FOOTER, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    set_page_config()
    st.title("🧬 前列安汇")
    st.caption("患者临床情境 × 穿刺决策项 · 三层混合架构（规则引擎 + LightRAG + LLM 仲裁）· "
               "v3 交互式问答可视化")

    tab_overview, tab_chat, tab_decision, tab_kg, tab_bench = st.tabs(
        ["📊 项目介绍", "💬 智能问答", "🔍 决策评估", "🕸️ 知识图谱", "📈 基准结果"])
    with tab_overview:
        overview_tab()
    with tab_chat:
        chat_tab()
    with tab_decision:
        decision_tab()
    with tab_kg:
        kg_tab()
    with tab_bench:
        benchmark_tab()


if __name__ == "__main__":
    main()
