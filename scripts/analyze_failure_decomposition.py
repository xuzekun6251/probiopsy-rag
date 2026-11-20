"""analyze_failure_decomposition — split the full system's residual errors into
corpus-gap / retrieval-miss / arbitration-error strata.

Mirrors the retrieval-vs-generation failure analysis of Sesen et al.
(BMJ Digit Health 2026;2:e000041): for every misclassified run, determine
whether the evidence the arbiter needed was (a) absent from the corpus at all,
(b) present but not retrieved, or (c) retrieved yet still mishandled.

The lexical evidence layer is deterministic (IDF scoring, entity boosts, no
API), so the evidence pack the arbiter saw can be reconstructed offline and
exactly for every statement.  Query construction, k=4, boost weights and the
3,500-char budget are copied verbatim from scripts/run_baselines.py
(``run_probiopsy_rag``) so the reconstruction matches the benchmark.

Outputs:
  outputs/failure_decomposition.json          summary + per-run strata
  outputs/figures/source_data/failure_decomposition_runs.csv  per-run rows
"""
from __future__ import annotations

import csv
import io
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from probiopsy_rag_agent.evidence_store import EvidenceStore  # noqa: E402

GOLD_PATH = ROOT / "data" / "seed" / "probiopsy_statements.csv"
CHUNKS_PATH = ROOT / "data" / "seed" / "evidence_chunks.jsonl"
PRED_PATH = ROOT / "outputs" / "baseline_predictions.jsonl"
OUT_JSON = ROOT / "outputs" / "failure_decomposition.json"
OUT_CSV = ROOT / "outputs" / "figures" / "source_data" / "failure_decomposition_runs.csv"

Q_RE = re.compile(r"\bQ\d+\b")


def build_question(row: dict) -> str:
    """Verbatim copy of run_baselines.build_question (drives retrieval)."""
    flags = (row.get("scenario_flags") or "").replace("|", ", ")
    return (
        "Prostate-biopsy decision under evaluation.\n"
        f"Consensus statement: \"{row['statement_text_en']}\"\n"
        f"Stem: {row['stem_name']}. Decision item id: {row['decision_item_id']}.\n"
        f"Patient scenario flags: {flags or '(unspecified)'}.\n"
        "Which action should a guideline-faithful decision-support system take?\n"
        "End your answer with exactly one line: FINAL ACTION: <class> where <class> is one of "
        "endorse, endorse_option, conditional, report_option, against."
    )


