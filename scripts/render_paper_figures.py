"""Project-specific final renderer for probiopsy-rag paper figures.

The generic contract renderer (medical-agent-writer build_figures.py) only
auto-renders forest/grouped_bar/scatter/heatmap; schematic and domain panels
come out as placeholders. This script draws Figure 1 (architecture schematic),
Figure 2 (performance), Figure 4 (demo case + evidence corpus), and Figure 5
(reasoning-trace timings + KG edges) from REAL project data, overwriting the
placeholder outputs at outputs/figures/figure{N}_*.{svg,pdf,png}.

Figure 3 (expert agreement) is intentionally NOT drawn: the expert blind
review (planner phase 4.5) has not run yet; no expert data exists.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "outputs" / "figures"

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 7,
    "axes.linewidth": 0.8,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

C_RULE = "#5B8FF9"   # layer 1
C_KG = "#5AD8A6"     # layer 2
C_LLM = "#F6BD16"    # layer 3
C_METH = {"pure_llm": "#B8B8B8", "naive_rag": "#9D2933",
          "lightrag": "#5AD8A6", "probiopsy-rag": "#5B8FF9"}
C_SEV = {"high": "#dc2626", "medium": "#ea580c", "low": "#16a34a"}
ACTIONS = ["endorse", "endorse_option", "conditional", "report_option", "against"]


def _export(fig, stem: str) -> None:
    for ext in ("svg", "pdf", "png"):
        fig.savefig(FIG / f"{stem}.{ext}", bbox_inches="tight", dpi=600 if ext != "png" else 300)
    plt.close(fig)
    print(f"  {stem}: svg/pdf/png written")


# ------------------------------------------------------------------ Figure 1
def fig1() -> None:
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def box(x, y, w, h, text, fc, ec, fs=7, weight="normal"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6",
                                    fc=fc, ec=ec, lw=0.9))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, fontweight=weight)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                     arrowstyle="-|>", mutation_scale=9,
                                     lw=0.9, color="#4B5563"))

    # input column
    box(2, 38, 17, 24, "Input\nPatient scenario\n(Entity A, 51)\nx\nDecision item\n(Entity B, 54)",
        "#F3F4F6", "#9CA3AF", 6.5)
    ax.text(10.5, 66, "flags +\npatient factors", ha="center", fontsize=6, color="#4B5563")

    # layer 1 — rules
    box(30, 76, 42, 16,
        "Layer 1 — Rule engine (deterministic)\n12 consensus rules + 4 patient-factor rules → hard constraints",
        "#EFF6FF", C_RULE, 6.8)
    # layer 2 — retrieval
    box(30, 46, 42, 16,
        "Layer 2 — Risk-guided retrieval\nLightRAG KG (1,864 entities / 3,078 relations)\n+ lexical evidence store (357 chunks)",
        "#ECFDF5", C_KG, 6.8)
    # layer 3 — arbiter
    box(30, 16, 42, 16,
        "Layer 3 — LLM arbiter (GLM-5.3)\nhard constraints + graph + lexical evidence → verdict",
        "#FFFBEB", C_LLM, 6.8)
    # output
    box(80, 16, 18, 16,
        "Structured verdict\n5-class action\n+ confidence\n+ Q-code & chunk\ncitations",
        "#F3F4F6", "#111827", 6.2, "bold")

    arrow(19, 50, 30, 82)          # input -> rules (up to first gate)
    arrow(51, 76, 51, 62)          # rules -> retrieval
    arrow(51, 46, 51, 32)          # retrieval -> arbiter
    arrow(72, 24, 80, 24)          # arbiter -> output
    # hard constraints bypass arrow
    ax.add_patch(FancyArrowPatch((72, 84), (89, 84), arrowstyle="-|>",
                                 mutation_scale=9, lw=0.9, color=C_RULE,
                                 linestyle=(0, (3, 2))))
    ax.add_patch(FancyArrowPatch((89, 84), (89, 32), arrowstyle="-",
                                 lw=0.9, color=C_RULE, linestyle=(0, (3, 2))))
    ax.text(80.5, 87, "hard constraints (cannot be overridden)", fontsize=5.8, color=C_RULE)

    ax.text(24.5, 82, "1", fontsize=8, fontweight="bold", color=C_RULE, ha="center")
    ax.text(24.5, 52, "2", fontsize=8, fontweight="bold", color=C_KG, ha="center")
    ax.text(24.5, 22, "3", fontsize=8, fontweight="bold", color="#B45309", ha="center")
    _export(fig, "figure1_architecture")


# ------------------------------------------------------------------ Figure 2
def fig2() -> None:
    summary = json.loads((ROOT / "outputs" / "evaluation_summary.json").read_text(encoding="utf-8"))
    methods = [("pure_llm", "pure_llm"), ("naive_rag", "naive_rag"),
               ("lightrag", "LightRAG-only"), ("probiopsy-rag", "QianLieAnHui (full)")]
    metrics = [("exact5", "Exact-5\nacc"), ("exact3", "Exact-3\nacc"),
               ("macro_f1", "Macro-F1"), ("kappa", "Cohen's κ"),
               ("against_f1", "Against-F1")]

    fig, (ax1, ax2, ax3) = plt.subplots(
        1, 3, figsize=(7.6, 2.9), gridspec_kw={"width_ratios": [3, 1.5, 2.1]})
    # (a) grouped bars with SD error bars
    n_m, n_met = len(methods), len(metrics)
    bw = 0.8 / n_m
    for j, (mid, label) in enumerate(methods):
        agg = summary["methods"][mid]["aggregate"]
        means = [agg[k]["mean"] for k, _ in metrics]
        sds = [agg[k]["sd"] for k, _ in metrics]
        xs = [i + j * bw - 0.4 + bw / 2 for i in range(n_met)]
        ax1.bar(xs, means, bw, yerr=sds, capsize=1.6,
                color=C_METH[mid], label=label,
                error_kw={"lw": 0.7, "elinewidth": 0.7})
    ax1.set_xticks(range(n_met))
    ax1.set_xticklabels([l for _, l in metrics], fontsize=6.2)
    ax1.set_ylabel("Score (0–1)")
    ax1.set_ylim(0, 1.0)
    ax1.legend(fontsize=5.8, ncol=4, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 1.02))
    ax1.set_title("(a) Core metrics by method (mean ± SD, 5 seeds)",
                  fontsize=7, pad=16)
    ax1.spines[["top", "right"]].set_visible(False)

    # (b) per-seed exact-5 dots + mean dash
    for j, (mid, label) in enumerate(methods):
        seeds = [s["exact5"] for s in summary["methods"][mid]["seeds"]]
        mean = summary["methods"][mid]["aggregate"]["exact5"]["mean"]
        xs = [j] * len(seeds)
        ax2.scatter([x + 0.06 for x in xs], seeds, s=9, color=C_METH[mid],
                    zorder=3, edgecolors="none")
        ax2.hlines(mean, j - 0.22, j + 0.28, color=C_METH[mid], lw=1.6, zorder=4)
    ax2.set_xticks(range(n_m))
    ax2.set_xticklabels(["pure\nLLM", "naive\nRAG", "LightRAG\nonly", "QianLie\nAnHui"], fontsize=6)
    ax2.set_ylabel("Exact-5 accuracy")
    ax2.set_ylim(0, 1.0)
    ax2.set_title("(b) Exact-5 per seed (dash = mean)", fontsize=7)
    ax2.spines[["top", "right"]].set_visible(False)

    # (c) predicted class distribution per method (counts over 560 runs),
    #     gold-standard counts overlaid as black diamonds
    import csv
    dist = {}
    with open(ROOT / "outputs" / "figures" / "source_data" /
              "figure2_pred_distribution.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            dist[row["action"]] = row
    classes = ["endorse", "endorse_option", "conditional", "report_option", "against"]
    class_lbl = ["endorse", "endorse_\noption", "conditional", "report_\noption",
                 "against"]
    n_c = len(classes)
    bw = 0.8 / n_m
    for j, (mid, label) in enumerate(methods):
        col = "probiopsy_rag" if mid == "probiopsy-rag" else mid
        counts = [int(dist[c][col]) for c in classes]
        xs = [i + j * bw - 0.4 + bw / 2 for i in range(n_c)]
        ax3.bar(xs, counts, bw, color=C_METH[mid], label=label)
    gold = [int(dist[c]["gold_standard"]) for c in classes]
    ax3.scatter(range(n_c), gold, marker="D", s=10, color="#222222", zorder=5,
                label="gold standard")
    ax3.set_xticks(range(n_c))
    ax3.set_xticklabels(class_lbl, fontsize=5.6)
    ax3.set_ylabel("Predictions (of 560 runs)")
    ax3.legend(fontsize=5.2, frameon=False, loc="upper right",
               bbox_to_anchor=(1.02, 1.04))
    ax3.set_title("(c) Predicted class distribution", fontsize=7)
    ax3.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    _export(fig, "figure2_performance")


# ------------------------------------------------------------------ Figure 4
def fig4() -> None:
    import yaml
    cfg_sev, rules = {}, {}
    cfg = yaml.safe_load((ROOT / "configs" / "rules.yaml").read_text(encoding="utf-8"))
    for r in cfg.get("rules", []):
        cfg_sev[r["id"]] = r.get("severity", "unknown")
        rules[r["id"]] = r.get("risk_type", "")
    pfr = cfg.get("patient_factor_rules", {})
    for rid, r in (pfr.items() if isinstance(pfr, dict) else enumerate(pfr)):
        if isinstance(r, dict) and "id" not in r:
            r = {"id": rid, **r}
        cfg_sev[r["id"]] = r.get("severity", "unknown")
        rules.setdefault(r["id"], "patient_factor")

    cases = []
    for jp in sorted((ROOT / "outputs" / "demo_cases").glob("case*.json")):
        d = json.loads(jp.read_text(encoding="utf-8"))
        cases.append(d)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.7),
                                   gridspec_kw={"width_ratios": [1, 1]})
    # (a) evidence corpus composition (stacked single bar by source_type)
    rows = [json.loads(l) for l in
            (ROOT / "data" / "seed" / "evidence_chunks.jsonl").open(encoding="utf-8") if l.strip()]
    st = Counter(r.get("source_type", "") for r in rows)
    labels = {"consensus_statement": "Consensus statements (B)",
              "literature_reference": "Literature entries (C)",
              "consensus_narrative": "Consensus narrative",
              "systematic_review_summary": "SR summaries (D)"}
    vals = [(labels.get(k, k), v) for k, v in st.most_common()]
    total = sum(v for _, v in vals)
    y = 0.0
    colors = ["#5B8FF9", "#5AD8A6", "#F6BD16", "#B8B8B8"]
    for (lab, v), c in zip(vals, colors):
        ax2.barh([0], [v], left=[y], color=c, label=f"{lab} (n={v})", height=0.5)
        if v / total > 0.08:
            ax2.text(y + v / 2, 0, str(v), ha="center", va="center", fontsize=6.5,
                     color="white", fontweight="bold")
        y += v
    ax2.set_yticks([])
    ax2.set_xlabel("Evidence chunks (n = 357)")
    ax2.legend(fontsize=5.8, frameon=False, loc="upper center",
               bbox_to_anchor=(0.5, -0.28), ncol=2)
    ax2.set_title("(b) Evidence corpus composition", fontsize=7)
    ax2.spines[["top", "right", "left"]].set_visible(False)

    # (a) demo cases: actions + rules fired count
    case_names = ["Unifocal\nscheme", "PSMA PET\nupfront", "bpMRI\nindeterminate",
                  "Advanced\ndisease", "Infection\nrisk"]
    n_rules = [len(d.get("rules_fired") or []) for d in cases]
    actions = [d["verdict"]["action"] for d in cases]
    colors_a = [C_METH["probiopsy-rag"] if a in ("endorse", "endorse_option")
                else ("#dc2626" if a == "against" else "#F6BD16") for a in actions]
    bars = ax1.bar(range(len(cases)), n_rules, color=colors_a, width=0.62)
    for i, (b, a) in enumerate(zip(bars, actions)):
        ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.06, a,
                 ha="center", fontsize=5.4, rotation=28, color="#374151")
    ax1.set_xticks(range(len(cases)))
    ax1.set_xticklabels(case_names, fontsize=6)
    ax1.set_ylabel("Consensus rules fired")
    ax1.set_ylim(0, max(n_rules) + 0.9)
    ax1.set_title("(a) Demo cases: rules fired → verdict action", fontsize=7)
    ax1.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    _export(fig, "figure4_demo_case")


# ------------------------------------------------------------------ Figure 5
def fig5() -> None:
    trace = list(csv.DictReader((FIG / "source_data" / "figure5_reasoning_trace.csv")
                                .open(encoding="utf-8")))
    paths = list(csv.DictReader((FIG / "source_data" / "figure5_paths.csv")
                                .open(encoding="utf-8")))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.7),
                                   gridspec_kw={"width_ratios": [1, 1.3]})
    # (a) per-case full-pass latency, stacked rule vs remainder
    cases, rule_ms, full_ms = [], [], []
    seen = {}
    for r in trace:
        seen.setdefault(r["case_id"], {})[r["layer"]] = float(r["duration_ms"])
    for cid, layers in seen.items():
        cases.append(cid.replace("_", " "))
        rule_ms.append(layers.get("rule_engine", 0.0))
        full_ms.append(layers.get("llm_arbiter", 0.0))
    rest = [max(f - ru, 0.0) for f, ru in zip(full_ms, rule_ms)]
    y = range(len(cases))
    ax1.barh(list(y), rule_ms, color=C_RULE, label="rule engine", height=0.55)
    ax1.barh(list(y), rest, left=rule_ms, color=C_LLM,
             label="retrieval + arbitration", height=0.55)
    ax1.set_yticks(list(y))
    ax1.set_yticklabels(cases, fontsize=6)
    ax1.set_xlabel("Latency (ms, log scale)")
    ax1.set_xscale("log")
    ax1.legend(fontsize=5.8, frameon=False, loc="upper center",
               bbox_to_anchor=(0.5, -0.22), ncol=2)
    ax1.set_title("(a) Decision-pass latency per demo case", fontsize=7)
    ax1.invert_yaxis()
    ax1.spines[["top", "right"]].set_visible(False)

    # (b) top KG edge weights
    top = paths[:12]
    labels = [f"{p['source_node'][:26]} → {p['target_node'][:26]}" for p in top]
    weights = [float(p["weight"]) for p in top]
    ax2.barh(range(len(top)), weights, color=C_KG, height=0.6)
    ax2.set_yticks(range(len(top)))
    ax2.set_yticklabels(labels, fontsize=5.4)
    ax2.invert_yaxis()
    ax2.set_xlabel("Relation weight (top-12 of 3,078 edges)")
    ax2.set_title("(b) Strongest knowledge-graph relations", fontsize=7)
    ax2.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    _export(fig, "figure5_reasoning_trace")


if __name__ == "__main__":
    print("[render] probiopsy-rag paper figures")
    fig1()
    fig2()
    fig4()
    fig5()
    print("[render] done (figure3 = expert panel pending, left as contract placeholder)")
