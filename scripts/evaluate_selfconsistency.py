"""Score the self-consistency ablation against the k=1 full-system benchmark.

Comparisons produced (all on the same 112-statement gold standard):
  1. k=1 full system (5 seeds, T=0 arbiter)        — from baseline_predictions.jsonl
  2. k=1 across-seed plurality vote (5 seeds voted) — cost-free ensemble of (1)
  3. k=5 self-consistency (T=0.7, plurality vote)   — from selfconsistency_predictions.jsonl

Uncertainty for (3): statement bootstrap (resample 112 statements) and vote
bootstrap (resample the k votes per statement and re-vote) — both capture a
distinct instability source without new API calls.

Usage:
    .venv/Scripts/python.exe scripts/evaluate_selfconsistency.py
"""
from __future__ import annotations

import json
import random
import sys
import io
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
# NB: no stdout re-wrap — evaluate.py's import does it once (double-wrap closes
# the underlying buffer when the first wrapper is GC'd).

from evaluate import ACTIONS, COLLAPSE, binary_metrics, kappa, macro_f1  # noqa: E402

BASE_PATH = ROOT / "outputs" / "baseline_predictions.jsonl"
SC_PATH = ROOT / "outputs" / "selfconsistency_predictions.jsonl"
OUT_PATH = ROOT / "outputs" / "selfconsistency_summary.json"
N_BOOT = 2000


def metrics(preds: list[str], golds: list[str]) -> dict:
    bm = binary_metrics(preds, golds)
    recall = {}
    for c in ACTIONS:
        n_c = sum(1 for g in golds if g == c)
        recall[c] = sum(1 for p, g in zip(preds, golds) if p == c and g == c) / n_c if n_c else 0.0
    return {
        "n": len(preds),
        "exact5": sum(p == g for p, g in zip(preds, golds)) / len(preds),
        "exact3": sum(COLLAPSE[p] == COLLAPSE[g] for p, g in zip(preds, golds)) / len(preds),
        "macro_f1": macro_f1(preds, golds),
        "kappa": kappa(preds, golds),
        "against_sensitivity": bm["sensitivity"],
        "against_specificity": bm["specificity"],
        "against_f1": bm["f1"],
        "class_recall": recall,
        "pred_distribution": dict(Counter(preds)),
    }


def plurality(votes: list[str]) -> str:
    dist = Counter(votes)
    top = max(dist.values())
    tied = [c for c in ACTIONS if dist.get(c, 0) == top]
    return tied[0]  # ACTION_CLASSES order tie-break (no confidence in k=1 rows)


