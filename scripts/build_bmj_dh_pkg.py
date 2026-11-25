# -*- coding: utf-8 -*-
"""Build the BMJ Digital Health submission extras under outputs/submission/bmj_dh/:
cover letter, plain language summary, and a completed DECIDE-AI reporting checklist.

The DECIDE-AI checklist rows (Vasey B et al. BMJ 2022;377:e070904) were extracted
from the open-access full text via Europe PMC (PMC9116198) and are stored verbatim
in scripts/decide_ai_checklist_rows.json so the build is offline-reproducible.

This study is a preclinical development / offline benchmark validation study, not a
live clinical evaluation; checklist items are answered with that adaptation stated
explicitly (same approach as Sesen et al., BMJ Digit Health 2026, for guideline CDS).
"""
import json
import re
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Mm, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "submission" / "bmj_dh"
ROWS = json.loads((ROOT / "scripts" / "decide_ai_checklist_rows.json").read_text(encoding="utf-8"))

ASCII, EA = "Times New Roman", "宋体"

TITLE = ("QianLieAnHui: development and benchmark validation of a hybrid rule-engine, knowledge-graph, and "
         "LLM-arbitration decision-support agent for the prostate biopsy pathway, against the ProBIOPSY "
         "international consensus")


def new_doc():
    d = Document()
    s = d.sections[0]
    s.page_width, s.page_height = Mm(210), Mm(297)
    s.top_margin = s.bottom_margin = Mm(25.4)
    s.left_margin = s.right_margin = Mm(31.7)
    st = d.styles["Normal"]
    st.font.name = ASCII
    st.font.size = Pt(12)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), EA)
    return d


