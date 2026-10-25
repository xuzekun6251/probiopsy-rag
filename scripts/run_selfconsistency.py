"""Self-consistency variant of the full-system arbiter (ablation for the paper).

Identical to the benchmark's ``probiopsy-rag`` method (run_baselines.py) in
every component — same question, same rule matches, same graph + lexical
evidence composition, same arbiter prompt contract — except the arbiter call:
instead of ONE completion at temperature 0.0, k completions are sampled at
temperature >0 and the final action is the plurality vote (ties: highest mean
confidence, then ACTION_CLASSES order; degraded samples count as their
fallback class, mirroring decide()'s report_option fallback).

Everything is logged per statement (all k raw votes) so the vote is auditable
and re-votable post hoc (bootstrap over votes without new API calls).

Output: outputs/selfconsistency_predictions.jsonl — append-safe, resumable by
(replication, statement_id).

Usage:
    .venv/Scripts/python.exe scripts/run_selfconsistency.py [--k 5]
        [--temperature 0.7] [--workers 4] [--limit N] [--replication sc1]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import io
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
# NB: no stdout re-wrap here — run_baselines' import already wraps it once;
# wrapping twice closes the underlying buffer when the first wrapper is GC'd.

# reuse the benchmark harness verbatim: question construction, rule matching,
# evidence composition, worker-thread-local LightRAG adapters
from run_baselines import (                                        # noqa: E402
    build_question, get_lightrag, load_env, log,
    CHUNKS_PATH, GOLD_PATH, INDEX_DIR, ITEMS_PATH, RULES_PATH,
)
from probiopsy_rag_agent.evidence_store import EvidenceStore       # noqa: E402
from probiopsy_rag_agent.lightrag_adapter import LightRAGAdapter   # noqa: E402
from probiopsy_rag_agent.llm_client import LLMClient               # noqa: E402
from probiopsy_rag_agent.risk_rules import (                       # noqa: E402
    load_decision_items, load_patient_factor_rules, load_rules,
    match_patient_factors, match_rules,
)
from probiopsy_rag_agent.safety_agent import (                     # noqa: E402
    ACTION_CLASSES, _constraints_block, _parse_json, _PROMPT, _SYSTEM,
)

PRED_PATH = ROOT / "outputs" / "selfconsistency_predictions.jsonl"

_print_lock = threading.Lock()


def log_sc(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def sample_votes(client: LLMClient, prompt: str, k: int) -> list[dict]:
    """Sample k arbiter completions and parse each into a vote record.

    Mirrors SafetyAgent.decide()'s robustness contract: one retry on
    degraded/invalid output, then the report_option fallback.
    """
    votes: list[dict] = []
    for _ in range(k):
        action, conf, rat, cites, degraded, err = None, 0.0, "", [], False, ""
        for attempt in range(2):
            resp = client.complete(prompt=prompt, system=_SYSTEM)
            if getattr(resp, "degraded", False):
                err = resp.text[:150]
                continue
            parsed = _parse_json(resp.text)
            if parsed and parsed.get("action") in ACTION_CLASSES:
                action = parsed["action"]
                try:
                    conf = float(parsed.get("confidence", 0.0))
                except (TypeError, ValueError):
                    conf = 0.0
                rat = str(parsed.get("rationale", ""))[:400]
                cites = list(parsed.get("citations") or [])[:8]
                break
            err = resp.text[:150]
        if action is None:
            action, conf, degraded = "report_option", 0.0, True
        votes.append({"action": action, "confidence": round(conf, 3),
                      "rationale": rat, "citations": cites,
                      "degraded": degraded, "error": err if degraded else ""})
    return votes


def plurality_vote(votes: list[dict]) -> tuple[str, dict]:
    """Plurality with documented deterministic tie-breaks."""
    dist = Counter(v["action"] for v in votes)
    top = max(dist.values())
    tied = [c for c, n in dist.items() if n == top]
    if len(tied) == 1:
        return tied[0], dict(dist)
    # tie-break 1: highest mean confidence among tied classes
    means: dict[str, float] = {}
    for c in tied:
        confs = [v["confidence"] for v in votes if v["action"] == c]
        means[c] = sum(confs) / len(confs)
    best = max(means.values())
    tied = sorted(c for c, m in means.items() if m == best)
    if len(tied) == 1:
        return tied[0], dict(dist)
    # tie-break 2: fixed ACTION_CLASSES order (endorse first)
    for c in ACTION_CLASSES:
        if c in tied:
            return c, dict(dist)
    return tied[0], dict(dist)  # unreachable


def run_statement(row: dict, ctx: dict) -> dict:
    adapter: LightRAGAdapter = get_lightrag(ctx)
    store: EvidenceStore = ctx["store"]

    flags = [f for f in (row.get("scenario_flags") or "").split("|") if f]
    decision_items = {row["decision_item_id"]} if row.get("decision_item_id") else set()
    matches = match_rules(ctx["rules"], set(flags), decision_items, ctx["items"])
    matches += match_patient_factors(ctx["pfrs"], set(flags), decision_items, ctx["items"])

    question = build_question(row)
    try:
        graph_ctx = adapter.query(question, mode="hybrid", only_need_context=True) or ""
    except Exception as e:
        graph_ctx = f"(graph retrieval failed: {e})"
    hits = store.retrieve(question, k=4, boost_entities_b=decision_items, boost_entities_a=flags)
    lex_ctx = store.pack_context(hits, char_budget=3500)
    evidence = (graph_ctx[:5500] + "\n\n--- lexical evidence ---\n\n" + lex_ctx) if graph_ctx.strip() else lex_ctx

    constraints, _ = _constraints_block(matches)
    prompt = _PROMPT.format(
        question=question,
        patient_flags=", ".join(sorted(flags)) or "(none)",
        constraints=constraints,
        no_constraints="" if matches else "",
        evidence=evidence[:8000] or "(no evidence retrieved)",
    )

    votes = sample_votes(ctx["client"], prompt, ctx["k"])
    final, dist = plurality_vote(votes)
    return {
        "method": "probiopsy-rag-sc",
        "replication": ctx["replication"],
        "k": ctx["k"], "temperature": ctx["temperature"],
        "statement_id": row["statement_id"],
        "gold_action": row["expected_system_action"],
        "votes": votes,
        "vote_distribution": dist,
        "pred_action": final,
        "context_chars": len(evidence),
        "chunks_retrieved": len(hits) + (1 if graph_ctx.strip() else 0),
        "rules": [m.rule.rule_id for m in matches],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0, help="only first N statements (smoke)")
    ap.add_argument("--replication", default="sc1")
    args = ap.parse_args()

    load_env()
    gold_rows = list(csv.DictReader(GOLD_PATH.open(encoding="utf-8-sig")))
    if args.limit:
        gold_rows = gold_rows[: args.limit]
    log_sc(f"[sc] {len(gold_rows)} statements x k={args.k} samples "
           f"at T={args.temperature} (replication {args.replication})")

    done_keys: set[tuple] = set()
    if PRED_PATH.exists():
        for line in PRED_PATH.open(encoding="utf-8"):
            try:
                r = json.loads(line)
                done_keys.add((r["replication"], r["statement_id"]))
            except Exception:
                pass
    log_sc(f"[sc] resume: {len(done_keys)} statements already complete")

    todo = [r for r in gold_rows if (args.replication, r["statement_id"]) not in done_keys]
    log_sc(f"[sc] todo: {len(todo)} statements = {len(todo) * args.k} arbiter calls")

    client = LLMClient(provider="deepseek", temperature=args.temperature)
    if client.degraded:
        log_sc("[sc] FATAL: no LLM key configured")
        return 1
    ctx: dict = {
        "client": client, "k": args.k, "temperature": args.temperature,
        "replication": args.replication,
        "store": EvidenceStore(CHUNKS_PATH),
        "rules": load_rules(RULES_PATH),
        "items": load_decision_items(ITEMS_PATH),
        "pfrs": load_patient_factor_rules(RULES_PATH),
        "lightrag_factory": lambda: LightRAGAdapter(
            working_dir=str(INDEX_DIR), enable_llm_cache=False
        ),
    }

    pred_fh = PRED_PATH.open("a", encoding="utf-8")
    write_lock = threading.Lock()
    t0 = time.time()
    n_ok = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(run_statement, row, ctx): row for row in todo}
        for fut in as_completed(futs):
            row = futs[fut]
            try:
                rec = fut.result()
            except Exception as e:
                # whole-statement failure: record a fully degraded replication
                rec = {
                    "method": "probiopsy-rag-sc", "replication": args.replication,
                    "k": args.k, "temperature": args.temperature,
                    "statement_id": row["statement_id"],
                    "gold_action": row["expected_system_action"],
                    "votes": [{"action": "report_option", "confidence": 0.0,
                               "rationale": f"statement-level error: {e}"[:200],
                               "citations": [], "degraded": True, "error": str(e)[:200]}
                              for _ in range(args.k)],
                    "vote_distribution": {"report_option": args.k},
                    "pred_action": "report_option",
                    "context_chars": 0, "chunks_retrieved": 0, "rules": [],
                }
            with write_lock:
                pred_fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                pred_fh.flush()
            n_ok += 1
            if n_ok % 5 == 0 or n_ok == len(todo):
                log_sc(f"[sc] {n_ok}/{len(todo)} statements "
                       f"({(time.time() - t0) / 60:.1f} min)")
    pred_fh.close()
    log_sc(f"[sc] DONE {len(todo)} statements in {(time.time() - t0) / 60:.1f} min -> {PRED_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
