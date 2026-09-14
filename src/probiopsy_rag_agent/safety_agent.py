"""safety_agent — the LLM arbiter of the hybrid system (PLAN.md §5).

The arbiter composes a final decision from three inputs:
  1. hard constraints from the rule engine (consensus verdict tags);
  2. retrieved evidence (LightRAG dual-level context or lexical chunks);
  3. its own clinical reasoning.

Output contract: strict JSON with a 5-class ``action``:
  endorse | endorse_option | conditional | report_option | against
matching the gold standard's ``expected_system_action`` encoding of the 112
ProBIOPSY statements:
  Consensus agree      → endorse
  Consensus disagree   → against
  neither (median 4-6) → conditional
  SOQ Consensus        → endorse_option
  SOQ No consensus     → report_option
"""
from __future__ import annotations

import json
import re

from .llm_client import LLMClient
from .risk_rules import RuleMatch

ACTION_CLASSES = ("endorse", "endorse_option", "conditional", "report_option", "against")

_SYSTEM = (
    "You are the safety arbiter of a clinical decision-support system for "
    "prostate biopsy. You must obey HARD CONSTRAINTS derived from the "
    "ProBIOPSY international consensus rule engine. Choose exactly one action "
    "class and answer with a single JSON object, no prose outside the JSON."
)

_PROMPT = """Decision under consideration: {question}

Patient scenario flags: {patient_flags}

HARD CONSTRAINTS from the consensus rule engine (must be obeyed):
{constraints}
{no_constraints}

Evidence from the knowledge base (ProBIOPSY consensus statements and trials):
{evidence}

Task: decide the action class for the decision under consideration for this patient.
Action classes:
- "endorse": the consensus agrees (median 7-9 with agreement) — recommend outright.
- "endorse_option": the statement achieved super-majority (SOQ) consensus — present as an endorsed option.
- "conditional": consensus neither agrees nor disagrees (median 4-6) — present with conditions/alternatives.
- "report_option": no consensus and no majority — report as an open option without endorsement.
- "against": the consensus disagrees (median 1-3) — recommend against.

HARD CONSTRAINTS override everything: if a constraint says the consensus REJECTS the
decision, the action must be "against"; if it says the consensus ENDORSES it, the action
must not be "against".

Answer with exactly this JSON (no markdown fences):
{{"action": "<one of the 5 classes>", "confidence": <0-1 float>, "rationale": "<=60 words, must cite statement ids like Q43 or medians where available", "citations": ["<chunk ids or Q ids used>"]}}"""


def _constraints_block(matches: list[RuleMatch]) -> tuple[str, str]:
    lines: list[str] = []
    for m in matches:
        lines.append(f"Rule {m.rule.rule_id} (severity {m.rule.severity}): {m.rule.rationale}")
        lines += [f"  - {c}" for c in m.hard_constraints]
    if not lines:
        return "  (none — no consensus rule matched this scenario)", ""
    return "\n".join("  " + l if not l.startswith("  ") else l for l in lines), ""


class SafetyAgent:
    def __init__(self, client: LLMClient | None = None) -> None:
        self.client = client or LLMClient(provider="deepseek", temperature=0.0)

    def decide(
        self,
        question: str,
        patient_flags: list[str] | set[str],
        rule_matches: list[RuleMatch],
        evidence: str,
    ) -> dict:
        constraints, _ = _constraints_block(rule_matches)
        prompt = _PROMPT.format(
            question=question,
            patient_flags=", ".join(sorted(patient_flags)) or "(none)",
            constraints=constraints,
            no_constraints="" if rule_matches else "",
            evidence=evidence[:8000] or "(no evidence retrieved)",
        )
        last_err = ""
        for attempt in range(2):
            resp = self.client.complete(prompt=prompt, system=_SYSTEM)
            if getattr(resp, "degraded", False):
                last_err = resp.text[:150]
                continue
            parsed = _parse_json(resp.text)
            if parsed and parsed.get("action") in ACTION_CLASSES:
                parsed["rationale"] = str(parsed.get("rationale", ""))[:400]
                parsed["citations"] = list(parsed.get("citations") or [])[:8]
                return parsed
            last_err = resp.text[:150]
        return {
            "action": "report_option",
            "confidence": 0.0,
            "rationale": f"arbiter fallback (invalid/unavailable LLM output): {last_err}",
            "citations": [],
            "degraded": True,
        }


def _parse_json(text: str) -> dict | None:
    """Tolerant JSON extraction (handles fences and leading prose)."""
    t = text.strip()
    m = re.search(r"\{.*\}", t, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        try:
            fixed = re.sub(r",\s*([}\]])", r"\1", m.group(0))
            return json.loads(fixed)
        except Exception:
            return None


def extract_action(text: str) -> str:
    """Extract the 5-class action from a free-text baseline answer.

    Baselines are instructed to end with ``FINAL ACTION: <class>``; if they
    don't, fall back to keyword mapping over the answer text.
    """
    m = re.search(r"FINAL\s+ACTION\s*[:\-]\s*(endorse[_ ]option|report[_ ]option|endorse|against|conditional)", text, re.I)
    if m:
        return m.group(1).lower().replace(" ", "_")
    low = text.lower()
    if "recommend against" in low or "not be recommended" in low or "should not" in low and "recommend" in low:
        return "against"
    if "no consensus" in low and ("report" in low or "option" in low):
        return "report_option"
    if "conditional" in low or "neither" in low:
        return "conditional"
    if "endorse" in low or "recommend" in low:
        return "endorse"
    return "report_option"
