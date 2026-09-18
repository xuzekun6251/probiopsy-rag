"""Run the 4-method × 5-seed statement-fidelity benchmark (PLAN.md §5).

Each of the 112 ProBIOPSY gold statements becomes one test item: the system
must output one of 5 action classes (endorse / endorse_option / conditional /
report_option / against) matching ``expected_system_action``.

Methods:
  pure_llm      — chat LLM only, no retrieval
  naive_rag     — lexical top-k retrieval + chat LLM
  lightrag      — LightRAG dual-level (hybrid) query + LLM, no rules
  probiopsy-rag — rule engine hard constraints + LightRAG graph context
                  (embedding-only) + SafetyAgent arbiter

Output: outputs/baseline_predictions.jsonl (append-safe, resumable by
(method, seed, statement_id)).

Usage:
    .venv/Scripts/python.exe scripts/run_baselines.py [--methods pure_llm,...] [--seeds 5]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import io
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from probiopsy_rag_agent.evidence_store import EvidenceStore          # noqa: E402
from probiopsy_rag_agent.lightrag_adapter import LightRAGAdapter      # noqa: E402
from probiopsy_rag_agent.llm_client import LLMClient                  # noqa: E402
from probiopsy_rag_agent.naive_rag import naive_rag_answer            # noqa: E402
from probiopsy_rag_agent.risk_rules import (                          # noqa: E402
    load_decision_items, load_patient_factor_rules, load_rules,
    match_patient_factors, match_rules,
)
from probiopsy_rag_agent.safety_agent import ACTION_CLASSES, SafetyAgent  # noqa: E402

PRED_PATH = ROOT / "outputs" / "baseline_predictions.jsonl"
GOLD_PATH = ROOT / "data" / "seed" / "probiopsy_statements.csv"
RULES_PATH = ROOT / "configs" / "rules.yaml"
ITEMS_PATH = ROOT / "data" / "seed" / "entities_b.csv"
CHUNKS_PATH = ROOT / "data" / "seed" / "evidence_chunks.jsonl"
INDEX_DIR = ROOT / "data" / "processed" / "lightrag_index"

_FINAL_RE = re.compile(r"FINAL\s+ACTION\s*[:\-]\s*([a-z_]+)", re.I)

_print_lock = threading.Lock()


def log(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def load_env() -> None:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())


# worker-thread-local LightRAG adapters: the adapter serializes all queries
# through ONE event-loop queue, so sharing one instance across worker threads
# caps the lightrag/probiopsy methods at single-threaded speed. Independent
# per-worker instances (LLM cache disabled) run fully parallel.
_ADAPTERS: dict[int, "LightRAGAdapter"] = {}
_ADAPTERS_LOCK = threading.Lock()


def get_lightrag(ctx) -> "LightRAGAdapter":
    key = threading.get_ident()
    with _ADAPTERS_LOCK:
        live = {t.ident for t in threading.enumerate()}
        for dead in [k for k in _ADAPTERS if k not in live]:
            _ADAPTERS.pop(dead, None)  # released pool thread; GC takes the index
        ad = _ADAPTERS.get(key)
        if ad is None:
            ad = ctx["lightrag_factory"]()
            _ADAPTERS[key] = ad
        return ad


def build_question(row: dict) -> str:
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


def parse_final_action(text: str) -> str:
    m = _FINAL_RE.search(text or "")
    if m and m.group(1) in ACTION_CLASSES:
        return m.group(1)
    # keyword fallback
    low = (text or "").lower()
    if "recommend against" in low or ("against" in low and "recommend" in low):
        return "against"
    if "endorse" in low:
        return "endorse"
    if "conditional" in low or "neither" in low:
        return "conditional"
    return "report_option"


# --------------------------------------------------------------------------- #
# method runners (each returns (pred_action, context_chars, chunks, meta))
# --------------------------------------------------------------------------- #

def run_pure_llm(row, question, ctx) -> tuple:
    client: LLMClient = ctx["client"]
    resp = client.complete(
        prompt=question,
        system=(
            "You are a clinical decision-support assistant for prostate biopsy. "
            "Answer from your own knowledge. End with 'FINAL ACTION: <class>' "
            "(endorse / endorse_option / conditional / report_option / against)."
        ),
    )
    text = "" if getattr(resp, "degraded", False) else resp.text
    return parse_final_action(text), 0, 0, {}


def run_naive_rag(row, question, ctx) -> tuple:
    store: EvidenceStore = ctx["store"]
    client: LLMClient = ctx["client"]
    ans, ctx_chars = naive_rag_answer(question, store, client, k=6)
    return parse_final_action(ans), ctx_chars, 6, {}


def run_lightrag(row, question, ctx) -> tuple:
    adapter: LightRAGAdapter = get_lightrag(ctx)
    # aquery returns None if the query-gen content came back null (observed
    # once on a cold process: GLM thinking exhausted the content budget and
    # LightRAG's role wrapper propagated None) — normalize to "" so the
    # degraded check below handles it.
    answer = adapter.query(question, mode="hybrid") or ""
    if answer.startswith("[llm error]") or not answer.strip():
        return "report_option", len(answer), 0, {"degraded": True}
    client: LLMClient = ctx["client"]
    resp = client.complete(
        prompt=(
            "Decision-support answer:\n"
            f"{answer[:4000]}\n\n"
            "Which action class does this answer support? End with exactly one line: "
            "FINAL ACTION: <class> (endorse / endorse_option / conditional / "
            "report_option / against)."
        ),
        system="You classify decision-support answers into action classes.",
    )
    text = "" if getattr(resp, "degraded", False) else resp.text
    return parse_final_action(text), len(answer), 0, {}


def run_probiopsy_rag(row, question, ctx) -> tuple:
    agent: SafetyAgent = ctx["agent"]
    adapter: LightRAGAdapter = get_lightrag(ctx)
    rules = ctx["rules"]
    items = ctx["items"]
    pfrs = ctx["pfrs"]
    store: EvidenceStore = ctx["store"]

    flags = [f for f in (row.get("scenario_flags") or "").split("|") if f]
    decision_items = {row["decision_item_id"]} if row.get("decision_item_id") else set()
    matches = match_rules(rules, set(flags), decision_items, items)
    matches += match_patient_factors(pfrs, set(flags), decision_items, items)

    # graph-aware evidence (embedding-only retrieval, no LLM generation)
    try:
        graph_ctx = adapter.query(question, mode="hybrid", only_need_context=True) or ""
    except Exception as e:
        graph_ctx = f"(graph retrieval failed: {e})"
    # lexical statement evidence with entity boosts
    hits = store.retrieve(question, k=4, boost_entities_b=decision_items, boost_entities_a=flags)
    lex_ctx = store.pack_context(hits, char_budget=3500)
    evidence = (graph_ctx[:5500] + "\n\n--- lexical evidence ---\n\n" + lex_ctx) if graph_ctx.strip() else lex_ctx

    verdict = agent.decide(question, flags, matches, evidence)
    n_chunks = len(hits) + (1 if graph_ctx.strip() else 0)
    return verdict["action"], len(evidence), n_chunks, {"rules": [m.rule.rule_id for m in matches]}


RUNNERS = {
    "pure_llm": run_pure_llm,
    "naive_rag": run_naive_rag,
    "lightrag": run_lightrag,
    "probiopsy-rag": run_probiopsy_rag,
}


# --------------------------------------------------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--methods", default="pure_llm,naive_rag,lightrag,probiopsy-rag")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--limit", type=int, default=0, help="only first N statements (smoke)")
    args = ap.parse_args()

    load_env()
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    for m in methods:
        if m not in RUNNERS:
            print(f"[run] unknown method {m}")
            return 1

    gold_rows = list(csv.DictReader(GOLD_PATH.open(encoding="utf-8-sig")))
    if args.limit:
        gold_rows = gold_rows[: args.limit]
    log(f"[run] {len(gold_rows)} gold statements x {len(methods)} methods x {args.seeds} seeds")

    done_keys: set[tuple] = set()
    if PRED_PATH.exists():
        for line in PRED_PATH.open(encoding="utf-8"):
            try:
                r = json.loads(line)
                done_keys.add((r["method"], int(r.get("seed", 0)), r["statement_id"]))
            except Exception:
                pass
    log(f"[run] resume: {len(done_keys)} predictions already present")

    pred_fh = PRED_PATH.open("a", encoding="utf-8")
    write_lock = threading.Lock()

    # shared context pieces
    store = EvidenceStore(CHUNKS_PATH) if {"naive_rag", "probiopsy-rag"} & set(methods) else None
    rules = load_rules(RULES_PATH) if "probiopsy-rag" in methods else None
    items = load_decision_items(ITEMS_PATH) if "probiopsy-rag" in methods else None
    pfrs = load_patient_factor_rules(RULES_PATH) if "probiopsy-rag" in methods else None

    for method in methods:
        for seed in range(args.seeds):
            todo = [r for r in gold_rows if (method, seed, r["statement_id"]) not in done_keys]
            if not todo:
                log(f"[run] {method} seed {seed}: complete, skipping")
                continue
            # per-seed client: temperature>0 for stochasticity across seeds
            client = LLMClient(provider="deepseek", temperature=args.temperature)
            ctx: dict = {"client": client}
            if method in ("lightrag", "probiopsy-rag"):
                # factory; adapters are built per worker thread (get_lightrag)
                ctx["lightrag_factory"] = lambda: LightRAGAdapter(
                    working_dir=str(INDEX_DIR), enable_llm_cache=False
                )
            if method == "probiopsy-rag":
                ctx["agent"] = SafetyAgent(client=LLMClient(provider="deepseek", temperature=0.0))
                ctx["rules"], ctx["items"], ctx["pfrs"] = rules, items, pfrs
            if method in ("naive_rag", "probiopsy-rag"):
                ctx["store"] = store

            t0 = time.time()
            n_ok = 0
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                futs = {pool.submit(RUNNERS[method], row, build_question(row), ctx): row
                        for row in todo}
                for fut in as_completed(futs):
                    row = futs[fut]
                    try:
                        pred, ctx_chars, chunks, meta = fut.result()
                    except Exception as e:
                        pred, ctx_chars, chunks, meta = "report_option", 0, 0, {"error": str(e)[:150]}
                    rec = {
                        "method": method, "seed": seed,
                        "statement_id": row["statement_id"],
                        "gold_action": row["expected_system_action"],
                        "pred_action": pred,
                        "context_chars": ctx_chars, "chunks_retrieved": chunks,
                        "meta": meta,
                    }
                    with write_lock:
                        pred_fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        pred_fh.flush()
                    done_keys.add((method, seed, row["statement_id"]))
                    n_ok += 1
                    if n_ok % 10 == 0:
                        log(f"[run] {method} seed {seed}: {n_ok}/{len(todo)} "
                            f"({time.time() - t0:.0f}s)")
            log(f"[run] {method} seed {seed}: DONE {len(todo)} items in {time.time() - t0:.0f}s")

    pred_fh.close()
    log(f"[run] all done -> {PRED_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
