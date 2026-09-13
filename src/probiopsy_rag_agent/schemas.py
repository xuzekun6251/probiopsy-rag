from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class RiskLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


RISK_ORDER: dict[RiskLevel, int] = {
    RiskLevel.UNKNOWN: 0,
    RiskLevel.LOW: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.HIGH: 3,
}


class EntityA(BaseModel):
    """Entity A registry record.

    Domain (probiopsy-rag): a **patient clinical scenario element** (imaging finding,
    biomarker, clinical presentation, infection-risk history, treatment intent, or
    resource-availability condition) that modulates prostate-biopsy decisions.

    CSV column is `patient_clinical_scenario_id`; the pydantic field keeps the
    TongYuan-compatible name `entity_a_id` (rule engine / evaluators depend on it),
    with a population alias mapping the CSV header.
    """
    entity_a_id: str = Field(alias="patient_clinical_scenario_id")
    primary_name: str = ""
    aliases: list[str] = Field(default_factory=list)
    category: str = ""
    active_mechanisms: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    evidence_sources: list[str] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class EntityB(BaseModel):
    """Entity B registry record.

    Domain (probiopsy-rag): a **prostate-biopsy decision item** (imaging-pathway
    choice, ancillary test gating, biopsy scheme, SBx template, route/anaesthesia/
    prophylaxis, or treatment-planning linkage) that the system recommends on,
    against, or conditionally. `metabolic_pathways` is repurposed as the decision
    action (recommend/against/conditional/report_only) and `transporter_substrates`
    as the linked ProBIOPSY statement ids.
    """
    entity_b_id: str
    generic_name: str
    aliases: list[str] = Field(default_factory=list)
    drug_class: str = ""
    flags: list[str] = Field(default_factory=list)
    metabolic_pathways: list[str] = Field(default_factory=list)
    transporter_substrates: list[str] = Field(default_factory=list)
    narrow_therapeutic_index: bool = False
    label_source: str = ""


class PatientFactors(BaseModel):
    factors: list[str] = Field(default_factory=list)


class InteractionCase(BaseModel):
    case_id: str
    entity_a: str
    entity_b: str
    patient_factors: list[str] = Field(default_factory=list)
    gold_risk_level: RiskLevel | None = None
    risk_type: list[str] = Field(default_factory=list)
    notes: str = ""


class EvidenceChunk(BaseModel):
    evidence_id: str
    title: str
    source: str
    source_type: str
    evidence_level: str = ""
    evidence_relation: str = ""
    source_locator: str = ""
    citation_hint: str = ""
    pmid: str = ""
    doi: str = ""
    verification_status: str = ""
    source_quality_rank: str = ""
    entities_a: list[str] = Field(default_factory=list)
    entities_b: list[str] = Field(default_factory=list)
    risk_types: list[str] = Field(default_factory=list)
    text: str
    url: str = ""
    weight: int = 1


class RiskSignal(BaseModel):
    rule_id: str
    risk_level: RiskLevel
    risk_type: str
    rationale: str
    recommendation: str
    matched_terms: dict[str, list[str]] = Field(default_factory=dict)


class RiskAssessment(BaseModel):
    risk_level: RiskLevel
    risk_types: list[str] = Field(default_factory=list)
    signals: list[RiskSignal] = Field(default_factory=list)
    confidence: str = "low"
    confidence_score: float = 0.0


class SafetyReport(BaseModel):
    case_id: str
    entity_a: str
    entity_b: str
    patient_factors: list[str] = Field(default_factory=list)
    risk_assessment: RiskAssessment
    evidence: list[EvidenceChunk] = Field(default_factory=list)
    report_text: str
    context_char_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
