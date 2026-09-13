# -*- coding: utf-8 -*-
"""Build the evidence base (data/seed/evidence_chunks.jsonl) for probiopsy-rag.

Sources (all local, deterministic):
  1. ProBIOPSY consensus main text  -> section chunks (consensus narrative)
  2. ProBIOPSY Supplementary Material 2 (systematic review evidence summary)
  3. ProBIOPSY reference lists (55 main + 90 SM2)     -> citation records
  4. 112 consensus statements (gold CSV)              -> B_consensus chunks

Source quality ranks (domain-adapted from TongYuan Level A-E):
  A_guideline   EAU / AUA guideline statements quoted inside the corpus
  B_consensus   ProBIOPSY consensus statements (the paper's gold standard)
  C_rct_meta    RCTs / systematic reviews & meta-analyses (consensus references)
  D_review      narrative reviews, secondary descriptions, consensus narrative

Entity linking: chunks are tagged with entity A ids / entity B ids via keyword
match against the registries (aliases + names). These tags drive naive_rag
keyword retrieval and enrich LightRAG chunk metadata.

Dedup: sha1 of normalized text; PMID/DOI kept on the first occurrence.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from probiopsy_rag_agent.schemas import EvidenceChunk  # noqa: E402

MAIN_TXT = ROOT / "data/raw/ProBIOPSY_consensus_main.txt"
SUPP_TXT = ROOT / "data/raw/ProBIOPSY_mmc1_supplementary.txt"
STMT_CSV = ROOT / "data/seed/probiopsy_statements.csv"
OUT = ROOT / "data/seed/evidence_chunks.jsonl"

CONSENSUS_DOI = "10.1016/j.eururo.2026.06.012"


def _norm(t: str) -> str:
    """Fix PDF ligature/quote artifacts and collapse whitespace."""
    t = (t.replace("\ufb01", "fi").replace("\ufb02", "fl")
          .replace("\ufb00", "ff").replace("\ufb03", "ffi").replace("\ufb04", "ffl")
          .replace("\u201c", '"').replace("\u201d", '"')
          .replace("\u2018", "'").replace("\u2019", "'")
          .replace("\u2013", "-").replace("\u2014", "-")
          .replace("\u00a0", " "))
    return re.sub(r"[ \t]+", " ", t)


def _hash(text: str) -> str:
    return hashlib.sha1(" ".join(text.lower().split()).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- entity tags
def _load_registry_keywords() -> tuple[list[tuple[str, list[str]]], list[tuple[str, list[str]]]]:
    """Return (a_keywords, b_keywords): (id, [lowercased search terms])."""
    a_kw: list[tuple[str, list[str]]] = []
    with io.open(ROOT / "data/seed/entities_a.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            terms = [row["primary_name"].lower()]
            terms += [a.lower() for a in row["aliases"].split("|") if a]
            a_kw.append((row["patient_clinical_scenario_id"], terms))
    b_kw: list[tuple[str, list[str]]] = []
    with io.open(ROOT / "data/seed/entities_b.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            terms = [row["generic_name"].lower()]
            terms += [a.lower() for a in row["aliases"].split("|") if a]
            b_kw.append((row["entity_b_id"], terms))
    return a_kw, b_kw


# flag -> entity_a_id index (scenario_flags in the gold CSV use flag vocabulary)
def _load_flag_to_a() -> dict[str, list[str]]:
    idx: dict[str, list[str]] = {}
    with io.open(ROOT / "data/seed/entities_a.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for fl in row["flags"].split("|"):
                if fl:
                    idx.setdefault(fl, []).append(row["patient_clinical_scenario_id"])
    return idx


# narrative-chunk keyword map for entity B tagging (registry generic_name
# sentences rarely appear verbatim in prose; these are the canonical corpus terms)
B_TERM_MAP: dict[str, list[str]] = {
    "d_mri_driven_pathway": ["mri-driven pathway", "mri driven", "diagnostic pathway"],
    "d_accept_any_field_strength": ["1.5t and 3t", "3t and 1.5t", "magnetic field strength", "field strength"],
    "d_mri_quality_check": ["quality check", "quality standards", "image quality"],
    "d_use_piqual_v2": ["pi-qual"],
    "d_bpmri_acceptable": ["bpmri", "biparametric"],
    "d_report_max3_lesions": ["number of lesions", "maximal number of lesions"],
    "d_contrast_mri_for_pz_indeterminate": ["contrast-enhanced mri"],
    "d_followup_indeterminate_bpmri": ["follow-up is needed", "followed over time"],
    "d_psad_gate_bpmri_indeterminate": ["psa density"],
    "d_psad_gate_mpmri_indeterminate": ["psa density"],
    "d_riskcalc_gate_mpmri_indeterminate": ["risk calculator"],
    "d_riskcalc_gate_bpmri_indeterminate": ["risk calculator"],
    "d_biomarker_gate_bpmri_indeterminate": ["biomarker"],
    "d_biomarker_gate_mpmri_indeterminate": ["biomarker"],
    "d_reject_psma_pet_upfront": ["psma pet"],
    "d_psma_pet_negative_mri_ancillary": ["psma pet-ct", "psma pet"],
    "d_psma_pet_indeterminate_ancillary": ["psma pet-ct", "psma pet"],
    "d_reject_microultrasound_upfront": ["micro-ultrasound", "microultrasound", "micro-us"],
    "d_reject_microultrasound_indeterminate": ["micro-ultrasound", "microultrasound"],
    "d_reject_microultrasound_negative_mri": ["micro-ultrasound", "microultrasound"],
    "d_sbx_negative_mri_high_suspicion": ["negative mri", "negative prostate mri"],
    "d_ai_mri_lesion_aid": ["ai algorithms", "artificial intelligence"],
    "d_tbx_cores_adapt_pirads": ["targeted cores"],
    "d_tbx_min3_cores": ["targeted cores", "cores per target", "cores per lesion"],
    "d_adopt_term_perilesional": ["perilesional"],
    "d_plbx_within_10mm": ["10-mm margin", "10 mm", "perilesional"],
    "d_plbx_count_by_lesion_size": ["perilesional"],
    "d_plbx_2cores_small_lesion": ["perilesional"],
    "d_plbx_max2cores_large_lesion": ["perilesional"],
    "d_scheme_unifocal_tbx_plbx": ["unifocal", "tbx + plbx", "tbx+plbx"],
    "d_scheme_unifocal_add_contralateral": ["contralateral"],
    "d_scheme_unifocal_add_sbx": ["systematic b"],
    "d_scheme_ipsilateral_multifocal": ["multifocal ipsilateral"],
    "d_scheme_bilateral_tbx_plbx": ["multifocal bilateral", "bilateral"],
    "d_sbx_12core_template": ["12-core", "12 cores", "6 cores per lobe"],
    "d_reject_sextant_template": ["sextant"],
    "d_reject_ginsburg_template": ["ginsburg"],
    "d_reject_saturation_bx": ["saturation"],
    "d_sbx_reduced_6core_advanced": ["reduced to a maximum of 6 cores", "max 6 cores"],
    "d_route_transperineal": ["transperineal"],
    "d_pnb_tr": ["periprostatic nerve block"],
    "d_pnb_tp": ["periprostatic nerve block"],
    "d_omit_abx_tp_no_risk": ["antibiotic prophylaxis", "antibiotics"],
    "d_augmented_abx_tr": ["antibiotic prophylaxis", "augmented"],
    "d_tp_focal_add_contralateral": ["focal therapy", "focal treatment"],
    "d_tp_focal_tbx_only_not_enough": ["focal therapy", "focal treatment"],
    "d_tp_nss_unifocal_tbx_plbx": ["nerve-sparing", "nerve sparing"],
    "d_tp_nss_bilateral_tbx_adequate": ["nerve-sparing", "nerve sparing"],
    "d_tp_plnd_unifocal_no_consensus": ["lymphadenectomy", "lymph node"],
    "d_tp_plnd_bilateral_tbx_plbx": ["lymphadenectomy", "lymph node"],
    "d_tp_wg_rt_tbx_plbx": ["whole-gland radiotherapy", "whole gland radiotherapy", "radiotherapy"],
    "d_tp_focal_boost_tbx_plbx": ["focal boost", "boost"],
    "d_tp_adt_duration_tbx_plbx": ["adt", "androgen deprivation"],
    "d_tp_reject_adding_systematic_universal": ["adt", "boost"],
}


def _tag_entities(text: str, a_kw, b_kw, b_terms) -> tuple[list[str], list[str]]:
    low = text.lower()
    a_hits = [eid for eid, terms in a_kw if any(t in low for t in terms if len(t) > 3)]
    b_hits = [eid for eid, terms in b_kw if any(t in low for t in terms if len(t) > 3)]
    b_hits += [bid for bid, terms in b_terms if any(t in low for t in terms)]
    # dedupe, preserve order
    a_hits = list(dict.fromkeys(a_hits))[:8]
    b_hits = list(dict.fromkeys(b_hits))[:8]
    return a_hits, b_hits


# ---------------------------------------------------------------- section split
MAIN_SECTIONS = [
    ("abstract", r"Abstract(.+?)ADVANCING PRACTICE"),
    ("what_this_study_adds", r"What does this study add\?(.+?)Patient Summary"),
    ("patient_summary", r"Patient Summary(.+?)1\. Introduction"),
    ("introduction", r"1\. Introduction(.+?)2\. Materials and methods"),
    ("methods", r"2\. Materials and methods(.+?)3\. Results"),
    ("results_d1_mri", r"3\.1\. Domain 1(.+?)3\.2\."),
    ("results_d1_lesions", r"3\.2\. Domain 1(.+?)3\.3\."),
    ("results_d1_ancillary", r"3\.3\. Domain 1(.+?)3\.4\."),
    ("results_d1_novel", r"3\.4\. Domain 1(.+?)With respect to arti"),
    ("results_d1_ai", r"With respect to arti\?cial intelligence(.+?)Table 1 -"),
    ("results_d2_cores", r"3\.5\. Domain 2(.+?)3\.6\."),
    ("results_d2_plbx", r"3\.6\. Domain 2(.+?)3\.7\."),
    ("results_d2_schemes", r"3\.7\. Domain 2(.+?)3\.8\."),
    ("results_d2_route", r"3\.8\. Domain 2(.+?)3\.9\."),
    ("results_d3_focal", r"3\.9\. Domain 3(.+?)3\.10\."),
    ("results_d3_nss", r"3\.10\. Domain 3(.+?)3\.11\."),
    ("results_d3_plnd", r"3\.11\. Domain 3(.+?)3\.12\."),
    ("results_d3_rt", r"3\.12\. Domain 3(.+?)3\.13\."),
    ("results_d3_adt", r"3\.13\. Domain 3(.+?)4\. Discussion"),
    ("discussion", r"4\. Discussion(.+?)5\. Conclusion"),
    ("conclusion", r"5\. Conclusion(.+?)Consensus reporting"),
]

SUPP_SECTIONS = [
    ("sm2_sr_methods", r"Supplementary material 2(.+?)Evidence synthesis strategy"),
    ("sm2_d1_biomarkers", r"Prostate biopsy indications on a MRI-driven pathway(.+?)Biopsy procedure aspects"),
    ("sm2_d2_targeting", r"Biopsy procedure aspects(.+?)The role of adding systematic"),
    ("sm2_d2_systematic", r"The role of adding systematic biopsy(.+?)A hot topic of the current"),
    ("sm2_d2_route_safety", r"A hot topic of the current literature(.+?)The choice of the biopsy approach"),
    ("sm2_d2_anaesthesia_needles", r"The choice of the biopsy approach(.+?)Treatment planning according"),
    ("sm2_d3_planning", r"Treatment planning according to biopsy schemes(.+?)References:"),
]


def _extract(text: str, pattern: str) -> str:
    m = re.search(pattern, text, re.S)
    return _norm(m.group(1)).strip() if m else ""


def _parse_main_refs(text: str) -> list[dict]:
    """Parse numbered references [n] ... from the main article."""
    start = text.find("References")
    refs = []
    if start < 0:
        return refs
    block = text[start:]
    pat = re.compile(r"\[(\d+)\]\s+((?:(?!\[\d+\]).)+)", re.S)
    for m in pat.finditer(block):
        num = int(m.group(1))
        body = _norm(m.group(2)).strip()
        body = re.sub(r"Please cite this article.*", "", body, flags=re.S).strip()
        if len(body) < 20:
            continue
        doi_m = re.search(r"(10\.\d{4,}/[^\s,;]+)", body)
        refs.append({"num": num, "body": body, "doi": doi_m.group(1).rstrip(".") if doi_m else ""})
    return refs


def _parse_supp_refs(text: str) -> list[dict]:
    """Parse SM2 numbered references '1. Author...' with trailing line-number artifacts."""
    start = text.find("References:")
    refs = []
    if start < 0:
        return refs
    block = text[start:]
    pat = re.compile(r"(?m)^(\d{1,2})\.\s+((?:(?!^\d{1,2}\.\s).)+)", re.S)
    for m in pat.finditer(block):
        num = int(m.group(1))
        if not (1 <= num <= 99):
            continue
        body = _norm(m.group(2)).strip()
        body = re.sub(r"\s\d{2,3}\s*$", "", body)  # trailing SM line-number artifact
        body = re.sub(r"(\s\d{2,3})\.?\s+doi:", " doi:", body)
        if len(body) < 20:
            continue
        doi_m = re.search(r"(10\.\d{4,}/[^\s,;]+)", body)
        refs.append({"num": num, "body": body, "doi": doi_m.group(1).rstrip(".") if doi_m else ""})
    return refs


def _title_of(ref_body: str) -> str:
    """Heuristic: reference format is 'Authors. Title. Journal.' -> take up to the
    second sentence-ending period, capped at 180 chars."""
    parts = ref_body.split(". ")
    if len(parts) >= 2:
        return ". ".join(parts[:2]).strip()
    return ref_body[:180].strip()


def main() -> None:
    main_text = _norm(io.open(MAIN_TXT, encoding="utf-8").read())
    supp_text = _norm(io.open(SUPP_TXT, encoding="utf-8").read())
    a_kw, b_kw = _load_registry_keywords()
    flag_to_a = _load_flag_to_a()
    b_terms = [(bid, [t.lower() for t in terms]) for bid, terms in B_TERM_MAP.items()]

    chunks: list[EvidenceChunk] = []
    seen: set[str] = set()

    def add(title: str, source: str, source_type: str, rank: str, text: str,
            locator: str, citation_hint: str = "", doi: str = "", pmid: str = "",
            weight: int = 1, a_ids: list[str] | None = None, b_ids: list[str] | None = None):
        text = text.strip()
        if len(text) < 40:
            return
        h = _hash(text)
        if h in seen:
            return
        seen.add(h)
        ea, eb = _tag_entities(text, a_kw, b_kw, b_terms)
        if a_ids:
            ea = sorted(set(ea) | set(a_ids))
        if b_ids:
            eb = sorted(set(eb) | set(b_ids))
        chunks.append(EvidenceChunk(
            evidence_id=f"EV{len(chunks) + 1:04d}",
            title=title, source=source, source_type=source_type,
            evidence_level=rank, evidence_relation="",
            source_locator=locator, citation_hint=citation_hint,
            pmid=pmid, doi=doi, verification_status="corpus_verified",
            source_quality_rank=rank, entities_a=ea, entities_b=eb,
            risk_types=[], text=text, url=f"https://doi.org/{doi}" if doi else "",
            weight=weight,
        ))

    # ---- 1. main-text sections
    for name, pat in MAIN_SECTIONS:
        body = _extract(main_text, pat)
        add(f"ProBIOPSY consensus - {name}", "ProBIOPSY Consensus (Eur Urol 2026)",
            "consensus_narrative", "D_review", body,
            locator=f"Main text / {name}", citation_hint=f"doi:{CONSENSUS_DOI}",
            doi=CONSENSUS_DOI, weight=2)

    # ---- 2. SM2 systematic-review sections
    for name, pat in SUPP_SECTIONS:
        body = _extract(supp_text, pat)
        add(f"ProBIOPSY SM2 evidence summary - {name}",
            "ProBIOPSY Supplementary Material 2", "systematic_review_summary",
            "D_review", body, locator=f"SM2 / {name}",
            citation_hint=f"doi:{CONSENSUS_DOI}", doi=CONSENSUS_DOI, weight=2)

    # ---- 3. statements -> B_consensus chunks (highest weight)
    with io.open(STMT_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            interp = row["interpretation"]
            soq = f" Panel choice: '{row['soq_option']}' ({row['soq_pct']}% of experts)." if row["soq_option"] else ""
            body = (
                f"ProBIOPSY consensus statement {row['statement_id']} "
                f"(domain: {row['domain']}; stem: {row['stem_name']}). "
                f"Statement: {row['statement_text_en']} "
                f"Panel result: {interp}."
                f"{soq} "
                f"Median Likert score: {row['median'] or 'n/a (SOQ)'} "
                f"(30th-70th percentile: {row['p30']}-{row['p70']})."
            )
            add(f"Statement {row['statement_id']}: {row['stem_name']}",
                "ProBIOPSY Consensus Tables 1-3", "consensus_statement",
                "B_consensus", body, locator=row["source_locator"],
                citation_hint=f"doi:{CONSENSUS_DOI}", doi=CONSENSUS_DOI, weight=3,
                a_ids=[aid for fl in row["scenario_flags"].split("|")
                       for aid in flag_to_a.get(fl, [])],
                b_ids=[row["decision_item_id"]] if row["decision_item_id"] else [])

    # ---- 4. reference lists -> citation records
    for ref in _parse_main_refs(main_text):
        title = _title_of(ref["body"])
        add(f"Ref [{ref['num']}]: {title}", "ProBIOPSY Consensus reference list",
            "literature_reference", "C_rct_meta", ref["body"],
            locator=f"Main text ref [{ref['num']}]",
            citation_hint=f"doi:{ref['doi']}" if ref["doi"] else "", doi=ref["doi"])
    for ref in _parse_supp_refs(supp_text):
        title = _title_of(ref["body"])
        add(f"SM2 Ref {ref['num']}: {title}",
            "ProBIOPSY SM2 reference list", "literature_reference",
            "C_rct_meta", ref["body"], locator=f"SM2 ref {ref['num']}",
            citation_hint=f"doi:{ref['doi']}" if ref["doi"] else "", doi=ref["doi"])

    # ---- write
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c.model_dump(), ensure_ascii=False) + "\n")

    from collections import Counter
    ranks = Counter(c.evidence_level for c in chunks)
    tagged_a = sum(1 for c in chunks if c.entities_a)
    tagged_b = sum(1 for c in chunks if c.entities_b)
    print(f"[ok] evidence_chunks.jsonl: {len(chunks)} chunks -> {OUT}")
    print(f"     ranks: {dict(ranks)}")
    print(f"     entity-tagged: A={tagged_a}, B={tagged_b}")
    lens = sorted(len(c.text) for c in chunks)
    print(f"     text length: min={lens[0]}, median={lens[len(lens) // 2]}, max={lens[-1]}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
