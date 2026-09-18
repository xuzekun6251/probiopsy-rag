# Internal Pre-Submission Review (Simulated Peer Review)

**Manuscript:** QianLieAnHui: development and benchmark validation of a hybrid rule-engine, knowledge-graph, and LLM-arbitration decision-support system for the prostate biopsy pathway, against the ProBIOPSY international consensus
**Target journal:** European Urology Open Science (Original Research)
**Reviewer simulation:** three-person panel (urology clinician; medical-AI methods reviewer; statistical reviewer)
**Date:** 2026-09-18 · **Status of this document:** internal quality gate, not for submission

---

## Summary Statement

The manuscript presents a three-layer decision-support system (deterministic rule engine, LightRAG knowledge-graph retrieval, LLM arbitration) for the prostate biopsy pathway, evaluated statement-by-statement against the 112 final statements of the ProBIOPSY consensus with a fixed-generator, multi-seed benchmark (2,240 runs). The architecture-vs-model claim is well supported by a genuinely well-controlled experiment, the writing is clear, and the traceability story is compelling and appropriate for the journal's readership.

**Recommendation: Major revision (internal).** No flaw invalidates the core claim, but several reporting gaps would draw fire from real reviewers: the full-system confusion matrix — which reveals a substantial residual weakness (conditional recall 0.51) — is never reported; inferential statistics are absent; one quantitative claim about baselines is imprecise; a cited figure panel and a cited supplementary material do not yet exist; and three figures are never cited in the text.

**Key strengths**
- Fixed-generator design cleanly isolates architecture from model tier; the flagship-tier supplement strengthens this further.
- Class-collapse analysis (Figure 2C now added) is an unusually honest and informative evaluation beyond headline accuracy.
- Complete provenance chain (Q-codes → rules → evidence chunks) matches current clinical-governance concerns.

**Key weaknesses**
- Residual conditional-class failure is undisclosed; readers see only aggregate metrics.
- "Structurally missing from LLM and RAG baselines" overstates: pure LLM emits endorse_option in 16.1% of runs (90/560) — it places them wrongly rather than never emitting them.
- Dangling internal references (Figure 2C before this revision; supplementary tables; Tables 1–2; Figure 1).

---

## Major Comments

**M1. The full-system confusion matrix is never reported, and it contains the study's most instructive negative result.**
The aggregated confusion matrix (from `outputs/evaluation_summary.json` and `scripts/internal_review_stats.py`) shows conditional recall of 95/185 = 0.51, with 74 of 185 gold-conditional statements predicted as *endorse* — i.e., when the system errs on conditional endorsement, it errs in the over-permissive direction, precisely the direction clinical governance worries about. This must be reported (Results + Limitations + supplementary table). *Action: ADD — done in this revision (Results §"Residual errors", Table S1).*

**M2. Imprecise baseline-collapse claim.**
Abstract/Intro/Discussion state that conditional and endorse_option are "structurally missing" from LLM and RAG baselines. The data support this for the two RAG baselines (conditional 3/560 and 6/560) but **not** for pure LLM (conditional 14/560 = 2.5%; endorse_option 90/560 = 16.1%). The defensible claim is: RAG baselines nearly never emit these classes, and **no baseline places them correctly** (all κ ≤ 0.53). Wording corrected throughout. The "9 of 1,120 baseline runs" figure is retained but explicitly attributed to the two RAG baselines.

