# -*- coding: utf-8 -*-
"""Pre-submission internal-review statistics (peer-review simulation support).

Computes, from real artifacts only:
1. Paired t-tests across seeds (n=5) for probiopsy-rag vs each baseline on
   exact-5 accuracy and Cohen's kappa, with Benjamini-Hochberg FDR correction
   (the figure contract's multiple-testing mitigation).
2. Full-system aggregated 5x5 confusion matrix (with zero cells filled),
   from baseline_predictions.jsonl (flash benchmark only).
3. Per-domain confusion matrices for the full system.
4. figure2_pred_distribution.csv source data for Figure 2 panel (c).

Writes outputs/tables/internal_review_stats.json and the panel-C CSV.
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
ACTIONS = ["endorse", "endorse_option", "conditional", "report_option", "against"]

summary = json.loads((OUT / "evaluation_summary.json").read_text(encoding="utf-8"))
glm53 = json.loads(
    (OUT / "evaluation_summary_glm53_baselines.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- 1. paired tests
def seed_vals(method: str, metric: str) -> list[float]:
    return [s[metric] for s in summary["methods"][method]["seeds"]]

FULL = "probiopsy-rag"
raw_tests = []
for baseline in ["lightrag", "naive_rag", "pure_llm"]:
    for metric in ["exact5", "kappa"]:
        a, b = seed_vals(FULL, metric), seed_vals(baseline, metric)
        t, p = stats.ttest_rel(a, b)
        raw_tests.append({
            "comparison": f"{FULL} vs {baseline}",
            "metric": metric,
            "t_stat": round(float(t), 3),
            "p_raw": float(p),
        })

# Benjamini-Hochberg FDR
m = len(raw_tests)
order = sorted(range(m), key=lambda i: raw_tests[i]["p_raw"])
adj = [0.0] * m
prev = 1.0
for rank, i in enumerate(reversed(order), start=1):
    idx = order[m - rank]
    prev = min(prev, raw_tests[idx]["p_raw"] * m / (m - rank + 1))
    adj[idx] = prev
for i, t_ in enumerate(raw_tests):
    t_["p_bh_fdr"] = round(adj[i], 6)

# ------------------------------------------------- 2/3. confusion matrices (flash, full system)
dom_by_stmt = {}
with open(ROOT / "data" / "seed" / "probiopsy_statements.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        dom_by_stmt[row["statement_id"]] = row["domain"]

overall = Counter()
per_dom = defaultdict(Counter)
n_flash_full = 0
with open(OUT / "baseline_predictions.jsonl", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        if r["method"] != FULL:
            continue
        n_flash_full += 1
        g, p = r["gold_action"], r["pred_action"]
        overall[(g, p)] += 1
        per_dom[dom_by_stmt.get(r["statement_id"], "?")][(g, p)] += 1

def matrix(counter: Counter) -> dict:
    return {g: {p: counter.get((g, p), 0) for p in ACTIONS} for g in ACTIONS}

cond_recall = matrix(overall)["conditional"]["conditional"] / 185.0

# ------------------------------------------------- 4. panel C source data
panel_c_path = OUT / "figures" / "source_data" / "figure2_pred_distribution.csv"
with open(panel_c_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["action", "gold_standard", "pure_llm", "naive_rag", "lightrag",
                "probiopsy_rag"])
    for a in ACTIONS:
        gold = summary["methods"]["probiopsy-rag"]["gold_distribution"][a]
        w.writerow([a, gold] + [summary["methods"][m]["pred_distribution"][a]
                                for m in ["pure_llm", "naive_rag", "lightrag", FULL]])

result = {
    "paired_tests_bh_fdr": raw_tests,
    "n_flash_full_runs": n_flash_full,
    "confusion_full_flash_aggregated": matrix(overall),
    "confusion_full_per_domain": {d: matrix(c) for d, c in sorted(per_dom.items())},
    "conditional_recall_full": round(cond_recall, 4),
    "panel_c_csv": str(panel_c_path.relative_to(ROOT)),
    "glm53_flagship": {
        m: {k: v for k, v in glm53["methods"][m]["aggregate"].items()
            if k in ("exact5", "kappa", "macro_f1")}
        for m in glm53.get("methods", {})
    },
}
dest = OUT / "tables" / "internal_review_stats.json"
dest.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"n_flash_full_runs={n_flash_full}")
for t_ in raw_tests:
    print(f"{t_['comparison']:32s} {t_['metric']:7s} t={t_['t_stat']:8.3f} "
          f"p_raw={t_['p_raw']:.2e} p_fdr={t_['p_bh_fdr']:.2e}")
print("conditional recall (full):", round(cond_recall, 4))
print("per-domain:", {d: sum(sum(row.values()) for row in mm.values())
                      for d, mm in result["confusion_full_per_domain"].items()})
print("written:", dest, "and", panel_c_path.name)
