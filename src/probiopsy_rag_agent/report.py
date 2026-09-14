"""report — structured decision-report rendering for the full system.

Renders the SafetyAgent verdict + rule matches + evidence into the
clinician-facing markdown report used by the demo cases (Phase 6) and the
Streamlit app. The report is the unit of the expert-blind-evaluation phase.
"""
from __future__ import annotations

from .risk_rules import RuleMatch

_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "unknown": 3}

_ACTION_LABEL = {
    "endorse": "推荐 (Consensus endorse)",
    "endorse_option": "推荐选项 (SOQ-endorsed option)",
    "conditional": "有条件考虑 (Conditional / neither)",
    "report_option": "报告为开放选项 (No consensus — report only)",
    "against": "不推荐 (Consensus against)",
}


def render_report(
    question: str,
    patient_flags: list[str],
    rule_matches: list[RuleMatch],
    verdict: dict,
    evidence_used: list[str] | None = None,
) -> str:
    lines: list[str] = []
    action = verdict.get("action", "report_option")
    lines.append("## 前列安汇 decision report")
    lines.append("")
    lines.append(f"**Decision under consideration:** {question}")
    lines.append("")
    lines.append(f"**Patient scenario flags:** {', '.join(patient_flags) or '(none)'}")
    lines.append("")
    lines.append(f"### Verdict: {_ACTION_LABEL.get(action, action)}")
    lines.append("")
    lines.append(f"{verdict.get('rationale', '')}")
    lines.append("")
    lines.append(f"*Confidence:* {verdict.get('confidence', 0):.2f}")
    lines.append("")

    if rule_matches:
        lines.append("### Triggered consensus rules")
        lines.append("")
        for m in sorted(rule_matches, key=lambda x: _SEVERITY_ORDER.get(x.rule.severity, 3)):
            cites = "; ".join(
                (c.get("ref", "") if isinstance(c, dict) else str(c)) for c in m.rule.citations
            )
            lines.append(
                f"- **{m.rule.rule_id}** ({m.rule.severity}) — {m.rule.recommendation} "
                f"*[citations: {cites}]*"
            )
            for c in m.hard_constraints:
                lines.append(f"  - {c}")
        lines.append("")
    else:
        lines.append("### Triggered consensus rules")
        lines.append("")
        lines.append("- (none matched — decision falls to the knowledge-graph + arbiter layer)")
        lines.append("")

    if evidence_used:
        lines.append("### Evidence grounding")
        lines.append("")
        for e in evidence_used[:8]:
            lines.append(f"- {e}")
        lines.append("")

    cites = verdict.get("citations") or []
    if cites:
        lines.append("### Citations")
        lines.append("")
        lines.append(", ".join(str(c) for c in cites))
        lines.append("")
    lines.append("---")
    lines.append("*Decision support only — not a substitute for clinical judgement. "
                 "Verdicts trace to ProBIOPSY consensus statements (Eur Urol 2026).*")
    return "\n".join(lines)