**M3. No inferential statistics.**
Differences are reported as mean ± SD over 5 seeds only. For a methods benchmark this invites the standard "is n=5 enough?" objection. *Action: ADD — paired two-sided t-tests across seeds (full system vs each baseline; exact-5 and κ; 6 tests), Benjamini–Hochberg FDR correction (the figure contract's own mitigation plan). All 6 comparisons remain significant after FDR (worst adjusted p = 8.9×10⁻⁴). Added to Methods and Results.*

**M4. Dangling references.**
(a) Results cited "Figure 2C" but the rendered figure had two panels — panel (c) (predicted class distribution vs gold standard) is now rendered from real prediction data. (b) "per-domain confusion matrices are provided in the supplementary material" — no supplementary existed; Supplementary S1–S4 now built. (c) Tables 1–2 and Figure 1 were never cited; now cited in Methods.

**M5. Figure legends missing.**
The manuscript had no figure-legend section. Added (Figures 1–5; Figure 3 marked pending expert-panel data and excluded from the submission set until filled).

**M6. Abstract over journal limit.**
272 words vs the ~250-word structured-abstract limit for European Urology family Original Research. Trimmed to ≤ 250 words with no loss of quantitative content.

---

## Minor Comments

1. **Ethics section** pointed to a repository filename (`Manuscript_Ethics_Statement.md`); replaced with a self-contained statement.
2. **Ref 1** lacks volume/pages (consensus published 2026; ahead of print) — flagged "in press" status for the submission check-list; verify pagination at submission time.
3. **Terminology consistency**: "Cohen's κ" vs "κ" mixed — unified as "Cohen's κ" at first use, κ thereafter.
4. **Runtime claim** "~20–40 s median latency" has no supporting table in the supplement — S4 now includes the per-case latency figure cross-reference (Figure 5) and the source CSV.
5. **Word count line** (abstract 272) now stale after trimming — updated.
6. **Figure 3**: placeholder files exist with blank expert columns; correctly excluded from the figure set and the legends; the Limitations section already discloses the pending panel. Keep it that way until data exist.
7. **Gold-standard distribution** (endorse 190 / conditional 185 / against 125 / endorse_option 35 / report_option 25) appears only implicitly; added explicitly to the Validation-set section — reviewers need it to interpret the collapse analysis.
8. **arXiv citations** (refs 10, 11): fine for preprints, but add version/date at submission.
9. **Keywords**: 9 keywords is above common limits (6–8); trimmed to 8.
10. **Data availability** states files that will be "released with the repository" — GitHub/Zenodo DOIs remain TODO (author action, tracked).

---

## Questions for Authors (answerable in revision or cover letter)

1. Why does the full system's conditional recall cap at 0.51 — is the rule engine's action prior biased toward endorse, or is the arbiter prompt under-weighting conditional? (Answer in Discussion: conditional is intrinsically the boundary class between endorse and endorse_option; 74/185 errors predict *endorse*, consistent with the class ordering; future work: class-specific calibration.)
2. Was any statement-level overlap check performed between the 218 literature-entry chunks and the gold statements (circularity quantification)? (Answered in Limitation 1 as exposure-to-text risk; a quantitative dedup check could be added in revision if requested.)
3. Are the five demonstration cases part of the 112-statement evaluation set? (No — synthetic vignettes over the same registries; clarified in Methods.)

---

## Verification appendix (all numbers re-derived from artifacts)

| Claim in manuscript | Source | Verified |
|---|---|---|
| exact-5 0.805 ± 0.012 / κ 0.730 ± 0.016 / macro-F1 0.825 ± 0.022 / against-F1 0.908 ± 0.023 | evaluation_summary.json probiopsy-rag aggregate | ✓ |
| lightrag 0.613 / 0.536 / 0.525 / 0.881; naive 0.605 / 0.514 / 0.512 / 0.890; pure 0.304 / 0.254 / 0.079 / 0.346 | evaluation_summary.json aggregates | ✓ |
| RAG conditional 3/560 & 6/560; pure_llm conditional 14/560, endorse_option 90/560 | pred_distribution per method | ✓ (wording fixed) |
| full system: endorse 280 / conditional 95 / against 115 / report 32 / endorse_option 38 (560) | pred_distribution | ✓ |
| against sens 0.872 / spec 0.986 | aggregate | ✓ |
| flagship: naive 0.605→0.538, κ 0.512→0.450; pure 0.288, κ 0.132 | evaluation_summary_glm53_baselines.json | ✓ |
| paired t, BH-FDR: all 6 tests p_fdr ≤ 8.9e-4 | internal_review_stats.py (scipy 1.18.1) | ✓ new |
| conditional recall 95/185 = 0.514; 74 conditional→endorse | confusion_full_flash_aggregated | ✓ new |
| per-domain totals 115/170/275 = 560 | confusion_full_per_domain | ✓ new |