def par(doc, text, bold=False, size=12, space_after=6, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.3
    r = p.add_run(text)
    r.font.name = ASCII
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    return p


def build_cover_letter():
    d = new_doc()
    par(d, "XU Zekun", bold=True)
    par(d, "Department of Urology, Affiliated Jinhua Hospital, Zhejiang University School of Medicine")
    par(d, "xuzekunurology@163.com (corresponding author)")
    par(d, "")
    par(d, "To: The Editors, BMJ Digital Health", bold=True)
    par(d, "")
    par(d, "Dear Editors,", bold=True)
    par(d, "We are pleased to submit our original research manuscript, \"" + TITLE + ",\" for consideration as an "
           "Original research article in BMJ Digital Health.")
    par(d, "A recent controlled evaluation published in this journal showed that retrieval augmentation improves "
           "clinician-rated correctness for guideline-based question answering in chronic kidney disease, while also "
           "revealing its collapse on questions outside the indexed corpus (Sesen et al., BMJ Digit Health "
           "2026;2:e000041). Our study extends this line of work from a question-answering task to an interventional "
           "decision pathway, and from retrieval architectures to a three-layer hybrid in which a deterministic rule "
           "engine, a knowledge-graph evidence base, and an LLM arbiter cover one another's failure modes. Three "
           "features differentiate the work: (1) the international consensus' 112 final statements themselves serve "
           "as the executable gold standard, with the action space bound to the consensus' voting semantics; (2) four "
           "architectures (pure LLM, naive RAG, GraphRAG-only, and the full agent) were benchmarked under one "
           "generator across five seeds — 2,240 runs; and (3) exploiting the determinism of the lexical retrieval "
           "layer, we decomposed every full-system run into retrieval and arbitration contributions: evidence "
           "coverage was complete, and all residual misclassifications were located in the arbitration layer, "
           "identifying calibration — not retrieval engineering — as the next improvement target. Every "
           "recommendation traces to numbered consensus statements, and the same frozen evidence chain supports a "
           "patient-facing lay-language education mode.")
    par(d, "We believe the manuscript fits the journal's scope of clinically oriented digital health and AI "
           "evaluation, and that its statement-by-statement validation design offers a reusable template for "
           "benchmarking decision-support agents against written guidance in other specialties.")
    par(d, "Declarations. The manuscript is original, is not published elsewhere, and is not under consideration by "
           "another journal. The computational evaluation involved no patient data or biological samples; the corpus "
           "and gold standard derive solely from the published ProBIOPSY consensus, demonstration cases are "
           "synthetic, and the four-expert face-validity review was anonymous and voluntary, so institutional review "
           "board approval was not required (assessment documented during project planning). Reporting follows the "
           "TRIPOD+AI and DECIDE-AI items applicable to a decision-support-system benchmark, and a completed "
           "DECIDE-AI checklist is provided as an additional file. The use of generative AI tools in manuscript "
           "preparation is declared in the manuscript. The corresponding author's ORCID iD will be linked at "
           "submission.")
    par(d, "Data availability. The rule base, dual seed registries, evidence chunk library, gold standard, all raw "
           "prediction records, the residual-error decomposition artefacts, and evaluation scripts are released with "
           "the code repository.")
    par(d, "Thank you for considering our submission.")
    par(d, "")
    par(d, "Yours sincerely,", bold=True)
    par(d, "XU Zekun", bold=True)
    out = OUT / "cover_letter_BMJ_DH.docx"
    d.save(out)
    print(f"[docx] {out} ({out.stat().st_size:,} bytes)")


def build_plain_language_summary():
    d = new_doc()
    par(d, "Plain language summary", bold=True, size=14)
    par(d, "Why is this topic important? Deciding who needs a prostate biopsy — and how it should be done — "
           "determines whether prostate cancer is found and treated appropriately, yet practice varies widely "
           "between hospitals and countries.")
    par(d, "What was the aim of the study? To turn an international consensus on prostate biopsy (112 agreed "
           "statements) into a computer assistant that gives auditable advice at the decision point, and to measure "
           "how closely its advice matches the consensus.")
    par(d, "How did we do it? The assistant combines fixed rules that mechanically block advice contradicting the "
           "consensus, a searchable knowledge base built from the consensus that shows where every piece of advice "
           "comes from, and an AI language model that produces the final recommendation within these guardrails. We "
           "tested four system variants against all 112 statements, 2,240 times in total, and analysed where the "
           "remaining mistakes came from.")
    par(d, "What did we find? The full system matched the consensus in about 8 of 10 cases (80.5%), clearly better "
           "than using an AI language model alone (30.4%) or retrieval without rules. Every answer can be traced "
           "back to the numbered consensus statement behind it, and the same knowledge base can explain biopsy "
           "decisions to patients in plain language.")
    par(d, "What does this mean? Written clinical guidelines can be turned into executable, auditable decision "
           "support. Before clinical use, the system needs calibration of its arbitration layer, versioned guideline "
           "updates, and prospective testing with real patients.")
    out = OUT / "plain_language_summary_BMJ_DH.docx"
    d.save(out)
    print(f"[docx] {out} ({out.stat().st_size:,} bytes)")


# Reported-location strings, aligned 1:1 with the item rows kept from ROWS below
# (grouping rows 'Title and abstract' / 'Introduction' / ... are rendered as table
# section headers; meta rows 0-2 are skipped).
REPORTED = [
    # Title and abstract
    "Reported — the title identifies the study as development and benchmark validation of a decision-support agent "
    "for the prostate biopsy pathway against the ProBIOPSY consensus (Title; Title page).",
    "Reported — structured abstract (Objective / Methods and analysis / Results / Conclusions) states intended use, "
    "architecture, the 112-statement evaluation cohort, and outcomes.",
    # Introduction
    "Reported — Introduction (clinical problem, current practice variation, intended patient population).",
    "Reported — Introduction, 'This paper examines' paragraph: intended users at the decision point, care-pathway "
    "integration, and the patient-facing education mode.",
    "Reported — Introduction, final paragraph (study objectives).",
    # Methods
    "Reported (adapted) — Methods, 'Study design and ethics': protocol registration is not applicable to an offline "
    "benchmark; IRB non-requirement assessment documented. No trial registration.",
    "Not applicable in the DECIDE-AI sense (no live patients). Adapted: the evaluation cohort is the 112 consensus "
    "statements × 51 synthetic patient-scenario archetypes — Methods, 'Validation set' and 'Input layer: dual "
    "registries' (Table 1).",
    "Not applicable — no clinician users were recruited for the benchmark. A separate four-expert blinded "
    "face-validity panel is described in Methods, 'Study design and ethics'.",
    "Not applicable — no users operating the system in clinical practice.",
    "Reported — Methods, 'System architecture' and 'Implementation and reproducibility' (rule engine, GraphRAG "
    "(LightRAG implementation), arbiter; generator GLM-5.3-Flash frozen; code released).",
    "Reported — Methods, 'Input layer: dual registries' and 'Layer 2' (evidence chunks; corpus derived solely from "
    "the published consensus).",
    "Reported — Methods, 'Layer 3' (five-action verdict with confidence and statement citations; Figure 1), and "
    "Figure 5 for a full reasoning trace.",
    "Reported (adapted) — Methods, 'Benchmark protocol' (offline computational evaluation; 4 architectures × 5 seeds "
    "× 112 statements).",
    "Not applicable — offline benchmark; care-pathway positioning is discussed in Discussion, 'Clinical implications'.",
    "Reported — Methods, 'Evaluation metrics' (primary: exact-5 accuracy; secondary: macro-F1, Cohen's κ, "
    "against-F1, specificity).",
    "Reported (adapted) — misclassification is defined against the statement-level gold standard (Methods, "
    "'Evaluation metrics'; Results, 'Residual errors').",
    "Not applicable — no patients were involved; the safety-oriented design (deterministic hard constraints) is "
    "described in Methods, 'Layer 1', and discussed in the Discussion.",
    "Not applicable — no human-factors framework was used in the offline benchmark; expert face validity is reported "
    "separately (Results, 'Face validity').",
    "Reported — Methods, 'Statistical analysis'.",
    "Reported — Methods, 'Study design and ethics'; no algorithmic-fairness methodology was applied.",
    "Reported — Methods, 'Patient and public involvement' (patients and/or the public were not involved).",
    # Results
    "Not applicable — no real patients; scenario-archetype characteristics are reported in Table 1.",
    "Not applicable — no users in the benchmark; the expert panel is described in Methods, 'Study design and ethics'.",
    "Not applicable — no users; system usage is reported as runtime cost (Results, 'Running cost').",
    "Not applicable — no clinical workflow was modified.",
    "Reported — Results, 'Benchmark overview and headline performance' (Table 3; Figure 2).",
    "Reported — Results, 'Domain breakdown' (Table 4).",
    "Reported (adapted) — the system was frozen during evaluation; the generator-tier supplementary experiment is "
    "described in Methods, 'Benchmark protocol', and Results, 'Generator-tier supplementary experiment'.",
    "Reported (adapted) — system-expert agreement: four-expert blinded face-validity review (Results, 'Face "
    "validity'; Figure 3). These experts did not operate the system in clinical practice, so human-computer "
    "agreement in the DECIDE-AI sense is not applicable.",
    "Reported (adapted) — all residual misclassifications are enumerated and decomposed (Results, 'Residual errors'; "
    "outputs/failure_decomposition.json and the per-run CSV released with the code).",
    "Not applicable — no patients; no possibility of harm in an offline benchmark.",
    "Not applicable — no usability evaluation; the patient education mode is demonstrated qualitatively (Results, "
    "'Patient education').",
    "Not applicable — no users, hence no learning curves.",
    # Discussion
    "Reported — Discussion, 'Principal findings' and 'Clinical implications'.",
    "Reported (adapted) — safety-oriented analysis: against-class F1 0.908 (specificity 0.986), hard-constraint "
    "behaviour, and the residual-error decomposition (Results; Discussion).",
    "Reported — Limitations and Future directions.",
    # Statements
    "Reported — Data availability section (code repository and Zenodo archive).",
    "Reported — Funding and Conflicts of interest sections.",
]

# Row structure of decide_ai_checklist_rows.json (verbatim from PMC9116198):
#   row 0 = 4-col header; rows 1-2 = grouping rows ("1-17"/"I-X"); six single-cell
#   section-header rows; main item rows = 3 cells [no, theme, recommendation];
#   continuation rows = 1 cell whose text starts "b)"/"c)" (11 of them).
# Structure is detected (not hardcoded) and asserted before rendering.
SECTION_ROWS = {0, 1, 2}
SECTION_NAMES = {"Title and abstract", "Introduction", "Methods", "Results", "Discussion", "Statements"}
GROUP_HEADERS, ITEM_IDX = {}, []
for _i, _r in enumerate(ROWS):
    if _i in SECTION_ROWS:
        continue
    if len(_r) == 1 and _r[0] in SECTION_NAMES:
        GROUP_HEADERS[_i] = _r[0]
    else:
        ITEM_IDX.append(_i)
assert sorted(GROUP_HEADERS) == [3, 6, 10, 27, 40, 44], sorted(GROUP_HEADERS)
assert len(ITEM_IDX) == len(REPORTED) == 38, (len(ITEM_IDX), len(REPORTED))
# theme labels with a known source typo ("Al" for "AI" in the published table)
THEME_FIX = {"Al system": "AI system"}


def build_decide_checklist():
    d = new_doc()
    par(d, "DECIDE-AI reporting checklist — completed for this submission", bold=True, size=14)
    par(d, "Reference: Vasey B, Nagendran M, Campbell B, et al. Reporting guideline for the early stage clinical "
           "evaluation of decision support systems driven by artificial intelligence: DECIDE-AI. BMJ 2022;377:e070904.",
           size=10)
    par(d, "Scope note. DECIDE-AI is designed for the early live clinical evaluation of AI-driven decision support "
           "systems as an intervention. The present study is a preclinical development and offline benchmark "
           "validation study: no live clinical care, no clinician users operating the system, and no real patients "
           "were involved. The checklist is completed with this adaptation stated explicitly — items that "
           "presuppose a live clinical evaluation are marked 'Not applicable' or answered with their closest "
           "preclinical analogue, following the approach of Sesen et al. (BMJ Digit Health 2026;2:e000041) for "
           "guideline-based clinical decision support. Page numbers are not yet assigned; locations refer to "
           "manuscript section headings (the submitted manuscript carries continuous line numbering).", size=10)

    t = d.add_table(rows=1, cols=3)
    t.style = "Table Grid"
    hdr = t.rows[0].cells
    for j, h in enumerate(["Item No", "DECIDE-AI recommendation", "Reported in this manuscript"]):
        hdr[j].text = ""
        p = hdr[j].paragraphs[0]
        p.paragraph_format.line_spacing = 1.1
        r = p.add_run(h)
        r.font.name = ASCII
        r.font.size = Pt(10)
        r.font.bold = True

    it = iter(REPORTED)
    last_no = ""

    def fill(cell, runs):
        cell.text = ""
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.1
        for txt, bold in runs:
            r = p.add_run(txt)
            r.font.name = ASCII
            r.font.size = Pt(9.5)
            r.font.bold = bold

    for i, row in enumerate(ROWS):
        if i in SECTION_ROWS:
            continue
        if i in GROUP_HEADERS:
            cells = t.add_row().cells
            cells[0].merge(cells[2])
            p = cells[0].paragraphs[0]
            r = p.add_run(GROUP_HEADERS[i])
            r.font.name = ASCII
            r.font.size = Pt(10)
            r.font.bold = True
            continue
        where = next(it)
        cells = t.add_row().cells
        if len(row) >= 3:
            no, theme, rec = row[0], row[1], row[2]
            theme = THEME_FIX.get(theme, theme)
            if re.fullmatch(r"\d+", no):
                last_no = no
            fill(cells[0], [(no, True)])
            fill(cells[1], [(theme + ": ", True), (rec, False)] if theme else [(rec, False)])
        else:
            # continuation row: full recommendation text in cell 0, e.g. "b) Describe ..."
            m = re.match(r"^([a-z])\)", row[0])
            no = f"{last_no}{m.group(1)}" if m else ""
            fill(cells[0], [(no, True)])
            fill(cells[1], [(row[0], False)])
        fill(cells[2], [(where, False)])

    out = OUT / "DECIDE-AI_checklist_BMJ_DH.docx"
    d.save(out)
    print(f"[docx] {out} ({out.stat().st_size:,} bytes)")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    build_cover_letter()
    build_plain_language_summary()
    build_decide_checklist()


if __name__ == "__main__":
    main()