def boot(vals: list[float]) -> dict:
    vals = sorted(vals)
    return {"mean": sum(vals) / len(vals),
            "sd": (sum((v - vals[len(vals)//2]) ** 2 for v in vals) / max(len(vals)-1, 1)) ** 0.5,
            "ci95": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]]}


def main() -> int:
    rng = random.Random(20261023)

    base_rows = [json.loads(l) for l in BASE_PATH.open(encoding="utf-8")
                 if l.strip() and json.loads(l)["method"] == "probiopsy-rag"]
    by_seed: dict[int, dict[str, str]] = defaultdict(dict)
    for r in base_rows:
        by_seed[int(r["seed"])][r["statement_id"]] = r["pred_action"]
    golds = {r["statement_id"]: r["gold_action"] for r in base_rows}
    sids = sorted(golds)

    k1_seed_metrics = []
    for seed in sorted(by_seed):
        preds = [by_seed[seed][s] for s in sids]
        m = metrics(preds, [golds[s] for s in sids])
        m["seed"] = seed
        k1_seed_metrics.append(m)
    k1_agg = {k: {"mean": round(sum(m[k] for m in k1_seed_metrics) / len(k1_seed_metrics), 4),
                  "sd": round((sum((m[k] - sum(x[k] for x in k1_seed_metrics) / len(k1_seed_metrics)) ** 2
                                   for m in k1_seed_metrics) / (len(k1_seed_metrics) - 1)) ** 0.5, 4)}
              for k in ("exact5", "exact3", "macro_f1", "kappa", "against_sensitivity",
                        "against_specificity", "against_f1")}

    # (2) across-seed plurality of the 5 k=1 seeds
    k1_voted_preds = [plurality([by_seed[seed][s] for seed in sorted(by_seed)]) for s in sids]
    k1_voted = metrics(k1_voted_preds, [golds[s] for s in sids])

    # (3) self-consistency
    sc_rows = [json.loads(l) for l in SC_PATH.open(encoding="utf-8") if l.strip()]
    sc_golds = {r["statement_id"]: r["gold_action"] for r in sc_rows}
    assert sc_golds == golds, "gold mismatch between baseline and self-consistency files"
    sc_votes = {r["statement_id"]: [v["action"] for v in r["votes"]] for r in sc_rows}
    sc_final = {r["statement_id"]: r["pred_action"] for r in sc_rows}
    sc = metrics([sc_final[s] for s in sids], [golds[s] for s in sids])

    # degraded-vote census
    n_votes = sum(len(v) for v in sc_votes.values())
    n_degraded = sum(1 for r in sc_rows for v in r["votes"] if v.get("degraded"))
    n_unanimous = sum(1 for v in sc_votes.values() if len(set(v)) == 1)

    # statement bootstrap over the observed SC vote
    sb = {k: [] for k in ("exact5", "kappa", "macro_f1", "cond_recall", "against_sens")}
    for _ in range(N_BOOT):
        sample = [sids[rng.randrange(len(sids))] for _ in sids]
        preds = [sc_final[s] for s in sample]
        g = [golds[s] for s in sample]
        sb["exact5"].append(metrics(preds, g)["exact5"])
        sb["kappa"].append(kappa(preds, g))
        sb["macro_f1"].append(macro_f1(preds, g))
        sb["cond_recall"].append(metrics(preds, g)["class_recall"]["conditional"])
        sb["against_sens"].append(binary_metrics(preds, g)["sensitivity"])
    sc_statement_boot = {k: boot(v) for k, v in sb.items()}

    # vote bootstrap: resample the k votes per statement, re-vote
    vb = {k: [] for k in ("exact5", "cond_recall", "against_sens")}
    k_votes = len(next(iter(sc_votes.values())))
    for _ in range(N_BOOT):
        preds = []
        for s in sids:
            votes = sc_votes[s]
            resample = [votes[rng.randrange(k_votes)] for _ in range(k_votes)]
            preds.append(plurality(resample))
        g = [golds[s] for s in sids]
        vb["exact5"].append(metrics(preds, g)["exact5"])
        vb["cond_recall"].append(metrics(preds, g)["class_recall"]["conditional"])
        vb["against_sens"].append(binary_metrics(preds, g)["sensitivity"])
    sc_vote_boot = {k: boot(v) for k, v in vb.items()}

    out = {
        "n_statements": len(sids),
        "k1_per_seed": k1_seed_metrics,
        "k1_aggregate": k1_agg,
        "k1_across_seed_plurality": k1_voted,
        "selfconsistency": sc,
        "selfconsistency_statement_bootstrap": sc_statement_boot,
        "selfconsistency_vote_bootstrap": sc_vote_boot,
        "vote_census": {"n_votes": n_votes, "n_degraded": n_degraded,
                        "n_unanimous_statements": n_unanimous,
                        "n_statements": len(sc_rows)},
    }
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    def row(label, m):
        print(f"{label:<34}{m['exact5']:>8.3f}{m['macro_f1']:>8.3f}{m['kappa']:>8.3f}"
              f"{m['class_recall']['conditional']:>10.3f}{m['against_sensitivity']:>10.3f}"
              f"{m['against_specificity']:>10.3f}")

    print(f"\n{'method':<34}{'exact5':>8}{'macF1':>8}{'kappa':>8}{'condRec':>10}{'againstSens':>12}{'againstSpec':>12}")
    row("k=1 full system (5 seeds)", {**k1_voted, "exact5": k1_agg["exact5"]["mean"],
        "macro_f1": k1_agg["macro_f1"]["mean"], "kappa": k1_agg["kappa"]["mean"],
        "against_sensitivity": k1_agg["against_sensitivity"]["mean"],
        "against_specificity": k1_agg["against_specificity"]["mean"],
        "class_recall": k1_seed_metrics[0]["class_recall"]})  # recall shown is seed 0; see json
    row("k=1 x5 seeds, plurality vote", k1_voted)
    row(f"k=5 self-consistency (sc)", sc)
    print(f"\nstatement bootstrap exact5: {sc_statement_boot['exact5']['mean']:.3f} "
          f"CI95 [{sc_statement_boot['exact5']['ci95'][0]:.3f}, {sc_statement_boot['exact5']['ci95'][1]:.3f}]")
    print(f"vote bootstrap exact5:      {sc_vote_boot['exact5']['mean']:.3f} "
          f"CI95 [{sc_vote_boot['exact5']['ci95'][0]:.3f}, {sc_vote_boot['exact5']['ci95'][1]:.3f}]")
    print(f"vote bootstrap cond recall: {sc_vote_boot['cond_recall']['mean']:.3f} "
          f"CI95 [{sc_vote_boot['cond_recall']['ci95'][0]:.3f}, {sc_vote_boot['cond_recall']['ci95'][1]:.3f}]")
    print(f"degraded votes: {n_degraded}/{n_votes}; unanimous statements: {n_unanimous}/{len(sc_rows)}")
    print(f"\n-> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