def main() -> int:
    rows = list(csv.DictReader(GOLD_PATH.open(encoding="utf-8-sig")))
    store = EvidenceStore(CHUNKS_PATH)

    # --- corpus-level linkage ------------------------------------------------
    q_to_corpus_chunks: dict[str, set[str]] = defaultdict(set)
    for c in store.chunks:
        for qid in Q_RE.findall(c.text + " " + c.source_locator):
            q_to_corpus_chunks[qid].add(c.chunk_id)

    per_stmt: dict[str, dict] = {}
    for row in rows:
        sid = row["statement_id"]
        did = (row.get("decision_item_id") or "").strip()
        flags = [f for f in (row.get("scenario_flags") or "").split("|") if f]
        corpus_item = {c.chunk_id for c in store.chunks if did and did in c.entities_b}
        corpus_q = set(q_to_corpus_chunks.get(sid, set()))

        question = build_question(row)
        hits = store.retrieve(question, k=4, boost_entities_b=[did] if did else [],
                              boost_entities_a=flags)
        pack_ids = [h.chunk.chunk_id for h in hits]
        pack_item = [cid for cid in pack_ids if cid in corpus_item]
        pack_q = [cid for cid in pack_ids if cid in corpus_q]

        per_stmt[sid] = {
            "decision_item_id": did,
            "domain": row.get("domain", ""),
            "corpus_item_chunks": len(corpus_item),
            "corpus_q_chunks": len(corpus_q),
            "pack_ids": pack_ids,
            "pack_item_chunks": pack_item,
            "pack_q_chunks": pack_q,
        }

    # --- join with benchmark predictions ------------------------------------
    runs = []
    for line in io.open(PRED_PATH, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        if r["method"] != "probiopsy-rag":
            continue
        sid = r["statement_id"]
        s = per_stmt[sid]
        if not s["decision_item_id"]:
            stratum = "no_decision_item"
        elif s["corpus_item_chunks"] == 0:
            stratum = "corpus_gap"
        elif not s["pack_item_chunks"]:
            stratum = "retrieval_miss"
        else:
            stratum = "arbitration_error" if r["gold_action"] != r["pred_action"] else "correct_with_evidence"
        runs.append({
            "seed": r["seed"],
            "statement_id": sid,
            "domain": s["domain"],
            "gold_action": r["gold_action"],
            "pred_action": r["pred_action"],
            "correct": r["gold_action"] == r["pred_action"],
            "stratum": stratum,
            "logged_chunks": r.get("chunks_retrieved"),
            "reconstructed_lex_chunks": len(s["pack_ids"]),
            "pack_has_item_evidence": bool(s["pack_item_chunks"]),
            "pack_has_gold_q_chunk": bool(s["pack_q_chunks"]),
        })

    wrong = [r for r in runs if not r["correct"]]
    strata = Counter(r["stratum"] for r in wrong)
    strata_stmts = {st: sorted({r["statement_id"] for r in wrong if r["stratum"] == st})
                    for st in ("corpus_gap", "retrieval_miss", "arbitration_error", "no_decision_item")}
    by_transition = defaultdict(Counter)
    for r in wrong:
        by_transition[f"{r['gold_action']}->{r['pred_action']}"][r["stratum"]] += 1
    by_domain = defaultdict(Counter)
    for r in wrong:
        by_domain[r["domain"]][r["stratum"]] += 1

    # conditional accuracy over all 560 runs
    cov = sum(1 for r in runs if r["pack_has_item_evidence"])
    acc_given = sum(1 for r in runs if r["pack_has_item_evidence"] and r["correct"]) / max(cov, 1)
    nocov = len(runs) - cov
    acc_missing = sum(1 for r in runs if not r["pack_has_item_evidence"] and r["correct"]) / max(nocov, 1)
    qcov = sum(1 for r in runs if r["pack_has_gold_q_chunk"])
    acc_q = sum(1 for r in runs if r["pack_has_gold_q_chunk"] and r["correct"]) / max(qcov, 1)

    # reconstruction fidelity: logged chunk count vs lexical reconstruction
    # (logged = lexical hits + 1 when the graph context was non-empty)
    diffs = Counter()
    for r in runs:
        d = (r["logged_chunks"] or 0) - r["reconstructed_lex_chunks"]
        diffs[d] += 1

    summary = {
        "n_full_system_runs": len(runs),
        "n_misclassified_runs": len(wrong),
        "misclassified_by_stratum": dict(strata),
        "misclassified_statements_by_stratum": strata_stmts,
        "misclassified_by_transition_and_stratum": {k: dict(v) for k, v in by_transition.items()},
        "misclassified_by_domain_and_stratum": {k: dict(v) for k, v in by_domain.items()},
        "runs_with_item_evidence_in_pack": cov,
        "item_evidence_coverage_rate": round(cov / len(runs), 4),
        "arbitration_accuracy_given_item_evidence": round(acc_given, 4),
        "arbitration_accuracy_given_item_evidence_missing": round(acc_missing, 4),
        "runs_with_gold_q_chunk_in_pack": qcov,
        "arbitration_accuracy_given_gold_q_chunk": round(acc_q, 4),
        "corpus_statements_without_item_linked_chunks":
            sorted(sid for sid, s in per_stmt.items() if s["corpus_item_chunks"] == 0),
        "corpus_statements_without_any_q_mention_chunk":
            sorted(sid for sid, s in per_stmt.items() if s["corpus_q_chunks"] == 0),
        "reconstruction_logged_minus_lexical_distribution": {str(k): v for k, v in sorted(diffs.items())},
    }

    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(runs[0].keys()))
        w.writeheader()
        w.writerows(runs)

    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
