"""Convert figure2 source data to the wide (metric x method) shape the
build_figures grouped_bar panel expects; per-seed long data kept separately.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "outputs" / "figures" / "source_data"

summary = json.loads((ROOT / "outputs" / "evaluation_summary.json").read_text(encoding="utf-8"))
METHODS = [("pure_llm", "pure_llm"), ("naive_rag", "naive_rag"),
           ("lightrag", "lightrag"), ("probiopsy-rag", "full_system")]
METRICS = [("exact5", "Exact-5 accuracy"), ("exact3", "Exact-3 accuracy"),
           ("macro_f1", "Macro-F1 (5-class)"), ("kappa", "Cohen's kappa"),
           ("against_sensitivity", "Against sensitivity"),
           ("against_specificity", "Against specificity"),
           ("against_f1", "Against F1")]

header = (["metric"] + [m[1] for m in METHODS]
          + [f"{m[1]}_sd" for m in METHODS])
rows = []
for key, label in METRICS:
    row = [label]
    for mid, _ in METHODS:
        row.append(round(summary["methods"][mid]["aggregate"][key]["mean"], 4))
    for mid, _ in METHODS:
        row.append(round(summary["methods"][mid]["aggregate"][key]["sd"], 4))
    rows.append(row)

with (SRC / "figure2_performance.csv").open("w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(header)
    w.writerows(rows)
print("figure2_performance.csv (wide):", len(rows), "metrics x", len(METHODS), "methods")

# keep the per-seed long data as a supplementary csv (caption/source reference)
with (SRC / "figure2_performance_seeds.csv").open("w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["method", "phase", "seed", "sensitivity_high", "specificity_high",
                "f1_high", "exact_4_level_accuracy", "cohens_kappa", "context_chars"])
    for mid, label in METHODS:
        for sd in summary["methods"][mid]["seeds"]:
            w.writerow([label, "benchmark", sd["seed"], round(sd["against_sensitivity"], 4),
                        round(sd["against_specificity"], 4), round(sd["against_f1"], 4),
                        round(sd["exact5"], 4), round(sd["kappa"], 4),
                        round(sd["context_chars"], 1)])
print("figure2_performance_seeds.csv: written")
