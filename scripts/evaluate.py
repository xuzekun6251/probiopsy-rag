"""Compute statement-fidelity metrics from baseline_predictions.jsonl.

Metrics (per method, aggregated over seeds as mean ± sd):
  - exact-5 accuracy        (endorse/endorse_option/conditional/report_option/against)
  - exact-3 accuracy        (collapsed: endorse*, conditional*/report_option, against)
  - macro-F1 (5-class)
  - Cohen's kappa (5-class, unweighted)
  - safety against-sensitivity / specificity / F1  (binary: against vs not)
  - retrieval efficiency: mean context chars, mean chunks retrieved

Usage:
    .venv/Scripts/python.exe scripts/evaluate.py [--pred outputs/baseline_predictions.jsonl]
"""
from __future__ import annotations

import argparse
import json
import sys
import io
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ACTIONS = ("endorse", "endorse_option", "conditional", "report_option", "against")
COLLAPSE = {
    "endorse": "endorse", "endorse_option": "endorse",
    "conditional": "conditional", "report_option": "conditional",
    "against": "against",
}


def kappa(preds: list[str], golds: list[str]) -> float:
    n = len(golds)
    if n == 0:
        return 0.0
    classes = sorted(set(golds) | set(preds))
    idx = {c: i for i, c in enumerate(classes)}
    mat = [[0] * len(classes) for _ in classes]
    for p, g in zip(preds, golds):
        mat[idx[g]][idx[p]] += 1
    po = sum(mat[i][i] for i in range(len(classes))) / n
    row = [sum(r) for r in mat]
    col = [sum(mat[i][j] for i in range(len(classes))) for j in range(len(classes))]
    pe = sum(row[i] * col[i] for i in range(len(classes))) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def macro_f1(preds: list[str], golds: list[str], classes=ACTIONS) -> float:
    f1s = []
    for c in classes:
        tp = sum(1 for p, g in zip(preds, golds) if p == c and g == c)
        fp = sum(1 for p, g in zip(preds, golds) if p == c and g != c)
        fn = sum(1 for p, g in zip(preds, golds) if p != c and g == c)
        f1s.append(2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0)
    return sum(f1s) / len(classes)


def binary_metrics(preds: list[str], golds: list[str], positive: str = "against") -> dict:
    tp = sum(1 for p, g in zip(preds, golds) if p == positive and g == positive)
    fp = sum(1 for p, g in zip(preds, golds) if p == positive and g != positive)
    fn = sum(1 for p, g in zip(preds, golds) if p != positive and g == positive)
    tn = len(preds) - tp - fp - fn
    sens = tp / (tp + fn) if tp + fn else 0.0
    spec = tn / (tn + fp) if tn + fp else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0
    return {"sensitivity": sens, "specificity": spec, "f1": f1}


def mean_sd(vals: list[float]) -> tuple[float, float]:
    if not vals:
        return 0.0, 0.0
    m = sum(vals) / len(vals)
    sd = (sum((v - m) ** 2 for v in vals) / max(len(vals) - 1, 1)) ** 0.5
    return m, sd


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", default=str(ROOT / "outputs" / "baseline_predictions.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "outputs" / "evaluation_summary.json"))
    args = ap.parse_args()

    rows = [json.loads(l) for l in Path(args.pred).open(encoding="utf-8") if l.strip()]
    if not rows:
        print("[evaluate] no prediction rows found")
        return 1

    by_ms: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for r in rows:
        by_ms[(r["method"], int(r.get("seed", 0)))].append(r)

    summary: dict[str, dict] = {}
    for method in sorted({m for (m, _s) in by_ms}):
        seed_metrics = []
        all_rows = [r for (m, _s), rs in by_ms.items() if m == method for r in rs]
        for (m, seed), rs in sorted(by_ms.items()):
            if m != method:
                continue
            golds = [r["gold_action"] for r in rs]
            preds = [r["pred_action"] for r in rs]
            bm = binary_metrics(preds, golds)
            seed_metrics.append({
                "seed": seed, "n": len(rs),
                "exact5": sum(p == g for p, g in zip(preds, golds)) / len(rs),
                "exact3": sum(COLLAPSE[p] == COLLAPSE[g] for p, g in zip(preds, golds)) / len(rs),
                "macro_f1": macro_f1(preds, golds),
                "kappa": kappa(preds, golds),
                **{f"against_{k}": v for k, v in bm.items()},
                "context_chars": sum(r.get("context_chars", 0) for r in rs) / len(rs),
                "chunks_retrieved": sum(r.get("chunks_retrieved", 0) for r in rs) / len(rs),
            })
        agg = {}
        for key in ("exact5", "exact3", "macro_f1", "kappa", "against_sensitivity",
                    "against_specificity", "against_f1", "context_chars", "chunks_retrieved"):
            m_, sd_ = mean_sd([s[key] for s in seed_metrics])
            agg[key] = {"mean": round(m_, 4), "sd": round(sd_, 4)}
        pred_dist = Counter(r["pred_action"] for r in all_rows)
        gold_dist = Counter(r["gold_action"] for r in all_rows)
        summary[method] = {"seeds": seed_metrics, "aggregate": agg,
                           "pred_distribution": dict(pred_dist),
                           "gold_distribution": dict(gold_dist),
                           "n_total": len(all_rows)}

    # confusion matrix for the full system (paper figure source)
    conf_rows = [r for r in rows if r["method"] == "probiopsy-rag"]
    conf = Counter((r["gold_action"], r["pred_action"]) for r in conf_rows)

    out = {"methods": summary,
           "confusion_probiopsy_rag": {f"{g}->{p}": c for (g, p), c in conf.items()},
           "n_methods": len(summary), "n_rows": len(rows)}
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[evaluate] methods={len(summary)} rows={len(rows)} -> {args.out}")
    print(f"{'method':<16}{'exact5':>16}{'exact3':>16}{'kappa':>16}{'against F1':>16}")
    for method, s in summary.items():
        a = s["aggregate"]
        row = f"{method:<16}"
        row += f"{a['exact5']['mean']:.3f}±{a['exact5']['sd']:.3f}".rjust(16)
        row += f"{a['exact3']['mean']:.3f}±{a['exact3']['sd']:.3f}".rjust(16)
        row += f"{a['kappa']['mean']:.3f}±{a['kappa']['sd']:.3f}".rjust(16)
        row += f"{a['against_f1']['mean']:.3f}±{a['against_f1']['sd']:.3f}".rjust(16)
        print(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
