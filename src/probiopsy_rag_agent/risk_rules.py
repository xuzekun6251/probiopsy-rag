"""risk_rules — rule engine over the A×B interaction skeleton.

Rule semantics (ProBIOPSY domain):
  - Entity A = patient clinical-scenario elements (flags in entities_a.csv).
  - Entity B = biopsy decision items (ids in entities_b.csv, ``d_*``).
  - A rule fires when ``entity_a_flags ∩ patient_flags`` AND
    ``entity_b_flags ∩ decision_items_under_consideration``.
  - The B registry ``flags`` column carries the consensus verdict per item:
    ``endorsement_{consensus|majority|against|neither}`` +
    ``action_{recommend|against|conditional|report_only}``.

The engine exposes these verdict tags as HARD CONSTRAINTS to the LLM arbiter:
  - ``endorsement_against``          → the arbiter must not endorse the item.
  - ``endorsement_consensus`` + ``action_recommend`` → the arbiter must not
    reject the item outright.
Exact class selection (endorse vs endorse_option vs conditional vs
report_option) is left to the arbiter, which also reads the statement-level
evidence (median + interpretation) retrieved from the evidence store.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Rule:
    rule_id: str
    severity: str
    risk_type: str
    entity_a_flags: list[str]
    entity_b_flags: list[str]
    rationale: str
    recommendation: str
    citations: list[dict] = field(default_factory=list)


@dataclass
class DecisionItem:
    item_id: str
    name: str
    endorsement: str   # consensus | majority | against | neither
    action: str        # recommend | against | conditional | report_only
    topic: str = ""


@dataclass
class PatientFactorRule:
    factor_id: str
    severity: str
    entity_a_flags: list[str]
    entity_b_flags: list[str]
    rationale: str


@dataclass
class RuleMatch:
    rule: Rule
    matched_items: list[DecisionItem]      # B items that are under consideration
    matched_a_flags: list[str]

    @property
    def hard_constraints(self) -> list[str]:
        """Human/LLM-readable hard constraints derived from the verdict tags."""
        out: list[str] = []
        for item in self.matched_items:
            if item.endorsement == "against":
                out.append(
                    f"HARD: the consensus explicitly REJECTS '{item.item_id}' "
                    f"({item.name}) — do not endorse it."
                )
            elif item.endorsement == "consensus" and item.action == "recommend":
                out.append(
                    f"HARD: the consensus ENDORSES '{item.item_id}' ({item.name}) "
                    f"— do not reject it outright."
                )
        return out


_ACTION_RE = re.compile(r"action_(recommend|against|conditional|report_only)")
_ENDORSE_RE = re.compile(r"endorsement_(consensus|majority|against|neither)")


def load_rules(path: str | Path) -> list[Rule]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    rules: list[Rule] = []
    for r in data.get("rules", []) or []:
        rules.append(Rule(
            rule_id=r["id"],
            severity=r.get("severity", "medium"),
            risk_type=r.get("risk_type", ""),
            entity_a_flags=list(r.get("entity_a_flags") or []),
            entity_b_flags=list(r.get("entity_b_flags") or []),
            rationale=(r.get("rationale") or "").strip(),
            recommendation=(r.get("recommendation") or "").strip(),
            citations=list(r.get("citations") or []),
        ))
    return rules


def load_decision_items(path: str | Path) -> dict[str, DecisionItem]:
    """Load entities_b.csv → {item_id: DecisionItem} with verdict tags parsed."""
    items: dict[str, DecisionItem] = {}
    with Path(path).open(encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            item_id = (list(row.values())[0] or "").strip()
            flags = row.get("flags") or ""
            act = _ACTION_RE.search(flags)
            end = _ENDORSE_RE.search(flags)
            items[item_id] = DecisionItem(
                item_id=item_id,
                name=(row.get("generic_name") or "").strip(),
                endorsement=end.group(1) if end else "neither",
                action=act.group(1) if act else "conditional",
            )
    return items


def load_patient_factor_rules(path: str | Path) -> list[PatientFactorRule]:
    """Load the ``patient_factor_rules`` section of rules.yaml (escalation layer).

    These modifiers do not carry their own consensus verdicts; they escalate an
    existing rule with a patient-specific rationale (see rules.yaml §Patient
    factor escalation rules).
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    out: list[PatientFactorRule] = []
    for fid, spec in (data.get("patient_factor_rules") or {}).items():
        spec = spec or {}
        out.append(PatientFactorRule(
            factor_id=fid,
            severity=spec.get("severity", "medium"),
            entity_a_flags=list(spec.get("matching_entity_a_flags") or []),
            entity_b_flags=list(spec.get("matching_entity_b_flags") or []),
            rationale=(spec.get("rationale") or "").strip(),
        ))
    return out


def match_patient_factors(
    pfrs: list[PatientFactorRule],
    patient_flags: set[str],
    decision_items: set[str],
    item_catalog: dict[str, DecisionItem] | None = None,
) -> list[RuleMatch]:
    """Fire patient-factor escalations (A∩ and B∩, same semantics as rules).

    Synthesized RuleMatches use ``PF-<factor_id>`` ids and ``risk_type=
    patient_factor``; their hard constraints derive from the B-catalog verdict
    tags of the matched items (real consensus verdicts), never from the
    modifier itself.
    """
    matches: list[RuleMatch] = []
    for p in pfrs:
        a_hit = sorted(patient_flags & set(p.entity_a_flags))
        b_hit = sorted(decision_items & set(p.entity_b_flags))
        if not a_hit or not b_hit:
            continue
        matched = [
            (item_catalog or {}).get(bid)
            or DecisionItem(bid, bid, "neither", "conditional")
            for bid in b_hit
        ]
        matches.append(RuleMatch(
            rule=Rule(
                rule_id=f"PF-{p.factor_id}",
                severity=p.severity,
                risk_type="patient_factor",
                entity_a_flags=p.entity_a_flags,
                entity_b_flags=p.entity_b_flags,
                rationale=p.rationale,
                recommendation="",   # escalation rationale only; no separate advice
                citations=[],
            ),
            matched_items=matched,
            matched_a_flags=a_hit,
        ))
    order = {"high": 0, "medium": 1, "low": 2, "unknown": 3}
    matches.sort(key=lambda m: order.get(m.rule.severity, 3))
    return matches


def match_rules(
    rules: list[Rule],
    patient_flags: set[str],
    decision_items: set[str],
    item_catalog: dict[str, DecisionItem] | None = None,
) -> list[RuleMatch]:
    """Fire every rule whose A-flags intersect patient_flags AND whose B-flags
    intersect the decision items under consideration."""
    matches: list[RuleMatch] = []
    for rule in rules:
        a_hit = sorted(patient_flags & set(rule.entity_a_flags))
        b_hit = sorted(decision_items & set(rule.entity_b_flags))
        if not a_hit or not b_hit:
            continue
        matched = [
            (item_catalog or {}).get(bid)
            or DecisionItem(bid, bid, "neither", "conditional")
            for bid in b_hit
        ]
        matches.append(RuleMatch(rule=rule, matched_items=matched, matched_a_flags=a_hit))
    # highest severity first
    order = {"high": 0, "medium": 1, "low": 2, "unknown": 3}
    matches.sort(key=lambda m: order.get(m.rule.severity, 3))
    return matches
