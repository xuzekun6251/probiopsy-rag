"""pipeline — shared orchestration for the demo cases + Streamlit app (Phase 6).

Composes the three layers exactly as the benchmarked system does
(``run_baselines.run_probiopsy_rag``):
  1. rule engine   — match_rules over rules.yaml (+ patient-factor escalations);
  2. evidence      — LightRAG graph context (embedding-only retrieval) +
                     lexical statement retrieval with entity boosts;
  3. LLM arbiter   — SafetyAgent.decide → 5-class verdict.

Interactive callers (demo script, Streamlit) use :func:`run_pipeline`; the
benchmark inlines the same steps so the evaluated system and the demoed
system stay identical.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

try:
    from .evidence_store import EvidenceStore, Retrieved
    from .report import render_report
    from .risk_rules import (
        DecisionItem,
        RuleMatch,
        load_decision_items,
        load_patient_factor_rules,
        load_rules,
        match_patient_factors,
        match_rules,
    )
except ImportError:  # direct-run fallback (scripts run from repo root)
    from evidence_store import EvidenceStore, Retrieved  # type: ignore
    from report import render_report  # type: ignore
    from risk_rules import (  # type: ignore
        DecisionItem,
        RuleMatch,
        load_decision_items,
        load_patient_factor_rules,
        load_rules,
        match_patient_factors,
        match_rules,
    )

ROOT = Path(__file__).resolve().parents[2]
RULES_PATH = ROOT / "configs" / "rules.yaml"
ITEMS_PATH = ROOT / "data" / "seed" / "entities_b.csv"
SCENARIOS_PATH = ROOT / "data" / "seed" / "entities_a.csv"
CHUNKS_PATH = ROOT / "data" / "seed" / "evidence_chunks.jsonl"
INDEX_DIR = ROOT / "data" / "processed" / "lightrag_index"


@dataclass
class ProjectAssets:
    rules: list
    items: dict[str, DecisionItem]
    pfrs: list
    store: EvidenceStore


def load_assets() -> ProjectAssets:
    """Load rule engine + evidence store (cheap, cacheable by callers)."""
    return ProjectAssets(
        rules=load_rules(RULES_PATH),
        items=load_decision_items(ITEMS_PATH),
        pfrs=load_patient_factor_rules(RULES_PATH),
        store=EvidenceStore(CHUNKS_PATH),
    )


@dataclass
class PipelineResult:
    question: str
    patient_flags: list[str] = field(default_factory=list)
    decision_items: list[str] = field(default_factory=list)
    rule_matches: list[RuleMatch] = field(default_factory=list)
    graph_context: str = ""
    lexical_hits: list[Retrieved] = field(default_factory=list)
    lexical_context: str = ""
    evidence: str = ""
    verdict: dict = field(default_factory=dict)
    elapsed: float = 0.0
    report_md: str = ""


def build_question(decision_items: list[str], items: dict[str, DecisionItem],
                   extra: str = "") -> str:
    """Compose a decision question from the selected decision items."""
    names = [f"{iid} ({items[iid].name})" if iid in items else iid for iid in decision_items]
    q = "Should the following decision(s) be taken: " + "; ".join(names) + "?"
    if extra:
        q = f"{extra} {q}"
    return q


def run_pipeline(
    question: str,
    patient_flags: list[str] | set[str],
    decision_items: list[str] | set[str],
    assets: ProjectAssets,
    adapter=None,          # LightRAGAdapter | None (None → lexical only)
    agent=None,            # SafetyAgent | None (None → rule-only placeholder verdict)
    use_graph: bool = True,
    k_lexical: int = 5,
) -> PipelineResult:
    t0 = time.time()
    flags = set(patient_flags)
    item_set = set(decision_items)

    # 1) rule engine
    matches = match_rules(assets.rules, flags, item_set, assets.items)
    matches += match_patient_factors(assets.pfrs, flags, item_set, assets.items)

    # 2) evidence: graph context (embedding-only) + lexical statement retrieval
    graph_ctx = ""
    if adapter is not None and use_graph:
        try:
            graph_ctx = adapter.query(question, mode="hybrid", only_need_context=True) or ""
        except Exception as e:  # degrade to lexical, never crash the pipeline
            graph_ctx = f"(graph retrieval failed: {e})"
    hits = assets.store.retrieve(
        question, k=k_lexical, boost_entities_b=item_set, boost_entities_a=flags
    )
    lex_ctx = assets.store.pack_context(hits, char_budget=3500)
    evidence = (
        (graph_ctx[:5500] + "\n\n--- lexical evidence ---\n\n" + lex_ctx)
        if graph_ctx.strip() else lex_ctx
    )

    # 3) arbiter
    if agent is not None:
        verdict = agent.decide(question, sorted(flags), matches, evidence)
    else:
        verdict = {
            "action": "conditional",
            "confidence": 0.0,
            "rationale": "rule-only mode (no LLM arbiter) — verdict class not determined",
            "citations": [],
            "degraded": True,
        }

    evidence_lines = [
        f"[{r.chunk.chunk_id}|{r.chunk.level}|{r.chunk.source_locator}] (score {r.score:.2f})"
        for r in hits
    ]
    res = PipelineResult(
        question=question,
        patient_flags=sorted(flags),
        decision_items=sorted(item_set),
        rule_matches=matches,
        graph_context=graph_ctx,
        lexical_hits=hits,
        lexical_context=lex_ctx,
        evidence=evidence,
        verdict=verdict,
        elapsed=time.time() - t0,
    )
    res.report_md = render_report(question, sorted(flags), matches, verdict, evidence_lines)
    return res
